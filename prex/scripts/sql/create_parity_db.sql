SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `pvdb`;
CREATE SCHEMA IF NOT EXISTS `pvdb` DEFAULT CHARACTER SET latin1 ;
USE `pvdb` ;

-- -----------------------------------------------------
-- Table `pvdb`.`condition_types`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pvdb`.`condition_types` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `value_type` VARCHAR(6) NOT NULL,
  `created` DATETIME NULL DEFAULT NULL,
  `description` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `pvdb`.`runs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pvdb`.`runs` (
  `number` INT(11) NOT NULL,
  `started` DATETIME NULL DEFAULT NULL,
  `finished` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`number`),
  UNIQUE INDEX `number` (`number` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `pvdb`.`files`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pvdb`.`files` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `path` TEXT NOT NULL,
  `sha256` VARCHAR(44) NOT NULL,
  `content` TEXT NOT NULL,
  `description` VARCHAR(255) NULL DEFAULT NULL,
  `importance` INT(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `pvdb`.`conditions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pvdb`.`conditions` ;

CREATE TABLE IF NOT EXISTS `pvdb`.`conditions` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `run_number` INT(11) NULL DEFAULT NULL,
  `text_value` TEXT NULL DEFAULT NULL,
  `int_value` INT(11) NOT NULL,
  `float_value` FLOAT NOT NULL,
  `bool_value` TINYINT(1) NOT NULL,
  `time_value` DATETIME NULL DEFAULT NULL,
  `condition_type_id` INT(11) NULL DEFAULT NULL,
  `created` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `condition_type_id` (`condition_type_id` ASC),
  INDEX `run_number` (`run_number` ASC),
  CONSTRAINT `conditions_ibfk_1`
    FOREIGN KEY (`condition_type_id`)
    REFERENCES `pvdb`.`condition_types` (`id`),
  CONSTRAINT `conditions_ibfk_2`
    FOREIGN KEY (`run_number`)
    REFERENCES `pvdb`.`runs` (`number`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `pvdb`.`logs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pvdb`.`logs` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `table_ids` VARCHAR(255) NULL DEFAULT NULL,
  `description` TEXT NULL DEFAULT NULL,
  `related_run` INT(11) NULL DEFAULT NULL,
  `created` DATETIME NULL DEFAULT NULL,
  `user_name` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `pvdb`.`files_have_runs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pvdb`.`files_have_runs` (
  `files_id` INT(11) NULL DEFAULT NULL,
  `run_number` INT(11) NULL DEFAULT NULL,
  INDEX `files_id` (`files_id` ASC),
  INDEX `run_number` (`run_number` ASC),
  CONSTRAINT `files_have_runs_ibfk_1`
    FOREIGN KEY (`files_id`)
    REFERENCES `pvdb`.`files` (`id`),
  CONSTRAINT `files_have_runs_ibfk_2`
    FOREIGN KEY (`run_number`)
    REFERENCES `pvdb`.`runs` (`number`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `pvdb`.`schema_versions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pvdb`.`schema_versions` (
  `version` INT(11) NOT NULL,
  `created` DATETIME NULL DEFAULT NULL,
  `comment` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`version`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;


-- -----------------------------------------------------
-- Data for table `pvdb`.`condition_types`
-- -----------------------------------------------------
START TRANSACTION;
Use `pvdb`;
INSERT INTO `pvdb`.`condition_types` (`name`, `value_type`) VALUES ('total_charge', 'float');

COMMIT;
