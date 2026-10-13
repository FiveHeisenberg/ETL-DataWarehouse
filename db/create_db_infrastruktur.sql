-- ============================================================
-- Basis Data Infrastruktur (db_infrastruktur)
-- 
-- Domain: jalan, jembatan, perumahan, pengairan, transportasi
-- Pembuat: Bryan
-- Tanggal: 2026-10-08
-- ============================================================

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
