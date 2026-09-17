-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 17 Sep 2026 pada 04.23
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_dinsos`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `penduduk`
--

CREATE TABLE `penduduk` (
  `nik` char(16) NOT NULL,
  `no_kk` char(16) NOT NULL,
  `nama_lengkap` varchar(150) NOT NULL,
  `tempat_lahir` varchar(100) NOT NULL,
  `tanggal_lahir` date NOT NULL,
  `jenis_kelamin` enum('L','P') NOT NULL,
  `alamat_ktp` text NOT NULL,
  `id_wilayah` char(10) NOT NULL,
  `status_kesejahteraan_desil` tinyint(3) UNSIGNED DEFAULT NULL COMMENT 'Skala 1 - 10',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `penduduk`
--

INSERT INTO `penduduk` (`nik`, `no_kk`, `nama_lengkap`, `tempat_lahir`, `tanggal_lahir`, `jenis_kelamin`, `alamat_ktp`, `id_wilayah`, `status_kesejahteraan_desil`, `created_at`) VALUES
('1173010101010001', '1173010101010001', 'Ahmad Rizki Kurniawan', 'Banda Aceh', '1985-03-15', 'L', 'Jalan Peuniti No. 123', '1171', 2, '2026-08-20 03:00:00'),
('1173010101010002', '1173010101010001', 'Siti Nur Azizah', 'Banda Aceh', '1988-07-22', 'P', 'Jalan Peuniti No. 123', '1171', 2, '2026-08-20 03:00:00'),
('1173010101010003', '1173010101010003', 'Hendra Gunawan', 'Banda Aceh', '1980-11-09', 'L', 'Jalan Punge Blang Cut No. 45', '1171', 1, '2026-08-20 03:00:00'),
('1173010101010004', '1173010101010003', 'Nurul Habibah', 'Aceh Besar', '1992-01-28', 'P', 'Jalan Punge Blang Cut No. 45', '1171', 2, '2026-08-20 03:00:00'),
('1173010102010005', '1173010102010005', 'Ridho Pratama', 'Banda Aceh', '1995-05-14', 'L', 'Jalan Lampriet No. 67', '1171', 1, '2026-08-20 03:00:00'),
('1173010102010006', '1173010102010005', 'Eka Putri Santoso', 'Lhokseumawe', '1990-09-03', 'P', 'Jalan Lampriet No. 67', '1171', 3, '2026-08-20 03:00:00'),
('1173010102010007', '1173010102010007', 'Muhammad Ilham', 'Banda Aceh', '1987-12-20', 'L', 'Jalan Larangan No. 89', '1171', 2, '2026-08-20 03:00:00'),
('1173010102010008', '1173010102010007', 'Dewi Lestari', 'Aceh Jaya', '1993-06-11', 'P', 'Jalan Larangan No. 89', '1171', 1, '2026-08-20 03:00:00'),
('1173010103010009', '1173010103010009', 'Budi Santoso', 'Banda Aceh', '1982-04-17', 'L', 'Jalan Rangkayo No. 101', '1171', 3, '2026-08-20 03:00:00'),
('1173010103010010', '1173010103010009', 'Sinta Wijaya', 'Sabang', '1991-10-26', 'P', 'Jalan Rangkayo No. 101', '1171', 2, '2026-08-20 03:00:00'),
('1173010104010011', '1173010104010011', 'Rahman Hakim', 'Banda Aceh', '1986-02-08', 'L', 'Jalan Lam U No. 112', '1171', 1, '2026-08-20 03:00:00'),
('1173010104010012', '1173010104010011', 'Linda Kusuma', 'Langsa', '1989-08-19', 'P', 'Jalan Lam U No. 112', '1171', 2, '2026-08-20 03:00:00'),
('1173010105010013', '1173010105010013', 'Fajar Ramadhan', 'Aceh Besar', '1994-03-05', 'L', 'Jalan Cot Kala No. 134', '1171', 1, '2026-08-20 03:00:00'),
('1173010105010014', '1173010105010013', 'Yuni Hartono', 'Banda Aceh', '1996-09-12', 'P', 'Jalan Cot Kala No. 134', '1171', 3, '2026-08-20 03:00:00'),
('1173010106010015', '1173010106010015', 'Arif Wijaksana', 'Aceh Utara', '1984-07-23', 'L', 'Jalan Pasa Baru No. 156', '1171', 2, '2026-08-20 03:00:00'),
('1173010106010016', '1173010106010015', 'Mira Handoko', 'Banda Aceh', '1988-11-30', 'P', 'Jalan Pasa Baru No. 156', '1171', 1, '2026-08-20 03:00:00'),
('1173020101010017', '1173020101010017', 'Dimas Pratama', 'Sabang', '1991-05-14', 'L', 'Jalan Pocut Baren No. 178', '1172', 3, '2026-08-20 03:00:00'),
('1173020101010018', '1173020101010017', 'Rini Susanto', 'Banda Aceh', '1993-12-02', 'P', 'Jalan Pocut Baren No. 178', '1172', 2, '2026-08-20 03:00:00'),
('1173020102010019', '1173020102010019', 'Wahyu Prasetyo', 'Sabang', '1985-06-16', 'L', 'Jalan Kuala No. 190', '1172', 1, '2026-08-20 03:00:00'),
('1173020102010020', '1173020102010019', 'Siti Marjiah', 'Sabang', '1987-10-21', 'P', 'Jalan Kuala No. 190', '1172', 4, '2026-08-20 03:00:00'),
('1173030101010021', '1173030101010021', 'Irfan Syaputra', 'Langsa', '1989-04-09', 'L', 'Jalan Rajabasa No. 101', '1173', 2, '2026-08-20 03:00:00'),
('1173030101010022', '1173030101010021', 'Anita Maharani', 'Langsa', '1992-02-15', 'P', 'Jalan Rajabasa No. 101', '1173', 1, '2026-08-20 03:00:00'),
('1173030102010023', '1173030102010023', 'Zainal Abidin', 'Langsa', '1980-09-27', 'L', 'Jalan Pante Kulu No. 202', '1173', 3, '2026-08-20 03:00:00'),
('1173030102010024', '1173030102010023', 'Ratna Dewi', 'Langsa', '1994-08-12', 'P', 'Jalan Pante Kulu No. 202', '1173', 2, '2026-08-20 03:00:00'),
('1173040101010025', '1173040101010025', 'Hendri Wijaya', 'Lhokseumawe', '1988-01-30', 'L', 'Jalan Alue Naga No. 213', '1174', 2, '2026-08-20 03:00:00'),
('1173040101010026', '1173040101010025', 'Joni Tarpada', 'Lhokseumawe', '1995-11-08', 'L', 'Jalan Alue Naga No. 213', '1174', 1, '2026-08-20 03:00:00'),
('1173040102010027', '1173040102010027', 'Karina Amelia', 'Lhokseumawe', '1991-07-25', 'P', 'Jalan Deah Raya No. 224', '1174', 2, '2026-08-20 03:00:00'),
('1173040102010028', '1173040102010027', 'Bambang Sutrisno', 'Aceh Besar', '1983-05-19', 'L', 'Jalan Deah Raya No. 224', '1174', 3, '2026-08-20 03:00:00'),
('1173040103010029', '1173040103010029', 'Susi Susanti', 'Lhokseumawe', '1990-10-03', 'P', 'Jalan Gompong No. 235', '1174', 1, '2026-08-20 03:00:00'),
('1173040103010030', '1173040103010029', 'Toto Suryanto', 'Aceh Besar', '1986-12-14', 'L', 'Jalan Gompong No. 235', '1174', 2, '2026-08-20 03:00:00'),
('1173050101010031', '1173050101010031', 'Rahmat Fauzi', 'Aceh Barat', '1981-03-22', 'L', 'Jalan Batoh No. 246', '1175', 2, '2026-08-20 03:00:00'),
('1173050101010032', '1173050101010031', 'Lina Marlina', 'Aceh Barat', '1985-08-10', 'P', 'Jalan Batoh No. 246', '1175', 1, '2026-08-20 03:00:00'),
('1173050102010033', '1173050102010033', 'Syaiful Rahman', 'Aceh Barat', '1992-04-07', 'L', 'Jalan Pulo Aceh No. 257', '1175', 1, '2026-08-20 03:00:00'),
('1173050102010034', '1173050102010033', 'Rina Kartini', 'Meulaboh', '1988-09-18', 'P', 'Jalan Pulo Aceh No. 257', '1175', 2, '2026-08-20 03:00:00'),
('1173050201010035', '1173050201010035', 'Juanda Gunawan', 'Aceh Barat', '1984-11-25', 'L', 'Jalan Sabang Kota No. 268', '1175', 3, '2026-08-20 03:00:00'),
('1173050201010036', '1173050201010035', 'Ayu Permata', 'Meulaboh', '1996-01-29', 'P', 'Jalan Sabang Kota No. 268', '1175', 4, '2026-08-20 03:00:00'),
('1173050202010037', '1173050202010037', 'Danang Permadi', 'Aceh Barat', '1989-07-11', 'L', 'Jalan Iboih No. 279', '1175', 2, '2026-08-20 03:00:00'),
('1173050202010038', '1173050202010037', 'Neneng Suryani', 'Aceh Barat', '1993-05-08', 'P', 'Jalan Iboih No. 279', '1175', 1, '2026-08-20 03:00:00'),
('1173050301010039', '1173050301010039', 'Ahmad Zainudin', 'Aceh Barat Daya', '1982-02-14', 'L', 'Jalan Teupin Layeu No. 280', '1175', 3, '2026-08-20 03:00:00'),
('1173050301010040', '1173050301010039', 'Masniyah Said', 'Aceh Barat Daya', '1987-06-20', 'P', 'Jalan Teupin Layeu No. 280', '1175', 2, '2026-08-20 03:00:00'),
('1173070101010041', '1173070101010041', 'Suryadi Gunawan', 'Aceh Besar', '1980-10-09', 'L', 'Jalan Blang Jurong No. 291', '1177', 2, '2026-08-20 03:00:00'),
('1173070101010042', '1173070101010041', 'Fitri Wahyuni', 'Aceh Besar', '1994-03-17', 'P', 'Jalan Blang Jurong No. 291', '1177', 1, '2026-08-20 03:00:00'),
('1173070102010043', '1173070102010043', 'Hari Prabowo', 'Aceh Besar', '1986-12-28', 'L', 'Jalan Arun Lama No. 302', '1177', 3, '2026-08-20 03:00:00'),
('1173070102010044', '1173070102010043', 'Putri Maharini', 'Aceh Besar', '1991-08-05', 'P', 'Jalan Arun Lama No. 302', '1177', 2, '2026-08-20 03:00:00'),
('1173070103010045', '1173070103010045', 'Andi Wijaya', 'Aceh Besar', '1988-04-19', 'L', 'Jalan Langsa Lama No. 313', '1177', 2, '2026-08-20 03:00:00'),
('1173070103010046', '1173070103010045', 'Hilda Kusuma', 'Aceh Besar', '1995-09-14', 'P', 'Jalan Langsa Lama No. 313', '1177', 1, '2026-08-20 03:00:00'),
('1173070104010047', '1173070104010047', 'Sumardi Santoso', 'Aceh Besar', '1983-07-22', 'L', 'Jalan Giok No. 324', '1177', 4, '2026-08-20 03:00:00'),
('1173070104010048', '1173070104010047', 'Soraya Amelia', 'Aceh Besar', '1993-01-10', 'P', 'Jalan Giok No. 324', '1177', 2, '2026-08-20 03:00:00'),
('1173070201010049', '1173070201010049', 'Didik Rahmat', 'Aceh Besar', '1987-11-03', 'L', 'Jalan Muara Batu No. 335', '1177', 1, '2026-08-20 03:00:00'),
('1173070201010050', '1173070201010049', 'Maya Kusuma', 'Aceh Besar', '1990-05-27', 'P', 'Jalan Muara Batu No. 335', '1177', 2, '2026-08-20 03:00:00'),
('1173070202010051', '1173070202010051', 'Rudi Hartono', 'Aceh Besar', '1981-08-13', 'L', 'Jalan Cot Mangga No. 346', '1177', 3, '2026-08-20 03:00:00'),
('1173070202010052', '1173070202010051', 'Indah Lestari', 'Aceh Besar', '1989-02-21', 'P', 'Jalan Cot Mangga No. 346', '1177', 1, '2026-08-20 03:00:00'),
('1173070301010053', '1173070301010053', 'Tri Hartanto', 'Aceh Besar', '1992-06-30', 'L', 'Jalan Muara Dua No. 357', '1177', 4, '2026-08-20 03:00:00'),
('1173070301010054', '1173070301010053', 'Dewi Puspita', 'Aceh Besar', '1986-09-08', 'P', 'Jalan Muara Dua No. 357', '1177', 2, '2026-08-20 03:00:00'),
('1173070302010055', '1173070302010055', 'Eka Prasetya', 'Aceh Besar', '1984-04-15', 'L', 'Jalan Kuala Marah No. 368', '1177', 1, '2026-08-20 03:00:00'),
('1173070302010056', '1173070302010055', 'Vivian Handoko', 'Aceh Besar', '1995-10-02', 'P', 'Jalan Kuala Marah No. 368', '1177', 2, '2026-08-20 03:00:00'),
('1173070401010057', '1173070401010057', 'Budi Hermanto', 'Aceh Besar', '1988-07-19', 'L', 'Jalan Blang Mangat No. 379', '1177', 3, '2026-08-20 03:00:00'),
('1173070401010058', '1173070401010057', 'Suri Sumardjo', 'Aceh Besar', '1993-12-11', 'P', 'Jalan Blang Mangat No. 379', '1177', 1, '2026-08-20 03:00:00'),
('1173070402010059', '1173070402010059', 'Gunawan Santoso', 'Aceh Besar', '1979-05-24', 'L', 'Jalan Pante Bidok No. 380', '1177', 2, '2026-08-20 03:00:00'),
('1173070402010060', '1173070402010059', 'Titik Wijaya', 'Aceh Besar', '1987-11-09', 'P', 'Jalan Pante Bidok No. 380', '1177', 4, '2026-08-20 03:00:00'),
('1173080101010061', '1173080101010061', 'Joko Setiawan', 'Aceh Jaya', '1985-03-26', 'L', 'Jalan Meulaboh No. 391', '1178', 2, '2026-08-20 03:00:00'),
('1173080101010062', '1173080101010061', 'Wulan Kurnia', 'Aceh Jaya', '1991-08-14', 'P', 'Jalan Meulaboh No. 391', '1178', 1, '2026-08-20 03:00:00'),
('1173080102010063', '1173080102010063', 'Adi Santoso', 'Aceh Jaya', '1988-01-07', 'L', 'Jalan Ujung Kalak No. 402', '1178', 3, '2026-08-20 03:00:00'),
('1173080102010064', '1173080102010063', 'Ninik Kusumawati', 'Aceh Jaya', '1994-09-22', 'P', 'Jalan Ujung Kalak No. 402', '1178', 2, '2026-08-20 03:00:00'),
('1173080201010065', '1173080201010065', 'Bambang Wijaksana', 'Aceh Jaya', '1982-10-17', 'L', 'Jalan Johan Pahlawan No. 413', '1178', 1, '2026-08-20 03:00:00'),
('1173080201010066', '1173080201010065', 'Lusi Suryanti', 'Aceh Jaya', '1990-04-29', 'P', 'Jalan Johan Pahlawan No. 413', '1178', 2, '2026-08-20 03:00:00'),
('1173080202010067', '1173080202010067', 'Santoso Wijayanto', 'Aceh Jaya', '1987-07-05', 'L', 'Jalan Saree No. 424', '1178', 3, '2026-08-20 03:00:00'),
('1173080202010068', '1173080202010067', 'Ulfah Rahmawati', 'Aceh Jaya', '1996-11-18', 'P', 'Jalan Saree No. 424', '1178', 1, '2026-08-20 03:00:00'),
('1173090101010069', '1173090101010069', 'Irawan Santoso', 'Aceh Selatan', '1983-12-08', 'L', 'Jalan Samatiga No. 435', '1179', 2, '2026-08-20 03:00:00'),
('1173090101010070', '1173090101010069', 'Rina Wijaksana', 'Aceh Selatan', '1989-05-13', 'P', 'Jalan Samatiga No. 435', '1179', 1, '2026-08-20 03:00:00'),
('1173090102010071', '1173090102010071', 'Muhammad Iksan', 'Aceh Selatan', '1986-09-19', 'L', 'Jalan Alue Ie No. 446', '1179', 3, '2026-08-20 03:00:00'),
('1173090102010072', '1173090102010071', 'Dwi Lestari', 'Aceh Selatan', '1992-02-27', 'P', 'Jalan Alue Ie No. 446', '1179', 2, '2026-08-20 03:00:00'),
('1173090201010073', '1173090201010073', 'Hendra Kusuma', 'Aceh Selatan', '1980-11-04', 'L', 'Jalan Arongan No. 457', '1179', 1, '2026-08-20 03:00:00'),
('1173090201010074', '1173090201010073', 'Sinta Wijaya', 'Aceh Selatan', '1991-06-16', 'P', 'Jalan Arongan No. 457', '1179', 2, '2026-08-20 03:00:00'),
('1173090202010075', '1173090202010075', 'Yuli Setiawan', 'Aceh Selatan', '1984-08-22', 'L', 'Jalan Lambalek No. 468', '1179', 3, '2026-08-20 03:00:00'),
('1173090202010076', '1173090202010075', 'Rima Hartono', 'Aceh Selatan', '1995-03-09', 'P', 'Jalan Lambalek No. 468', '1179', 1, '2026-08-20 03:00:00'),
('1173100101010077', '1173100101010077', 'Iwan Suryanto', 'Aceh Singkil', '1988-10-14', 'L', 'Jalan Bubon No. 479', '11710', 2, '2026-08-20 03:00:00'),
('1173100101010078', '1173100101010077', 'Anis Kusuma', 'Aceh Singkil', '1993-04-26', 'P', 'Jalan Bubon No. 479', '11710', 1, '2026-08-20 03:00:00'),
('1173100102010079', '1173100102010079', 'Taufik Rahman', 'Aceh Singkil', '1981-07-11', 'L', 'Jalan Pante Tutue No. 480', '11710', 3, '2026-08-20 03:00:00'),
('1173100102010080', '1173100102010079', 'Yasmin Suwardi', 'Aceh Singkil', '1989-12-03', 'P', 'Jalan Pante Tutue No. 480', '11710', 2, '2026-08-20 03:00:00'),
('1173110101010081', '1173110101010081', 'Wahyu Hermanto', 'Aceh Tamiang', '1985-02-19', 'L', 'Jalan Pantai Cerah No. 491', '11711', 2, '2026-08-20 03:00:00'),
('1173110101010082', '1173110101010081', 'Siti Nurjannah', 'Aceh Tamiang', '1991-08-30', 'P', 'Jalan Pantai Cerah No. 491', '11711', 1, '2026-08-20 03:00:00'),
('1173110102010083', '1173110102010083', 'Rizki Adiputra', 'Aceh Tamiang', '1987-06-25', 'L', 'Jalan Kuala Merah No. 502', '11711', 3, '2026-08-20 03:00:00'),
('1173110102010084', '1173110102010083', 'Meilina Wijaya', 'Aceh Tamiang', '1994-01-08', 'P', 'Jalan Kuala Merah No. 502', '11711', 2, '2026-08-20 03:00:00'),
('1173120101010085', '1173120101010085', 'Syamsu Zaman', 'Aceh Tengah', '1982-09-12', 'L', 'Jalan Lhoknga No. 513', '11712', 1, '2026-08-20 03:00:00'),
('1173120101010086', '1173120101010085', 'Yulia Purnama', 'Aceh Tengah', '1988-04-21', 'P', 'Jalan Lhoknga No. 513', '11712', 2, '2026-08-20 03:00:00'),
('1173120102010087', '1173120102010087', 'Fajar Gunawan', 'Aceh Tengah', '1990-10-05', 'L', 'Jalan Beutong No. 524', '11712', 3, '2026-08-20 03:00:00'),
('1173120102010088', '1173120102010087', 'Eka Sundari', 'Aceh Tengah', '1996-05-15', 'P', 'Jalan Beutong No. 524', '11712', 1, '2026-08-20 03:00:00'),
('1173130101010089', '1173130101010089', 'Marto Wijaksana', 'Aceh Tenggara', '1983-11-28', 'L', 'Jalan Leubak Bata No. 535', '11713', 2, '2026-08-20 03:00:00'),
('1173130101010090', '1173130101010089', 'Isna Wijaya', 'Aceh Tenggara', '1992-07-14', 'P', 'Jalan Leubak Bata No. 535', '11713', 1, '2026-08-20 03:00:00'),
('1173130102010091', '1173130102010091', 'Hendra Santoso', 'Aceh Tenggara', '1986-03-02', 'L', 'Jalan Meulaboh Jaya No. 546', '11713', 3, '2026-08-20 03:00:00'),
('1173130102010092', '1173130102010091', 'Ratna Kumala', 'Aceh Tenggara', '1989-09-24', 'P', 'Jalan Meulaboh Jaya No. 546', '11713', 2, '2026-08-20 03:00:00');

-- --------------------------------------------------------

--
-- Struktur dari tabel `penyaluran_bansos`
--

CREATE TABLE `penyaluran_bansos` (
  `id_penyaluran` int(11) NOT NULL,
  `id_program` int(11) NOT NULL,
  `nik` char(16) NOT NULL,
  `periode_tahun` year(4) NOT NULL,
  `periode_tahap` varchar(50) NOT NULL,
  `status_penyaluran` enum('Pending','Disalurkan','Gagal','Valid') DEFAULT 'Pending',
  `nominal_atau_bentuk` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `penyaluran_bansos`
--

INSERT INTO `penyaluran_bansos` (`id_penyaluran`, `id_program`, `nik`, `periode_tahun`, `periode_tahap`, `status_penyaluran`, `nominal_atau_bentuk`) VALUES
(1, 1, '1173010101010001', '2025', 'Tahap 1 (Jan-Mar)', 'Disalurkan', 'Rp 750.000'),
(2, 2, '1173010101010002', '2025', 'Tahap 1 (Jan-Mar)', 'Disalurkan', 'Beras 10 Kg & Sembako'),
(3, 1, '1173010101010003', '2025', 'Tahap 2 (Apr-Jun)', 'Pending', 'Rp 750.000'),
(4, 4, '1173010101010004', '2025', 'Tahap 2 (Apr-Jun)', 'Disalurkan', 'Alat Bantu Mobilitas'),
(5, 2, '1173010102010005', '2025', 'Tahap 3 (Jul-Sep)', 'Disalurkan', 'Paket Sembako'),
(6, 3, '1173010102010006', '2025', 'Tahap 3 (Jul-Sep)', 'Valid', 'Paket Logistik Bencana'),
(7, 1, '1173010102010007', '2025', 'Tahap 4 (Okt-Des)', 'Gagal', 'Rp 750.000'),
(8, 2, '1173010102010008', '2025', 'Tahap 4 (Okt-Des)', 'Disalurkan', 'Beras 10 Kg'),
(9, 1, '1173010103010009', '2025', 'Tahap 1 (Jan-Mar)', 'Disalurkan', 'Rp 600.000'),
(10, 4, '1173010103010010', '2025', 'Tahap 2 (Apr-Jun)', 'Pending', 'Kursi Roda'),
(11, 2, '1173010104010011', '2025', 'Tahap 3 (Jul-Sep)', 'Disalurkan', 'Sembako'),
(12, 1, '1173010104010012', '2025', 'Tahap 4 (Okt-Des)', '', 'Rp 750.000'),
(13, 2, '1173010105010013', '2025', 'Tahap 1 (Jan-Mar)', 'Disalurkan', 'Beras 10 Kg & Sembako'),
(14, 1, '1173010105010014', '2025', 'Tahap 2 (Apr-Jun)', 'Disalurkan', 'Rp 500.000'),
(15, 4, '1173010106010015', '2025', 'Tahap 3 (Jul-Sep)', 'Valid', 'Alat Bantu Dengar'),
(16, 2, '1173010106010016', '2025', 'Tahap 4 (Okt-Des)', 'Pending', 'Paket Sembako'),
(17, 1, '1173020101010017', '2025', 'Tahap 1 (Jan-Mar)', 'Disalurkan', 'Rp 750.000'),
(18, 3, '1173020101010018', '2025', 'Darurat Bencana', 'Valid', 'Paket Logistik Darurat'),
(19, 2, '1173020102010019', '2025', 'Tahap 2 (Apr-Jun)', 'Disalurkan', 'Beras 10 Kg'),
(20, 1, '1173020102010020', '2025', 'Tahap 3 (Jul-Sep)', 'Gagal', 'Rp 600.000'),
(21, 1, '1173030101010021', '2026', 'Tahap 1 (Jan-Mar)', 'Disalurkan', 'Rp 750.000'),
(22, 2, '1173030101010022', '2026', 'Tahap 1 (Jan-Mar)', 'Disalurkan', 'Beras 10 Kg & Sembako'),
(23, 1, '1173030102010023', '2026', 'Tahap 2 (Apr-Jun)', 'Pending', 'Rp 750.000'),
(24, 3, '1173030102010024', '2026', 'Darurat Bencana', 'Valid', 'Paket Logistik'),
(25, 4, '1173040101010025', '2026', 'Tahap 2 (Apr-Jun)', 'Disalurkan', 'Alat Bantu Disabilitas'),
(26, 1, '1173040101010026', '2026', 'Tahap 3 (Jul-Sep)', 'Disalurkan', 'Rp 750.000'),
(27, 2, '1173040102010027', '2026', 'Tahap 3 (Jul-Sep)', '', 'Paket Sembako'),
(28, 1, '1173040102010028', '2026', 'Tahap 4 (Okt-Des)', 'Pending', 'Rp 600.000'),
(29, 2, '1173040103010029', '2026', 'Tahap 4 (Okt-Des)', 'Disalurkan', 'Beras 10 Kg'),
(30, 4, '1173040103010030', '2026', 'Tahap 1 (Jan-Mar)', 'Valid', 'Alat Bantu Sosial'),
(31, 1, '1173050101010031', '2026', 'Tahap 1 (Jan-Mar)', 'Disalurkan', 'Rp 750.000'),
(32, 2, '1173050101010032', '2026', 'Tahap 2 (Apr-Jun)', 'Disalurkan', 'Sembako'),
(33, 3, '1173050102010033', '2026', 'Darurat Bencana', 'Valid', 'Paket Logistik Darurat'),
(34, 1, '1173050102010034', '2026', 'Tahap 3 (Jul-Sep)', 'Gagal', 'Rp 500.000'),
(35, 2, '1173050201010035', '2026', 'Tahap 4 (Okt-Des)', 'Disalurkan', 'Beras 10 Kg & Sembako'),
(36, 4, '1173050201010036', '2026', 'Tahap 2 (Apr-Jun)', 'Pending', 'Alat Bantu Mobilitas'),
(37, 1, '1173070101010041', '2026', 'Tahap 1 (Jan-Mar)', 'Disalurkan', 'Rp 750.000'),
(38, 2, '1173070101010042', '2026', 'Tahap 3 (Jul-Sep)', 'Disalurkan', 'Paket Sembako'),
(39, 3, '1173070102010043', '2026', 'Darurat Bencana', 'Valid', 'Paket Logistik'),
(40, 4, '1173070102010044', '2026', 'Tahap 4 (Okt-Des)', '', 'Kursi Roda');

-- --------------------------------------------------------

--
-- Struktur dari tabel `ppks`
--

CREATE TABLE `ppks` (
  `id_ppks` int(11) NOT NULL,
  `nik` char(16) NOT NULL,
  `kategori_ppks` enum('Fakir Miskin','Penyandang Disabilitas','Lanjut Usia Terlantar','Anak Terlantar','Anak Berhadapan Hukum','Korban Kekerasan','Korban Bencana','Lainnya') NOT NULL,
  `derajat_keparahan` varchar(50) DEFAULT NULL,
  `tanggal_terdata` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `ppks`
--

INSERT INTO `ppks` (`id_ppks`, `nik`, `kategori_ppks`, `derajat_keparahan`, `tanggal_terdata`) VALUES
(1, '1173010101010001', 'Fakir Miskin', 'Sedang', '2026-01-05'),
(2, '1173010102010005', 'Lanjut Usia Terlantar', 'Ringan', '2026-01-08'),
(3, '1173010103010009', 'Penyandang Disabilitas', 'Berat', '2026-01-12'),
(4, '1173010105010013', 'Anak Terlantar', 'Sedang', '2026-01-18'),
(5, '1173010106010015', 'Fakir Miskin', 'Ringan', '2026-01-22'),
(6, '1173020101010017', 'Korban Bencana', 'Berat', '2026-02-01'),
(7, '1173020102010019', 'Fakir Miskin', 'Sedang', '2026-02-04'),
(8, '1173030101010021', 'Lanjut Usia Terlantar', 'Berat', '2026-02-10'),
(9, '1173030102010023', 'Fakir Miskin', 'Ringan', '2026-02-14'),
(10, '1173040101010025', 'Penyandang Disabilitas', 'Sedang', '2026-02-18'),
(11, '1173040103010029', 'Fakir Miskin', 'Berat', '2026-02-22'),
(12, '1173050101010031', 'Fakir Miskin', 'Sedang', '2026-02-28'),
(13, '1173050102010033', 'Anak Terlantar', 'Ringan', '2026-03-04'),
(14, '1173050201010035', 'Korban Bencana', 'Berat', '2026-03-08'),
(15, '1173050202010037', 'Fakir Miskin', 'Sedang', '2026-03-12'),
(16, '1173070101010041', 'Lanjut Usia Terlantar', 'Berat', '2026-03-18'),
(17, '1173070103010045', 'Penyandang Disabilitas', 'Sedang', '2026-03-22'),
(18, '1173070201010049', 'Fakir Miskin', 'Ringan', '2026-03-25'),
(19, '1173070301010053', 'Anak Terlantar', 'Berat', '2026-03-28'),
(20, '1173070401010057', 'Fakir Miskin', 'Sedang', '2026-04-02'),
(21, '1173080101010061', 'Korban Bencana', 'Ringan', '2026-04-06'),
(22, '1173080201010065', 'Penyandang Disabilitas', 'Berat', '2026-04-12'),
(23, '1173090101010069', 'Fakir Miskin', 'Sedang', '2026-04-16'),
(24, '1173090201010073', 'Lanjut Usia Terlantar', 'Berat', '2026-04-20'),
(25, '1173100101010077', 'Fakir Miskin', 'Ringan', '2026-04-25'),
(26, '1173110101010081', 'Korban Bencana', 'Sedang', '2026-05-01'),
(27, '1173120101010085', 'Fakir Miskin', 'Berat', '2026-05-05'),
(28, '1173120102010087', 'Anak Terlantar', 'Sedang', '2026-05-10'),
(29, '1173130101010089', 'Penyandang Disabilitas', 'Berat', '2026-05-15'),
(30, '1173130102010091', 'Fakir Miskin', 'Ringan', '2026-05-20');

-- --------------------------------------------------------

--
-- Struktur dari tabel `program_bansos`
--

CREATE TABLE `program_bansos` (
  `id_program` int(11) NOT NULL,
  `nama_program` varchar(100) NOT NULL,
  `kriteria_penerima` text DEFAULT NULL,
  `anggaran_tahun` year(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `program_bansos`
--

INSERT INTO `program_bansos` (`id_program`, `nama_program`, `kriteria_penerima`, `anggaran_tahun`) VALUES
(1, 'Program Keluarga Harapan (PKH)', 'Keluarga miskin dengan ibu hamil, anak sekolah, penyandang disabilitas atau lansia.', '2026'),
(2, 'Bantuan Pangan Non Tunai (BPNT)', 'Keluarga dengan tingkat kesejahteraan desil 1 sampai 4.', '2026'),
(3, 'Bantuan Sosial Tunai (BST)', 'Masyarakat terdampak bencana alam atau bencana sosial.', '2026'),
(4, 'Asistensi Rehabilitasi Sosial (ATENSI)', 'Penyandang disabilitas, anak terlantar dan kelompok rentan.', '2026');

-- --------------------------------------------------------

--
-- Struktur dari tabel `psks`
--

CREATE TABLE `psks` (
  `id_psks` int(11) NOT NULL,
  `nama_sumber` varchar(150) NOT NULL,
  `jenis_psks` enum('TKSK','Tagana','Peksos','Karang Taruna','LKS / Panti Sosial') NOT NULL,
  `id_wilayah` char(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `psks`
--

INSERT INTO `psks` (`id_psks`, `nama_sumber`, `jenis_psks`, `id_wilayah`) VALUES
(1, 'Karang Taruna Kota Banda Aceh', 'Karang Taruna', '1171'),
(2, 'Tagana Kota Banda Aceh', 'Tagana', '1171'),
(3, 'TKSK Kota Banda Aceh', 'TKSK', '1171'),
(4, 'LKS Kasih Ibu Banda Aceh', 'LKS / Panti Sosial', '1171'),
(5, 'Karang Taruna Kota Sabang', 'Karang Taruna', '1172'),
(6, 'Tagana Kota Sabang', 'Tagana', '1172'),
(7, 'Karang Taruna Kota Langsa', 'Karang Taruna', '1173'),
(8, 'TKSK Kota Langsa', 'TKSK', '1173'),
(9, 'Karang Taruna Kota Lhokseumawe', 'Karang Taruna', '1174'),
(10, 'Tagana Kota Lhokseumawe', 'Tagana', '1174'),
(11, 'Karang Taruna Aceh Barat', 'Karang Taruna', '1175'),
(12, 'TKSK Aceh Besar', 'TKSK', '1177'),
(13, 'LKS Aceh Jaya', 'LKS / Panti Sosial', '1178'),
(14, 'TKSK Aceh Selatan', 'TKSK', '1179');

-- --------------------------------------------------------

--
-- Struktur dari tabel `rumah_tangga`
--

CREATE TABLE `rumah_tangga` (
  `id_rt` varchar(30) NOT NULL,
  `no_kk` char(16) NOT NULL,
  `kepala_keluarga_nik` char(16) NOT NULL,
  `kondisi_rumah` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`kondisi_rumah`)),
  `score_kelayakan` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `rumah_tangga`
--

INSERT INTO `rumah_tangga` (`id_rt`, `no_kk`, `kepala_keluarga_nik`, `kondisi_rumah`, `score_kelayakan`) VALUES
('RT-001', '1173010101010001', '1173010101010001', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 87.50),
('RT-002', '1173010101010003', '1173010101010003', '{\"dinding\":\"tembok\",\"lantai\":\"plester\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 74.30),
('RT-003', '1173010102010005', '1173010102010005', '{\"dinding\":\"kayu\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 59.80),
('RT-004', '1173010102010007', '1173010102010007', '{\"dinding\":\"kayu\",\"lantai\":\"tanah\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"menumpang\"}', 43.20),
('RT-005', '1173010103010009', '1173010103010009', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 90.10),
('RT-006', '1173010104010011', '1173010104010011', '{\"dinding\":\"tembok\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 62.40),
('RT-007', '1173010105010013', '1173010105010013', '{\"dinding\":\"kayu\",\"lantai\":\"tanah\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"menumpang\"}', 46.80),
('RT-008', '1173010106010015', '1173010106010015', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 83.70),
('RT-009', '1173020101010017', '1173020101010017', '{\"dinding\":\"bambu\",\"lantai\":\"tanah\",\"atap\":\"seng_rusak\",\"listrik\":\"tidak_ada\",\"kepemilikan_rumah\":\"sewa\"}', 27.40),
('RT-010', '1173020102010019', '1173020102010019', '{\"dinding\":\"kayu\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 56.20),
('RT-011', '1173030101010021', '1173030101010021', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 91.20),
('RT-012', '1173030102010023', '1173030102010023', '{\"dinding\":\"kayu\",\"lantai\":\"tanah\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"menumpang\"}', 41.50),
('RT-013', '1173040101010025', '1173040101010025', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 85.80),
('RT-014', '1173040102010027', '1173040102010027', '{\"dinding\":\"tembok\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 64.20),
('RT-015', '1173040103010029', '1173040103010029', '{\"dinding\":\"bambu\",\"lantai\":\"tanah\",\"atap\":\"seng_rusak\",\"listrik\":\"tidak_ada\",\"kepemilikan_rumah\":\"sewa\"}', 26.30),
('RT-016', '1173050101010031', '1173050101010031', '{\"dinding\":\"kayu\",\"lantai\":\"tanah\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"menumpang\"}', 44.80),
('RT-017', '1173050102010033', '1173050102010033', '{\"dinding\":\"tembok\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 61.40),
('RT-018', '1173050201010035', '1173050201010035', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 84.60),
('RT-019', '1173050202010037', '1173050202010037', '{\"dinding\":\"kayu\",\"lantai\":\"tanah\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"menumpang\"}', 39.70),
('RT-020', '1173050301010039', '1173050301010039', '{\"dinding\":\"bambu\",\"lantai\":\"tanah\",\"atap\":\"seng_rusak\",\"listrik\":\"tidak_ada\",\"kepemilikan_rumah\":\"sewa\"}', 24.90),
('RT-021', '1173070101010041', '1173070101010041', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 89.40),
('RT-022', '1173070102010043', '1173070102010043', '{\"dinding\":\"tembok\",\"lantai\":\"plester\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 78.20),
('RT-023', '1173070103010045', '1173070103010045', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 86.70),
('RT-024', '1173070104010047', '1173070104010047', '{\"dinding\":\"kayu\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 68.40),
('RT-025', '1173070201010049', '1173070201010049', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 88.80),
('RT-026', '1173070202010051', '1173070202010051', '{\"dinding\":\"kayu\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 63.60),
('RT-027', '1173070301010053', '1173070301010053', '{\"dinding\":\"kayu\",\"lantai\":\"tanah\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"menumpang\"}', 48.50),
('RT-028', '1173070302010055', '1173070302010055', '{\"dinding\":\"tembok\",\"lantai\":\"plester\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 76.30),
('RT-029', '1173070401010057', '1173070401010057', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 84.90),
('RT-030', '1173070402010059', '1173070402010059', '{\"dinding\":\"kayu\",\"lantai\":\"tanah\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 52.10),
('RT-031', '1173080101010061', '1173080101010061', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 80.50),
('RT-032', '1173080102010063', '1173080102010063', '{\"dinding\":\"kayu\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 61.80),
('RT-033', '1173080201010065', '1173080201010065', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 83.10),
('RT-034', '1173080202010067', '1173080202010067', '{\"dinding\":\"kayu\",\"lantai\":\"tanah\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"menumpang\"}', 44.20),
('RT-035', '1173090101010069', '1173090101010069', '{\"dinding\":\"tembok\",\"lantai\":\"plester\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 73.60),
('RT-036', '1173090102010071', '1173090102010071', '{\"dinding\":\"kayu\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 57.80),
('RT-037', '1173090201010073', '1173090201010073', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 81.90),
('RT-038', '1173090202010075', '1173090202010075', '{\"dinding\":\"kayu\",\"lantai\":\"tanah\",\"atap\":\"seng_rusak\",\"listrik\":\"tidak_ada\",\"kepemilikan_rumah\":\"sewa\"}', 31.60),
('RT-039', '1173100101010077', '1173100101010077', '{\"dinding\":\"tembok\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 63.20),
('RT-040', '1173100102010079', '1173100102010079', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 79.80),
('RT-041', '1173110101010081', '1173110101010081', '{\"dinding\":\"kayu\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 54.70),
('RT-042', '1173110102010083', '1173110102010083', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 82.60),
('RT-043', '1173120101010085', '1173120101010085', '{\"dinding\":\"tembok\",\"lantai\":\"plester\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 77.40),
('RT-044', '1173120102010087', '1173120102010087', '{\"dinding\":\"kayu\",\"lantai\":\"tanah\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"menumpang\"}', 47.80),
('RT-045', '1173130101010089', '1173130101010089', '{\"dinding\":\"tembok\",\"lantai\":\"keramik\",\"atap\":\"genteng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"milik_sendiri\"}', 86.10),
('RT-046', '1173130102010091', '1173130102010091', '{\"dinding\":\"tembok\",\"lantai\":\"plester\",\"atap\":\"seng\",\"listrik\":\"ada\",\"kepemilikan_rumah\":\"sewa\"}', 66.30);

-- --------------------------------------------------------

--
-- Struktur dari tabel `wilayah`
--

CREATE TABLE `wilayah` (
  `id_wilayah` char(10) NOT NULL,
  `nama_wilayah` varchar(100) NOT NULL,
  `level_wilayah` enum('Provinsi','Kabupaten/Kota','Kecamatan','Kelurahan/Desa') NOT NULL,
  `parent_id` char(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `wilayah`
--

INSERT INTO `wilayah` (`id_wilayah`, `nama_wilayah`, `level_wilayah`, `parent_id`) VALUES
('1171', 'Kota Banda Aceh', 'Kabupaten/Kota', NULL),
('11710', 'Kabupaten Aceh Singkil', 'Kabupaten/Kota', NULL),
('11711', 'Kabupaten Aceh Tamiang', 'Kabupaten/Kota', NULL),
('11712', 'Kabupaten Aceh Tengah', 'Kabupaten/Kota', NULL),
('11713', 'Kabupaten Aceh Tenggara', 'Kabupaten/Kota', NULL),
('1172', 'Kota Sabang', 'Kabupaten/Kota', NULL),
('1173', 'Kota Langsa', 'Kabupaten/Kota', NULL),
('1174', 'Kota Lhokseumawe', 'Kabupaten/Kota', NULL),
('1175', 'Kabupaten Aceh Barat', 'Kabupaten/Kota', NULL),
('1177', 'Kabupaten Aceh Besar', 'Kabupaten/Kota', NULL),
('1178', 'Kabupaten Aceh Jaya', 'Kabupaten/Kota', NULL),
('1179', 'Kabupaten Aceh Selatan', 'Kabupaten/Kota', NULL);

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `penduduk`
--
ALTER TABLE `penduduk`
  ADD PRIMARY KEY (`nik`),
  ADD KEY `fk_penduduk_wilayah` (`id_wilayah`);

--
-- Indeks untuk tabel `penyaluran_bansos`
--
ALTER TABLE `penyaluran_bansos`
  ADD PRIMARY KEY (`id_penyaluran`),
  ADD KEY `fk_penyaluran_program` (`id_program`),
  ADD KEY `fk_penyaluran_penduduk` (`nik`);

--
-- Indeks untuk tabel `ppks`
--
ALTER TABLE `ppks`
  ADD PRIMARY KEY (`id_ppks`),
  ADD KEY `fk_ppks_penduduk` (`nik`);

--
-- Indeks untuk tabel `program_bansos`
--
ALTER TABLE `program_bansos`
  ADD PRIMARY KEY (`id_program`);

--
-- Indeks untuk tabel `psks`
--
ALTER TABLE `psks`
  ADD PRIMARY KEY (`id_psks`),
  ADD KEY `fk_psks_wilayah` (`id_wilayah`);

--
-- Indeks untuk tabel `rumah_tangga`
--
ALTER TABLE `rumah_tangga`
  ADD PRIMARY KEY (`id_rt`),
  ADD KEY `fk_rt_kepala` (`kepala_keluarga_nik`);

--
-- Indeks untuk tabel `wilayah`
--
ALTER TABLE `wilayah`
  ADD PRIMARY KEY (`id_wilayah`),
  ADD KEY `fk_wilayah_parent` (`parent_id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `penyaluran_bansos`
--
ALTER TABLE `penyaluran_bansos`
  MODIFY `id_penyaluran` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT untuk tabel `ppks`
--
ALTER TABLE `ppks`
  MODIFY `id_ppks` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT untuk tabel `program_bansos`
--
ALTER TABLE `program_bansos`
  MODIFY `id_program` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT untuk tabel `psks`
--
ALTER TABLE `psks`
  MODIFY `id_psks` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `penduduk`
--
ALTER TABLE `penduduk`
  ADD CONSTRAINT `fk_penduduk_wilayah` FOREIGN KEY (`id_wilayah`) REFERENCES `wilayah` (`id_wilayah`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `penyaluran_bansos`
--
ALTER TABLE `penyaluran_bansos`
  ADD CONSTRAINT `fk_penyaluran_penduduk` FOREIGN KEY (`nik`) REFERENCES `penduduk` (`nik`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_penyaluran_program` FOREIGN KEY (`id_program`) REFERENCES `program_bansos` (`id_program`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `ppks`
--
ALTER TABLE `ppks`
  ADD CONSTRAINT `fk_ppks_penduduk` FOREIGN KEY (`nik`) REFERENCES `penduduk` (`nik`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `psks`
--
ALTER TABLE `psks`
  ADD CONSTRAINT `fk_psks_wilayah` FOREIGN KEY (`id_wilayah`) REFERENCES `wilayah` (`id_wilayah`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `rumah_tangga`
--
ALTER TABLE `rumah_tangga`
  ADD CONSTRAINT `fk_rt_kepala` FOREIGN KEY (`kepala_keluarga_nik`) REFERENCES `penduduk` (`nik`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `wilayah`
--
ALTER TABLE `wilayah`
  ADD CONSTRAINT `fk_wilayah_parent` FOREIGN KEY (`parent_id`) REFERENCES `wilayah` (`id_wilayah`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
