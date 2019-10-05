# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 08:18:44 2019

@author: Jolene
"""

import source_etl as setl

def create_options():
    df_dp = setl.demand_plan()
    df_pc = setl.pack_capacity()
    df_he = setl.harvest_estimate()
    df_lugs = setl.lug_generation()
    list_dp = df_dp['id'].tolist()
    list_he = df_he['id'].tolist()
    list_pc = df_pc['id'].tolist()
    
    ddic_pc = {}
    ddic_he = {}
    no_he = []
    no_pc = []
    ddic_options={}
    
    for d in range(0,len(df_dp)):
        ddemand_id = df_dp.id[d]
        dvacat_id = df_dp.vacat_id[d]
        dtime_id = df_dp.time_id[d]
        
        # find all available harvest estimates for demand 
        ddf_he = df_he[df_he['vacat_id']==dvacat_id]
        ddf_he = ddf_he[ddf_he['time_id']==dtime_id].reset_index(drop=True)
        dlist_he = ddf_he['id'].tolist()
        
        # get all the lugs in he
        ddic_het = {}
        for he in dlist_he:
            ddf_lugs = df_lugs[df_lugs['he_id'] == he].reset_index(drop=True)
            dlist_lugs = ddf_lugs['id'].tolist()
            ddic_het.update({he: dlist_lugs})

        ddic_he.update({ddemand_id: ddic_het})
        list_he = [x for x in list_he if x not in ddf_he['id'].tolist()]

        if len(ddf_he) == 0:
            no_he.append(ddemand_id)

        # find all available pack_capacities for demand    
        ddf_pc = df_pc[df_pc['time_id']==dtime_id]
        ddf_pc = ddf_pc[ddf_pc['pack_type_id']==dtime_id].reset_index(drop=True)
        ddic_pc.update({ddemand_id: ddf_pc['id'].tolist()})
        list_pc = [x for x in list_pc if x not in ddf_pc['id'].tolist()]
        
        if len(ddf_pc) == 0:
            no_pc.append(ddemand_id)
    
    dlist_ready = [x for x in list_dp if x not in no_he]
    dlist_ready = [x for x in dlist_ready if x not in no_pc]
    print('The following demands can be served: ' + str(dlist_ready))
    print('- The following demands = no harvest estimate options: ' + str(no_he))        
    print('- The following demands = no pack_capacity options: ' + str(no_pc))
    print('')
    ddic_options.update({'demands_ready_for_allocation':dlist_ready})
    ddic_options.update({'demands_pc':ddic_pc})
    ddic_options.update({'demands_he':ddic_he})
    ddic_options.update({'demands_no_he':no_he}) # all he for demand with lugs in he
    ddic_options.update({'demands_no_pc':no_pc})    
    ddic_options.update({'he_no_ass':list_he})
    ddic_options.update({'pc_no_ass':list_pc})                                                    
    return(ddic_options)
    

