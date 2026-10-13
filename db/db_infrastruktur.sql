-- ============================================================
-- Basis Data Infrastruktur (db_infrastruktur)
-- Contoh Data
-- 
-- Domain: jalan, jembatan, perumahan, pengairan, transportasi
-- Pembuat: Bryan
-- Tanggal: 2026-10-08
-- ============================================================

-- Buat basis data
CREATE DATABASE IF NOT EXISTS `db_infrastruktur`
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE `db_infrastruktur`;

-- ============================================================
-- Tabel: tb_jalan (Jalan)
-- ============================================================

CREATE TABLE IF NOT EXISTS `tb_jalan` (
    `id_jalan` MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `nama_jalan` VARCHAR(80) NOT NULL,
    `lokasi` VARCHAR(80) NOT NULL,
    `tipe_jalan` ENUM('nasional','provinsi','kabupaten','desa') NOT NULL,
    `panjang_km` DECIMAL(6,2) NOT NULL,
    `lebar_m` DECIMAL(4,2) NOT NULL,
    `jenis_permukaan` ENUM('aspal','beton','tanah','kerikil') NOT NULL,
    `kondisi` ENUM('baik','sedang','rusak ringan','rusak berat') NOT NULL,
    `tahun_pembangunan` YEAR NOT NULL,
    `tahun_pemeliharaan_terakhir` YEAR NULL,
    `nama_proyek` VARCHAR(120) NULL,
    `kontraktor_pelaksana` VARCHAR(80) NULL,
    `anggaran_rupiah` BIGINT UNSIGNED NULL,
    `status_proyek` ENUM('operasional','dalam perbaikan','perencanaan') NOT NULL DEFAULT 'operasional',
    `dibuat_pada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `diperbarui_pada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX `idx_jalan_status_kondisi` (`status_proyek`, `kondisi`, `tahun_pembangunan`),
    INDEX `idx_jalan_tahun_tipe` (`tahun_pembangunan`, `tipe_jalan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================================
-- Tabel: tb_jembatan (Jembatan)
-- ============================================================

CREATE TABLE IF NOT EXISTS `tb_jembatan` (
    `id_jembatan` MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `nama_jembatan` VARCHAR(80) NOT NULL,
    `lokasi` VARCHAR(80) NOT NULL,
    `panjang_m` DECIMAL(6,2) NOT NULL,
    `lebar_m` DECIMAL(4,2) NOT NULL,
    `tipe_jembatan` ENUM('beton','baja','gantung','bailey','kayu') NOT NULL,
    `kapasitas_beban_ton` TINYINT UNSIGNED NOT NULL,
    `kondisi` ENUM('baik','sedang','rusak ringan','rusak berat') NOT NULL,
    `tahun_pembangunan` YEAR NOT NULL,
    `tahun_pemeliharaan_terakhir` YEAR NULL,
    `nama_proyek` VARCHAR(120) NULL,
    `kontraktor_pelaksana` VARCHAR(80) NULL,
    `anggaran_rupiah` BIGINT UNSIGNED NULL,
    `status_proyek` ENUM('operasional','dalam perbaikan','perencanaan') NOT NULL DEFAULT 'operasional',
    `dibuat_pada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `diperbarui_pada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX `idx_jembatan_status_kondisi` (`status_proyek`, `kondisi`, `tahun_pembangunan`),
    INDEX `idx_jembatan_tahun_tipe` (`tahun_pembangunan`, `tipe_jembatan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================================
-- Tabel: tb_perumahan (Perumahan)
-- ============================================================

CREATE TABLE IF NOT EXISTS `tb_perumahan` (
    `id_perumahan` MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `nama_proyek` VARCHAR(120) NOT NULL,
    `lokasi` VARCHAR(80) NOT NULL,
    `jenis_program` ENUM('rumah rakyat','subsidi','relokasi bencana','kampung layak','rusunawa') NOT NULL,
    `jumlah_unit` SMALLINT UNSIGNED NOT NULL,
    `luas_area_m2` DECIMAL(8,2) NULL,
    `status_kepemilikan` ENUM('hak milik','sewa','hibah') NOT NULL,
    `tahun_pembangunan` YEAR NOT NULL,
    `tahun_selesai` YEAR NULL,
    `persentase_penyelesaian` TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `pengelola` VARCHAR(80) NULL,
    `anggaran_rupiah` BIGINT UNSIGNED NOT NULL,
    `jumlah_penghuni` MEDIUMINT UNSIGNED NULL,
    `kondisi_bangunan` ENUM('baik','sedang','rusak') NOT NULL,
    `status_proyek` ENUM('perencanaan','konstruksi','selesai','ditangguhkan') NOT NULL,
    `dibuat_pada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `diperbarui_pada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX `idx_perumahan_status` (`status_proyek`, `persentase_penyelesaian`),
    INDEX `idx_perumahan_tahun_program` (`tahun_pembangunan`, `jenis_program`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================================
-- Tabel: tb_pengairan (Pengairan)
-- ============================================================

CREATE TABLE IF NOT EXISTS `tb_pengairan` (
    `id_pengairan` MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `nama_aset` VARCHAR(80) NOT NULL,
    `jenis_aset` ENUM('bendungan','saluran primer','saluran sekunder','embung','sumur bor') NOT NULL,
    `lokasi` VARCHAR(80) NOT NULL,
    `luas_layanan_ha` DECIMAL(8,2) NULL,
    `panjang_saluran_km` DECIMAL(6,2) NULL,
    `kapasitas_debit_m3` DECIMAL(8,2) NULL,
    `kondisi` ENUM('baik','sedang','rusak ringan','rusak berat') NOT NULL,
    `tahun_pembangunan` YEAR NOT NULL,
    `tahun_pemeliharaan_terakhir` YEAR NULL,
    `nama_proyek` VARCHAR(120) NULL,
    `kontraktor_pelaksana` VARCHAR(80) NULL,
    `anggaran_rupiah` BIGINT UNSIGNED NULL,
    `status_operasional` ENUM('beroperasi','tidak beroperasi','dalam perbaikan') NOT NULL,
    `dibuat_pada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `diperbarui_pada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX `idx_pengairan_status` (`status_operasional`, `kondisi`),
    INDEX `idx_pengairan_tahun_jenis` (`tahun_pembangunan`, `jenis_aset`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================================
-- Tabel: tb_transportasi (Transportasi Umum)
-- ============================================================

CREATE TABLE IF NOT EXISTS `tb_transportasi` (
    `id_transportasi` MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `nama_aset` VARCHAR(80) NOT NULL,
    `jenis_aset` ENUM('terminal bus','pelabuhan','bandara','halte','pool','dermaga') NOT NULL,
    `lokasi` VARCHAR(80) NOT NULL,
    `kapasitas_penumpang` MEDIUMINT UNSIGNED NULL,
    `luas_area_m2` DECIMAL(8,2) NULL,
    `fasilitas` VARCHAR(120) NULL,
    `kondisi` ENUM('baik','sedang','rusak') NOT NULL,
    `tahun_pembangunan` YEAR NOT NULL,
    `tahun_renovasi_terakhir` YEAR NULL,
    `pengelola` VARCHAR(80) NULL,
    `anggaran_pembangunan_rupiah` BIGINT UNSIGNED NULL,
    `status_operasional` ENUM('beroperasi','tutup sementara','dalam renovasi') NOT NULL,
    `dibuat_pada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `diperbarui_pada` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX `idx_transportasi_status` (`status_operasional`, `kondisi`),
    INDEX `idx_transportasi_tahun_jenis` (`tahun_pembangunan`, `jenis_aset`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================================
-- Contoh Data: tb_jalan (50 rekaman - Jalan di seluruh Aceh)
-- ============================================================

INSERT INTO `tb_jalan` (`nama_jalan`, `lokasi`, `tipe_jalan`, `panjang_km`, `lebar_m`, `jenis_permukaan`, `kondisi`, `tahun_pembangunan`, `tahun_pemeliharaan_terakhir`, `nama_proyek`, `kontraktor_pelaksana`, `anggaran_rupiah`, `status_proyek`) VALUES
-- Jalan nasional
('Jalan Lintas Banda Aceh - Medan', 'Banda Aceh, Kuta Alam', 'nasional', 45.50, 12.00, 'aspal', 'baik', 2018, 2024, 'Rehabilitasi Jalan Lintas Sumatera 2018', 'PT Pembangunan Aceh Jaya', 85000000000, 'operasional'),
('Jalan Banda Aceh - Meulaboh', 'Aceh Besar, Indrapuri', 'nasional', 52.30, 11.50, 'aspal', 'baik', 2019, 2023, 'Peningkatan Jalan Lintas Barat 2019', 'PT Infrastruktur Nusantara', 95000000000, 'operasional'),
('Jalan Lhokseumawe - Bireuen', 'Lhokseumawe, Banda Sakti', 'nasional', 38.75, 12.00, 'aspal', 'sedang', 2017, 2022, 'Pemeliharaan Jalan Pantai Utara 2017', 'PT Konstruksi Mandiri', 68000000000, 'operasional'),
('Jalan Takengon - Bener Meriah', 'Aceh Tengah, Takengon', 'nasional', 42.00, 10.50, 'aspal', 'rusak ringan', 2015, 2020, 'Pembangunan Jalan Trans Gayo 2015', 'CV Gayo Konstruksi', 72000000000, 'dalam perbaikan'),
('Jalan Sigli - Banda Aceh', 'Pidie, Sigli', 'nasional', 48.20, 11.00, 'aspal', 'baik', 2020, 2025, 'Rehabilitasi Jalan Pantai Timur 2020', 'PT Aceh Infrastructure', 88000000000, 'operasional'),

-- Jalan provinsi  
('Jalan Provinsi Bireuen - Takengon', 'Bireuen, Peusangan', 'provinsi', 65.40, 9.00, 'aspal', 'sedang', 2016, 2023, 'Pembangunan Jalan Pegunungan 2016', 'PT Karya Pembangunan', 58000000000, 'operasional'),
('Jalan Provinsi Calang - Meulaboh', 'Aceh Jaya, Calang', 'provinsi', 55.80, 8.50, 'aspal', 'rusak ringan', 2014, 2021, 'Rehabilitasi Jalan Pesisir Barat 2014', 'CV Pantai Barat', 45000000000, 'dalam perbaikan'),
('Jalan Provinsi Langsa - Aceh Timur', 'Langsa, Langsa Kota', 'provinsi', 35.20, 9.00, 'aspal', 'baik', 2021, 2025, 'Peningkatan Jalan Kota Langsa 2021', 'PT Timur Konstruksi', 48000000000, 'operasional'),
('Jalan Provinsi Sabang - Balohan', 'Sabang, Sukakarya', 'provinsi', 18.50, 8.00, 'aspal', 'baik', 2019, 2024, 'Pembangunan Jalan Wisata Sabang 2019', 'PT Sabang Mandiri', 32000000000, 'operasional'),
('Jalan Provinsi Blangkejeren - Kutacane', 'Gayo Lues, Blangkejeren', 'provinsi', 72.30, 7.50, 'aspal', 'rusak ringan', 2013, 2019, 'Pembangunan Jalan Gayo Lues 2013', 'CV Lues Sejahtera', 52000000000, 'dalam perbaikan'),
('Jalan Provinsi Simeulue - Sinabang', 'Simeulue, Simeulue Timur', 'provinsi', 28.40, 8.00, 'aspal', 'sedang', 2018, 2023, 'Rehabilitasi Jalan Pulau Simeulue 2018', 'PT Simeulue Jaya', 38000000000, 'operasional'),
('Jalan Provinsi Aceh Barat Daya - Blangpidie', 'Aceh Barat Daya, Blangpidie', 'provinsi', 42.60, 8.50, 'aspal', 'baik', 2020, 2025, 'Peningkatan Jalan Kabupaten 2020', 'PT Barat Daya Konstruksi', 46000000000, 'operasional'),
('Jalan Provinsi Singkil - Subulussalam', 'Aceh Singkil, Singkil', 'provinsi', 38.90, 9.00, 'aspal', 'sedang', 2017, 2022, 'Pembangunan Jalan Perbatasan 2017', 'CV Singkil Mandiri', 42000000000, 'operasional'),
('Jalan Provinsi Aceh Utara - Lhoksukon', 'Aceh Utara, Lhoksukon', 'provinsi', 32.70, 9.50, 'aspal', 'baik', 2021, 2026, 'Rehabilitasi Jalan Utara 2021', 'PT Utara Sejahtera', 44000000000, 'operasional'),
('Jalan Provinsi Nagan Raya - Kuala', 'Nagan Raya, Kuala', 'provinsi', 46.20, 8.00, 'aspal', 'rusak ringan', 2015, 2020, 'Pembangunan Jalan Kabupaten Nagan Raya 2015', 'CV Nagan Konstruksi', 39000000000, 'dalam perbaikan'),

-- Jalan kabupaten
('Jalan Kabupaten Banda Aceh - Lambaro', 'Banda Aceh, Meuraxa', 'kabupaten', 12.50, 7.00, 'aspal', 'baik', 2022, 2025, 'Peningkatan Jalan Perkotaan 2022', 'PT Kota Serambi', 18000000000, 'operasional'),
('Jalan Kabupaten Bireuen - Juli', 'Bireuen, Juli', 'kabupaten', 24.80, 7.00, 'aspal', 'sedang', 2019, 2024, 'Rehabilitasi Jalan Kecamatan 2019', 'CV Bireuen Jaya', 22000000000, 'operasional'),
('Jalan Kabupaten Pidie - Titue', 'Pidie, Mutiara', 'kabupaten', 18.30, 6.50, 'aspal', 'rusak ringan', 2016, 2021, 'Pembangunan Jalan Pedesaan 2016', 'CV Pidie Konstruksi', 15000000000, 'dalam perbaikan'),
('Jalan Kabupaten Aceh Besar - Lhoknga', 'Aceh Besar, Lhoknga', 'kabupaten', 22.40, 7.50, 'aspal', 'baik', 2020, 2025, 'Rehabilitasi Jalan Wisata Pantai 2020', 'PT Aceh Besar Mandiri', 28000000000, 'operasional'),
('Jalan Kabupaten Aceh Timur - Idi', 'Aceh Timur, Idi Rayeuk', 'kabupaten', 15.60, 7.00, 'aspal', 'baik', 2021, 2026, 'Peningkatan Jalan Idi 2021', 'PT Timur Jaya', 19000000000, 'operasional'),
('Jalan Kabupaten Aceh Tengah - Silih Nara', 'Aceh Tengah, Silih Nara', 'kabupaten', 20.90, 6.50, 'beton', 'baik', 2022, NULL, 'Pembangunan Jalan Beton Gayo 2022', 'CV Gayo Beton', 25000000000, 'operasional'),
('Jalan Kabupaten Aceh Selatan - Tapaktuan', 'Aceh Selatan, Tapaktuan', 'kabupaten', 16.70, 7.00, 'aspal', 'sedang', 2018, 2023, 'Rehabilitasi Jalan Kota Tapaktuan 2018', 'PT Selatan Konstruksi', 17000000000, 'operasional'),
('Jalan Kabupaten Aceh Barat - Meulaboh Kota', 'Aceh Barat, Meulaboh', 'kabupaten', 14.20, 7.50, 'aspal', 'baik', 2020, 2024, 'Peningkatan Jalan Perkotaan Meulaboh 2020', 'PT Barat Sejahtera', 20000000000, 'operasional'),
('Jalan Kabupaten Pidie Jaya - Meureudu', 'Pidie Jaya, Meureudu', 'kabupaten', 19.50, 6.50, 'aspal', 'rusak ringan', 2017, 2022, 'Pembangunan Jalan Pidie Jaya 2017', 'CV Pidie Jaya Mandiri', 16000000000, 'dalam perbaikan'),
('Jalan Kabupaten Aceh Jaya - Lamno', 'Aceh Jaya, Jaya', 'kabupaten', 21.80, 7.00, 'aspal', 'sedang', 2019, 2024, 'Rehabilitasi Jalan Pesisir 2019', 'PT Jaya Konstruksi', 21000000000, 'operasional'),
('Jalan Kabupaten Bener Meriah - Simpang Tiga', 'Bener Meriah, Simpang Tiga Redelong', 'kabupaten', 17.40, 6.50, 'aspal', 'baik', 2021, 2025, 'Peningkatan Jalan Bener Meriah 2021', 'CV Bener Sejahtera', 18000000000, 'operasional'),
('Jalan Kabupaten Gayo Lues - Blangjerango', 'Gayo Lues, Blangjerango', 'kabupaten', 26.30, 6.00, 'aspal', 'rusak berat', 2012, 2018, 'Pembangunan Jalan Pegunungan Lues 2012', 'CV Lues Karya', 14000000000, 'dalam perbaikan'),
('Jalan Kabupaten Aceh Tenggara - Kutacane Kota', 'Aceh Tenggara, Babussalam', 'kabupaten', 13.90, 7.00, 'aspal', 'baik', 2022, NULL, 'Peningkatan Jalan Kota Kutacane 2022', 'PT Tenggara Mandiri', 16000000000, 'operasional'),
('Jalan Kabupaten Simeulue - Labuhan Bajau', 'Simeulue, Simeulue Barat', 'kabupaten', 22.50, 6.50, 'aspal', 'sedang', 2018, 2023, 'Rehabilitasi Jalan Simeulue Barat 2018', 'CV Simeulue Konstruksi', 19000000000, 'operasional'),
('Jalan Kabupaten Singkil - Gunung Meriah', 'Aceh Singkil, Gunung Meriah', 'kabupaten', 18.70, 6.50, 'aspal', 'rusak ringan', 2016, 2021, 'Pembangunan Jalan Singkil 2016', 'PT Singkil Jaya', 15000000000, 'dalam perbaikan'),

-- Jalan desa
('Jalan Desa Lamteuba - Lhoknga', 'Aceh Besar, Lhoknga', 'desa', 5.20, 4.00, 'aspal', 'baik', 2023, NULL, 'Program Jalan Desa 2023', 'CV Desa Mandiri', 3500000000, 'operasional'),
('Jalan Desa Lampuuk - Lhoknga', 'Aceh Besar, Lhoknga', 'desa', 4.80, 4.00, 'aspal', 'baik', 2022, 2025, 'Pembangunan Jalan Wisata Desa 2022', 'CV Lampuuk Jaya', 3200000000, 'operasional'),
('Jalan Desa Blang Bintang', 'Aceh Besar, Blang Bintang', 'desa', 6.50, 3.50, 'aspal', 'sedang', 2020, 2024, 'Jalan Desa Blang Bintang 2020', 'CV Blang Konstruksi', 2800000000, 'operasional'),
('Jalan Desa Peukan Bada', 'Aceh Besar, Peukan Bada', 'desa', 7.30, 4.00, 'aspal', 'baik', 2021, 2025, 'Program Infrastruktur Desa 2021', 'CV Peukan Mandiri', 3800000000, 'operasional'),
('Jalan Desa Lam Ara - Darussalam', 'Aceh Besar, Darussalam', 'desa', 4.20, 3.50, 'beton', 'baik', 2023, NULL, 'Betonisasi Jalan Desa 2023', 'CV Darussalam Jaya', 2500000000, 'operasional'),
('Jalan Desa Matang Glumpang Dua', 'Bireuen, Matang Glumpang Dua', 'desa', 5.80, 4.00, 'aspal', 'sedang', 2019, 2023, 'Pembangunan Jalan Desa Bireuen 2019', 'CV Matang Sejahtera', 2900000000, 'operasional'),
('Jalan Desa Cot Girek', 'Pidie, Mutiara', 'desa', 6.70, 3.50, 'aspal', 'rusak ringan', 2017, 2022, 'Jalan Desa Cot Girek 2017', 'CV Pidie Desa', 2400000000, 'dalam perbaikan'),
('Jalan Desa Meunasah Meucap', 'Aceh Utara, Lhoksukon', 'desa', 5.40, 4.00, 'aspal', 'baik', 2022, 2025, 'Program Jalan Desa Aceh Utara 2022', 'CV Utara Desa', 3100000000, 'operasional'),
('Jalan Desa Kuala Dua', 'Nagan Raya, Kuala', 'desa', 8.20, 4.00, 'tanah', 'rusak ringan', 2015, 2020, 'Pembangunan Jalan Desa Kuala 2015', 'CV Nagan Desa', 1800000000, 'dalam perbaikan'),
('Jalan Desa Alue Rambot', 'Aceh Timur, Idi Rayeuk', 'desa', 6.90, 3.50, 'aspal', 'sedang', 2020, 2024, 'Jalan Desa Idi 2020', 'CV Timur Desa', 2700000000, 'operasional'),
('Jalan Desa Kampung Jawa', 'Aceh Tengah, Takengon', 'desa', 4.60, 3.50, 'beton', 'baik', 2023, NULL, 'Betonisasi Jalan Kampung Jawa 2023', 'CV Gayo Desa', 2600000000, 'operasional'),
('Jalan Desa Gegarang', 'Aceh Tengah, Silih Nara', 'desa', 7.80, 4.00, 'aspal', 'sedang', 2019, 2023, 'Pembangunan Jalan Desa Gayo 2019', 'CV Silih Nara Mandiri', 3300000000, 'operasional'),
('Jalan Desa Blang Dalam', 'Aceh Selatan, Tapaktuan', 'desa', 5.30, 3.50, 'kerikil', 'rusak berat', 2014, 2019, 'Jalan Desa Blang Dalam 2014', 'CV Selatan Desa', 1500000000, 'perencanaan'),
('Jalan Desa Pante Ceureumen', 'Aceh Barat, Meulaboh', 'desa', 6.40, 4.00, 'aspal', 'baik', 2021, 2025, 'Program Jalan Desa Aceh Barat 2021', 'CV Barat Desa', 3000000000, 'operasional'),
('Jalan Desa Suaq Bakong', 'Aceh Selatan, Bakongan', 'desa', 7.50, 3.50, 'aspal', 'rusak ringan', 2018, 2022, 'Pembangunan Jalan Desa Bakongan 2018', 'CV Bakongan Jaya', 2200000000, 'dalam perbaikan'),
('Jalan Desa Kota Fajar', 'Aceh Selatan, Kota Fajar', 'desa', 5.90, 4.00, 'aspal', 'sedang', 2020, 2024, 'Jalan Desa Kota Fajar 2020', 'CV Fajar Mandiri', 2800000000, 'operasional'),
('Jalan Desa Kedai Baru', 'Aceh Jaya, Jaya', 'desa', 8.40, 3.50, 'tanah', 'rusak ringan', 2016, 2021, 'Pembangunan Jalan Desa Aceh Jaya 2016', 'CV Jaya Desa', 1900000000, 'perencanaan'),
('Jalan Desa Telaga Tujuh', 'Simeulue, Teluk Dalam', 'desa', 6.20, 3.50, 'aspal', 'sedang', 2019, 2023, 'Jalan Desa Simeulue 2019', 'CV Simeulue Desa', 2500000000, 'operasional'),
('Jalan Desa Kuta Padang', 'Bener Meriah, Bukit', 'desa', 7.10, 4.00, 'aspal', 'baik', 2022, 2025, 'Program Jalan Desa Bener Meriah 2022', 'CV Bener Desa', 3200000000, 'operasional'),
('Jalan Desa Rikit Gaib', 'Gayo Lues, Rikit Gaib', 'desa', 9.30, 3.50, 'kerikil', 'rusak berat', 2013, 2018, 'Pembangunan Jalan Desa Lues 2013', 'CV Rikit Konstruksi', 1600000000, 'perencanaan');

-- ============================================================
-- Contoh Data: tb_jembatan (15 rekaman - Jembatan strategis)
-- ============================================================

INSERT INTO `tb_jembatan` (`nama_jembatan`, `lokasi`, `panjang_m`, `lebar_m`, `tipe_jembatan`, `kapasitas_beban_ton`, `kondisi`, `tahun_pembangunan`, `tahun_pemeliharaan_terakhir`, `nama_proyek`, `kontraktor_pelaksana`, `anggaran_rupiah`, `status_proyek`) VALUES
('Jembatan Krueng Aceh', 'Banda Aceh, Kuta Alam', 185.50, 12.00, 'beton', 50, 'baik', 2019, 2024, 'Pembangunan Jembatan Krueng Aceh 2019', 'PT Jembatan Nusantara', 45000000000, 'operasional'),
('Jembatan Peusangan', 'Bireuen, Peusangan', 142.30, 10.00, 'beton', 40, 'baik', 2020, 2025, 'Rehabilitasi Jembatan Peusangan 2020', 'PT Aceh Bridge Construction', 38000000000, 'operasional'),
('Jembatan Krueng Teunom', 'Aceh Jaya, Teunom', 98.70, 9.00, 'baja', 35, 'sedang', 2016, 2022, 'Pembangunan Jembatan Teunom 2016', 'PT Infrastruktur Aceh Jaya', 28000000000, 'operasional'),
('Jembatan Krueng Meureudu', 'Pidie Jaya, Meureudu', 76.40, 8.50, 'beton', 30, 'baik', 2021, NULL, 'Pembangunan Jembatan Meureudu 2021', 'CV Pidie Jaya Konstruksi', 22000000000, 'operasional'),
('Jembatan Alue Ie Mirah', 'Aceh Besar, Indrapuri', 125.80, 11.00, 'beton', 45, 'baik', 2018, 2023, 'Rehabilitasi Jembatan Indrapuri 2018', 'PT Pembangunan Aceh Besar', 35000000000, 'operasional'),
('Jembatan Woyla', 'Aceh Barat, Woyla', 156.20, 10.50, 'beton', 50, 'sedang', 2015, 2021, 'Pembangunan Jembatan Woyla 2015', 'PT Barat Infrastructure', 42000000000, 'operasional'),
('Jembatan Krueng Raya', 'Nagan Raya, Kuala', 108.50, 9.50, 'baja', 40, 'rusak ringan', 2014, 2020, 'Pembangunan Jembatan Nagan Raya 2014', 'CV Nagan Bridge', 32000000000, 'dalam perbaikan'),
('Jembatan Jambo Aye', 'Aceh Utara, Lhoksukon', 92.30, 9.00, 'beton', 35, 'baik', 2022, NULL, 'Pembangunan Jembatan Aceh Utara 2022', 'PT Utara Konstruksi', 26000000000, 'operasional'),
('Jembatan Krueng Baro', 'Pidie, Sigli', 134.60, 10.00, 'beton', 45, 'baik', 2019, 2024, 'Rehabilitasi Jembatan Pidie 2019', 'PT Pidie Bridge Construction', 38000000000, 'operasional'),
('Jembatan Peureulak', 'Aceh Timur, Peureulak', 88.40, 8.50, 'baja', 30, 'sedang', 2017, 2023, 'Pembangunan Jembatan Peureulak 2017', 'CV Timur Jembatan', 24000000000, 'operasional'),
('Jembatan Krueng Simpang Kiri', 'Aceh Singkil, Singkil', 165.70, 11.00, 'beton', 50, 'baik', 2020, 2025, 'Pembangunan Jembatan Simpang Kiri 2020', 'PT Singkil Infrastructure', 48000000000, 'operasional'),
('Jembatan Gantung Blangkejeren', 'Gayo Lues, Blangkejeren', 215.30, 4.50, 'gantung', 15, 'sedang', 2013, 2019, 'Pembangunan Jembatan Gantung Lues 2013', 'CV Lues Bridge', 52000000000, 'operasional'),
('Jembatan Bailey Takengon', 'Aceh Tengah, Takengon', 45.60, 5.00, 'bailey', 20, 'rusak ringan', 2012, 2018, 'Instalasi Jembatan Bailey Gayo 2012', 'PT Gayo Engineering', 8500000000, 'dalam perbaikan'),
('Jembatan Kayu Kampung Laut', 'Aceh Selatan, Bakongan', 32.80, 3.50, 'kayu', 10, 'rusak berat', 2010, 2016, 'Pembangunan Jembatan Kayu Desa 2010', 'CV Selatan Kayu', 2500000000, 'perencanaan'),
('Jembatan Krueng Simeulue', 'Simeulue, Teluk Dalam', 78.90, 8.00, 'beton', 30, 'baik', 2021, 2025, 'Pembangunan Jembatan Simeulue 2021', 'PT Simeulue Construction', 24000000000, 'operasional');

-- ============================================================
-- Contoh Data: tb_perumahan (15 rekaman - Proyek perumahan)
-- ============================================================

INSERT INTO `tb_perumahan` (`nama_proyek`, `lokasi`, `jenis_program`, `jumlah_unit`, `luas_area_m2`, `status_kepemilikan`, `tahun_pembangunan`, `tahun_selesai`, `persentase_penyelesaian`, `pengelola`, `anggaran_rupiah`, `jumlah_penghuni`, `kondisi_bangunan`, `status_proyek`) VALUES
('Rusunawa Lambaro', 'Aceh Besar, Kuta Baro', 'rusunawa', 240, 15600.00, 'sewa', 2021, 2023, 100, 'Dinas Perumahan Aceh Besar', 72000000000, 960, 'baik', 'selesai'),
('Perumahan Subsidi Darussalam', 'Aceh Besar, Darussalam', 'subsidi', 180, 21600.00, 'hak milik', 2020, 2022, 100, 'PT Aceh Permai Property', 45000000000, 720, 'baik', 'selesai'),
('Kampung Nelayan Lampuuk', 'Aceh Besar, Lhoknga', 'kampung layak', 85, 10200.00, 'hak milik', 2019, 2021, 100, 'Dinas Kelautan dan Perikanan Aceh', 25500000000, 340, 'baik', 'selesai'),
('Relokasi Korban Bencana Meulaboh', 'Aceh Barat, Meulaboh', 'relokasi bencana', 320, 38400.00, 'hibah', 2018, 2020, 100, 'BPBD Aceh Barat', 96000000000, 1280, 'sedang', 'selesai'),
('Rusunawa Peusangan', 'Bireuen, Peusangan', 'rusunawa', 180, 12600.00, 'sewa', 2022, 2024, 100, 'Dinas Perumahan Bireuen', 58000000000, 720, 'baik', 'selesai'),
('Perumahan Rakyat Sigli', 'Pidie, Sigli', 'rumah rakyat', 150, 18000.00, 'hak milik', 2021, 2023, 100, 'PT Pidie Properti Mandiri', 38000000000, 600, 'baik', 'selesai'),
('Kampung Layak Huni Takengon', 'Aceh Tengah, Takengon', 'kampung layak', 120, 14400.00, 'hak milik', 2020, 2022, 100, 'Pemkab Aceh Tengah', 36000000000, 480, 'baik', 'selesai'),
('Perumahan Subsidi Lhokseumawe', 'Lhokseumawe, Banda Sakti', 'subsidi', 200, 24000.00, 'hak milik', 2019, 2021, 100, 'PT Lhokseumawe Property', 52000000000, 800, 'sedang', 'selesai'),
('Relokasi Bencana Calang', 'Aceh Jaya, Calang', 'relokasi bencana', 145, 17400.00, 'hibah', 2017, 2019, 100, 'BPBD Aceh Jaya', 43500000000, 580, 'sedang', 'selesai'),
('Rusunawa Kutacane', 'Aceh Tenggara, Babussalam', 'rusunawa', 160, 11200.00, 'sewa', 2023, 2025, 85, 'Dinas Perumahan Aceh Tenggara', 52000000000, 480, 'baik', 'konstruksi'),
('Kampung Nelayan Kuala Langsa', 'Langsa, Langsa Barat', 'kampung layak', 95, 11400.00, 'hak milik', 2022, 2024, 100, 'Pemkot Langsa', 28500000000, 380, 'baik', 'selesai'),
('Perumahan Rakyat Tapaktuan', 'Aceh Selatan, Tapaktuan', 'rumah rakyat', 110, 13200.00, 'hak milik', 2020, 2022, 100, 'PT Selatan Property', 33000000000, 440, 'baik', 'selesai'),
('Perumahan Subsidi Blangpidie', 'Aceh Barat Daya, Blangpidie', 'subsidi', 125, 15000.00, 'hak milik', 2021, 2023, 100, 'PT Barat Daya Properti', 32000000000, 500, 'baik', 'selesai'),
('Relokasi Bencana Sinabang', 'Simeulue, Simeulue Timur', 'relokasi bencana', 180, 21600.00, 'hibah', 2019, 2021, 100, 'BPBD Simeulue', 54000000000, 720, 'sedang', 'selesai'),
('Rusunawa Subulussalam', 'Subulussalam, Simpang Kiri', 'rusunawa', 200, 14000.00, 'sewa', 2024, NULL, 45, 'Dinas Perumahan Subulussalam', 68000000000, NULL, 'baik', 'konstruksi');

-- ============================================================
-- Contoh Data: tb_pengairan (12 rekaman - Sistem pengairan)
-- ============================================================

INSERT INTO `tb_pengairan` (`nama_aset`, `jenis_aset`, `lokasi`, `luas_layanan_ha`, `panjang_saluran_km`, `kapasitas_debit_m3`, `kondisi`, `tahun_pembangunan`, `tahun_pemeliharaan_terakhir`, `nama_proyek`, `kontraktor_pelaksana`, `anggaran_rupiah`, `status_operasional`) VALUES
('Bendungan Krueng Aceh', 'bendungan', 'Aceh Besar, Indrapuri', 8500.00, NULL, 125000.00, 'baik', 2015, 2023, 'Pembangunan Bendungan Krueng Aceh 2015', 'PT Waskita Karya', 850000000000, 'beroperasi'),
('Saluran Irigasi Primer Peusangan', 'saluran primer', 'Bireuen, Peusangan', 5200.00, 42.50, 85000.00, 'baik', 2018, 2024, 'Rehabilitasi Irigasi Peusangan 2018', 'PT Aceh Irigasi', 145000000000, 'beroperasi'),
('Saluran Irigasi Sekunder Pidie', 'saluran sekunder', 'Pidie, Mutiara', 2800.00, 28.30, 45000.00, 'sedang', 2016, 2022, 'Pembangunan Irigasi Pidie 2016', 'CV Pidie Irigasi', 68000000000, 'beroperasi'),
('Embung Blang Bintang', 'embung', 'Aceh Besar, Blang Bintang', 450.00, NULL, 12500.00, 'baik', 2020, 2025, 'Pembangunan Embung Pertanian 2020', 'PT Aceh Besar Mandiri', 32000000000, 'beroperasi'),
('Saluran Irigasi Primer Aceh Utara', 'saluran primer', 'Aceh Utara, Lhoksukon', 6300.00, 48.70, 95000.00, 'sedang', 2014, 2021, 'Rehabilitasi Irigasi Aceh Utara 2014', 'PT Utara Irigasi', 152000000000, 'beroperasi'),
('Bendungan Peusangan', 'bendungan', 'Bireuen, Peusangan Siblah Krueng', 4800.00, NULL, 78000.00, 'baik', 2019, 2024, 'Pembangunan Bendungan Peusangan 2019', 'PT Pembangunan Perumahan', 520000000000, 'beroperasi'),
('Saluran Irigasi Sekunder Takengon', 'saluran sekunder', 'Aceh Tengah, Takengon', 1850.00, 22.40, 28000.00, 'rusak ringan', 2013, 2019, 'Pembangunan Irigasi Gayo 2013', 'CV Gayo Irigasi', 48000000000, 'dalam perbaikan'),
('Embung Lhoknga', 'embung', 'Aceh Besar, Lhoknga', 320.00, NULL, 9500.00, 'baik', 2021, NULL, 'Pembangunan Embung Lhoknga 2021', 'PT Lhoknga Mandiri', 28000000000, 'beroperasi'),
('Saluran Irigasi Primer Aceh Barat', 'saluran primer', 'Aceh Barat, Meulaboh', 3900.00, 38.60, 62000.00, 'rusak ringan', 2012, 2020, 'Rehabilitasi Irigasi Aceh Barat 2012', 'PT Barat Irigasi', 125000000000, 'dalam perbaikan'),
('Sumur Bor Kampung Baro', 'sumur bor', 'Pidie, Mutiara Baro', 180.00, NULL, 2500.00, 'baik', 2022, 2025, 'Program Sumur Bor Pertanian 2022', 'CV Pidie Air', 8500000000, 'beroperasi'),
('Saluran Irigasi Sekunder Aceh Timur', 'saluran sekunder', 'Aceh Timur, Idi Rayeuk', 2200.00, 24.80, 38000.00, 'sedang', 2017, 2023, 'Pembangunan Irigasi Aceh Timur 2017', 'PT Timur Irigasi', 62000000000, 'beroperasi'),
('Embung Blangkejeren', 'embung', 'Gayo Lues, Blangkejeren', 280.00, NULL, 8200.00, 'sedang', 2019, 2024, 'Pembangunan Embung Gayo Lues 2019', 'CV Lues Pertanian', 24000000000, 'beroperasi');

-- ============================================================
-- Contoh Data: tb_transportasi (10 rekaman - Hub transportasi)
-- ============================================================

INSERT INTO `tb_transportasi` (`nama_aset`, `jenis_aset`, `lokasi`, `kapasitas_penumpang`, `luas_area_m2`, `fasilitas`, `kondisi`, `tahun_pembangunan`, `tahun_renovasi_terakhir`, `pengelola`, `anggaran_pembangunan_rupiah`, `status_operasional`) VALUES
('Bandara Internasional Sultan Iskandar Muda', 'bandara', 'Aceh Besar, Blang Bintang', 1500000, 125000.00, 'runway 3000m, terminal internasional, cargo, musholla, restoran, lounge, ATM, rental mobil', 'baik', 2015, 2023, 'PT Angkasa Pura II', 1250000000000, 'beroperasi'),
('Pelabuhan Malahayati', 'pelabuhan', 'Banda Aceh, Kuta Alam', 800000, 85000.00, 'dermaga internasional, terminal penumpang, gudang kargo, kantor bea cukai, musholla, kantin', 'baik', 2017, 2024, 'PT Pelindo I', 850000000000, 'beroperasi'),
('Terminal Tipe A Batoh', 'terminal bus', 'Banda Aceh, Lueng Bata', 5000, 28000.00, 'ruang tunggu AC, toilet, musholla, kantin, area parkir, loket tiket, ATM', 'baik', 2019, 2024, 'Dinas Perhubungan Aceh', 45000000000, 'beroperasi'),
('Pelabuhan Ulee Lheue', 'pelabuhan', 'Banda Aceh, Meuraxa', 250000, 42000.00, 'terminal ferry, dermaga penyeberangan, ruang tunggu, toilet, kantin, area parkir', 'sedang', 2013, 2021, 'PT ASDP Indonesia Ferry', 120000000000, 'beroperasi'),
('Terminal Tipe B Lhokseumawe', 'terminal bus', 'Lhokseumawe, Banda Sakti', 3500, 18500.00, 'ruang tunggu, toilet, musholla, kantin, loket tiket, area parkir', 'baik', 2020, 2025, 'Dinas Perhubungan Lhokseumawe', 32000000000, 'beroperasi'),
('Pelabuhan Sinabang', 'pelabuhan', 'Simeulue, Simeulue Timur', 180000, 32000.00, 'dermaga kapal, terminal penumpang, gudang, musholla, kantin', 'sedang', 2016, 2022, 'PT Pelindo I', 85000000000, 'beroperasi'),
('Terminal Tipe C Meulaboh', 'terminal bus', 'Aceh Barat, Meulaboh', 2000, 12000.00, 'ruang tunggu, toilet, musholla, loket tiket, area parkir', 'rusak', 2014, 2020, 'Dinas Perhubungan Aceh Barat', 18000000000, 'dalam renovasi'),
('Bandara Cut Nyak Dhien', 'bandara', 'Nagan Raya, Kuala', 120000, 15000.00, 'runway 1800m, terminal domestik, musholla, kantin', 'baik', 2021, NULL, 'PT Angkasa Pura II', 180000000000, 'beroperasi'),
('Dermaga Penyeberangan Calang', 'dermaga', 'Aceh Jaya, Calang', 50000, 8500.00, 'dermaga kapal kecil, ruang tunggu sederhana, toilet, kantin', 'sedang', 2018, 2023, 'Dinas Perhubungan Aceh Jaya', 12000000000, 'beroperasi'),
('Pool Bus Trans Koetaradja', 'pool', 'Banda Aceh, Baiturrahman', 1200, 9500.00, 'halte utama, tempat istirahat driver, bengkel, musholla, kantin, area parkir', 'baik', 2022, 2025, 'Dinas Perhubungan Banda Aceh', 28000000000, 'beroperasi');

-- ============================================================
-- Akhir Contoh Data
-- ============================================================
