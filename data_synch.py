# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 06:57:20 2020

@author: Jolene
"""
import pandas as pd
from connect import engine_central
from connect import engine_phd


table = 'dim_va'
open_file=open('input_data\\sql\\'+table+'.sql','r')
sql = open_file.read()
open_file.close()

table_central = pd.read_sql(sql,engine_central)
table_phd = pd.read_sql('select * from '+table+';',engine_phd)

df1_i = table_central.set_index(['id','name'])
df2_i = table_phd.set_index(['id','name'])
df_diff = df1_i.join(df2_i,how='outer',rsuffix='UPDATE').fillna(0)
#df_diff = (df_diff['Num'] - df_diff['Num_'])

table_add = df_diff.reset_index(drop = False)
rem_cols = [col for col in table_add.columns if 'UPDATE' in col]
table_add = table_add[table_add[rem_cols[0]]==0].reset_index(drop = True)
rem_cols = [col for col in table_add.columns if 'UPDATE' in col]
table_add = table_add.drop(rem_cols,axis=1)

if len(table_add) > 0:
    table_add.to_sql(table,engine_phd,if_exists='append',index=False)
else:
    print('table is up to date')