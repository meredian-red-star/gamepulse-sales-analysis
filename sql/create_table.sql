-- Run this file with a MySQL account allowed to create databases and tables.
-- Sales values are in millions of units. Zero sales values are valid.
CREATE DATABASE IF NOT EXISTS `gamepulse`
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `gamepulse`;

CREATE TABLE IF NOT EXISTS `video_game_sales` (
    `Rank` INT UNSIGNED NOT NULL PRIMARY KEY,
    `Name` VARCHAR(255) NOT NULL,
    `Platform` VARCHAR(20) NOT NULL,
    `Year` SMALLINT UNSIGNED NOT NULL,
    `Genre` VARCHAR(50) NOT NULL,
    `Publisher` VARCHAR(255) NOT NULL,
    `NA_Sales` DECIMAL(10, 2) UNSIGNED NOT NULL,
    `EU_Sales` DECIMAL(10, 2) UNSIGNED NOT NULL,
    `JP_Sales` DECIMAL(10, 2) UNSIGNED NOT NULL,
    `Other_Sales` DECIMAL(10, 2) UNSIGNED NOT NULL,
    `Global_Sales` DECIMAL(10, 2) UNSIGNED NOT NULL
) ENGINE = InnoDB;
