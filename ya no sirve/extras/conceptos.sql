-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 07, 2025 at 04:58 AM
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
-- Database: `seguridad`
--

-- --------------------------------------------------------

--
-- Table structure for table `conceptos`
--

CREATE TABLE `conceptos` (
  `id` int(11) NOT NULL,
  `termino` varchar(255) NOT NULL,
  `definicion` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `conceptos`
--

INSERT INTO `conceptos` (`id`, `termino`, `definicion`) VALUES
(1, 'firewall', 'Un sistema de seguridad que monitorea y controla el tráfico de red.'),
(2, 'malware', 'Software malicioso diseñado para dañar o explotar sistemas.'),
(3, 'phishing', 'Un tipo de ataque cibernético que intenta engañar a las personas para que revelen información sensible.'),
(4, 'cifrado', 'El proceso de convertir datos en un formato ilegible para proteger su confidencialidad.');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `conceptos`
--
ALTER TABLE `conceptos`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `conceptos`
--
ALTER TABLE `conceptos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
