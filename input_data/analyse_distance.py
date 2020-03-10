# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 21:36:49 2020

@author: Jolene
"""
import  googlemaps
import pandas as pd
import numpy as np
from connect import engine_phd

df_packhouse = pd.read_sql('SELECT * FROM dss.dim_packhouse;', engine_phd)
df_block = pd.read_sql('SELECT * FROM dss.dim_block;', engine_phd)

df_block  = df_block[df_block['longitude'] > 0].reset_index(drop=True)
df_packhouse  = df_packhouse[df_packhouse['longitude'] > 0].reset_index(drop=True)

key = 'AIzaSyBbm4F0L1HQRJxOilkVJm3ysquzDHGSp0A'
gmaps = googlemaps.Client(key = key)

from_to_df = pd.DataFrame({})
ft_id = 0
for i in range(0,len(df_block)):
    print(i)
    fromi = df_block.id[i]    
    latO = df_block.latitude[i]
    longO = df_block.longitude[i]
    
    for j in range(0,len(df_packhouse)):
        print(str(i) + ":" + str(j))
        ft_id = ft_id + 1
        toj = df_packhouse.id[j]
        latD = df_packhouse.latitude[j]
        longD = df_packhouse.longitude[j]
        orig = str(latO) + ',' + str(longO)
        dest = str(latD) + ',' + str(longD)
        try:
            result = gmaps.distance_matrix(orig, dest)
            result1 = round(result["rows"][0]["elements"][0]["distance"]["value"]/1000,2)
            data = [(ft_id,fromi,toj,result1)]
            col = ['id','block_id','packhouse_id','km']
            from_to_dft = pd.DataFrame(data,columns=col)
            from_to_df = from_to_df.append([from_to_dft]).reset_index(drop=True)
        except:
            print('issue detected')

from_to_df.to_sql('f_from_to',engine_phd,if_exists='replace',index=False)
