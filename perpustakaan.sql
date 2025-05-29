-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 29, 2025 at 01:04 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `perpustakaan`
--

-- --------------------------------------------------------

--
-- Table structure for table `buku`
--

CREATE TABLE `buku` (
  `id` int(11) NOT NULL,
  `judul` varchar(100) DEFAULT NULL,
  `penulis` varchar(100) DEFAULT NULL,
  `penerbit` varchar(100) DEFAULT NULL,
  `tahun_terbit` year(4) DEFAULT NULL,
  `stok` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `buku`
--

INSERT INTO `buku` (`id`, `judul`, `penulis`, `penerbit`, `tahun_terbit`, `stok`) VALUES
(1, 'PENDIDIKAN AGAMA ISLAM', 'KELOMPOK 1', 'Gramedia', '2025', 0),
(2, 'NOVEL 5 MENARA', 'Ahmad Fuadi', 'Gramedia', '2009', 49);

-- --------------------------------------------------------

--
-- Table structure for table `pinjaman`
--

CREATE TABLE `pinjaman` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `buku_id` int(11) DEFAULT NULL,
  `tanggal_pinjam` date DEFAULT NULL,
  `tanggal_kembali` date DEFAULT NULL,
  `status` enum('dipinjam','dikembalikan') DEFAULT 'dipinjam'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pinjaman`
--

INSERT INTO `pinjaman` (`id`, `user_id`, `buku_id`, `tanggal_pinjam`, `tanggal_kembali`, `status`) VALUES
(1, 2, 1, '2025-05-28', '2025-05-28', 'dikembalikan'),
(2, 2, 1, '2025-05-28', '2025-05-28', 'dikembalikan'),
(3, 5, 1, '2025-05-29', NULL, 'dipinjam'),
(4, 5, 2, '2025-05-29', NULL, 'dipinjam'),
(5, 5, 1, '2025-05-29', NULL, 'dipinjam');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `telepon` varchar(13) DEFAULT NULL,
  `foto_profil` varchar(255) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','pengunjung') NOT NULL,
  `nama_lengkap` varchar(100) DEFAULT NULL,
  `tanggal_daftar` timestamp NULL DEFAULT current_timestamp(),
  `status` enum('aktif','tidak aktif') DEFAULT 'aktif'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `telepon`, `foto_profil`, `password`, `role`, `nama_lengkap`, `tanggal_daftar`, `status`) VALUES
(1, 'admin', '0', '0', NULL, 'scrypt:32768:8:1$iluXeIFVXQm0599n$26eb28e0e1796a7b9ada25ab35534255cd38b302ad4ac442198d88ba575805c4d7e09b74475fe818fc02ce99bc614659504ec1dbed21fa13c8954a5af4df0d44', 'admin', 'farjehan alaraf', NULL, 'aktif'),
(2, 'JehanDesign', '0', '0', NULL, 'scrypt:32768:8:1$wghXX9VDk2V2iZwf$3a6754d036f89728af0c109d61df171bf5ea5dd86f7900327b36e59b065d92dae1a7d775c3d110640ee33292f8c21653c8ef5f0c4b28375414dc804a95dbee5d', 'pengunjung', 'farjehan alaraf', '2025-05-27 17:00:00', 'aktif'),
(3, 'Mario', '0', '0', NULL, 'scrypt:32768:8:1$6ArjPdTBBwiZoxLp$4d9bdc54e98165bf3bcf642711b39454b1742b21e0c384220bd7b978387facb57c4be172783dbd974f1131f369a7e2963a2a9be4497ef1c64ca960f16aea698c', 'pengunjung', 'Mario', '2025-05-27 17:00:00', 'aktif'),
(5, 'doni159', 'farjehanalaraf02@gmail.com', '082335360672', 'doni159_profile.jpg', 'scrypt:32768:8:1$yO87ZdBKX10bDkwM$458a504569727e5959f1d1557b39b068b2ddba5d58beb1dd0ebcf31b7de27c21b431ec1290324f8ab19eb6a71bdd2374b280e651a6b73ee696476bf436f120fe', 'pengunjung', 'Farjehan Alaraf', '2025-05-28 20:09:15', 'aktif');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `buku`
--
ALTER TABLE `buku`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pinjaman`
--
ALTER TABLE `pinjaman`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `buku_id` (`buku_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `buku`
--
ALTER TABLE `buku`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `pinjaman`
--
ALTER TABLE `pinjaman`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `pinjaman`
--
ALTER TABLE `pinjaman`
  ADD CONSTRAINT `pinjaman_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `pinjaman_ibfk_2` FOREIGN KEY (`buku_id`) REFERENCES `buku` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
