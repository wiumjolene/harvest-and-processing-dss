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
else:
    connect = r''

open_file=open(connect + '\\password3','r')
file_lines=open_file.readlines()
sun = file_lines[0].strip()  # First Line
spw = file_lines[1].strip()  # Second Line

host="127.0.0.1"
port="3307"
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

#mycursor = mydb.cursor()