# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 10:57:15 2020

@author: Jolene
"""
from sqlalchemy.dialects import mysql
import mysql.connector
from sqlalchemy import create_engine
import os


if os.getenv('COMPUTERNAME') == 'DESKTOP-7LVDBO0':
    connect = r'C:\sumitins\connect'
    
    
    open_file=open(connect + '\\password8','r')
    file_lines=open_file.readlines()
    sun = file_lines[0].strip()  # First Line
    spw = file_lines[1].strip()  # Second Line
    
    host="159.65.247.178"
    port="3306"
    user=sun
    passwd=spw
    database="dss"
    
    engine_phd = create_engine('mysql://' + user + ':' + passwd + '@' + host + ':' + port + '/' + database)
    
    mydb = mysql.connector.connect(
      host=host,
      port=port,
      user=user,
      passwd=passwd
    )
    
    open_file=open(connect + '\\password4','r')
    file_lines=open_file.readlines()
    sunW = file_lines[0].strip()  # First Line
    spwW = file_lines[1].strip()  # Second Line
    
    engine_central = create_engine('mysql://' + sunW + ':' + spwW + '@10.16.20.5:3306/pt_admin1718')
    
        
else:
#    connect = r'~/phd/connect'
    connect = os.path.join(os.path.expanduser('~'), 'phd', 'connect','password3')

    open_file=open(connect,'r')
    file_lines=open_file.readlines()
    sun = file_lines[0].strip()  # First Line
    spw = file_lines[1].strip()  # Second Line
    
    host="127.0.0.1"
    port="3306"
    user=sun
    passwd=spw
    database="dss"
    
    engine_phd = create_engine('mysql://' + user + ':' + passwd + '@' + host + ':' + port + '/' + database)
    
