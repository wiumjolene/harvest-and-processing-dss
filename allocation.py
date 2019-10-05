# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 08:18:44 2019

@author: Jolene
"""

import source_etl as setl

def create_options():
    df_dp = setl.demand_plan()
    df_pc = setl.pack_capacity()
    df_lugs = setl.lug_generation()
    list_dp = df_dp['id'].tolist()
    list_lugs = df_lugs['id'].tolist()
    list_pc = df_pc['id'].tolist()
    
    ddic_pc = {}
    ddic_lugs = {}
    no_lug = []
    no_pc = []
    ddic_options={}
    
    for d in range(0,len(df_dp)):
        ddemand_id = df_dp.id[d]
        dvacat_id = df_dp.vacat_id[d]
        dtime_id = df_dp.time_id[d]
    
        # find all available lugs for demand    
        ddf_lug = df_lugs[df_lugs['vacat_id']==dvacat_id]
        ddf_lug = ddf_lug[ddf_lug['time_id']==dtime_id].reset_index(drop=True)
        ddic_lugs.update({ddemand_id: ddf_lug['id'].tolist()})
        list_lugs = [x for x in list_lugs if x not in ddf_lug['id'].tolist()]
        
        if len(ddf_lug) == 0:
            no_lug.append(ddemand_id)
            
        # find all available pack_capacities for demand    
        ddf_pc = df_pc[df_pc['time_id']==dtime_id]
        ddf_pc = ddf_pc[ddf_pc['pack_type_id']==dtime_id].reset_index(drop=True)
        ddic_pc.update({ddemand_id: ddf_pc['id'].tolist()})
        list_pc = [x for x in list_pc if x not in ddf_pc['id'].tolist()]
        
        if len(ddf_pc) == 0:
            no_pc.append(ddemand_id)
    
    dlist_ready = [x for x in list_dp if x not in no_lug]
    dlist_ready = [x for x in dlist_ready if x not in no_pc]
    print('The following demands = no lug options: ' + str(no_lug))        
    print('The following demands = no pack_capacity options: ' + str(no_pc))
    print('The following demands can be served: ' + str(dlist_ready))
    print('')
    ddic_options.update({'dlist_ready':dlist_ready})
    ddic_options.update({'ddic_pc':ddic_pc})
    ddic_options.update({'ddic_lugs':ddic_lugs})
    ddic_options.update({'no_lug':no_lug})
    ddic_options.update({'no_pc':no_pc})    
    ddic_options.update({'lugs with no ass':list_lugs})
    ddic_options.update({'pc with no ass':list_pc})                                                    
    return(ddic_options)
    
test = create_options()
