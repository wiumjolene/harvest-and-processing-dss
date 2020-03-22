# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 06:57:20 2020

@author: Jolene
"""
#from __future__ import print_function
import pandas as pd
import datetime
import variables
from connect import engine_central
from connect import engine_phd
from input_data.models import TABLES
from input_data.models import DB_NAME

import mysql.connector
from mysql.connector import errorcode
from connect import mydb as cnx_phd

cursor = cnx_phd.cursor()

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx_phd.database = DB_NAME
    else:
        print(err)
        exit(1)
        
        
for table_name in TABLES['CREATE_TABLES']:
    table_description = TABLES['CREATE_TABLES'][table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")
cursor.close()
cnx_phd.close()

print('')
print('')
for table in TABLES['FROM_TO']:
#    print(table)
    if TABLES['FROM_TO'][table][0] != 0:
        open_file=open('sql\\'+table+'.sql','r')
        sql = open_file.read()
        open_file.close()
        
        table_central = pd.read_sql(sql,engine_central)
        table_phd = pd.read_sql('select * from '+table+';',engine_phd)
        if table == 'dim_block':
            coo = pd.read_excel('oc_site.xlsx', 'pu')
            table_central = pd.merge(table_central, coo, how='left', on='id')

        if table == 'dim_packhouse':
            coo = pd.read_excel('venue.xlsx', 'venue_metadata')
            table_central = pd.merge(table_central, coo, how='left', on='name')
        
        df1_i = table_central.set_index(['id'])
        df2_i = table_phd.set_index(['id'])
        df_diff = df1_i.join(df2_i,how='outer',rsuffix='UPDATE').fillna(0)
        
        table_add = df_diff.reset_index(drop = False)
        rem_cols = [col for col in table_add.columns if 'UPDATE' in col]
        table_add = table_add[table_add[rem_cols[0]]==0].reset_index(drop = True)
        rem_cols = [col for col in table_add.columns if 'UPDATE' in col]
        table_add = table_add.drop(rem_cols,axis=1)
        table_add['add_datetime'] = datetime.datetime.now()
        
        if len(table_add) > 0:
            table_add.to_sql(table,engine_phd,if_exists='append',index=False)
            print(table + ' has been updated')
            
        else:
            print('no new updates to ' + table)


lugs_sql = """
SELECT 
    he.id, he.va_id, he.block_id, w.id AS time_id, he.kg_raw
FROM
    dss.f_harvest_estimate he
        LEFT JOIN
    dim_week w ON he.packweek = w.week
WHERE
    he.block_id IN (43 , 5, 6, 1, 35, 47, 45, 46)
        AND kg_raw > 0;
"""

df_he = pd.read_sql(lugs_sql,engine_phd)
df_va = pd.read_sql('SELECT * FROM dss.dim_va;',engine_phd,index_col ='id')
df_he = df_he.merge(df_va ,how='left', left_on = 'va_id', right_index=True)
df_he['stdunits'] = (df_he['kg_raw'] * (1 - variables.giveaway)) / variables.stdunit
df_he['trucks_raw'] = df_he['kg_raw'] / variables.truck
df_he['lugs_raw'] = df_he['kg_raw'] / variables.lug
df_lugs = pd.DataFrame({})
columns = ['he_id','block_id','va_id','vacat_id','time_id','kg']
for i in range(0,len(df_he)):
    he_id = df_he.id[i]
    numlugs = df_he.lugs_raw[i]
    block = df_he.block_id[i]
    va = df_he.va_id[i]
    vacat = df_he.vacat_id[i]
    time = df_he.time_id[i]
    data = [[he_id,block,va,vacat,time,variables.lug]] * int(numlugs)
    df_lugst = pd.DataFrame(data = data, columns = columns)
    df_lugs = df_lugs.append(df_lugst).reset_index(drop=True)
df_lugs['id'] = df_lugs.index + 1
df_lugs.to_sql('f_lugs',engine_phd,if_exists='append',index=False)

