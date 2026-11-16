-- =========================================================
-- Database Source: SDA Lingkungan (Kotor - Raw Data)
-- Digunakan untuk testing ETL: raw → staging → dwh
-- Total rows: 300+ (300 untuk master + transactional)
-- Dirty data variations untuk real-world testing
-- =========================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- =========================================================
-- Table: master_wilayah (100 rows - KOTOR)
-- =========================================================

DROP TABLE IF EXISTS `master_wilayah`;
CREATE TABLE `master_wilayah` (
  `id_desa` varchar(10) NOT NULL,
  `nama_desa` varchar(100),
  `id_kecamatan` varchar(10),
  `nama_kecamatan` varchar(100),
  `id_kabupaten_kota` varchar(10),
  `nama_kabupaten_kota` varchar(100),
  `nama_provinsi` varchar(100),
  PRIMARY KEY (`id_desa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `master_wilayah` VALUES
('01011', '  Desa Peuniti  ', '0101', 'Kecamatan Baiturrahman', '01', 'Kota Banda Aceh', 'Aceh'),
('01012', 'Desa Punge Blang Cut', '0101', 'Kecamatan Baiturrahman', '01', 'Kota Banda Aceh', NULL),
('01013', 'DESA LAMPRIET', '0101', 'kecamatan baiturrahman', '01', 'Kota Banda Aceh', 'Aceh'),
('01014', 'Desa Larangan', '0101', 'Kecamatan Baiturrahman', '01', 'kota banda aceh', 'Aceh'),
('01015', 'Desa Rangkayo ', '0101', 'Kecamatan Baiturrahman', '01', 'Kota Banda Aceh', 'Aceh'),
('01021', 'desa lam u', '0102', 'KECAMATAN JAYA BARU', '01', 'Kota Banda Aceh', 'Aceh'),
('01022', 'Desa Cot Kala', '0102', 'Kecamatan Jaya Baru', '01', 'Kota Banda Aceh', NULL),
('01023', 'Desa Pasa Baru ', '0102', 'kecamatan jaya baru', '01', 'Kota Banda Aceh', 'Aceh'),
('01031', 'Desa Pocut Baren', '0103', 'Kecamatan Kuta Alam', '01', 'Kota Banda Aceh', 'Aceh'),
('01032', 'DESA KUALA', '0103', 'Kecamatan Kuta Alam', '01', 'kota banda aceh', 'Aceh'),
('01041', 'Desa Rajabasa  ', '0104', 'Kecamatan Kuta Raja', '01', 'Kota Banda Aceh', 'Aceh'),
('01042', 'Desa Pante Kulu', '0104', 'Kecamatan Kuta Raja', '01', 'Kota Banda Aceh', 'Aceh'),
('01051', 'Desa Alue Naga', '0105', 'Kecamatan Meuraxa', '01', 'KOTA BANDA ACEH', 'Aceh'),
('01052', 'Desa Deah Raya ', '0105', 'Kecamatan Meuraxa', '01', 'Kota Banda Aceh', NULL),
('01061', 'Desa Gompong', '0106', 'Kecamatan Syiah Kuala', '01', 'Kota Banda Aceh', 'Aceh'),
('01062', 'desa batoh', '0106', 'kecamatan syiah kuala', '01', 'Kota Banda Aceh', 'Aceh'),
('02011', 'Desa Pulo Aceh ', '0201', 'Kecamatan Sabang', '02', 'Kota Sabang', 'Aceh'),
('02012', 'Desa Sabang Kota', '0201', 'Kecamatan Sabang', '02', 'KOTA SABANG', 'Aceh'),
('02021', 'DESA IBOIH', '0202', 'Kecamatan Pulau Weh', '02', 'Kota Sabang', NULL),
('02022', 'Desa Teupin Layeu', '0202', 'Kecamatan Pulau Weh', '02', 'Kota Sabang', 'Aceh'),
('03011', 'Desa Blang Jurong ', '0301', 'Kecamatan Langsa Barat', '03', 'Kota Langsa', 'Aceh'),
('03012', 'desa arun lama', '0301', 'kecamatan langsa barat', '03', 'Kota Langsa', 'Aceh'),
('03021', 'Desa Langsa Lama', '0302', 'Kecamatan Langsa Timur', '03', 'Kota Langsa', 'Aceh'),
('03022', 'Desa Giok  ', '0302', 'Kecamatan Langsa Timur', '03', 'KOTA LANGSA', NULL),
('04011', 'Desa Muara Batu', '0401', 'Kecamatan Muara Batu', '04', 'Kota Lhokseumawe', 'Aceh'),
('04012', 'Desa Cot Mangga ', '0401', 'Kecamatan Muara Batu', '04', 'Kota Lhokseumawe', 'Aceh'),
('04021', 'DESA MUARA DUA', '0402', 'Kecamatan Muara Dua', '04', 'Kota Lhokseumawe', 'Aceh'),
('04022', 'Desa Kuala Marah', '0402', 'Kecamatan Muara Dua', '04', 'kota lhokseumawe', 'Aceh'),
('04031', 'Desa Blang Mangat ', '0403', 'Kecamatan Blang Mangat', '04', 'Kota Lhokseumawe', NULL),
('04032', 'desa pante bidok', '0403', 'kecamatan blang mangat', '04', 'Kota Lhokseumawe', 'Aceh'),
('05011', 'Desa Meulaboh', '0501', 'Kecamatan Meulaboh', '05', 'Kabupaten Aceh Barat', 'Aceh'),
('05012', 'Desa Ujung Kalak  ', '0501', 'Kecamatan Meulaboh', '05', 'Kabupaten Aceh Barat', 'Aceh'),
('05021', 'DESA JOHAN PAHLAWAN', '0502', 'Kecamatan Johan Pahlawan', '05', 'Kabupaten Aceh Barat', NULL),
('05022', 'Desa Saree', '0502', 'Kecamatan Johan Pahlawan', '05', 'Kabupaten Aceh Barat', 'Aceh'),
('05031', 'Desa Samatiga ', '0503', 'Kecamatan Samatiga', '05', 'KABUPATEN ACEH BARAT', 'Aceh'),
('05032', 'desa alue ie', '0503', 'kecamatan samatiga', '05', 'Kabupaten Aceh Barat', 'Aceh'),
('05041', 'Desa Arongan', '0504', 'Kecamatan Arongan Lambalek', '05', 'Kabupaten Aceh Barat', 'Aceh'),
('05042', 'Desa Lambalek ', '0504', 'Kecamatan Arongan Lambalek', '05', 'Kabupaten Aceh Barat', 'Aceh'),
('05051', 'DESA BUBON', '0505', 'Kecamatan Bubon', '05', 'Kabupaten Aceh Barat', NULL),
('05052', 'Desa Pante Tutue', '0505', 'Kecamatan Bubon', '05', 'Kabupaten Aceh Barat', 'Aceh'),
('05061', 'Desa Pantai Cerah ', '0506', 'Kecamatan Pantai Cerah', '05', 'Kabupaten Aceh Barat', 'Aceh'),
('05062', 'desa kuala merah', '0506', 'kecamatan pantai cerah', '05', 'Kabupaten Aceh Barat', 'Aceh'),
('06011', 'Desa Blangpidie', '0601', 'Kecamatan Blangpidie', '06', 'Kabupaten Aceh Barat Daya', 'Aceh'),
('06012', 'Desa Alue Sungai Pinang  ', '0601', 'Kecamatan Blangpidie', '06', 'Kabupaten Aceh Barat Daya', NULL),
('06021', 'DESA MANGGENG', '0602', 'Kecamatan Manggeng', '06', 'Kabupaten Aceh Barat Daya', 'Aceh'),
('06022', 'Desa Kedai Manggeng', '0602', 'Kecamatan Manggeng', '06', 'kabupaten aceh barat daya', 'Aceh'),
('06031', 'Desa Ujung Padang', '0603', 'Kecamatan Samatiga', '06', 'Kabupaten Aceh Barat Daya', 'Aceh'),
('06032', 'Desa Suak Bakong ', '0603', 'Kecamatan Samatiga', '06', 'Kabupaten Aceh Barat Daya', 'Aceh'),
('06041', 'desa kuala bhee', '0604', 'kecamatan kuala bhee', '06', 'Kabupaten Aceh Barat Daya', NULL),
('06042', 'Desa Sikabu', '0604', 'Kecamatan Kuala Bhee', '06', 'Kabupaten Aceh Barat Daya', 'Aceh'),
('07011', 'Desa Lhoknga', '0701', 'Kecamatan Lhoknga', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07012', 'DESA BEUTONG', '0701', 'Kecamatan Lhoknga', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07013', 'Desa Leubak Bata ', '0701', 'Kecamatan Lhoknga', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07014', 'Desa Meulaboh Jaya', NULL, NULL, '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07021', 'desa leupuet', '0702', 'kecamatan leupuet', '07', 'KABUPATEN ACEH BESAR', NULL),
('07022', 'Desa Lampanah  ', '0702', 'Kecamatan Leupuet', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07023', 'Desa Ueubeulo', '0702', 'Kecamatan Leupuet', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07031', 'DESA DARUL IMARAH', '0703', 'Kecamatan Darul Imarah', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07032', 'Desa Mekar Tanjung ', '0703', 'Kecamatan Darul Imarah', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07041', 'Desa Lhoong', '0704', 'Kecamatan Lhoong', '07', 'Kabupaten Aceh Besar', NULL),
('07042', 'desa cot garpet', '0704', 'kecamatan lhoong', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07051', 'Desa Baitussalam ', '0705', 'Kecamatan Baitussalam', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07052', 'Desa Neunom', '0705', 'Kecamatan Baitussalam', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07061', 'DESA LHOWE', '0706', 'Kecamatan Lhowe', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07062', 'Desa Cot Raya', '0706', 'Kecamatan Lhowe', '07', 'KABUPATEN ACEH BESAR', 'Aceh'),
('07071', 'Desa Ulim  ', '0707', 'Kecamatan Ulim', '07', 'Kabupaten Aceh Besar', NULL),
('07072', 'desa jaro', '0707', 'kecamatan ulim', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07081', 'Desa Montasik', '0708', 'Kecamatan Montasik', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07082', 'Desa Pante Pandeu ', '0708', 'Kecamatan Montasik', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07091', 'DESA MESJID RAYA', '0709', 'Kecamatan Mesjid Raya', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07092', 'Desa Cot Tabe', '0709', 'Kecamatan Mesjid Raya', '07', 'Kabupaten Aceh Besar', NULL),
('07101', 'Desa Lheuh', '0710', 'Kecamatan Lheuh', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07102', 'Desa Lhee ', '0710', 'Kecamatan Lheuh', '07', 'KABUPATEN ACEH BESAR', 'Aceh'),
('07111', 'desa peukan bada', '0711', 'kecamatan peukan bada', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07112', 'Desa Neunyeu', '0711', 'Kecamatan Peukan Bada', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('07121', 'DESA LHOKTAI', '0712', 'Kecamatan Lhoktai', '07', 'Kabupaten Aceh Besar', NULL),
('07122', 'Desa Banda Raya ', '0712', 'Kecamatan Lhoktai', '07', 'Kabupaten Aceh Besar', 'Aceh'),
('08011', 'Desa Seulimeum', '0801', 'Kecamatan Seulimeum', '08', 'Kabupaten Aceh Jaya', 'Aceh'),
('08012', 'desa panggang', '0801', 'kecamatan seulimeum', '08', 'Kabupaten Aceh Jaya', 'Aceh'),
('08021', 'Desa Acehjaya  ', '0802', 'Kecamatan Acehjaya', '08', 'KABUPATEN ACEH JAYA', 'Aceh'),
('08022', 'Desa Cot Gajah', '0802', 'Kecamatan Acehjaya', '08', 'Kabupaten Aceh Jaya', 'Aceh'),
('08031', 'DESA JAYA', '0803', 'Kecamatan Jaya', '08', 'Kabupaten Aceh Jaya', NULL),
('08032', 'Desa Meulaboh Baru', '0803', 'Kecamatan Jaya', '08', 'Kabupaten Aceh Jaya', 'Aceh'),
('08041', 'Desa Teunom ', '0804', 'Kecamatan Teunom', '08', 'Kabupaten Aceh Jaya', 'Aceh'),
('08042', 'desa ilie', '0804', 'kecamatan teunom', '08', 'Kabupaten Aceh Jaya', 'Aceh'),
('09011', 'Desa Tapaktuan', '0901', 'Kecamatan Tapaktuan', '09', 'Kabupaten Aceh Selatan', 'Aceh'),
('09012', 'DESA UJUNG', '0901', 'Kecamatan Tapaktuan', '09', 'Kabupaten Aceh Selatan', 'Aceh'),
('09021', 'Desa Bakongan ', '0902', 'Kecamatan Bakongan', '09', 'KABUPATEN ACEH SELATAN', NULL),
('09022', 'Desa Menanggal', '0902', 'Kecamatan Bakongan', '09', 'Kabupaten Aceh Selatan', 'Aceh'),
('09031', 'desa labuhan haji', '0903', 'kecamatan labuhan haji', '09', 'Kabupaten Aceh Selatan', 'Aceh'),
('09032', 'Desa Labuhan Haji Barat ', '0903', 'Kecamatan Labuhan Haji', '09', 'Kabupaten Aceh Selatan', 'Aceh'),
('09041', 'Desa Tanjong Layeu', '0904', 'Kecamatan Tanjong Layeu', '09', 'Kabupaten Aceh Selatan', 'Aceh'),
('09042', 'DESA UJUNG LHEU', '0904', 'Kecamatan Tanjong Layeu', '09', 'Kabupaten Aceh Selatan', NULL),
('09051', 'Desa Sama Dua ', '0905', 'Kecamatan Sama Dua', '09', 'Kabupaten Aceh Selatan', 'Aceh'),
('09052', 'desa payakumbuh', '0905', 'kecamatan sama dua', '09', 'Kabupaten Aceh Selatan', 'Aceh'),
('09061', 'Desa Kota Baharu', '0906', 'Kecamatan Kota Baharu', '09', 'Kabupaten Aceh Selatan', 'Aceh'),
('09062', 'Desa Sebrang  ', '0906', 'Kecamatan Kota Baharu', '09', 'KABUPATEN ACEH SELATAN', 'Aceh'),
('09071', 'DESA MANGGENG', '0907', 'Kecamatan Manggeng', '09', 'Kabupaten Aceh Selatan', 'Aceh'),
('09072', 'Desa Batu Raja', '0907', 'Kecamatan Manggeng', '09', 'Kabupaten Aceh Selatan', NULL),
('10011', 'Desa Singkil ', '1001', 'Kecamatan Singkil', '10', 'Kabupaten Aceh Singkil', 'Aceh');

-- =========================================================
-- Table: master_fasilitas_sampah (22 rows - KOTOR)
-- =========================================================

DROP TABLE IF EXISTS `master_fasilitas_sampah`;
CREATE TABLE `master_fasilitas_sampah` (
  `id_fasilitas` varchar(20) NOT NULL,
  `nama_fasilitas` varchar(255),
  `jenis_fasilitas` varchar(50),
  `id_desa` varchar(10),
  `nama_desa` varchar(100),
  `kapasitas_maksimal_ton` decimal(10,2),
  `status_operasional` varchar(50),
  PRIMARY KEY (`id_fasilitas`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `master_fasilitas_sampah` VALUES
('FAS-002', 'Fasilitas Bank Sampah Desa Meulaboh Jaya', 'bank sampah', '07014', 'Desa Meulaboh Jaya', 1417.58, 'Aktif'),
('FAS-005', 'Fasilitas TPA Desa Peukan Bada', 'TPA', '07111', 'Desa Peukan Bada', 1298.22, 'aktif'),
('FAS-008', '  Fasilitas TPA Desa Lhoknga  ', NULL, '07011', 'Desa Lhoknga', -500.00, 'Non-Aktif'),
('FAS-009', 'Fasilitas Bank Sampah Desa Cot Gajah', 'Bank Sampah', '08022', 'Desa Cot Gajah', 1304.23, 'AKTIF'),
('FAS-012', 'FASILITAS BANK SAMPAH DESA PANTE PANDEU', '', '07082', 'Desa Pante Pandeu', 219.99, 'Aktif'),
('FAS-014', 'Fasilitas TPA Desa Mesjid Raya', 'TPA', '07091', 'Desa Mesjid Raya', 1351.41, NULL),
('FAS-015', 'Fasilitas TPS 3R Desa Deah Raya ', 'TPS 3R', '01052', 'Desa Deah Raya', 1007.41, 'Aktif'),
('FAS-016', 'fasilitas tpa desa ulim', 'TPA', '07071', 'Desa Ulim', 116.86, 'aktif'),
('FAS-018', 'Fasilitas TPS 3R Desa Mekar Tanjung', 'tps 3r', '07032', 'Desa Mekar Tanjung', 1256.38, 'Aktif'),
('FAS-019', 'Fasilitas Bank Sampah Desa Lampanah ', 'Bank Sampah', '07022', 'Desa Lampanah', 254.97, 'AKTIF'),
('FAS-020', 'Fasilitas TPS 3R Desa Manggeng', 'TPS 3R', '09071', 'Desa Manggeng', 133.21, NULL),
('FAS-021', 'Fasilitas TPS 3R Desa Panggang', 'TPS 3R', '08012', 'Desa Panggang', 1172.18, 'Aktif'),
('FAS-022', 'FASILITAS BANK SAMPAH DESA JAYA  ', 'Bank Sampah', '08031', 'Desa Jaya', 545.25, 'aktif'),
('FAS-023', 'Fasilitas TPS 3R Desa Lhowe', 'tps 3r', '07061', 'Desa Lhowe', 824.68, 'Aktif'),
('FAS-026', 'fasilitas tpa desa neunom', NULL, '07052', 'Desa Neunom', -664.35, 'Non-Aktif'),
('FAS-028', 'Fasilitas TPA Desa Rajabasa ', 'TPA', '01041', 'Desa Rajabasa', 565.14, 'Aktif'),
('FAS-029', 'Fasilitas Bank Sampah Desa Sama Dua', 'Bank Sampah', '09051', 'Desa Sama Dua', 920.59, 'AKTIF'),
('FAS-032', 'FASILITAS BANK SAMPAH DESA LHOONG', 'bank sampah', '07041', 'Desa Lhoong', 636.32, NULL),
('FAS-034', 'Fasilitas TPA Desa Peuniti ', 'TPA', '01011', 'Desa Peuniti', 1168.09, 'Aktif'),
('FAS-037', 'fasilitas tpa desa montasik', 'TPA', '07081', 'Desa Montasik', 341.68, 'aktif'),
('FAS-039', 'Fasilitas TPA Desa Pocut Baren', 'TPA', '01031', 'Desa Pocut Baren', 434.68, 'Aktif'),
('FAS-040', 'Fasilitas TPA Desa Muara Batu  ', NULL, '04011', 'Desa Muara Batu', 918.41, 'AKTIF');

-- =========================================================
-- Table: master_perusahaan (15 rows - KOTOR)
-- =========================================================

DROP TABLE IF EXISTS `master_perusahaan`;
CREATE TABLE `master_perusahaan` (
  `id_perusahaan` varchar(20) NOT NULL,
  `nama_perusahaan` varchar(255),
  `bidang_usaha` varchar(100),
  `alamat_lengkap` varchar(300),
  `id_desa` varchar(10),
  `nama_desa` varchar(100),
  `kontak_perusahaan` varchar(50),
  PRIMARY KEY (`id_perusahaan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `master_perusahaan` VALUES
('PT-002', '  PT. Aceh Mandiri 2  ', 'Agribisnis', 'Jalan Utama Desa Banda Raya No. 2', '07122', 'Desa Banda Raya', '08123456702'),
('PT-010', 'PT. ACEH MANDIRI 10', 'PLTU / Energi', 'Jalan Utama Desa Sabang Kota No. 10', '02012', 'Desa Sabang Kota', '+62-812-345-6710'),
('PT-016', 'PT. Aceh Mandiri 16', 'Pengolahan Kayu', 'Jalan Utama Desa Meulaboh Baru No. 16', '08032', 'Desa Meulaboh Baru', NULL),
('PT-017', 'PT. Aceh Mandiri 17 ', NULL, 'Jalan Utama Desa Cot Gajah No. 17', '08022', 'Desa Cot Gajah', '08123456717'),
('PT-020', 'PT. Aceh Mandiri 20', 'Pabrik Kopi', '  Jalan Utama Desa Rangkayo No. 20  ', '01015', 'Desa Rangkayo', '081234567XX'),
('PT-023', 'pt. aceh mandiri 23', 'Agribisnis', 'Jalan Utama Desa Singkil No. 23', '10011', 'Desa Singkil', '08123456723'),
('PT-024', 'PT. ACEH MANDIRI 24', 'Pengolahan Kayu', 'Jalan Utama Desa Peuniti No. 24 ', '01011', 'Desa Peuniti', NULL),
('PT-029', 'PT. Aceh Mandiri 29', 'Pabrik Kopi', 'Jalan Utama Desa Ilie No. 29', '08042', 'Desa Ilie', '08123456729'),
('PT-030', 'PT. Aceh Mandiri 30  ', 'Pengolahan Kayu', 'Jalan Utama Desa Sebrang No. 30', '09062', 'Desa Sebrang', '0812-345-6730'),
('PT-033', 'PT. Aceh Mandiri 33', 'Pertambangan', 'Jalan Utama Desa Blang Mangat No. 33', '04031', 'Desa Blang Mangat', '08123456733'),
('PT-040', 'pt aceh mandiri 40', 'Agribisnis', 'Jalan Utama Desa Kuala Marah No. 40', '04022', 'Desa Kuala Marah', NULL),
('PT-041', 'PT. Aceh Mandiri 41', 'Pengolahan Kayu', '  Jalan Utama Desa Pocut Baren No. 41  ', '01031', 'Desa Pocut Baren', '08123456741'),
('PT-043', 'PT. ACEH MANDIRI 43', 'PLTU / Energi', 'Jalan Utama Desa Lheuh No. 43', '07101', 'Desa Lheuh', '08123456743'),
('PT-049', 'PT. Aceh Mandiri 49', 'Pabrik Kopi', 'Jalan Utama Desa Alue Naga No. 49', '01051', 'Desa Alue Naga', NULL),
('PT-050', 'PT. Aceh Mandiri 50 ', 'Agribisnis', 'Jalan Utama Desa Iboih No. 50', '02021', 'Desa Iboih', '08123456750');

-- =========================================================
-- Table: master_stasiun_pantau (27 rows - KOTOR)
-- =========================================================

DROP TABLE IF EXISTS `master_stasiun_pantau`;
CREATE TABLE `master_stasiun_pantau` (
  `id_stasiun` varchar(20) NOT NULL,
  `nama_stasiun` varchar(255),
  `jenis_stasiun` varchar(50),
  `id_desa` varchar(10),
  `nama_desa` varchar(100),
  `koordinat_gps` varchar(100),
  `status_aktif` varchar(50),
  PRIMARY KEY (`id_stasiun`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `master_stasiun_pantau` VALUES
('ST-001', 'Stasiun Desa Tanjong Layeu', 'Air Sungai', '09041', 'Desa Tanjong Layeu', '2.8395,97.5629', '1'),
('ST-003', 'Stasiun Desa Sabang Kota ', 'Udara', '02012', 'Desa Sabang Kota', 'invalid', '0'),
('ST-004', 'Stasiun Desa Pante Bidok', 'UDARA', '04032', 'Desa Pante Bidok', '4.8545,95.6800', 'Aktif'),
('ST-005', 'STASIUN DESA RAJABASA', NULL, '01041', 'Desa Rajabasa', '', '1'),
('ST-006', 'Stasiun Desa Ujung Kalak ', 'Air sungai', '05012', 'Desa Ujung Kalak', '4.2600,96.6884', 'yes'),
('ST-010', 'Stasiun Desa Cot Raya', 'Air Sungai', '07062', 'Desa Cot Raya', '3.7375,95.8024', NULL),
('ST-011', 'stasiun desa larangan', 'udara', '01014', 'Desa Larangan', '2.6560,97.2577', 'Aktif'),
('ST-013', 'Stasiun Desa Labuhan Haji ', 'Udara', '09031', 'Desa Labuhan Haji', '5.7050,96.0682', '1'),
('ST-014', 'Stasiun Desa Menanggal', 'UDARA', '09022', 'Desa Menanggal', '', '0'),
('ST-016', 'STASIUN DESA NEUNOM  ', 'Udara', '07052', 'Desa Neunom', '3.5719,97.7097', 'Aktif'),
('ST-017', 'Stasiun Desa Muara Batu', 'udara', '04011', 'Desa Muara Batu', '2.2916,95.4234', NULL),
('ST-018', 'Stasiun Desa Tanjong Layeu ', 'Udara', '09041', 'Desa Tanjong Layeu', '5.2214,95.8930', '1'),
('ST-019', 'Stasiun Desa Meulaboh Jaya', 'AIR SUNGAI', '07014', 'Desa Meulaboh Jaya', '3.6780,97.1447', 'Aktif'),
('ST-020', 'stasiun desa muara dua', 'udara', '04021', 'Desa Muara Dua', '2.1836,95.7218', 'Aktif'),
('ST-022', 'Stasiun Desa Ujung Lheu', 'Udara', '09042', 'Desa Ujung Lheu', '4.9646,97.4512', NULL),
('ST-023', 'STASIUN DESA MEULABOH  ', 'Air Sungai', '05011', 'Desa Meulaboh', '5.8147,96.8731', '1'),
('ST-024', 'Stasiun Desa Ujung Kalak', 'udara', '05012', 'Desa Ujung Kalak', '4.9840,98.1512', 'Aktif'),
('ST-025', 'Stasiun Desa Leubak Bata ', 'Udara', '07013', 'Desa Leubak Bata', '2.1103,95.0210', '0'),
('ST-026', 'Stasiun Desa Peuniti', 'UDARA', '01011', 'Desa Peuniti', '3.2840,95.5289', NULL),
('ST-027', 'stasiun desa pante tutue', 'udara', '05052', 'Desa Pante Tutue', '2.7144,98.1622', 'Aktif'),
('ST-029', 'Stasiun Desa Neunom ', 'Air Sungai', '07052', 'Desa Neunom', '5.2726,97.8893', '1'),
('ST-030', 'STASIUN DESA PUNGE BLANG CUT', 'air sungai', '01012', 'Desa Punge Blang Cut', '5.8050,97.6509', 'Aktif'),
('ST-036', 'Stasiun Desa Samatiga', 'Air Sungai', '05031', 'Desa Samatiga', '2.1179,97.9517', NULL),
('ST-042', 'Stasiun Desa Labuhan Haji Barat ', 'Udara', '09032', 'Desa Labuhan Haji Barat', '4.2050,96.4235', '1'),
('ST-044', 'stasiun desa leubak bata', 'air sungai', '07013', 'Desa Leubak Bata', '2.1691,97.1456', 'Aktif'),
('ST-045', 'Stasiun Desa Acehjaya', 'AIR SUNGAI', '08021', 'Desa Acehjaya', '3.6993,95.0093', 'Aktif'),
('ST-050', 'STASIUN DESA MEULABOH', 'Air Sungai', '05011', 'Desa Meulaboh', '4.8717,96.1249', NULL);

-- =========================================================
-- Table: izin_lingkungan (31 rows - KOTOR)
-- =========================================================

DROP TABLE IF EXISTS `izin_lingkungan`;
CREATE TABLE `izin_lingkungan` (
  `id_izin` varchar(20) NOT NULL,
  `id_perusahaan` varchar(20),
  `nomor_izin` varchar(50),
  `jenis_dokumen` varchar(100),
  `tanggal_terbit` varchar(50),
  `masa_berlaku_tahun` int,
  `status_izin` varchar(50),
  PRIMARY KEY (`id_izin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `izin_lingkungan` VALUES
('IZN-0001', 'PT-002', 'IZN-0002', 'AMDAL', '2026-07-31', 5, 'Aktif'),
('IZN-0002', 'PT-010', 'IZN-0004', 'SPPL', '31/07/2025', 5, 'aktif'),
('IZN-0003', 'PT-016', 'IZN-0009', 'sppl', '2024-12-07', -2, 'Expired'),
('IZN-0004', 'PT-017', 'IZN-0011', 'AMDAL', '20-05-2026', NULL, 'AKTIF'),
('IZN-0005', 'PT-020', NULL, 'UKL-UPL', '2024-05-01', 5, 'Aktif'),
('IZN-0006', 'PT-023', 'IZN-0020', '', '2025-07-20', 5, NULL),
('IZN-0007', 'PT-024', 'IZN-0021  ', 'AMDAL', '2025-05-15', 5, 'Aktif'),
('IZN-0008', 'PT-029', 'IZN-0023', 'sppl', '15/05/2025', 5, 'aktif'),
('IZN-0009', 'PT-030', 'IZN-0025', 'UKL-UPL', '2024-08-20', 3, 'Expired'),
('IZN-0010', 'PT-033', 'IZN-0028', 'AMDAL', '20-08-2026', NULL, 'AKTIF'),
('IZN-0011', 'PT-040', 'IZN-0032 ', 'SPPL', '2025-09-10', 5, 'Aktif'),
('IZN-0012', 'PT-041', NULL, 'UKL-UPL', '10/09/2024', 3, 'Expired'),
('IZN-0013', 'PT-043', 'IZN-0039', 'amdal', '2026-02-28', 5, 'aktif'),
('IZN-0014', 'PT-049', 'IZN-0041 ', 'SPPL', '28/02/2026', NULL, 'Aktif'),
('IZN-0015', 'PT-050', 'IZN-0045', 'UKL-UPL', '2025-01-15', 5, NULL),
('IZN-0016', 'PT-002', 'IZN-0050', 'AMDAL', '15-01-2025', 5, 'Aktif'),
('IZN-0017', 'PT-010', 'IZN-0051  ', 'SPPL', '2026-03-20', 5, 'aktif'),
('IZN-0018', 'PT-016', NULL, 'UKL-UPL', '20/03/2026', 5, 'AKTIF'),
('IZN-0019', 'PT-017', 'IZN-0054', 'amdal', '2024-11-05', -1, 'Expired'),
('IZN-0020', 'PT-020', 'IZN-0056', 'SPPL', '05-11-2024', NULL, 'Aktif'),
('IZN-0021', 'PT-023', 'IZN-0058 ', 'UKL-UPL', '2025-06-30', 3, NULL),
('IZN-0022', 'PT-024', 'IZN-0060', 'AMDAL', '30/06/2025', 5, 'aktif'),
('IZN-0023', 'PT-029', NULL, 'SPPL', '2026-04-12', 5, 'Aktif'),
('IZN-0024', 'PT-030', 'IZN-0065 ', 'UKL-UPL', '12-04-2026', NULL, 'AKTIF'),
('IZN-0025', 'PT-033', 'IZN-0067', 'amdal', '2025-12-25', 5, 'Expired'),
('IZN-0026', 'PT-040', 'IZN-0070', 'SPPL', '25/12/2025', NULL, 'Aktif'),
('IZN-0027', 'PT-041', 'IZN-0072  ', 'UKL-UPL', '2024-09-17', 3, 'aktif'),
('IZN-0028', 'PT-043', NULL, 'AMDAL', '17-09-2024', 5, 'Expired'),
('IZN-0029', 'PT-049', 'IZN-0078', 'SPPL', '2026-10-05', NULL, 'Aktif'),
('IZN-0030', 'PT-050', 'IZN-0080 ', 'UKL-UPL', '05/10/2026', 5, 'AKTIF'),
('IZN-0031', 'PT-002', 'IZN-0082', 'amdal', '2025-02-14', NULL, 'aktif');

-- =========================================================
-- Table: kualitas_air_sungai (59 rows - KOTOR)
-- =========================================================

DROP TABLE IF EXISTS `kualitas_air_sungai`;
CREATE TABLE `kualitas_air_sungai` (
  `id_sampel` varchar(20) NOT NULL,
  `id_stasiun` varchar(20),
  `nama_sungai` varchar(255),
  `waktu_pengambilan` varchar(100),
  `ph_air` decimal(5,2),
  `bod_mg_l` decimal(8,2),
  `cod_mg_l` varchar(50),
  `tss_mg_l` decimal(8,2),
  `status_mutu` varchar(100),
  PRIMARY KEY (`id_sampel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `kualitas_air_sungai` VALUES
('KA-0001', 'ST-001', 'Sungai Desa Lampanah', '2026-10-05 19:00:00', 7.77, 10.65, '42.61', 51.13, 'Cemar Ringan'),
('KA-0002', 'ST-003', 'Sungai Desa Sabang ', '-15.50', 'invalid', 69.66, 83.59, NULL, 'CEMAR BERAT'),
('KA-0003', 'ST-004', '  Sungai Desa Pante  ', '08-10-2026 23:00', 6.52, 7.81, '31.25', NULL, 'cemar ringan'),
('KA-0004', NULL, 'Sungai Desa Rajabasa', '2026-10-04', 7.09, 16.45, '65.81', 78.97, 'Memenuhi Baku Mutu'),
('KA-0005', 'ST-006', 'Sungai Desa Ujung Kalak ', 'invalid', 12.30, '49.19', 59.03, NULL, 'Valid'),
('KA-0006', 'ST-010', 'Sungai Desa Cot Raya', '2026-10-07 07:00:00', 6.32, 2.02, '8.10', 9.72, ''),
('KA-0007', 'ST-011', '   Sungai Desa Larangan   ', '2026-10-02 14:30:00', 6.95, 8.50, '34.20', 40.60, 'Cemar Ringan'),
('KA-0008', 'ST-013', 'Sungai Desa Labuhan Haji', '03-10-2026', 7.25, 11.20, '45.80', NULL, 'Cemar Ringan'),
('KA-0009', 'ST-014', 'SUNGAI DESA MENANGGAL', '2026-10-01 10:00', -5.30, 'tidak valid', '28.90', 35.10, NULL),
('KA-0010', 'ST-016', 'Sungai Desa Neunom ', '2026-10-06 08:30', 7.42, 9.75, '39.00', 46.50, 'Cemar Ringan'),
('KA-0011', 'ST-017', 'sungai desa muara batu', '08-10-2026', 6.88, 14.30, 'invalid', 71.50, 'Cemar Sedang'),
('KA-0012', 'ST-018', 'Sungai Desa Tanjong Layeu', '2026-10-05 12:00:00', 7.65, 13.80, '55.20', NULL, 'CEMAR RINGAN'),
('KA-0013', 'ST-019', '  Sungai Desa Meulaboh Jaya  ', '05-10-2026 15:30', -8.50, 19.50, '78.00', 92.40, NULL),
('KA-0014', 'ST-020', 'Sungai Desa Muara Dua', '2026-10-04 11:15:00', 7.10, 10.40, '41.60', 49.80, 'Cemar Ringan'),
('KA-0015', NULL, 'Sungai Desa Ujung Lheu ', '04-10-2026', 6.75, 15.90, '63.60', NULL, 'Cemar Sedang'),
('KA-0016', 'ST-023', 'Sungai Desa Meulaboh', '2026-10-03 09:45:00', 7.55, 12.10, '48.40', 57.70, 'cemar ringan'),
('KA-0017', 'ST-024', 'sungai desa ujung kalak ', '03-10-2026 13:20', 6.42, 8.90, '35.60', 42.70, ''),
('KA-0018', 'ST-025', 'Sungai Desa Leubak Bata', '2026-10-02 16:00', 7.32, 11.75, '47.00', NULL, 'Cemar Ringan'),
('KA-0019', 'ST-026', 'SUNGAI DESA PEUNITI', '02-10-2026', 'invalid', 13.20, '52.80', 63.40, 'Cemar Sedang'),
('KA-0020', 'ST-027', 'Sungai Desa Pante Tutue ', '2026-10-01 07:30:00', 7.48, 9.30, '37.20', NULL, 'Valid'),
('KA-0021', 'ST-029', 'sungai desa neunom', '01-10-2026 14:45', 6.65, 7.40, '29.60', 35.50, 'Cemar Ringan'),
('KA-0022', 'ST-030', 'Sungai Desa Punge Blang Cut ', '2026-09-30 10:00:00', 7.58, 10.80, '43.20', 51.80, ''),
('KA-0023', 'ST-036', '  Sungai Desa Samatiga  ', '30-09-2026 12:30', -6.20, 'error', '38.40', NULL, 'CEMAR SEDANG'),
('KA-0024', 'ST-042', 'Sungai Desa Labuhan Haji Barat', '2026-09-29 15:15:00', 7.20, 16.50, '66.00', 79.20, 'Cemar Sedang'),
('KA-0025', NULL, 'sungai desa leubak bata ', '29-09-2026 08:45', 6.85, 12.60, '50.40', NULL, 'Valid'),
('KA-0026', 'ST-045', 'Sungai Desa Acehjaya', '2026-09-28 11:30:00', 7.35, 14.90, '59.60', 71.50, 'Cemar Sedang'),
('KA-0027', 'ST-050', 'SUNGAI DESA MEULABOH ', '28-09-2026 13:50', 'invalid', 10.20, '40.80', 48.90, NULL),
('KA-0028', 'ST-001', 'Sungai Desa Tanjong Layeu ', '2026-09-27 09:00:00', 7.42, 8.70, '34.80', 41.80, 'Cemar Ringan'),
('KA-0029', 'ST-003', 'sungai desa sabang', '27-09-2026 16:20', -12.15, 'nilai negatif', '72.50', NULL, 'Cemar Berat'),
('KA-0030', 'ST-004', 'Sungai Desa Pante Bidok ', '2026-09-26 10:45:00', 6.55, 6.80, '27.20', 32.60, 'Cemar Ringan'),
('KA-0031', 'ST-005', '   Sungai Desa Rajabasa   ', '26-09-2026', 7.12, 15.70, 'invalid', 75.20, ''),
('KA-0032', 'ST-006', 'Sungai Desa Ujung Kalak ', '2026-09-25 14:30:00', 6.92, 9.50, '38.00', NULL, 'Cemar Ringan'),
('KA-0033', NULL, 'Sungai Desa Cot Raya', '25-09-2026 12:00', 7.28, 11.30, '45.20', 54.20, 'Cemar Ringan'),
('KA-0034', 'ST-010', 'SUNGAI DESA COT RAYA ', '2026-09-24 08:15:00', 6.42, 13.60, '54.40', NULL, 'Cemar Sedang'),
('KA-0035', 'ST-011', 'Sungai Desa Larangan', '24-09-2026 11:45', 'error', 7.20, '28.80', 34.60, 'Valid'),
('KA-0036', 'ST-013', 'sungai desa labuhan haji ', '2026-09-23 15:30:00', 7.15, 10.90, '43.60', 52.30, 'Cemar Ringan'),
('KA-0037', 'ST-014', 'Sungai Desa Menanggal ', '23-09-2026 09:00', -4.80, 'tidak ada', '25.60', NULL, ''),
('KA-0038', 'ST-016', '  Sungai Desa Neunom  ', '2026-09-22 13:20:00', 7.38, 8.40, '33.60', 40.30, 'Cemar Ringan'),
('KA-0039', 'ST-017', 'Sungai Desa Muara Batu ', '22-09-2026 10:50', 6.72, 12.80, 'invalid', 64.00, 'Cemar Sedang'),
('KA-0040', 'ST-018', 'SUNGAI DESA TANJONG LAYEU', '2026-09-21 14:45:00', 7.52, 14.70, '58.80', NULL, 'Cemar Sedang'),
('KA-0041', NULL, 'Sungai Desa Meulaboh Jaya', '21-09-2026 11:30', -7.25, '18.20', '72.80', 87.30, 'CEMAR BERAT'),
('KA-0042', 'ST-020', 'sungai desa muara dua ', '2026-09-20 12:00:00', 7.05, 9.80, '39.20', 47.00, ''),
('KA-0043', 'ST-022', 'Sungai Desa Ujung Lheu ', '20-09-2026 15:15', 6.88, 14.40, 'error', NULL, 'Cemar Sedang'),
('KA-0044', 'ST-023', '   Sungai Desa Meulaboh   ', '2026-09-19 10:30:00', 7.45, 11.60, '46.40', 55.70, 'Cemar Ringan'),
('KA-0045', 'ST-024', 'Sungai Desa Ujung Kalak', '19-09-2026 13:45', 6.55, 7.90, '31.60', 37.90, ''),
('KA-0046', 'ST-025', 'SUNGAI DESA LEUBAK BATA ', '2026-09-18 09:00:00', 7.32, 10.30, '41.20', NULL, 'Cemar Ringan'),
('KA-0047', 'ST-026', 'Sungai Desa Peuniti ', '18-09-2026 14:20', 'invalid', 12.70, '50.80', 61.00, 'Cemar Sedang'),
('KA-0048', 'ST-027', 'sungai desa pante tutue', '2026-09-17 11:50:00', 7.25, 8.60, '34.40', 41.30, 'Valid'),
('KA-0049', 'ST-029', 'Sungai Desa Neunom ', '17-09-2026 10:00', 6.92, 6.50, '26.00', NULL, 'Cemar Ringan'),
('KA-0050', 'ST-030', '  Sungai Desa Punge Blang Cut  ', '2026-09-16 15:30:00', 7.62, 11.20, '44.80', 53.80, 'Cemar Ringan'),
('KA-0051', NULL, 'Sungai Desa Samatiga', '16-09-2026 12:15', -9.40, 'negatif error', '37.20', 44.60, ''),
('KA-0052', 'ST-042', 'SUNGAI DESA LABUHAN HAJI BARAT', '2026-09-15 08:45:00', 7.18, 15.80, 'invalid', NULL, 'Cemar Sedang'),
('KA-0053', 'ST-044', 'Sungai Desa Leubak Bata ', '15-09-2026 14:00', 6.78, 13.20, '52.80', 63.40, 'Cemar Sedang'),
('KA-0054', 'ST-045', 'sungai desa acehjaya ', '2026-09-14 10:30:00', 7.48, 9.40, '37.60', NULL, 'Valid'),
('KA-0055', 'ST-050', 'Sungai Desa Meulaboh', '14-09-2026 13:20', 'error', 10.70, '42.80', 51.40, 'Cemar Ringan'),
('KA-0056', 'ST-001', '   Sungai Desa Lampanah   ', '2026-09-13 09:15:00', 7.35, 11.50, '46.00', 55.20, 'Cemar Ringan'),
('KA-0057', 'ST-003', 'Sungai Desa Sabang', '13-09-2026 12:45', -14.25, 'tidak valid', '70.00', NULL, 'Cemar Berat'),
('KA-0058', 'ST-004', 'Sungai Desa Pante Bidok ', '2026-09-12 11:00:00', 6.65, 5.80, '23.20', 27.80, ''),
('KA-0059', 'ST-005', 'SUNGAI DESA RAJABASA ', '12-09-2026 14:30', 7.22, 16.40, 'invalid', 78.50, 'Cemar Sedang');

-- =========================================================
-- Table: kualitas_udara (55 rows - KOTOR)
-- =========================================================

DROP TABLE IF EXISTS `kualitas_udara`;
CREATE TABLE `kualitas_udara` (
  `id_record` varchar(20) NOT NULL,
  `id_stasiun` varchar(20),
  `waktu_pengukuran` varchar(100),
  `pm10` decimal(8,2),
  `so2` decimal(8,2),
  `co` decimal(8,2),
  `o3` decimal(8,2),
  `no2` decimal(8,2),
  `kategori_ispu` varchar(100),
  PRIMARY KEY (`id_record`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `kualitas_udara` VALUES
('KU-0001', 'ST-001', '2026-10-07 17:00:00', 47.82, 19.13, '23.91', 28.69, 9.56, 'Baik'),
('KU-0002', 'ST-003', '2026-10-03 16:00', 999.99, 27.56, 34.45, 41.35, NULL, 'SANGAT BURUK'),
('KU-0003', 'ST-004', '03-10-2026', 82.60, 'invalid', '41.30', 49.56, 16.52, 'Sedang'),
('KU-0004', 'ST-005', '2026-10-04 08:00:00', -50.00, 33.04, '41.30', 49.56, NULL, 'Unknown'),
('KU-0005', NULL, '2026-10-06 07:00', 41.29, 16.52, '20.64', 24.77, 8.26, 'BAIK'),
('KU-0006', 'ST-010', '2026-10-05', 96.16, 38.46, '48.08', 57.70, 19.23, ''),
('KU-0007', 'ST-011', '05-10-2026 09:30', 55.44, 22.18, '27.72', 33.26, 11.09, 'Sedang'),
('KU-0008', 'ST-013', '2026-10-02 14:45:00', 68.70, 27.48, '34.35', 41.22, NULL, 'Sedang'),
('KU-0009', 'ST-014', '02-10-2026 11:00', 'error', 'tidak valid', '28.50', 34.20, 11.40, ''),
('KU-0010', 'ST-016', '2026-10-01 10:15:00', 35.91, 14.36, '17.95', 21.55, 7.18, 'Baik'),
('KU-0011', NULL, '01-10-2026 15:30', -75.50, 31.20, 'negative', 37.45, 12.48, 'Buruk'),
('KU-0012', 'ST-018', '2026-09-30 08:45:00', 89.34, 35.74, '44.67', 53.60, 17.87, 'Sedang'),
('KU-0013', 'ST-019', '30-09-2026 13:20', 102.50, 41.00, 'invalid', 61.50, NULL, 'Buruk'),
('KU-0014', 'ST-020', '2026-09-29 12:00:00', 45.67, 18.27, '22.84', 27.40, 9.13, 'Baik'),
('KU-0015', 'ST-022', '29-09-2026 16:50', -65.20, 'error', '32.60', 39.12, 13.04, ''),
('KU-0016', 'ST-023', '2026-09-28 09:30:00', 58.92, 23.57, '29.46', 35.35, 11.79, 'Sedang'),
('KU-0017', 'ST-024', '28-09-2026 14:15', 76.20, 30.48, '38.10', 45.72, NULL, 'Sedang'),
('KU-0018', 'ST-025', '2026-09-27 11:45:00', 52.08, 20.83, '26.04', 31.25, 10.42, 'Sedang'),
('KU-0019', 'ST-026', '27-09-2026 10:00', 'invalid', 25.60, '32.00', 38.40, 12.80, 'Buruk'),
('KU-0020', 'ST-027', '2026-09-26 15:20:00', 39.85, 15.94, '19.93', 23.92, 7.97, 'Baik'),
('KU-0021', NULL, '26-09-2026 12:30', -88.75, 'tidak ada', '44.38', 53.25, 17.75, ''),
('KU-0022', 'ST-030', '2026-09-25 08:00:00', 64.68, 25.87, '32.34', 38.81, 12.94, 'Sedang'),
('KU-0023', 'ST-036', '25-09-2026 13:45', 95.40, 38.16, 'error', NULL, 19.08, 'Buruk'),
('KU-0024', 'ST-042', '2026-09-24 10:30:00', 48.96, 19.58, '24.48', 29.38, 9.79, 'Baik'),
('KU-0025', 'ST-044', '24-09-2026 14:00', -55.30, 22.12, '27.65', 33.18, 11.06, 'Unknown'),
('KU-0026', 'ST-045', '2026-09-23 11:15:00', 71.82, 28.73, '35.91', 43.09, 14.36, 'Sedang'),
('KU-0027', 'ST-050', '23-09-2026 15:40', 'nilai invalid', 'tidak valid', '40.50', 48.60, NULL, ''),
('KU-0028', 'ST-001', '2026-09-22 09:50:00', 57.30, 22.92, '28.65', 34.38, 11.46, 'Sedang'),
('KU-0029', 'ST-003', '22-09-2026 12:20', -92.15, 36.86, '46.08', 55.29, 18.43, 'Buruk'),
('KU-0030', 'ST-004', '2026-09-21 10:00:00', 83.50, 33.40, '41.75', NULL, 16.70, 'Sedang'),
('KU-0031', 'ST-005', '21-09-2026 14:30', 'error', 29.60, '37.00', 44.40, 14.80, 'Buruk'),
('KU-0032', 'ST-006', '2026-09-20 11:45:00', 42.36, 16.94, '21.18', 25.42, 8.48, 'Baik'),
('KU-0033', NULL, '20-09-2026 15:00', -45.90, 'tidak ada', '22.95', 27.54, 9.18, ''),
('KU-0034', 'ST-011', '2026-09-19 08:30:00', 74.52, 29.81, '37.26', 44.71, 14.90, 'Sedang'),
('KU-0035', 'ST-013', '19-09-2026 13:15', 61.98, 24.79, 'invalid', 37.18, NULL, 'Sedang'),
('KU-0036', 'ST-014', '2026-09-18 10:45:00', 51.30, 20.52, '25.65', 30.78, 10.26, 'Sedang'),
('KU-0037', 'ST-016', '18-09-2026 14:50', -78.60, 'error', '39.30', 47.16, 15.72, 'Unknown'),
('KU-0038', 'ST-017', '2026-09-17 11:20:00', 87.66, 35.06, '43.83', 52.60, 17.53, 'Sedang'),
('KU-0039', 'ST-018', '17-09-2026 15:35', 'nilai tidak valid', 32.40, '40.50', NULL, 13.50, ''),
('KU-0040', 'ST-019', '2026-09-16 09:00:00', 49.62, 19.85, '24.81', 29.77, 9.92, 'Baik'),
('KU-0041', NULL, '16-09-2026 12:40', -70.25, 28.10, '35.13', 42.15, 14.05, 'Buruk'),
('KU-0042', 'ST-020', '2026-09-15 10:15:00', 66.48, 26.59, '33.24', 39.89, 13.30, 'Sedang'),
('KU-0043', 'ST-022', '15-09-2026 13:50', 81.90, 32.76, 'error', 49.14, NULL, 'Sedang'),
('KU-0044', 'ST-023', '2026-09-14 11:30:00', 53.76, 21.50, '26.88', 32.26, 10.75, 'Sedang'),
('KU-0045', 'ST-024', '14-09-2026 15:15', 'invalid', 'tidak ada', '30.40', 36.48, 12.16, ''),
('KU-0046', 'ST-025', '2026-09-13 08:45:00', 72.00, 28.80, '36.00', 43.20, 14.40, 'Sedang'),
('KU-0047', 'ST-026', '13-09-2026 14:20', -63.50, 25.40, '31.75', 38.10, 12.70, 'Unknown'),
('KU-0048', 'ST-027', '2026-09-12 10:50:00', 46.44, 18.58, '23.22', 27.86, 9.29, 'Baik'),
('KU-0049', 'ST-029', '12-09-2026 13:30', 'error', 20.80, '26.00', 31.20, NULL, 'Sedang'),
('KU-0050', 'ST-030', '2026-09-11 12:00:00', 79.08, 31.63, '39.54', 47.45, 15.81, 'Sedang'),
('KU-0051', 'ST-036', '11-09-2026 15:45', -98.20, 'nilai tidak valid', '49.10', 58.92, 19.64, ''),
('KU-0052', 'ST-042', '2026-09-10 09:30:00', 59.04, 23.62, '29.52', 35.42, 11.81, 'Sedang'),
('KU-0053', NULL, '10-09-2026 14:00', 88.30, 35.32, 'invalid', NULL, 17.66, 'Buruk'),
('KU-0054', 'ST-045', '2026-09-09 11:15:00', 67.50, 27.00, '33.75', 40.50, 13.50, 'Sedang'),
('KU-0055', 'ST-050', '09-09-2026 10:30', -45.75, 'error', '22.88', 27.45, 9.15, 'Unknown');

-- =========================================================
-- Table: timbulan_sampah (60 rows - KOTOR)
-- =========================================================

DROP TABLE IF EXISTS `timbulan_sampah`;
CREATE TABLE `timbulan_sampah` (
  `id_laporan` varchar(20) NOT NULL,
  `id_fasilitas` varchar(20),
  `tanggal_lapor` varchar(50),
  `volume_masuk_ton` varchar(50),
  `jenis_sampah_dominan` varchar(100),
  `sumber_sistem` varchar(100),
  PRIMARY KEY (`id_laporan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `timbulan_sampah` VALUES
('TS-0001', 'FAS-002', '2026-10-05', '173.24', 'Campuran', 'Sistem Terpadu DLHK'),
('TS-0002', 'FAS-005', '05-10-2026', '265.89', 'plastik', 'Sistem Terpadu DLHK'),
('TS-0003', 'FAS-008', '2026-10-03', '-500.00', 'Campuran', 'Manual'),
('TS-0004', 'FAS-009', '2026-10-08', 'invalid', 'PLASTIK', 'Sistem Terpadu DLHK'),
('TS-0005', NULL, '2026-10-02', '103.30', 'Plastik', NULL),
('TS-0006', 'FAS-014', '08-10-2026', '  120.50  ', 'Organik', 'Sistem Terpadu DLHK'),
('TS-0007', 'FAS-015', '2026-10-01', '89.75', 'kertas', 'Manual'),
('TS-0008', 'FAS-016', '01-10-2026', 'error', 'KERTAS', 'Sistem Terpadu DLHK'),
('TS-0009', 'FAS-018', '2026-09-30 14:30', '145.20', 'Campuran', NULL),
('TS-0010', 'FAS-019', '30-09-2026', '98.60  ', 'plastik', 'Sistem Terpadu DLHK'),
('TS-0011', 'FAS-020', '2026-09-29', -125.45, 'Organik', 'Manual'),
('TS-0012', 'FAS-021', '29-09-2026', '234.80', 'CAMPURAN', ''),
('TS-0013', NULL, '2026-09-28', '156.70', 'Kertas', 'Sistem Terpadu DLHK'),
('TS-0014', 'FAS-023', '28-09-2026', 'tidak ada', 'plastik', 'Manual'),
('TS-0015', 'FAS-026', '2026-09-27', '203.50', 'ORGANIK', 'Sistem Terpadu DLHK'),
('TS-0016', 'FAS-028', '27-09-2026', '187.30 ', 'Campuran', NULL),
('TS-0017', 'FAS-029', '2026-09-26', 'invalid', 'kertas', 'Manual'),
('TS-0018', 'FAS-032', '26-09-2026', '142.90', 'plastik', 'Sistem Terpadu DLHK'),
('TS-0019', 'FAS-034', '2026-09-25 11:00', '119.40', 'CAMPURAN', ''),
('TS-0020', 'FAS-037', '25-09-2026', -95.75, 'Organik', 'Sistem Terpadu DLHK'),
('TS-0021', 'FAS-039', '2026-09-24', '177.60', 'kertas', 'Manual'),
('TS-0022', 'FAS-040', '24-09-2026', '  208.45  ', 'PLASTIK', 'Sistem Terpadu DLHK'),
('TS-0023', 'FAS-002', '2026-09-23', 'error', 'Campuran', NULL),
('TS-0024', 'FAS-005', '23-09-2026', '251.80', 'organik', 'Manual'),
('TS-0025', NULL, '2026-09-22', '164.90', 'Kertas', 'Sistem Terpadu DLHK'),
('TS-0026', 'FAS-009', '22-09-2026', '-158.30', 'CAMPURAN', ''),
('TS-0027', 'FAS-012', '2026-09-21', '193.25', 'plastik', 'Sistem Terpadu DLHK'),
('TS-0028', 'FAS-014', '21-09-2026', 'nilai tidak valid', 'kertas', 'Manual'),
('TS-0029', 'FAS-015', '2026-09-20', '127.55', 'ORGANIK', 'Sistem Terpadu DLHK'),
('TS-0030', 'FAS-016', '20-09-2026', '216.70 ', 'Campuran', NULL),
('TS-0031', 'FAS-018', '2026-09-19', 'invalid', 'plastik', 'Manual'),
('TS-0032', 'FAS-019', '19-09-2026', '174.40', 'kertas', 'Sistem Terpadu DLHK'),
('TS-0033', 'FAS-020', '2026-09-18 09:15', '105.60', 'CAMPURAN', ''),
('TS-0034', NULL, '18-09-2026', -142.85, 'Organik', 'Sistem Terpadu DLHK'),
('TS-0035', 'FAS-023', '2026-09-17', '198.30', 'plastik', 'Manual'),
('TS-0036', 'FAS-026', '17-09-2026', '  265.15  ', 'kertas', 'Sistem Terpadu DLHK'),
('TS-0037', 'FAS-028', '2026-09-16', 'error', 'CAMPURAN', NULL),
('TS-0038', 'FAS-029', '16-09-2026', '182.60', 'organik', 'Manual'),
('TS-0039', 'FAS-032', '2026-09-15', '224.80', 'Plastik', 'Sistem Terpadu DLHK'),
('TS-0040', 'FAS-034', '15-09-2026', 'tidak valid', 'kertas', ''),
('TS-0041', 'FAS-037', '2026-09-14', '147.25', 'CAMPURAN', 'Sistem Terpadu DLHK'),
('TS-0042', 'FAS-039', '14-09-2026', '196.70 ', 'Organik', 'Manual'),
('TS-0043', NULL, '2026-09-13', -173.40, 'Plastik', 'Sistem Terpadu DLHK'),
('TS-0044', 'FAS-040', '13-09-2026', '138.50', 'KERTAS', ''),
('TS-0045', 'FAS-002', '2026-09-12', 'invalid', 'Campuran', 'Manual'),
('TS-0046', 'FAS-005', '12-09-2026', '192.70', 'organik', 'Sistem Terpadu DLHK'),
('TS-0047', 'FAS-008', '2026-09-11', '155.85', 'Plastik', 'Sistem Terpadu DLHK'),
('TS-0048', 'FAS-009', '11-09-2026', 'nilai tidak ada', 'kertas', NULL),
('TS-0049', 'FAS-012', '2026-09-10', '218.40', 'CAMPURAN', 'Manual'),
('TS-0050', 'FAS-014', '10-09-2026', '  127.30  ', 'organik', 'Sistem Terpadu DLHK'),
('TS-0051', 'FAS-015', '2026-09-09', -189.60, 'Plastik', ''),
('TS-0052', 'FAS-016', '09-09-2026', '243.75', 'KERTAS', 'Sistem Terpadu DLHK'),
('TS-0053', NULL, '2026-09-08', 'error', 'Campuran', 'Manual'),
('TS-0054', 'FAS-018', '08-09-2026', '161.20', 'organik', 'Sistem Terpadu DLHK'),
('TS-0055', 'FAS-019', '2026-09-07', '204.80', 'Plastik', 'Sistem Terpadu DLHK'),
('TS-0056', 'FAS-020', '07-09-2026', 'tidak valid', 'kertas', NULL),
('TS-0057', 'FAS-021', '2026-09-06', '175.45', 'CAMPURAN', 'Manual'),
('TS-0058', 'FAS-023', '06-09-2026', '  149.30  ', 'organik', 'Sistem Terpadu DLHK'),
('TS-0059', 'FAS-026', '2026-09-05', -167.90, 'Plastik', ''),
('TS-0060', 'FAS-028', '05-09-2026', 'nilai error', 'kertas', 'Sistem Terpadu DLHK');

-- =========================================================
-- Table: tutupan_lahan_rth (44 rows - KOTOR)
-- =========================================================

DROP TABLE IF EXISTS `tutupan_lahan_rth`;
CREATE TABLE `tutupan_lahan_rth` (
  `id_polygon` varchar(20) NOT NULL,
  `id_desa` varchar(10),
  `jenis_tutupan` varchar(100),
  `luas_hektar` varchar(50),
  `sumber_citra` varchar(100),
  `tanggal_citra` varchar(50),
  PRIMARY KEY (`id_polygon`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `tutupan_lahan_rth` VALUES
('RTH-0001', '01011', 'Hutan Lindung', '36.18', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0002', '01012', 'PERKEBUNAN', '451.18', 'Citra Satelit Sentinel-2', '01-01-2026'),
('RTH-0003', '01013', 'hutan lindung', '-438.04', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0004', '07014', '', '71.37', 'Citra Satelit Sentinel-2', NULL),
('RTH-0005', '09071', 'Taman Nasional', 'invalid', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0006', '07111', 'RTH Kota', '37.80  ', 'Citra Satelit Sentinel', '01/01/2026'),
('RTH-0007', '05011', 'Sawah', '  289.50  ', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0008', '04011', 'kebun', '156.30', 'Citra Satelit Landsat 8', '01-01-2026'),
('RTH-0009', '08022', 'Hutan Alam', '-285.60', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0010', '02012', 'PERKEBUNAN', 'tidak ada', 'Citra Satelit Sentinel-2', NULL),
('RTH-0011', '01041', 'RTH Kota', '43.25', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0012', '03021', 'hutan produksi', '  327.80  ', 'Citra Satelit Landsat 8', '01-01-2026'),
('RTH-0013', '05031', 'Taman Nasional', 'error', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0014', '07052', 'Sawah', '512.40', 'Citra Satelit Sentinel', NULL),
('RTH-0015', '09022', 'KEBUN', -198.75, 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0016', '01051', 'Hutan Lindung', '  89.60  ', 'Citra Satelit Landsat 8', '01-01-2026'),
('RTH-0017', '06021', 'hutan alam', 'nilai tidak valid', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0018', '08012', 'Perkebunan', '276.30', 'Citra Satelit Sentinel-2', '01-01-2026'),
('RTH-0019', '04031', 'RTH Kota', '-412.50  ', 'Citra Satelit Sentinel', '2026-01-01'),
('RTH-0020', '02021', 'Taman Nasional', 'invalid', 'Citra Satelit Sentinel-2', NULL),
('RTH-0021', '01021', 'Sawah', '421.85', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0022', '05012', 'KEBUN', '  158.70  ', 'Citra Satelit Landsat 8', '01-01-2026'),
('RTH-0023', '07082', 'hutan produksi', 'error', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0024', '09041', 'Hutan Alam', '503.60', 'Citra Satelit Sentinel', 'NULL'),
('RTH-0025', '03011', 'RTH Kota', '-256.40', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0026', '06012', 'Perkebunan', '  378.90  ', 'Citra Satelit Landsat 8', NULL),
('RTH-0027', '08041', 'Sawah', 'tidak valid', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0028', '01023', 'HUTAN LINDUNG', '324.15', 'Citra Satelit Sentinel-2', '01-01-2026'),
('RTH-0029', '04022', 'hutan alam', '-189.30', 'Citra Satelit Sentinel', '2026-01-01'),
('RTH-0030', '07041', 'Taman Nasional', 'invalid', 'Citra Satelit Sentinel-2', '01-01-2026'),
('RTH-0031', '09061', 'RTH Kota', '  445.75  ', 'Citra Satelit Landsat 8', '2026-01-01'),
('RTH-0032', '02022', 'Kebun', 'error', 'Citra Satelit Sentinel-2', NULL),
('RTH-0033', '05051', 'Sawah', '267.40', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0034', '08032', 'HUTAN ALAM', -334.20, 'Citra Satelit Landsat 8', '01-01-2026'),
('RTH-0035', '07031', 'Perkebunan', 'nilai tidak ada', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0036', '03022', 'hutan produksi', '  392.60  ', 'Citra Satelit Sentinel', NULL),
('RTH-0037', '04012', 'Hutan Lindung', 'invalid', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0038', '01031', 'RTH Kota', '195.85', 'Citra Satelit Sentinel-2', '01-01-2026'),
('RTH-0039', '06031', 'Taman Nasional', '-478.50', 'Citra Satelit Landsat 8', '2026-01-01'),
('RTH-0040', '07062', 'Sawah', '  283.40  ', 'Citra Satelit Sentinel-2', '01-01-2026'),
('RTH-0041', '09012', 'KEBUN', 'error', 'Citra Satelit Sentinel', '2026-01-01'),
('RTH-0042', '05021', 'hutan alam', '156.75', 'Citra Satelit Sentinel-2', NULL),
('RTH-0043', '08042', 'Perkebunan', 'tidak valid', 'Citra Satelit Sentinel-2', '2026-01-01'),
('RTH-0044', '01062', 'Hutan Produksi', '  418.90  ', 'Citra Satelit Landsat 8', '01-01-2026');

-- =========================================================
-- Foreign Key Constraints (diterapkan setelah data load untuk menghindari error pada data kotor)
-- =========================================================

-- master_fasilitas_sampah -> master_wilayah
ALTER TABLE `master_fasilitas_sampah`
ADD CONSTRAINT `fk_fasilitas_wilayah`
FOREIGN KEY (`id_desa`) REFERENCES `master_wilayah` (`id_desa`)
ON DELETE SET NULL ON UPDATE CASCADE;

-- master_perusahaan -> master_wilayah
ALTER TABLE `master_perusahaan`
ADD CONSTRAINT `fk_perusahaan_wilayah`
FOREIGN KEY (`id_desa`) REFERENCES `master_wilayah` (`id_desa`)
ON DELETE SET NULL ON UPDATE CASCADE;

-- master_stasiun_pantau -> master_wilayah
ALTER TABLE `master_stasiun_pantau`
ADD CONSTRAINT `fk_stasiun_wilayah`
FOREIGN KEY (`id_desa`) REFERENCES `master_wilayah` (`id_desa`)
ON DELETE SET NULL ON UPDATE CASCADE;

-- izin_lingkungan -> master_perusahaan
ALTER TABLE `izin_lingkungan`
ADD CONSTRAINT `fk_izin_perusahaan`
FOREIGN KEY (`id_perusahaan`) REFERENCES `master_perusahaan` (`id_perusahaan`)
ON DELETE CASCADE ON UPDATE CASCADE;

-- kualitas_air_sungai -> master_stasiun_pantau
ALTER TABLE `kualitas_air_sungai`
ADD CONSTRAINT `fk_kualitas_air_stasiun`
FOREIGN KEY (`id_stasiun`) REFERENCES `master_stasiun_pantau` (`id_stasiun`)
ON DELETE SET NULL ON UPDATE CASCADE;

-- kualitas_udara -> master_stasiun_pantau
ALTER TABLE `kualitas_udara`
ADD CONSTRAINT `fk_kualitas_udara_stasiun`
FOREIGN KEY (`id_stasiun`) REFERENCES `master_stasiun_pantau` (`id_stasiun`)
ON DELETE SET NULL ON UPDATE CASCADE;

-- timbulan_sampah -> master_fasilitas_sampah
ALTER TABLE `timbulan_sampah`
ADD CONSTRAINT `fk_timbulan_fasilitas`
FOREIGN KEY (`id_fasilitas`) REFERENCES `master_fasilitas_sampah` (`id_fasilitas`)
ON DELETE SET NULL ON UPDATE CASCADE;

-- tutupan_lahan_rth -> master_wilayah
ALTER TABLE `tutupan_lahan_rth`
ADD CONSTRAINT `fk_rth_wilayah`
FOREIGN KEY (`id_desa`) REFERENCES `master_wilayah` (`id_desa`)
ON DELETE SET NULL ON UPDATE CASCADE;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
