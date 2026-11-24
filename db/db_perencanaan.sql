-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Nov 24, 2026 at 03:34 AM
-- Server version: 8.4.13
-- PHP Version: 8.3.36

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_perencanaan`
--

-- --------------------------------------------------------

--
-- Table structure for table `master_skpa`
--

CREATE TABLE `master_skpa` (
  `id_skpa` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `kode_skpa` varchar(25) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nama_skpa` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `bidang_urusan` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `master_skpa`
--

INSERT INTO `master_skpa` (`id_skpa`, `kode_skpa`, `nama_skpa`, `bidang_urusan`) VALUES
('SKPA-01', '2.11.01', 'Dinas Lingkungan Hidup dan Kehutanan Aceh', 'Lingkungan Hidup dan Kehutanan'),
('SKPA-02', '3.29.01', 'Dinas Energi dan Sumber Daya Mineral Aceh', 'Energi dan Sumber Daya Mineral'),
('SKPA-03', '1.03.02', 'Dinas Pengairan Aceh', 'Pekerjaan Umum dan Pengairan'),
('SKPA-04', '3.27.01', 'Dinas Pertanian dan Perkebunan Aceh', 'Pertanian dan Pangan'),
('SKPA-05', '5.01.01', 'Badan Perencanaan Pembangunan Daerah Aceh', 'Perencanaan Pembangunan Daerah'),
('SKPA-06', '1.02.01', '  Dinas Kesehatan Aceh  ', 'Kesehatan'),
('SKPA-07', '1.01.01', 'Dinas Pendidikan Aceh', 'pendidikan'),
('SKPA-08', '2.15.01', 'Dinas Perhubungan   Aceh', 'Perhubungan dan Transportasi'),
('SKPA-09', '3.25.01', 'Dinas Kelautan dan Perikanan Aceh', 'Kelautan dan Perikanan'),
('SKPA-10', '1.06.01', 'dinas sosial aceh', 'Sosial dan Penanggulangan Bencana');

-- --------------------------------------------------------

--
-- Table structure for table `tb_evaluasi_pembangunan`
--

CREATE TABLE `tb_evaluasi_pembangunan` (
  `id_evaluasi` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_program` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_kegiatan` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_realisasi` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `periode_evaluasi` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tanggal_evaluasi` date NOT NULL,
  `skor_capaian_kinerja` decimal(5,2) NOT NULL,
  `predikat_kinerja` enum('Sangat Tinggi','Tinggi','Sedang','Rendah','Sangat Rendah') COLLATE utf8mb4_unicode_ci NOT NULL,
  `status_tindak_lanjut` enum('Dipertahankan','Perlu Percepatan','Evaluasi Ulang') COLLATE utf8mb4_unicode_ci NOT NULL,
  `catatan_evaluasi` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `rekomendasi_kebijakan` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `evaluator_skpa` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Badan Perencanaan Pembangunan Daerah Aceh'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tb_evaluasi_pembangunan`
--

INSERT INTO `tb_evaluasi_pembangunan` (`id_evaluasi`, `id_program`, `id_kegiatan`, `id_realisasi`, `periode_evaluasi`, `tanggal_evaluasi`, `skor_capaian_kinerja`, `predikat_kinerja`, `status_tindak_lanjut`, `catatan_evaluasi`, `rekomendasi_kebijakan`, `evaluator_skpa`) VALUES
('EVL-001', 'PRG-001', 'KEG-001', 'RLS-001', 'Triwulan III 2026', '2026-10-15', 73.75, 'Tinggi', 'Perlu Percepatan', 'Capaian fisik pengelolaan sampah mencapai 73,50% dengan serapan anggaran 74,00%.', 'Prioritaskan aktivasi bank sampah desa dan penambahan armada angkut di wilayah dengan beban TPA tinggi.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-002', 'PRG-001', 'KEG-002', 'RLS-002', 'Triwulan III 2026', '2026-10-15', 75.50, 'Tinggi', 'Perlu Percepatan', 'Penataan RTH mencapai 112,50 Ha dari target 150 Ha, namun rasio RTH perkotaan masih di bawah ambang 30%.', 'Fokuskan anggaran triwulan IV pada pembebasan dan penghijauan koridor hijau di Kota Banda Aceh dan Aceh Besar.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-003', 'PRG-002', 'KEG-003', 'RLS-003', 'Triwulan III 2026', '2026-10-15', 80.74, 'Sangat Tinggi', 'Dipertahankan', 'Pemantauan kualitas air sungai dan udara berjalan sesuai jadwal pada mayoritas stasiun pantau.', 'Tindak lanjuti temuan parameter cemar ringan pada daerah aliran sungai dengan inspeksi sumber limbah domestik.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-004', 'PRG-002', 'KEG-004', 'RLS-004', 'Triwulan III 2026', '2026-10-15', 86.79, 'Sangat Tinggi', 'Dipertahankan', 'Audit dokumen izin lingkungan mencapai 31 dokumen aktif dengan tingkat serapan anggaran 85%.', 'Terbitkan surat peringatan pembinaan bagi perusahaan yang masa berlaku izinnya mendekati kedaluwarsa.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-005', 'PRG-003', 'KEG-005', 'RLS-005', 'Triwulan III 2026', '2026-10-15', 69.00, 'Sedang', 'Evaluasi Ulang', 'Realisasi fisik dan serapan anggaran masih di bawah target triwulan III akibat kendala cuaca lapangan.', 'Jadwalkan ulang supervisi lapangan bersama tim teknis kabupaten dan optimalkan pemantauan berbasis citra.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-006', 'PRG-004', 'KEG-006', 'RLS-006', 'Triwulan III 2026', '2026-10-15', 71.00, 'Tinggi', 'Perlu Percepatan', 'Rehabilitasi jaringan irigasi mencapai 9,00 km dari target 12,50 km.', 'Percepat penyelesaian konstruksi saluran primer sebelum puncak musim hujan akhir tahun.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-007', 'PRG-005', 'KEG-007', 'RLS-007', 'Triwulan III 2026', '2026-10-15', 79.00, 'Tinggi', 'Dipertahankan', 'Perlindungan lahan pertanian berkelanjutan seluas 360 Ha selaras dengan pemetaan tutupan lahan.', 'Integrasikan batas poligon lahan sawah dilindungi ke dalam dokumen pengendalian pemanfaatan ruang.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-008', 'PRG-006', 'KEG-008', 'RLS-008', 'Akhir Tahun 2025', '2025-12-28', 98.50, 'Sangat Tinggi', 'Dipertahankan', 'Seluruh 23 kabupaten/kota telah menyelesaikan validasi laporan evaluasi kinerja pembangunan tahun 2025.', 'Gunakan hasil evaluasi 2025 sebagai baseline penyusunan prioritas pagu anggaran tahun berikutnya.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-009', 'PRG-007', 'KEG-009', 'RLS-009', 'Akhir Tahun 2025', '2025-12-27', 99.00, 'Sangat Tinggi', 'Dipertahankan', 'Rehabilitasi hutan lindung dan mangrove seluas 320 Ha di Sabang tuntas 100%.', 'Lanjutkan pemeliharaan tanaman mangrove bersama kelompok masyarakat pesisir.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-010', 'PRG-007', 'KEG-010', 'RLS-010', 'Akhir Tahun 2025', '2025-12-27', 97.50, 'Sangat Tinggi', 'Dipertahankan', 'Pemulihan lahan gambut di Kabupaten Aceh Singkil mencapai 98% dari target tahunan.', 'Integrasikan sekat kanal gambut ke dalam sistem pemantauan tinggi muka air.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-011', 'PRG-008', 'KEG-011', 'RLS-013', 'Triwulan III 2026', '2026-10-16', 72.67, 'Tinggi', 'Perlu Percepatan', 'Kapasitas pengolahan sampah terpadu di Lhokseumawe mendekati target triwulan III.', 'Percepat instalasi unit pencacah organik agar target tahunan tercapai tepat waktu.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-012', 'PRG-008', 'KEG-012', 'RLS-015', 'Triwulan III 2026', '2026-10-16', 113.75, 'Sangat Tinggi', 'Evaluasi Ulang', 'Realisasi fisik tercatat 132,50% akibat lonjakan volume limbah masuk dan perlu verifikasi duplikasi pencatatan.', 'Lakukan rekonsiliasi data bersama unit pelaksana teknis di Kota Lhokseumawe.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-013', 'PRG-009', 'KEG-013', 'RLS-016', 'Triwulan III 2026', '2026-10-16', 81.67, 'Sangat Tinggi', 'Dipertahankan', 'Standarisasi sanitasi fasilitas kesehatan di Banda Aceh berjalan sesuai rencana.', 'Pertahankan pengawasan pengelolaan limbah cair medis pada seluruh puskesmas.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-014', 'PRG-009', 'KEG-014', 'RLS-018', 'Triwulan III 2026', '2026-10-16', 29.25, 'Rendah', 'Evaluasi Ulang', 'Terdapat jurnal koreksi pengembalian anggaran pada triwulan III sehingga serapan neto menurun.', 'Audit ulang rincian kontrak pengadaan pengolah limbah medis sebelum pencairan termin akhir.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-015', 'PRG-010', 'KEG-015', 'RLS-019', 'Akhir Tahun 2025', '2025-12-26', 99.00, 'Sangat Tinggi', 'Dipertahankan', 'Seluruh 25 titik sarana air bersih di Aceh Barat Daya selesai dibangun meski pagu awal perlu disinkronkan.', 'Lengkapi pencatatan pagu definitif pada arsip perencanaan anggaran.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-016', 'PRG-011', 'KEG-017', 'RLS-021', 'Triwulan III 2026', '2026-10-16', 70.00, 'Tinggi', 'Perlu Percepatan', 'Revitalisasi 21 ruang kelas di Aceh Besar berjalan, namun metadata jadwal kegiatan perlu diperbaiki.', 'Perbaiki entri tanggal selesai kegiatan pada sistem pelaporan dan kejar sisa 9 ruang di triwulan IV.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-017', 'PRG-011', 'KEG-018', 'RLS-022', 'Triwulan III 2026', '2026-10-16', 84.00, 'Sangat Tinggi', 'Dipertahankan', 'Pembinaan 34 sekolah Adiwiyata di Aceh Barat berdampak positif pada pengelolaan sampah sekolah.', 'Perluas cakupan program bank sampah sekolah ke kecamatan pesisir.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-018', 'PRG-012', 'KEG-019', 'RLS-023', 'Triwulan III 2026', '2026-10-16', 75.50, 'Tinggi', 'Perlu Percepatan', 'Pemasangan 114 unit PJU tenaga surya di Aceh Jaya mencapai 76% dengan serapan 75%.', 'Gunakan jalur distribusi alternatif untuk mempercepat pengiriman sisa material tiang.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-019', 'PRG-013', 'KEG-020', 'RLS-024', 'Triwulan III 2026', '2026-10-16', 84.50, 'Sangat Tinggi', 'Dipertahankan', 'Penataan kawasan konservasi pesisir di Pulau Weh mencapai 72,25 Ha.', 'Sinkronkan batas zona konservasi laut dengan peta tutupan lahan wilayah pesisir.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-020', 'PRG-013', 'KEG-021', 'RLS-025', 'Triwulan III 2026', '2026-10-16', 77.50, 'Tinggi', 'Perlu Percepatan', 'Penanganan sampah pesisir di Aceh Selatan mencapai 390 ton dari target 500 ton.', 'Optimalkan jadwal operasi pembersihan pantai saat kondisi cuaca perairan kondusif.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-021', 'PRG-014', 'KEG-022', 'RLS-029', 'Triwulan III 2026', '2026-10-16', 77.50, 'Tinggi', 'Dipertahankan', 'Pembentukan kampung siaga bencana di kawasan pesisir Banda Aceh melampaui target triwulan III.', 'Lakukan simulasi evakuasi terpadu sebelum memasuki puncak musim penghujan.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-022', 'PRG-016', 'KEG-024', 'RLS-031', 'Triwulan III 2026', '2026-10-16', 0.00, 'Sangat Rendah', 'Evaluasi Ulang', 'Kegiatan normalisasi sungai di Peukan Bada belum berjalan akibat kendala pembebasan lahan.', 'Jadwalkan ulang pelaksanaan fisik dan realokasikan sisa anggaran jika lahan belum siap hingga November.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-039', 'PRG-025', 'KEG-040', 'RLS-074', 'Akhir Tahun 2024', '2024-12-27', 99.00, 'Sangat Tinggi', 'Dipertahankan', 'Penataan RTH dan sempadan sungai di Aceh Tamiang tuntas 100%.', 'Pertahankan pengawasan zonasi sempadan sungai bersama perangkat kecamatan.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-040', 'PRG-025', 'KEG-041', 'RLS-075', 'Akhir Tahun 2024', '2024-12-27', 97.50, 'Sangat Tinggi', 'Dipertahankan', 'Rehabilitasi daerah tangkapan air Danau Lut Tawar tercapai 98%.', 'Lanjutkan pengendalian erosi lahan miring di sekitar kawasan danau.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-041', 'PRG-026', 'KEG-042', 'RLS-076', 'Akhir Tahun 2024', '2024-12-27', 98.50, 'Sangat Tinggi', 'Dipertahankan', 'Penguatan tebing Sungai Alas sepanjang 7,20 km di Aceh Tenggara selesai tepat waktu.', 'Lakukan inspeksi berkala terhadap struktur bronjong pasca musim hujan.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-042', 'PRG-026', 'KEG-043', 'RLS-077', 'Akhir Tahun 2024', '2024-12-27', 97.50, 'Sangat Tinggi', 'Dipertahankan', 'Rehabilitasi saluran irigasi teknis di Aceh Utara mencapai 98% dengan serapan 97%.', 'Optimalkan pembagian jadwal tanam bersama perkumpulan petani pemakai air.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-043', 'PRG-027', 'KEG-044', 'RLS-078', 'Akhir Tahun 2025', '2025-12-28', 98.50, 'Sangat Tinggi', 'Dipertahankan', 'Perlindungan lahan pangan seluas 260 Ha di Gayo Lues tuntas.', 'Integrasikan peta lahan pertanian dilindungi ke dalam dokumen tata ruang daerah.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-044', 'PRG-027', 'KEG-045', 'RLS-079', 'Akhir Tahun 2025', '2025-12-28', 97.50, 'Sangat Tinggi', 'Dipertahankan', 'Optimalisasi tata air sawah di Kabupaten Pidie mencapai 98% dari target.', 'Lanjutkan pemeliharaan pintu air sekunder secara berkala.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-045', 'PRG-028', 'KEG-046', 'RLS-080', 'Akhir Tahun 2025', '2025-12-28', 99.00, 'Sangat Tinggi', 'Dipertahankan', 'Penanaman sabuk hijau mangrove seluas 140 Ha di Pidie Jaya selesai seluruhnya.', 'Libatkan kelompok masyarakat pesisir dalam pemantauan pertumbuhan bibit mangrove.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-046', 'PRG-028', 'KEG-047', 'RLS-081', 'Akhir Tahun 2025', '2025-12-28', 97.50, 'Sangat Tinggi', 'Dipertahankan', 'Penanganan sampah pesisir di Kabupaten Simeulue mencapai 637 ton.', 'Perkuat armada pengumpulan sampah pada titik dermaga dan pemukiman pesisir.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-047', 'PRG-029', 'KEG-048', 'RLS-084', 'Triwulan III 2026', '2026-10-16', 79.00, 'Tinggi', 'Dipertahankan', 'Pengelolaan sampah TPA regional Bireuen mencapai 80% dengan serapan anggaran 78%.', 'Perluas operasional bank sampah unit di kecamatan padat penduduk.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-048', 'PRG-029', 'KEG-049', 'RLS-087', 'Triwulan III 2026', '2026-10-16', 82.17, 'Sangat Tinggi', 'Dipertahankan', 'Pemantauan kualitas udara di Nagan Raya berjalan optimal pada 15 titik pantau.', 'Tindak lanjuti hasil pemantauan partikulat dengan pengawasan cerobong emisi industri.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-049', 'PRG-029', 'KEG-050', 'RLS-090', 'Triwulan III 2026', '2026-10-16', 77.00, 'Tinggi', 'Perlu Percepatan', 'Penataan RTH di Kota Subulussalam mencapai 85,80 Ha dari target 110 Ha.', 'Percepat penyelesaian penanaman koridor hijau pada triwulan IV.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-050', 'PRG-030', 'KEG-051', 'RLS-092', 'Triwulan III 2026', '2026-10-16', 84.36, 'Sangat Tinggi', 'Dipertahankan', 'Audit izin lingkungan usaha pengolahan kopi di Bener Meriah mencapai 24 dokumen.', 'Dorong penerapan instalasi pengolahan air limbah kopi ramah lingkungan.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-051', 'PRG-030', 'KEG-052', 'RLS-094', 'Triwulan III 2026', '2026-10-16', 80.91, 'Sangat Tinggi', 'Dipertahankan', 'Pemantauan kualitas air sungai di Aceh Timur terealisasi pada 18 stasiun.', 'Jadwalkan ulang pengambilan sampel pada titik hulu saat kondisi cuaca stabil.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-052', 'PRG-029', 'KEG-053', 'RLS-095', 'Triwulan III 2026', '2026-10-16', 76.00, 'Tinggi', 'Perlu Percepatan', 'Pengolahan sampah organik di Aceh Tamiang mencapai 1.463 ton dari target 1.900 ton.', 'Optimalkan kapasitas rumah kompos pada triwulan IV.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-053', 'PRG-030', 'KEG-054', 'RLS-096', 'Triwulan III 2026', '2026-10-16', 67.00, 'Sedang', 'Evaluasi Ulang', 'Pemasangan pembangkit mikrohidro di Aceh Tengah terhambat pengiriman komponen.', 'Gunakan jalur logistik alternatif agar instalasi selesai sebelum akhir tahun.', 'Badan Perencanaan Pembangunan Daerah Aceh'),
('EVL-054', 'PRG-029', 'KEG-055', 'RLS-097', 'Triwulan III 2026', '2026-10-16', 83.19, 'Sangat Tinggi', 'Dipertahankan', 'Audit kepatuhan limbah industri di Aceh Utara mencapai 27 perusahaan.', 'Terbitkan laporan evaluasi kepatuhan semester II sebagai bahan pembinaan industri.', 'Badan Perencanaan Pembangunan Daerah Aceh');

-- --------------------------------------------------------

--
-- Table structure for table `tb_kegiatan`
--

CREATE TABLE `tb_kegiatan` (
  `id_kegiatan` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_program` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `kode_kegiatan` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nama_kegiatan` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_desa` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nama_desa` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_kecamatan` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nama_kecamatan` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_kabupaten_kota` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nama_kabupaten_kota` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pagu_anggaran_kegiatan` decimal(18,2) NOT NULL DEFAULT '0.00',
  `tanggal_mulai` date NOT NULL,
  `tanggal_selesai` date NOT NULL,
  `status_kegiatan` enum('Belum Mulai','Berjalan','Selesai','Terkendala') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Berjalan'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tb_kegiatan`
--

INSERT INTO `tb_kegiatan` (`id_kegiatan`, `id_program`, `kode_kegiatan`, `nama_kegiatan`, `id_desa`, `nama_desa`, `id_kecamatan`, `nama_kecamatan`, `id_kabupaten_kota`, `nama_kabupaten_kota`, `pagu_anggaran_kegiatan`, `tanggal_mulai`, `tanggal_selesai`, `status_kegiatan`) VALUES
('KEG-001', 'PRG-001', '2.11.03.1.01', 'Optimalisasi Pengelolaan Sampah dan Kapasitas Fasilitas TPA/TPS 3R', '07011', 'Desa Lhoknga', '0701', 'Kecamatan Lhoknga', '07', 'Kabupaten Aceh Besar', 2500000000.00, '2026-02-01', '2026-11-30', 'Berjalan'),
('KEG-002', 'PRG-001', '2.11.03.1.02', 'Penataan dan Perluasan Kawasan Ruang Terbuka Hijau (RTH) Perkotaan', '01011', 'Desa Peuniti', '0101', 'Kecamatan Baiturrahman', '01', 'Kota Banda Aceh', 2000000000.00, '2026-02-15', '2026-11-30', 'Berjalan'),
('KEG-003', 'PRG-002', '2.11.04.1.01', 'Pemantauan Baku Mutu Air Sungai dan Kualitas Udara Ambien', '05012', 'Desa Ujung Kalak', '0501', 'Kecamatan Meulaboh', '05', 'Kabupaten Aceh Barat', 1800000000.00, '2026-01-20', '2026-12-15', 'Berjalan'),
('KEG-004', 'PRG-002', '2.11.04.1.02', 'Pembinaan dan Pengawasan Ketaatan Dokumen Izin Lingkungan Usaha', '04031', 'Desa Blang Mangat', '0403', 'Kecamatan Blang Mangat', '04', 'Kota Lhokseumawe', 1400000000.00, '2026-02-10', '2026-11-25', 'Berjalan'),
('KEG-005', 'PRG-003', '3.29.02.1.01', 'Pengawasan Kegiatan Pertambangan Mineral dan Konservasi Air Tanah', '09011', 'Desa Tapaktuan', '0901', 'Kecamatan Tapaktuan', '09', 'Kabupaten Aceh Selatan', 2800000000.00, '2026-03-01', '2026-12-10', 'Terkendala'),
('KEG-006', 'PRG-004', '1.03.05.1.01', 'Rehabilitasi Jaringan Irigasi dan Pengendalian Daya Rusak Air', '08041', 'Desa Teunom', '0804', 'Kecamatan Teunom', '08', 'Kabupaten Aceh Jaya', 5000000000.00, '2026-02-05', '2026-12-20', 'Berjalan'),
('KEG-007', 'PRG-005', '3.27.03.1.01', 'Perlindungan Kawasan Sawah dan Lahan Pertanian Pangan Berkelanjutan', '07052', 'Desa Neunom', '0705', 'Kecamatan Baitussalam', '07', 'Kabupaten Aceh Besar', 3600000000.00, '2026-01-25', '2026-11-30', 'Berjalan'),
('KEG-008', 'PRG-006', '5.01.02.1.01', 'Evaluasi Capaian Kinerja Pembangunan Kabupaten/Kota Se-Aceh', '01031', 'Desa Pocut Baren', '0103', 'Kecamatan Kuta Alam', '01', 'Kota Banda Aceh', 1500000000.00, '2025-02-01', '2025-12-20', 'Selesai'),
('KEG-009', 'PRG-007', '2.11.05.1.01', 'Rehabilitasi Kawasan Hutan Lindung dan Penanaman Mangrove Pesisir', '02012', 'Desa Sabang Kota', '0201', 'Kecamatan Sabang', '02', 'Kota Sabang', 2100000000.00, '2025-02-10', '2025-11-25', 'Selesai'),
('KEG-010', 'PRG-007', '2.11.05.1.02', 'Pemulihan Ekosistem Lahan Basah dan Konservasi Rawa Gambut', '10011', 'Desa Singkil', '1001', 'Kecamatan Singkil', '10', 'Kabupaten Aceh Singkil', 2000000000.00, '2025-03-01', '2025-12-10', 'Selesai'),
('KEG-011', 'PRG-008', '2.11.06.1.01', '  Pembangunan Fasilitas Pengolahan Sampah Terpadu dan Limbah Industri  ', '4011', 'desa muara batu', '401', 'KECAMATAN MUARA BATU', '4', 'kota lhokseumawe', 2250000000.00, '2026-02-01', '2026-11-30', 'Berjalan'),
('KEG-012', 'PRG-008', '2.11.06.1.02', 'Pembangunan Fasilitas Pengolahan Sampah Terpadu dan Limbah Industri', '04011', 'Desa Muara Batu', '0401', 'Kecamatan Muara Batu', '04', 'Kota Lhokseumawe', 1500000000.00, '2026-02-01', '2026-11-30', 'Berjalan'),
('KEG-013', 'PRG-009', '1.02.02.1.01', 'Peningkatan Layanan Puskesmas dan Pemantauan Sanitasi Lingkungan', '1012', 'Ds. Punge Blang Cut', '101', 'Kec. Baiturrahman', '1', 'Banda Aceh', 3200000000.00, '2026-01-15', '2026-12-15', 'Berjalan'),
('KEG-014', 'PRG-009', '1.02.02.1.02', 'Pengadaan Alat Kesehatan dan Pengolahan Limbah Medis Rumah Sakit', '03011', 'Desa Blang Jurong', '0301', 'Kecamatan Langsa Barat', '03', 'Kota Langsa', 3000000000.00, '2026-02-12', '2026-11-28', 'Berjalan'),
('KEG-015', 'PRG-010', '1.02.03.1.01', 'Pembangunan Sarana Air Bersih dan Sanitasi Berbasis Masyarakat', '06011', 'Desa Blangpidie', '0601', 'Kecamatan Blangpidie', '06', 'Kabupaten Aceh Barat Daya', 0.00, '2025-03-10', '2025-11-20', 'Selesai'),
('KEG-016', 'PRG-010', '1.02.03.1.02', 'Pengawasan Kualitas Air Minum Desa dan Pengendalian Vektor Penyakit', '06021', 'Desa Manggeng', '0602', 'Kecamatan Manggeng', '06', 'Kabupaten Aceh Barat Daya', 1450000000.00, '2025-02-20', '2025-11-30', 'Selesai'),
('KEG-017', 'PRG-011', '1.01.02.1.01', 'Revitalisasi Ruang Kelas dan Laboratorium Sekolah Menengah Kejuruan', '07091', 'Desa Mesjid Raya', '0709', 'Kecamatan Mesjid Raya', '07', 'KAB. ACEH BESAR', 4500000000.00, '2026-08-01', '2026-04-10', 'Berjalan'),
('KEG-018', 'PRG-011', '1.01.02.1.02', 'Pengembangan Sekolah Adiwiyata dan Kurikulum Literasi Lingkungan', '05011', 'Desa Meulaboh', '0501', 'Kecamatan Meulaboh', '05', 'Kabupaten Aceh Barat', 4000000000.00, '2026-01-20', '2026-11-30', 'Berjalan'),
('KEG-019', 'PRG-012', '2.15.02.1.01', 'Pemasangan Penerangan Jalan Umum Tenaga Surya dan Rambu Lalu Lintas', '08012', 'Desa Panggang', '0801', 'Kecamatan Seulimeum', '08', 'Kabupaten Aceh Jaya', 3300000000.00, '2026-03-01', '2026-12-05', 'Berjalan'),
('KEG-020', 'PRG-013', '3.25.02.1.01', 'Konservasi Terumbu Karang dan Perlindungan Sempadan Pantai', '02021', 'Desa   Iboih ', '0202', 'Kecamatan Pulau Weh', '02', 'Kota Sabang', 1500000000.00, '2026-02-15', '2026-11-20', 'Berjalan'),
('KEG-021', 'PRG-013', '3.25.02.1.02', 'Pemberdayaan Nelayan Pesisir dan Pengelolaan Sampah Laut', '09031', 'Desa Labuhan Haji', '0903', 'Kecamatan Labuhan Haji', '09', 'Kab. Aceh Selatan', 1200000000.00, '2026-03-05', '2026-11-25', 'Berjalan'),
('KEG-022', 'PRG-014', '1.06.02.1.01', 'Penguatan Kampung Siaga Bencana dan Logistik Tanggap Darurat Banjir', '01052', 'Desa Deah Raya', '0105', 'Kecamatan Meuraxa', '01', 'Kota Banda Aceh', 4400000000.00, '2026-01-10', '2026-12-15', 'Berjalan'),
('KEG-023', 'PRG-015', '3.29.03.1.01', 'Pembangunan Pembangkit Listrik Tenaga Surya Terpusat Wilayah Terpencil', '09051', 'Desa Sama Dua', '0905', 'Kecamatan Sama Dua', '09', 'Kabupaten Aceh Selatan', 3100000000.00, '2024-02-15', '2024-11-30', 'Selesai'),
('KEG-024', 'PRG-016', '1.03.06.1.01', 'Normalisasi Daerah Aliran Sungai dan Pengendalian Banjir', '07111', 'Desa Peukan Bada', '0711', 'Kecamatan Peukan Bada', '07', 'Kabupaten Aceh Besar', 4800000000.00, '2026-04-01', '2026-12-20', 'Belum Mulai'),
('KEG-040', 'PRG-025', '2.11.07.24.01', 'Rehabilitasi Sempadan Sungai dan Penataan Ruang Terbuka Hijau Karang Baru', '11011', 'Desa Tanah Terban', '1101', 'Kecamatan Karang Baru', '11', 'Kabupaten Aceh Tamiang', 1700000000.00, '2024-02-05', '2024-11-25', 'Selesai'),
('KEG-041', 'PRG-025', '2.11.07.24.02', 'Konservasi Daerah Tangkapan Air Danau Lut Tawar', '12011', 'Desa Takengon Timur', '1201', 'Kecamatan Lut Tawar', '12', 'Kabupaten Aceh Tengah', 1800000000.00, '2024-02-12', '2024-11-30', 'Selesai'),
('KEG-042', 'PRG-026', '1.03.07.24.01', 'Penguatan Tebing Sungai Alas dan Pengendalian Banjir Babussalam', '13011', 'Desa Kutacane Lama', '1301', 'Kecamatan Babussalam', '13', 'Kabupaten Aceh Tenggara', 2300000000.00, '2024-02-01', '2024-12-05', 'Selesai'),
('KEG-043', 'PRG-026', '1.03.07.24.02', 'Rehabilitasi Saluran Irigasi Teknis Daerah Aliran Krueng Pase', '14011', 'Desa Kuta Lhoksukon', '1401', 'Kecamatan Lhoksukon', '14', 'Kabupaten Aceh Utara', 2600000000.00, '2024-02-15', '2024-12-10', 'Selesai'),
('KEG-044', 'PRG-027', '3.27.04.25.01', 'Perlindungan Lahan Pertanian Pangan Berkelanjutan Wilayah Dataran Tinggi', '15011', 'Desa Kota Blangkejeren', '1501', 'Kecamatan Blangkejeren', '15', 'Kabupaten Gayo Lues', 1600000000.00, '2025-02-01', '2025-11-20', 'Selesai'),
('KEG-045', 'PRG-027', '3.27.04.25.02', 'Optimalisasi Jaringan Tata Air Sawah Kabupaten Pidie', '16011', 'Desa Kramat Dalam', '1601', 'Kecamatan Kota Sigli', '16', 'Kabupaten Pidie', 1700000000.00, '2025-02-10', '2025-11-28', 'Selesai'),
('KEG-046', 'PRG-028', '3.25.03.25.01', 'Penanaman Sabuk Hijau Mangrove Pesisir Meureudu', '17011', 'Desa Kota Meureudu', '1701', 'Kecamatan Meureudu', '17', 'Kabupaten Pidie Jaya', 1350000000.00, '2025-02-15', '2025-11-25', 'Selesai'),
('KEG-047', 'PRG-028', '3.25.03.25.02', 'Pengelolaan Sampah Pesisir dan Konservasi Ekosistem Laut Simeulue', '18011', 'Desa Sinabang', '1801', 'Kecamatan Simeulue Timur', '18', 'Kabupaten Simeulue', 1450000000.00, '2025-03-01', '2025-12-05', 'Selesai'),
('KEG-048', 'PRG-029', '2.11.08.26.01', 'Peningkatan Kapasitas TPA Regional dan Bank Sampah Kota Juang', '19011', 'Desa Bandar Bireuen', '1901', 'Kecamatan Kota Juang', '19', 'Kabupaten Bireuen', 1800000000.00, '2026-02-01', '2026-11-30', 'Berjalan'),
('KEG-049', 'PRG-029', '2.11.08.26.02', 'Pemantauan Kualitas Udara Ambien dan Pengendalian Emisi Industri', '20011', 'Desa Ujong Fatihah', '2001', 'Kecamatan Kuala', '20', 'Kabupaten Nagan Raya', 1650000000.00, '2026-02-10', '2026-12-05', 'Berjalan'),
('KEG-050', 'PRG-029', '2.11.08.26.03', 'Penataan Ruang Terbuka Hijau dan Pengelolaan Persampahan Kota Subulussalam', '21011', 'desa subulussalam', '2101', 'Kec. Simpang Kiri', '21', 'kota subulussalam', 1550000000.00, '2026-02-15', '2026-11-28', 'Berjalan'),
('KEG-051', 'PRG-030', '3.29.04.26.01', 'Pengawasan Ketaatan Izin Lingkungan Industri Pengolahan Kopi', '22011', 'Desa Bale Atu', '2201', 'Kecamatan Bukit', '22', 'Kabupaten Bener Meriah', 1400000000.00, '2026-02-05', '2026-11-25', 'Berjalan'),
('KEG-052', 'PRG-030', '3.29.04.26.02', 'Pemantauan Kualitas Air Sungai dan Konservasi Air Tanah Idi Rayeuk', '23011', 'Desa Tanoh Anou', '2301', 'Kecamatan Idi Rayeuk', '23', 'Kabupaten Aceh Timur', 1750000000.00, '2026-02-12', '2026-12-10', 'Berjalan'),
('KEG-053', 'PRG-029', '2.11.08.26.04', '  Pengembangan Fasilitas Pemilahan Sampah Organik Terpadu  ', '11011', 'Desa Tanah Terban', '1101', 'Kecamatan Karang Baru', '11', 'kabupaten aceh tamiang', 1800000000.00, '2026-01-25', '2026-11-30', 'Berjalan'),
('KEG-054', 'PRG-030', '3.29.04.26.03', 'Pengembangan Mikrohidro dan Energi Terbarukan Pedesaan Aceh Tengah', '12011', 'Desa Takengon Timur', '1201', 'Kecamatan Lut Tawar', '12', 'Kabupaten Aceh Tengah', 1450000000.00, '2026-02-20', '2026-12-01', 'Terkendala'),
('KEG-055', 'PRG-029', '2.11.08.26.05', 'Audit Kepatuhan Pengelolaan Limbah Cair dan Emisi Kawasan Industri', '14011', 'Desa Kuta Lhoksukon', '1401', 'Kecamatan Lhoksukon', '14', 'KAB. ACEH UTARA', 1900000000.00, '2026-02-01', '2026-12-15', 'Berjalan');

-- --------------------------------------------------------

--
-- Table structure for table `tb_program`
--

CREATE TABLE `tb_program` (
  `id_program` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_skpa` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `kode_program` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nama_program` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `bidang_urusan` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tahun_anggaran` year NOT NULL,
  `sumber_dana` enum('APBA','APBN','Non-APBA / Hibah') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'APBA',
  `pagu_anggaran_program` decimal(18,2) NOT NULL DEFAULT '0.00',
  `status_program` enum('Direncanakan','Berjalan','Selesai','Ditunda') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Berjalan'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tb_program`
--

INSERT INTO `tb_program` (`id_program`, `id_skpa`, `kode_program`, `nama_program`, `bidang_urusan`, `tahun_anggaran`, `sumber_dana`, `pagu_anggaran_program`, `status_program`) VALUES
('PRG-001', 'SKPA-01', '2.11.03', 'Program Pengelolaan Persampahan dan Ruang Terbuka Hijau', 'Lingkungan Hidup dan Kehutanan', '2026', 'APBA', 4500000000.00, 'Berjalan'),
('PRG-002', 'SKPA-01', '2.11.04', 'Program Pengendalian Pencemaran dan Perizinan Lingkungan', 'Lingkungan Hidup dan Kehutanan', '2026', 'APBA', 3200000000.00, 'Berjalan'),
('PRG-003', 'SKPA-02', '3.29.02', 'Program Pengawasan Pertambangan dan Konservasi Air Tanah', 'Energi dan Sumber Daya Mineral', '2026', 'APBA', 2800000000.00, 'Berjalan'),
('PRG-004', 'SKPA-03', '1.03.05', 'Program Pengelolaan Sumber Daya Air dan Jaringan Irigasi', 'Pekerjaan Umum dan Pengairan', '2026', 'APBN', 5000000000.00, 'Berjalan'),
('PRG-005', 'SKPA-04', '3.27.03', 'Program Perlindungan Lahan Pertanian dan Ketahanan Pangan', 'Pertanian dan Pangan', '2026', 'APBA', 3600000000.00, 'Berjalan'),
('PRG-006', 'SKPA-05', '5.01.02', 'Program Pengendalian, Evaluasi dan Pelaporan Pembangunan Daerah', 'Perencanaan Pembangunan Daerah', '2025', 'APBA', 1500000000.00, 'Selesai'),
('PRG-007', 'SKPA-01', '2.11.05', 'Program Rehabilitasi Hutan, Lahan Kritis dan Konservasi Ekosistem', 'Lingkungan Hidup dan Kehutanan', '2025', 'APBA', 4100000000.00, 'Selesai'),
('PRG-008', 'SKPA-01', '2.11.06', '  Program Peningkatan Sarana Prasarana Pengelolaan Limbah B3  ', 'Lingkungan Hidup dan Kehutanan', '2026', 'APBN', 3750000000.00, 'Berjalan'),
('PRG-009', 'SKPA-06', '1.02.02', 'Program Pemenuhan Upaya Kesehatan Perorangan dan Masyarakat', 'Kesehatan', '2026', 'APBA', 6200000000.00, 'Berjalan'),
('PRG-010', 'SKPA-06', '1.02.03', 'Program Penyehatan Lingkungan Permukiman dan Sanitasi Dasar', 'Kesehatan', '2025', 'APBN', 2900000000.00, 'Selesai'),
('PRG-011', 'SKPA-07', '1.01.02', 'Program Pengelolaan Pendidikan Menengah dan Kejuruan', 'pendidikan', '2026', 'APBA', 8500000000.00, 'Berjalan'),
('PRG-012', 'SKPA-08', '2.15.02', 'Program Penyelenggaraan Lalu Lintas dan Angkutan Jalan', 'Perhubungan dan Transportasi', '2026', 'APBA', 3300000000.00, 'Berjalan'),
('PRG-013', 'SKPA-09', '3.25.02', 'Program Pengelolaan Perikanan Tangkap dan Konservasi Pesisir', 'Kelautan dan Perikanan', '2026', 'Non-APBA / Hibah', 2700000000.00, 'Berjalan'),
('PRG-014', 'SKPA-10', '1.06.02', 'Program Perlindungan dan Jaminan Sosial Korban Bencana Alam', 'Sosial dan Penanggulangan Bencana', '2026', 'APBA', 4400000000.00, 'Berjalan'),
('PRG-015', 'SKPA-02', '3.29.03', 'Program Pengembangan Energi Baru Terbarukan Pedesaan', 'Energi dan Sumber Daya Mineral', '2024', 'APBN', 3100000000.00, 'Selesai'),
('PRG-016', 'SKPA-03', '1.03.06', 'Program Pengelolaan Sumber Daya Air Terpadu Wilayah Sungai', 'Pekerjaan Umum dan Pengairan', '2026', 'APBA', 4800000000.00, 'Ditunda'),
('PRG-025', 'SKPA-01', '2.11.07.24', 'Program Pengendalian Kerusakan Lingkungan Wilayah Timur dan Tengah 2024', 'Lingkungan Hidup dan Kehutanan', '2024', 'APBA', 3500000000.00, 'Selesai'),
('PRG-026', 'SKPA-03', '1.03.07.24', 'Program Pengelolaan Jaringan Irigasi Wilayah Tenggara dan Utara 2024', 'Pekerjaan Umum dan Pengairan', '2024', 'APBN', 4900000000.00, 'Selesai'),
('PRG-027', 'SKPA-04', '3.27.04.25', 'Program Ketahanan Pangan dan Konservasi Lahan Pertanian 2025', 'Pertanian dan Pangan', '2025', 'APBA', 3300000000.00, 'Selesai'),
('PRG-028', 'SKPA-09', '3.25.03.25', 'Program Rehabilitasi Pesisir dan Pulau-Pulau Kecil 2025', 'Kelautan dan Perikanan', '2025', 'Non-APBA / Hibah', 2800000000.00, 'Selesai'),
('PRG-029', 'SKPA-01', '2.11.08.26', 'Program Pengelolaan Sampah Terpadu dan RTH Lintas Kabupaten 2026', 'Lingkungan Hidup dan Kehutanan', '2026', 'APBA', 6800000000.00, 'Berjalan'),
('PRG-030', 'SKPA-02', '3.29.04.26', 'Program Konservasi Energi dan Pengawasan Lingkungan Usaha 2026', 'Energi dan Sumber Daya Mineral', '2026', 'APBN', 4600000000.00, 'Berjalan');

-- --------------------------------------------------------

--
-- Table structure for table `tb_realisasi`
--

CREATE TABLE `tb_realisasi` (
  `id_realisasi` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_kegiatan` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_target` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tanggal_lapor` date NOT NULL,
  `triwulan` enum('TW1','TW2','TW3','TW4') COLLATE utf8mb4_unicode_ci NOT NULL,
  `realisasi_fisik_nilai` decimal(12,2) NOT NULL,
  `realisasi_fisik_persen` decimal(5,2) NOT NULL,
  `realisasi_anggaran` decimal(18,2) NOT NULL,
  `serapan_anggaran_persen` decimal(5,2) NOT NULL,
  `kendala_lapangan` text COLLATE utf8mb4_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tb_realisasi`
--

INSERT INTO `tb_realisasi` (`id_realisasi`, `id_kegiatan`, `id_target`, `tanggal_lapor`, `triwulan`, `realisasi_fisik_nilai`, `realisasi_fisik_persen`, `realisasi_anggaran`, `serapan_anggaran_persen`, `kendala_lapangan`) VALUES
('RLS-001', 'KEG-001', 'TRG-001', '2026-10-10', 'TW3', 2205.00, 73.50, 1850000000.00, 74.00, 'Lonjakan volume sampah campuran di Aceh Besar memerlukan penambahan unit pemilahan di TPS 3R.'),
('RLS-002', 'KEG-002', 'TRG-002', '2026-10-12', 'TW3', 112.50, 75.00, 1520000000.00, 76.00, 'Keterbatasan lahan aset pemerintah daerah di kawasan pusat kota Banda Aceh.'),
('RLS-003', 'KEG-003', 'TRG-003', '2026-10-08', 'TW3', 22.00, 81.48, 1440000000.00, 80.00, 'Kalibrasi sensor kualitas udara pada 2 titik pantau pesisir membutuhkan suku cadang tambahan.'),
('RLS-004', 'KEG-004', 'TRG-004', '2026-10-11', 'TW3', 31.00, 88.57, 1190000000.00, 85.00, 'Beberapa badan usaha belum memperbarui pelaporan semesteran UKL-UPL dan SPPL.'),
('RLS-005', 'KEG-005', 'TRG-005', '2026-10-09', 'TW3', 14.00, 70.00, 1904000000.00, 68.00, 'Akses menuju titik pantau di wilayah pegunungan Aceh Selatan terkendala curah hujan tinggi.'),
('RLS-006', 'KEG-006', 'TRG-006', '2026-10-12', 'TW3', 9.00, 72.00, 3500000000.00, 70.00, 'Penyesuaian debit air sungai selama musim penghujan memperlambat pekerjaan fisik.'),
('RLS-007', 'KEG-007', 'TRG-007', '2026-10-13', 'TW3', 360.00, 80.00, 2808000000.00, 78.00, 'Sinkronisasi peta poligon lahan sawah dengan data tata ruang kabupaten berjalan bertahap.'),
('RLS-008', 'KEG-008', 'TRG-008', '2025-12-20', 'TW4', 23.00, 100.00, 1455000000.00, 97.00, NULL),
('RLS-009', 'KEG-009', 'TRG-009', '2025-12-15', 'TW4', 320.00, 100.00, 2058000000.00, 98.00, NULL),
('RLS-010', 'KEG-010', 'TRG-010', '2025-12-18', 'TW4', 274.40, 98.00, 1940000000.00, 97.00, '-'),
('RLS-011', 'KEG-011', 'TRG-011', '2026-04-05', 'TW1', 420.00, 23.33, 520000000.00, 23.11, ''),
('RLS-012', 'KEG-011', 'TRG-012', '2026-07-08', 'TW2', 880.00, 48.89, 1080000000.00, 48.00, 'N/A'),
('RLS-013', 'KEG-011', 'TRG-013', '2026-10-09', 'TW3', 1320.00, 73.33, 1620000000.00, 72.00, 'Keterlambatan pengiriman mesin pencacah organik.'),
('RLS-014', 'KEG-011', 'TRG-013', '2026-10-09', 'TW3', 1320.00, 73.33, 1620000000.00, 72.00, '  Keterlambatan pengiriman mesin pencacah organik.  '),
('RLS-015', 'KEG-012', 'TRG-014', '2026-10-11', 'TW3', 2385.00, 132.50, 1425000000.00, 95.00, 'Volume kiriman sampah industri melebihi kapasitas rencana awal.'),
('RLS-016', 'KEG-013', 'TRG-015', '2026-10-12', 'TW3', 15.00, 83.33, 2560000000.00, 80.00, 'Tidak ada kendala'),
('RLS-017', 'KEG-014', 'TRG-016', '2026-07-15', 'TW2', 6.00, 60.00, 1800000000.00, 60.00, NULL),
('RLS-018', 'KEG-014', 'TRG-016', '2026-10-14', 'TW3', 6.00, 60.00, -45000000.00, -1.50, 'Koreksi pengembalian kelebihan pembayaran termin II.'),
('RLS-019', 'KEG-015', 'TRG-017', '2025-12-10', 'TW4', 25.00, 100.00, 1421000000.00, 98.00, NULL),
('RLS-020', 'KEG-016', 'TRG-018', '2025-12-12', 'TW4', 120.00, 100.00, 1435500000.00, 99.00, ''),
('RLS-021', 'KEG-017', 'TRG-019', '1970-01-01', 'TW3', 21.00, 70.00, 3150000000.00, 70.00, 'Penyesuaian jadwal libur semester sekolah.'),
('RLS-022', 'KEG-018', 'TRG-020', '2026-10-10', 'TW3', 34.00, 85.00, 3320000000.00, 83.00, '-'),
('RLS-023', 'KEG-019', 'TRG-021', '2026-10-13', 'TW3', 114.00, 76.00, 2475000000.00, 75.00, 'Pengiriman tiang PJU terhambat perbaikan jembatan lintas barat.'),
('RLS-024', 'KEG-020', 'TRG-022', '2026-10-11', 'TW3', 72.25, 85.00, 1260000000.00, 84.00, NULL),
('RLS-025', 'KEG-021', 'TRG-023', '2026-10-12', 'TW3', 390.00, 78.00, 924000000.00, 77.00, 'Gelombang tinggi membatasi operasi kapal pembersih pesisir.'),
('RLS-026', 'KEG-022', 'TRG-024', '2026-04-08', 'TW1', 5.00, 25.00, 1080000000.00, 24.55, NULL),
('RLS-027', 'KEG-022', 'TRG-025', '2026-07-10', 'TW2', 10.00, 50.00, 2150000000.00, 48.86, NULL),
('RLS-028', 'KEG-022', 'TRG-026', '2026-10-14', 'TW3', 15.00, 75.00, 3250000000.00, 73.86, 'N/A'),
('RLS-029', 'KEG-022', 'TRG-026', '2026-10-14', 'TW3', 16.00, 80.00, 3300000000.00, 75.00, 'Pembaruan data desa binaan.'),
('RLS-030', 'KEG-023', 'TRG-027', '2024-12-18', 'TW4', 250.00, 100.00, 3038000000.00, 98.00, NULL),
('RLS-031', 'KEG-024', 'TRG-028', '2026-10-15', 'TW3', 0.00, 0.00, 0.00, 0.00, 'Menunggu penyelesaian pembebasan lahan bantaran sungai.'),
('RLS-032', 'KEG-001', 'TRG-001', '2026-07-05', 'TW2', 1480.00, 49.33, 1225000000.00, 49.00, 'Operasional pemilahan sampah berjalan bertahap.'),
('RLS-074', 'KEG-040', 'TRG-044', '2024-12-16', 'TW4', 95.00, 100.00, 1666000000.00, 98.00, NULL),
('RLS-075', 'KEG-041', 'TRG-045', '2024-12-18', 'TW4', 205.80, 98.00, 1746000000.00, 97.00, '-'),
('RLS-076', 'KEG-042', 'TRG-046', '2024-12-19', 'TW4', 7.20, 100.00, 2231000000.00, 97.00, NULL),
('RLS-077', 'KEG-043', 'TRG-047', '2024-12-20', 'TW4', 10.29, 98.00, 2522000000.00, 97.00, NULL),
('RLS-078', 'KEG-044', 'TRG-048', '2025-12-15', 'TW4', 260.00, 100.00, 1552000000.00, 97.00, NULL),
('RLS-079', 'KEG-045', 'TRG-049', '2025-12-17', 'TW4', 372.40, 98.00, 1649000000.00, 97.00, ''),
('RLS-080', 'KEG-046', 'TRG-050', '2025-12-16', 'TW4', 140.00, 100.00, 1323000000.00, 98.00, NULL),
('RLS-081', 'KEG-047', 'TRG-051', '2025-12-18', 'TW4', 637.00, 98.00, 1406500000.00, 97.00, NULL),
('RLS-082', 'KEG-048', 'TRG-052', '2026-04-07', 'TW1', 624.00, 26.00, 450000000.00, 25.00, NULL),
('RLS-083', 'KEG-048', 'TRG-052', '2026-07-08', 'TW2', 1296.00, 54.00, 936000000.00, 52.00, NULL),
('RLS-084', 'KEG-048', 'TRG-052', '2026-10-11', 'TW3', 1920.00, 80.00, 1404000000.00, 78.00, 'Penambahan jadwal angkut sampah pasar Kecamatan Kota Juang.'),
('RLS-085', 'KEG-049', 'TRG-053', '2026-04-08', 'TW1', 5.00, 27.78, 429000000.00, 26.00, NULL),
('RLS-086', 'KEG-049', 'TRG-053', '2026-07-09', 'TW2', 10.00, 55.56, 891000000.00, 54.00, NULL),
('RLS-087', 'KEG-049', 'TRG-053', '2026-10-12', 'TW3', 15.00, 83.33, 1336500000.00, 81.00, 'Kalibrasi sensor partikulat PM10 di sekitar kawasan industri.'),
('RLS-088', 'KEG-050', 'TRG-054', '2026-04-09', 'TW1', 27.50, 25.00, 372000000.00, 24.00, NULL),
('RLS-089', 'KEG-050', 'TRG-054', '2026-07-10', 'TW2', 57.20, 52.00, 775000000.00, 50.00, '-'),
('RLS-090', 'KEG-050', 'TRG-054', '2026-10-13', 'TW3', 85.80, 78.00, 1178000000.00, 76.00, 'Penyesuaian titik penanaman pohon pelindung jalan kota.'),
('RLS-091', 'KEG-051', 'TRG-055', '2026-07-11', 'TW2', 16.00, 57.14, 770000000.00, 55.00, NULL),
('RLS-092', 'KEG-051', 'TRG-055', '2026-10-12', 'TW3', 24.00, 85.71, 1162000000.00, 83.00, 'N/A'),
('RLS-093', 'KEG-052', 'TRG-056', '2026-07-10', 'TW2', 12.00, 54.55, 927500000.00, 53.00, NULL),
('RLS-094', 'KEG-052', 'TRG-056', '2026-10-14', 'TW3', 18.00, 81.82, 1400000000.00, 80.00, 'Akses pengambilan sampel hulu sungai terhambat debit air tinggi.'),
('RLS-095', 'KEG-053', 'TRG-057', '2026-10-11', 'TW3', 1463.00, 77.00, 1350000000.00, 75.00, NULL),
('RLS-096', 'KEG-054', 'TRG-058', '2026-10-13', 'TW3', 81.60, 68.00, 957000000.00, 66.00, 'Pengiriman komponen turbin mikrohidro terkendala cuaca pegunungan.'),
('RLS-097', 'KEG-055', 'TRG-059', '2026-10-14', 'TW3', 27.00, 84.38, 1558000000.00, 82.00, 'Tidak ada kendala');

-- --------------------------------------------------------

--
-- Table structure for table `tb_target`
--

CREATE TABLE `tb_target` (
  `id_target` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_kegiatan` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tahun` year NOT NULL,
  `triwulan` enum('TW1','TW2','TW3','TW4','Tahunan') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Tahunan',
  `indikator_kinerja` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_fisik_nilai` decimal(12,2) NOT NULL,
  `satuan_fisik` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_persentase` decimal(5,2) NOT NULL DEFAULT '100.00',
  `target_anggaran` decimal(18,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tb_target`
--

INSERT INTO `tb_target` (`id_target`, `id_kegiatan`, `tahun`, `triwulan`, `indikator_kinerja`, `target_fisik_nilai`, `satuan_fisik`, `target_persentase`, `target_anggaran`) VALUES
('TRG-001', 'KEG-001', '2026', 'Tahunan', 'Volume sampah terkelola pada fasilitas TPA dan TPS 3R', 3000.00, 'Ton', 100.00, 2500000000.00),
('TRG-002', 'KEG-002', '2026', 'Tahunan', 'Luas kawasan Ruang Terbuka Hijau perkotaan yang ditata', 150.00, 'Hektar', 100.00, 2000000000.00),
('TRG-003', 'KEG-003', '2026', 'Tahunan', 'Jumlah stasiun pantau kualitas air dan udara yang beroperasi optimal', 27.00, 'Lokasi', 100.00, 1800000000.00),
('TRG-004', 'KEG-004', '2026', 'Tahunan', 'Jumlah dokumen izin lingkungan perusahaan yang diaudit kepatuhannya', 35.00, 'Dokumen', 100.00, 1400000000.00),
('TRG-005', 'KEG-005', '2026', 'Tahunan', 'Jumlah titik pengawasan pertambangan dan sumur pantau air tanah', 20.00, 'Lokasi', 100.00, 2800000000.00),
('TRG-006', 'KEG-006', '2026', 'Tahunan', 'Panjang saluran irigasi dan tebing sungai yang direhabilitasi', 12.50, 'Kilometer', 100.00, 5000000000.00),
('TRG-007', 'KEG-007', '2026', 'Tahunan', 'Luas lahan sawah produktif yang terlindungi dari alih fungsi', 450.00, 'Hektar', 100.00, 3600000000.00),
('TRG-008', 'KEG-008', '2025', 'Tahunan', 'Jumlah laporan evaluasi pembangunan kabupaten/kota yang tervalidasi', 23.00, 'Dokumen', 100.00, 1500000000.00),
('TRG-009', 'KEG-009', '2025', 'Tahunan', 'Luas kawasan hutan lindung dan mangrove yang direhabilitasi', 320.00, 'Hektar', 100.00, 2100000000.00),
('TRG-010', 'KEG-010', '2025', 'Tahunan', 'Luas ekosistem lahan gambut yang dipulihkan', 280.00, 'Ha', 100.00, 2000000000.00),
('TRG-011', 'KEG-011', '2026', 'TW1', 'Kapasitas pengolahan sampah dan limbah terpadu triwulan I', 450.00, 'ton', 25.00, 562500000.00),
('TRG-012', 'KEG-011', '2026', 'TW2', 'Kapasitas pengolahan sampah dan limbah terpadu triwulan II', 900.00, 'TON', 50.00, 1125000000.00),
('TRG-013', 'KEG-011', '2026', 'TW3', 'Kapasitas pengolahan sampah dan limbah terpadu triwulan III', 1350.00, 'Ton ', 75.00, 1687500000.00),
('TRG-014', 'KEG-012', '2026', 'Tahunan', 'Kapasitas pengolahan sampah dan limbah terpadu tahunan', 1800.00, 'Ton', 100.00, 1500000000.00),
('TRG-015', 'KEG-013', '2026', 'Tahunan', 'Jumlah fasilitas kesehatan tingkat pertama terstandar sanitasi', 18.00, 'Unit', 100.00, 3200000000.00),
('TRG-016', 'KEG-014', '2026', 'Tahunan', 'Jumlah unit pengolah limbah medis yang beroperasi sesuai baku mutu', 10.00, 'unit', 100.00, 3000000000.00),
('TRG-017', 'KEG-015', '2025', 'Tahunan', 'Jumlah titik sarana air bersih dan sanitasi desa terbangun', 25.00, 'Lokasi', 100.00, 1450000000.00),
('TRG-018', 'KEG-016', '2025', 'Tahunan', 'Jumlah sampel kualitas air minum desa yang diuji laboratorium', 120.00, 'Sampel', 100.00, 1450000000.00),
('TRG-019', 'KEG-017', '2026', 'Tahunan', 'Jumlah ruang kelas dan laboratorium kejuruan yang direvitalisasi', 30.00, 'Ruang', 100.00, 4500000000.00),
('TRG-020', 'KEG-018', '2026', 'Tahunan', 'Jumlah sekolah penerima pembinaan program Adiwiyata', 40.00, 'Sekolah', 100.00, 4000000000.00),
('TRG-021', 'KEG-019', '2026', 'Tahunan', 'Jumlah unit penerangan jalan umum tenaga surya terpasang', 150.00, 'Unit', 100.00, 3300000000.00),
('TRG-022', 'KEG-020', '2026', 'Tahunan', 'Luas kawasan konservasi terumbu karang dan pesisir yang ditata', 85.00, 'Hektar', 100.00, 1500000000.00),
('TRG-023', 'KEG-021', '2026', 'Tahunan', 'Volume sampah pesisir dan laut yang tertangani', 500.00, 'ton', 100.00, 1200000000.00),
('TRG-024', 'KEG-022', '2026', 'TW1', 'Jumlah kampung siaga bencana yang dibentuk triwulan I', 5.00, 'Desa', 25.00, 1100000000.00),
('TRG-025', 'KEG-022', '2026', 'TW2', 'Jumlah kampung siaga bencana yang dibentuk triwulan II', 10.00, 'Desa', 50.00, 2200000000.00),
('TRG-026', 'KEG-022', '2026', 'TW3', 'Jumlah kampung siaga bencana yang dibentuk triwulan III', 15.00, 'Desa', 75.00, 3300000000.00),
('TRG-027', 'KEG-023', '2024', 'Tahunan', 'Kapasitas daya pembangkit listrik tenaga surya pedesaan', 250.00, 'kWp', 100.00, 3100000000.00),
('TRG-028', 'KEG-024', '2026', 'Tahunan', 'Panjang alur sungai yang dinormalisasi untuk pengendalian banjir', 8.00, 'km', 100.00, 4800000000.00),
('TRG-044', 'KEG-040', '2024', 'Tahunan', 'Luas kawasan sempadan sungai dan RTH yang ditata', 95.00, 'Hektar', 100.00, 1700000000.00),
('TRG-045', 'KEG-041', '2024', 'Tahunan', 'Luas lahan kritis daerah tangkapan air yang direhabilitasi', 210.00, 'Hektar', 100.00, 1800000000.00),
('TRG-046', 'KEG-042', '2024', 'Tahunan', 'Panjang tebing sungai pengendali banjir yang diperkuat', 7.20, 'Kilometer', 100.00, 2300000000.00),
('TRG-047', 'KEG-043', '2024', 'Tahunan', 'Panjang saluran irigasi teknis yang direhabilitasi', 10.50, 'Kilometer', 100.00, 2600000000.00),
('TRG-048', 'KEG-044', '2025', 'Tahunan', 'Luas lahan sawah berkelanjutan yang ditetapkan dan dilindungi', 260.00, 'Hektar', 100.00, 1600000000.00),
('TRG-049', 'KEG-045', '2025', 'Tahunan', 'Luas area layanan tata air irigasi sawah produktif', 380.00, 'Hektar', 100.00, 1700000000.00),
('TRG-050', 'KEG-046', '2025', 'Tahunan', 'Luas kawasan mangrove pesisir yang ditanam dan dipelihara', 140.00, 'Hektar', 100.00, 1350000000.00),
('TRG-051', 'KEG-047', '2025', 'Tahunan', 'Volume sampah pesisir pulau yang tertangani secara terpadu', 650.00, 'Ton', 100.00, 1450000000.00),
('TRG-052', 'KEG-048', '2026', 'Tahunan', 'Volume sampah terkelola pada TPA regional dan bank sampah', 2400.00, 'ton', 100.00, 1800000000.00),
('TRG-053', 'KEG-049', '2026', 'Tahunan', 'Jumlah titik pantau kualitas udara dan emisi industri', 18.00, 'Lokasi', 100.00, 1650000000.00),
('TRG-054', 'KEG-050', '2026', 'Tahunan', 'Luas RTH perkotaan dan kapasitas layanan persampahan', 110.00, 'ha', 100.00, 1550000000.00),
('TRG-055', 'KEG-051', '2026', 'Tahunan', 'Jumlah dokumen izin lingkungan usaha yang diaudit kepatuhannya', 28.00, 'Dokumen', 100.00, 1400000000.00),
('TRG-056', 'KEG-052', '2026', 'Tahunan', 'Jumlah stasiun pantau kualitas air sungai yang beroperasi', 22.00, 'Lokasi', 100.00, 1750000000.00),
('TRG-057', 'KEG-053', '2026', 'Tahunan', 'Volume sampah organik yang diolah menjadi kompos terpadu', 1900.00, 'TON', 100.00, 1800000000.00),
('TRG-058', 'KEG-054', '2026', 'Tahunan', 'Kapasitas pembangkit energi terbarukan pedesaan terpasang', 120.00, 'kWp', 100.00, 1450000000.00),
('TRG-059', 'KEG-055', '2026', 'Tahunan', 'Jumlah perusahaan kawasan industri yang lulus audit lingkungan', 32.00, 'Dokumen', 100.00, 1900000000.00);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `master_skpa`
--
ALTER TABLE `master_skpa`
  ADD PRIMARY KEY (`id_skpa`),
  ADD UNIQUE KEY `uk_kode_skpa` (`kode_skpa`),
  ADD KEY `idx_skpa_bidang` (`bidang_urusan`);

--
-- Indexes for table `tb_evaluasi_pembangunan`
--
ALTER TABLE `tb_evaluasi_pembangunan`
  ADD PRIMARY KEY (`id_evaluasi`),
  ADD KEY `idx_evaluasi_program` (`id_program`),
  ADD KEY `idx_evaluasi_kegiatan` (`id_kegiatan`),
  ADD KEY `idx_evaluasi_realisasi` (`id_realisasi`);

--
-- Indexes for table `tb_kegiatan`
--
ALTER TABLE `tb_kegiatan`
  ADD PRIMARY KEY (`id_kegiatan`),
  ADD UNIQUE KEY `uk_kode_kegiatan` (`kode_kegiatan`),
  ADD KEY `idx_kegiatan_program` (`id_program`),
  ADD KEY `idx_kegiatan_kabkota` (`id_kabupaten_kota`),
  ADD KEY `idx_kegiatan_desa` (`id_desa`);

--
-- Indexes for table `tb_program`
--
ALTER TABLE `tb_program`
  ADD PRIMARY KEY (`id_program`),
  ADD UNIQUE KEY `uk_kode_program` (`kode_program`),
  ADD KEY `idx_program_skpa` (`id_skpa`),
  ADD KEY `idx_program_tahun_bidang` (`tahun_anggaran`,`bidang_urusan`);

--
-- Indexes for table `tb_realisasi`
--
ALTER TABLE `tb_realisasi`
  ADD PRIMARY KEY (`id_realisasi`),
  ADD KEY `idx_realisasi_kegiatan` (`id_kegiatan`),
  ADD KEY `idx_realisasi_target` (`id_target`),
  ADD KEY `idx_realisasi_tanggal` (`tanggal_lapor`);

--
-- Indexes for table `tb_target`
--
ALTER TABLE `tb_target`
  ADD PRIMARY KEY (`id_target`),
  ADD KEY `idx_target_kegiatan` (`id_kegiatan`),
  ADD KEY `idx_target_tahun` (`tahun`,`triwulan`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tb_evaluasi_pembangunan`
--
ALTER TABLE `tb_evaluasi_pembangunan`
  ADD CONSTRAINT `fk_evaluasi_kegiatan` FOREIGN KEY (`id_kegiatan`) REFERENCES `tb_kegiatan` (`id_kegiatan`) ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_evaluasi_program` FOREIGN KEY (`id_program`) REFERENCES `tb_program` (`id_program`) ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_evaluasi_realisasi` FOREIGN KEY (`id_realisasi`) REFERENCES `tb_realisasi` (`id_realisasi`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_kegiatan`
--
ALTER TABLE `tb_kegiatan`
  ADD CONSTRAINT `fk_kegiatan_program` FOREIGN KEY (`id_program`) REFERENCES `tb_program` (`id_program`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_program`
--
ALTER TABLE `tb_program`
  ADD CONSTRAINT `fk_program_skpa` FOREIGN KEY (`id_skpa`) REFERENCES `master_skpa` (`id_skpa`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_realisasi`
--
ALTER TABLE `tb_realisasi`
  ADD CONSTRAINT `fk_realisasi_kegiatan` FOREIGN KEY (`id_kegiatan`) REFERENCES `tb_kegiatan` (`id_kegiatan`) ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_realisasi_target` FOREIGN KEY (`id_target`) REFERENCES `tb_target` (`id_target`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `tb_target`
--
ALTER TABLE `tb_target`
  ADD CONSTRAINT `fk_target_kegiatan` FOREIGN KEY (`id_kegiatan`) REFERENCES `tb_kegiatan` (`id_kegiatan`) ON DELETE RESTRICT ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
