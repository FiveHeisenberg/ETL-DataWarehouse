-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 04, 2026 at 04:36 AM
-- Server version: 8.4.3
-- PHP Version: 8.3.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_dispenda`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_kategori_pajak`
--

CREATE TABLE `tb_kategori_pajak` (
  `id_kategori` int NOT NULL,
  `nama_pajak` varchar(100) NOT NULL,
  `tarif_persentase` decimal(5,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_kategori_pajak`
--

INSERT INTO `tb_kategori_pajak` (`id_kategori`, `nama_pajak`, `tarif_persentase`) VALUES
(1, 'Pajak Kendaraan Bermotor (Roda 2)', 1.50),
(2, 'Pajak Kendaraan Bermotor (Roda 4)', 2.00),
(3, 'Pajak Air Permukaan', 10.00),
(4, 'Pajak Alat Berat', 0.20),
(5, 'Pajak Rokok', 10.00);

-- --------------------------------------------------------

--
-- Table structure for table `tb_objek_pajak`
--

CREATE TABLE `tb_objek_pajak` (
  `id_objek` int NOT NULL,
  `nik_wp` varchar(16) NOT NULL,
  `id_kategori` int NOT NULL,
  `nomor_identitas_aset` varchar(50) DEFAULT NULL,
  `rincian_objek` varchar(100) NOT NULL,
  `nilai_aset` bigint NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_objek_pajak`
--

INSERT INTO `tb_objek_pajak` (`id_objek`, `nik_wp`, `id_kategori`, `nomor_identitas_aset`, `rincian_objek`, `nilai_aset`) VALUES
(1, '1173010101010001', 1, 'BL 1234 ABC', 'Honda Vario BL 1234 ABC', 15000000),
(2, '1173010101010001', 2, 'BL 5678 XYZ', 'Toyota Brio BL 5678 XYZ', 150000000),
(3, '1173010101010002', 1, 'BL 9999 K', 'Yamaha NMAX BL 9999 K', 25000000),
(4, '1173010101010003', 3, 'NOP-SB-2026-001', 'Sumur Bor Industri', 50000000),
(5, '1173010101010004', 2, 'BL 111 AA', 'Honda HR-V BL 111 AA', 300000000),
(6, '1173010102010005', 4, 'ALB-PC200-006', 'Ekskavator PC200', 800000000),
(7, '1173010102010006', 2, 'BL 222 BB', 'Toyota Innova BL 222 BB', 350000000),
(8, '1173010102010007', 1, 'BL 4444 CD', 'Honda Beat BL 4444 CD', 12000000),
(9, '1173010102010008', 1, 'BL 7777 EF', 'Yamaha Aerox BL 7777 EF', 23000000),
(10, '1173010103010009', 2, 'BL 888 GG', 'Mitsubishi Fortuner BL 888 GG', 450000000);

-- --------------------------------------------------------

--
-- Table structure for table `tb_pembayaran`
--

CREATE TABLE `tb_pembayaran` (
  `id_pembayaran` int NOT NULL,
  `id_tagihan` int NOT NULL,
  `tanggal_bayar` date NOT NULL,
  `jumlah_bayar` bigint NOT NULL,
  `denda_keterlambatan` bigint DEFAULT '0',
  `metode_bayar` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_pembayaran`
--

INSERT INTO `tb_pembayaran` (`id_pembayaran`, `id_tagihan`, `tanggal_bayar`, `jumlah_bayar`, `denda_keterlambatan`, `metode_bayar`) VALUES
(1, 1, '2026-03-15', 225000, 0, 'Transfer Bank Aceh'),
(2, 3, '2026-04-10', 375000, 0, 'Qris Dana'),
(3, 4, '2026-05-20', 5000000, 0, 'Transfer Bank Jago'),
(4, 6, '2026-06-05', 1600000, 0, 'Tunai Teller'),
(5, 7, '2026-07-11', 7000000, 0, 'Transfer BSI'),
(6, 10, '2026-08-01', 9000000, 0, 'Transfer BSI');

-- --------------------------------------------------------

--
-- Table structure for table `tb_tagihan`
--

CREATE TABLE `tb_tagihan` (
  `id_tagihan` int NOT NULL,
  `id_objek` int NOT NULL,
  `tahun_pajak` year NOT NULL,
  `nominal_tagihan` bigint NOT NULL,
  `tanggal_jatuh_tempo` date DEFAULT NULL,
  `status_tagihan` enum('Belum Lunas','Lunas') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_tagihan`
--

INSERT INTO `tb_tagihan` (`id_tagihan`, `id_objek`, `tahun_pajak`, `nominal_tagihan`, `tanggal_jatuh_tempo`, `status_tagihan`) VALUES
(1, 1, '2026', 225000, '2026-06-30', 'Lunas'),
(2, 2, '2026', 3000000, '2026-12-31', 'Lunas'),
(3, 3, '2026', 375000, '2026-06-30', 'Lunas'),
(4, 4, '2026', 5000000, '2026-06-30', 'Lunas'),
(5, 5, '2026', 6000000, '2026-12-31', 'Belum Lunas'),
(6, 6, '2026', 1600000, '2026-09-30', 'Lunas'),
(7, 7, '2026', 7000000, '2026-09-30', 'Lunas'),
(8, 8, '2026', 180000, '2026-12-31', 'Belum Lunas'),
(9, 9, '2026', 345000, '2026-12-31', 'Lunas'),
(10, 10, '2026', 9000000, '2026-09-30', 'Lunas');

-- --------------------------------------------------------

--
-- Table structure for table `tb_wajib_pajak`
--

CREATE TABLE `tb_wajib_pajak` (
  `nik_wp` varchar(16) NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `jenis_kelamin` enum('Pria','Wanita') NOT NULL,
  `alamat` varchar(255) DEFAULT NULL,
  `kabupaten_kota` varchar(50) DEFAULT NULL,
  `npwpd` varchar(25) DEFAULT NULL,
  `tanggal_daftar` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_wajib_pajak`
--

INSERT INTO `tb_wajib_pajak` (`nik_wp`, `nama_lengkap`, `jenis_kelamin`, `alamat`, `kabupaten_kota`, `npwpd`, `tanggal_daftar`) VALUES
('1173010101010001', 'Ahmad Rizki Kurniawan', 'Pria', 'Jl. Merdeka No. 1, Banda Aceh', 'Banda Aceh', 'P.1173.001', '2026-08-01'),
('1173010101010002', 'Siti Nur Azizah', 'Wanita', 'Jl. Merdeka No. 2, Lhokseumawe', 'Lhokseumawe', 'P.1173.002', '2026-08-01'),
('1173010101010003', 'Hendra Gunawan', 'Pria', 'Jl. Merdeka No. 3, Banda Aceh', 'Banda Aceh', 'P.1173.003', '2026-08-01'),
('1173010101010004', 'Nurul Habibah', 'Wanita', 'Jl. Merdeka No. 4, Lhokseumawe', 'Lhokseumawe', 'P.1173.004', '2026-08-01'),
('1173010102010005', 'Ridho Pratama', 'Pria', 'Jl. Merdeka No. 5, Banda Aceh', 'Banda Aceh', 'P.1173.005', '2026-08-01'),
('1173010102010006', 'Eka Putri Santoso', 'Wanita', 'Jl. Merdeka No. 6, Lhokseumawe', 'Lhokseumawe', 'P.1173.006', '2026-08-01'),
('1173010102010007', 'Muhammad Ilham', 'Pria', 'Jl. Merdeka No. 7, Banda Aceh', 'Banda Aceh', 'P.1173.007', '2026-08-01'),
('1173010102010008', 'Dewi Lestari', 'Wanita', 'Jl. Merdeka No. 8, Lhokseumawe', 'Lhokseumawe', 'P.1173.008', '2026-08-01'),
('1173010103010009', 'Budi Santoso', 'Pria', 'Jl. Merdeka No. 9, Banda Aceh', 'Banda Aceh', 'P.1173.009', '2026-08-01'),
('1173010103010010', 'Sinta Wijaya', 'Wanita', 'Jl. Merdeka No. 10, Lhokseumawe', 'Lhokseumawe', 'P.1173.010', '2026-08-01'),
('1173010104010011', 'Rahman Hakim', 'Pria', 'Jl. Merdeka No. 11, Banda Aceh', 'Banda Aceh', 'P.1173.011', '2026-08-01'),
('1173010104010012', 'Linda Kusuma', 'Wanita', 'Jl. Merdeka No. 12, Lhokseumawe', 'Lhokseumawe', 'P.1173.012', '2026-08-01'),
('1173010105010013', 'Fajar Ramadhan', 'Pria', 'Jl. Merdeka No. 13, Banda Aceh', 'Banda Aceh', 'P.1173.013', '2026-08-01'),
('1173010105010014', 'Yuni Hartono', 'Wanita', 'Jl. Merdeka No. 14, Lhokseumawe', 'Lhokseumawe', 'P.1173.014', '2026-08-01'),
('1173010106010015', 'Arif Wijaksana', 'Pria', 'Jl. Merdeka No. 15, Banda Aceh', 'Banda Aceh', 'P.1173.015', '2026-08-01'),
('1173010106010016', 'Mira Handoko', 'Wanita', 'Jl. Merdeka No. 16, Lhokseumawe', 'Lhokseumawe', 'P.1173.016', '2026-08-01'),
('1173020101010017', 'Dimas Pratama', 'Pria', 'Jl. Merdeka No. 17, Banda Aceh', 'Banda Aceh', 'P.1173.017', '2026-08-01'),
('1173020101010018', 'Rini Susanto', 'Wanita', 'Jl. Merdeka No. 18, Lhokseumawe', 'Lhokseumawe', 'P.1173.018', '2026-08-01'),
('1173020102010019', 'Wahyu Prasetyo', 'Pria', 'Jl. Merdeka No. 19, Banda Aceh', 'Banda Aceh', 'P.1173.019', '2026-08-01'),
('1173020102010020', 'Siti Marjiah', 'Wanita', 'Jl. Merdeka No. 20, Lhokseumawe', 'Lhokseumawe', 'P.1173.020', '2026-08-01'),
('1173030101010021', 'Irfan Syaputra', 'Pria', 'Jl. Merdeka No. 21, Banda Aceh', 'Banda Aceh', 'P.1173.021', '2026-08-01'),
('1173030101010022', 'Anita Maharani', 'Wanita', 'Jl. Merdeka No. 22, Lhokseumawe', 'Lhokseumawe', 'P.1173.022', '2026-08-01'),
('1173030102010023', 'Zainal Abidin', 'Pria', 'Jl. Merdeka No. 23, Banda Aceh', 'Banda Aceh', 'P.1173.023', '2026-08-01'),
('1173030102010024', 'Ratna Dewi', 'Wanita', 'Jl. Merdeka No. 24, Lhokseumawe', 'Lhokseumawe', 'P.1173.024', '2026-08-01'),
('1173040101010025', 'Hendri Wijaya', 'Pria', 'Jl. Merdeka No. 25, Banda Aceh', 'Banda Aceh', 'P.1173.025', '2026-08-01'),
('1173040101010026', 'Joni Tarpada', 'Pria', 'Jl. Merdeka No. 26, Lhokseumawe', 'Lhokseumawe', 'P.1173.026', '2026-08-01'),
('1173040102010027', 'Karina Amelia', 'Wanita', 'Jl. Merdeka No. 27, Banda Aceh', 'Banda Aceh', 'P.1173.027', '2026-08-01'),
('1173040102010028', 'Bambang Sutrisno', 'Pria', 'Jl. Merdeka No. 28, Lhokseumawe', 'Lhokseumawe', 'P.1173.028', '2026-08-01'),
('1173040103010029', 'Susi Susanti', 'Wanita', 'Jl. Merdeka No. 29, Banda Aceh', 'Banda Aceh', 'P.1173.029', '2026-08-01'),
('1173040103010030', 'Toto Suryanto', 'Pria', 'Jl. Merdeka No. 30, Lhokseumawe', 'Lhokseumawe', 'P.1173.030', '2026-08-01'),
('1173050101010031', 'Rahmat Fauzi', 'Pria', 'Jl. Merdeka No. 31, Banda Aceh', 'Banda Aceh', 'P.1173.031', '2026-08-01'),
('1173050101010032', 'Lina Marlina', 'Wanita', 'Jl. Merdeka No. 32, Lhokseumawe', 'Lhokseumawe', 'P.1173.032', '2026-08-01'),
('1173050102010033', 'Syaiful Rahman', 'Pria', 'Jl. Merdeka No. 33, Banda Aceh', 'Banda Aceh', 'P.1173.033', '2026-08-01'),
('1173050102010034', 'Rina Kartini', 'Wanita', 'Jl. Merdeka No. 34, Lhokseumawe', 'Lhokseumawe', 'P.1173.034', '2026-08-01'),
('1173050201010035', 'Juanda Gunawan', 'Pria', 'Jl. Merdeka No. 35, Banda Aceh', 'Banda Aceh', 'P.1173.035', '2026-08-01'),
('1173050201010036', 'Ayu Permata', 'Wanita', 'Jl. Merdeka No. 36, Lhokseumawe', 'Lhokseumawe', 'P.1173.036', '2026-08-01'),
('1173050202010037', 'Danang Permadi', 'Pria', 'Jl. Merdeka No. 37, Banda Aceh', 'Banda Aceh', 'P.1173.037', '2026-08-01'),
('1173050202010038', 'Neneng Suryani', 'Wanita', 'Jl. Merdeka No. 38, Lhokseumawe', 'Lhokseumawe', 'P.1173.038', '2026-08-01'),
('1173050301010039', 'Ahmad Zainudin', 'Pria', 'Jl. Merdeka No. 39, Banda Aceh', 'Banda Aceh', 'P.1173.039', '2026-08-01'),
('1173050301010040', 'Masniyah Said', 'Wanita', 'Jl. Merdeka No. 40, Lhokseumawe', 'Lhokseumawe', 'P.1173.040', '2026-08-01'),
('1173070101010041', 'Suryadi Gunawan', 'Pria', 'Jl. Merdeka No. 41, Banda Aceh', 'Banda Aceh', 'P.1173.041', '2026-08-01'),
('1173070101010042', 'Fitri Wahyuni', 'Wanita', 'Jl. Merdeka No. 42, Lhokseumawe', 'Lhokseumawe', 'P.1173.042', '2026-08-01'),
('1173070102010043', 'Hari Prabowo', 'Pria', 'Jl. Merdeka No. 43, Banda Aceh', 'Banda Aceh', 'P.1173.043', '2026-08-01'),
('1173070102010044', 'Putri Maharini', 'Wanita', 'Jl. Merdeka No. 44, Lhokseumawe', 'Lhokseumawe', 'P.1173.044', '2026-08-01'),
('1173070103010045', 'Andi Wijaya', 'Pria', 'Jl. Merdeka No. 45, Banda Aceh', 'Banda Aceh', 'P.1173.045', '2026-08-01'),
('1173070103010046', 'Hilda Kusuma', 'Wanita', 'Jl. Merdeka No. 46, Lhokseumawe', 'Lhokseumawe', 'P.1173.046', '2026-08-01'),
('1173070104010047', 'Sumardi Santoso', 'Pria', 'Jl. Merdeka No. 47, Banda Aceh', 'Banda Aceh', 'P.1173.047', '2026-08-01'),
('1173070104010048', 'Soraya Amelia', 'Wanita', 'Jl. Merdeka No. 48, Lhokseumawe', 'Lhokseumawe', 'P.1173.048', '2026-08-01'),
('1173070201010049', 'Didik Rahmat', 'Pria', 'Jl. Merdeka No. 49, Banda Aceh', 'Banda Aceh', 'P.1173.049', '2026-08-01'),
('1173070201010050', 'Maya Kusuma', 'Wanita', 'Jl. Merdeka No. 50, Lhokseumawe', 'Lhokseumawe', 'P.1173.050', '2026-08-01'),
('1173070202010051', 'Rudi Hartono', 'Pria', 'Jl. Merdeka No. 51, Banda Aceh', 'Banda Aceh', 'P.1173.051', '2026-08-01'),
('1173070202010052', 'Indah Lestari', 'Wanita', 'Jl. Merdeka No. 52, Lhokseumawe', 'Lhokseumawe', 'P.1173.052', '2026-08-01'),
('1173070301010053', 'Tri Hartanto', 'Pria', 'Jl. Merdeka No. 53, Banda Aceh', 'Banda Aceh', 'P.1173.053', '2026-08-01'),
('1173070301010054', 'Dewi Puspita', 'Wanita', 'Jl. Merdeka No. 54, Lhokseumawe', 'Lhokseumawe', 'P.1173.054', '2026-08-01'),
('1173070302010055', 'Eka Prasetya', 'Pria', 'Jl. Merdeka No. 55, Banda Aceh', 'Banda Aceh', 'P.1173.055', '2026-08-01'),
('1173070302010056', 'Vivian Handoko', 'Wanita', 'Jl. Merdeka No. 56, Lhokseumawe', 'Lhokseumawe', 'P.1173.056', '2026-08-01'),
('1173070401010057', 'Budi Hermanto', 'Pria', 'Jl. Merdeka No. 57, Banda Aceh', 'Banda Aceh', 'P.1173.057', '2026-08-01'),
('1173070401010058', 'Suri Sumardjo', 'Wanita', 'Jl. Merdeka No. 58, Lhokseumawe', 'Lhokseumawe', 'P.1173.058', '2026-08-01'),
('1173070402010059', 'Gunawan Santoso', 'Pria', 'Jl. Merdeka No. 59, Banda Aceh', 'Banda Aceh', 'P.1173.059', '2026-08-01'),
('1173070402010060', 'Titik Wijaya', 'Wanita', 'Jl. Merdeka No. 60, Lhokseumawe', 'Lhokseumawe', 'P.1173.060', '2026-08-01');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_kategori_pajak`
--
ALTER TABLE `tb_kategori_pajak`
  ADD PRIMARY KEY (`id_kategori`);

--
-- Indexes for table `tb_objek_pajak`
--
ALTER TABLE `tb_objek_pajak`
  ADD PRIMARY KEY (`id_objek`),
  ADD KEY `nik_wp` (`nik_wp`),
  ADD KEY `id_kategori` (`id_kategori`);

--
-- Indexes for table `tb_pembayaran`
--
ALTER TABLE `tb_pembayaran`
  ADD PRIMARY KEY (`id_pembayaran`),
  ADD KEY `id_tagihan` (`id_tagihan`);

--
-- Indexes for table `tb_tagihan`
--
ALTER TABLE `tb_tagihan`
  ADD PRIMARY KEY (`id_tagihan`),
  ADD KEY `id_objek` (`id_objek`);

--
-- Indexes for table `tb_wajib_pajak`
--
ALTER TABLE `tb_wajib_pajak`
  ADD PRIMARY KEY (`nik_wp`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_kategori_pajak`
--
ALTER TABLE `tb_kategori_pajak`
  MODIFY `id_kategori` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `tb_objek_pajak`
--
ALTER TABLE `tb_objek_pajak`
  MODIFY `id_objek` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `tb_pembayaran`
--
ALTER TABLE `tb_pembayaran`
  MODIFY `id_pembayaran` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `tb_tagihan`
--
ALTER TABLE `tb_tagihan`
  MODIFY `id_tagihan` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tb_objek_pajak`
--
ALTER TABLE `tb_objek_pajak`
  ADD CONSTRAINT `tb_objek_pajak_ibfk_1` FOREIGN KEY (`nik_wp`) REFERENCES `tb_wajib_pajak` (`nik_wp`) ON DELETE CASCADE,
  ADD CONSTRAINT `tb_objek_pajak_ibfk_2` FOREIGN KEY (`id_kategori`) REFERENCES `tb_kategori_pajak` (`id_kategori`) ON DELETE RESTRICT;

--
-- Constraints for table `tb_pembayaran`
--
ALTER TABLE `tb_pembayaran`
  ADD CONSTRAINT `tb_pembayaran_ibfk_1` FOREIGN KEY (`id_tagihan`) REFERENCES `tb_tagihan` (`id_tagihan`) ON DELETE CASCADE;

--
-- Constraints for table `tb_tagihan`
--
ALTER TABLE `tb_tagihan`
  ADD CONSTRAINT `tb_tagihan_ibfk_1` FOREIGN KEY (`id_objek`) REFERENCES `tb_objek_pajak` (`id_objek`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
