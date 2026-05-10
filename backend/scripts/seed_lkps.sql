-- ============================================================
-- LKPS Sample Data Seed Script
-- Usage:
--   docker exec -i <db-container> psql -U postgres -d stei_accreditation < backend/scripts/seed_lkps.sql
--
-- Or from project root:
--   docker exec -i $(docker ps -qf "name=db") psql -U postgres -d stei_accreditation < backend/scripts/seed_lkps.sql
--
-- Safe to re-run: deletes existing data for this submission first.
-- Submission: Teknik Informatika IF (S1) — draft submission
-- ============================================================

-- ── Resolve IDs ──────────────────────────────────────────────
-- Ensure prodi IF exists (created by seed.py); get its ID dynamically.

DO $$
DECLARE
    v_prodi_id   UUID;
    v_sid        UUID;
    v_tahun_ts   INTEGER;
BEGIN

-- ── 1. Get or create the IF prodi ────────────────────────────
SELECT id INTO v_prodi_id FROM program_studi WHERE kode = 'IF';
IF v_prodi_id IS NULL THEN
    RAISE EXCEPTION 'Program studi IF not found. Run seed.py first.';
END IF;

-- ── 2. Update prodi profile fields ───────────────────────────
UPDATE program_studi SET
    alamat                          = 'Jl. Ganesha No. 10, Labtek VIII',
    kota                            = 'Bandung',
    kode_pos                        = '40132',
    nomor_telepon                   = '+62-22-2500935',
    email                           = 'informatika@stei.itb.ac.id',
    website                         = 'https://www.informatika.stei.itb.ac.id',
    no_sk_pendirian_pt              = 'PP No. 157 Tahun 1959',
    tanggal_sk_pendirian_pt         = '1959-09-02',
    pejabat_sk_pendirian_pt         = 'Presiden Republik Indonesia',
    no_sk_pembukaan_ps              = 'SK Mendikbud No. 0124/O/1979',
    tanggal_sk_pembukaan_ps         = '1979-04-28',
    pejabat_sk_pembukaan_ps         = 'Menteri Pendidikan dan Kebudayaan',
    tahun_pertama_menerima_mahasiswa = 1979,
    perguruan_tinggi                = 'Institut Teknologi Bandung',
    no_sk_ban_pt                    = '2030/SK/BAN-PT/Ak-PPJ/S/VII/2022'
WHERE id = v_prodi_id;

-- ── 3. Get or create a draft submission for IF's active accreditation year ──
SELECT tahun_akreditasi INTO v_tahun_ts
FROM target_akreditasi
WHERE program_studi_id = v_prodi_id AND is_aktif = true
ORDER BY tahun_akreditasi DESC
LIMIT 1;

IF v_tahun_ts IS NULL THEN
    v_tahun_ts := EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER;
END IF;

SELECT id INTO v_sid FROM lkps_submission
WHERE program_studi_id = v_prodi_id AND tahun_ts = v_tahun_ts
LIMIT 1;

IF v_sid IS NULL THEN
    -- find any template to use
    DECLARE v_tmpl_id UUID;
    BEGIN
        SELECT id INTO v_tmpl_id FROM lkps_template LIMIT 1;
        INSERT INTO lkps_submission (id, program_studi_id, template_id, tahun_ts, status)
        VALUES (gen_random_uuid(), v_prodi_id, v_tmpl_id, v_tahun_ts, 'draft')
        RETURNING id INTO v_sid;
        RAISE NOTICE 'Created new submission for TS %: %', v_tahun_ts, v_sid;
    END;
ELSE
    RAISE NOTICE 'Using existing submission for TS %: %', v_tahun_ts, v_sid;
END IF;

-- ── 4. Clear existing LKPS data for this submission ──────────
DELETE FROM lkps_vmts                WHERE submission_id = v_sid;
DELETE FROM lkps_kerjasama           WHERE submission_id = v_sid;
DELETE FROM lkps_penggunaan_dana     WHERE submission_id = v_sid;
DELETE FROM lkps_kurikulum           WHERE submission_id = v_sid;
DELETE FROM lkps_penelitian_summary  WHERE submission_id = v_sid;
DELETE FROM lkps_pkm_summary         WHERE submission_id = v_sid;
DELETE FROM lkps_dosen_profil        WHERE submission_id = v_sid;
DELETE FROM lkps_tenaga_kependidikan WHERE submission_id = v_sid;
DELETE FROM lkps_beban_kerja_dosen   WHERE submission_id = v_sid;
DELETE FROM lkps_publikasi_ilmiah    WHERE submission_id = v_sid;
DELETE FROM lkps_luaran_penelitian   WHERE submission_id = v_sid;
DELETE FROM lkps_produk_jasa         WHERE submission_id = v_sid;
DELETE FROM lkps_kinerja_dtps        WHERE submission_id = v_sid;
DELETE FROM lkps_sitasi_dtps         WHERE submission_id = v_sid;
DELETE FROM lkps_rekognisi_dtps      WHERE submission_id = v_sid;
DELETE FROM lkps_prasarana           WHERE submission_id = v_sid;
DELETE FROM lkps_k3l_dokumen         WHERE submission_id = v_sid;
DELETE FROM lkps_k3l_fasilitas       WHERE submission_id = v_sid;
DELETE FROM lkps_mahasiswa_aktif     WHERE submission_id = v_sid;
DELETE FROM lkps_ipk_lulusan         WHERE submission_id = v_sid;
DELETE FROM lkps_prestasi_mahasiswa  WHERE submission_id = v_sid;
DELETE FROM lkps_masa_studi          WHERE submission_id = v_sid;
DELETE FROM lkps_waktu_tunggu        WHERE submission_id = v_sid;
DELETE FROM lkps_kesesuaian_kerja    WHERE submission_id = v_sid;
DELETE FROM lkps_tempat_kerja        WHERE submission_id = v_sid;
DELETE FROM lkps_kepuasan_pengguna   WHERE submission_id = v_sid;
DELETE FROM lkps_penelitian_mahasiswa WHERE submission_id = v_sid;
DELETE FROM lkps_spmi_dokumen        WHERE submission_id = v_sid;
DELETE FROM lkps_spmi_pelaksanaan    WHERE submission_id = v_sid;
DELETE FROM lkps_integrasi_penelitian WHERE submission_id = v_sid;
DELETE FROM lkps_mk_basic_science    WHERE submission_id = v_sid;
DELETE FROM lkps_capstone_design     WHERE submission_id = v_sid;
DELETE FROM lkps_pembimbing_lapangan WHERE submission_id = v_sid;

-- ── Sheet 1 – VMTS ───────────────────────────────────────────
INSERT INTO lkps_vmts (id, submission_id, no, jenis_vmts, pernyataan, no_sk, link_dokumen) VALUES
(gen_random_uuid(), v_sid, 1, 'VMTS PT',
    'Menjadi universitas riset kelas dunia yang unggul, bermartabat, mandiri, dan diakui dunia internasional.',
    'SK-PT-001/2023', 'https://itb.ac.id/vmts/pt'),
(gen_random_uuid(), v_sid, 1, 'VMTS UPPS',
    'Menjadi sekolah tinggi teknik dan ilmu komputer yang unggul dan berperan aktif dalam pengembangan ilmu pengetahuan.',
    'SK-UPPS-001/2023', 'https://stei.itb.ac.id/vmts/upps'),
(gen_random_uuid(), v_sid, 1, 'Visi Keilmuan PS',
    'Menjadi program studi teknik informatika yang menghasilkan lulusan yang mampu berinovasi di bidang teknologi informasi.',
    'SK-PS-001/2023', 'https://if.itb.ac.id/vmts/ps'),
(gen_random_uuid(), v_sid, 2, 'Visi Keilmuan PS',
    'Mengembangkan ilmu komputasi, kecerdasan buatan, dan rekayasa perangkat lunak.',
    'SK-PS-002/2023', 'https://if.itb.ac.id/vmts/ps2');

-- ── Sheet 2b – Kerjasama ─────────────────────────────────────
INSERT INTO lkps_kerjasama (id, submission_id, jenis, lembaga_mitra, tingkat, judul_kegiatan, manfaat, tanggal_awal, tanggal_akhir, durasi_tahun, status_kerjasama, bukti_kerjasama) VALUES
(gen_random_uuid(), v_sid, 'pendidikan',  'Google LLC',          'internasional', 'Program Magang Google STEP',                  'Mahasiswa mendapat pengalaman industri global',    '2022-01-01', '2024-12-31', 3.0, 'Aktif', 'https://drive.google.com/bukti1'),
(gen_random_uuid(), v_sid, 'pendidikan',  'Microsoft Indonesia',  'nasional',      'Hibah Azure dan Pelatihan Cloud',              'Akses lisensi software dan platform cloud gratis', '2021-01-01', '2024-12-31', 4.0, 'Aktif', 'https://drive.google.com/bukti2'),
(gen_random_uuid(), v_sid, 'penelitian',  'BRIN',                 'nasional',      'Riset Kolaboratif Kecerdasan Artifisial',       'Publikasi bersama dan akses data riset nasional',  '2022-06-01', '2025-05-31', 3.0, 'Aktif', 'https://drive.google.com/bukti3'),
(gen_random_uuid(), v_sid, 'pendidikan',  'Osaka University',     'internasional', 'Program Pertukaran Pelajar',                   'Pertukaran mahasiswa dan dosen internasional',     '2020-01-01', '2025-12-31', 6.0, 'Aktif', 'https://drive.google.com/bukti4'),
(gen_random_uuid(), v_sid, 'pkm',         'Gojek Indonesia',      'nasional',      'Pelatihan Teknologi Digital untuk UMKM',       'Peningkatan literasi digital masyarakat',          '2023-01-01', '2024-12-31', 2.0, 'Aktif', 'https://drive.google.com/bukti5'),
(gen_random_uuid(), v_sid, 'pendidikan',  'Tokopedia',            'nasional',      'Program Beasiswa Mahasiswa Berprestasi',       'Beasiswa pendidikan dan pengembangan karir',       '2021-01-01', '2025-12-31', 5.0, 'Aktif', 'https://drive.google.com/bukti6'),
(gen_random_uuid(), v_sid, 'penelitian',  'LIPI',                 'nasional',      'Riset Terapan Komputasi Sains',                'Paten dan inovasi produk teknologi',               '2022-01-01', '2024-12-31', 3.0, 'Aktif', 'https://drive.google.com/bukti7');

-- ── Sheet 3b – Penelitian Summary ────────────────────────────
-- kode_sumber must match mapper keys: perguruan_tinggi_mandiri, dalam_negeri, luar_negeri
INSERT INTO lkps_penelitian_summary (id, submission_id, kode_sumber, ts2, ts1, ts) VALUES
(gen_random_uuid(), v_sid, 'perguruan_tinggi_mandiri', 15, 18, 20),
(gen_random_uuid(), v_sid, 'dalam_negeri',              5,  6,  8),
(gen_random_uuid(), v_sid, 'luar_negeri',               3,  4,  5);

-- ── Sheet 3c – PkM Summary ───────────────────────────────────
-- kode_sumber must match mapper keys: perguruan_tinggi_mandiri, dalam_negeri, luar_negeri
INSERT INTO lkps_pkm_summary (id, submission_id, kode_sumber, ts2, ts1, ts) VALUES
(gen_random_uuid(), v_sid, 'perguruan_tinggi_mandiri', 6, 7, 8),
(gen_random_uuid(), v_sid, 'dalam_negeri',             2, 3, 4),
(gen_random_uuid(), v_sid, 'luar_negeri',              1, 1, 2);

-- ── Sheet 3c – Integrasi Penelitian ke Pembelajaran ──────────
INSERT INTO lkps_integrasi_penelitian (id, submission_id, nama_dosen, judul_penelitian_pkm, mata_kuliah, bentuk_integrasi, tahun_ts2, tahun_ts1, tahun_ts, kesesuaian_peta_jalan, bukti_sahih, kesesuaian_rps) VALUES
(gen_random_uuid(), v_sid, 'Dr. Ahmad Budi Santoso',   'Deep Learning untuk Deteksi Anomali Jaringan',         'Kecerdasan Buatan',        'Studi kasus riset dijadikan bahan kuliah',    false, true, true, 'Sesuai', 'https://drive.google.com/integrasi1', 'Ya'),
(gen_random_uuid(), v_sid, 'Dr. Siti Rahayu Wulandari','Automated Testing Framework untuk Microservices',      'Rekayasa Perangkat Lunak', 'Hasil riset menjadi modul praktikum',        true,  true, true, 'Sesuai', 'https://drive.google.com/integrasi2', 'Ya'),
(gen_random_uuid(), v_sid, 'Dr. Hendra Kusuma',        'Optimasi Edge Computing untuk IoT',                    'Jaringan Komputer',        'Paper dijadikan bahan bacaan wajib',         false, true, true, 'Sesuai', 'https://drive.google.com/integrasi3', 'Ya');

-- ── Sheet 3d – MK Basic Science ──────────────────────────────
INSERT INTO lkps_mk_basic_science (id, submission_id, no, nama_mk, semester, jumlah_sks) VALUES
(gen_random_uuid(), v_sid, 1, 'Kalkulus I',                    1, 4.0),
(gen_random_uuid(), v_sid, 2, 'Kalkulus II',                   2, 4.0),
(gen_random_uuid(), v_sid, 3, 'Aljabar Linier dan Geometri',   2, 4.0),
(gen_random_uuid(), v_sid, 4, 'Probabilitas dan Statistika',   3, 3.0),
(gen_random_uuid(), v_sid, 5, 'Fisika Dasar',                  1, 3.0);

-- ── Sheet 3e – Capstone Design ───────────────────────────────
INSERT INTO lkps_capstone_design (id, submission_id, no, nama_mk_pendukung, sks_pendukung, nama_mk_capstone, sks_capstone, semester, cakupan_bahasan) VALUES
(gen_random_uuid(), v_sid, 1, 'Rekayasa Perangkat Lunak', 3.0, 'Tugas Akhir I',  3.0, 7, 'Perumusan masalah, tinjauan pustaka, perancangan sistem'),
(gen_random_uuid(), v_sid, 2, 'Metodologi Penelitian',    2.0, 'Tugas Akhir II', 3.0, 8, 'Implementasi, pengujian, evaluasi, dan presentasi');

-- ── Sheet 4a – Dosen Profil (DTPS) ───────────────────────────
INSERT INTO lkps_dosen_profil (id, submission_id, no, nama_dosen, nidn_nidk, kategori, prodi_sarjana, prodi_magister, prodi_doktor, bidang_keahlian, perusahaan_industri, kesesuaian_kompetensi, jabatan_akademik, no_sertifikat_pendidik, bidang_sertifikasi, lembaga_penerbit_sertifikasi, skip, stri, mk_diampu_ps_diakreditasi, kesesuaian_bidang_mk, mk_diampu_ps_lain) VALUES
(gen_random_uuid(), v_sid, 1, 'Dr. Ahmad Budi Santoso',     '0101010101', 'DTPS', 'Teknik Informatika ITB', 'Computer Science UI',       'Computer Science TU Delft',      'Kecerdasan Buatan, Machine Learning',       NULL, 'Sesuai', 'Profesor',      'SP-001/2019', 'AI & Machine Learning',  'AWS',      NULL, NULL, 'IF3270 Machine Learning, IF3280 Deep Learning', 'Sesuai', NULL),
(gen_random_uuid(), v_sid, 2, 'Dr. Siti Rahayu Wulandari',  '0202020202', 'DTPS', 'Teknik Informatika ITB', 'Software Engineering ITB',  'Software Engineering CMU',       'Rekayasa Perangkat Lunak, Software Testing', NULL, 'Sesuai', 'Lektor Kepala', 'SP-002/2018', 'Software Engineering',   'Oracle',   NULL, NULL, 'IF2110 RPL, IF3110 Pengembangan Web',           'Sesuai', NULL),
(gen_random_uuid(), v_sid, 3, 'Dr. Muhammad Rizky Pratama', '0303030303', 'DTPS', 'Teknik Informatika ITB', 'Informatika BINUS',         'Computer Science NUS',           'Keamanan Siber, Kriptografi',               NULL, 'Sesuai', 'Lektor Kepala', 'SP-003/2020', 'Cybersecurity',          'CompTIA',  NULL, NULL, 'IF3140 Keamanan Sistem dan Jaringan',           'Sesuai', NULL),
(gen_random_uuid(), v_sid, 4, 'Ir. Dewi Anggraeni, M.T.',   '0404040404', 'DTPS', 'Teknik Elektro ITB',     'Teknik Informatika ITB',    NULL,                             'Basis Data, Sistem Informasi',              NULL, 'Sesuai', 'Lektor',        'SP-004/2021', 'Electrical Engineering', 'IEEE',     NULL, NULL, 'IF2230 Organisasi dan Arsitektur Komputer',     'Sesuai', NULL),
(gen_random_uuid(), v_sid, 5, 'Dr. Hendra Kusuma',          '0505050505', 'DTPS', 'Teknik Informatika ITB', 'Computer Networks ITB',     'Distributed Systems ETH Zurich', 'Jaringan Komputer, Cloud Computing',        NULL, 'Sesuai', 'Profesor',      'SP-005/2017', 'Computer Networks',      'Cisco',    NULL, NULL, 'IF3130 Jaringan Komputer',                     'Sesuai', NULL);

-- ── Sheet 4b – Pembimbing Lapangan ───────────────────────────
INSERT INTO lkps_pembimbing_lapangan (id, submission_id, no, nama, industri, bidang_keinsinyuran, pengalaman_kerja_tahun, pendidikan_tinggi, kategori_sip, nomor_sip, tanggal_berakhir_sip, jumlah_bimbingan_3tahun) VALUES
(gen_random_uuid(), v_sid, 1, 'Ir. Hary Sudrajat, M.T.',      'PT Telkom Indonesia', 'Teknik Informatika', 15, 'S2', 'IPP', 'SIP-TI-2021-001', '2026-12-31', 12),
(gen_random_uuid(), v_sid, 2, 'Ir. Maya Kusumawati, M.T.',    'PT Gojek Indonesia',  'Teknik Informatika', 10, 'S2', 'IPM', 'SIP-TI-2022-002', '2027-06-30',  9);

-- ── Sheet 4c – Beban Kerja Dosen ─────────────────────────────
INSERT INTO lkps_beban_kerja_dosen (id, submission_id, no, nama_dosen, dtps, bk_ps_diakreditasi, bk_ps_lain_pt, bk_ps_luar_pt, bk_penelitian, bk_pkm, bk_tugas_tambahan) VALUES
(gen_random_uuid(), v_sid, 1, 'Dr. Ahmad Budi Santoso',     true,  6.0, 2.0, 0.0, 4.0, 2.0, 2.0),
(gen_random_uuid(), v_sid, 2, 'Dr. Siti Rahayu Wulandari',  true,  8.0, 0.0, 0.0, 4.0, 2.0, 2.0),
(gen_random_uuid(), v_sid, 3, 'Dr. Muhammad Rizky Pratama', true,  6.0, 0.0, 2.0, 6.0, 0.0, 2.0),
(gen_random_uuid(), v_sid, 4, 'Ir. Dewi Anggraeni, M.T.',   true, 10.0, 2.0, 0.0, 2.0, 2.0, 0.0),
(gen_random_uuid(), v_sid, 5, 'Dr. Hendra Kusuma',          true,  6.0, 0.0, 0.0, 6.0, 2.0, 2.0);

-- ── Sheet 5a – Tenaga Kependidikan ───────────────────────────
INSERT INTO lkps_tenaga_kependidikan (id, submission_id, no, nama, pendidikan_terakhir, sertifikat_kompetensi, unit_kerja) VALUES
(gen_random_uuid(), v_sid, 1, 'Budi Hartono',  'S1', 'Sertifikat IT Support, CompTIA A+',          'IF ITB'),
(gen_random_uuid(), v_sid, 2, 'Ani Susanti',   'D3', 'Sertifikat Administrasi Perkantoran',        'IF ITB'),
(gen_random_uuid(), v_sid, 3, 'Rudi Setiawan', 'S1', 'Sertifikat Teknisi Lab Komputer',            'IF ITB');

-- ── Sheet 2b – Penggunaan Dana ───────────────────────────────
-- kode must match mapper's _DANA_ROW keys exactly
INSERT INTO lkps_penggunaan_dana (id, submission_id, kode, upps_ts2, upps_ts1, upps_ts, ps_ts2, ps_ts1, ps_ts) VALUES
(gen_random_uuid(), v_sid, 'biaya_dosen',              3000000000, 3200000000, 3500000000, 1500000000, 1600000000, 1800000000),
(gen_random_uuid(), v_sid, 'biaya_tendik',              800000000,  900000000, 1000000000,  300000000,  350000000,  400000000),
(gen_random_uuid(), v_sid, 'biaya_op_pembelajaran',     500000000,  550000000,  600000000,  200000000,  220000000,  250000000),
(gen_random_uuid(), v_sid, 'biaya_op_tidak_langsung',   700000000,  750000000,  800000000,  280000000,  300000000,  320000000),
(gen_random_uuid(), v_sid, 'biaya_praktik_ppi',               0,        0,        0,        0,        0,        0),
(gen_random_uuid(), v_sid, 'biaya_investasi',          2000000000, 1800000000, 2500000000,  700000000,  650000000,  900000000),
(gen_random_uuid(), v_sid, 'biaya_kemahasiswaan',       400000000,  450000000,  500000000,  150000000,  170000000,  200000000),
(gen_random_uuid(), v_sid, 'biaya_penelitian',         1500000000, 1800000000, 2000000000,  800000000,  900000000, 1000000000),
(gen_random_uuid(), v_sid, 'biaya_pkm',                 500000000,  600000000,  700000000,  200000000,  250000000,  300000000);

-- ── Sheet 6b – Kurikulum ─────────────────────────────────────
INSERT INTO lkps_kurikulum (id, submission_id, no, semester, kode_mk, nama_mk, kompetensi, sks_kuliah, sks_seminar, sks_praktikum, konversi_jam, dokumen_rps, unit_penyelenggara) VALUES
(gen_random_uuid(), v_sid, 1, 1, 'IF1001', 'Dasar-Dasar Pemrograman',      'Mampu memprogram secara terstruktur',                3, 0, 1, 48, 'https://drive/rps-if1001', 'IF ITB'),
(gen_random_uuid(), v_sid, 2, 1, 'MA1101', 'Kalkulus I',                   'Memahami konsep kalkulus diferensial',               4, 0, 0, 48, 'https://drive/rps-ma1101', 'FMIPA ITB'),
(gen_random_uuid(), v_sid, 3, 2, 'IF2110', 'Algoritma dan Struktur Data',  'Mampu merancang algoritma efisien',                  3, 0, 1, 48, 'https://drive/rps-if2110', 'IF ITB'),
(gen_random_uuid(), v_sid, 4, 3, 'IF2211', 'Strategi Algoritma',           'Menguasai teknik desain algoritma lanjut',           3, 0, 0, 36, 'https://drive/rps-if2211', 'IF ITB'),
(gen_random_uuid(), v_sid, 5, 4, 'IF3110', 'Pengembangan Aplikasi Web',    'Mampu mengembangkan aplikasi web modern',            3, 0, 1, 48, 'https://drive/rps-if3110', 'IF ITB'),
(gen_random_uuid(), v_sid, 6, 5, 'IF4021', 'Kriptografi',                  'Memahami prinsip keamanan sistem informasi',         3, 0, 0, 36, 'https://drive/rps-if4021', 'IF ITB'),
(gen_random_uuid(), v_sid, 7, 6, 'IF4092', 'Tugas Akhir',                  'Mampu menyelesaikan proyek riset mandiri',           6, 0, 0, 72, 'https://drive/rps-if4092', 'IF ITB');

-- ── Sheet 6d – Masa Studi (S1) ───────────────────────────────
INSERT INTO lkps_masa_studi (id, submission_id, jenis_program, tahun_masuk, jumlah_masuk, jumlah_lulus_tepat_waktu, jumlah_lulus_terlambat, jumlah_tidak_lulus) VALUES
(gen_random_uuid(), v_sid, 'S1', 'TS-7', 110, 85, 18, 7),
(gen_random_uuid(), v_sid, 'S1', 'TS-6', 115, 88, 20, 7),
(gen_random_uuid(), v_sid, 'S1', 'TS-5', 120, 92, 21, 7),
(gen_random_uuid(), v_sid, 'S1', 'TS-4', 118, 90, 20, 8),
(gen_random_uuid(), v_sid, 'S1', 'TS-3', 122, 95, 20, 7),
(gen_random_uuid(), v_sid, 'S1', 'TS-2', 125, 98, 20, 7),
(gen_random_uuid(), v_sid, 'S1', 'TS-1', 128,100, 21, 7),
(gen_random_uuid(), v_sid, 'S1', 'TS',   130,  0,  0, 0);

-- ── Sheet 6e1 – Mahasiswa Aktif ──────────────────────────────
INSERT INTO lkps_mahasiswa_aktif (id, submission_id, no, program_studi_nama, prodi_diakreditasi, aktif_ts2, aktif_ts1, aktif_ts, asing_fulltime_ts2, asing_fulltime_ts1, asing_fulltime_ts, asing_parttime_ts2, asing_parttime_ts1, asing_parttime_ts) VALUES
(gen_random_uuid(), v_sid, 1, 'Teknik Informatika', true, 380, 390, 400, 2, 3, 5, 1, 1, 2);

-- ── Sheet 6e2 – IPK Lulusan ──────────────────────────────────
INSERT INTO lkps_ipk_lulusan (id, submission_id, periode, jumlah_lulusan, ipk_min, ipk_rata, ipk_maks) VALUES
(gen_random_uuid(), v_sid, 'TS-2', 85, 2.80, 3.42, 3.96),
(gen_random_uuid(), v_sid, 'TS-1', 92, 2.75, 3.48, 3.99),
(gen_random_uuid(), v_sid, 'TS',   98, 2.90, 3.51, 4.00);

-- ── Sheet 6e3 – Prestasi Mahasiswa ───────────────────────────
INSERT INTO lkps_prestasi_mahasiswa (id, submission_id, jenis, no, nama_kegiatan, waktu_perolehan, tingkat, prestasi_dicapai) VALUES
(gen_random_uuid(), v_sid, 'akademik',     1, 'Olimpiade Informatika Nasional 2023',        '2023-10-15', 'Nasional',      'Juara 1'),
(gen_random_uuid(), v_sid, 'akademik',     2, 'International Collegiate Programming Contest 2023', '2023-11-20', 'Internasional', 'Medali Perunggu'),
(gen_random_uuid(), v_sid, 'akademik',     3, 'Hackathon Google DevFest 2023',              '2023-12-01', 'Internasional', 'Runner Up'),
(gen_random_uuid(), v_sid, 'non_akademik', 1, 'Kompetisi Robot Nasional 2023',              '2023-09-10', 'Nasional',      'Juara 2'),
(gen_random_uuid(), v_sid, 'non_akademik', 2, 'Lomba Desain UI/UX IDN Times Award 2023',   '2023-08-25', 'Nasional',      'Juara 1'),
(gen_random_uuid(), v_sid, 'non_akademik', 3, 'Asia Pacific ICT Award 2022',               '2022-11-15', 'Internasional', 'Silver Award');

-- ── Produk/Jasa Mahasiswa (section 6e4) ──────────────────────
INSERT INTO lkps_produk_jasa (id, submission_id, sumber, nama_pembuat, nama_produk_jasa, deskripsi, bukti) VALUES
(gen_random_uuid(), v_sid, 'mahasiswa', 'Bima Prasetyo', 'SmartCampus App', 'Aplikasi manajemen kampus berbasis AI karya mahasiswa IF', 'https://drive.google.com/produk-mhs1');

-- ── Sheet 6f1 – Waktu Tunggu ─────────────────────────────────
INSERT INTO lkps_waktu_tunggu (id, submission_id, jenis_program, tahun_lulus, jumlah_lulusan, jumlah_terlacak, jumlah_dipesan_sebelum_lulus, wt_lt_3bulan, wt_3_6bulan, wt_gt_6bulan) VALUES
(gen_random_uuid(), v_sid, 'S1', 'TS-2', 103, 95, 45, 60, 25, 10),
(gen_random_uuid(), v_sid, 'S1', 'TS-1', 108,100, 50, 65, 25, 10);

-- ── Sheet 6f2 – Kesesuaian Kerja ────────────────────────────
INSERT INTO lkps_kesesuaian_kerja (id, submission_id, tahun_lulus, jumlah_lulusan, jumlah_terlacak, kesesuaian_rendah, kesesuaian_sedang, kesesuaian_tinggi) VALUES
(gen_random_uuid(), v_sid, 'TS-2', 103, 95,  5, 15, 75),
(gen_random_uuid(), v_sid, 'TS-1', 108,100,  4, 16, 80);

-- ── Sheet 6g1 – Tempat Kerja ─────────────────────────────────
INSERT INTO lkps_tempat_kerja (id, submission_id, tahun_lulus, jumlah_lulusan, jumlah_pengguna_tanggapan, jumlah_terlacak, bekerja_lokal, bekerja_nasional, bekerja_multinasional) VALUES
(gen_random_uuid(), v_sid, 'TS-2', 103, 80, 95, 10, 60, 25),
(gen_random_uuid(), v_sid, 'TS-1', 108, 85,100,  8, 65, 27);

-- ── Sheet 6g2 – Kepuasan Pengguna ────────────────────────────
INSERT INTO lkps_kepuasan_pengguna (id, submission_id, no, jenis_kemampuan, sangat_baik, baik, cukup, kurang, rencana_tindak_lanjut) VALUES
(gen_random_uuid(), v_sid, 1, 'Integritas (etika dan moral)',                   75.00, 20.00, 5.00, 0.00, 'Penguatan nilai etika profesi dalam kurikulum'),
(gen_random_uuid(), v_sid, 2, 'Keahlian berdasarkan bidang ilmu (kompetensi utama)', 70.00, 25.00, 5.00, 0.00, 'Peningkatan hands-on experience'),
(gen_random_uuid(), v_sid, 3, 'Bahasa Inggris',                                55.00, 35.00, 8.00, 2.00, 'Program English for Professional Communication'),
(gen_random_uuid(), v_sid, 4, 'Penggunaan teknologi informasi',                80.00, 18.00, 2.00, 0.00, 'Integrasi tools terbaru dalam pembelajaran'),
(gen_random_uuid(), v_sid, 5, 'Komunikasi',                                    65.00, 30.00, 5.00, 0.00, 'Workshop public speaking dan presentasi'),
(gen_random_uuid(), v_sid, 6, 'Kerjasama tim',                                 72.00, 25.00, 3.00, 0.00, 'Penguatan proyek berbasis tim'),
(gen_random_uuid(), v_sid, 7, 'Pengembangan diri',                             68.00, 28.00, 4.00, 0.00, 'Program mentoring dan pengembangan karir');

-- ── Sheet 4d (DTPS akademik) and 6e1 (mahasiswa akademik) – Publikasi Ilmiah ─
-- kode_publikasi and jenis_program must match mapper's _PUBLIKASI_ROW_AKADEMIK keys
INSERT INTO lkps_publikasi_ilmiah (id, submission_id, sumber, jenis_program, kode_publikasi, ts2, ts1, ts) VALUES
(gen_random_uuid(), v_sid, 'dtps',      'akademik', 'jurnal_nasional_tidak_terakreditasi',     3,  4,  5),
(gen_random_uuid(), v_sid, 'dtps',      'akademik', 'jurnal_nasional_terakreditasi',           10, 12, 15),
(gen_random_uuid(), v_sid, 'dtps',      'akademik', 'jurnal_internasional',                    5,  6,  8),
(gen_random_uuid(), v_sid, 'dtps',      'akademik', 'jurnal_internasional_bereputasi',         8, 10, 12),
(gen_random_uuid(), v_sid, 'dtps',      'akademik', 'prosiding_nasional',                      8, 10, 12),
(gen_random_uuid(), v_sid, 'dtps',      'akademik', 'prosiding_internasional_tidak_terindeks', 4,  5,  6),
(gen_random_uuid(), v_sid, 'dtps',      'akademik', 'prosiding_internasional_terindeks',      12, 14, 16),
(gen_random_uuid(), v_sid, 'mahasiswa', 'akademik', 'jurnal_nasional_tidak_terakreditasi',     2,  3,  5),
(gen_random_uuid(), v_sid, 'mahasiswa', 'akademik', 'jurnal_nasional_terakreditasi',           5,  7,  9),
(gen_random_uuid(), v_sid, 'mahasiswa', 'akademik', 'jurnal_internasional',                    3,  4,  6),
(gen_random_uuid(), v_sid, 'mahasiswa', 'akademik', 'jurnal_internasional_bereputasi',         2,  3,  5),
(gen_random_uuid(), v_sid, 'mahasiswa', 'akademik', 'prosiding_nasional',                     10, 12, 16),
(gen_random_uuid(), v_sid, 'mahasiswa', 'akademik', 'prosiding_internasional_tidak_terindeks', 3,  4,  6),
(gen_random_uuid(), v_sid, 'mahasiswa', 'akademik', 'prosiding_internasional_terindeks',       8, 10, 14);

-- ── Sheet 6i – Luaran Penelitian ─────────────────────────────
INSERT INTO lkps_luaran_penelitian (id, submission_id, sumber, jenis_luaran, judul, tanggal, nomor_paten, nomor_hki, status_tkt, nomor_sertifikat_tkt, nomor_isbn, status_mahasiswa, keterangan) VALUES
(gen_random_uuid(), v_sid, 'dtps',      'paten',     'Sistem Deteksi Anomali Berbasis Deep Learning',   '2023-06-15', 'P00202312345', NULL,           NULL,    NULL,             NULL,                NULL,    'Terdaftar di DJKI'),
(gen_random_uuid(), v_sid, 'dtps',      'hak_cipta', 'Algoritma Optimasi Jadwal Adaptif',               '2023-09-01', NULL,           'EC00202387654', NULL,    NULL,             NULL,                NULL,    'Hak Cipta Program Komputer'),
(gen_random_uuid(), v_sid, 'dtps',      'buku',      'Pengantar Kecerdasan Buatan Modern',              '2022-03-01', NULL,           NULL,            NULL,    NULL,             '978-979-456-789-0', NULL,    'Penerbit ITB Press'),
(gen_random_uuid(), v_sid, 'dtps',      'teknologi', 'Aplikasi Manajemen Akademik Berbasis AI',         '2023-11-01', NULL,           NULL,            'TKT-6', 'TKT-2023-001',   NULL,                NULL,    'Siap dikomersialkan'),
(gen_random_uuid(), v_sid, 'mahasiswa', 'hak_cipta', 'Framework Pengembangan Aplikasi IoT',             '2023-07-15', NULL,           'EC00202311111', NULL,    NULL,             NULL,                'Lulus', 'Tugas Akhir Mahasiswa'),
(gen_random_uuid(), v_sid, 'mahasiswa', 'teknologi', 'Chatbot Layanan Akademik',                        '2023-10-01', NULL,           NULL,            'TKT-4', 'TKT-2023-002',   NULL,                'Aktif', 'Capstone project'),
(gen_random_uuid(), v_sid, 'mahasiswa', 'buku',      'Pemrograman Web Modern',                          '2022-08-01', NULL,           NULL,            NULL,    NULL,             '978-979-111-222-3', 'Lulus', 'Buku ajar kolaborasi dosen-mahasiswa');

-- ── Sheet 6j – Produk/Jasa DTPS ─────────────────────────────
INSERT INTO lkps_produk_jasa (id, submission_id, sumber, nama_pembuat, nama_produk_jasa, deskripsi, bukti) VALUES
(gen_random_uuid(), v_sid, 'dtps', 'Dr. Ahmad Budi Santoso', 'AI Diagnostic Tool',       'Alat bantu diagnosis berbasis machine learning untuk sektor kesehatan', 'https://drive.google.com/produk1'),
(gen_random_uuid(), v_sid, 'dtps', 'Dr. Hendra Kusuma',      'Network Security Monitor', 'Sistem monitoring keamanan jaringan real-time',                         'https://drive.google.com/produk2');

-- ── Sheet 6k – Kinerja DTPS ──────────────────────────────────
INSERT INTO lkps_kinerja_dtps (id, submission_id, no, nama_dosen, ts2, ts1, ts, keterangan) VALUES
(gen_random_uuid(), v_sid, 1, 'Dr. Ahmad Budi Santoso',    3, 4, 5, 'Penelitian aktif di bidang AI'),
(gen_random_uuid(), v_sid, 2, 'Dr. Siti Rahayu Wulandari', 4, 4, 5, 'Aktif menghasilkan paper di konferensi internasional'),
(gen_random_uuid(), v_sid, 3, 'Dr. Hendra Kusuma',         2, 3, 4, 'Riset jaringan komputer dan cloud');

-- ── Sheet 6l – Sitasi DTPS ───────────────────────────────────
INSERT INTO lkps_sitasi_dtps (id, submission_id, no, nama_dosen, judul_artikel, jumlah_sitasi) VALUES
(gen_random_uuid(), v_sid, 1, 'Dr. Ahmad Budi Santoso',    'Deep Learning for Anomaly Detection in Network Traffic',         245),
(gen_random_uuid(), v_sid, 2, 'Dr. Siti Rahayu Wulandari', 'Automated Testing Framework for Microservices Architecture',     128),
(gen_random_uuid(), v_sid, 3, 'Dr. Hendra Kusuma',         'Edge Computing Optimization in IoT Networks',                    189);

-- ── Sheet 6m – Rekognisi DTPS ────────────────────────────────
INSERT INTO lkps_rekognisi_dtps (id, submission_id, no, nama_dosen, bidang_keahlian, rekognisi, bukti_pendukung, tingkat, tahun) VALUES
(gen_random_uuid(), v_sid, 1, 'Dr. Ahmad Budi Santoso',    'Kecerdasan Buatan',       'Best Paper Award IEEE ICACSIS 2023',  'https://drive.google.com/rekognisi1', 'Internasional', 2023),
(gen_random_uuid(), v_sid, 2, 'Dr. Siti Rahayu Wulandari', 'Rekayasa Perangkat Lunak','Pembicara Undangan ICCSA 2022',       'https://drive.google.com/rekognisi2', 'Internasional', 2022),
(gen_random_uuid(), v_sid, 3, 'Dr. Hendra Kusuma',         'Jaringan Komputer',       'Anggota IEEE Senior Member 2021',    'https://drive.google.com/rekognisi3', 'Internasional', 2021);

-- ── Sheet 6n – Penelitian Mahasiswa ──────────────────────────
INSERT INTO lkps_penelitian_mahasiswa (id, submission_id, jenis, no, nama_dosen, tema_penelitian, nama_mahasiswa, judul_kegiatan, tahun) VALUES
(gen_random_uuid(), v_sid, 'penelitian', 1, 'Dr. Ahmad Budi Santoso',    'Kecerdasan Buatan',        'Bima Prasetyo',    'Deteksi Deepfake Berbasis Vision Transformer', 2023),
(gen_random_uuid(), v_sid, 'penelitian', 2, 'Dr. Hendra Kusuma',         'Komputasi Awan',           'Citra Dewi',       'Optimasi Penjadwalan Task di Kubernetes',       2023),
(gen_random_uuid(), v_sid, 'pkm',        1, 'Dr. Siti Rahayu Wulandari', 'Rekayasa Perangkat Lunak', 'Deni Firmansyah',  'Platform Digital UMKM Berbasis AI',             2022),
(gen_random_uuid(), v_sid, 'pkm',        2, 'Dr. Muhammad Rizky Pratama','Keamanan Siber',           'Eka Putra',        'Sistem Deteksi Penipuan Online Real-time',       2023);

-- ── Sheet 6o – Prasarana ─────────────────────────────────────
INSERT INTO lkps_prasarana (id, submission_id, no, nama_prasarana, jumlah_prasarana, nama_sarana, jumlah_standar_minimal, jumlah_dimiliki, kepemilikan, kondisi, logbook) VALUES
(gen_random_uuid(), v_sid, 1, 'Ruang Kuliah',          10, 'Meja dan Kursi',         40,   50, 'Milik Sendiri', 'Baik', 'Ada'),
(gen_random_uuid(), v_sid, 2, 'Laboratorium Komputer',  5, 'Komputer',               30,   35, 'Milik Sendiri', 'Baik', 'Ada'),
(gen_random_uuid(), v_sid, 3, 'Ruang Seminar',          3, 'Proyektor dan Layar',     1,    2, 'Milik Sendiri', 'Baik', 'Ada'),
(gen_random_uuid(), v_sid, 4, 'Perpustakaan',           1, 'Koleksi Buku Digital', 1000, 5000, 'Milik Sendiri', 'Baik', 'Ada'),
(gen_random_uuid(), v_sid, 5, 'Ruang Penelitian Dosen', 8, 'Workstation Penelitian',  2,    3, 'Milik Sendiri', 'Baik', 'Ada');

-- ── Sheet 6p – K3L Dokumen ───────────────────────────────────
INSERT INTO lkps_k3l_dokumen (id, submission_id, no, jenis_dokumen, jumlah, riwayat_pengesahan) VALUES
(gen_random_uuid(), v_sid, 1, 'Kebijakan K3L',                  1, 'Disahkan Rektor 2022'),
(gen_random_uuid(), v_sid, 2, 'Prosedur Keselamatan Lab',        5, 'Revisi terakhir Jan 2023'),
(gen_random_uuid(), v_sid, 3, 'Laporan Audit K3L Tahunan',       3, 'Audit terakhir Desember 2023');

-- ── Sheet 6q – K3L Fasilitas ─────────────────────────────────
INSERT INTO lkps_k3l_fasilitas (id, submission_id, no, nama_sarana, fungsi, jumlah_unit, kondisi) VALUES
(gen_random_uuid(), v_sid, 1, 'APAR (Alat Pemadam Api Ringan)', 'Pemadam kebakaran darurat', 20, 'Baik'),
(gen_random_uuid(), v_sid, 2, 'P3K Kit',                        'Pertolongan pertama kecelakaan', 15, 'Baik'),
(gen_random_uuid(), v_sid, 3, 'CCTV',                           'Keamanan dan pengawasan gedung', 50, 'Baik'),
(gen_random_uuid(), v_sid, 4, 'Jalur Evakuasi',                 'Panduan evakuasi darurat',       10, 'Baik');

-- ── Sheet 7a – SPMI Dokumen ──────────────────────────────────
-- jenis_dokumen must match exactly to mapper keys
INSERT INTO lkps_spmi_dokumen (id, submission_id, no, jenis_dokumen, no_dokumen, tanggal_dokumen) VALUES
(gen_random_uuid(), v_sid, 1, 'Kebijakan SPMI',                                                                                                          'KEP-ITB-001/2022', '2022-01-15'),
(gen_random_uuid(), v_sid, 2, 'Pedoman penerapan siklus PPEPP standar pendidikan tinggi dalam SPMI',                                                     'PED-SPMI-002/2022','2022-02-01'),
(gen_random_uuid(), v_sid, 3, 'Standar dan/atau kriteria, norma, acuan mutu penyelenggaraan pendidikan dan pengelolaan perguruan tinggi',                 'STD-MUTU-003/2022','2022-03-01'),
(gen_random_uuid(), v_sid, 4, 'Tata cara pendokumentasian implementasi SPMI',                                                                            'DOK-SPMI-004/2022','2022-04-01');

-- ── Sheet 7b – SPMI Pelaksanaan ──────────────────────────────
-- jenis_pelaksanaan must match exactly: Penetapan, Pelaksanaan, Evaluasi, Pengendalian, Peningkatan
INSERT INTO lkps_spmi_pelaksanaan (id, submission_id, no, jenis_pelaksanaan, link_dokumen, link_laporan_audit, link_laporan_rtm, link_dokumen_peningkatan) VALUES
(gen_random_uuid(), v_sid, 1, 'Penetapan',    'https://drive.google.com/spmi/penetapan',    'https://drive.google.com/audit/penetapan',    'https://drive.google.com/rtm/penetapan',    'https://drive.google.com/peningkatan/penetapan'),
(gen_random_uuid(), v_sid, 2, 'Pelaksanaan',  'https://drive.google.com/spmi/pelaksanaan',  'https://drive.google.com/audit/pelaksanaan',  'https://drive.google.com/rtm/pelaksanaan',  'https://drive.google.com/peningkatan/pelaksanaan'),
(gen_random_uuid(), v_sid, 3, 'Evaluasi',     'https://drive.google.com/spmi/evaluasi',     'https://drive.google.com/audit/evaluasi',     'https://drive.google.com/rtm/evaluasi',     'https://drive.google.com/peningkatan/evaluasi'),
(gen_random_uuid(), v_sid, 4, 'Pengendalian', 'https://drive.google.com/spmi/pengendalian', 'https://drive.google.com/audit/pengendalian', 'https://drive.google.com/rtm/pengendalian', 'https://drive.google.com/peningkatan/pengendalian'),
(gen_random_uuid(), v_sid, 5, 'Peningkatan',  'https://drive.google.com/spmi/peningkatan',  'https://drive.google.com/audit/peningkatan',  'https://drive.google.com/rtm/peningkatan',  'https://drive.google.com/peningkatan/peningkatan');

RAISE NOTICE 'LKPS seed complete for submission %', v_sid;

END $$;
