-- MySQL dump 10.13  Distrib 5.7.24, for Linux (x86_64)
--
-- Host: localhost    Database: leobox
-- ------------------------------------------------------
-- Server version	5.7.24-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ld_accounts`
--

DROP TABLE IF EXISTS `ld_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ld_accounts` (
  `user_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `email` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `display_name` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `last_login` int(11) NOT NULL DEFAULT '0',
  `password` longtext COLLATE utf8mb4_bin,
  `state` smallint(6) NOT NULL DEFAULT '0' COMMENT '0: initial, 1: enabled, 2: disabled, 3: deleted',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `UNIQ_907AA303A76ED395` (`user_id`),
  KEY `display_name_index` (`display_name`),
  KEY `email_index` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ld_authtoken`
--

DROP TABLE IF EXISTS `ld_authtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ld_authtoken` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `uid` varchar(64) COLLATE utf8mb4_bin NOT NULL DEFAULT '',
  `login_name` varchar(64) COLLATE utf8mb4_bin NOT NULL DEFAULT '',
  `app_name` varchar(200) COLLATE utf8mb4_bin NOT NULL,
  `token` varchar(200) COLLATE utf8mb4_bin NOT NULL DEFAULT '',
  `expiration` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `authtoken_token_index` (`token`),
  KEY `authtoken_expiration_token` (`expiration`)
) ENGINE=InnoDB AUTO_INCREMENT=175 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ld_filecache`
--

DROP TABLE IF EXISTS `ld_filecache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ld_filecache` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `id_storage` bigint(20) NOT NULL DEFAULT '0',
  `path` varchar(4000) COLLATE utf8mb4_bin DEFAULT NULL,
  `path_hash` varchar(32) COLLATE utf8mb4_bin NOT NULL DEFAULT '',
  `name` varchar(250) COLLATE utf8mb4_bin DEFAULT NULL,
  `mime_type` varchar(250) COLLATE utf8mb4_bin DEFAULT NULL,
  `size` bigint(20) NOT NULL DEFAULT '0',
  `storage_mtime` bigint(20) NOT NULL DEFAULT '0',
  `id_parent` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fs_storage_path_hash` (`id_storage`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ld_properties`
--

DROP TABLE IF EXISTS `ld_properties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ld_properties` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `id_file` bigint(20) unsigned DEFAULT NULL,
  `propertyname` varchar(255) COLLATE utf8mb4_bin NOT NULL DEFAULT '',
  `propertyvalue` varchar(255) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fileid_index` (`id_file`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ld_share`
--

DROP TABLE IF EXISTS `ld_share`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ld_share` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid_owner` bigint(20) NOT NULL,
  `uid_recipient` bigint(20) NOT NULL,
  `item_type` varchar(64) COLLATE utf8mb4_bin NOT NULL DEFAULT '',
  `uid_file` bigint(20) NOT NULL,
  `file_target` varchar(512) COLLATE utf8mb4_bin DEFAULT NULL,
  `stime` bigint(20) NOT NULL DEFAULT '0',
  `expiration` datetime DEFAULT NULL,
  `token` varchar(32) COLLATE utf8mb4_bin DEFAULT NULL,
  `share_name` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `item_share_type_index` (`item_type`),
  KEY `token_index` (`token`),
  KEY `item_source_index` (`uid_file`),
  KEY `item_source_type_index` (`uid_file`,`item_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oc_storages`
--

DROP TABLE IF EXISTS `oc_storages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oc_storages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `path_home` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `quota` bigint(20) DEFAULT NULL,
  `used_space` bigint(20) DEFAULT NULL,
  `available` int(11) NOT NULL DEFAULT '1',
  `uid` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `storages_id_index` (`path_home`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ROW_FORMAT=COMPRESSED;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-01-23 19:54:57
