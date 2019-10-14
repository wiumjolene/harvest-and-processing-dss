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

def population(solution_num):
#    solution_num = 0
    
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
    
    ddic_notes = {}
    ddic_solution_2 = {}
    note = ''
    ddic_solution = {}
    llist_usedlugs = []
    
    for d in dlist_allocate:
        d=6
        ddic_metadata = demand_options['demands_metadata'][d]
        kg = 0
        dkg_raw = dic_dp[d]['kg_raw']        
        # list of he's and lugs for demand he
        ddic_he = demand_options['demands_he'][d]
        # get a list of all available he's (without lugs)
        dlist_he = list(ddic_he.keys())
        
        # allocate lugs to d
        while dkg_raw > 0:
            if len(dlist_he) == 0:
                note = 'no he available'
                break
                
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
            
            # loop through available lugs of he only if lugs are available
            if len(dlist_he_lugs_s) > 0:
                for l in dlist_he_lugs_s:
                    if dkg_raw > 0:
                        dkg_raw = dkg_raw - variables.s_unit
                        kg = kg + variables.s_unit
                        llist_usedlugs.append(l) 
                        # get all available pc's for lug and sort from closest to furthest
                        df_pc = pd.DataFrame.from_dict(dic_pc, orient='index')
                        df_pct = df_pc.merge(df_ftt, on = 'packhouse_id')  # get distance from block
                        df_pct = df_pct[df_pct['time_id'] == ddic_metadata['time_id']]
                        df_pct = df_pct[df_pct['km'] < variables.travel_restriction]
                        df_pct = df_pct[df_pct['pack_type_id'] == ddic_metadata['pack_type_id']]
                        df_pct = df_pct[df_pct['kg_remain'] >= variables.s_unit]
                        df_pct = df_pct.sort_values(['km']).reset_index(drop=True)
                        dlist_pc = df_pct['id'].tolist()
                        dlist_pc_km = df_pct['km'].tolist() 
                        if len(dlist_pc) > 0:
                            # allocate closest pc to block
                            lug_pc = int(dlist_pc[0])
                            lug_km = dlist_pc_km[0]
                            # subtract kg from pc capacity for day  
                            pckg_remain = dic_pc[lug_pc]['kg_remain'] - variables.s_unit
                            dic_pc[lug_pc]['kg_remain'] =  pckg_remain
                        else:
                            lug_pc = 0
                            note = 'no pc available'
                            break
                        
                        kg_nett = variables.s_unit * (1 - variables.giveaway)
                        ddic_solution.update({l:{'pack_capacity_id':lug_pc,
                                                 'demand_id': d,
                                                 'harvest_estimate_id':he,
                                                 'demand_id': d,
                                                 'lug_id':l,
                                                 'km': lug_km,
                                                 'kg_raw': variables.s_unit,
                                                 'kg': kg_nett,
                                                 'stdunits': kg_nett/variables.stdunit}})
                    else:
                        note = 'no more lugs available in he'
                        break
    
        ddic_notes.update({d:note})
    ddic_solution_2.update({solution_num: {'ddic_solution':ddic_solution,
                                      'ddic_notes':ddic_notes}})

    ddf_solution = pd.DataFrame.from_dict(ddic_solution, orient='index')
    ddf_solution['solution_num'] = solution_num
    return(ddic_solution_2)

 