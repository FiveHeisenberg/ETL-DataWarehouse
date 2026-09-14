-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 09, 2026 at 08:05 AM
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
-- Database: `db_disnaker`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_kasus_hi`
--

CREATE TABLE `tb_kasus_hi` (
  `id_kasus` int NOT NULL,
  `nib_perusahaan` varchar(20) NOT NULL,
  `kategori_kasus` enum('PHK','Sengketa Gaji','Kecelakaan Kerja','Pelanggaran K3') NOT NULL,
  `deskripsi_kejadian` text NOT NULL,
  `tanggal_laporan` date NOT NULL,
  `status_penyelesaian` enum('Proses Mediasi','Selesai','Eskalasi Pengadilan') NOT NULL DEFAULT 'Proses Mediasi'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_kasus_hi`
--

INSERT INTO `tb_kasus_hi` (`id_kasus`, `nib_perusahaan`, `kategori_kasus`, `deskripsi_kejadian`, `tanggal_laporan`, `status_penyelesaian`) VALUES
(1, '6152433455667799', 'Sengketa Gaji', 'Pelanggaran jam kerja dan keterlambatan insentif kurir pada divisi pengantaran makanan.', '2026-07-10', 'Proses Mediasi'),
(2, '9120304050607080', 'Sengketa Gaji', 'Perselisihan kepemilikan paten algoritma Machine Learning yang dikembangkan oleh mantan karyawan.', '2026-07-15', 'Eskalasi Pengadilan'),
(3, '7162534455667788', 'Kecelakaan Kerja', 'Karyawan terpeleset akibat tumpahan UHT milk di area sterilisasi, menyebabkan cedera ringan.', '2026-07-22', 'Selesai'),
(4, '5142322455667700', 'PHK', 'Restrukturisasi departemen yang menyebabkan PHK pada 5 staf administrator server.', '2026-08-02', 'Selesai'),
(5, '3122100455667722', 'Pelanggaran K3', 'Insiden korsleting perangkat audio akibat minimnya standar keselamatan perangkat saat persiapan event.', '2026-08-05', 'Proses Mediasi'),
(6, '4132211455667711', 'Sengketa Gaji', 'Pembayaran pesangon yang tidak sesuai dengan ketentuan PKWT setelah masa kontrak habis.', '2026-08-08', 'Proses Mediasi'),
(7, '2112099455667733', 'Kecelakaan Kerja', 'Insiden kejatuhan material konstruksi di blok B, penanganan medis sudah ditanggung BPJS.', '2026-08-10', 'Selesai');

-- --------------------------------------------------------

--
-- Table structure for table `tb_lowongan`
--

CREATE TABLE `tb_lowongan` (
  `id_lowongan` int NOT NULL,
  `nib_perusahaan` varchar(20) NOT NULL,
  `posisi_jabatan` varchar(100) NOT NULL,
  `syarat_pendidikan` varchar(50) NOT NULL,
  `kuota_penerimaan` int NOT NULL,
  `tanggal_buka` date NOT NULL,
  `tanggal_tutup` date NOT NULL,
  `status_aktif` tinyint(1) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_lowongan`
--

INSERT INTO `tb_lowongan` (`id_lowongan`, `nib_perusahaan`, `posisi_jabatan`, `syarat_pendidikan`, `kuota_penerimaan`, `tanggal_buka`, `tanggal_tutup`, `status_aktif`) VALUES
(1, '9120304050607080', 'Computer Vision Engineer (Python/OpenCV)', 'S1', 2, '2026-08-01', '2026-09-01', 1),
(2, '9120304050607080', 'Machine Learning Researcher', 'S2', 1, '2026-08-05', '2026-09-05', 1),
(3, '8172635409182736', 'Hybrid Cloud Architect', 'S1', 2, '2026-08-10', '2026-09-10', 1),
(4, '8172635409182736', 'System Administrator', 'D3', 3, '2026-08-12', '2026-08-25', 1),
(5, '7162534455667788', 'Spesialis Produksi Greek Yoghurt', 'SMK/D3', 4, '2026-08-15', '2026-09-15', 1),
(6, '7162534455667788', 'Quality Control (UHT Milk)', 'S1', 1, '2026-08-15', '2026-09-15', 1),
(7, '6152433455667799', 'Backend Developer', 'S1', 5, '2026-08-20', '2026-09-20', 1),
(8, '6152433455667799', 'System Analyst (DFD Specialist)', 'S1', 2, '2026-08-20', '2026-09-20', 1),
(9, '5142322455667700', 'Windows Server 2022 Administrator', 'S1', 2, '2026-08-01', '2026-08-30', 1),
(10, '5142322455667700', 'PowerShell Automation Engineer', 'D3', 1, '2026-08-01', '2026-08-30', 1),
(11, '3122100455667722', 'Audio Mixer / Sound Engineer', 'SMK', 2, '2026-08-10', '2026-09-10', 1),
(12, '3122100455667722', 'Event Organizer / Promotor', 'S1', 3, '2026-08-10', '2026-09-10', 1),
(13, '2112099455667733', 'Pengawas Lapangan (HSE)', 'S1', 4, '2026-08-05', '2026-09-05', 1),
(14, '1101988455667744', 'Mandor Perkebunan', 'SMA', 10, '2026-08-01', '2026-08-31', 1),
(15, '0191877455667755', 'Perawat Gigi', 'D3', 2, '2026-08-15', '2026-09-15', 1);

-- --------------------------------------------------------

--
-- Table structure for table `tb_pelatihan_blk`
--

CREATE TABLE `tb_pelatihan_blk` (
  `id_pelatihan` int NOT NULL,
  `nama_program` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `jenis_kejuruan` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `kuota_peserta` int NOT NULL,
  `tanggal_pelaksanaan` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_pelatihan_blk`
--

INSERT INTO `tb_pelatihan_blk` (`id_pelatihan`, `nama_program`, `jenis_kejuruan`, `kuota_peserta`, `tanggal_pelaksanaan`) VALUES
(1, 'Bootcamp Computer Vision dengan Python', 'Teknologi Informasi', 20, '2026-09-10'),
(2, 'Manajemen Infrastruktur Cloud Komunitas', 'Teknologi Informasi', 25, '2026-09-15'),
(3, 'Teknik Fermentasi Yoghurt Skala UMKM', 'Tata Boga', 15, '2026-09-20'),
(4, 'Pemodelan Data Flow Diagram (DFD) & UML', 'Teknologi Informasi', 30, '2026-10-01'),
(5, 'Administrasi Server CLI (MailEnable & IIS)', 'Teknologi Informasi', 20, '2026-10-05'),
(6, 'K3 Konstruksi dan Alat Berat', 'Keselamatan Kerja', 40, '2026-10-15');

-- --------------------------------------------------------

--
-- Table structure for table `tb_penduduk_pencaker`
--

CREATE TABLE `tb_penduduk_pencaker` (
  `nik` varchar(16) NOT NULL,
  `nama_lengkap` varchar(35) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `jenis_kelamin` enum('L','P') NOT NULL,
  `tanggal_lahir` date NOT NULL,
  `pendidikan_terakhir` varchar(50) NOT NULL,
  `keahlian_utama` text,
  `status_bekerja` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_penduduk_pencaker`
--

INSERT INTO `tb_penduduk_pencaker` (`nik`, `nama_lengkap`, `jenis_kelamin`, `tanggal_lahir`, `pendidikan_terakhir`, `keahlian_utama`, `status_bekerja`) VALUES
('1171040104050076', 'Vidi Al', 'L', '2005-04-01', 'SMA', NULL, 0),
('1171040205060077', 'Wulan Guritno', 'P', '2006-05-02', 'S1', NULL, 0),
('1171040306070078', 'Yuni Shara', 'P', '2007-06-03', 'SMA', NULL, 0),
('1171040407080079', 'Jakia Adya Mecca', 'P', '2008-07-04', 'S1', NULL, 0),
('1171040508090080', 'Agnez Monica', 'P', '2009-08-05', 'SMA', NULL, 0),
('1171040609900081', 'Baim Wong', 'L', '1990-09-06', 'S1', NULL, 0),
('1171040710910082', 'Celsi Islan', 'P', '1991-10-07', 'SMA', NULL, 0),
('1171040811920083', 'Deddy karbujer', 'L', '1992-11-08', 'S2', NULL, 0),
('1171040912930084', 'Ernest Prakasa', 'L', '1993-12-09', 'S1', NULL, 0),
('1171041001940085', 'Fedi Nuril', 'L', '1994-01-10', 'SMA', NULL, 0),
('1171041102950086', 'Gading Martin', 'L', '1995-02-11', 'S1', NULL, 0),
('1171041203960087', 'Hesti Purwadinata', 'P', '1996-03-12', 'SMA', NULL, 0),
('1171041304970088', 'Iko Uwais', 'L', '1997-04-13', 'SMA', NULL, 0),
('1171041405980089', 'Jepri Nikol', 'L', '1998-05-14', 'SMA', NULL, 0),
('1171041506990090', 'Kiky Saputri', 'P', '1999-06-15', 'S1', NULL, 0),
('1171041607000091', 'Lukman Sardi', 'L', '2000-07-16', 'S1', NULL, 0),
('1171041708010092', 'Maudy Ayunda', 'P', '2001-08-17', 'S1', NULL, 0),
('1171041809020093', 'Nikolas Saputra', 'L', '2002-09-18', 'S1', NULL, 0),
('1171041910030094', 'Oka Antara', 'L', '2003-10-19', 'SMA', NULL, 0),
('1171042011040095', 'Pevita Pearce', 'P', '2004-11-20', 'SMA', NULL, 0),
('1171042112050096', 'Rio Dewanto', 'L', '2005-12-21', 'SMA', NULL, 0),
('1171042201060097', 'Sophia Latjuba', 'P', '2006-01-22', 'SMA', NULL, 0),
('1171042302070098', 'Tara Bakso', 'P', '2007-02-23', 'S1', NULL, 0),
('1171042403080099', 'Umay Shahab', 'L', '2008-03-24', 'SMA', NULL, 0),
('1171042504090100', 'Vino G. Bastian', 'L', '2009-04-25', 'S1', NULL, 0),
('1174020102950026', 'Fitriani', 'P', '1995-02-01', 'SMA', NULL, 0),
('1174020108050056', 'Aldi Tahe', 'L', '2005-08-01', 'S1', NULL, 0),
('1174020203960027', 'Andi Pratama', 'L', '1996-03-02', 'SMA', NULL, 0),
('1174020209060057', 'Bunga Citra', 'P', '2006-09-02', 'S1', NULL, 0),
('11740203000051', 'Vina Panduwinata', 'P', '2000-03-26', 'SMA', NULL, 0),
('1174020304970028', 'Yulia Citra', 'P', '1997-04-03', 'SMA', NULL, 0),
('1174020310070058', 'Candra Wijaya', 'L', '2007-10-03', 'SMA', NULL, 0),
('1174020405980029', 'Surya Dharma', 'L', '1998-05-04', 'S1', NULL, 0),
('1174020411080059', 'Dinda Kanya', 'P', '2008-11-04', 'SMA', NULL, 0),
('1174020506990030', 'Kiki Fatmala', 'P', '1999-06-05', 'SMA', NULL, 0),
('1174020512090060', 'Eza Gionino', 'L', '2009-12-05', 'SMA', NULL, 0),
('1174020601900061', 'Fathia Izzati', 'P', '1990-01-06', 'S1', NULL, 0),
('1174020607000031', 'Reza Pahlevi', 'L', '2000-07-06', 'S1', NULL, 0),
('1174020702910062', 'Gilang Dirga', 'L', '1991-02-07', 'SMA', NULL, 0),
('1174020708010032', 'Intan Nuraini', 'P', '2001-08-07', 'S1', NULL, 0),
('1174020803920063', 'Hesty Purwadinata', 'P', '1992-03-08', 'SMA', NULL, 0),
('1174020809020033', 'Doni Salman', 'L', '2002-09-08', 'SMA', NULL, 0),
('1174020904930064', 'Irfan Hakim', 'L', '1993-04-09', 'S1', NULL, 0),
('1174020910030034', 'Eka Saputri', 'P', '2003-10-09', 'SMA', NULL, 0),
('1174021005940065', 'Jessica Mila', 'P', '1994-05-10', 'S1', NULL, 0),
('1174021011040035', 'Feryawan', 'L', '2004-11-10', 'SMA', NULL, 0),
('1174021106950066', 'Kevin Julio', 'L', '1995-06-11', 'SMA', NULL, 0),
('1174021112050036', 'Gita Gutawow', 'P', '2005-12-11', 'S1', NULL, 0),
('1174021201060037', 'Husni Thamrin', 'L', '2006-01-12', 'SMA', NULL, 0),
('1174021207960067', 'Luna Maya', 'P', '1996-07-12', 'S1', NULL, 0),
('1174021302070038', 'Ika Kartika', 'P', '2007-02-13', 'SMA', NULL, 0),
('1174021308970068', 'Melaney Ricardo', 'P', '1997-08-13', 'S1', NULL, 0),
('1174021403080039', 'Joko Susilo', 'L', '2008-03-14', 'SMA', NULL, 0),
('1174021409980069', 'Nino Fernandez', 'L', '1998-09-14', 'S1', NULL, 0),
('1174021504090040', 'Kartini', 'P', '2009-04-15', 'SMA', NULL, 0),
('1174021510990070', 'Olla Ramlan', 'P', '1999-10-15', 'SMA', NULL, 0),
('1174021605900041', 'Lukman Hakim', 'L', '1990-05-16', 'SMA', NULL, 0),
('1174021611000071', 'Prilly Latuconsina', 'P', '2000-11-16', 'S1', NULL, 0),
('1174021706910042', 'Maya Sari', 'P', '1991-06-17', 'SMA', NULL, 0),
('1174021712010072', 'Raditya Dika', 'L', '2001-12-17', 'S1', NULL, 0),
('1174021801020073', 'Syifa Hadju', 'P', '2002-01-18', 'SMA', NULL, 0),
('1174021807920043', 'Nanda Syahputra', 'L', '1992-07-18', 'S1', NULL, 0),
('1174021902030074', 'Tora Sudiro', 'L', '2003-02-19', 'SMA', NULL, 0),
('1174021908930044', 'Oki Setiana', 'P', '1993-08-19', 'S1', NULL, 0),
('1174022003040075', 'Ussy Sulistiawaty', 'P', '2004-03-20', 'SMA', NULL, 0),
('1174022009940045', 'Panji Pragi', 'L', '1994-09-20', 'S1', NULL, 0),
('1174022110950046', 'Qory Sandioriva', 'P', '1995-10-21', 'SMA', NULL, 0),
('1174022211960047', 'Rahmat Hidayat', 'L', '1996-11-22', 'S1', NULL, 0),
('1174022312970048', 'Susi Susanti', 'P', '1997-12-23', 'SMA', NULL, 0),
('1174022401980049', 'Tari Lestari', 'P', '1998-01-24', 'S1', NULL, 0),
('1174022502990050', 'Umar Kayam', 'L', '1999-02-25', 'SMA', NULL, 0),
('1174022704010052', 'Wawan Darmawan', 'L', '2001-04-27', 'S1', NULL, 0),
('1174022805020053', 'Xena Aprilia', 'P', '2002-05-28', 'SMA', NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `tb_penempatan`
--

CREATE TABLE `tb_penempatan` (
  `id_penempatan` int NOT NULL,
  `nik_pencaker` varchar(16) NOT NULL,
  `id_lowongan` int NOT NULL,
  `tanggal_diterima` date NOT NULL,
  `jenis_kontrak` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_penempatan`
--

INSERT INTO `tb_penempatan` (`id_penempatan`, `nik_pencaker`, `id_lowongan`, `tanggal_diterima`, `jenis_kontrak`) VALUES
(1, '1171040104050076', 1, '2026-08-28', 'PKWTT (Tetap)'),
(2, '1171040205060077', 3, '2026-08-29', 'PKWTT (Tetap)'),
(3, '1171040306070078', 5, '2026-08-30', 'PKWT (Kontrak 1 Tahun)'),
(4, '1171040407080079', 8, '2026-09-02', 'PKWT (Kontrak 6 Bulan)'),
(5, '1171040508090080', 10, '2026-08-15', 'PKWTT (Tetap)'),
(6, '1171040609900081', 11, '2026-08-20', 'Freelance'),
(7, '1174020102950026', 14, '2026-08-10', 'Harian Lepas'),
(8, '1174020108050056', 15, '2026-08-25', 'PKWTT (Tetap)'),
(9, '1174020203960027', 9, '2026-08-18', 'PKWT (Kontrak 1 Tahun)'),
(10, '1174020209060057', 6, '2026-08-22', 'PKWT (Kontrak 2 Tahun)');

-- --------------------------------------------------------

--
-- Table structure for table `tb_perusahaan`
--

CREATE TABLE `tb_perusahaan` (
  `nib` varchar(20) NOT NULL,
  `nama_perusahaan` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `sektor_industri` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `alamat_perusahaan` text NOT NULL,
  `jml_pekerja_tetap` int NOT NULL,
  `jml_pekerja_kontrak` int NOT NULL,
  `status_bpjs` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_perusahaan`
--

INSERT INTO `tb_perusahaan` (`nib`, `nama_perusahaan`, `sektor_industri`, `alamat_perusahaan`, `jml_pekerja_tetap`, `jml_pekerja_kontrak`, `status_bpjs`) VALUES
('0191877455667755', 'Klinik Sehat Bersama', 'Kesehatan', 'Jl. Ahmad Yani No. 90, Surabaya', 30, 10, 1),
('1101988455667744', 'PT Agro Makmur Sentosa', 'Agribisnis', 'Jl. Perkebunan Sawit, Riau', 400, 80, 1),
('2112099455667733', 'PT Bina Karya Konstruksi', 'Konstruksi', 'Kawasan Industri Medan', 300, 150, 1),
('3122100455667722', 'PT Rekaman Nu Metal Media', 'Hiburan & Media', 'Kawasan Kemang, Jakarta Selatan', 25, 15, 1),
('4132211455667711', 'CV Valerius Leofric Makmur', 'Perdagangan Umum', 'Jl. Gajah Mada No. 12, Semarang', 10, 2, 0),
('5142322455667700', 'PT Server Andalan Dua Dua', 'Telekomunikasi', 'Data Center Cibinong Blok C', 60, 5, 1),
('6152433455667799', 'PT Pesan Antar Pangan', 'Logistik & E-Commerce', 'Jl. Sudirman Kav 21, Jakarta', 200, 450, 1),
('7162534455667788', 'CV Susu Fermentasi Nusantara', 'Industri Pangan', 'Jl. Peternakan No. 8, Lembang', 15, 25, 1),
('8172635409182736', 'PT Hibrida Komunitas Awan', 'Infrastruktur Cloud', 'Kawasan Industri Bizpark, Bandung', 120, 30, 1),
('9120304050607080', 'PT Visi Komputasi Cerdas', 'Teknologi Informasi', 'Gedung Cyber Lt. 4, Jakarta', 45, 12, 1);

-- --------------------------------------------------------

--
-- Table structure for table `tb_peserta_pelatihan`
--

CREATE TABLE `tb_peserta_pelatihan` (
  `id_peserta_pelatihan` int NOT NULL,
  `nik_pencaker` varchar(16) NOT NULL,
  `id_pelatihan` int NOT NULL,
  `tanggal_daftar` date NOT NULL,
  `status_peserta` enum('Terdaftar','Mengikuti','Lulus','Tidak Lulus') NOT NULL DEFAULT 'Terdaftar'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_peserta_pelatihan`
--

INSERT INTO `tb_peserta_pelatihan` (`id_peserta_pelatihan`, `nik_pencaker`, `id_pelatihan`, `tanggal_daftar`, `status_peserta`) VALUES
(1, '1171040811920083', 1, '2026-08-01', 'Lulus'),
(2, '1171040912930084', 1, '2026-08-02', 'Lulus'),
(3, '1171041001940085', 3, '2026-08-05', 'Mengikuti'),
(4, '1171041102950086', 4, '2026-08-10', 'Mengikuti'),
(5, '1171041203960087', 5, '2026-08-12', 'Terdaftar'),
(6, '1174020304970028', 6, '2026-08-15', 'Lulus'),
(7, '1174020310070058', 2, '2026-08-15', 'Tidak Lulus');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_kasus_hi`
--
ALTER TABLE `tb_kasus_hi`
  ADD PRIMARY KEY (`id_kasus`),
  ADD KEY `tb_kasus_hi_nib_perusahaan_index` (`nib_perusahaan`),
  ADD KEY `tb_kasus_hi_kategori_kasus_index` (`kategori_kasus`),
  ADD KEY `tb_kasus_hi_status_penyelesaian_index` (`status_penyelesaian`);

--
-- Indexes for table `tb_lowongan`
--
ALTER TABLE `tb_lowongan`
  ADD PRIMARY KEY (`id_lowongan`),
  ADD KEY `tb_lowongan_nib_perusahaan_index` (`nib_perusahaan`);

--
-- Indexes for table `tb_pelatihan_blk`
--
ALTER TABLE `tb_pelatihan_blk`
  ADD PRIMARY KEY (`id_pelatihan`),
  ADD KEY `tb_pelatihan_blk_jenis_kejuruan_index` (`jenis_kejuruan`),
  ADD KEY `tb_pelatihan_blk_tanggal_pelaksanaan_index` (`tanggal_pelaksanaan`);

--
-- Indexes for table `tb_penduduk_pencaker`
--
ALTER TABLE `tb_penduduk_pencaker`
  ADD PRIMARY KEY (`nik`);

--
-- Indexes for table `tb_penempatan`
--
ALTER TABLE `tb_penempatan`
  ADD PRIMARY KEY (`id_penempatan`),
  ADD UNIQUE KEY `tb_penempatan_nik_pencaker_id_lowongan_unique` (`nik_pencaker`,`id_lowongan`),
  ADD KEY `tb_penempatan_nik_pencaker_index` (`nik_pencaker`),
  ADD KEY `tb_penempatan_id_lowongan_index` (`id_lowongan`);

--
-- Indexes for table `tb_perusahaan`
--
ALTER TABLE `tb_perusahaan`
  ADD PRIMARY KEY (`nib`);

--
-- Indexes for table `tb_peserta_pelatihan`
--
ALTER TABLE `tb_peserta_pelatihan`
  ADD PRIMARY KEY (`id_peserta_pelatihan`),
  ADD UNIQUE KEY `tb_peserta_pelatihan_nik_pencaker_id_pelatihan_unique` (`nik_pencaker`,`id_pelatihan`),
  ADD KEY `tb_peserta_pelatihan_nik_pencaker_index` (`nik_pencaker`),
  ADD KEY `tb_peserta_pelatihan_id_pelatihan_index` (`id_pelatihan`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_kasus_hi`
--
ALTER TABLE `tb_kasus_hi`
  MODIFY `id_kasus` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `tb_lowongan`
--
ALTER TABLE `tb_lowongan`
  MODIFY `id_lowongan` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `tb_pelatihan_blk`
--
ALTER TABLE `tb_pelatihan_blk`
  MODIFY `id_pelatihan` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `tb_penempatan`
--
ALTER TABLE `tb_penempatan`
  MODIFY `id_penempatan` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `tb_peserta_pelatihan`
--
ALTER TABLE `tb_peserta_pelatihan`
  MODIFY `id_peserta_pelatihan` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tb_kasus_hi`
--
ALTER TABLE `tb_kasus_hi`
  ADD CONSTRAINT `tb_kasus_hi_nib_perusahaan_foreign` FOREIGN KEY (`nib_perusahaan`) REFERENCES `tb_perusahaan` (`nib`);

--
-- Constraints for table `tb_lowongan`
--
ALTER TABLE `tb_lowongan`
  ADD CONSTRAINT `tb_lowongan_nib_perusahaan_foreign` FOREIGN KEY (`nib_perusahaan`) REFERENCES `tb_perusahaan` (`nib`);

--
-- Constraints for table `tb_penempatan`
--
ALTER TABLE `tb_penempatan`
  ADD CONSTRAINT `tb_penempatan_id_lowongan_foreign` FOREIGN KEY (`id_lowongan`) REFERENCES `tb_lowongan` (`id_lowongan`),
  ADD CONSTRAINT `tb_penempatan_nik_pencaker_foreign` FOREIGN KEY (`nik_pencaker`) REFERENCES `tb_penduduk_pencaker` (`nik`);

--
-- Constraints for table `tb_peserta_pelatihan`
--
ALTER TABLE `tb_peserta_pelatihan`
  ADD CONSTRAINT `tb_peserta_pelatihan_id_pelatihan_foreign` FOREIGN KEY (`id_pelatihan`) REFERENCES `tb_pelatihan_blk` (`id_pelatihan`),
  ADD CONSTRAINT `tb_peserta_pelatihan_nik_pencaker_foreign` FOREIGN KEY (`nik_pencaker`) REFERENCES `tb_penduduk_pencaker` (`nik`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
