# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 06:26:50 2020

@author: Jolene
"""

CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root1`@`%` 
    SQL SECURITY DEFINER
VIEW `dss`.`dim_week` AS
    SELECT 
        MIN(`dss`.`dim_time`.`id`) AS `id`,
        MIN(`dss`.`dim_time`.`day`) AS `weekstart`,
        `dss`.`dim_time`.`weeknum` AS `weeknum`,
        `dss`.`dim_time`.`week` AS `week`,
        `dss`.`dim_time`.`season` AS `season`,
        LEFT(`dss`.`dim_time`.`yearweek`, 4) AS `year`
    FROM
        `dss`.`dim_time`
    GROUP BY `dss`.`dim_time`.`weeknum` , `dss`.`dim_time`.`week` , `dss`.`dim_time`.`season`
    ORDER BY `id`