-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 07, 2026 at 02:51 AM
-- Server version: 8.0.30
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_dukcapil`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_agama`
--

CREATE TABLE `tb_agama` (
  `id_agama` char(1) NOT NULL,
  `nama_agama` varchar(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_agama`
--

INSERT INTO `tb_agama` (`id_agama`, `nama_agama`) VALUES
('1', 'Islam'),
('2', 'Kristen'),
('3', 'Katolik'),
('4', 'Hindu'),
('5', 'Buddha'),
('6', 'Konghucu');

-- --------------------------------------------------------

--
-- Table structure for table `tb_alamat`
--

CREATE TABLE `tb_alamat` (
  `id_alamat` char(5) NOT NULL,
  `id_desa` char(5) NOT NULL,
  `jalan` text,
  `kode_pos` char(5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_alamat`
--

INSERT INTO `tb_alamat` (`id_alamat`, `id_desa`, `jalan`, `kode_pos`) VALUES
('00001', '01011', 'Jalan Peuniti No. 123', '23111'),
('00002', '01012', 'Jalan Punge Blang Cut No. 45', '23112'),
('00003', '01013', 'Jalan Lampriet No. 67', '23113'),
('00004', '01014', 'Jalan Larangan No. 89', '23114'),
('00005', '01015', 'Jalan Rangkayo No. 101', '23115'),
('00006', '01021', 'Jalan Lam U No. 112', '23121'),
('00007', '01022', 'Jalan Cot Kala No. 134', '23122'),
('00008', '01023', 'Jalan Pasa Baru No. 156', '23123'),
('00009', '01031', 'Jalan Pocut Baren No. 178', '23131'),
('00010', '01032', 'Jalan Kuala No. 190', '23132'),
('00011', '01041', 'Jalan Rajabasa No. 101', '23141'),
('00012', '01042', 'Jalan Pante Kulu No. 202', '23142'),
('00013', '01051', 'Jalan Alue Naga No. 213', '23151'),
('00014', '01052', 'Jalan Deah Raya No. 224', '23152'),
('00015', '01061', 'Jalan Gompong No. 235', '23161'),
('00016', '01062', 'Jalan Batoh No. 246', '23162'),
('00017', '02011', 'Jalan Pulo Aceh No. 257', '23211'),
('00018', '02012', 'Jalan Sabang Kota No. 268', '23212'),
('00019', '02021', 'Jalan Iboih No. 279', '23221'),
('00020', '02022', 'Jalan Teupin Layeu No. 280', '23222'),
('00021', '03011', 'Jalan Blang Jurong No. 291', '24311'),
('00022', '03012', 'Jalan Arun Lama No. 302', '24312'),
('00023', '03021', 'Jalan Langsa Lama No. 313', '24321'),
('00024', '03022', 'Jalan Giok No. 324', '24322'),
('00025', '04011', 'Jalan Muara Batu No. 335', '24411'),
('00026', '04012', 'Jalan Cot Mangga No. 346', '24412'),
('00027', '04021', 'Jalan Muara Dua No. 357', '24421'),
('00028', '04022', 'Jalan Kuala Marah No. 368', '24422'),
('00029', '04031', 'Jalan Blang Mangat No. 379', '24431'),
('00030', '04032', 'Jalan Pante Bidok No. 380', '24432'),
('00031', '05011', 'Jalan Meulaboh No. 391', '25611'),
('00032', '05012', 'Jalan Ujung Kalak No. 402', '25612'),
('00033', '05021', 'Jalan Johan Pahlawan No. 413', '25621'),
('00034', '05022', 'Jalan Saree No. 424', '25622'),
('00035', '05031', 'Jalan Samatiga No. 435', '25631'),
('00036', '05032', 'Jalan Alue Ie No. 446', '25632'),
('00037', '05041', 'Jalan Arongan No. 457', '25641'),
('00038', '05042', 'Jalan Lambalek No. 468', '25642'),
('00039', '05051', 'Jalan Bubon No. 479', '25651'),
('00040', '05052', 'Jalan Pante Tutue No. 480', '25652'),
('00041', '05061', 'Jalan Pantai Cerah No. 491', '25661'),
('00042', '05062', 'Jalan Kuala Merah No. 502', '25662'),
('00043', '07011', 'Jalan Lhoknga No. 513', '23611'),
('00044', '07012', 'Jalan Beutong No. 524', '23612'),
('00045', '07013', 'Jalan Leubak Bata No. 535', '23613'),
('00046', '07014', 'Jalan Meulaboh Jaya No. 546', '23614'),
('00047', '07021', 'Jalan Leupuet No. 557', '23621'),
('00048', '07022', 'Jalan Lampanah No. 568', '23622'),
('00049', '07023', 'Jalan Ueubeulo No. 579', '23623'),
('00050', '07031', 'Jalan Darul Imarah No. 580', '23631'),
('00051', '07032', 'Jalan Mekar Tanjung No. 591', '23632'),
('00052', '07041', 'Jalan Lhoong No. 602', '23641'),
('00053', '07042', 'Jalan Cot Garpet No. 613', '23642'),
('00054', '07051', 'Jalan Baitussalam No. 624', '23651'),
('00055', '07052', 'Jalan Neunom No. 635', '23652'),
('00056', '07061', 'Jalan Lhowe No. 646', '23661'),
('00057', '07062', 'Jalan Cot Raya No. 657', '23662'),
('00058', '07071', 'Jalan Ulim No. 668', '23671'),
('00059', '07072', 'Jalan Jaro No. 679', '23672'),
('00060', '07081', 'Jalan Montasik No. 680', '23681'),
('00061', '07082', 'Jalan Pante Pandeu No. 691', '23682'),
('00062', '07091', 'Jalan Mesjid Raya No. 702', '23691'),
('00063', '07092', 'Jalan Cot Tabe No. 713', '23692'),
('00064', '07101', 'Jalan Lheuh No. 724', '23701'),
('00065', '07102', 'Jalan Lhee No. 735', '23702'),
('00066', '07111', 'Jalan Peukan Bada No. 746', '23711'),
('00067', '07112', 'Jalan Neunyeu No. 757', '23712'),
('00068', '07121', 'Jalan Lhoktai No. 768', '23721'),
('00069', '07122', 'Jalan Banda Raya No. 779', '23722'),
('00070', '08011', 'Jalan Seulimeum No. 780', '23811'),
('00071', '08012', 'Jalan Panggang No. 791', '23812'),
('00072', '08021', 'Jalan Acehjaya No. 802', '23821'),
('00073', '08022', 'Jalan Cot Gajah No. 813', '23822'),
('00074', '08031', 'Jalan Jaya No. 824', '23831'),
('00075', '08032', 'Jalan Meulaboh Baru No. 835', '23832'),
('00076', '08041', 'Jalan Teunom No. 846', '23841'),
('00077', '08042', 'Jalan Ilie No. 857', '23842'),
('00078', '09011', 'Jalan Tapaktuan No. 868', '23711'),
('00079', '09012', 'Jalan Ujung No. 879', '23712'),
('00080', '09021', 'Jalan Bakongan No. 880', '23721'),
('00081', '09022', 'Jalan Menanggal No. 891', '23722'),
('00082', '09031', 'Jalan Labuhan Haji No. 902', '23731'),
('00083', '09032', 'Jalan Labuhan Haji Barat No. 913', '23732'),
('00084', '09041', 'Jalan Tanjong Layeu No. 924', '23741'),
('00085', '09042', 'Jalan Ujung Lheu No. 935', '23742'),
('00086', '09051', 'Jalan Sama Dua No. 946', '23751'),
('00087', '09052', 'Jalan Payakumbuh No. 957', '23752'),
('00088', '09061', 'Jalan Kota Baharu No. 968', '23761'),
('00089', '09062', 'Jalan Sebrang No. 979', '23762'),
('00090', '09071', 'Jalan Manggeng No. 980', '23771'),
('00091', '09072', 'Jalan Batu Raja No. 991', '23772'),
('00092', '10011', 'Jalan Singkil No. 1002', '24781'),
('00093', '10012', 'Jalan Bakongan Timur No. 1013', '24782'),
('00094', '10021', 'Jalan Pulau Banyak No. 1024', '24791'),
('00095', '10022', 'Jalan Tuangku No. 1035', '24792'),
('00096', '11011', 'Jalan Kuta Makmur No. 1046', '24571'),
('00097', '11021', 'Jalan Kuala Simpang No. 1057', '24581'),
('00098', '12011', 'Jalan Takengon No. 1068', '24512'),
('00099', '13011', 'Jalan Idi Rayeuk No. 1079', '24711'),
('00100', '14011', 'Jalan Lhoksukon No. 1080', '24382');

-- --------------------------------------------------------

--
-- Table structure for table `tb_desa`
--

CREATE TABLE `tb_desa` (
  `id_desa` char(5) NOT NULL,
  `id_kecamatan` char(4) NOT NULL,
  `nama_desa` varchar(35) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_desa`
--

INSERT INTO `tb_desa` (`id_desa`, `id_kecamatan`, `nama_desa`) VALUES
('01011', '0101', 'Desa Peuniti'),
('01012', '0101', 'Desa Punge Blang Cut'),
('01013', '0101', 'Desa Lampriet'),
('01014', '0101', 'Desa Larangan'),
('01015', '0101', 'Desa Rangkayo'),
('01021', '0102', 'Desa Lam U'),
('01022', '0102', 'Desa Cot Kala'),
('01023', '0102', 'Desa Pasa Baru'),
('01031', '0103', 'Desa Pocut Baren'),
('01032', '0103', 'Desa Kuala'),
('01041', '0104', 'Desa Rajabasa'),
('01042', '0104', 'Desa Pante Kulu'),
('01051', '0105', 'Desa Alue Naga'),
('01052', '0105', 'Desa Deah Raya'),
('01061', '0106', 'Desa Gompong'),
('01062', '0106', 'Desa Batoh'),
('02011', '0201', 'Desa Pulo Aceh'),
('02012', '0201', 'Desa Sabang Kota'),
('02021', '0202', 'Desa Iboih'),
('02022', '0202', 'Desa Teupin Layeu'),
('03011', '0301', 'Desa Blang Jurong'),
('03012', '0301', 'Desa Arun Lama'),
('03021', '0302', 'Desa Langsa Lama'),
('03022', '0302', 'Desa Giok'),
('04011', '0401', 'Desa Muara Batu'),
('04012', '0401', 'Desa Cot Mangga'),
('04021', '0402', 'Desa Muara Dua'),
('04022', '0402', 'Desa Kuala Marah'),
('04031', '0403', 'Desa Blang Mangat'),
('04032', '0403', 'Desa Pante Bidok'),
('05011', '0501', 'Desa Meulaboh'),
('05012', '0501', 'Desa Ujung Kalak'),
('05021', '0502', 'Desa Johan Pahlawan'),
('05022', '0502', 'Desa Saree'),
('05031', '0503', 'Desa Samatiga'),
('05032', '0503', 'Desa Alue Ie'),
('05041', '0504', 'Desa Arongan'),
('05042', '0504', 'Desa Lambalek'),
('05051', '0505', 'Desa Bubon'),
('05052', '0505', 'Desa Pante Tutue'),
('05061', '0506', 'Desa Pantai Cerah'),
('05062', '0506', 'Desa Kuala Merah'),
('07011', '0701', 'Desa Lhoknga'),
('07012', '0701', 'Desa Beutong'),
('07013', '0701', 'Desa Leubak Bata'),
('07014', '0701', 'Desa Meulaboh Jaya'),
('07021', '0702', 'Desa Leupuet'),
('07022', '0702', 'Desa Lampanah'),
('07023', '0702', 'Desa Ueubeulo'),
('07031', '0703', 'Desa Darul Imarah'),
('07032', '0703', 'Desa Mekar Tanjung'),
('07041', '0704', 'Desa Lhoong'),
('07042', '0704', 'Desa Cot Garpet'),
('07051', '0705', 'Desa Baitussalam'),
('07052', '0705', 'Desa Neunom'),
('07061', '0706', 'Desa Lhowe'),
('07062', '0706', 'Desa Cot Raya'),
('07071', '0707', 'Desa Ulim'),
('07072', '0707', 'Desa Jaro'),
('07081', '0708', 'Desa Montasik'),
('07082', '0708', 'Desa Pante Pandeu'),
('07091', '0709', 'Desa Mesjid Raya'),
('07092', '0709', 'Desa Cot Tabe'),
('07101', '0710', 'Desa Lheuh'),
('07102', '0710', 'Desa Lhee'),
('07111', '0711', 'Desa Peukan Bada'),
('07112', '0711', 'Desa Neunyeu'),
('07121', '0712', 'Desa Lhoktai'),
('07122', '0712', 'Desa Banda Raya'),
('08011', '0801', 'Desa Seulimeum'),
('08012', '0801', 'Desa Panggang'),
('08021', '0802', 'Desa Acehjaya'),
('08022', '0802', 'Desa Cot Gajah'),
('08031', '0803', 'Desa Jaya'),
('08032', '0803', 'Desa Meulaboh Baru'),
('08041', '0804', 'Desa Teunom'),
('08042', '0804', 'Desa Ilie'),
('09011', '0901', 'Desa Tapaktuan'),
('09012', '0901', 'Desa Ujung'),
('09021', '0902', 'Desa Bakongan'),
('09022', '0902', 'Desa Menanggal'),
('09031', '0903', 'Desa Labuhan Haji'),
('09032', '0903', 'Desa Labuhan Haji Barat'),
('09041', '0904', 'Desa Tanjong Layeu'),
('09042', '0904', 'Desa Ujung Lheu'),
('09051', '0905', 'Desa Sama Dua'),
('09052', '0905', 'Desa Payakumbuh'),
('09061', '0906', 'Desa Kota Baharu'),
('09062', '0906', 'Desa Sebrang'),
('09071', '0907', 'Desa Manggeng'),
('09072', '0907', 'Desa Batu Raja'),
('10011', '1001', 'Desa Singkil'),
('10012', '1001', 'Desa Bakongan Timur'),
('10021', '1002', 'Desa Pulau Banyak'),
('10022', '1002', 'Desa Tuangku'),
('10031', '1003', 'Desa Simeulue Timur'),
('10032', '1003', 'Desa Salimetinggi'),
('10041', '1004', 'Desa Kluet Utara'),
('10042', '1004', 'Desa Kluet Tengah'),
('11011', '1101', 'Desa Kuta Makmur'),
('11012', '1101', 'Desa Kubu Raya'),
('11021', '1102', 'Desa Kuala Simpang'),
('11022', '1102', 'Desa Rantau Rasau'),
('11031', '1103', 'Desa Bandar Pusaka'),
('11032', '1103', 'Desa Bandar Mulia'),
('11041', '1104', 'Desa Rantau'),
('11042', '1104', 'Desa Rantau Rasau Lama'),
('12011', '1201', 'Desa Takengon'),
('12012', '1201', 'Desa Lut Tawar'),
('12021', '1202', 'Desa Bener Meriah'),
('12022', '1202', 'Desa Kemili'),
('12031', '1203', 'Desa Kebayakan'),
('12032', '1203', 'Desa Pelepat'),
('12041', '1204', 'Desa Ketol'),
('12042', '1204', 'Desa Setui'),
('13011', '1301', 'Desa Idi Rayeuk'),
('13012', '1301', 'Desa Idi Rayeuk Timur'),
('13021', '1302', 'Desa Idi'),
('13022', '1302', 'Desa Perlak'),
('13031', '1303', 'Desa Jantho'),
('13032', '1303', 'Desa Jambak'),
('13041', '1304', 'Desa Birem Bayeun'),
('13042', '1304', 'Desa Birem Putih'),
('14011', '1401', 'Desa Lhoksukon'),
('14012', '1401', 'Desa Ujung'),
('14021', '1402', 'Desa Seunuddon'),
('14022', '1402', 'Desa Peuneulop'),
('14031', '1403', 'Desa Sawang'),
('14032', '1403', 'Desa Banggel'),
('14041', '1404', 'Desa Tanah Pasir'),
('14042', '1404', 'Desa Darussalam'),
('15011', '1501', 'Desa Blangkejeren'),
('15012', '1501', 'Desa Wih Ilang'),
('15021', '1502', 'Desa Kuta Panjang'),
('15022', '1502', 'Desa Pining'),
('15031', '1503', 'Desa Punti Raya'),
('15032', '1503', 'Desa Makmur Jaya'),
('16011', '1601', 'Desa Sigli'),
('16012', '1601', 'Desa Peuree'),
('16021', '1602', 'Desa Bireuen'),
('16022', '1602', 'Desa Bergeolak'),
('16031', '1603', 'Desa Muara Batu'),
('16032', '1603', 'Desa Ulee Kareng'),
('16041', '1604', 'Desa Peudada'),
('16042', '1604', 'Desa Peukan Jaya'),
('17011', '1701', 'Desa Meutiq'),
('17012', '1701', 'Desa Gajah Putih'),
('17021', '1702', 'Desa Bangli'),
('17022', '1702', 'Desa Bangli Maju'),
('18011', '1801', 'Desa Simeulue Timur'),
('18012', '1801', 'Desa Teupah Selatan'),
('18021', '1802', 'Desa Simeulue Tengah'),
('18022', '1802', 'Desa Benakat'),
('18031', '1803', 'Desa Simeulue Barat'),
('18032', '1803', 'Desa Sinabang');

-- --------------------------------------------------------

--
-- Table structure for table `tb_kabupaten_kota`
--

CREATE TABLE `tb_kabupaten_kota` (
  `id_kabupaten_kota` char(3) NOT NULL,
  `id_provinsi` char(2) NOT NULL,
  `nama_kabupaten_kota` varchar(35) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_kabupaten_kota`
--

INSERT INTO `tb_kabupaten_kota` (`id_kabupaten_kota`, `id_provinsi`, `nama_kabupaten_kota`) VALUES
('01', '11', 'Kota Banda Aceh'),
('02', '11', 'Kota Sabang'),
('03', '11', 'Kota Langsa'),
('04', '11', 'Kota Lhokseumawe'),
('05', '11', 'Kabupaten Aceh Barat'),
('06', '11', 'Kabupaten Aceh Barat Daya'),
('07', '11', 'Kabupaten Aceh Besar'),
('08', '11', 'Kabupaten Aceh Jaya'),
('09', '11', 'Kabupaten Aceh Selatan'),
('10', '11', 'Kabupaten Aceh Singkil'),
('11', '11', 'Kabupaten Aceh Tamiang'),
('12', '11', 'Kabupaten Aceh Tengah'),
('13', '11', 'Kabupaten Aceh Tenggara'),
('14', '11', 'Kabupaten Aceh Utara'),
('15', '11', 'Kabupaten Gayo Lues'),
('16', '11', 'Kabupaten Pidie'),
('17', '11', 'Kabupaten Pidie Jaya'),
('18', '11', 'Kabupaten Simeulue');

-- --------------------------------------------------------

--
-- Table structure for table `tb_kartu_keluarga`
--

CREATE TABLE `tb_kartu_keluarga` (
  `id_kk` char(10) NOT NULL,
  `no_kk` varchar(16) NOT NULL,
  `nik_kepala_keluarga` char(16) NOT NULL,
  `tanggal_terbit` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_kartu_keluarga`
--

INSERT INTO `tb_kartu_keluarga` (`id_kk`, `no_kk`, `nik_kepala_keluarga`, `tanggal_terbit`) VALUES
('1001000001', '1173010101010001', '1173010101010001', '2015-03-10'),
('1001000002', '1173010101010003', '1173010101010003', '2014-05-15'),
('1001000003', '1173010102010005', '1173010102010005', '2016-07-20'),
('1001000004', '1173010102010007', '1173010102010007', '2015-11-25'),
('1001000005', '1173010103010009', '1173010103010009', '2017-01-30'),
('1001000006', '1173010104010011', '1173010104010011', '2016-04-12'),
('1001000007', '1173010105010013', '1173010105010013', '2018-02-08'),
('1001000008', '1173010106010015', '1173010106010015', '2015-09-18'),
('1001000009', '1173020101010017', '1173020101010017', '2017-06-22'),
('1001000010', '1173020102010019', '1173020102010019', '2016-12-05'),
('1001000011', '1173030101010021', '1173030101010021', '2014-08-14'),
('1001000012', '1173030102010023', '1173030102010023', '2015-10-19'),
('1001000013', '1173040101010025', '1173040101010025', '2018-03-25'),
('1001000014', '1173040102010027', '1173040102010027', '2017-05-11'),
('1001000015', '1173040103010029', '1173040103010029', '2016-09-30'),
('1001000016', '1173050101010031', '1173050101010031', '2015-01-20'),
('1001000017', '1173050102010033', '1173050102010033', '2018-04-16'),
('1001000018', '1173050201010035', '1173050201010035', '2017-07-09'),
('1001000019', '1173050202010037', '1173050202010037', '2016-11-14'),
('1001000020', '1173050301010039', '1173050301010039', '2015-02-28'),
('1001000021', '1173070101010041', '1173070101010041', '2017-10-03'),
('1001000022', '1173070102010043', '1173070102010043', '2016-06-17'),
('1001000023', '1173070103010045', '1173070103010045', '2018-01-22'),
('1001000024', '1173070104010047', '1173070104010047', '2015-08-05'),
('1001000025', '1173070201010049', '1173070201010049', '2017-03-12'),
('1001000026', '1173070202010051', '1173070202010051', '2016-12-27'),
('1001000027', '1173070301010053', '1173070301010053', '2014-07-11'),
('1001000028', '1173070302010055', '1173070302010055', '2018-02-19'),
('1001000029', '1173070401010057', '1173070401010057', '2017-09-24'),
('1001000030', '1173070402010059', '1173070402010059', '2015-05-07'),
('1001000031', '1173080101010061', '1173080101010061', '2016-10-13'),
('1001000032', '1173080102010063', '1173080102010063', '2017-04-26'),
('1001000033', '1173080201010065', '1173080201010065', '2015-12-31'),
('1001000034', '1173080202010067', '1173080202010067', '2018-06-08'),
('1001000035', '1173090101010069', '1173090101010069', '2016-08-23'),
('1001000036', '1173090102010071', '1173090102010071', '2017-01-15'),
('1001000037', '1173090201010073', '1173090201010073', '2015-07-02'),
('1001000038', '1173090202010075', '1173090202010075', '2018-09-14'),
('1001000039', '1173100101010077', '1173100101010077', '2016-03-29'),
('1001000040', '1173100102010079', '1173100102010079', '2017-11-06'),
('1001000041', '1173110101010081', '1173110101010081', '2015-04-18'),
('1001000042', '1173110102010083', '1173110102010083', '2016-09-23'),
('1001000043', '1173120101010085', '1173120101010085', '2018-05-12'),
('1001000044', '1173120102010087', '1173120102010087', '2017-02-20'),
('1001000045', '1173130101010089', '1173130101010089', '2015-10-09'),
('1001000046', '1173130102010091', '1173130102010091', '2018-08-04'),
('1001000047', '1173140101010093', '1173140101010093', '2016-12-17'),
('1001000048', '1173140102010095', '1173140102010095', '2015-06-25'),
('1001000049', '1173150101010097', '1173150101010097', '2017-11-11'),
('1001000050', '1173150102010099', '1173150102010099', '2016-02-14');

-- --------------------------------------------------------

--
-- Table structure for table `tb_kecamatan`
--

CREATE TABLE `tb_kecamatan` (
  `id_kecamatan` char(4) NOT NULL,
  `id_kabupaten_kota` char(3) NOT NULL,
  `nama_kecamatan` varchar(35) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_kecamatan`
--

INSERT INTO `tb_kecamatan` (`id_kecamatan`, `id_kabupaten_kota`, `nama_kecamatan`) VALUES
('0101', '01', 'Kecamatan Baiturrahman'),
('0102', '01', 'Kecamatan Jaya Baru'),
('0103', '01', 'Kecamatan Kuta Alam'),
('0104', '01', 'Kecamatan Kuta Raja'),
('0105', '01', 'Kecamatan Meuraxa'),
('0106', '01', 'Kecamatan Syiah Kuala'),
('0201', '02', 'Kecamatan Sabang'),
('0202', '02', 'Kecamatan Pulau Weh'),
('0301', '03', 'Kecamatan Langsa Barat'),
('0302', '03', 'Kecamatan Langsa Timur'),
('0401', '04', 'Kecamatan Muara Batu'),
('0402', '04', 'Kecamatan Muara Dua'),
('0403', '04', 'Kecamatan Blang Mangat'),
('0501', '05', 'Kecamatan Meulaboh'),
('0502', '05', 'Kecamatan Johan Pahlawan'),
('0503', '05', 'Kecamatan Samatiga'),
('0504', '05', 'Kecamatan Arongan Lambalek'),
('0505', '05', 'Kecamatan Bubon'),
('0506', '05', 'Kecamatan Pantai Cerah'),
('0601', '06', 'Kecamatan Blangpidie'),
('0602', '06', 'Kecamatan Manggeng'),
('0603', '06', 'Kecamatan Samatiga'),
('0604', '06', 'Kecamatan Kuala Bhee'),
('0701', '07', 'Kecamatan Lhoknga'),
('0702', '07', 'Kecamatan Leupuet'),
('0703', '07', 'Kecamatan Darul Imarah'),
('0704', '07', 'Kecamatan Lhoong'),
('0705', '07', 'Kecamatan Baitussalam'),
('0706', '07', 'Kecamatan LhOWE'),
('0707', '07', 'Kecamatan Ulim'),
('0708', '07', 'Kecamatan Montasik'),
('0709', '07', 'Kecamatan Mesjid Raya'),
('0710', '07', 'Kecamatan Lheuh'),
('0711', '07', 'Kecamatan Peukan Bada'),
('0712', '07', 'Kecamatan Lhoktai'),
('0801', '08', 'Kecamatan Seulimeum'),
('0802', '08', 'Kecamatan Acehjaya'),
('0803', '08', 'Kecamatan Jaya'),
('0804', '08', 'Kecamatan Teunom'),
('0901', '09', 'Kecamatan Tapaktuan'),
('0902', '09', 'Kecamatan Bakongan'),
('0903', '09', 'Kecamatan Labuhan Haji'),
('0904', '09', 'Kecamatan Tanjong Layeu'),
('0905', '09', 'Kecamatan Sama Dua'),
('0906', '09', 'Kecamatan Kota Baharu'),
('0907', '09', 'Kecamatan Manggeng'),
('1001', '10', 'Kecamatan Singkil'),
('1002', '10', 'Kecamatan Pulau Banyak'),
('1003', '10', 'Kecamatan Simeulue Timur'),
('1004', '10', 'Kecamatan Kluet Utara'),
('1101', '11', 'Kecamatan Kuta Makmur'),
('1102', '11', 'Kecamatan Kuala Simpang'),
('1103', '11', 'Kecamatan Bandar Pusaka'),
('1104', '11', 'Kecamatan Rantau'),
('1201', '12', 'Kecamatan Takengon'),
('1202', '12', 'Kecamatan Bener Meriah'),
('1203', '12', 'Kecamatan Lut Tawar'),
('1204', '12', 'Kecamatan Ketol'),
('1301', '13', 'Kecamatan Idi Rayeuk'),
('1302', '13', 'Kecamatan Idi'),
('1303', '13', 'Kecamatan Jantho'),
('1304', '13', 'Kecamatan Birem Bayeun'),
('1401', '14', 'Kecamatan Lhoksukon'),
('1402', '14', 'Kecamatan Seunuddon'),
('1403', '14', 'Kecamatan Sawang'),
('1404', '14', 'Kecamatan Tanah Pasir'),
('1501', '15', 'Kecamatan Blangkejeren'),
('1502', '15', 'Kecamatan Kuta Panjang'),
('1503', '15', 'Kecamatan Punti Raya'),
('1601', '16', 'Kecamatan Sigli'),
('1602', '16', 'Kecamatan Bireuen'),
('1603', '16', 'Kecamatan Muara Batu'),
('1604', '16', 'Kecamatan Peudada'),
('1701', '17', 'Kecamatan Meutiq'),
('1702', '17', 'Kecamatan Bangli'),
('1801', '18', 'Kecamatan Simeulue Timur'),
('1802', '18', 'Kecamatan Simeulue Tengah'),
('1803', '18', 'Kecamatan Simeulue Barat');

-- --------------------------------------------------------

--
-- Table structure for table `tb_penduduk`
--

CREATE TABLE `tb_penduduk` (
  `nik` char(16) NOT NULL,
  `nama_lengkap` varchar(30) NOT NULL,
  `tempat_lahir` varchar(15) DEFAULT NULL,
  `tanggal_lahir` date DEFAULT NULL,
  `jenis_kelamin` enum('L','P') DEFAULT NULL,
  `id_agama` char(1) DEFAULT NULL,
  `id_alamat` char(5) DEFAULT NULL,
  `id_status_perkawinan` char(1) DEFAULT NULL,
  `kewarganegaraan` varchar(3) DEFAULT NULL,
  `id_status_penduduk` char(1) DEFAULT NULL,
  `id_kk` char(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_penduduk`
--

INSERT INTO `tb_penduduk` (`nik`, `nama_lengkap`, `tempat_lahir`, `tanggal_lahir`, `jenis_kelamin`, `id_agama`, `id_alamat`, `id_status_perkawinan`, `kewarganegaraan`, `id_status_penduduk`, `id_kk`) VALUES
('1173010101010001', 'Ahmad Rizki Kurniawan', 'Banda Aceh', '1985-03-15', 'L', '1', '00001', '2', 'WNI', '1', '1001000001'),
('1173010101010002', 'Siti Nur Azizah', 'Banda Aceh', '1988-07-22', 'P', '1', '00001', '2', 'WNI', '1', '1001000001'),
('1173010101010003', 'Hendra Gunawan', 'Banda Aceh', '1980-11-09', 'L', '1', '00002', '2', 'WNI', '1', '1001000002'),
('1173010101010004', 'Nurul Habibah', 'Aceh Besar', '1992-01-28', 'P', '1', '00002', '1', 'WNI', '1', '1001000002'),
('1173010102010005', 'Ridho Pratama', 'Banda Aceh', '1995-05-14', 'L', '1', '00003', '1', 'WNI', '1', '1001000003'),
('1173010102010006', 'Eka Putri Santoso', 'Lhokseumawe', '1990-09-03', 'P', '1', '00003', '2', 'WNI', '1', '1001000003'),
('1173010102010007', 'Muhammad Ilham', 'Banda Aceh', '1987-12-20', 'L', '1', '00004', '2', 'WNI', '1', '1001000004'),
('1173010102010008', 'Dewi Lestari', 'Aceh Jaya', '1993-06-11', 'P', '1', '00004', '2', 'WNI', '1', '1001000004'),
('1173010103010009', 'Budi Santoso', 'Banda Aceh', '1982-04-17', 'L', '1', '00005', '2', 'WNI', '2', '1001000005'),
('1173010103010010', 'Sinta Wijaya', 'Sabang', '1991-10-26', 'P', '1', '00005', '3', 'WNI', '1', '1001000005'),
('1173010104010011', 'Rahman Hakim', 'Banda Aceh', '1986-02-08', 'L', '1', '00006', '2', 'WNI', '1', '1001000006'),
('1173010104010012', 'Linda Kusuma', 'Langsa', '1989-08-19', 'P', '1', '00006', '2', 'WNI', '1', '1001000006'),
('1173010105010013', 'Fajar Ramadhan', 'Aceh Besar', '1994-03-05', 'L', '1', '00007', '1', 'WNI', '1', '1001000007'),
('1173010105010014', 'Yuni Hartono', 'Banda Aceh', '1996-09-12', 'P', '2', '00007', '1', 'WNA', '1', '1001000007'),
('1173010106010015', 'Arif Wijaksana', 'Aceh Utara', '1984-07-23', 'L', '1', '00008', '2', 'WNI', '1', '1001000008'),
('1173010106010016', 'Mira Handoko', 'Banda Aceh', '1988-11-30', 'P', '1', '00008', '2', 'WNI', '1', '1001000008'),
('1173020101010017', 'Dimas Pratama', 'Sabang', '1991-05-14', 'L', '1', '00009', '1', 'WNI', '1', '1001000009'),
('1173020101010018', 'Rini Susanto', 'Banda Aceh', '1993-12-02', 'P', '1', '00009', '2', 'WNI', '1', '1001000009'),
('1173020102010019', 'Wahyu Prasetyo', 'Sabang', '1985-06-16', 'L', '1', '00010', '2', 'WNI', '1', '1001000010'),
('1173020102010020', 'Siti Marjiah', 'Sabang', '1987-10-21', 'P', '1', '00010', '4', 'WNI', '1', '1001000010'),
('1173030101010021', 'Irfan Syaputra', 'Langsa', '1989-04-09', 'L', '1', '00011', '2', 'WNI', '1', '1001000011'),
('1173030101010022', 'Anita Maharani', 'Langsa', '1992-02-15', 'P', '1', '00011', '2', 'WNI', '1', '1001000011'),
('1173030102010023', 'Zainal Abidin', 'Langsa', '1980-09-27', 'L', '1', '00012', '2', 'WNI', '1', '1001000012'),
('1173030102010024', 'Ratna Dewi', 'Langsa', '1994-08-12', 'P', '3', '00012', '1', 'WNA', '1', '1001000012'),
('1173040101010025', 'Hendri Wijaya', 'Lhokseumawe', '1988-01-30', 'L', '1', '00013', '2', 'WNI', '1', '1001000013'),
('1173040101010026', 'Joni Tarpada', 'Lhokseumawe', '1995-11-08', 'L', '1', '00013', '1', 'WNI', '1', '1001000013'),
('1173040102010027', 'Karina Amelia', 'Lhokseumawe', '1991-07-25', 'P', '1', '00014', '2', 'WNI', '1', '1001000014'),
('1173040102010028', 'Bambang Sutrisno', 'Aceh Besar', '1983-05-19', 'L', '1', '00014', '2', 'WNI', '1', '1001000014'),
('1173040103010029', 'Susi Susanti', 'Lhokseumawe', '1990-10-03', 'P', '1', '00015', '3', 'WNI', '1', '1001000015'),
('1173040103010030', 'Toto Suryanto', 'Aceh Besar', '1986-12-14', 'L', '1', '00015', '2', 'WNI', '1', '1001000015'),
('1173050101010031', 'Rahmat Fauzi', 'Aceh Barat', '1981-03-22', 'L', '1', '00016', '2', 'WNI', '1', '1001000016'),
('1173050101010032', 'Lina Marlina', 'Aceh Barat', '1985-08-10', 'P', '1', '00016', '2', 'WNI', '1', '1001000016'),
('1173050102010033', 'Syaiful Rahman', 'Aceh Barat', '1992-04-07', 'L', '1', '00017', '1', 'WNI', '2', '1001000017'),
('1173050102010034', 'Rina Kartini', 'Meulaboh', '1988-09-18', 'P', '1', '00017', '2', 'WNI', '1', '1001000017'),
('1173050201010035', 'Juanda Gunawan', 'Aceh Barat', '1984-11-25', 'L', '1', '00018', '2', 'WNI', '1', '1001000018'),
('1173050201010036', 'Ayu Permata', 'Meulaboh', '1996-01-29', 'P', '2', '00018', '1', 'WNA', '1', '1001000018'),
('1173050202010037', 'Danang Permadi', 'Aceh Barat', '1989-07-11', 'L', '1', '00019', '3', 'WNI', '1', '1001000019'),
('1173050202010038', 'Neneng Suryani', 'Aceh Barat', '1993-05-08', 'P', '1', '00019', '2', 'WNI', '1', '1001000019'),
('1173050301010039', 'Ahmad Zainudin', 'Aceh Barat Daya', '1982-02-14', 'L', '1', '00020', '2', 'WNI', '1', '1001000020'),
('1173050301010040', 'Masniyah Said', 'Aceh Barat Daya', '1987-06-20', 'P', '1', '00020', '2', 'WNI', '1', '1001000020'),
('1173070101010041', 'Suryadi Gunawan', 'Aceh Besar', '1980-10-09', 'L', '1', '00021', '2', 'WNI', '1', '1001000021'),
('1173070101010042', 'Fitri Wahyuni', 'Aceh Besar', '1994-03-17', 'P', '1', '00021', '1', 'WNI', '1', '1001000021'),
('1173070102010043', 'Hari Prabowo', 'Aceh Besar', '1986-12-28', 'L', '1', '00022', '2', 'WNI', '1', '1001000022'),
('1173070102010044', 'Putri Maharini', 'Aceh Besar', '1991-08-05', 'P', '1', '00022', '2', 'WNI', '1', '1001000022'),
('1173070103010045', 'Andi Wijaya', 'Aceh Besar', '1988-04-19', 'L', '4', '00023', '2', 'WNI', '1', '1001000023'),
('1173070103010046', 'Hilda Kusuma', 'Aceh Besar', '1995-09-14', 'P', '1', '00023', '1', 'WNI', '1', '1001000023'),
('1173070104010047', 'Sumardi Santoso', 'Aceh Besar', '1983-07-22', 'L', '1', '00024', '4', 'WNI', '2', '1001000024'),
('1173070104010048', 'Soraya Amelia', 'Aceh Besar', '1993-01-10', 'P', '1', '00024', '2', 'WNI', '1', '1001000024'),
('1173070201010049', 'Didik Rahmat', 'Aceh Besar', '1987-11-03', 'L', '1', '00025', '2', 'WNI', '1', '1001000025'),
('1173070201010050', 'Maya Kusuma', 'Aceh Besar', '1990-05-27', 'P', '1', '00025', '2', 'WNI', '1', '1001000025'),
('1173070202010051', 'Rudi Hartono', 'Aceh Besar', '1981-08-13', 'L', '1', '00026', '2', 'WNI', '1', '1001000026'),
('1173070202010052', 'Indah Lestari', 'Aceh Besar', '1989-02-21', 'P', '1', '00026', '3', 'WNI', '1', '1001000026'),
('1173070301010053', 'Tri Hartanto', 'Aceh Besar', '1992-06-30', 'L', '5', '00027', '1', 'WNA', '1', '1001000027'),
('1173070301010054', 'Dewi Puspita', 'Aceh Besar', '1986-09-08', 'P', '1', '00027', '2', 'WNI', '1', '1001000027'),
('1173070302010055', 'Eka Prasetya', 'Aceh Besar', '1984-04-15', 'L', '1', '00028', '2', 'WNI', '1', '1001000028'),
('1173070302010056', 'Vivian Handoko', 'Aceh Besar', '1995-10-02', 'P', '1', '00028', '1', 'WNI', '1', '1001000028'),
('1173070401010057', 'Budi Hermanto', 'Aceh Besar', '1988-07-19', 'L', '1', '00029', '2', 'WNI', '1', '1001000029'),
('1173070401010058', 'Suri Sumardjo', 'Aceh Besar', '1993-12-11', 'P', '1', '00029', '2', 'WNI', '1', '1001000029'),
('1173070402010059', 'Gunawan Santoso', 'Aceh Besar', '1979-05-24', 'L', '1', '00030', '2', 'WNI', '2', '1001000030'),
('1173070402010060', 'Titik Wijaya', 'Aceh Besar', '1987-11-09', 'P', '1', '00030', '4', 'WNI', '1', '1001000030'),
('1173080101010061', 'Joko Setiawan', 'Aceh Jaya', '1985-03-26', 'L', '1', '00031', '2', 'WNI', '1', '1001000031'),
('1173080101010062', 'Wulan Kurnia', 'Aceh Jaya', '1991-08-14', 'P', '1', '00031', '2', 'WNI', '1', '1001000031'),
('1173080102010063', 'Adi Santoso', 'Aceh Jaya', '1988-01-07', 'L', '1', '00032', '1', 'WNI', '1', '1001000032'),
('1173080102010064', 'Ninik Kusumawati', 'Aceh Jaya', '1994-09-22', 'P', '2', '00032', '1', 'WNA', '1', '1001000032'),
('1173080201010065', 'Bambang Wijaksana', 'Aceh Jaya', '1982-10-17', 'L', '1', '00033', '2', 'WNI', '1', '1001000033'),
('1173080201010066', 'Lusi Suryanti', 'Aceh Jaya', '1990-04-29', 'P', '1', '00033', '2', 'WNI', '1', '1001000033'),
('1173080202010067', 'Santoso Wijayanto', 'Aceh Jaya', '1987-07-05', 'L', '1', '00034', '3', 'WNI', '1', '1001000034'),
('1173080202010068', 'Ulfah Rahmawati', 'Aceh Jaya', '1996-11-18', 'P', '1', '00034', '1', 'WNI', '1', '1001000034'),
('1173090101010069', 'Irawan Santoso', 'Aceh Selatan', '1983-12-08', 'L', '1', '00035', '2', 'WNI', '1', '1001000035'),
('1173090101010070', 'Rina Wijaksana', 'Aceh Selatan', '1989-05-13', 'P', '1', '00035', '2', 'WNI', '1', '1001000035'),
('1173090102010071', 'Muhammad Iksan', 'Aceh Selatan', '1986-09-19', 'L', '1', '00036', '2', 'WNI', '1', '1001000036'),
('1173090102010072', 'Dwi Lestari', 'Aceh Selatan', '1992-02-27', 'P', '1', '00036', '2', 'WNI', '1', '1001000036'),
('1173090201010073', 'Hendra Kusuma', 'Aceh Selatan', '1980-11-04', 'L', '1', '00037', '2', 'WNI', '2', '1001000037'),
('1173090201010074', 'Sinta Wijaya', 'Aceh Selatan', '1991-06-16', 'P', '1', '00037', '1', 'WNI', '1', '1001000037'),
('1173090202010075', 'Yuli Setiawan', 'Aceh Selatan', '1984-08-22', 'L', '1', '00038', '2', 'WNI', '1', '1001000038'),
('1173090202010076', 'Rima Hartono', 'Aceh Selatan', '1995-03-09', 'P', '3', '00038', '1', 'WNA', '1', '1001000038'),
('1173100101010077', 'Iwan Suryanto', 'Aceh Singkil', '1988-10-14', 'L', '1', '00039', '2', 'WNI', '1', '1001000039'),
('1173100101010078', 'Anis Kusuma', 'Aceh Singkil', '1993-04-26', 'P', '1', '00039', '2', 'WNI', '1', '1001000039'),
('1173100102010079', 'Taufik Rahman', 'Aceh Singkil', '1981-07-11', 'L', '1', '00040', '2', 'WNI', '1', '1001000040'),
('1173100102010080', 'Yasmin Suwardi', 'Aceh Singkil', '1989-12-03', 'P', '1', '00040', '4', 'WNI', '1', '1001000040'),
('1173110101010081', 'Wahyu Hermanto', 'Aceh Tamiang', '1985-02-19', 'L', '1', '00041', '2', 'WNI', '1', '1001000041'),
('1173110101010082', 'Siti Nurjannah', 'Aceh Tamiang', '1991-08-30', 'P', '1', '00041', '2', 'WNI', '1', '1001000041'),
('1173110102010083', 'Rizki Adiputra', 'Aceh Tamiang', '1987-06-25', 'L', '1', '00042', '1', 'WNI', '1', '1001000042'),
('1173110102010084', 'Meilina Wijaya', 'Aceh Tamiang', '1994-01-08', 'P', '1', '00042', '2', 'WNI', '1', '1001000042'),
('1173120101010085', 'Syamsu Zaman', 'Aceh Tengah', '1982-09-12', 'L', '1', '00043', '2', 'WNI', '1', '1001000043'),
('1173120101010086', 'Yulia Purnama', 'Aceh Tengah', '1988-04-21', 'P', '1', '00043', '2', 'WNI', '1', '1001000043'),
('1173120102010087', 'Fajar Gunawan', 'Aceh Tengah', '1990-10-05', 'L', '5', '00044', '1', 'WNA', '1', '1001000044'),
('1173120102010088', 'Eka Sundari', 'Aceh Tengah', '1996-05-15', 'P', '1', '00044', '1', 'WNI', '1', '1001000044'),
('1173130101010089', 'Marto Wijaksana', 'Aceh Tenggara', '1983-11-28', 'L', '1', '00045', '2', 'WNI', '1', '1001000045'),
('1173130101010090', 'Isna Wijaya', 'Aceh Tenggara', '1992-07-14', 'P', '1', '00045', '2', 'WNI', '1', '1001000045'),
('1173130102010091', 'Hendra Santoso', 'Aceh Tenggara', '1986-03-02', 'L', '1', '00046', '3', 'WNI', '1', '1001000046'),
('1173130102010092', 'Ratna Kumala', 'Aceh Tenggara', '1989-09-24', 'P', '1', '00046', '2', 'WNI', '1', '1001000046'),
('1173140101010093', 'Ahmad Riyanto', 'Aceh Utara', '1981-05-17', 'L', '1', '00047', '2', 'WNI', '2', '1001000047'),
('1173140101010094', 'Susi Mulyani', 'Aceh Utara', '1993-10-30', 'P', '1', '00047', '1', 'WNI', '1', '1001000047'),
('1173140102010095', 'Dedy Hermawan', 'Aceh Utara', '1988-01-22', 'L', '1', '00048', '2', 'WNI', '1', '1001000048'),
('1173140102010096', 'Komang Siswanti', 'Aceh Utara', '1995-06-11', 'P', '4', '00048', '1', 'WNA', '1', '1001000048'),
('1173150101010097', 'Bambang Hermanto', 'Gayo Lues', '1982-04-08', 'L', '1', '00049', '2', 'WNI', '1', '1001000049'),
('1173150101010098', 'Laila Mukmin', 'Gayo Lues', '1990-12-19', 'P', '1', '00049', '2', 'WNI', '1', '1001000049'),
('1173150102010099', 'Rizal Wijaya', 'Gayo Lues', '1987-08-06', 'L', '1', '00050', '1', 'WNI', '1', '1001000050'),
('1173150102010100', 'Cantika Wijaksana', 'Gayo Lues', '1994-11-13', 'P', '1', '00050', '2', 'WNI', '1', '1001000050');

-- --------------------------------------------------------

--
-- Table structure for table `tb_provinsi`
--

CREATE TABLE `tb_provinsi` (
  `id_provinsi` char(2) NOT NULL,
  `nama_provinsi` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_provinsi`
--

INSERT INTO `tb_provinsi` (`id_provinsi`, `nama_provinsi`) VALUES
('11', 'Aceh');

-- --------------------------------------------------------

--
-- Table structure for table `tb_status_penduduk`
--

CREATE TABLE `tb_status_penduduk` (
  `id_status_penduduk` char(1) NOT NULL,
  `status_penduduk` varchar(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_status_penduduk`
--

INSERT INTO `tb_status_penduduk` (`id_status_penduduk`, `status_penduduk`) VALUES
('1', 'Hidup'),
('2', 'Mati');

-- --------------------------------------------------------

--
-- Table structure for table `tb_status_perkawinan`
--

CREATE TABLE `tb_status_perkawinan` (
  `id_status_perkawinan` char(1) NOT NULL,
  `status_perkawinan` varchar(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_status_perkawinan`
--

INSERT INTO `tb_status_perkawinan` (`id_status_perkawinan`, `status_perkawinan`) VALUES
('1', 'Belum Kawin'),
('2', 'Sudah Kawin'),
('3', 'Cerai Hidup'),
('4', 'Cerai Mati');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_agama`
--
ALTER TABLE `tb_agama`
  ADD PRIMARY KEY (`id_agama`);

--
-- Indexes for table `tb_alamat`
--
ALTER TABLE `tb_alamat`
  ADD PRIMARY KEY (`id_alamat`),
  ADD KEY `fk_alamat_desa` (`id_desa`);

--
-- Indexes for table `tb_desa`
--
ALTER TABLE `tb_desa`
  ADD PRIMARY KEY (`id_desa`),
  ADD KEY `fk_desa_kecamatan` (`id_kecamatan`);

--
-- Indexes for table `tb_kabupaten_kota`
--
ALTER TABLE `tb_kabupaten_kota`
  ADD PRIMARY KEY (`id_kabupaten_kota`),
  ADD KEY `fk_kabupaten_provinsi` (`id_provinsi`);

--
-- Indexes for table `tb_kartu_keluarga`
--
ALTER TABLE `tb_kartu_keluarga`
  ADD PRIMARY KEY (`id_kk`),
  ADD UNIQUE KEY `no_kk` (`no_kk`);

--
-- Indexes for table `tb_kecamatan`
--
ALTER TABLE `tb_kecamatan`
  ADD PRIMARY KEY (`id_kecamatan`),
  ADD KEY `fk_kecamatan_kabupaten` (`id_kabupaten_kota`);

--
-- Indexes for table `tb_penduduk`
--
ALTER TABLE `tb_penduduk`
  ADD PRIMARY KEY (`nik`),
  ADD KEY `fk_penduduk_agama` (`id_agama`),
  ADD KEY `fk_penduduk_alamat` (`id_alamat`),
  ADD KEY `fk_penduduk_perkawinan` (`id_status_perkawinan`),
  ADD KEY `fk_penduduk_status` (`id_status_penduduk`),
  ADD KEY `fk_penduduk_kk` (`id_kk`);

--
-- Indexes for table `tb_provinsi`
--
ALTER TABLE `tb_provinsi`
  ADD PRIMARY KEY (`id_provinsi`);

--
-- Indexes for table `tb_status_penduduk`
--
ALTER TABLE `tb_status_penduduk`
  ADD PRIMARY KEY (`id_status_penduduk`);

--
-- Indexes for table `tb_status_perkawinan`
--
ALTER TABLE `tb_status_perkawinan`
  ADD PRIMARY KEY (`id_status_perkawinan`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tb_alamat`
--
ALTER TABLE `tb_alamat`
  ADD CONSTRAINT `fk_alamat_desa` FOREIGN KEY (`id_desa`) REFERENCES `tb_desa` (`id_desa`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_desa`
--
ALTER TABLE `tb_desa`
  ADD CONSTRAINT `fk_desa_kecamatan` FOREIGN KEY (`id_kecamatan`) REFERENCES `tb_kecamatan` (`id_kecamatan`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_kabupaten_kota`
--
ALTER TABLE `tb_kabupaten_kota`
  ADD CONSTRAINT `fk_kabupaten_provinsi` FOREIGN KEY (`id_provinsi`) REFERENCES `tb_provinsi` (`id_provinsi`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_kecamatan`
--
ALTER TABLE `tb_kecamatan`
  ADD CONSTRAINT `fk_kecamatan_kabupaten` FOREIGN KEY (`id_kabupaten_kota`) REFERENCES `tb_kabupaten_kota` (`id_kabupaten_kota`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_penduduk`
--
ALTER TABLE `tb_penduduk`
  ADD CONSTRAINT `fk_penduduk_agama` FOREIGN KEY (`id_agama`) REFERENCES `tb_agama` (`id_agama`) ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_penduduk_alamat` FOREIGN KEY (`id_alamat`) REFERENCES `tb_alamat` (`id_alamat`) ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_penduduk_kk` FOREIGN KEY (`id_kk`) REFERENCES `tb_kartu_keluarga` (`id_kk`) ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_penduduk_perkawinan` FOREIGN KEY (`id_status_perkawinan`) REFERENCES `tb_status_perkawinan` (`id_status_perkawinan`) ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_penduduk_status` FOREIGN KEY (`id_status_penduduk`) REFERENCES `tb_status_penduduk` (`id_status_penduduk`) ON DELETE RESTRICT ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
