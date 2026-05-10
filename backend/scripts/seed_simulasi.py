import app.models  # noqa: F401
from app.db import SessionLocal
from app.models.simulasi import IndikatorSimulasi, KomponenPenilaian, MatriksAkreditasi


def get_or_create_matriks(
    db, lembaga, jenjang, bobot_input, bobot_proses, bobot_output
):
    matriks = (
        db.query(MatriksAkreditasi).filter_by(lembaga=lembaga, jenjang=jenjang).first()
    )
    if not matriks:
        matriks = MatriksAkreditasi(lembaga=lembaga, jenjang=jenjang)
        db.add(matriks)
        db.flush()

        db.add_all(
            [
                KomponenPenilaian(
                    matriks_id=matriks.id, nama="Input", bobot=bobot_input
                ),
                KomponenPenilaian(
                    matriks_id=matriks.id, nama="Proses", bobot=bobot_proses
                ),
                KomponenPenilaian(
                    matriks_id=matriks.id, nama="Output", bobot=bobot_output
                ),
            ]
        )
        db.flush()
    return matriks


def seed():
    db = SessionLocal()
    try:
        print("Memulai seeding seluruh matriks (TEKNIK & INFOKOM)...")

        # 1. TEKNIK SARJANA (Bobot Asumsi: 25, 35, 40)
        m_ts = get_or_create_matriks(db, "TEKNIK", "SARJANA", 25.0, 35.0, 40.0)

        # 2. TEKNIK MAGISTER (Bobot Asumsi: 25, 35, 40)
        m_tm = get_or_create_matriks(db, "TEKNIK", "MAGISTER", 25.0, 35.0, 40.0)

        # 3. TEKNIK DOKTOR (Bobot Asumsi: 25, 35, 40)
        m_td = get_or_create_matriks(db, "TEKNIK", "DOKTOR", 25.0, 35.0, 40.0)

        # 4. INFOKOM SARJANA (Bobot Asumsi: 15, 30, 55 - based on Plan.MD)
        m_is = get_or_create_matriks(db, "INFOKOM", "SARJANA", 15.0, 30.0, 55.0)

        # 5. INFOKOM MAGISTER (Bobot Asumsi: 15, 30, 55)
        m_im = get_or_create_matriks(db, "INFOKOM", "MAGISTER", 15.0, 30.0, 55.0)

        # Get Komponen IDs for TEKNIK SARJANA to attach these indicators
        komponen_input = (
            db.query(KomponenPenilaian)
            .filter_by(matriks_id=m_ts.id, nama="Input")
            .first()
        )
        komponen_proses = (
            db.query(KomponenPenilaian)
            .filter_by(matriks_id=m_ts.id, nama="Proses")
            .first()
        )
        komponen_output = (
            db.query(KomponenPenilaian)
            .filter_by(matriks_id=m_ts.id, nama="Output")
            .first()
        )

        # TEKNIK SARJANA Indicators (First 11 extracted from Matriks Penilaian Sarjana)
        indikator_data = [
            # KRITERIA 1, 2, 3 (Bagian INPUT / Tata Pamong / Keuangan)
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "1",
                "nama_indikator": "Kekhasan VMTS",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "2",
                "nama_indikator": "Mekanisme penyusunan VMTS",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "3",
                "nama_indikator": "Tingkat pemahaman dan pencapaian VMTS",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "4",
                "nama_indikator": "Sistem tata pamong",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "5",
                "nama_indikator": "Komitmen pimpinan dan kemampuan manajerial",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "6",
                "nama_indikator": "Kerja sama",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "7",
                "nama_indikator": "Pelaksanaan kerja sama",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "8",
                "nama_indikator": "Pengelolaan keuangan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "9",
                "nama_indikator": "Biaya Operasional Pendidikan (BOP)",
                "tipe_evaluasi": "LINEAR_SCALE",
                "konfigurasi_rumus": {
                    "min": 0,
                    "max": 20000000,
                    "formula": "BOP / 5000000",
                },
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "10",
                "nama_indikator": "Dana Penelitian DTPS (DPD)",
                "tipe_evaluasi": "LINEAR_SCALE",
                "konfigurasi_rumus": {
                    "min": 0,
                    "max": 10000000,
                    "formula": "(2 * DPD) / 5000000",
                },
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "11",
                "nama_indikator": "Dana PkM (DPkMD)",
                "tipe_evaluasi": "LINEAR_SCALE",
                "konfigurasi_rumus": {
                    "min": 0,
                    "max": 5000000,
                    "formula": "(4 * DPkMD) / 5000000",
                },
            },
            # PROSES & OUTPUT (Indikator 12 - 25)
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "12",
                "nama_indikator": "Pemutakhiran kurikulum",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "13",
                "nama_indikator": "Profil lulusan dan CPL",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "14",
                "nama_indikator": "Kesesuaian dan tinjauan CPL",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "15",
                "nama_indikator": "Rencana Proses Pembelajaran (RPS)",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "16",
                "nama_indikator": "Proses Pembelajaran",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "17",
                "nama_indikator": "Integrasi Penelitian dan PkM dalam pembelajaran",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "18",
                "nama_indikator": "Pembelajaran praktikum/lapangan (PJP)",
                "tipe_evaluasi": "PIECEWISE",
                "konfigurasi_rumus": {
                    "conditions": [
                        {"condition": "PJP < 0.2", "formula": "20 * PJP"},
                        {"condition": "0.2 <= PJP <= 0.5", "formula": "4"},
                        {"condition": "PJP > 0.5", "formula": "8 - (8 * PJP)"},
                    ]
                },
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "19",
                "nama_indikator": "Basic sciences dan matematika",
                "tipe_evaluasi": "STEP_SCALE",
                "konfigurasi_rumus": {
                    "steps": [
                        {"min": 25, "max": 999, "score": 4},
                        {"min": 20, "max": 24, "score": 3},
                        {"min": 15, "max": 19, "score": 2},
                        {"min": 10, "max": 14, "score": 1},
                        {"min": 0, "max": 9, "score": 0},
                    ]
                },
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "20",
                "nama_indikator": "Proyek rekayasa penciri bidang prodi (Capstone design)",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "21",
                "nama_indikator": "Suasana Akademik",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "22",
                "nama_indikator": "Kesesuaian Penelitian",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "23",
                "nama_indikator": "Penelitian melibatkan mahasiswa (PPDMhs)",
                "tipe_evaluasi": "LINEAR_SCALE",
                "konfigurasi_rumus": {
                    "min": 0,
                    "max": 0.5,
                    "formula": "1 + (6 * PPDMhs)",
                },
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "24",
                "nama_indikator": "Kesesuaian PkM",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4},
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "25",
                "nama_indikator": "PkM melibatkan mahasiswa (PKDMhs)",
                "tipe_evaluasi": "LINEAR_SCALE",
                "konfigurasi_rumus": {
                    "min": 0,
                    "max": 0.5,
                    "formula": "1 + (6 * PKDMhs)",
                },
            },
        ]


        # --- TEKNIK SARJANA (26-End) ---
        indikator_data.extend([
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "26",
                "nama_indikator": "Profil Dosen  Kecukupan Jumlah",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "27",
                "nama_indikator": "Kualifikasi akademik",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "28",
                "nama_indikator": "Jabatan akademik",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "29",
                "nama_indikator": "Tenaga",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "30",
                "nama_indikator": "Beban kerja",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "31",
                "nama_indikator": "Kinerja DTPS  Kegiatan penelitian",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "32",
                "nama_indikator": "Kegiatan PkM DTPS",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "33",
                "nama_indikator": "Publikasi ilmiah dengan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "34",
                "nama_indikator": "Luaran penelitian dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "35",
                "nama_indikator": "Persentase DTPS yang",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "36",
                "nama_indikator": "Persentase Karya ilmiah",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "37",
                "nama_indikator": "Persentase DTPS yang",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "38",
                "nama_indikator": "Sarana dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "39",
                "nama_indikator": "Keselamatan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "40",
                "nama_indikator": "Mahasiswa  Rasio jumlah",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "41",
                "nama_indikator": "Mahasiswa",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "42",
                "nama_indikator": "IPK lulusan  IPK lulusan.",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "43",
                "nama_indikator": "Prestasi",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "44",
                "nama_indikator": "Masa studi  Masa studi.",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "45",
                "nama_indikator": "Persentase",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "46",
                "nama_indikator": "Publikasi ilmiah",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "47",
                "nama_indikator": "Luaran penelitian dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "48",
                "nama_indikator": "Tracer Study  Pelaksanaan tracer",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "49",
                "nama_indikator": "Waktu tunggu  Waktu tunggu.",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "50",
                "nama_indikator": "Kesesuaian",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "51",
                "nama_indikator": "Tingkat dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "52",
                "nama_indikator": "Tingkat",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "53",
                "nama_indikator": "Keberadaan unit",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "54",
                "nama_indikator": "Indikator Kinerja",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "55",
                "nama_indikator": "Keterlaksanaan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "56",
                "nama_indikator": "Evaluasi",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "57",
                "nama_indikator": "Kepuasan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "58",
                "nama_indikator": "Analisis",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "59",
                "nama_indikator": "Tujuan Strategis",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "60",
                "nama_indikator": "Program",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
        ])
        # --- TEKNIK MAGISTER ---
        komponen_input = db.query(KomponenPenilaian).filter_by(matriks_id=m_tm.id, nama="Input").first()
        komponen_proses = db.query(KomponenPenilaian).filter_by(matriks_id=m_tm.id, nama="Proses").first()
        komponen_output = db.query(KomponenPenilaian).filter_by(matriks_id=m_tm.id, nama="Output").first()
        indikator_data.extend([
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "1",
                "nama_indikator": "Kekhasan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "2",
                "nama_indikator": "Mekanisme",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "3",
                "nama_indikator": "Tingkat",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "4",
                "nama_indikator": "Sistem tata",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "5",
                "nama_indikator": "Komitmen",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "6",
                "nama_indikator": "Relevansi",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "7",
                "nama_indikator": "Pelaksanaan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "8",
                "nama_indikator": "Pengelolaan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "9",
                "nama_indikator": "Biaya",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "10",
                "nama_indikator": "Dana Penelitian DTPS",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "11",
                "nama_indikator": "Dana PkM (DPkMD).",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "12",
                "nama_indikator": "Pemutakhira",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "13",
                "nama_indikator": "Profil lulusan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "14",
                "nama_indikator": "Kesesuaian",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "15",
                "nama_indikator": "Kualitas Input",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "16",
                "nama_indikator": "Rencana",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "17",
                "nama_indikator": "Proses",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "18",
                "nama_indikator": "Integrasi",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "19",
                "nama_indikator": "Suasana",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "20",
                "nama_indikator": "Penelitian  Kesesuaian penelitian",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "21",
                "nama_indikator": "Penelitian DTPS yang",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "22",
                "nama_indikator": "Penelitian DTPS yang",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "23",
                "nama_indikator": "PkM Kesesuaian PkM",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "24",
                "nama_indikator": "PkM DTPS yang",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "25",
                "nama_indikator": "Profil Dosen  Kecukupan Jumlah",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "26",
                "nama_indikator": "Jabatan akademik",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "27",
                "nama_indikator": "Tenaga",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "28",
                "nama_indikator": "Beban kerja",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "29",
                "nama_indikator": "Kinerja DTPS  Kegiatan penelitian",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "30",
                "nama_indikator": "Kegiatan PkM DTPS",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "31",
                "nama_indikator": "Publikasi ilmiah",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "32",
                "nama_indikator": "Luaran penelitian dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "33",
                "nama_indikator": "Persentase DTPS",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "34",
                "nama_indikator": "Persentase Karya",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "35",
                "nama_indikator": "Rekognisi DTPS",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "36",
                "nama_indikator": "Sarana dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "37",
                "nama_indikator": "Keselamatan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "38",
                "nama_indikator": "Mahasiswa",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "39",
                "nama_indikator": "IPK Lulusan  IPK lulusan.",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "40",
                "nama_indikator": "Prestasi",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "41",
                "nama_indikator": "Masa studi  Masa studi.",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "42",
                "nama_indikator": "Persentase",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "43",
                "nama_indikator": "Publikasi",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "44",
                "nama_indikator": "Luaran penelitian dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "45",
                "nama_indikator": "Tracer Study  Pelaksanaan tracer",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "46",
                "nama_indikator": "Kesesuaian",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "47",
                "nama_indikator": "Tingkat",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "48",
                "nama_indikator": "Keberadaan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "49",
                "nama_indikator": "Indikator",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "50",
                "nama_indikator": "Keterlaksana",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "51",
                "nama_indikator": "Evaluasi",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "52",
                "nama_indikator": "Kepuasan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "53",
                "nama_indikator": "Analisis",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "54",
                "nama_indikator": "Tujuan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "55",
                "nama_indikator": "Program",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
        ])
        # --- TEKNIK DOKTOR ---
        komponen_input = db.query(KomponenPenilaian).filter_by(matriks_id=m_td.id, nama="Input").first()
        komponen_proses = db.query(KomponenPenilaian).filter_by(matriks_id=m_td.id, nama="Proses").first()
        komponen_output = db.query(KomponenPenilaian).filter_by(matriks_id=m_td.id, nama="Output").first()
        indikator_data.extend([
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "1",
                "nama_indikator": "Kekhasan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "2",
                "nama_indikator": "Mekanisme",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "3",
                "nama_indikator": "Tingkat",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "4",
                "nama_indikator": "Sistem tata",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "5",
                "nama_indikator": "Komitmen",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "6",
                "nama_indikator": "Relevansi dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "7",
                "nama_indikator": "Pelaksanaan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "8",
                "nama_indikator": "Pengelolaan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "9",
                "nama_indikator": "Biaya",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "10",
                "nama_indikator": "Dana Penelitian DTPS",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "11",
                "nama_indikator": "Dana PkM (DPkMD).",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "12",
                "nama_indikator": "Pemutakhiran",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "13",
                "nama_indikator": "Profil lulusan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "14",
                "nama_indikator": "Kesesuaian",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "15",
                "nama_indikator": "Kualitas Input",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "16",
                "nama_indikator": "Rencana",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "17",
                "nama_indikator": "Proses",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "18",
                "nama_indikator": "Integrasi",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "19",
                "nama_indikator": "Suasana",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "20",
                "nama_indikator": "Penelitian  Kesesuaian penelitian",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "21",
                "nama_indikator": "Penelitian DTPS yang",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "22",
                "nama_indikator": "Penelitian DTPS yang",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "23",
                "nama_indikator": "PkM Kesesuaian PkM dalam",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "24",
                "nama_indikator": "PkM DTPS yang sesuai",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "25",
                "nama_indikator": "Profil Dosen  Kecukupan Jumlah",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "26",
                "nama_indikator": "Jabatan akademik",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "27",
                "nama_indikator": "Tenaga",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "28",
                "nama_indikator": "Beban kerja",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "29",
                "nama_indikator": "Kinerja DTPS  Kegiatan penelitian",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "30",
                "nama_indikator": "Kegiatan PkM DTPS",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "31",
                "nama_indikator": "Publikasi ilmiah dengan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "32",
                "nama_indikator": "Luaran penelitian dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "33",
                "nama_indikator": "Publikasi ilmiah dengan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "34",
                "nama_indikator": "Persentase Karya ilmiah",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "35",
                "nama_indikator": "Persentase DTPS yang",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "36",
                "nama_indikator": "Sarana dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "37",
                "nama_indikator": "Keselamatan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "38",
                "nama_indikator": "Mahasiswa",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "39",
                "nama_indikator": "IPK Lulusan  IPK lulusan.",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "40",
                "nama_indikator": "Prestasi",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "41",
                "nama_indikator": "Masa studi  Masa studi.",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "42",
                "nama_indikator": "Persentase",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "43",
                "nama_indikator": "Publikasi ilmiah",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "44",
                "nama_indikator": "Luaran penelitian dan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "45",
                "nama_indikator": "Tracer Study  Pelaksanaan tracer study",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "46",
                "nama_indikator": "Keberadaan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "47",
                "nama_indikator": "Indikator",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "48",
                "nama_indikator": "Keterlaksanaan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "49",
                "nama_indikator": "Evaluasi",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "50",
                "nama_indikator": "Kepuasan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "51",
                "nama_indikator": "Analisis",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "52",
                "nama_indikator": "Tujuan",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "53",
                "nama_indikator": "Program",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
        ])
        # --- INFOKOM SARJANA ---
        komponen_input = db.query(KomponenPenilaian).filter_by(matriks_id=m_is.id, nama="Input").first()
        komponen_proses = db.query(KomponenPenilaian).filter_by(matriks_id=m_is.id, nama="Proses").first()
        komponen_output = db.query(KomponenPenilaian).filter_by(matriks_id=m_is.id, nama="Output").first()
        indikator_data.extend([
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "1",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "2",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "3",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "4",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "5",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "6",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "7",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "8",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "9",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "10",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "11",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "12",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "13",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "14",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "15",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "16",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "17",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "18",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "19",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "20",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "21",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "22",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "23",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "24",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "25",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "26",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "27",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "28",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "29",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "30",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "31",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "32",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "33",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "34",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "35",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "36",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "37",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "38",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "39",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "40",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "41",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "42",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "43",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "44",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "45",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "46",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "47",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "48",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "49",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "50",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "51",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "52",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "53",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "54",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "55",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "56",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "57",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "58",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "59",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "60",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "61",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "62",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "63",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "64",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "65",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "66",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "67",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "68",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "69",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "70",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "71",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "72",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "73",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "74",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "75",
                "nama_indikator": "A   1   10,0",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "76",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "77",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
        ])
        # --- INFOKOM MAGISTER ---
        komponen_input = db.query(KomponenPenilaian).filter_by(matriks_id=m_im.id, nama="Input").first()
        komponen_proses = db.query(KomponenPenilaian).filter_by(matriks_id=m_im.id, nama="Proses").first()
        komponen_output = db.query(KomponenPenilaian).filter_by(matriks_id=m_im.id, nama="Output").first()
        indikator_data.extend([
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "1",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "2",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "3",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "4",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "5",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "6",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "7",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "8",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "9",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "10",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_input.id,
                "kode_indikator": "11",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "12",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "13",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "14",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "15",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "16",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "17",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "18",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "19",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "20",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "21",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "22",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "23",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "24",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "25",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "26",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "27",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "28",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "29",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_proses.id,
                "kode_indikator": "30",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "31",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "32",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "33",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "34",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "35",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "36",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "37",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "38",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "39",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "40",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "41",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "42",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "43",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "44",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "45",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "46",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "47",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "48",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "49",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "50",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "51",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "52",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "53",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "54",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "55",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "56",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "57",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "58",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "59",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "60",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "61",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "62",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "63",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "64",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "65",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "66",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "67",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "68",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "69",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "70",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "71",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "72",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "73",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "74",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "75",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "76",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "77",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "78",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "79",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
            {
                "komponen_id": komponen_output.id,
                "kode_indikator": "80",
                "nama_indikator": "Matriks  Penilaian  Kinerja  Program  Studi  dan Suplemen  LA",
                "tipe_evaluasi": "DIRECT_SCORE",
                "konfigurasi_rumus": {"min": 0, "max": 4}
            },
        ])

        # Cleanup existing IndikatorSimulasi before inserting new ones
        db.query(IndikatorSimulasi).delete()

        indikators = [IndikatorSimulasi(**data) for data in indikator_data]
        db.add_all(indikators)

        db.commit()
        print(
            "Struktur Matriks dan Komponen berhasil di-seed untuk semua prodi/jenjang!"
        )

        # NOTE: Mem-parsing >80 aturan per PDF ke JSON secara akurat membutuhkan
        # model language ekstraksi per tabel seperti yang disarankan di PLAN.md ("Gunakan Gemini IDE...").
        # Skrip ini telah menyiapkan kerangka database untuk menampung JSON tersebut.
        # Pengguna dapat menambahkan file JSON hasil ekstraksi ke folder `docs/`
        # dan melooping isinya ke model `IndikatorSimulasi` di sini.

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
