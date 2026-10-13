-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Oct 06, 2026 at 05:24 AM
-- Server version: 8.4.3
-- PHP Version: 8.3.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_ketaben`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_bencana`
--

CREATE TABLE `tb_bencana` (
  `id_bencana` int NOT NULL,
  `jenis_bencana` varchar(100) NOT NULL,
  `lokasi` varchar(150) NOT NULL,
  `deskripsi_kejadian` text,
  `tanggal_kejadian` datetime NOT NULL,
  `tingkat_keparahan` enum('ringan','sedang','berat') NOT NULL,
  `status_tanggap` enum('tanggap darurat','pemulihan','selesai') NOT NULL DEFAULT 'tanggap darurat',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_bencana`
--

INSERT INTO `tb_bencana` (`id_bencana`, `jenis_bencana`, `lokasi`, `deskripsi_kejadian`, `tanggal_kejadian`, `tingkat_keparahan`, `status_tanggap`, `created_at`, `updated_at`) VALUES
(1, 'gempa bumi', 'Pidie Jaya, Kecamatan Bandar Baru', 'Gempa berkekuatan 6.5 SR mengguncang wilayah Pidie Jaya pada dini hari. Getaran dirasakan hingga Banda Aceh dan Bireuen.', '2024-01-15 03:22:00', 'berat', 'selesai', '2024-01-15 04:00:00', '2024-06-20 10:00:00'),
(2, 'banjir', 'Aceh Utara, Kecamatan Lhoksukon', 'Banjir bandang akibat luapan Sungai Jambo Aye yang merendam 8 desa di Kecamatan Lhoksukon.', '2024-03-10 14:30:00', 'sedang', 'selesai', '2024-03-10 15:00:00', '2024-04-25 09:00:00'),
(3, 'tanah longsor', 'Aceh Tengah, Kecamatan Silih Nara', 'Longsor terjadi di lereng bukit akibat hujan deras selama 3 hari berturut-turut, menutupi akses jalan Trans Aceh.', '2024-05-22 08:15:00', 'sedang', 'selesai', '2024-05-22 09:00:00', '2024-07-10 11:30:00'),
(4, 'kebakaran', 'Banda Aceh, Kecamatan Baiturrahman', 'Kebakaran hebat melanda pasar tradisional Peunayong, diduga akibat korsleting listrik pada dini hari.', '2024-07-18 02:45:00', 'sedang', 'selesai', '2024-07-18 03:15:00', '2024-09-05 14:00:00'),
(5, 'banjir', 'Aceh Besar, Kecamatan Indrapuri', 'Banjir rob dan luapan sungai merendam pemukiman dan sawah warga akibat air pasang dan intensitas hujan tinggi.', '2024-09-05 16:00:00', 'ringan', 'selesai', '2024-09-05 17:00:00', '2024-10-12 08:00:00'),
(6, 'gempa bumi', 'Aceh Barat, Kecamatan Woyla', 'Gempa tektonik berkekuatan 5.8 SR dengan pusat gempa di laut lepas pantai barat Aceh, menyebabkan kepanikan warga.', '2025-02-08 11:20:00', 'sedang', 'selesai', '2025-02-08 12:00:00', '2025-04-20 10:00:00'),
(7, 'angin puting beliung', 'Bireuen, Kecamatan Peusangan', 'Angin kencang disertai hujan lebat merusak puluhan rumah dan menumbangkan pohon serta tiang listrik.', '2025-06-12 15:30:00', 'ringan', 'selesai', '2025-06-12 16:00:00', '2025-07-30 09:00:00'),
(8, 'banjir', 'Aceh Timur, Kecamatan Idi Rayeuk', 'Banjir melanda kawasan pesisir dan perkotaan Idi Rayeuk akibat curah hujan ekstrem dan drainase buruk.', '2025-11-20 10:00:00', 'sedang', 'pemulihan', '2025-11-20 11:00:00', '2026-01-15 13:00:00'),
(9, 'tanah longsor', 'Gayo Lues, Kecamatan Blangkejeren', 'Longsor menutup jalan penghubung antar kecamatan dan menimbun 2 rumah warga di lereng pegunungan.', '2026-04-03 06:45:00', 'berat', 'pemulihan', '2026-04-03 07:30:00', '2026-08-10 14:00:00'),
(10, 'gempa bumi', 'Simeulue, Kecamatan Teluk Dalam', 'Gempa berkekuatan 6.2 SR dengan episentrum di barat daya Simeulue, diikuti beberapa gempa susulan.', '2026-08-25 09:10:00', 'berat', 'tanggap darurat', '2026-08-25 09:45:00', '2026-08-25 09:45:00');

-- --------------------------------------------------------

--
-- Table structure for table `tb_korban_bencana`
--

CREATE TABLE `tb_korban_bencana` (
  `id_korban` int NOT NULL,
  `id_bencana` int NOT NULL,
  `jenis_korban` enum('meninggal','luka berat','luka ringan','hilang','mengungsi') NOT NULL,
  `jumlah_korban` int UNSIGNED NOT NULL,
  `keterangan` varchar(100) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_korban_bencana`
--

INSERT INTO `tb_korban_bencana` (`id_korban`, `id_bencana`, `jenis_korban`, `jumlah_korban`, `keterangan`, `created_at`, `updated_at`) VALUES
(1, 1, 'meninggal', 102, 'RSUD Cut Nyak Dhien Meulaboh', '2024-01-15 05:00:00', '2024-01-15 05:00:00'),
(2, 1, 'luka berat', 215, 'RSUD Zainoel Abidin dan RS TNI Kesdam IM', '2024-01-15 05:00:00', '2024-01-15 05:00:00'),
(3, 1, 'luka ringan', 487, 'Puskesmas dan klinik setempat', '2024-01-15 06:00:00', '2024-01-15 06:00:00'),
(4, 1, 'mengungsi', 8420, 'Posko GOR Pidie Jaya dan tenda darurat', '2024-01-15 07:00:00', '2024-01-15 07:00:00'),
(5, 2, 'meninggal', 3, 'RSUD Lhokseumawe', '2024-03-10 16:00:00', '2024-03-10 16:00:00'),
(6, 2, 'luka ringan', 12, 'Terseret arus banjir, luka lecet', '2024-03-10 16:30:00', '2024-03-10 16:30:00'),
(7, 2, 'mengungsi', 1850, 'Balai desa dan masjid setempat', '2024-03-10 17:00:00', '2024-03-10 17:00:00'),
(8, 3, 'meninggal', 7, 'Tertimbun longsoran tanah', '2024-05-22 10:00:00', '2024-05-22 10:00:00'),
(9, 3, 'luka berat', 5, 'RSUD Takengon', '2024-05-22 11:00:00', '2024-05-22 11:00:00'),
(10, 3, 'luka ringan', 18, 'Puskesmas Silih Nara', '2024-05-22 11:30:00', '2024-05-22 11:30:00'),
(11, 3, 'mengungsi', 320, 'Posko kecamatan', '2024-05-22 12:00:00', '2024-05-22 12:00:00'),
(12, 4, 'meninggal', 8, 'Terbakar di dalam bangunan', '2024-07-18 04:00:00', '2024-07-18 04:00:00'),
(13, 4, 'luka berat', 15, 'Luka bakar tingkat 2 dan 3, RSUD Meuraxa', '2024-07-18 05:00:00', '2024-07-18 05:00:00'),
(14, 4, 'luka ringan', 28, 'Sesak napas akibat asap', '2024-07-18 06:00:00', '2024-07-18 06:00:00'),
(15, 4, 'mengungsi', 450, 'Pedagang pasar kehilangan tempat usaha', '2024-07-18 08:00:00', '2024-07-18 08:00:00'),
(16, 5, 'luka ringan', 5, 'Terpeleset saat evakuasi', '2024-09-05 18:00:00', '2024-09-05 18:00:00'),
(17, 5, 'mengungsi', 680, 'Balai desa Indrapuri', '2024-09-05 19:00:00', '2024-09-05 19:00:00'),
(18, 6, 'luka ringan', 45, 'Panik dan terluka ringan saat evakuasi', '2025-02-08 13:00:00', '2025-02-08 13:00:00'),
(19, 6, 'mengungsi', 2100, 'Lapangan terbuka dan masjid', '2025-02-08 14:00:00', '2025-02-08 14:00:00'),
(20, 7, 'luka ringan', 18, 'Tertimpa reruntuhan atap', '2025-06-12 17:00:00', '2025-06-12 17:00:00'),
(21, 7, 'mengungsi', 285, 'Rumah warga yang masih layak', '2025-06-12 18:00:00', '2025-06-12 18:00:00'),
(22, 8, 'meninggal', 2, 'Terseret arus banjir', '2025-11-20 12:00:00', '2025-11-20 12:00:00'),
(23, 8, 'luka ringan', 22, 'Puskesmas Idi Rayeuk', '2025-11-20 13:00:00', '2025-11-20 13:00:00'),
(24, 8, 'mengungsi', 1520, 'Gedung sekolah dan balai kecamatan', '2025-11-20 14:00:00', '2025-11-20 14:00:00'),
(25, 9, 'meninggal', 14, 'Tertimbun rumah yang longsor', '2026-04-03 08:00:00', '2026-04-03 08:00:00'),
(26, 9, 'luka berat', 8, 'RSUD Blangkejeren', '2026-04-03 09:00:00', '2026-04-03 09:00:00'),
(27, 9, 'luka ringan', 25, 'Luka akibat reruntuhan', '2026-04-03 10:00:00', '2026-04-03 10:00:00'),
(28, 9, 'hilang', 3, 'Masih dalam pencarian', '2026-04-03 11:00:00', '2026-04-03 11:00:00'),
(29, 9, 'mengungsi', 950, 'Posko lapangan dan tenda darurat', '2026-04-03 12:00:00', '2026-04-03 12:00:00'),
(30, 10, 'meninggal', 18, 'Tertimpa reruntuhan bangunan', '2026-08-25 10:00:00', '2026-08-25 10:00:00'),
(31, 10, 'luka berat', 67, 'RSUD Simeulue', '2026-08-25 11:00:00', '2026-08-25 11:00:00'),
(32, 10, 'luka ringan', 142, 'Puskesmas dan klinik', '2026-08-25 12:00:00', '2026-08-25 12:00:00'),
(33, 10, 'mengungsi', 4200, 'Lapangan terbuka Teluk Dalam', '2026-08-25 13:00:00', '2026-08-25 13:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `tb_kerusakan_bencana`
--

CREATE TABLE `tb_kerusakan_bencana` (
  `id_kerusakan` int NOT NULL,
  `id_bencana` int NOT NULL,
  `jenis_objek` varchar(100) NOT NULL,
  `tingkat_kerusakan` enum('rusak ringan','rusak berat','rusak total') NOT NULL,
  `jumlah_unit` int UNSIGNED NOT NULL,
  `estimasi_kerugian_rupiah` bigint DEFAULT NULL,
  `lokasi_kerusakan` varchar(150) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_kerusakan_bencana`
--

INSERT INTO `tb_kerusakan_bencana` (`id_kerusakan`, `id_bencana`, `jenis_objek`, `tingkat_kerusakan`, `jumlah_unit`, `estimasi_kerugian_rupiah`, `lokasi_kerusakan`, `created_at`, `updated_at`) VALUES
(1, 1, 'rumah', 'rusak total', 1245, 156000000000, 'Pidie Jaya, berbagai kecamatan', '2024-01-15 08:00:00', '2024-01-15 08:00:00'),
(2, 1, 'rumah', 'rusak berat', 2870, 143500000000, 'Pidie Jaya, berbagai kecamatan', '2024-01-15 08:00:00', '2024-01-15 08:00:00'),
(3, 1, 'sekolah', 'rusak berat', 45, 22500000000, 'Kecamatan Bandar Baru dan sekitarnya', '2024-01-15 09:00:00', '2024-01-15 09:00:00'),
(4, 1, 'masjid', 'rusak berat', 78, 15600000000, 'Seluruh Pidie Jaya', '2024-01-15 09:30:00', '2024-01-15 09:30:00'),
(5, 1, 'puskesmas', 'rusak berat', 8, 16000000000, 'Pidie Jaya', '2024-01-15 10:00:00', '2024-01-15 10:00:00'),
(6, 1, 'jalan', 'rusak berat', 35, 87500000000, '35 km jalan rusak', '2024-01-15 10:30:00', '2024-01-15 10:30:00'),
(7, 2, 'rumah', 'rusak total', 125, 12500000000, 'Lhoksukon, 8 desa', '2024-03-10 18:00:00', '2024-03-10 18:00:00'),
(8, 2, 'rumah', 'rusak ringan', 340, 8500000000, 'Lhoksukon', '2024-03-10 18:30:00', '2024-03-10 18:30:00'),
(9, 2, 'sekolah', 'rusak ringan', 12, 2400000000, 'Kecamatan Lhoksukon', '2024-03-10 19:00:00', '2024-03-10 19:00:00'),
(10, 2, 'jalan', 'rusak ringan', 8, 4000000000, 'Jalan desa tergenang', '2024-03-10 19:30:00', '2024-03-10 19:30:00'),
(11, 2, 'irigasi', 'rusak berat', 5, 7500000000, 'Saluran irigasi tersumbat lumpur', '2024-03-10 20:00:00', '2024-03-10 20:00:00'),
(12, 3, 'rumah', 'rusak total', 18, 2700000000, 'Kecamatan Silih Nara', '2024-05-22 13:00:00', '2024-05-22 13:00:00'),
(13, 3, 'rumah', 'rusak berat', 32, 4800000000, 'Lereng bukit Silih Nara', '2024-05-22 13:30:00', '2024-05-22 13:30:00'),
(14, 3, 'jalan', 'rusak total', 3, 18000000000, 'Trans Aceh tertutup longsoran', '2024-05-22 14:00:00', '2024-05-22 14:00:00'),
(15, 3, 'jembatan', 'rusak berat', 2, 8000000000, 'Jembatan di Silih Nara', '2024-05-22 14:30:00', '2024-05-22 14:30:00'),
(16, 4, 'rumah', 'rusak total', 85, 8500000000, 'Sekitar Pasar Peunayong', '2024-07-18 09:00:00', '2024-07-18 09:00:00'),
(17, 4, 'pasar', 'rusak total', 1, 45000000000, 'Pasar Peunayong', '2024-07-18 09:30:00', '2024-07-18 09:30:00'),
(18, 4, 'kios', 'rusak total', 420, 21000000000, 'Kios pedagang di pasar', '2024-07-18 10:00:00', '2024-07-18 10:00:00'),
(19, 5, 'rumah', 'rusak ringan', 215, 5375000000, 'Kecamatan Indrapuri', '2024-09-05 20:00:00', '2024-09-05 20:00:00'),
(20, 5, 'sawah', 'rusak ringan', 450, 6750000000, 'Sawah terendam', '2024-09-05 20:30:00', '2024-09-05 20:30:00'),
(21, 6, 'rumah', 'rusak berat', 78, 11700000000, 'Kecamatan Woyla', '2025-02-08 15:00:00', '2025-02-08 15:00:00'),
(22, 6, 'rumah', 'rusak ringan', 245, 6125000000, 'Aceh Barat pesisir', '2025-02-08 15:30:00', '2025-02-08 15:30:00'),
(23, 6, 'masjid', 'rusak berat', 15, 3000000000, 'Kecamatan Woyla', '2025-02-08 16:00:00', '2025-02-08 16:00:00'),
(24, 6, 'sekolah', 'rusak ringan', 8, 1600000000, 'Woyla dan sekitarnya', '2025-02-08 16:30:00', '2025-02-08 16:30:00'),
(25, 7, 'rumah', 'rusak berat', 42, 6300000000, 'Kecamatan Peusangan', '2025-06-12 19:00:00', '2025-06-12 19:00:00'),
(26, 7, 'rumah', 'rusak ringan', 88, 2200000000, 'Bireuen', '2025-06-12 19:30:00', '2025-06-12 19:30:00'),
(27, 7, 'gardu listrik', 'rusak berat', 12, 2400000000, 'Tiang listrik tumbang', '2025-06-12 20:00:00', '2025-06-12 20:00:00'),
(28, 8, 'rumah', 'rusak total', 95, 9500000000, 'Idi Rayeuk kawasan pesisir', '2025-11-20 15:00:00', '2025-11-20 15:00:00'),
(29, 8, 'rumah', 'rusak ringan', 310, 7750000000, 'Aceh Timur', '2025-11-20 15:30:00', '2025-11-20 15:30:00'),
(30, 8, 'sekolah', 'rusak ringan', 15, 3000000000, 'Kecamatan Idi Rayeuk', '2025-11-20 16:00:00', '2025-11-20 16:00:00'),
(31, 8, 'jalan', 'rusak ringan', 12, 6000000000, 'Jalan kota tergenang', '2025-11-20 16:30:00', '2025-11-20 16:30:00'),
(32, 9, 'rumah', 'rusak total', 28, 4200000000, 'Lereng Blangkejeren', '2026-04-03 13:00:00', '2026-04-03 13:00:00'),
(33, 9, 'rumah', 'rusak berat', 45, 6750000000, 'Gayo Lues', '2026-04-03 13:30:00', '2026-04-03 13:30:00'),
(34, 9, 'jalan', 'rusak total', 5, 25000000000, 'Jalan antar kecamatan tertimbun', '2026-04-03 14:00:00', '2026-04-03 14:00:00'),
(35, 9, 'sekolah', 'rusak berat', 3, 1500000000, 'SD dan SMP di lereng', '2026-04-03 14:30:00', '2026-04-03 14:30:00'),
(36, 10, 'rumah', 'rusak total', 285, 42750000000, 'Teluk Dalam dan sekitarnya', '2026-08-25 14:00:00', '2026-08-25 14:00:00'),
(37, 10, 'rumah', 'rusak berat', 520, 78000000000, 'Simeulue', '2026-08-25 14:30:00', '2026-08-25 14:30:00'),
(38, 10, 'sekolah', 'rusak berat', 18, 9000000000, 'Seluruh Simeulue', '2026-08-25 15:00:00', '2026-08-25 15:00:00'),
(39, 10, 'puskesmas', 'rusak berat', 5, 10000000000, 'Puskesmas di Simeulue', '2026-08-25 15:30:00', '2026-08-25 15:30:00'),
(40, 10, 'masjid', 'rusak berat', 32, 6400000000, 'Berbagai kecamatan', '2026-08-25 16:00:00', '2026-08-25 16:00:00'),
(41, 10, 'jalan', 'rusak berat', 28, 70000000000, 'Jalan rusak di Simeulue', '2026-08-25 16:30:00', '2026-08-25 16:30:00');

-- --------------------------------------------------------

--
-- Table structure for table `tb_bantuan`
--

CREATE TABLE `tb_bantuan` (
  `id_bantuan` int NOT NULL,
  `id_bencana` int NOT NULL,
  `jenis_bantuan` varchar(150) NOT NULL,
  `sumber_bantuan` varchar(150) NOT NULL,
  `jumlah_bantuan` varchar(15) NOT NULL,
  `satuan` varchar(50) NOT NULL,
  `penerima_bantuan` varchar(200) DEFAULT NULL,
  `tanggal_distribusi` datetime NOT NULL,
  `lokasi_distribusi` varchar(150) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_bantuan`
--

INSERT INTO `tb_bantuan` (`id_bantuan`, `id_bencana`, `jenis_bantuan`, `sumber_bantuan`, `jumlah_bantuan`, `satuan`, `penerima_bantuan`, `tanggal_distribusi`, `lokasi_distribusi`, `created_at`, `updated_at`) VALUES
(1, 1, 'sembako', 'BNPB', '8500', 'paket', 'Pengungsi di Posko GOR Pidie Jaya', '2024-01-16 08:00:00', 'GOR Pidie Jaya', '2024-01-16 08:00:00', '2024-01-16 08:00:00'),
(2, 1, 'tenda darurat', 'PMI Aceh', '250', 'unit', 'Korban gempa Pidie Jaya', '2024-01-16 10:00:00', 'Lapangan Kecamatan Bandar Baru', '2024-01-16 10:00:00', '2024-01-16 10:00:00'),
(3, 1, 'obat-obatan', 'Kemenkes RI', '1200', 'paket', 'Puskesmas dan posko kesehatan', '2024-01-17 09:00:00', 'Puskesmas Pidie Jaya', '2024-01-17 09:00:00', '2024-01-17 09:00:00'),
(4, 1, 'uang tunai', 'Pemerintah Aceh', '50000000000', 'rupiah', 'Keluarga korban meninggal dan rumah rusak berat', '2024-01-20 10:00:00', 'Kantor Bupati Pidie Jaya', '2024-01-20 10:00:00', '2024-01-20 10:00:00'),
(5, 1, 'selimut', 'Donor internasional', '5000', 'unit', 'Pengungsi di tenda darurat', '2024-01-18 14:00:00', 'Posko-posko pengungsian', '2024-01-18 14:00:00', '2024-01-18 14:00:00'),
(6, 2, 'sembako', 'BPBD Aceh', '1900', 'paket', 'Korban banjir Lhoksukon', '2024-03-11 08:00:00', 'Balai Desa Lhoksukon', '2024-03-11 08:00:00', '2024-03-11 08:00:00'),
(7, 2, 'air bersih', 'PDAM Tirta Meuligoe', '25000', 'liter', 'Warga terdampak banjir', '2024-03-11 10:00:00', '8 desa di Lhoksukon', '2024-03-11 10:00:00', '2024-03-11 10:00:00'),
(8, 2, 'uang tunai', 'Pemerintah Pusat', '5000000000', 'rupiah', 'Keluarga korban meninggal dan rumah rusak', '2024-03-15 09:00:00', 'Kecamatan Lhoksukon', '2024-03-15 09:00:00', '2024-03-15 09:00:00'),
(9, 3, 'logistik', 'TNI dan Polri', '350', 'paket', 'Korban longsor Silih Nara', '2024-05-23 07:00:00', 'Posko Kecamatan Silih Nara', '2024-05-23 07:00:00', '2024-05-23 07:00:00'),
(10, 3, 'obat-obatan', 'Dinas Kesehatan Aceh Tengah', '180', 'paket', 'Puskesmas Silih Nara', '2024-05-23 09:00:00', 'Puskesmas Silih Nara', '2024-05-23 09:00:00', '2024-05-23 09:00:00'),
(11, 3, 'uang tunai', 'Pemerintah Aceh', '3500000000', 'rupiah', 'Keluarga korban meninggal', '2024-05-25 10:00:00', 'Kantor Camat Silih Nara', '2024-05-25 10:00:00', '2024-05-25 10:00:00'),
(12, 4, 'sembako', 'Baznas Aceh', '500', 'paket', 'Pedagang Pasar Peunayong', '2024-07-18 12:00:00', 'Posko Baiturrahman', '2024-07-18 12:00:00', '2024-07-18 12:00:00'),
(13, 4, 'uang tunai', 'Pemerintah Kota Banda Aceh', '15000000000', 'rupiah', 'Pedagang kehilangan kios dan korban', '2024-07-22 09:00:00', 'Balai Kota Banda Aceh', '2024-07-22 09:00:00', '2024-07-22 09:00:00'),
(14, 4, 'obat luka bakar', 'RS Zainoel Abidin', '85', 'paket', 'Korban luka bakar', '2024-07-18 10:00:00', 'RS Zainoel Abidin', '2024-07-18 10:00:00', '2024-07-18 10:00:00'),
(15, 5, 'sembako', 'Masyarakat Aceh Besar', '700', 'paket', 'Korban banjir Indrapuri', '2024-09-06 08:00:00', 'Balai Desa Indrapuri', '2024-09-06 08:00:00', '2024-09-06 08:00:00'),
(16, 5, 'pompa air', 'BPBD Aceh Besar', '15', 'unit', 'Warga untuk memompa air banjir', '2024-09-06 10:00:00', 'Kecamatan Indrapuri', '2024-09-06 10:00:00', '2024-09-06 10:00:00'),
(17, 6, 'sembako', 'BPBD Aceh', '2200', 'paket', 'Pengungsi gempa Woyla', '2025-02-09 07:00:00', 'Posko Kecamatan Woyla', '2025-02-09 07:00:00', '2025-02-09 07:00:00'),
(18, 6, 'tenda darurat', 'PMI Aceh Barat', '120', 'unit', 'Korban gempa', '2025-02-09 10:00:00', 'Lapangan Woyla', '2025-02-09 10:00:00', '2025-02-09 10:00:00'),
(19, 6, 'uang tunai', 'Pemerintah Aceh', '12000000000', 'rupiah', 'Keluarga rumah rusak berat', '2025-02-12 09:00:00', 'Kantor Bupati Aceh Barat', '2025-02-12 09:00:00', '2025-02-12 09:00:00'),
(20, 7, 'terpal', 'BPBD Bireuen', '150', 'unit', 'Korban angin puting beliung', '2025-06-13 08:00:00', 'Kecamatan Peusangan', '2025-06-13 08:00:00', '2025-06-13 08:00:00'),
(21, 7, 'sembako', 'Baznas Bireuen', '300', 'paket', 'Warga rumah rusak', '2025-06-13 10:00:00', 'Balai Kecamatan Peusangan', '2025-06-13 10:00:00', '2025-06-13 10:00:00'),
(22, 7, 'uang tunai', 'Pemerintah Kabupaten Bireuen', '3500000000', 'rupiah', 'Keluarga rumah rusak', '2025-06-15 09:00:00', 'Kantor Bupati Bireuen', '2025-06-15 09:00:00', '2025-06-15 09:00:00'),
(23, 8, 'sembako', 'BNPB', '1600', 'paket', 'Pengungsi banjir Idi Rayeuk', '2025-11-21 08:00:00', 'Posko Sekolah Idi Rayeuk', '2025-11-21 08:00:00', '2025-11-21 08:00:00'),
(24, 8, 'obat-obatan', 'Dinas Kesehatan Aceh Timur', '220', 'paket', 'Puskesmas Idi Rayeuk', '2025-11-21 10:00:00', 'Puskesmas Idi Rayeuk', '2025-11-21 10:00:00', '2025-11-21 10:00:00'),
(25, 8, 'air bersih', 'NGO Water for Life', '30000', 'liter', 'Warga terdampak banjir', '2025-11-22 09:00:00', 'Aceh Timur', '2025-11-22 09:00:00', '2025-11-22 09:00:00'),
(26, 8, 'uang tunai', 'Pemerintah Aceh', '8500000000', 'rupiah', 'Keluarga korban dan rumah rusak', '2025-11-25 09:00:00', 'Kantor Bupati Aceh Timur', '2025-11-25 09:00:00', '2025-11-25 09:00:00'),
(27, 9, 'sembako', 'BNPB', '1000', 'paket', 'Korban longsor Blangkejeren', '2026-04-04 07:00:00', 'Posko Lapangan Blangkejeren', '2026-04-04 07:00:00', '2026-04-04 07:00:00'),
(28, 9, 'tenda darurat', 'PMI Gayo Lues', '80', 'unit', 'Pengungsi longsor', '2026-04-04 09:00:00', 'Lapangan Blangkejeren', '2026-04-04 09:00:00', '2026-04-04 09:00:00'),
(29, 9, 'obat-obatan', 'Kemenkes RI', '150', 'paket', 'RSUD dan Puskesmas Blangkejeren', '2026-04-05 08:00:00', 'RSUD Blangkejeren', '2026-04-05 08:00:00', '2026-04-05 08:00:00'),
(30, 9, 'uang tunai', 'Pemerintah Aceh', '12000000000', 'rupiah', 'Keluarga korban meninggal dan hilang', '2026-04-08 10:00:00', 'Kantor Bupati Gayo Lues', '2026-04-08 10:00:00', '2026-04-08 10:00:00'),
(31, 10, 'sembako', 'BNPB', '4500', 'paket', 'Pengungsi gempa Simeulue', '2026-08-26 07:00:00', 'Lapangan Teluk Dalam', '2026-08-26 07:00:00', '2026-08-26 07:00:00'),
(32, 10, 'tenda darurat', 'PMI Aceh', '350', 'unit', 'Korban gempa Simeulue', '2026-08-26 09:00:00', 'Teluk Dalam', '2026-08-26 09:00:00', '2026-08-26 09:00:00'),
(33, 10, 'obat-obatan', 'Kemenkes RI', '580', 'paket', 'RSUD dan Puskesmas Simeulue', '2026-08-26 10:00:00', 'RSUD Simeulue', '2026-08-26 10:00:00', '2026-08-26 10:00:00'),
(34, 10, 'air bersih', 'PDAM dan NGO', '50000', 'liter', 'Pengungsi di tenda darurat', '2026-08-27 08:00:00', 'Posko-posko Simeulue', '2026-08-27 08:00:00', '2026-08-27 08:00:00'),
(35, 10, 'selimut', 'Donor internasional', '3000', 'unit', 'Pengungsi Simeulue', '2026-08-27 10:00:00', 'Lapangan Teluk Dalam', '2026-08-27 10:00:00', '2026-08-27 10:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `tb_rehabilitasi`
--

CREATE TABLE `tb_rehabilitasi` (
  `id_rehabilitasi` int NOT NULL,
  `id_bencana` int NOT NULL,
  `jenis_rehabilitasi` varchar(150) NOT NULL,
  `lokasi` varchar(150) NOT NULL,
  `deskripsi_kegiatan` text,
  `tanggal_mulai` datetime NOT NULL,
  `tanggal_selesai` datetime DEFAULT NULL,
  `anggaran_rupiah` bigint NOT NULL,
  `sumber_dana` varchar(100) NOT NULL,
  `status_pelaksanaan` enum('perencanaan','dalam proses','selesai','tertunda') NOT NULL DEFAULT 'perencanaan',
  `persentase_penyelesaian` tinyint UNSIGNED NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_rehabilitasi`
--

INSERT INTO `tb_rehabilitasi` (`id_rehabilitasi`, `id_bencana`, `jenis_rehabilitasi`, `lokasi`, `deskripsi_kegiatan`, `tanggal_mulai`, `tanggal_selesai`, `anggaran_rupiah`, `sumber_dana`, `status_pelaksanaan`, `persentase_penyelesaian`, `created_at`, `updated_at`) VALUES
(1, 1, 'perbaikan rumah', 'Pidie Jaya, berbagai kecamatan', 'Perbaikan rumah rusak berat dan ringan pasca gempa untuk 2000 unit rumah', '2024-02-01 08:00:00', '2024-05-30 17:00:00', 85000000000, 'APBN', 'selesai', 100, '2024-02-01 08:00:00', '2024-05-30 17:00:00'),
(2, 1, 'trauma healing', 'Pidie Jaya', 'Program pendampingan psikososial untuk korban gempa, khususnya anak-anak dan lansia', '2024-01-20 09:00:00', '2024-04-20 17:00:00', 2500000000, 'Donor', 'selesai', 100, '2024-01-20 09:00:00', '2024-04-20 17:00:00'),
(3, 1, 'infrastruktur publik', 'Pidie Jaya', 'Perbaikan sekolah, masjid, dan puskesmas yang rusak', '2024-03-01 08:00:00', '2024-06-15 17:00:00', 45000000000, 'APBA', 'selesai', 100, '2024-03-01 08:00:00', '2024-06-15 17:00:00'),
(4, 2, 'perbaikan infrastruktur publik', 'Lhoksukon, Aceh Utara', 'Pembersihan lumpur di sekolah dan perbaikan fasilitas umum', '2024-03-15 08:00:00', '2024-04-10 17:00:00', 8000000000, 'APBA', 'selesai', 100, '2024-03-15 08:00:00', '2024-04-10 17:00:00'),
(5, 2, 'pemulihan ekonomi', 'Lhoksukon', 'Bantuan modal usaha untuk warga yang terdampak banjir', '2024-03-20 09:00:00', '2024-04-20 17:00:00', 5000000000, 'Hibah', 'selesai', 100, '2024-03-20 09:00:00', '2024-04-20 17:00:00'),
(6, 3, 'perbaikan rumah', 'Silih Nara, Aceh Tengah', 'Perbaikan 50 rumah yang rusak akibat longsor', '2024-06-01 08:00:00', '2024-07-05 17:00:00', 12000000000, 'APBN', 'selesai', 100, '2024-06-01 08:00:00', '2024-07-05 17:00:00'),
(7, 3, 'trauma healing', 'Silih Nara', 'Pendampingan psikososial untuk keluarga korban meninggal', '2024-05-25 09:00:00', '2024-06-25 17:00:00', 1500000000, 'Donor', 'selesai', 100, '2024-05-25 09:00:00', '2024-06-25 17:00:00'),
(8, 4, 'pemulihan ekonomi', 'Pasar Peunayong, Banda Aceh', 'Bantuan modal usaha untuk pedagang yang kehilangan kios', '2024-08-01 09:00:00', '2024-09-01 17:00:00', 35000000000, 'APBA', 'selesai', 100, '2024-08-01 09:00:00', '2024-09-01 17:00:00'),
(9, 4, 'trauma healing', 'Banda Aceh', 'Konseling untuk korban luka bakar dan keluarga korban meninggal', '2024-07-22 09:00:00', '2024-08-22 17:00:00', 1800000000, 'Donor', 'selesai', 100, '2024-07-22 09:00:00', '2024-08-22 17:00:00'),
(10, 5, 'perbaikan infrastruktur publik', 'Indrapuri, Aceh Besar', 'Perbaikan drainase dan jalan desa yang rusak', '2024-09-15 08:00:00', '2024-10-10 17:00:00', 4500000000, 'APBA', 'selesai', 100, '2024-09-15 08:00:00', '2024-10-10 17:00:00'),
(11, 6, 'perbaikan rumah', 'Woyla, Aceh Barat', 'Perbaikan 323 rumah rusak pasca gempa', '2025-03-01 08:00:00', '2025-04-15 17:00:00', 28000000000, 'APBN', 'selesai', 100, '2025-03-01 08:00:00', '2025-04-15 17:00:00'),
(12, 6, 'infrastruktur publik', 'Aceh Barat', 'Perbaikan masjid dan sekolah yang rusak', '2025-03-10 08:00:00', '2025-04-20 17:00:00', 8500000000, 'APBA', 'selesai', 100, '2025-03-10 08:00:00', '2025-04-20 17:00:00'),
(13, 7, 'perbaikan rumah', 'Peusangan, Bireuen', 'Perbaikan atap dan struktur rumah rusak angin', '2025-06-20 08:00:00', '2025-07-25 17:00:00', 9500000000, 'APBA', 'selesai', 100, '2025-06-20 08:00:00', '2025-07-25 17:00:00'),
(14, 7, 'infrastruktur publik', 'Bireuen', 'Perbaikan jaringan listrik yang rusak', '2025-06-18 08:00:00', '2025-07-10 17:00:00', 3200000000, 'APBN', 'selesai', 100, '2025-06-18 08:00:00', '2025-07-10 17:00:00'),
(15, 8, 'perbaikan rumah', 'Idi Rayeuk, Aceh Timur', 'Perbaikan 405 rumah rusak banjir', '2025-12-01 08:00:00', '2026-01-10 17:00:00', 22000000000, 'APBN', 'selesai', 100, '2025-12-01 08:00:00', '2026-01-10 17:00:00'),
(16, 8, 'infrastruktur publik', 'Aceh Timur', 'Pembersihan sekolah dan perbaikan fasilitas umum', '2025-11-25 08:00:00', '2025-12-20 17:00:00', 6500000000, 'APBA', 'selesai', 100, '2025-11-25 08:00:00', '2025-12-20 17:00:00'),
(17, 8, 'pemulihan ekonomi', 'Idi Rayeuk', 'Bantuan modal usaha untuk pedagang dan petani', '2025-12-05 09:00:00', NULL, 8000000000, 'Hibah', 'dalam proses', 75, '2025-12-05 09:00:00', '2026-01-15 13:00:00'),
(18, 9, 'perbaikan rumah', 'Blangkejeren, Gayo Lues', 'Perbaikan dan relokasi rumah rusak longsor', '2026-05-01 08:00:00', NULL, 18000000000, 'APBN', 'dalam proses', 60, '2026-05-01 08:00:00', '2026-08-10 14:00:00'),
(19, 9, 'trauma healing', 'Gayo Lues', 'Pendampingan psikososial untuk keluarga korban', '2026-04-10 09:00:00', NULL, 2000000000, 'Donor', 'dalam proses', 70, '2026-04-10 09:00:00', '2026-08-10 14:00:00'),
(20, 9, 'infrastruktur publik', 'Blangkejeren', 'Perbaikan sekolah yang rusak', '2026-06-01 08:00:00', NULL, 3500000000, 'APBA', 'dalam proses', 45, '2026-06-01 08:00:00', '2026-08-10 14:00:00'),
(21, 10, 'perbaikan rumah', 'Simeulue', 'Perbaikan darurat rumah rusak gempa', '2026-09-01 08:00:00', NULL, 95000000000, 'APBN', 'dalam proses', 20, '2026-09-01 08:00:00', '2026-09-01 08:00:00'),
(22, 10, 'trauma healing', 'Teluk Dalam, Simeulue', 'Program pendampingan psikososial untuk korban gempa', '2026-08-28 09:00:00', NULL, 3500000000, 'Donor', 'dalam proses', 30, '2026-08-28 09:00:00', '2026-08-28 09:00:00'),
(23, 10, 'infrastruktur publik', 'Simeulue', 'Perbaikan puskesmas, sekolah, dan masjid', '2026-09-10 08:00:00', NULL, 28000000000, 'APBA', 'perencanaan', 0, '2026-09-10 08:00:00', '2026-09-10 08:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `tb_rekonstruksi`
--

CREATE TABLE `tb_rekonstruksi` (
  `id_rekonstruksi` int NOT NULL,
  `id_bencana` int NOT NULL,
  `nama_proyek` varchar(200) NOT NULL,
  `jenis_pembangunan` varchar(150) NOT NULL,
  `lokasi` varchar(150) NOT NULL,
  `anggaran_rupiah` bigint NOT NULL,
  `sumber_dana` varchar(100) NOT NULL,
  `kontraktor_pelaksana` varchar(200) DEFAULT NULL,
  `tanggal_mulai` datetime NOT NULL,
  `tanggal_target_selesai` datetime NOT NULL,
  `tanggal_selesai_aktual` datetime DEFAULT NULL,
  `persentase_penyelesaian` tinyint UNSIGNED NOT NULL DEFAULT '0',
  `status_proyek` enum('perencanaan','tender','konstruksi','selesai','ditangguhkan') NOT NULL DEFAULT 'perencanaan',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_rekonstruksi`
--

INSERT INTO `tb_rekonstruksi` (`id_rekonstruksi`, `id_bencana`, `nama_proyek`, `jenis_pembangunan`, `lokasi`, `anggaran_rupiah`, `sumber_dana`, `kontraktor_pelaksana`, `tanggal_mulai`, `tanggal_target_selesai`, `tanggal_selesai_aktual`, `persentase_penyelesaian`, `status_proyek`, `created_at`, `updated_at`) VALUES
(1, 1, 'Pembangunan 500 Unit Rumah Permanen Korban Gempa Pidie Jaya', 'rumah permanen', 'Pidie Jaya, berbagai kecamatan', 175000000000, 'APBN', 'PT Aceh Maju Sejahtera', '2024-04-01 08:00:00', '2024-09-30 17:00:00', '2024-09-28 16:00:00', 100, 'selesai', '2024-04-01 08:00:00', '2024-09-28 16:00:00'),
(2, 1, 'Rekonstruksi Jalan Trans Aceh Pidie Jaya 35 km', 'jalan', 'Pidie Jaya', 95000000000, 'APBN', 'PT Pembangunan Infrastruktur Nusantara', '2024-05-01 08:00:00', '2024-10-31 17:00:00', '2024-10-25 17:00:00', 100, 'selesai', '2024-05-01 08:00:00', '2024-10-25 17:00:00'),
(3, 1, 'Pembangunan Kembali 15 Sekolah Rusak Gempa', 'sekolah', 'Pidie Jaya', 45000000000, 'APBN', 'PT Karya Pendidikan Indonesia', '2024-06-01 08:00:00', '2024-12-31 17:00:00', '2024-12-20 17:00:00', 100, 'selesai', '2024-06-01 08:00:00', '2024-12-20 17:00:00'),
(4, 2, 'Normalisasi Sungai Jambo Aye', 'infrastruktur pengairan', 'Lhoksukon, Aceh Utara', 12000000000, 'APBA', 'PT Tirta Engineering', '2024-05-01 08:00:00', '2024-08-31 17:00:00', '2024-08-28 17:00:00', 100, 'selesai', '2024-05-01 08:00:00', '2024-08-28 17:00:00'),
(5, 2, 'Perbaikan Saluran Irigasi 5 Desa', 'irigasi', 'Lhoksukon', 8500000000, 'APBN', 'CV Bangun Tani Aceh', '2024-06-01 08:00:00', '2024-09-30 17:00:00', '2024-09-25 17:00:00', 100, 'selesai', '2024-06-01 08:00:00', '2024-09-25 17:00:00'),
(6, 3, 'Rekonstruksi Jalan Trans Aceh Silih Nara 3 km', 'jalan', 'Silih Nara, Aceh Tengah', 22000000000, 'APBN', 'PT Pembangunan Infrastruktur Nusantara', '2024-07-01 08:00:00', '2024-11-30 17:00:00', '2024-11-28 17:00:00', 100, 'selesai', '2024-07-01 08:00:00', '2024-11-28 17:00:00'),
(7, 3, 'Perbaikan 2 Jembatan Rusak Longsor', 'jembatan', 'Silih Nara', 9500000000, 'APBA', 'PT Jembatan Aceh Raya', '2024-08-01 08:00:00', '2024-12-31 17:00:00', '2024-12-28 17:00:00', 100, 'selesai', '2024-08-01 08:00:00', '2024-12-28 17:00:00'),
(8, 4, 'Pembangunan Kembali Pasar Peunayong', 'pasar', 'Banda Aceh', 68000000000, 'APBA', 'PT Perdagangan Aceh Jaya', '2024-10-01 08:00:00', '2025-06-30 17:00:00', '2025-06-25 17:00:00', 100, 'selesai', '2024-10-01 08:00:00', '2025-06-25 17:00:00'),
(9, 4, 'Relokasi dan Pembangunan 85 Unit Rumah Korban Kebakaran', 'rumah permanen', 'Banda Aceh', 25500000000, 'APBN', 'PT Hunian Aceh Mandiri', '2024-09-01 08:00:00', '2025-03-31 17:00:00', '2025-03-28 17:00:00', 100, 'selesai', '2024-09-01 08:00:00', '2025-03-28 17:00:00'),
(10, 5, 'Perbaikan Sistem Drainase Indrapuri', 'infrastruktur drainase', 'Indrapuri, Aceh Besar', 8500000000, 'APBA', 'CV Tirta Aceh Besar', '2024-11-01 08:00:00', '2025-02-28 17:00:00', '2025-02-25 17:00:00', 100, 'selesai', '2024-11-01 08:00:00', '2025-02-25 17:00:00'),
(11, 6, 'Pembangunan 78 Unit Rumah Permanen Korban Gempa Woyla', 'rumah permanen', 'Woyla, Aceh Barat', 27300000000, 'APBN', 'PT Aceh Barat Konstruksi', '2025-05-01 08:00:00', '2025-10-31 17:00:00', '2025-10-28 17:00:00', 100, 'selesai', '2025-05-01 08:00:00', '2025-10-28 17:00:00'),
(12, 6, 'Rekonstruksi 15 Masjid Rusak Gempa', 'tempat ibadah', 'Aceh Barat', 9000000000, 'Donor', 'Yayasan Masjid Aceh', '2025-06-01 08:00:00', '2025-11-30 17:00:00', '2025-11-25 17:00:00', 100, 'selesai', '2025-06-01 08:00:00', '2025-11-25 17:00:00'),
(13, 7, 'Pembangunan 42 Unit Rumah Korban Angin', 'rumah permanen', 'Peusangan, Bireuen', 14700000000, 'APBA', 'PT Bireuen Mandiri', '2025-08-01 08:00:00', '2025-12-31 17:00:00', '2025-12-28 17:00:00', 100, 'selesai', '2025-08-01 08:00:00', '2025-12-28 17:00:00'),
(14, 8, 'Pembangunan 95 Unit Rumah Permanen Korban Banjir Idi', 'rumah permanen', 'Idi Rayeuk, Aceh Timur', 33250000000, 'APBN', 'PT Timur Aceh Konstruksi', '2026-02-01 08:00:00', '2026-07-31 17:00:00', '2026-07-28 17:00:00', 100, 'selesai', '2026-02-01 08:00:00', '2026-07-28 17:00:00'),
(15, 8, 'Perbaikan Sistem Drainase Kota Idi Rayeuk', 'infrastruktur drainase', 'Idi Rayeuk', 15000000000, 'APBA', 'CV Aceh Timur Engineering', '2026-03-01 08:00:00', '2026-08-31 17:00:00', NULL, 85, 'konstruksi', '2026-03-01 08:00:00', '2026-08-10 10:00:00'),
(16, 9, 'Rekonstruksi Jalan Antar Kecamatan Gayo Lues 5 km', 'jalan', 'Blangkejeren, Gayo Lues', 28000000000, 'APBN', 'PT Pembangunan Infrastruktur Nusantara', '2026-06-01 08:00:00', '2026-12-31 17:00:00', NULL, 50, 'konstruksi', '2026-06-01 08:00:00', '2026-08-10 14:00:00'),
(17, 9, 'Relokasi dan Pembangunan 28 Unit Rumah Permanen', 'rumah permanen', 'Blangkejeren', 11200000000, 'APBN', 'PT Gayo Lues Sejahtera', '2026-07-01 08:00:00', '2026-12-31 17:00:00', NULL, 40, 'konstruksi', '2026-07-01 08:00:00', '2026-08-10 14:00:00'),
(18, 10, 'Pembangunan 285 Unit Rumah Permanen Korban Gempa Simeulue', 'rumah permanen', 'Simeulue', 99750000000, 'APBN', NULL, '2026-11-01 08:00:00', '2027-06-30 17:00:00', NULL, 0, 'perencanaan', '2026-09-01 10:00:00', '2026-09-01 10:00:00'),
(19, 10, 'Rekonstruksi Jalan Rusak Gempa 28 km', 'jalan', 'Simeulue', 84000000000, 'APBN', NULL, '2026-12-01 08:00:00', '2027-08-31 17:00:00', NULL, 0, 'tender', '2026-09-05 10:00:00', '2026-09-10 14:00:00'),
(20, 10, 'Pembangunan Kembali 18 Sekolah Rusak Gempa', 'sekolah', 'Simeulue', 36000000000, 'APBN', NULL, '2027-01-01 08:00:00', '2027-09-30 17:00:00', NULL, 0, 'perencanaan', '2026-09-08 10:00:00', '2026-09-08 10:00:00');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_bencana`
--
ALTER TABLE `tb_bencana`
  ADD PRIMARY KEY (`id_bencana`),
  ADD KEY `idx_bencana_tanggal` (`tanggal_kejadian`),
  ADD KEY `idx_bencana_lokasi` (`lokasi`),
  ADD KEY `idx_bencana_jenis` (`jenis_bencana`);

--
-- Indexes for table `tb_korban_bencana`
--
ALTER TABLE `tb_korban_bencana`
  ADD PRIMARY KEY (`id_korban`),
  ADD KEY `idx_korban_bencana` (`id_bencana`);

--
-- Indexes for table `tb_kerusakan_bencana`
--
ALTER TABLE `tb_kerusakan_bencana`
  ADD PRIMARY KEY (`id_kerusakan`),
  ADD KEY `idx_kerusakan_bencana` (`id_bencana`);

--
-- Indexes for table `tb_bantuan`
--
ALTER TABLE `tb_bantuan`
  ADD PRIMARY KEY (`id_bantuan`),
  ADD KEY `idx_bantuan_bencana` (`id_bencana`),
  ADD KEY `idx_bantuan_tanggal` (`tanggal_distribusi`);

--
-- Indexes for table `tb_rehabilitasi`
--
ALTER TABLE `tb_rehabilitasi`
  ADD PRIMARY KEY (`id_rehabilitasi`),
  ADD KEY `idx_rehabilitasi_bencana` (`id_bencana`),
  ADD KEY `idx_rehabilitasi_status` (`status_pelaksanaan`);

--
-- Indexes for table `tb_rekonstruksi`
--
ALTER TABLE `tb_rekonstruksi`
  ADD PRIMARY KEY (`id_rekonstruksi`),
  ADD KEY `idx_rekonstruksi_bencana` (`id_bencana`),
  ADD KEY `idx_rekonstruksi_status` (`status_proyek`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_bencana`
--
ALTER TABLE `tb_bencana`
  MODIFY `id_bencana` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `tb_korban_bencana`
--
ALTER TABLE `tb_korban_bencana`
  MODIFY `id_korban` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT for table `tb_kerusakan_bencana`
--
ALTER TABLE `tb_kerusakan_bencana`
  MODIFY `id_kerusakan` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;

--
-- AUTO_INCREMENT for table `tb_bantuan`
--
ALTER TABLE `tb_bantuan`
  MODIFY `id_bantuan` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT for table `tb_rehabilitasi`
--
ALTER TABLE `tb_rehabilitasi`
  MODIFY `id_rehabilitasi` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `tb_rekonstruksi`
--
ALTER TABLE `tb_rekonstruksi`
  MODIFY `id_rekonstruksi` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tb_korban_bencana`
--
ALTER TABLE `tb_korban_bencana`
  ADD CONSTRAINT `tb_korban_bencana_ibfk_1` FOREIGN KEY (`id_bencana`) REFERENCES `tb_bencana` (`id_bencana`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_kerusakan_bencana`
--
ALTER TABLE `tb_kerusakan_bencana`
  ADD CONSTRAINT `tb_kerusakan_bencana_ibfk_1` FOREIGN KEY (`id_bencana`) REFERENCES `tb_bencana` (`id_bencana`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_bantuan`
--
ALTER TABLE `tb_bantuan`
  ADD CONSTRAINT `tb_bantuan_ibfk_1` FOREIGN KEY (`id_bencana`) REFERENCES `tb_bencana` (`id_bencana`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_rehabilitasi`
--
ALTER TABLE `tb_rehabilitasi`
  ADD CONSTRAINT `tb_rehabilitasi_ibfk_1` FOREIGN KEY (`id_bencana`) REFERENCES `tb_bencana` (`id_bencana`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_rekonstruksi`
--
ALTER TABLE `tb_rekonstruksi`
  ADD CONSTRAINT `tb_rekonstruksi_ibfk_1` FOREIGN KEY (`id_bencana`) REFERENCES `tb_bencana` (`id_bencana`) ON DELETE RESTRICT ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
