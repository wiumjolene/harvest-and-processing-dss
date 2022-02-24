CREATE TABLE `dim_block` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `pu_id` int DEFAULT NULL,
  `fc_id` int DEFAULT NULL,
  `va_id` int DEFAULT NULL,
  `hectare` decimal(10,3) DEFAULT NULL,
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=851 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `dim_client` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(14) DEFAULT NULL,
  `long_name` varchar(50) DEFAULT NULL,
  `priority` int DEFAULT '0',
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=191 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `dim_fc` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(14) DEFAULT NULL,
  `long_name` varchar(50) DEFAULT NULL,
  `packtopackplans` int DEFAULT NULL,
  `management` varchar(45) DEFAULT NULL,
  `province` varchar(45) DEFAULT 'NC',
  `longitude` decimal(10,5) DEFAULT NULL,
  `latitude` decimal(10,5) DEFAULT NULL,
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=137 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `dim_pack_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(14) DEFAULT NULL,
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `dim_packhouse` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(14) DEFAULT NULL,
  `long_name` varchar(50) DEFAULT NULL,
  `type` int DEFAULT NULL,
  `loose` int DEFAULT NULL,
  `punnet` int DEFAULT NULL,
  `longitude` decimal(11,5) DEFAULT NULL,
  `latitude` decimal(11,5) DEFAULT NULL,
  `province` varchar(45) DEFAULT 'NC',
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `dim_productionunit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(14) DEFAULT NULL,
  `long_name` varchar(50) DEFAULT NULL,
  `fc_id` int DEFAULT NULL,
  `longitude` decimal(9,6) DEFAULT NULL,
  `latitude` decimal(8,6) DEFAULT NULL,
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `dim_time` (
  `id` int NOT NULL AUTO_INCREMENT,
  `day` date DEFAULT NULL,
  `weeknum` int DEFAULT NULL,
  `yearweek` varchar(14) DEFAULT NULL,
  `week` varchar(14) DEFAULT NULL,
  `season` int DEFAULT NULL,
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `day_UNIQUE` (`day`)
) ENGINE=InnoDB AUTO_INCREMENT=4002 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `dim_va` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(14) DEFAULT NULL,
  `long_name` varchar(50) DEFAULT NULL,
  `vacat_id` int DEFAULT NULL,
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=276 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `dim_vacat` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(14) DEFAULT NULL,
  `long_name` varchar(50) DEFAULT NULL,
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `f_demand_plan` (
  `id` int NOT NULL,
  `client_id` int DEFAULT NULL,
  `vacat_id` int DEFAULT NULL,
  `pack_type_id` int DEFAULT NULL,
  `priority` int DEFAULT NULL,
  `arrivalweek` varchar(14) DEFAULT NULL,
  `packweek` varchar(45) DEFAULT NULL,
  `transitdays` int DEFAULT NULL,
  `stdunits` decimal(11,2) DEFAULT NULL,
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `f_from_to` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fc_id` bigint DEFAULT NULL,
  `packhouse_id` bigint DEFAULT NULL,
  `km` double DEFAULT NULL,
  `allowed` int DEFAULT NULL,
  `history` int DEFAULT '0',
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNIQUE` (`fc_id`,`packhouse_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1387 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `f_from_to_TRUNCATED` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `pu_id` bigint DEFAULT NULL,
  `packhouse_id` bigint DEFAULT NULL,
  `km` double DEFAULT NULL,
  `allowed` int DEFAULT NULL,
  `history` int DEFAULT '0',
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNIQUE` (`pu_id`,`packhouse_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3641 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `f_harvest_estimate` (
  `id` int NOT NULL AUTO_INCREMENT,
  `block_id` bigint DEFAULT NULL,
  `va_id` bigint DEFAULT NULL,
  `packweek` text,
  `kg_raw` double DEFAULT NULL,
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1758 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `f_pack_capacity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `packhouse_id` int DEFAULT NULL,
  `pack_type_id` int DEFAULT NULL,
  `packweek` varchar(14) DEFAULT NULL,
  `stdunits` decimal(11,2) DEFAULT NULL COMMENT 'This is the updated stdunits to match Kobus Jona plan',
  `stdunits_source` decimal(11,2) DEFAULT NULL COMMENT 'This is the original planned stdunits as tracked from source system',
  `adjusted` int DEFAULT '0',
  `add_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNIQUE` (`packhouse_id`,`pack_type_id`,`packweek`)
) ENGINE=InnoDB AUTO_INCREMENT=462 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `f_speed` (
  `id` bigint DEFAULT NULL,
  `packhouse_id` bigint DEFAULT NULL,
  `packtype_id` bigint DEFAULT NULL,
  `va_id` bigint DEFAULT NULL,
  `stdunits.manhour` double DEFAULT NULL,
  `speed` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `harvest_estimate_0638_data` (
  `EstimateID` bigint DEFAULT NULL,
  `Grower` text,
  `Farm` text,
  `Orchard` text,
  `OrchardSection` double DEFAULT NULL,
  `Season` text,
  `kgGross` double DEFAULT NULL,
  `PercentageWaste` double DEFAULT NULL,
  `PercentageGiveAway` double DEFAULT NULL,
  `EstimateType` text,
  `AsOnDate` text,
  `Latest` bigint DEFAULT NULL,
  `PackFormat` text,
  `PackFormatPercentage` double DEFAULT NULL,
  `Variety` text,
  `VarietyGroup` text,
  `Commodity` text,
  `kgWaste` double DEFAULT NULL,
  `kgGiveAway` double DEFAULT NULL,
  `kgNettEstimate` double DEFAULT NULL,
  `Week` text,
  `WeekPerc` double DEFAULT NULL,
  `StdUnitsNett` double DEFAULT NULL,
  `Hectare` double DEFAULT NULL,
  `NumberOfplants` double DEFAULT NULL,
  `BunchesPerPlant` bigint DEFAULT NULL,
  `BerryWeight` double DEFAULT NULL,
  `BerryCount` bigint DEFAULT NULL,
  `PUStatus` text,
  `kgNettPerHectare` double DEFAULT NULL,
  `stdUnitsNettPerHectare` double DEFAULT NULL,
  `extract_datetime` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `harvest_estimate_data` (
  `Season` text,
  `Grower` text,
  `ProductionUnit` text,
  `Orchard` text,
  `Variety` text,
  `Hectare` double DEFAULT NULL,
  `NumberOfPlants` bigint DEFAULT NULL,
  `BunchesPerPlant` bigint DEFAULT NULL,
  `BerryWeight` double DEFAULT NULL,
  `BerryCount` bigint DEFAULT NULL,
  `WeightPerBunch` double DEFAULT NULL,
  `GrossEstimate` double DEFAULT NULL,
  `PercentageWaste` double DEFAULT NULL,
  `PercentageGiveAway` double DEFAULT NULL,
  `NettEstimate` double DEFAULT NULL,
  `NettEstimateHectare` double DEFAULT NULL,
  `StandardCartons` double DEFAULT NULL,
  `StandardCartonsHectare` double DEFAULT NULL,
  `Week` text,
  `WeekPercentage` double DEFAULT NULL,
  `StandardCartonsWeek` double DEFAULT NULL,
  `PercentageLoose` double DEFAULT NULL,
  `PercentagePunnet` double DEFAULT NULL,
  `StandardCartonsLooseWeek` double DEFAULT NULL,
  `StandardCartonsPunnetWeek` double DEFAULT NULL,
  `estimatetype` text,
  `OCSection` bigint DEFAULT NULL,
  `extract_datetime` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `harvest_estimate_quicadj_data` (
  `recordno` bigint DEFAULT NULL,
  `fc` text,
  `pu` text,
  `season` text,
  `va` text,
  `week` text,
  `oc` text,
  `kg` bigint DEFAULT NULL,
  `pcdate` date DEFAULT NULL,
  `pctime` bigint DEFAULT NULL,
  `username` text,
  `pcname` text,
  `sz` text,
  `extract_datetime` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `history_from_to` (
  `id` int NOT NULL AUTO_INCREMENT,
  `grower` varchar(45) DEFAULT NULL,
  `packsite` varchar(45) DEFAULT NULL,
  `pv_std` int DEFAULT NULL,
  `p_std` int DEFAULT NULL,
  `perc` decimal(5,4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=177 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `interim_options_he` (
  `va_id` bigint DEFAULT NULL,
  `vacat_id` bigint DEFAULT NULL,
  `block_id` bigint DEFAULT NULL,
  `time_id` bigint DEFAULT NULL,
  `kg` double DEFAULT NULL,
  `id` bigint DEFAULT NULL,
  `stdunits` double DEFAULT NULL,
  `kg_rem` double DEFAULT NULL,
  `demand_id` bigint DEFAULT NULL,
  `client_id` bigint DEFAULT NULL,
  `priority` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `interim_options_pc` (
  `packhouse_id` bigint DEFAULT NULL,
  `pack_type_id` bigint DEFAULT NULL,
  `time_id` bigint DEFAULT NULL,
  `stdunits` double DEFAULT NULL,
  `stdunits_hour` double DEFAULT NULL,
  `id` bigint DEFAULT NULL,
  `kg` double DEFAULT NULL,
  `kg_rem` double DEFAULT NULL,
  `demand_id` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `pack_capacity_data` (
  `recordno` bigint DEFAULT NULL,
  `phc` text,
  `packweek` text,
  `packformat` text,
  `noofstdcartons` bigint DEFAULT NULL,
  `extract_datetime` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `planning_data` (
  `recordtype` text,
  `demandid` bigint DEFAULT NULL,
  `clientno` text,
  `demand_salesweek` text,
  `demand_arrivalweek` text,
  `physicalctnweight` double DEFAULT NULL,
  `qty_physicalctns` bigint DEFAULT NULL,
  `demand_noofcontainers` text,
  `qty_kg` double DEFAULT NULL,
  `qty_standardctns` double DEFAULT NULL,
  `packplanid` text,
  `packplan_splitid` text,
  `targetmarket` text,
  `commodity` text,
  `varietygroup` text,
  `variety` text,
  `innerpacking` text,
  `cartontype` text,
  `size` text,
  `brand` text,
  `grade` text,
  `stacking` text,
  `gtin` text,
  `targetregion` text,
  `targetcountry` text,
  `grower` text,
  `packweek` text,
  `earliest_allowed_packdate` text,
  `latest_allowed_packdate` text,
  `packsite` text,
  `notes` text,
  `split_notes` text,
  `priority` text,
  `format` text,
  `alternative_gtins` text,
  `alternative_specs` text,
  `DefaultCurrencyIncome` text,
  `DefaultCurrencyCosts` text,
  `SellPricePerWeighUnit` text,
  `CostsPerWeighUnit` text,
  `extract_datetime` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `rules_prioritse_client_va` (
  `id` int NOT NULL AUTO_INCREMENT,
  `client_id` int DEFAULT NULL,
  `va_id` int DEFAULT NULL,
  `priority` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `rules_refuse_client_va` (
  `id` int NOT NULL AUTO_INCREMENT,
  `client_id` int DEFAULT NULL,
  `va_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `run_season` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plan_date` date DEFAULT NULL,
  `weekstart` date DEFAULT NULL,
  `week` varchar(45) DEFAULT NULL,
  `runtime` datetime DEFAULT NULL,
  `make_plan` int DEFAULT '0',
  `horizon` int DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `sol_actual_plan` (
  `demand_id` bigint DEFAULT NULL,
  `pc` bigint DEFAULT NULL,
  `fc_id` bigint DEFAULT NULL,
  `va_id` double DEFAULT NULL,
  `kg` double DEFAULT NULL,
  `stdunits` double DEFAULT NULL,
  `km` double DEFAULT NULL,
  `kgkm` double DEFAULT NULL,
  `speed` double DEFAULT NULL,
  `packhours` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `sol_fitness` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `obj1` double DEFAULT NULL,
  `obj2` double DEFAULT NULL,
  `population` text,
  `result` text,
  `alg` text,
  `indiv_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1845 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `sol_kobus_plan` (
  `demand_id` bigint DEFAULT NULL,
  `pc` bigint DEFAULT NULL,
  `fc_id` bigint DEFAULT NULL,
  `va_id` double DEFAULT NULL,
  `kg` double DEFAULT NULL,
  `stdunits` double DEFAULT NULL,
  `km` double DEFAULT NULL,
  `kgkm` double DEFAULT NULL,
  `speed` double DEFAULT NULL,
  `packhours` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `sol_pareto_individuals` (
  `he` bigint DEFAULT NULL,
  `pc` bigint DEFAULT NULL,
  `kg` double DEFAULT NULL,
  `kgkm` double DEFAULT NULL,
  `packhours` double DEFAULT NULL,
  `demand_id` bigint DEFAULT NULL,
  `time_id` bigint DEFAULT NULL,
  `indiv_id` bigint DEFAULT NULL,
  `alg` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `transitdays` (
  `recordno` int NOT NULL,
  `transitdays` int DEFAULT NULL,
  PRIMARY KEY (`recordno`),
  UNIQUE KEY `recordno_UNIQUE` (`recordno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE ALGORITHM=UNDEFINED DEFINER=`powerbi`@`%` SQL SECURITY DEFINER VIEW `dim_week` AS select min(`dim_time`.`id`) AS `id`,min(`dim_time`.`day`) AS `weekstart`,`dim_time`.`weeknum` AS `weeknum`,`dim_time`.`week` AS `week`,`dim_time`.`season` AS `season`,left(`dim_time`.`yearweek`,4) AS `year` from `dim_time` 
group by `dim_time`.`weeknum`,`dim_time`.`week`,`dim_time`.`season`,`dim_time`.`yearweek` order by `id`;