# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 09:58:11 2019

@author: Jolene
"""

import pandas as pd
import variables

def demand_plan():   
    df_dp = pd.read_excel(r'input_data/source_data.xlsx','f.demand_plan')
    df_dp['kg_raw'] = df_dp['stdunits'] * variables.stdunit * (1 + variables.giveaway)
    df_dp = df_dp.sort_values(by=['time_id', 'priority']).reset_index(drop=True)
    df_dp['trucks_raw'] = df_dp['kg_raw'] /variables.truck
    return(df_dp)

def harvest_estimate():   
    df_he = pd.read_excel(r'input_data/source_data.xlsx','f.harvest_estimate')
    df_va = pd.read_excel(r'input_data/source_data.xlsx','dim.va',index_col ='id',usecols='A,D')
    df_he = df_he.merge(df_va ,how='left', left_on = 'va_id', right_index=True)
    df_he['stdunits'] = (df_he['kg_raw'] * (1 - variables.giveaway)) / variables.stdunit
    df_he['trucks_raw'] = df_he['kg_raw'] / variables.truck
    df_he['lugs_raw'] = df_he['kg_raw'] / variables.lug
    return(df_he)

def pack_capacity():   
    df_pc = pd.read_excel(r'input_data/source_data.xlsx','f.pack_capacity')
    df_pc['stdunits'] = df_pc['kg'] / variables.stdunit
    df_pc['trucks_raw'] = (df_pc['kg'] * (1 + variables.giveaway))/variables.truck
    return(df_pc)
    
def pack_capacity_dic():
    df_pc = pack_capacity()
    df_pc['kg_remain'] = df_pc['kg']
    df_pc['id2'] = df_pc['id']
    df_pc = df_pc.set_index('id2')
    dic_pc = df_pc.to_dict('index')
    return(dic_pc)
    
def from_to():   
    df_ft = pd.read_excel(r'input_data/source_data.xlsx','f.from_to')
    return(df_ft)
    
def lug_generation():   
    """transform harvest estimate into lists of lugs"""
    df_he = harvest_estimate()
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
    return(df_lugs)
