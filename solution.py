# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 15:13:08 2019

@author: Jolene
"""
import feasible_options as fo
import source_etl as setl
import random
import variables
import pandas as pd


# import relevant tables
df_dp = setl.demand_plan()
df_ft = setl.from_to()
df_he = setl.harvest_estimate()
dic_dp = df_dp.set_index('id').T.to_dict('dic')
dic_pc = setl.pack_capacity_dic()

# create a dictionary of options and issues
demand_options = fo.create_options()

# get list of all demands with pc and he options 
dlist_allocate = demand_options['demands_ready_for_allocation']

ddic_lug_allocation = {}
ddic_solution = {}
llist_usedlugs = []
llist_usedhe = []

for d in dlist_allocate:
    ddic_metadata = demand_options['demands_metadata'][d]
    kg = 0
    dstdunits = dic_dp[d]['stdunits']
    dkg_raw = dic_dp[d]['kg_raw']
    dkg_raw2 = round(dic_dp[d]['kg_raw'],2)  # variable to subrtact allocated he from
    
    # list of pc's for demand d
#    dlist_pc = demand_options['demands_pc'][d]
    # list of he's and lugs for demand he
    ddic_he = demand_options['demands_he'][d]
    # get a list of all available he's (without lugs)
    dlist_he = list(ddic_he.keys())
    
    # allocate lugs to d
    d_lugs = []
    while dkg_raw > 0:
        # get a random position in available he estimates and select he
        hepos = random.randint(0,len(dlist_he)-1)
        he = dlist_he[hepos]
        # get list of all lugs available in the he
        dlist_he_lugs = ddic_he[he]
        dlist_he.remove(he)  # remove he from list to not reuse it
        #ensure lugs can be packed
        dlist_he_lugs_s = [x for x in dlist_he_lugs if x not in llist_usedlugs]

        # get closest pc for he from available pc's
        df_het = df_he[df_he['id'] == he].reset_index(drop=True)
        block_id = df_het.block_id[0]
        
        df_ftt = df_ft[df_ft['block_id'] == block_id].reset_index(drop=True)
        df_ftt = df_ftt.filter(['packhouse_id','km'])
        
        # loop through available lugs of he
        if len(dlist_he_lugs_s) > 0:
            for l in dlist_he_lugs_s:
                if dkg_raw > 0:
                    dkg_raw = dkg_raw - variables.lug
                    kg = kg + variables.lug
                    d_lugs.append(l)
                    llist_usedlugs.append(l) 
                    
                    df_pc = pd.DataFrame.from_dict(dic_pc, orient='index')
                    df_pct = df_pc.merge(df_ftt, on = 'packhouse_id')
            
                    df_pct = df_pct[df_pct['time_id'] == ddic_metadata['time_id']]
                    df_pct = df_pct[df_pct['pack_type_id'] == ddic_metadata['pack_type_id']]
                    df_pct = df_pct[df_pct['kg_remain'] > 0]
                    df_pct = df_pct.sort_values(['km']).reset_index(drop=True)
                    dlist_pc = df_pct['id'].tolist()  
                    dlist_pc_km = df_pct['km'].tolist() 

                    if len(dlist_pc) > 0:
                        # allocate closest pc to block
                        lug_pc = int(dlist_pc[0])
                        lug_km = dlist_pc_km[0]
                        # subtract kg from pc capacity for day  
                        pckg_remain = dic_pc[lug_pc]['kg_remain'] - variables.lug
                        dic_pc[lug_pc]['kg_remain'] =  pckg_remain
                        
                    else:
                        lug_pc = 0

                    ddic_solution.update({d:{'lugs':d_lugs,
                                             'pc':lug_pc,
                                             'km': lug_km,
                                             'weight': kg,
                                             'demand_kg':dkg_raw2}})
                    
                    
                else:
                    break

 





    
    

#update packhouse capacity
#select new list of lugs/ packhouse capacities if other one fails/ too small    