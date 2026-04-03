import app.models  # noqa: F401 - register all models with Base
from datetime import date, timedelta
from app.core.security import hash_password
from app.db import Base, SessionLocal, engine
from app.models.program_studi import ProgramStudi
from app.models.role import Role
from app.models.user import User
from app.models.kriteria import Kriteria
from app.models.indikator import Indikator
from app.models.target_akreditasi import TargetAkreditasi


def seed():
    Base.metadata.create_all(bind=engine, checkfirst=True)

    db = SessionLocal()
    try:
        # Seed roles
        role_names = ["admin", "pimpinan", "koordinator", "tim_prodi"]
        roles = {}
        for name in role_names:
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name)
                db.add(role)
                db.flush()
                print(f"Seeded role: {name}")
            else:
                print(f"Role already exists: {name}")
            roles[name] = role

        db.commit()

        # Seed Program Studi
        prodi_data = [
            {
                "kode": "IF",
                "nama": "Teknik Informatika",
                "jenjang": "S1",
                "fakultas": "STEI",
                "perguruan_tinggi": "Institut Teknologi Bandung",
                "akreditasi": "Unggul",
            },
            {
                "kode": "EL",
                "nama": "Teknik Elektro",
                "jenjang": "S1",
                "fakultas": "STEI",
                "perguruan_tinggi": "Institut Teknologi Bandung",
            },
            {
                "kode": "TE",
                "nama": "Teknik Tenaga Listrik",
                "jenjang": "S1",
                "fakultas": "STEI",
                "perguruan_tinggi": "Institut Teknologi Bandung",
            },
            {
                "kode": "TS",
                "nama": "Teknik Telekomunikasi",
                "jenjang": "S1",
                "fakultas": "STEI",
                "perguruan_tinggi": "Institut Teknologi Bandung",
            },
            {
                "kode": "SI",
                "nama": "Sistem dan Teknologi Informasi",
                "jenjang": "S1",
                "fakultas": "STEI",
                "perguruan_tinggi": "Institut Teknologi Bandung",
            },
            {
                "kode": "STI",
                "nama": "Sistem Teknologi Informasi",
                "jenjang": "S1",
                "fakultas": "STEI",
                "perguruan_tinggi": "Institut Teknologi Bandung",
                "akreditasi": "Baik Sekali",
            },
        ]
        prodis = {}
        for p in prodi_data:
            prodi = db.query(ProgramStudi).filter(ProgramStudi.kode == p["kode"]).first()
            if not prodi:
                prodi = ProgramStudi(**p)
                db.add(prodi)
                db.flush()
                print(f"Seeded prodi: {p['nama']}")
            else:
                print(f"Prodi already exists: {p['nama']}")
            prodis[p["kode"]] = prodi
        
        db.commit()

        # Seed users
        seed_users = [
            {"email": "admin@stei.itb.ac.id",       "password": "admin123",       "nama": "Admin User",        "role": "admin", "prodi": None},
            {"email": "pimpinan@stei.itb.ac.id",     "password": "pimpinan123",    "nama": "Pimpinan User",     "role": "pimpinan", "prodi": None},
            {"email": "koordinator@stei.itb.ac.id",   "password": "koordinator123", "nama": "Koordinator User",  "role": "koordinator", "prodi": "IF"},
            {"email": "timprodi@stei.itb.ac.id",      "password": "timprodi123",    "nama": "Tim Prodi User",    "role": "tim_prodi", "prodi": "IF"},
        ]

        for u in seed_users:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                print(f"User already exists: id={existing.id}, email={existing.email}")
                # Update prodi if missing
                if not existing.program_studi_id and u["prodi"]:
                    existing.program_studi_id = prodis[u["prodi"]].id
                    db.add(existing)
                    db.commit()
                    print(f"Updated user prodi: {u['email']}")
            else:
                user = User(
                    email=u["email"],
                    hashed_password=hash_password(u["password"]),
                    nama=u["nama"],
                    role_id=roles[u["role"]].id,
                    program_studi_id=prodis[u["prodi"]].id if u["prodi"] else None
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"Seeded user: id={user.id}, email={user.email}, role={u['role']}")

        db.commit()

        kriteria_data = [
            {"kode": "C1", "nama": "Tata Pamong, Tata Kelola, dan Kerjasama"},
            {"kode": "C2", "nama": "Mahasiswa"},
            {"kode": "C3", "nama": "Sumber Daya Manusia"},
            {"kode": "C4", "nama": "Keuangan, Sarana, dan Prasarana"},
            {"kode": "C5", "nama": "Pendidikan"},
            {"kode": "C6", "nama": "Penelitian"},
            {"kode": "C7", "nama": "Pengabdian Kepada Masyarakat"},
            {"kode": "C8", "nama": "Luaran dan Capaian"},
        ]
        
        for k in kriteria_data:
            existing = db.query(Kriteria).filter(Kriteria.kode == k["kode"]).first()
            if not existing:
                kriteria = Kriteria(kode=k["kode"], nama=k["nama"])
                db.add(kriteria)
                db.flush()
                print(f"Seeded kriteria: {k['kode']} - {k['nama']}")
            else:
                kriteria = existing
                if kriteria.nama != k["nama"]:
                    kriteria.nama = k["nama"]
                    db.add(kriteria)
                    print(f"Updated kriteria name: {k['kode']} to {k['nama']}")
                else:
                    print(f"Kriteria already exists: {k['kode']}")
            
            # Seed some indicators
            for i in range(1, 3):
                kode_ind = f"{k['kode']}.{i}"
                existing_ind = db.query(Indikator).filter(Indikator.kode_indikator == kode_ind).first()
                if not existing_ind:
                    ind = Indikator(
                        kriteria_id=kriteria.id,
                        kode_indikator=kode_ind,
                        deskripsi=f"Deskripsi Indikator {kode_ind}",
                        tipe_input="both"
                    )
                    db.add(ind)
                    print(f"  Seeded indikator: {kode_ind}")
        
        db.commit()

        # Seed Target Akreditasi for IF
        if "IF" in prodis:
            prodi_if = prodis["IF"]
            existing_target = db.query(TargetAkreditasi).filter(
                TargetAkreditasi.program_studi_id == prodi_if.id,
                TargetAkreditasi.tahun_akreditasi == 2025
            ).first()
            if not existing_target:
                target = TargetAkreditasi(
                    program_studi_id=prodi_if.id,
                    tahun_akreditasi=2025,
                    target_skor=3.8,
                    deadline=date.today() + timedelta(days=60),
                    is_aktif=True
                )
                db.add(target)
                db.commit()
                print(f"Seeded target akreditasi for IF 2025")
            else:
                print("Target akreditasi for IF 2025 already exists")

    finally:
        db.close()


if __name__ == "__main__":
    seed()

