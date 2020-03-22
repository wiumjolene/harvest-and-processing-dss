# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 15:49:28 2020

@author: Jolene
"""

from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode
from connect import mydb as cnx_phd

DB_NAME = 'dss'

CREATE_TABLES = {}
FROM_TO = {}
CREATE_TABLES['f_from_to'] = (
    "CREATE TABLE f_from_to ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"
    "  block_id int(11),"    
    "  packhouse_id int(11),"        
    "  km decimal(11,2),"  
    "  add_datetime datetime,"      
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['f_from_to'] = [0,'f_from_to']

CREATE_TABLES['f_pack_capacity'] = (
    "CREATE TABLE f_pack_capacity ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  packhouse_id int(11),"  
    "  pack_type_id int(11),"
    "  packweek varchar(14),"
    "  time_id int(11),"      
    "  kg decimal(11,2)," 
    "  stdunits decimal(11,2),"
    "  add_datetime datetime,"    
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['f_pack_capacity'] = ['f_pack_capacity.sql','f_pack_capacity']

CREATE_TABLES['f_demand_plan'] = (
    "CREATE TABLE f_demand_plan ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  client_id int(11),"  
    "  vacat_id int(11),"  
    "  pack_type_id int(11)," 
    "  priority int(11)," 
    "  arrivalweek varchar(14),"
    "  time_id int(11),"
    "  transitdays int(11),"      
    "  stdunits decimal(11,2)," 
    "  add_datetime datetime,"    
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['f_demand_plan'] = ['f_demand_plan','f_demand_plan']

CREATE_TABLES['f_harvest_estimate'] = (
    "CREATE TABLE f_harvest_estimate ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  va_id int(11),"  
    "  block_id int(11)," 
    "  packweek varchar(14),"
    "  time_id int(11),"      
    "  kg_raw decimal(11,2)," 
    "  add_datetime datetime,"    
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['f_harvest_estimate'] = ['f_harvest_estimate.sql','f_harvest_estimate']

CREATE_TABLES['dim_block'] = (
    "CREATE TABLE dim_block ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  name varchar(14),"
    "  long_name varchar(50),"
    "  ha decimal(11,4)," 
    "  fc_id int(11),"       
    "  longitude decimal(9,6),"    
    "  latitude decimal(8,6)," 
    "  add_datetime datetime,"
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['dim_block'] = ['dim_block.sql','dim_block']

CREATE_TABLES['dim_va'] = (
    "CREATE TABLE dim_va ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  name varchar(14),"
    "  long_name varchar(50),"
    "  vacat_id int(11),"  
    "  add_datetime datetime,"      
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['dim_va'] = ['dim_va.sql','dim_va']

CREATE_TABLES['dim_vacat'] = (
    "CREATE TABLE dim_vacat ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  name varchar(14)," 
    "  long_name varchar(50)," 
    "  add_datetime datetime,"    
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['dim_vacat'] = ['dim_vacat.sql','dim_vacat']

CREATE_TABLES['dim_packhouse'] = (
    "CREATE TABLE dim_packhouse ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  name varchar(14)," 
    "  long_name varchar(50),"
    "  type int(11),"   
    "  loose int(11),"
    "  punnet int(11),"
    "  longitude decimal(11,2),"    
    "  latitude decimal(11,2)," 
    "  add_datetime datetime,"
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['dim_packhouse'] = ['dim.packhouse.sql','dim_packhouse']

CREATE_TABLES['dim_client'] = (
    "CREATE TABLE dim_client ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  name varchar(14)," 
    "  long_name varchar(50)," 
    "  add_datetime datetime,"    
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['dim_client'] = ['dim_client.sql','dim_client']

CREATE_TABLES['dim_fc'] = (
    "CREATE TABLE dim_fc ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  name varchar(14)," 
    "  long_name varchar(50)," 
    "  add_datetime datetime,"    
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['dim_fc'] = ['dim_fc.sql','dim_fc']

CREATE_TABLES['dim_pack_type'] = (
    "CREATE TABLE dim_pack_type ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  name varchar(14),"
    "  add_datetime datetime,"
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['dim_pack_type'] = ['dim_pack_type.sql','dim_pack_type']

CREATE_TABLES['dim_time'] = (
    "CREATE TABLE dim_time ("
    "  id int(11) NOT NULL AUTO_INCREMENT,"   
    "  day date,"  
    "  weeknum int(11),"
    "  yearweek varchar(14),"
    "  week varchar(14),"
    "  season int(11),"
    "  add_datetime datetime,"
    "  PRIMARY KEY (id)"
    ") ENGINE=InnoDB")
FROM_TO['dim_time'] = ['dim_time.sql','dim_time']

TABLES = {'CREATE_TABLES': CREATE_TABLES,
          'FROM_TO': FROM_TO}
x = TABLES



        