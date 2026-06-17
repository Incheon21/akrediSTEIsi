from datetime import date, timedelta

import app.models  # noqa: F401 - register all models with Base
from app.core.security import hash_password
from app.db import Base, SessionLocal, engine
from app.models.indikator import Indikator
from app.models.kriteria import Kriteria
from app.models.program_studi import ProgramStudi
from app.models.role import Role
from app.models.target_akreditasi import TargetAkreditasi
from app.models.user import User


def seed():
    db = SessionLocal()
    try:
        # Seed roles
        role_names = ["admin", "pimpinan", "tim_prodi"]
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
                "kode": "TTL",
                "nama": "Teknik Tenaga Listrik",
                "jenjang": "S1",
                "fakultas": "STEI",
                "perguruan_tinggi": "Institut Teknologi Bandung",
            },
            {
                "kode": "TK",
                "nama": "Teknik Telekomunikasi",
                "jenjang": "S1",
                "fakultas": "STEI",
                "perguruan_tinggi": "Institut Teknologi Bandung",
            },
            {
                "kode": "STI",
                "nama": "Sistem dan Teknologi Informasi",
                "jenjang": "S1",
                "fakultas": "STEI",
                "perguruan_tinggi": "Institut Teknologi Bandung",
            },
            {
                "kode": "BM",
                "nama": "Teknik Biomedis",
                "jenjang": "S1",
                "fakultas": "STEI",
                "perguruan_tinggi": "Institut Teknologi Bandung",
            },
        ]
        prodis = {}
        for p in prodi_data:
            prodi = (
                db.query(ProgramStudi).filter(ProgramStudi.kode == p["kode"]).first()
            )
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
            {
                "email": "admin@stei.itb.ac.id",
                "password": "admin123",
                "nama": "Admin User",
                "role": "admin",
                "prodi": None,
            },
            {
                "email": "pimpinan@stei.itb.ac.id",
                "password": "pimpinan123",
                "nama": "Pimpinan User",
                "role": "pimpinan",
                "prodi": None,
            },
            {
                "email": "timprodiIF@stei.itb.ac.id",
                "password": "timprodiIF123",
                "nama": "Tim Prodi User",
                "role": "tim_prodi",
                "prodi": "IF",
            },
            {
                "email": "timprodiEL@stei.itb.ac.id",
                "password": "timprodiEL123",
                "nama": "Tim Prodi EL",
                "role": "tim_prodi",
                "prodi": "EL",
            },
            {
                "email": "timprodiTTL@stei.itb.ac.id",
                "password": "timprodiTTL123",
                "nama": "Tim Prodi TTL",
                "role": "tim_prodi",
                "prodi": "TTL",
            },
            {
                "email": "timprodiTK@stei.itb.ac.id",
                "password": "timprodiTK123",
                "nama": "Tim Prodi TK",
                "role": "tim_prodi",
                "prodi": "TK",
            },
            {
                "email": "timprodiSTI@stei.itb.ac.id",
                "password": "timprodiSTI123",
                "nama": "Tim Prodi STI",
                "role": "tim_prodi",
                "prodi": "STI",
            },
            {
                "email": "timprodiBM@stei.itb.ac.id",
                "password": "timprodiBM123",
                "nama": "Tim Prodi BM",
                "role": "tim_prodi",
                "prodi": "BM",
            },
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
                    program_studi_id=prodis[u["prodi"]].id if u["prodi"] else None,
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(
                    f"Seeded user: id={user.id}, email={user.email}, role={u['role']}"
                )

        db.commit()

        # Kriteria LAM Teknik 2026
        kriteria_data = [
            {
                "kode": "C1",
                "nama": "Diferensiasi Misi (Visi, Misi, Tujuan, dan Strategi)",
            },
            {"kode": "C2", "nama": "Akuntabilitas"},
            {"kode": "C3", "nama": "Relevansi Pendidikan, Penelitian, dan PkM"},
            {"kode": "C4", "nama": "Sumber Daya Manusia"},
            {
                "kode": "C5",
                "nama": "Sarana, Prasarana, dan Keselamatan Kesehatan Kerja dan Lingkungan (K3L)",
            },
            {"kode": "C6", "nama": "Mahasiswa dan Luaran Mahasiswa"},
            {"kode": "C7", "nama": "Sistem Penjaminan Mutu"},
        ]

        # Specific sub-indikator mapping based on LED LAM Teknik 2026
        lam_teknik_indicators = {
            'C1': [
                {'kode': 'C1.1', 'nama': 'Latar Belakang', 'tipe': 'teks'},
                {'kode': 'C1.2', 'nama': 'Kebijakan', 'tipe': 'teks'},
                {'kode': 'C1.3.1', 'nama': 'Kekhasan VMTS', 'tipe': 'teks'},
                {'kode': 'C1.3.2', 'nama': 'Mekanisme Penyusunan VMTS', 'tipe': 'teks'},
                {'kode': 'C1.3.3', 'nama': 'Tingkat Pemahaman dan Pencapaian VMTS', 'tipe': 'teks'},
                {'kode': 'C1.4', 'nama': 'Analisis Faktor Keberhasilan dan Penghambat Pencapaian VMTS', 'tipe': 'teks'},
                {'kode': 'C1.5', 'nama': 'Strategi Perbaikan dan Pengembangan (Menggunakan Analisis SWOT)', 'tipe': 'teks'},
            ],
            'C2': [
                {'kode': 'C2.3.1', 'nama': 'Tata Pamong dan Tata Kelola', 'tipe': 'group'},
                {'kode': 'C2.3.2', 'nama': 'Kerja Sama', 'tipe': 'group'},
                {'kode': 'C2.3.3', 'nama': 'Keuangan', 'tipe': 'group'},
                {'kode': 'C2.1', 'nama': 'Latar Belakang', 'tipe': 'teks'},
                {'kode': 'C2.2', 'nama': 'Kebijakan', 'tipe': 'teks'},
                {'kode': 'C2.3.1.a', 'nama': 'Sistem Tata Pamong', 'tipe': 'teks'},
                {'kode': 'C2.3.1.b', 'nama': 'Good University Governance', 'tipe': 'teks'},
                {'kode': 'C2.3.1.c', 'nama': 'Komitmen Pimpinan (Visi dan Integritas)', 'tipe': 'teks'},
                {'kode': 'C2.3.1.d', 'nama': 'Komitmen Pimpinan (Kemampuan Manajerial)', 'tipe': 'teks'},
                {'kode': 'C2.3.2.a', 'nama': 'Relevansi Kerja Sama', 'tipe': 'teks'},
                {'kode': 'C2.3.2.b', 'nama': 'Tingkat Kerja Sama', 'tipe': 'teks'},
                {'kode': 'C2.3.2.c', 'nama': 'Pelaksanaan Kerja Sama', 'tipe': 'teks'},
                {'kode': 'C2.3.3.a', 'nama': 'Pengelolaan Keuangan', 'tipe': 'teks'},
                {'kode': 'C2.3.3.b', 'nama': 'Biaya Operasional Pendidikan', 'tipe': 'teks'},
                {'kode': 'C2.3.3.c', 'nama': 'Dana Penelitian', 'tipe': 'teks'},
                {'kode': 'C2.3.3.d', 'nama': 'Dana PkM', 'tipe': 'teks'},
                {'kode': 'C2.4', 'nama': 'Analisis Faktor Keberhasilan dan Penghambat Pencapaian', 'tipe': 'teks'},
                {'kode': 'C2.5', 'nama': 'Strategi Perbaikan dan Pengembangan (Menggunakan Analisis SWOT)', 'tipe': 'teks'},
            ],
            'C3': [
                {'kode': 'C3.3.1', 'nama': 'Pendidikan', 'tipe': 'group'},
                {'kode': 'C3.3.2', 'nama': 'Penelitian', 'tipe': 'group'},
                {'kode': 'C3.3.3', 'nama': 'Pengabdian Kepada Masyarakat (PkM)', 'tipe': 'group'},
                {'kode': 'C3.1', 'nama': 'Latar Belakang', 'tipe': 'teks'},
                {'kode': 'C3.2', 'nama': 'Kebijakan', 'tipe': 'teks'},
                {'kode': 'C3.3.1.a', 'nama': 'Pemutakhiran kurikulum', 'tipe': 'teks'},
                {'kode': 'C3.3.1.b', 'nama': 'Profil lulusan', 'tipe': 'teks'},
                {'kode': 'C3.3.1.c', 'nama': 'Kesesuaian CPL dengan profil lulusan', 'tipe': 'teks'},
                {'kode': 'C3.3.1.d', 'nama': 'Kesesuaian CPL dengan standar kompetensi lulusan', 'tipe': 'teks'},
                {'kode': 'C3.3.1.e', 'nama': 'Proses tinjauan rutin CPL', 'tipe': 'teks'},
                {'kode': 'C3.3.1.f', 'nama': 'Kualitas input mahasiswa (Metode rekrutmen)', 'tipe': 'teks'},
                {'kode': 'C3.3.1.g', 'nama': 'Kriteria penerimaan mahasiswa', 'tipe': 'teks'},
                {'kode': 'C3.3.1.h', 'nama': 'Proses seleksi', 'tipe': 'teks'},
                {'kode': 'C3.3.1.i', 'nama': 'Ketersediaan dan kelengkapan dokumen RPS', 'tipe': 'teks'},
                {'kode': 'C3.3.1.j', 'nama': 'Proses tinjauan rutin RPS', 'tipe': 'teks'},
                {'kode': 'C3.3.1.k', 'nama': 'Proses pembelajaran', 'tipe': 'teks'},
                {'kode': 'C3.3.1.l', 'nama': 'Proses tinjauan rutin proses pembelajaran', 'tipe': 'teks'},
                {'kode': 'C3.3.1.m', 'nama': 'Integrasi penelitian dan PkM dalam pembelajaran', 'tipe': 'teks'},
                {'kode': 'C3.3.1.n', 'nama': 'Pembelajaran penugasan, praktikum, praktik lapangan', 'tipe': 'teks'},
                {'kode': 'C3.3.1.o', 'nama': 'Basic Sciences dan matematika', 'tipe': 'teks'},
                {'kode': 'C3.3.1.p', 'nama': 'Proyek Rekayasa Penciri bidang Prodi (Capstone Design)', 'tipe': 'teks'},
                {'kode': 'C3.3.1.q', 'nama': 'Suasana akademik', 'tipe': 'teks'},
                {'kode': 'C3.3.1.r', 'nama': 'Integritas dan kebebasan ilmiah', 'tipe': 'teks'},
                {'kode': 'C3.3.2.a', 'nama': 'Kesesuaian penelitian dalam mendukung VMTS dan Visi Keilmuan', 'tipe': 'teks'},
                {'kode': 'C3.3.2.b', 'nama': 'Penelitian DTPS yang sesuai dengan Peta jalan', 'tipe': 'teks'},
                {'kode': 'C3.3.2.c', 'nama': 'Penelitian DTPS yang menjadi rujukan tema tesis/disertasi', 'tipe': 'teks'},
                {'kode': 'C3.3.3.a', 'nama': 'Kesesuaian PkM dalam mendukung VMTS dan Visi Keilmuan', 'tipe': 'teks'},
                {'kode': 'C3.3.3.b', 'nama': 'PkM DTPS yang sesuai dengan Peta jalan', 'tipe': 'teks'},
                {'kode': 'C3.4', 'nama': 'Analisis Faktor Keberhasilan dan Penghambat Pencapaian', 'tipe': 'teks'},
                {'kode': 'C3.5', 'nama': 'Strategi Perbaikan dan Pengembangan (Menggunakan Analisis SWOT)', 'tipe': 'teks'},
            ],
            'C4': [
                {'kode': 'C4.3.1', 'nama': 'Profil Dosen dan Tenaga Kependidikan', 'tipe': 'group'},
                {'kode': 'C4.3.2', 'nama': 'Beban Kerja DTPS', 'tipe': 'group'},
                {'kode': 'C4.1', 'nama': 'Latar Belakang', 'tipe': 'teks'},
                {'kode': 'C4.2', 'nama': 'Kebijakan', 'tipe': 'teks'},
                {'kode': 'C4.3.1.a', 'nama': 'Profil Dosen (Kecukupan jumlah dosen tetap)', 'tipe': 'teks'},
                {'kode': 'C4.3.1.b', 'nama': 'Profil Dosen (Kecukupan jumlah DTPSPPI dan DI)', 'tipe': 'teks'},
                {'kode': 'C4.3.1.c', 'nama': 'Kualifikasi akademik DTPS', 'tipe': 'teks'},
                {'kode': 'C4.3.1.d', 'nama': 'Kualifikasi keinsinyuran DTPSPPI', 'tipe': 'teks'},
                {'kode': 'C4.3.1.e', 'nama': 'Jabatan akademik DTPS (Guru Besar/Lektor Kepala/Lektor)', 'tipe': 'teks'},
                {'kode': 'C4.3.1.f', 'nama': 'Jabatan akademik DTPS (Guru Besar/Lektor Kepala)', 'tipe': 'teks'},
                {'kode': 'C4.3.1.g', 'nama': 'Jabatan akademik DTPS (Guru Besar)', 'tipe': 'teks'},
                {'kode': 'C4.3.1.h', 'nama': 'Sertifikat kompetensi/profesi/industri', 'tipe': 'teks'},
                {'kode': 'C4.3.1.i', 'nama': 'Mata kuliah kompetensi diampu oleh dosen industri/praktisi', 'tipe': 'teks'},
                {'kode': 'C4.3.1.j', 'nama': 'Tenaga Kependidikan (Kualifikasi dan kecukupan laboran)', 'tipe': 'teks'},
                {'kode': 'C4.3.2.a', 'nama': 'Beban Kerja DTPS', 'tipe': 'teks'},
                {'kode': 'C4.3.2.b', 'nama': 'Kegiatan Penelitian DTPS', 'tipe': 'teks'},
                {'kode': 'C4.3.2.c', 'nama': 'Kegiatan Penelitian Kolaboratif Industri DTPSPPI', 'tipe': 'teks'},
                {'kode': 'C4.3.2.d', 'nama': 'Kegiatan PkM DTPS', 'tipe': 'teks'},
                {'kode': 'C4.3.2.e', 'nama': 'Kegiatan PkM Kolaboratif Industri DTPSPPI', 'tipe': 'teks'},
                {'kode': 'C4.3.2.f', 'nama': 'Publikasi ilmiah DTPS', 'tipe': 'teks'},
                {'kode': 'C4.3.2.g', 'nama': 'Pagelaran / pameran / presentasi / publikasi ilmiah DTPS', 'tipe': 'teks'},
                {'kode': 'C4.3.2.h', 'nama': 'Luaran penelitian dan PkM DTPS (HKI, Paten, dll)', 'tipe': 'teks'},
                {'kode': 'C4.3.2.i', 'nama': 'Luaran kolaboratif industri DTPSPPI (HKI, Paten, dll)', 'tipe': 'teks'},
                {'kode': 'C4.3.2.j', 'nama': 'Produk/jasa yang diadopsi oleh industri/masyarakat', 'tipe': 'teks'},
                {'kode': 'C4.3.2.k', 'nama': 'Kinerja DTPS dalam mendukung keunggulan kompetitif UPPS', 'tipe': 'teks'},
                {'kode': 'C4.3.2.l', 'nama': 'Karya ilmiah DTPS yang disitasi', 'tipe': 'teks'},
                {'kode': 'C4.3.2.m', 'nama': 'Pengakuan / rekognisi atas prestasi / kinerja DTPS', 'tipe': 'teks'},
                {'kode': 'C4.3.2.n', 'nama': 'Pengakuan / rekognisi atas kepakaran DTPSPPI', 'tipe': 'teks'},
                {'kode': 'C4.3.2.o', 'nama': 'Pengembangan Dosen DTPSPPI', 'tipe': 'teks'},
                {'kode': 'C4.3.2.p', 'nama': 'Pembimbing Lapangan', 'tipe': 'teks'},
                {'kode': 'C4.4', 'nama': 'Analisis Faktor Keberhasilan dan Penghambat', 'tipe': 'teks'},
                {'kode': 'C4.5', 'nama': 'Strategi Perbaikan dan Pengembangan (Menggunakan Analisis SWOT)', 'tipe': 'teks'},
            ],
            'C5': [
                {'kode': 'C5.3.1', 'nama': 'Sarana dan Prasarana', 'tipe': 'group'},
                {'kode': 'C5.1', 'nama': 'Latar Belakang', 'tipe': 'teks'},
                {'kode': 'C5.2', 'nama': 'Kebijakan', 'tipe': 'teks'},
                {'kode': 'C5.3.1.a', 'nama': 'Sarana dan Prasarana (Kegiatan Akademik)', 'tipe': 'teks'},
                {'kode': 'C5.3.1.b', 'nama': 'Sarana dan Prasarana (Kegiatan Non Akademik)', 'tipe': 'teks'},
                {'kode': 'C5.3.2', 'nama': 'Keselamatan, Kesehatan Kerja dan Lingkungan (K3L)', 'tipe': 'teks'},
                {'kode': 'C5.4', 'nama': 'Analisis Faktor Keberhasilan dan Penghambat', 'tipe': 'teks'},
                {'kode': 'C5.5', 'nama': 'Strategi Perbaikan dan Pengembangan (Menggunakan Analisis SWOT)', 'tipe': 'teks'},
            ],
            'C6': [
                {'kode': 'C6.3.1', 'nama': 'Kualitas Mahasiswa', 'tipe': 'group'},
                {'kode': 'C6.3.2', 'nama': 'Prestasi Mahasiswa', 'tipe': 'group'},
                {'kode': 'C6.3.3', 'nama': 'Masa Studi, Lulusan Tepat Waktu, dan IPK', 'tipe': 'group'},
                {'kode': 'C6.3.4', 'nama': 'Keberhasilan Lulusan (Tracer Study)', 'tipe': 'group'},
                {'kode': 'C6.1', 'nama': 'Latar Belakang', 'tipe': 'teks'},
                {'kode': 'C6.2', 'nama': 'Kebijakan', 'tipe': 'teks'},
                {'kode': 'C6.3.1.a', 'nama': 'Kualitas Mahasiswa (Rasio mahasiswa terhadap DTPS)', 'tipe': 'teks'},
                {'kode': 'C6.3.1.b', 'nama': 'Kualitas Mahasiswa (Persentase mahasiswa asing)', 'tipe': 'teks'},
                {'kode': 'C6.3.3.a', 'nama': 'Masa Studi, Lulusan Tepat Waktu, dan IPK (IPK lulusan)', 'tipe': 'teks'},
                {'kode': 'C6.3.2.a', 'nama': 'Prestasi Mahasiswa (Prestasi akademik)', 'tipe': 'teks'},
                {'kode': 'C6.3.2.b', 'nama': 'Prestasi Mahasiswa (Prestasi nonakademik)', 'tipe': 'teks'},
                {'kode': 'C6.3.2.c', 'nama': 'Produk / jasa karya mahasiswa', 'tipe': 'teks'},
                {'kode': 'C6.3.3.b', 'nama': 'Masa Studi, Lulusan Tepat Waktu, dan IPK (Masa studi)', 'tipe': 'teks'},
                {'kode': 'C6.3.3.c', 'nama': 'Masa Studi, Lulusan Tepat Waktu, dan IPK (Lulusan tepat waktu)', 'tipe': 'teks'},
                {'kode': 'C6.3.3.d', 'nama': 'Persentase keberhasilan studi moda reguler', 'tipe': 'teks'},
                {'kode': 'C6.3.2.d', 'nama': 'Publikasi ilmiah mahasiswa', 'tipe': 'teks'},
                {'kode': 'C6.3.2.e', 'nama': 'Pagelaran / pameran / presentasi mahasiswa', 'tipe': 'teks'},
                {'kode': 'C6.3.2.f', 'nama': 'Luaran penelitian dan PkM yang dihasilkan mahasiswa', 'tipe': 'teks'},
                {'kode': 'C6.3.4.a', 'nama': 'Keberhasilan Lulusan (Tracer study)', 'tipe': 'teks'},
                {'kode': 'C6.3.4.b', 'nama': 'Keberhasilan Lulusan (Waktu tunggu)', 'tipe': 'teks'},
                {'kode': 'C6.3.4.c', 'nama': 'Keberhasilan Lulusan (Waktu tunggu moda reguler)', 'tipe': 'teks'},
                {'kode': 'C6.3.4.d', 'nama': 'Keberhasilan Lulusan (Kesesuaian bidang kerja)', 'tipe': 'teks'},
                {'kode': 'C6.3.4.e', 'nama': 'Keberhasilan Lulusan (Tingkat dan ukuran tempat kerja)', 'tipe': 'teks'},
                {'kode': 'C6.3.4.f', 'nama': 'Keberhasilan Lulusan (Tingkat kepuasan pengguna)', 'tipe': 'teks'},
                {'kode': 'C6.4', 'nama': 'Analisis Faktor Keberhasilan dan Penghambat', 'tipe': 'teks'},
                {'kode': 'C6.5', 'nama': 'Strategi Perbaikan dan Pengembangan (Menggunakan Analisis SWOT)', 'tipe': 'teks'},
            ],
            'C7': [
                {'kode': 'C7.3.1', 'nama': 'Sistem Penjaminan Mutu', 'tipe': 'group'},
                {'kode': 'C7.1', 'nama': 'Latar Belakang', 'tipe': 'teks'},
                {'kode': 'C7.2', 'nama': 'Kebijakan', 'tipe': 'teks'},
                {'kode': 'C7.3.1.a', 'nama': 'Keberadaan unit penjaminan dan komitmen pimpinan', 'tipe': 'teks'},
                {'kode': 'C7.3.1.b', 'nama': 'Ketersediaan Perangkat SPMI dan pengakuan mutu eksternal', 'tipe': 'teks'},
                {'kode': 'C7.3.1.c', 'nama': 'Indikator Kinerja Tambahan (IKT)', 'tipe': 'teks'},
                {'kode': 'C7.3.1.d', 'nama': 'Keterlaksanaan penjaminan mutu dan audit mutu internal', 'tipe': 'teks'},
                {'kode': 'C7.3.1.e', 'nama': 'Evaluasi capaian kinerja', 'tipe': 'teks'},
                {'kode': 'C7.3.1.f', 'nama': 'Kepuasan Pemangku kepentingan', 'tipe': 'teks'},
                {'kode': 'C7.4', 'nama': 'Analisis Faktor Keberhasilan dan Penghambat Pelaksanaan SPMI', 'tipe': 'teks'},
                {'kode': 'C7.5', 'nama': 'Strategi Perbaikan dan Pengembangan (Menggunakan Analisis SWOT)', 'tipe': 'teks'},
            ],
        }

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

            # Seed specific Indicators for this kriteria
            k_indikators = lam_teknik_indicators.get(k["kode"], [])
            for ind_data in k_indikators:
                kode_ind = ind_data["kode"]
                deskripsi_ind = ind_data["nama"]

                existing_ind = (
                    db.query(Indikator)
                    .filter(Indikator.kode_indikator == kode_ind)
                    .first()
                )
                if not existing_ind:
                    ind = Indikator(
                        kriteria_id=kriteria.id,
                        kode_indikator=kode_ind,
                        deskripsi=deskripsi_ind,
                        tipe_input=ind_data["tipe"],
                    )
                    db.add(ind)
                    print(f"  Seeded indikator: {kode_ind} - {deskripsi_ind}")
                else:
                    if existing_ind.deskripsi != deskripsi_ind:
                        existing_ind.deskripsi = deskripsi_ind
                        db.add(existing_ind)

        db.commit()

        # ==========================================
        # Seed Target Akreditasi
        # 2026: IF (target skor terisi), TE/Teknik Tenaga Listrik (belum set target skor)
        # 2025: EL/Teknik Elektro (target skor terisi)
        # ==========================================

        def upsert_target(prodi_obj, tahun, target_skor_val, deadline_val, is_aktif_val):
            existing = (
                db.query(TargetAkreditasi)
                .filter(
                    TargetAkreditasi.program_studi_id == prodi_obj.id,
                    TargetAkreditasi.tahun_akreditasi == tahun,
                )
                .first()
            )
            if not existing:
                t = TargetAkreditasi(
                    program_studi_id=prodi_obj.id,
                    tahun_akreditasi=tahun,
                    target_skor=target_skor_val,
                    deadline=deadline_val,
                    is_aktif=is_aktif_val,
                )
                db.add(t)
                print(f"  Seeded TargetAkreditasi {prodi_obj.kode} {tahun}")
            else:
                existing.target_skor = target_skor_val
                existing.deadline = deadline_val
                existing.is_aktif = is_aktif_val
                print(f"  Updated TargetAkreditasi {prodi_obj.kode} {tahun}")
            db.commit()

        def deactivate_other_targets(prodi_obj, keep_tahun):
            """Nonaktifkan semua target prodi ini selain tahun yang ditentukan."""
            others = (
                db.query(TargetAkreditasi)
                .filter(
                    TargetAkreditasi.program_studi_id == prodi_obj.id,
                    TargetAkreditasi.tahun_akreditasi != keep_tahun,
                )
                .all()
            )
            for o in others:
                o.is_aktif = False
            if others:
                db.commit()
                print(f"  Deactivated {len(others)} stale target(s) for {prodi_obj.kode} (non-{keep_tahun})")

        # --- IF: aktif 2026, target skor terisi ---
        if "IF" in prodis:
            deactivate_other_targets(prodis["IF"], keep_tahun=2026)
            upsert_target(
                prodis["IF"],
                tahun=2026,
                target_skor_val=340.0,
                deadline_val=date.today() + timedelta(days=60),
                is_aktif_val=True,
            )

        # --- TTL (Teknik Tenaga Listrik): aktif 2026, BELUM set target skor ---
        if "TTL" in prodis:
            deactivate_other_targets(prodis["TTL"], keep_tahun=2026)
            upsert_target(
                prodis["TTL"],
                tahun=2026,
                target_skor_val=None,
                deadline_val=None,
                is_aktif_val=True,
            )

        # --- TK (Teknik Telekomunikasi): aktif 2026 ---
        if "TK" in prodis:
            deactivate_other_targets(prodis["TK"], keep_tahun=2026)
            upsert_target(
                prodis["TK"],
                tahun=2026,
                target_skor_val=None,
                deadline_val=None,
                is_aktif_val=True,
            )

        # --- STI (Sistem dan Teknologi Informasi): aktif 2026 ---
        if "STI" in prodis:
            deactivate_other_targets(prodis["STI"], keep_tahun=2026)
            upsert_target(
                prodis["STI"],
                tahun=2026,
                target_skor_val=None,
                deadline_val=None,
                is_aktif_val=True,
            )

        # --- BM (Teknik Biomedis): aktif 2026 ---
        if "BM" in prodis:
            deactivate_other_targets(prodis["BM"], keep_tahun=2026)
            upsert_target(
                prodis["BM"],
                tahun=2026,
                target_skor_val=None,
                deadline_val=None,
                is_aktif_val=True,
            )

        # --- EL (Teknik Elektro): aktif 2025, target skor terisi ---
        if "EL" in prodis:
            deactivate_other_targets(prodis["EL"], keep_tahun=2025)
            upsert_target(
                prodis["EL"],
                tahun=2025,
                target_skor_val=300.0,
                deadline_val=None,  # Tidak ada deadline spesifik untuk testing
                is_aktif_val=True,
            )

        try:
            from scripts.seed_simulasi import seed as seed_simulasi

            seed_simulasi()
        except Exception as e:
            print(f"Warning: failed to seed simulation matrix: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
