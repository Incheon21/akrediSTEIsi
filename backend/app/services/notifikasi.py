from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.indikator import Indikator
from app.models.kriteria import Kriteria
from app.models.lkps import LkpsSubmission
from app.models.narasi_led import NarasiLED
from app.models.notifikasi import Notifikasi
from app.models.target_akreditasi import TargetAkreditasi
from app.models.user import User
from app.services.dashboard import KRITERIA_LKPS_MODELS


def notify_komentar_to_tim_prodi(
    db: Session,
    *,
    komentar_id: UUID,
    target_akreditasi_id: UUID,
    pengirim_nama: str,
    isi_komentar: str,
    program_studi_id: UUID,
) -> None:
    """Create a notification for each tim_prodi member of the prodi when a comment is posted."""
    from app.models.role import Role  # avoid circular import

    tim_prodi_role = db.query(Role).filter(Role.name == "tim_prodi").first()
    if not tim_prodi_role:
        return

    recipients = (
        db.query(User)
        .filter(
            User.role_id == tim_prodi_role.id,
            User.program_studi_id == program_studi_id,
        )
        .all()
    )

    target = db.query(TargetAkreditasi).filter(TargetAkreditasi.id == target_akreditasi_id).first()
    prodi_name = target.program_studi.nama if target and target.program_studi else ""
    tahun = target.tahun_akreditasi if target else ""
    href = "/prodi/dashboard-prodi"
    source_key = f"komentar:{komentar_id}"
    preview = isi_komentar[:80] + ("…" if len(isi_komentar) > 80 else "")

    for user in recipients:
        existing = (
            db.query(Notifikasi)
            .filter(Notifikasi.user_id == user.id, Notifikasi.source_key == source_key)
            .first()
        )
        if existing:
            continue
        db.add(
            Notifikasi(
                user_id=user.id,
                source_key=source_key,
                kategori="komentar",
                severity="info",
                judul=f"Komentar baru dari {pengirim_nama}",
                pesan=f"{prodi_name} ({tahun}): {preview}",
                href=href,
                program_studi_id=program_studi_id,
                target_akreditasi_id=target_akreditasi_id,
            )
        )
    db.commit()


GENERATED_PREFIX = "reminder"


def _dashboard_href(target: TargetAkreditasi, include_prodi_id: bool) -> str:
    suffix = f"?id={target.program_studi_id}" if include_prodi_id else ""
    return f"/prodi/dashboard-prodi{suffix}"


def _lkps_href(
    submission: LkpsSubmission,
    target: TargetAkreditasi,
    include_prodi_id: bool,
) -> str:
    prodi_query = f"&id={target.program_studi_id}" if include_prodi_id else ""
    return (
        f"/akreditasi/lkps/{submission.id}"
        f"?target_akreditasi_id={target.id}&tahun={target.tahun_akreditasi}{prodi_query}"
    )


def _upsert_generated_notification(
    db: Session,
    *,
    user_id: UUID,
    source_key: str,
    kategori: str,
    severity: str,
    judul: str,
    pesan: str,
    href: str,
    program_studi_id: UUID | None,
    target_akreditasi_id: UUID | None,
) -> None:
    row = (
        db.query(Notifikasi)
        .filter(Notifikasi.user_id == user_id, Notifikasi.source_key == source_key)
        .first()
    )
    if row:
        row.kategori = kategori
        row.severity = severity
        row.judul = judul
        row.pesan = pesan
        row.href = href
        row.program_studi_id = program_studi_id
        row.target_akreditasi_id = target_akreditasi_id
        return

    db.add(
        Notifikasi(
            user_id=user_id,
            source_key=source_key,
            kategori=kategori,
            severity=severity,
            judul=judul,
            pesan=pesan,
            href=href,
            program_studi_id=program_studi_id,
            target_akreditasi_id=target_akreditasi_id,
        )
    )


def _accessible_active_targets(db: Session, current_user: User) -> list[TargetAkreditasi]:
    role_name = current_user.role.name if current_user.role else ""
    query = db.query(TargetAkreditasi).filter(TargetAkreditasi.is_aktif.is_(True))

    if role_name == "tim_prodi":
        if not current_user.program_studi_id:
            return []
        query = query.filter(TargetAkreditasi.program_studi_id == current_user.program_studi_id)

    return query.all()


def _sync_deadline_notification(
    db: Session,
    current_user: User,
    target: TargetAkreditasi,
    include_prodi_id: bool,
    active_keys: set[str],
) -> None:
    if not target.deadline:
        return

    days_left = (target.deadline - date.today()).days
    if days_left > 30:
        return

    prodi_name = target.program_studi.nama if target.program_studi else "Program studi"
    source_key = f"{GENERATED_PREFIX}:deadline:{target.id}"
    active_keys.add(source_key)

    if days_left < 0:
        severity = "critical"
        judul = f"Deadline {prodi_name} sudah lewat"
        pesan = f"Deadline akreditasi {target.tahun_akreditasi} sudah terlewat {abs(days_left)} hari."
    elif days_left <= 7:
        severity = "critical"
        judul = f"Deadline {prodi_name} sangat dekat"
        pesan = f"Deadline akreditasi {target.tahun_akreditasi} tinggal {days_left} hari."
    else:
        severity = "warning"
        judul = f"Deadline {prodi_name} mendekat"
        pesan = f"Deadline akreditasi {target.tahun_akreditasi} tinggal {days_left} hari."

    _upsert_generated_notification(
        db,
        user_id=current_user.id,
        source_key=source_key,
        kategori="deadline",
        severity=severity,
        judul=judul,
        pesan=pesan,
        href=_dashboard_href(target, include_prodi_id),
        program_studi_id=target.program_studi_id,
        target_akreditasi_id=target.id,
    )


def _sync_lkps_notification(
    db: Session,
    current_user: User,
    target: TargetAkreditasi,
    include_prodi_id: bool,
    active_keys: set[str],
) -> None:
    prodi_name = target.program_studi.nama if target.program_studi else "Program studi"
    submission = (
        db.query(LkpsSubmission)
        .filter(
            LkpsSubmission.program_studi_id == target.program_studi_id,
            LkpsSubmission.tahun_ts == target.tahun_akreditasi,
        )
        .first()
    )
    if not submission:
        source_key = f"{GENERATED_PREFIX}:lkps-missing:{target.id}"
        active_keys.add(source_key)
        _upsert_generated_notification(
            db,
            user_id=current_user.id,
            source_key=source_key,
            kategori="lkps",
            severity="warning",
            judul=f"LKPS {prodi_name} belum dibuat",
            pesan=f"Submission LKPS untuk tahun akreditasi {target.tahun_akreditasi} belum tersedia.",
            href=_dashboard_href(target, include_prodi_id),
            program_studi_id=target.program_studi_id,
            target_akreditasi_id=target.id,
        )
        return

    total_sections = 0
    filled_sections = 0
    incomplete_kriteria: list[str] = []

    jenjang = target.program_studi.jenjang if target.program_studi else ""
    for kriteria in db.query(Kriteria).all():
        model_entries = KRITERIA_LKPS_MODELS.get(kriteria.kode, [])
        applicable_models = [
            model
            for model, allowed in model_entries
            if allowed is None or jenjang in allowed
        ]
        if not applicable_models:
            continue

        total_sections += len(applicable_models)
        filled_for_kriteria = sum(
            1
            for model in applicable_models
            if db.query(model).filter(model.submission_id == submission.id).first()
        )
        filled_sections += filled_for_kriteria
        if filled_for_kriteria < len(applicable_models):
            incomplete_kriteria.append(kriteria.kode)

    if total_sections == 0 or filled_sections >= total_sections:
        return

    source_key = f"{GENERATED_PREFIX}:lkps-incomplete:{submission.id}"
    active_keys.add(source_key)
    missing_count = total_sections - filled_sections

    _upsert_generated_notification(
        db,
        user_id=current_user.id,
        source_key=source_key,
        kategori="lkps",
        severity="warning",
        judul=f"LKPS {prodi_name} belum lengkap",
        pesan=(
            f"{missing_count} bagian LKPS belum terisi. "
            f"Kriteria terdampak: {', '.join(incomplete_kriteria[:5])}."
        ),
        href=_lkps_href(submission, target, include_prodi_id),
        program_studi_id=target.program_studi_id,
        target_akreditasi_id=target.id,
    )


def _sync_led_notification(
    db: Session,
    current_user: User,
    target: TargetAkreditasi,
    include_prodi_id: bool,
    active_keys: set[str],
) -> None:
    prodi_name = target.program_studi.nama if target.program_studi else "Program studi"
    led_indicators = (
        db.query(Indikator)
        .filter(Indikator.tipe_input.in_(("narasi", "text", "teks", "both")))
        .all()
    )
    if not led_indicators:
        return

    indicator_ids = [indicator.id for indicator in led_indicators]
    filled_count = (
        db.query(NarasiLED)
        .filter(
            NarasiLED.target_akreditasi_id == target.id,
            NarasiLED.indikator_id.in_(indicator_ids),
            NarasiLED.narasi.isnot(None),
            NarasiLED.narasi != "",
        )
        .count()
    )
    if filled_count >= len(led_indicators):
        return

    source_key = f"{GENERATED_PREFIX}:led-incomplete:{target.id}"
    active_keys.add(source_key)
    missing_count = len(led_indicators) - filled_count

    _upsert_generated_notification(
        db,
        user_id=current_user.id,
        source_key=source_key,
        kategori="led",
        severity="info",
        judul=f"Narasi LED {prodi_name} belum lengkap",
        pesan=f"{missing_count} narasi LED belum terisi untuk tahun akreditasi {target.tahun_akreditasi}.",
        href=_dashboard_href(target, include_prodi_id),
        program_studi_id=target.program_studi_id,
        target_akreditasi_id=target.id,
    )


def sync_generated_notifications(db: Session, current_user: User) -> None:
    role_name = current_user.role.name if current_user.role else ""
    include_prodi_id = role_name in {"admin", "pimpinan"}
    active_keys: set[str] = set()

    for target in _accessible_active_targets(db, current_user):
        _sync_deadline_notification(db, current_user, target, include_prodi_id, active_keys)
        _sync_lkps_notification(db, current_user, target, include_prodi_id, active_keys)
        _sync_led_notification(db, current_user, target, include_prodi_id, active_keys)

    stale_rows = (
        db.query(Notifikasi)
        .filter(
            Notifikasi.user_id == current_user.id,
            Notifikasi.source_key.like(f"{GENERATED_PREFIX}:%"),
        )
        .all()
    )
    for row in stale_rows:
        if row.source_key not in active_keys:
            db.delete(row)

    db.commit()
