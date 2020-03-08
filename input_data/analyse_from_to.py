# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 12:55:55 2019

@author: Jolene

https://www.google.com/maps/d/u/0/edit?hl=en&mid=1ulL5Iu0NhpSBfI72rLe1qXXojibX6T4X&ll=-28.690633405386414%2C20.069170299999996&z=9
"""
import  googlemaps
import datetime
import pandas as pd
import numpy as np
import mpu

df_packhouse = pd.read_csv('venue_metadata.csv')
df_oc = pd.read_excel('oc_site.xlsx','oc')

df_oc  = df_oc[df_oc['show'] > 0].reset_index(drop=True)
df_packhouse  = df_packhouse[df_packhouse['long'] > 0].reset_index(drop=True)

key = 'AIzaSyBbm4F0L1HQRJxOilkVJm3ysquzDHGSp0A'
gmaps = googlemaps.Client(key = key)

directions_df = pd.DataFrame({})
for i in range(0,len(df_oc)):
    print(i)
    fromi = df_oc.fc_oc[i]    
    latO = df_oc.lat[i]
    longO = df_oc.long[i]
    
    for j in range(0,len(df_packhouse)):
        print(str(i) + ":" + str(j))
        toj = df_packhouse.venuecode[j]
        latD = df_packhouse.lat[j]
        longD = df_packhouse.long[j]

        origin = str(latO) + ',' + str(longO)
        destination = str(latD) + ',' + str(longD)
                
        now = datetime.datetime.now()
        directions_result = gmaps.directions(origin,
                                             destination,
                                             mode="driving",
                                             departure_time=now)

        directions_dic = directions_result[0]['legs'][0]['steps']
        
        for x in directions_dic:
            distance = x['distance']['value']
            end_lat = x['end_location']['lat']
            end_long = x['end_location']['lng']
            route_a = [(distance,end_lat,end_long,fromi,toj)]
            df_route_a = pd.DataFrame(route_a,columns = ['distance','end_lat','end_long','from','to',])
            directions_df = directions_df.append([df_route_a]).reset_index(drop=True)

directions_df['from_to'] = directions_df['from'] + ':' + directions_df['to']
directions_dfshort = directions_df.groupby(['from','to','from_to'])['distance'].sum()
directions_dfshort = directions_dfshort.reset_index()

#directions_df.to_csv('input_data\\from_to_detail_m.csv')
#directions_dfshort.to_csv('input_data\\from_to_m.csv')