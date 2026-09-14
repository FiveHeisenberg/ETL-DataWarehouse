-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 09, 2026 at 10:07 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_pendidikan`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_pendidikan`
--

CREATE TABLE `tb_pendidikan` (
  `id_pendidikan` int(11) NOT NULL,
  `id_sekolah` char(8) NOT NULL,
  `id_waktu` int(11) NOT NULL,
  `jumlah_siswa` int(11) DEFAULT NULL,
  `jumlah_guru` int(11) DEFAULT NULL,
  `jumlah_rombel` int(11) DEFAULT NULL,
  `jumlah_mapel` int(11) DEFAULT NULL,
  `jumlah_jam_pembelajaran` int(11) DEFAULT NULL,
  `rata_rata_nilai` decimal(5,2) DEFAULT NULL,
  `persentase_kelulusan` decimal(5,2) DEFAULT NULL,
  `jumlah_lulus` int(11) DEFAULT NULL,
  `jumlah_mengulang` int(11) DEFAULT NULL,
  `jumlah_putus_sekolah` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_pendidikan`
--

INSERT INTO `tb_pendidikan` (`id_pendidikan`, `id_sekolah`, `id_waktu`, `jumlah_siswa`, `jumlah_guru`, `jumlah_rombel`, `jumlah_mapel`, `jumlah_jam_pembelajaran`, `rata_rata_nilai`, `persentase_kelulusan`, `jumlah_lulus`, `jumlah_mengulang`, `jumlah_putus_sekolah`) VALUES
(1, '10000001', 4, 30, 9, 2, 9, 30, 70.80, 96.67, 29, 1, 0),
(2, '10000002', 4, 35, 10, 2, 10, 32, 71.60, 94.29, 33, 2, 0),
(3, '10000003', 4, 40, 11, 2, 11, 34, 72.40, 92.50, 37, 3, 0),
(4, '10000004', 4, 45, 12, 3, 12, 36, 73.20, 100.00, 45, 0, 0),
(5, '10000005', 4, 50, 13, 3, 13, 38, 74.00, 98.00, 49, 1, 0),
(6, '10000006', 4, 55, 14, 3, 14, 40, 74.80, 96.36, 53, 2, 0),
(7, '10000007', 4, 60, 15, 4, 8, 42, 75.60, 95.00, 57, 3, 1),
(8, '10000008', 4, 65, 8, 4, 9, 44, 76.40, 100.00, 65, 0, 0),
(9, '10000009', 4, 70, 9, 4, 10, 28, 77.20, 98.57, 69, 1, 0),
(10, '10000010', 4, 25, 10, 2, 11, 30, 78.00, 92.00, 23, 2, 0),
(11, '10000011', 4, 30, 11, 2, 12, 32, 78.80, 90.00, 27, 3, 0),
(12, '10000012', 4, 35, 12, 2, 13, 34, 79.60, 100.00, 35, 0, 0),
(13, '10000013', 4, 40, 13, 2, 14, 36, 80.40, 97.50, 39, 1, 0),
(14, '10000014', 4, 45, 14, 3, 8, 38, 81.20, 95.56, 43, 2, 0),
(15, '10000015', 4, 50, 15, 3, 9, 40, 82.00, 94.00, 47, 3, 0),
(16, '10000016', 4, 55, 8, 3, 10, 42, 82.80, 100.00, 55, 0, 0),
(17, '10000017', 4, 60, 9, 4, 11, 44, 83.60, 98.33, 59, 1, 1),
(18, '10000018', 4, 65, 10, 4, 12, 28, 84.40, 96.92, 63, 2, 0),
(19, '10000019', 4, 70, 11, 4, 13, 30, 85.20, 95.71, 67, 3, 0),
(20, '10000020', 4, 25, 12, 2, 14, 32, 86.00, 100.00, 25, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `tb_ptk`
--

CREATE TABLE `tb_ptk` (
  `id_ptk` char(8) NOT NULL,
  `nik` char(16) NOT NULL,
  `nuptk` char(16) DEFAULT NULL,
  `nama_ptk` varchar(25) NOT NULL,
  `jenis_kelamin` enum('L','P') NOT NULL,
  `id_sekolah` char(8) NOT NULL,
  `jenis_ptk` enum('Guru','Kepala Sekolah','Tenaga Kependidikan') DEFAULT NULL,
  `status_kepegawaian` enum('PNS','PPPK','Honorer','GTY','GTT','Tenaga Kependidikan') DEFAULT NULL,
  `pendidikan_terakhir` varchar(30) DEFAULT NULL,
  `bidang_studi` varchar(30) DEFAULT NULL,
  `jabatan` varchar(25) DEFAULT NULL,
  `tahun_masuk` year(4) DEFAULT NULL,
  `status_ptk` enum('Aktif','Tidak Aktif') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_ptk`
--

INSERT INTO `tb_ptk` (`id_ptk`, `nik`, `nuptk`, `nama_ptk`, `jenis_kelamin`, `id_sekolah`, `jenis_ptk`, `status_kepegawaian`, `pendidikan_terakhir`, `bidang_studi`, `jabatan`, `tahun_masuk`, `status_ptk`) VALUES
('PTK00001', '1173010101010001', '1200000000000001', 'Ahmad Rizki Kurniawan', 'L', '10000001', 'Guru', 'PPPK', 'S1 Matematika', 'Bahasa Indonesia', 'Guru Mata Pelajaran', '2001', 'Aktif'),
('PTK00002', '1173010101010002', '1200000000000002', 'Siti Nur Azizah', 'P', '10000002', 'Guru', 'Honorer', 'S1 Bahasa Indonesia', 'Informatika', 'Guru Mata Pelajaran', '2002', 'Aktif'),
('PTK00003', '1173010101010003', '1200000000000003', 'Hendra Gunawan', 'L', '10000003', 'Kepala Sekolah', 'GTY', 'S1 Informatika', 'IPA', 'Kepala Sekolah', '2003', 'Aktif'),
('PTK00004', '1173010101010004', '1200000000000004', 'Nurul Habibah', 'P', '10000004', 'Tenaga Kependidikan', 'GTT', 'D3 Administrasi', 'IPS', 'Wali Kelas', '2004', 'Aktif'),
('PTK00005', '1173010102010005', '1200000000000005', 'Ridho Pratama', 'L', '10000005', 'Guru', 'PNS', 'S1 Pendidikan', 'Matematika', 'Guru Mata Pelajaran', '2005', 'Aktif'),
('PTK00006', '1173010102010006', '1200000000000006', 'Eka Putri Santoso', 'P', '10000006', 'Guru', 'PPPK', 'S1 Matematika', 'Bahasa Indonesia', 'Guru Mata Pelajaran', '2006', 'Aktif'),
('PTK00007', '1173010102010007', '1200000000000007', 'Muhammad Ilham', 'L', '10000007', 'Guru', 'Honorer', 'S1 Bahasa Indonesia', 'Informatika', 'Guru Mata Pelajaran', '2007', 'Aktif'),
('PTK00008', '1173010102010008', '1200000000000008', 'Dewi Lestari', 'P', '10000008', 'Kepala Sekolah', 'GTY', 'S1 Informatika', 'IPA', 'Kepala Sekolah', '2008', 'Aktif'),
('PTK00009', '1173010103010009', '1200000000000009', 'Budi Santoso', 'L', '10000009', 'Tenaga Kependidikan', 'GTT', 'D3 Administrasi', 'IPS', 'Guru Mata Pelajaran', '2009', 'Aktif'),
('PTK00010', '1173010103010010', '1200000000000010', 'Sinta Wijaya', 'P', '10000010', 'Guru', 'PNS', 'S1 Pendidikan', 'Matematika', 'Guru Mata Pelajaran', '2010', 'Aktif'),
('PTK00011', '1173010104010011', '1200000000000011', 'Rahman Hakim', 'L', '10000011', 'Guru', 'PPPK', 'S1 Matematika', 'Bahasa Indonesia', 'Guru Mata Pelajaran', '2011', 'Aktif'),
('PTK00012', '1173010104010012', '1200000000000012', 'Linda Kusuma', 'P', '10000012', 'Guru', 'Honorer', 'S1 Bahasa Indonesia', 'Informatika', 'Wali Kelas', '2012', 'Aktif'),
('PTK00013', '1173010105010013', '1200000000000013', 'Fajar Ramadhan', 'L', '10000013', 'Kepala Sekolah', 'GTY', 'S1 Informatika', 'IPA', 'Kepala Sekolah', '2013', 'Aktif'),
('PTK00014', '1173010105010014', '1200000000000014', 'Yuni Hartono', 'P', '10000014', 'Tenaga Kependidikan', 'GTT', 'D3 Administrasi', 'IPS', 'Guru Mata Pelajaran', '2014', 'Aktif'),
('PTK00015', '1173010106010015', '1200000000000015', 'Arif Wijaksana', 'L', '10000015', 'Guru', 'PNS', 'S1 Pendidikan', 'Matematika', 'Guru Mata Pelajaran', '2015', 'Aktif'),
('PTK00016', '1173010106010016', '1200000000000016', 'Mira Handoko', 'P', '10000016', 'Guru', 'PPPK', 'S1 Matematika', 'Bahasa Indonesia', 'Wali Kelas', '2016', 'Aktif'),
('PTK00017', '1173020101010017', '1200000000000017', 'Dimas Pratama', 'L', '10000017', 'Guru', 'Honorer', 'S1 Bahasa Indonesia', 'Informatika', 'Guru Mata Pelajaran', '2017', 'Aktif'),
('PTK00018', '1173020101010018', '1200000000000018', 'Rini Susanto', 'P', '10000018', 'Kepala Sekolah', 'GTY', 'S1 Informatika', 'IPA', 'Kepala Sekolah', '2018', 'Aktif'),
('PTK00019', '1173020102010019', '1200000000000019', 'Wahyu Prasetyo', 'L', '10000019', 'Tenaga Kependidikan', 'GTT', 'D3 Administrasi', 'IPS', 'Guru Mata Pelajaran', '2019', 'Aktif'),
('PTK00020', '1173020102010020', '1200000000000020', 'Siti Marjiah', 'P', '10000020', 'Guru', 'PNS', 'S1 Pendidikan', 'Matematika', 'Wali Kelas', '2000', 'Aktif'),
('PTK00021', '1173030101010021', '1200000000000021', 'Irfan Syaputra', 'L', '10000001', 'Guru', 'PPPK', 'S1 Matematika', 'Bahasa Indonesia', 'Guru Mata Pelajaran', '2001', 'Aktif'),
('PTK00022', '1173030101010022', '1200000000000022', 'Anita Maharani', 'P', '10000002', 'Guru', 'Honorer', 'S1 Bahasa Indonesia', 'Informatika', 'Guru Mata Pelajaran', '2002', 'Aktif'),
('PTK00023', '1173030102010023', '1200000000000023', 'Zainal Abidin', 'L', '10000003', 'Kepala Sekolah', 'GTY', 'S1 Informatika', 'IPA', 'Kepala Sekolah', '2003', 'Aktif'),
('PTK00024', '1173030102010024', '1200000000000024', 'Ratna Dewi', 'P', '10000004', 'Tenaga Kependidikan', 'GTT', 'D3 Administrasi', 'IPS', 'Wali Kelas', '2004', 'Aktif'),
('PTK00025', '1173040101010025', '1200000000000025', 'Hendri Wijaya', 'L', '10000005', 'Guru', 'PNS', 'S1 Pendidikan', 'Matematika', 'Guru Mata Pelajaran', '2005', 'Aktif'),
('PTK00026', '1173040102010026', '1200000000000026', 'Joni Tarpada', 'L', '10000006', 'Guru', 'PPPK', 'S1 Matematika', 'Bahasa Indonesia', 'Guru Mata Pelajaran', '2006', 'Aktif'),
('PTK00027', '1173040102010027', '1200000000000027', 'Karina Amelia', 'P', '10000007', 'Guru', 'Honorer', 'S1 Bahasa Indonesia', 'Informatika', 'Guru Mata Pelajaran', '2007', 'Aktif'),
('PTK00028', '1173040102010028', '1200000000000028', 'Bambang Sutrisno', 'L', '10000008', 'Kepala Sekolah', 'GTY', 'S1 Informatika', 'IPA', 'Kepala Sekolah', '2008', 'Aktif'),
('PTK00029', '1173040103010029', '1200000000000029', 'Susi Susanti', 'P', '10000009', 'Tenaga Kependidikan', 'GTT', 'D3 Administrasi', 'IPS', 'Guru Mata Pelajaran', '2009', 'Aktif'),
('PTK00030', '1173040103010030', '1200000000000030', 'Toto Suryanto', 'L', '10000010', 'Guru', 'PNS', 'S1 Pendidikan', 'Matematika', 'Guru Mata Pelajaran', '2010', 'Aktif'),
('PTK00031', '1173050101010031', '1200000000000031', 'Rahmat Fauzi', 'L', '10000011', 'Guru', 'PPPK', 'S1 Matematika', 'Bahasa Indonesia', 'Guru Mata Pelajaran', '2011', 'Aktif'),
('PTK00032', '1173050101010032', '1200000000000032', 'Lina Marlina', 'P', '10000012', 'Guru', 'Honorer', 'S1 Bahasa Indonesia', 'Informatika', 'Wali Kelas', '2012', 'Aktif'),
('PTK00033', '1173050102010033', '1200000000000033', 'Syaiful Rahman', 'L', '10000013', 'Kepala Sekolah', 'GTY', 'S1 Informatika', 'IPA', 'Kepala Sekolah', '2013', 'Aktif'),
('PTK00034', '1173050102010034', '1200000000000034', 'Rina Kartini', 'P', '10000014', 'Tenaga Kependidikan', 'GTT', 'D3 Administrasi', 'IPS', 'Guru Mata Pelajaran', '2014', 'Aktif'),
('PTK00035', '1173050201010035', '1200000000000035', 'Juanda Gunawan', 'L', '10000015', 'Guru', 'PNS', 'S1 Pendidikan', 'Matematika', 'Guru Mata Pelajaran', '2015', 'Aktif'),
('PTK00036', '1173050201010036', '1200000000000036', 'Ayu Permata', 'P', '10000016', 'Guru', 'PPPK', 'S1 Matematika', 'Bahasa Indonesia', 'Wali Kelas', '2016', 'Aktif'),
('PTK00037', '1173050202010037', '1200000000000037', 'Danang Permadi', 'L', '10000017', 'Guru', 'Honorer', 'S1 Bahasa Indonesia', 'Informatika', 'Guru Mata Pelajaran', '2017', 'Aktif'),
('PTK00038', '1173050202010038', '1200000000000038', 'Neneng Suryani', 'P', '10000018', 'Kepala Sekolah', 'GTY', 'S1 Informatika', 'IPA', 'Kepala Sekolah', '2018', 'Aktif'),
('PTK00039', '1173050301010039', '1200000000000039', 'Ahmad Zainudin', 'L', '10000019', 'Tenaga Kependidikan', 'GTT', 'D3 Administrasi', 'IPS', 'Guru Mata Pelajaran', '2019', 'Aktif'),
('PTK00040', '1173050301010040', '1200000000000040', 'Masniyah Said', 'P', '10000020', 'Guru', 'PNS', 'S1 Pendidikan', 'Matematika', 'Wali Kelas', '2000', 'Aktif'),
('PTK00041', '1173070101010041', '1200000000000041', 'Suryadi Gunawan', 'L', '10000001', 'Guru', 'PPPK', 'S1 Matematika', 'Bahasa Indonesia', 'Guru Mata Pelajaran', '2001', 'Aktif'),
('PTK00042', '1173070101010042', '1200000000000042', 'Fitri Wahyuni', 'P', '10000002', 'Guru', 'Honorer', 'S1 Bahasa Indonesia', 'Informatika', 'Guru Mata Pelajaran', '2002', 'Aktif'),
('PTK00043', '1173070102010043', '1200000000000043', 'Hari Prabowo', 'L', '10000003', 'Kepala Sekolah', 'GTY', 'S1 Informatika', 'IPA', 'Kepala Sekolah', '2003', 'Aktif'),
('PTK00044', '1173070102010044', '1200000000000044', 'Putri Maharini', 'P', '10000004', 'Tenaga Kependidikan', 'GTT', 'D3 Administrasi', 'IPS', 'Wali Kelas', '2004', 'Aktif'),
('PTK00045', '1173070103010045', '1200000000000045', 'Andi Wijaya', 'L', '10000005', 'Guru', 'PNS', 'S1 Pendidikan', 'Matematika', 'Guru Mata Pelajaran', '2005', 'Aktif'),
('PTK00046', '1173070103010046', '1200000000000046', 'Hilda Kusuma', 'P', '10000006', 'Guru', 'PPPK', 'S1 Matematika', 'Bahasa Indonesia', 'Guru Mata Pelajaran', '2006', 'Aktif'),
('PTK00047', '1173070104010047', '1200000000000047', 'Sumardi Santoso', 'L', '10000007', 'Guru', 'Honorer', 'S1 Bahasa Indonesia', 'Informatika', 'Guru Mata Pelajaran', '2007', 'Tidak Aktif'),
('PTK00048', '1173070104010048', '1200000000000048', 'Soraya Amelia', 'P', '10000008', 'Kepala Sekolah', 'GTY', 'S1 Informatika', 'IPA', 'Kepala Sekolah', '2008', 'Aktif'),
('PTK00049', '1173070201010049', '1200000000000049', 'Didik Rahmat', 'L', '10000009', 'Tenaga Kependidikan', 'GTT', 'D3 Administrasi', 'IPS', 'Guru Mata Pelajaran', '2009', 'Aktif'),
('PTK00050', '1173070201010050', '1200000000000050', 'Maya Kusuma', 'P', '10000010', 'Guru', 'PNS', 'S1 Pendidikan', 'Matematika', 'Guru Mata Pelajaran', '2010', 'Tidak Aktif');

-- --------------------------------------------------------

--
-- Table structure for table `tb_sarana`
--

CREATE TABLE `tb_sarana` (
  `id_sarana` int(11) NOT NULL,
  `id_sekolah` char(8) NOT NULL,
  `id_waktu` int(11) NOT NULL,
  `jumlah_ruang_kelas` int(11) DEFAULT NULL,
  `jumlah_laboratorium` int(11) DEFAULT NULL,
  `jumlah_perpustakaan` int(11) DEFAULT NULL,
  `jumlah_toilet` int(11) DEFAULT NULL,
  `jumlah_ruang_guru` int(11) DEFAULT NULL,
  `jumlah_ruang_kepala` int(11) DEFAULT NULL,
  `jumlah_ruang_rusak` int(11) DEFAULT NULL,
  `kondisi_sarana` enum('Baik','Rusak Ringan','Rusak Berat') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_sarana`
--

INSERT INTO `tb_sarana` (`id_sarana`, `id_sekolah`, `id_waktu`, `jumlah_ruang_kelas`, `jumlah_laboratorium`, `jumlah_perpustakaan`, `jumlah_toilet`, `jumlah_ruang_guru`, `jumlah_ruang_kepala`, `jumlah_ruang_rusak`, `kondisi_sarana`) VALUES
(1, '10000001', 4, 6, 1, 2, 4, 2, 1, 1, 'Baik'),
(2, '10000002', 4, 7, 2, 1, 5, 3, 1, 2, 'Rusak Ringan'),
(3, '10000003', 4, 8, 3, 2, 6, 1, 1, 3, 'Rusak Berat'),
(4, '10000004', 4, 9, 0, 1, 7, 2, 1, 0, 'Baik'),
(5, '10000005', 4, 10, 1, 2, 3, 3, 1, 1, 'Baik'),
(6, '10000006', 4, 11, 2, 1, 4, 1, 1, 2, 'Rusak Ringan'),
(7, '10000007', 4, 12, 3, 2, 5, 2, 1, 3, 'Rusak Berat'),
(8, '10000008', 4, 13, 0, 1, 6, 3, 1, 0, 'Baik'),
(9, '10000009', 4, 14, 1, 2, 7, 1, 1, 1, 'Baik'),
(10, '10000010', 4, 5, 2, 1, 3, 2, 1, 2, 'Rusak Ringan'),
(11, '10000011', 4, 6, 3, 2, 4, 3, 1, 3, 'Rusak Berat'),
(12, '10000012', 4, 7, 0, 1, 5, 1, 1, 0, 'Baik'),
(13, '10000013', 4, 8, 1, 2, 6, 2, 1, 1, 'Baik'),
(14, '10000014', 4, 9, 2, 1, 7, 3, 1, 2, 'Rusak Ringan'),
(15, '10000015', 4, 10, 3, 2, 3, 1, 1, 3, 'Rusak Berat'),
(16, '10000016', 4, 11, 0, 1, 4, 2, 1, 0, 'Baik'),
(17, '10000017', 4, 12, 1, 2, 5, 3, 1, 1, 'Baik'),
(18, '10000018', 4, 13, 2, 1, 6, 1, 1, 2, 'Rusak Ringan'),
(19, '10000019', 4, 14, 3, 2, 7, 2, 1, 3, 'Rusak Berat'),
(20, '10000020', 4, 5, 0, 1, 3, 3, 1, 0, 'Baik');

-- --------------------------------------------------------

--
-- Table structure for table `tb_sekolah`
--

CREATE TABLE `tb_sekolah` (
  `id_sekolah` char(8) NOT NULL,
  `npsn` char(8) NOT NULL,
  `nama_sekolah` varchar(80) NOT NULL,
  `jenjang` enum('PAUD','TK','SD','SMP','SMA','SMK','SLB') NOT NULL,
  `status_sekolah` enum('Negeri','Swasta') NOT NULL,
  `akreditasi` enum('A','B','C','Belum Terakreditasi') DEFAULT NULL,
  `id_desa` char(10) DEFAULT NULL,
  `alamat_sekolah` varchar(35) DEFAULT NULL,
  `status_operasional` enum('Aktif','Tidak Aktif') DEFAULT NULL,
  `tahun_berdiri` year(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_sekolah`
--

INSERT INTO `tb_sekolah` (`id_sekolah`, `npsn`, `nama_sekolah`, `jenjang`, `status_sekolah`, `akreditasi`, `id_desa`, `alamat_sekolah`, `status_operasional`, `tahun_berdiri`) VALUES
('10000001', '10000001', 'TK Peuniti Ceria', 'TK', 'Swasta', 'B', '01011', 'Jalan Peuniti', 'Aktif', '2001'),
('10000002', '10000002', 'SD Negeri Punge Blang Cut', 'SD', 'Negeri', 'A', '01012', 'Jalan Punge Blang Cut', 'Aktif', '1998'),
('10000003', '10000003', 'SD Negeri Lampriet', 'SD', 'Negeri', 'B', '01013', 'Jalan Lampriet', 'Aktif', '2000'),
('10000004', '10000004', 'SD Islam Larangan', 'SD', 'Swasta', 'A', '01014', 'Jalan Larangan', 'Aktif', '2005'),
('10000005', '10000005', 'SMP Negeri Lampoh Daya', 'SMP', 'Negeri', 'A', '01015', 'Jalan Lampoh Daya', 'Aktif', '1995'),
('10000006', '10000006', 'SMP Negeri Lamgugob', 'SMP', 'Negeri', 'B', '01016', 'Jalan Lamgugob', 'Aktif', '2003'),
('10000007', '10000007', 'SMP Al-Hikmah Lamteumen', 'SMP', 'Swasta', 'B', '01017', 'Jalan Lamteumen', 'Aktif', '2008'),
('10000008', '10000008', 'SMA Negeri Lueng Bata', 'SMA', 'Negeri', 'A', '01018', 'Jalan Lueng Bata', 'Aktif', '1990'),
('10000009', '10000009', 'SMA Negeri Lamdom', 'SMA', 'Negeri', 'A', '01019', 'Jalan Lamdom', 'Aktif', '2004'),
('10000010', '10000010', 'SMK Bina Teknologi', 'SMK', 'Swasta', 'B', '01020', 'Jalan Bina Teknologi', 'Aktif', '2010'),
('10000011', '10000011', 'SD Negeri Johan Pahlawan', 'SD', 'Negeri', 'A', '05011', 'Jalan Johan Pahlawan', 'Aktif', '1997'),
('10000012', '10000012', 'SMP Negeri Saree', 'SMP', 'Negeri', 'A', '05012', 'Jalan Saree', 'Aktif', '1999'),
('10000013', '10000013', 'SMA Negeri Samatiga', 'SMA', 'Negeri', 'B', '05021', 'Jalan Samatiga', 'Aktif', '2002'),
('10000014', '10000014', 'SMK Negeri Aceh Barat', 'SMK', 'Negeri', 'A', '05022', 'Jalan Aceh Barat', 'Aktif', '2006'),
('10000015', '10000015', 'SD Negeri Arongan', 'SD', 'Negeri', 'B', '05031', 'Jalan Arongan', 'Aktif', '2001'),
('10000016', '10000016', 'SMP Harapan Meulaboh', 'SMP', 'Swasta', 'C', '05032', 'Jalan Meulaboh', 'Aktif', '2012'),
('10000017', '10000017', 'SMA Negeri Darul Imarah', 'SMA', 'Negeri', 'A', '07031', 'Jalan Darul Imarah', 'Aktif', '1994'),
('10000018', '10000018', 'SMK Teknologi Aceh', 'SMK', 'Swasta', 'B', '07032', 'Jalan Montasik', 'Aktif', '2015'),
('10000019', '10000019', 'SD Negeri Lamno', 'SD', 'Negeri', 'B', '07051', 'Jalan Lamno', 'Aktif', '2000'),
('10000020', '10000020', 'SMP Negeri Lhoknga', 'SMP', 'Negeri', 'A', '07052', 'Jalan Lhoknga', 'Aktif', '2007');

-- --------------------------------------------------------

--
-- Table structure for table `tb_siswa`
--

CREATE TABLE `tb_siswa` (
  `nik` char(16) NOT NULL,
  `nisn` char(10) NOT NULL,
  `nama_siswa` varchar(25) NOT NULL,
  `jenis_kelamin` enum('L','P') NOT NULL,
  `tanggal_lahir` date DEFAULT NULL,
  `id_sekolah` char(8) NOT NULL,
  `id_waktu` int(11) NOT NULL,
  `kelas` varchar(10) DEFAULT NULL,
  `jurusan` varchar(100) DEFAULT NULL,
  `tahun_masuk` year(4) DEFAULT NULL,
  `status_siswa` enum('Aktif','Lulus','Pindah','Keluar') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_siswa`
--

INSERT INTO `tb_siswa` (`nik`, `nisn`, `nama_siswa`, `jenis_kelamin`, `tanggal_lahir`, `id_sekolah`, `id_waktu`, `kelas`, `jurusan`, `tahun_masuk`, `status_siswa`) VALUES
('1173999900010001', '5000000001', 'Aulia Rahma', 'P', '2012-02-14', '10000001', 4, 'TK B', NULL, '2025', 'Aktif'),
('1173999900010002', '5000000002', 'Fajar Maulana', 'L', '2011-06-21', '10000002', 4, '5', NULL, '2024', 'Aktif'),
('1173999900010003', '5000000003', 'Nabila Putri', 'P', '2013-09-03', '10000003', 4, '6', NULL, '2025', 'Lulus'),
('1173999900010004', '5000000004', 'Rizki Saputra', 'L', '2010-12-18', '10000004', 4, '4', NULL, '2023', 'Aktif'),
('1173999900010005', '5000000005', 'Salsa Amelia', 'P', '2012-04-09', '10000005', 4, '8', NULL, '2024', 'Aktif'),
('1173999900010006', '5000000006', 'Daffa Pratama', 'L', '2011-08-27', '10000006', 4, '9', NULL, '2025', 'Aktif'),
('1173999900010007', '5000000007', 'Citra Lestari', 'P', '2010-01-12', '10000007', 4, '7', NULL, '2023', 'Aktif'),
('1173999900010008', '5000000008', 'Bagas Ramadhan', 'L', '2013-05-30', '10000008', 4, '11', 'TKJ', '2024', 'Lulus'),
('1173999900010009', '5000000009', 'Mutiara Sari', 'P', '2012-11-07', '10000009', 4, '12', 'RPL', '2025', 'Aktif'),
('1173999900010010', '5000000010', 'Rafi Kurniawan', 'L', '2011-03-25', '10000010', 4, '10', 'Akuntansi', '2023', 'Aktif'),
('1173999900010011', '5000000011', 'Intan Permata', 'P', '2010-07-16', '10000011', 4, '5', NULL, '2024', 'Aktif'),
('1173999900010012', '5000000012', 'Doni Saputra', 'L', '2013-10-05', '10000012', 4, '9', NULL, '2025', 'Aktif'),
('1173999900010013', '5000000013', 'Aisyah Fitri', 'P', '2012-01-29', '10000013', 4, '10', 'TKJ', '2023', 'Lulus'),
('1173999900010014', '5000000014', 'Galang Pratama', 'L', '2011-09-14', '10000014', 4, '11', 'RPL', '2024', 'Aktif'),
('1173999900010015', '5000000015', 'Maya Safitri', 'P', '2010-05-22', '10000015', 4, '6', NULL, '2025', 'Aktif'),
('1173999900010016', '5000000016', 'Iqbal Maulana', 'L', '2013-02-08', '10000016', 4, '7', NULL, '2023', 'Aktif'),
('1173999900010017', '5000000017', 'Nisa Khairani', 'P', '2012-06-19', '10000017', 4, '11', 'IPS', '2024', 'Aktif'),
('1173999900010018', '5000000018', 'Fauzan Akbar', 'L', '2011-11-28', '10000018', 4, '12', 'TKJ', '2025', 'Lulus'),
('1173999900010019', '5000000019', 'Putri Wulandari', 'P', '2010-03-17', '10000019', 4, '4', NULL, '2023', 'Aktif'),
('1173999900010020', '5000000020', 'Rendy Hidayat', 'L', '2013-08-04', '10000020', 4, '8', NULL, '2024', 'Aktif'),
('1173999900010021', '5000000021', 'Sarah Nabila', 'P', '2012-10-23', '10000001', 4, 'TK B', NULL, '2025', 'Aktif'),
('1173999900010022', '5000000022', 'Yoga Pranata', 'L', '2011-04-11', '10000002', 4, '4', NULL, '2023', 'Aktif'),
('1173999900010023', '5000000023', 'Dewi Anggraini', 'P', '2010-09-29', '10000003', 4, '5', NULL, '2024', 'Lulus'),
('1173999900010024', '5000000024', 'Arif Setiawan', 'L', '2013-01-15', '10000004', 4, '6', NULL, '2025', 'Aktif'),
('1173999900010025', '5000000025', 'Vina Oktaviani', 'P', '2012-07-02', '10000005', 4, '7', NULL, '2023', 'Aktif'),
('1173999900010026', '5000000026', 'Hafiz Maulana', 'L', '2011-12-09', '10000006', 4, '8', NULL, '2024', 'Aktif'),
('1173999900010027', '5000000027', 'Laila Hasanah', 'P', '2010-06-26', '10000007', 4, '9', NULL, '2025', 'Aktif'),
('1173999900010028', '5000000028', 'Bima Saputra', 'L', '2013-03-20', '10000008', 4, '10', 'TKJ', '2023', 'Lulus'),
('1173999900010029', '5000000029', 'Fitria Handayani', 'P', '2012-09-13', '10000009', 4, '11', 'RPL', '2024', 'Aktif'),
('1173999900010030', '5000000030', 'Dimas Ramadhan', 'L', '2011-05-06', '10000010', 4, '12', 'Akuntansi', '2025', 'Aktif');

-- --------------------------------------------------------

--
-- Table structure for table `tb_waktu`
--

CREATE TABLE `tb_waktu` (
  `id_waktu` int(11) NOT NULL,
  `tahun` year(4) NOT NULL,
  `semester` enum('Ganjil','Genap') NOT NULL,
  `tanggal_mulai` date DEFAULT NULL,
  `tanggal_selesai` date DEFAULT NULL,
  `status_periode` enum('Aktif','Tidak Aktif') DEFAULT 'Aktif'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_waktu`
--

INSERT INTO `tb_waktu` (`id_waktu`, `tahun`, `semester`, `tanggal_mulai`, `tanggal_selesai`, `status_periode`) VALUES
(1, '2024', 'Ganjil', '2024-07-15', '2024-12-20', 'Tidak Aktif'),
(2, '2024', 'Genap', '2025-01-06', '2025-06-20', 'Tidak Aktif'),
(3, '2025', 'Ganjil', '2025-07-14', '2025-12-19', 'Tidak Aktif'),
(4, '2026', 'Ganjil', '2026-07-13', '2026-12-18', 'Aktif');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_pendidikan`
--
ALTER TABLE `tb_pendidikan`
  ADD PRIMARY KEY (`id_pendidikan`),
  ADD KEY `fk_pendidikan_sekolah` (`id_sekolah`),
  ADD KEY `fk_pendidikan_waktu` (`id_waktu`);

--
-- Indexes for table `tb_ptk`
--
ALTER TABLE `tb_ptk`
  ADD PRIMARY KEY (`id_ptk`),
  ADD UNIQUE KEY `nik` (`nik`),
  ADD UNIQUE KEY `nuptk` (`nuptk`),
  ADD KEY `fk_ptk_sekolah` (`id_sekolah`);

--
-- Indexes for table `tb_sarana`
--
ALTER TABLE `tb_sarana`
  ADD PRIMARY KEY (`id_sarana`),
  ADD KEY `fk_sarana_sekolah` (`id_sekolah`),
  ADD KEY `fk_sarana_waktu` (`id_waktu`);

--
-- Indexes for table `tb_sekolah`
--
ALTER TABLE `tb_sekolah`
  ADD PRIMARY KEY (`id_sekolah`),
  ADD UNIQUE KEY `npsn` (`npsn`);

--
-- Indexes for table `tb_siswa`
--
ALTER TABLE `tb_siswa`
  ADD PRIMARY KEY (`nik`),
  ADD UNIQUE KEY `nisn` (`nisn`),
  ADD KEY `fk_pesertadidik_sekolah` (`id_sekolah`),
  ADD KEY `fk_pesertadidik_waktu` (`id_waktu`);

--
-- Indexes for table `tb_waktu`
--
ALTER TABLE `tb_waktu`
  ADD PRIMARY KEY (`id_waktu`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_pendidikan`
--
ALTER TABLE `tb_pendidikan`
  MODIFY `id_pendidikan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `tb_sarana`
--
ALTER TABLE `tb_sarana`
  MODIFY `id_sarana` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `tb_waktu`
--
ALTER TABLE `tb_waktu`
  MODIFY `id_waktu` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tb_pendidikan`
--
ALTER TABLE `tb_pendidikan`
  ADD CONSTRAINT `fk_pendidikan_sekolah` FOREIGN KEY (`id_sekolah`) REFERENCES `tb_sekolah` (`id_sekolah`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_pendidikan_waktu` FOREIGN KEY (`id_waktu`) REFERENCES `tb_waktu` (`id_waktu`) ON UPDATE CASCADE;

--
-- Constraints for table `tb_ptk`
--
ALTER TABLE `tb_ptk`
  ADD CONSTRAINT `fk_ptk_sekolah` FOREIGN KEY (`id_sekolah`) REFERENCES `tb_sekolah` (`id_sekolah`) ON UPDATE CASCADE;

--
-- Constraints for table `tb_sarana`
--
ALTER TABLE `tb_sarana`
  ADD CONSTRAINT `fk_sarana_sekolah` FOREIGN KEY (`id_sekolah`) REFERENCES `tb_sekolah` (`id_sekolah`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_sarana_waktu` FOREIGN KEY (`id_waktu`) REFERENCES `tb_waktu` (`id_waktu`) ON UPDATE CASCADE;

--
-- Constraints for table `tb_siswa`
--
ALTER TABLE `tb_siswa`
  ADD CONSTRAINT `fk_pesertadidik_sekolah` FOREIGN KEY (`id_sekolah`) REFERENCES `tb_sekolah` (`id_sekolah`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_pesertadidik_waktu` FOREIGN KEY (`id_waktu`) REFERENCES `tb_waktu` (`id_waktu`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
