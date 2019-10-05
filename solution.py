# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 15:13:08 2019

@author: Jolene
"""
import feasible_options as fo
import source_etl as setl
import random
import variables


#### basic feasible solutions ####
df_dp = setl.demand_plan()
df_ft = setl.from_to()
df_he = setl.harvest_estimate()
df_pc = setl.pack_capacity()
dic_dp = df_dp.set_index('id').T.to_dict('dic')
demand_options = fo.create_options()

dlist_allocate = demand_options['demands_ready_for_allocation']

ddic_lug_allocation = {}
ddic_solution = {}

for d in dlist_allocate:
    kg = 0
    dstdunits = dic_dp[d]['stdunits']
    dkg_raw = dic_dp[d]['kg_raw']
    dkg_raw2 = dic_dp[d]['kg_raw']
    
    dlist_pc = demand_options['demands_pc'][d]
    ddic_he = demand_options['demands_he'][d]
    dlist_he = list(ddic_he.keys())
    
    d_pc = dlist_pc[random.randint(0,len(dlist_pc)-1)]
    key = dlist_he[random.randint(0,len(dlist_he)-1)]
    dlist_he_o = ddic_he[key]
    dlist_he_r = ddic_he[key]

    d_lugs = []
    for l in dlist_he_o:
        if dkg_raw > 0:
            dkg_raw = dkg_raw - variables.lug
            d_lugs.append(l)
            dlist_he_r.remove(l)
            kg = kg + variables.lug
            
    ddic_lug_allocation.update({d:d_lugs})
    demand_options['demands_he'][d].update({key:dlist_he_r})

    df_het = df_he[df_he['id'] == key].reset_index(drop=True)
    block_id = df_het.block_id[0]
    
    df_pct = df_pc[df_pc['id'] == d_pc].reset_index(drop=True)
    packhouse_id = df_pct.packhouse_id[0]
    
    df_ftt = df_ft[df_ft['block_id'] == block_id]
    df_ftt = df_ftt[df_ftt['packhouse_id'] == packhouse_id].reset_index(drop=True)
    km = df_ftt.km[0]

    
    ddic_solution.update({d:{'lugs':d_lugs,
                             'pc':d_pc,
                             'km': km,
                             'weight': kg}})       
   
    
    