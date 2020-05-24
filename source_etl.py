# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 09:58:11 2019

@author: Jolene
"""

import pandas as pd
import variables
from connect import engine_phd

def demand_plan(): 
    s = """SELECT 
            fdp.id,
            fdp.client_id,
            fdp.vacat_id,
            fdp.pack_type_id,
            fdp.priority,
            fdp.arrivalweek,
            w.id AS arrival_time_id,
            fdp.stdunits,
            fdp.transitdays,
            w.id - (ceiling(fdp.transitdays/7) * 7) as time_id
        FROM
            dss.f_demand_plan fdp
                LEFT JOIN
            dim_week w ON fdp.arrivalweek = w.week"""
    df_dp = pd.read_sql(s,engine_phd)
    df_dp['kg_raw'] = df_dp['stdunits'] * variables.stdunit * (1 + variables.giveaway)
    df_dp = df_dp.sort_values(by=['time_id', 'priority']).reset_index(drop=True)
    df_dp['trucks_raw'] = df_dp['kg_raw'] /variables.truck
    return(df_dp)

def harvest_estimate(): 
    s= """SELECT 
            he.id, he.va_id, he.block_id, w.id AS time_id, he.kg_raw
        FROM
            dss.f_harvest_estimate he
                LEFT JOIN dim_week w ON he.packweek = w.week
        WHERE
            kg_raw > 0;"""
#            he.block_id in (43, 5, 6 ,1, 35, 47, 45, 46)
    df_he = pd.read_sql(s,engine_phd)
    df_va = pd.read_sql('SELECT * FROM dss.dim_va;',engine_phd,index_col ='id')
    df_he = df_he.merge(df_va ,how='left', left_on = 'va_id', right_index=True)
    df_he['stdunits'] = (df_he['kg_raw'] * (1 - variables.giveaway)) / variables.stdunit
    df_he['trucks_raw'] = df_he['kg_raw'] / variables.truck
    df_he['lugs_raw'] = df_he['kg_raw'] / variables.lug
    return(df_he)

def pack_capacity(): 
    s = """SELECT 
        pc.id,
        pc.packhouse_id,
        pc.pack_type_id,
        w.id AS time_id,
        pc.kg,
        pc.stdunits
    FROM
        dss.f_pack_capacity pc
            LEFT JOIN
        dim_week w ON pc.packweek = w.week;"""
    df_pc = pd.read_sql(s,engine_phd)
    df_pc['stdunits'] = df_pc['kg'] / variables.stdunit
    df_pc['trucks_raw'] = (df_pc['kg'] * (1 + variables.giveaway))/variables.truck
    return(df_pc)
    
def pack_capacity_dic():
    df_pc = pack_capacity()
    df_pc['kg_remain'] = df_pc['kg'] * (1 + variables.giveaway)
    df_pc['id2'] = df_pc['id'].reset_index(drop=True)
    df_pc = df_pc.set_index('id2')
    df_pc['time_id'] = df_pc['time_id'].astype(int)
    dic_pc = df_pc.to_dict('index')
    return(dic_pc)
    
def from_to():   
    df_ft = pd.read_sql('SELECT * FROM dss.f_from_to;',engine_phd)
    return(df_ft)
    
def lug_generation():   
    """transform harvest estimate into lists of lugs"""
    s = """SELECT id, he_id,block_id,va_id,vacat_id,time_id,kg 
        FROM dss.f_lugs;"""
    df_lugs = pd.read_sql(s,engine_phd)
    return(df_lugs)


def speed():
    s = """SELECT * FROM dss.f_speed;"""
    df_speed = pd.read_sql(s,engine_phd)
    
    dic_speed = {}
    packhouses = df_speed.filter(['packhouse_id']).drop_duplicates()
    packhouses = packhouses['packhouse_id'].tolist()
    for p in packhouses:
        
        df_speed1 = df_speed[df_speed['packhouse_id']==p].reset_index(drop=True)
        packtypes = df_speed1.filter(['packtype_id']).drop_duplicates()
        packtypes = packtypes['packtype_id'].tolist()
        
        dic_packtypes = {}
        for pt in packtypes:
        
            df_speed2 = df_speed1[df_speed1['packtype_id']==pt].reset_index(drop=True)
            vas = df_speed2.filter(['va_id']).drop_duplicates()
            vas = vas['va_id'].tolist()   
            
            dic_vas = {}
            for va in vas:
                df_speed3 = df_speed2[df_speed2['va_id']==va].reset_index(drop=True)
                speed = df_speed3.speed[0]
                
                dic_vas.update({va: speed})
            dic_packtypes.update({pt:dic_vas})
        dic_speed.update({p:dic_packtypes})
    return(dic_speed)