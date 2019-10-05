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
dic_dp = df_dp.set_index('id').T.to_dict('dic')
demand_options = fo.create_options()

dlist_allocate = demand_options['demands_ready_for_allocation']

for d in dlist_allocate:
    dstdunits = dic_dp[d]['stdunits']
    dkg_raw = dic_dp[d]['kg_raw']
    dkg_raw2 = dic_dp[d]['kg_raw']
    
    dlist_pc = demand_options['demands_pc'][d]
    ddic_he = demand_options['demands_he'][d]
    dlist_he = list(ddic_he.keys())
    
    d_pc = dlist_pc[random.randint(0,len(dlist_pc)-1)]
    dlist_he_o = ddic_he[dlist_he[random.randint(0,len(dlist_he)-1)]]

    d_lugs = []
    for l in dlist_he_o:
        if dkg_raw > 0:
            dkg_raw = dkg_raw - variables.lug
            d_lugs.append(l)
