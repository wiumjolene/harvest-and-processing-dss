# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 15:20:03 2020

@author: Jolene
"""

import random
import copy
import datetime

import pandas as pd

import allocate as aloc
import source_etl as setl
import variables
from connect import engine_phd


def create_options(df_dp_co,df_pc_co,df_he_co,df_lugs_co):
    df_dp = setl.demand_plan()
    df_pc = setl.pack_capacity()
    df_he = setl.harvest_estimate()
    df_lugs = setl.lug_generation()

    df_dp = df_dp_co.reset_index(drop=True)
    df_pc = df_pc_co.reset_index(drop=True)
    df_he = df_he_co.reset_index(drop=True)
    df_lugs = df_lugs_co.reset_index(drop=True)
    
    list_dp = df_dp['id'].tolist()
    list_he = df_he['id'].tolist()
    list_pc = df_pc['id'].tolist()
    
    ddic_pc = {}
    ddic_he = {}
    no_he = []
    no_pc = []
    ddic_options={}
    ddic_metadata={}
    df_demand_lug = pd.DataFrame({})
    df_demand_pc = pd.DataFrame({})
    
    print('start do: ' + str(datetime.datetime.now()))
    
    for d in range(0,len(df_dp)):
        ddemand_id = df_dp.id[d]
        dvacat_id = df_dp.vacat_id[d]
        dtime_id = int(df_dp.time_id[d])
        dpack_type_id = df_dp.pack_type_id[d]
        ddic_metadata.update({ddemand_id: {'vacat_id': dvacat_id,
                                           'time_id': dtime_id,
                                           'pack_type_id': dpack_type_id}})
        
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
            ddf_lugs['demand_id'] = ddemand_id
            df_demand_lug = df_demand_lug.append(ddf_lugs).reset_index(drop=True)

        ddic_he.update({ddemand_id: ddic_het})
        list_he = [x for x in list_he if x not in ddf_he['id'].tolist()]

        if len(ddf_he) == 0:
            no_he.append(ddemand_id)

        # find all available pack_capacities for demand    
        ddf_pc = df_pc[df_pc['time_id']==dtime_id]
        ddf_pc = ddf_pc[ddf_pc['pack_type_id']==dpack_type_id].reset_index(drop=True)
        ddic_pc.update({ddemand_id: ddf_pc['id'].tolist()})
        list_pc = [x for x in list_pc if x not in ddf_pc['id'].tolist()]
        ddf_pc['demand_id'] = ddemand_id
        df_demand_pc = df_demand_pc.append(ddf_pc).reset_index(drop=True)
        
        if len(ddf_pc) == 0:
            no_pc.append(ddemand_id)
    
    dlist_ready = [x for x in list_dp if x not in no_he]
    dlist_ready = [x for x in dlist_ready if x not in no_pc]
    
    ddic_options.update({'demands_ready_for_allocation':dlist_ready})
    ddic_options.update({'demands_pc':ddic_pc})
    ddic_options.update({'demands_he':ddic_he})
    ddic_options.update({'demands_no_he':no_he}) # all he for demand with lugs in he
    ddic_options.update({'demands_no_pc':no_pc})    
    ddic_options.update({'he_no_ass':list_he})
    ddic_options.update({'pc_no_ass':list_pc}) 
    ddic_options.update({'demands_metadata':ddic_metadata})  

    df_demand_lug.to_sql('do_demand_lugs',engine_phd,if_exists='replace',index=False)
    df_demand_pc.to_sql('do_demand_pc',engine_phd,if_exists='replace',index=False) 
    print('finish do: ' + str(datetime.datetime.now()))                                                 
    return(ddic_options)
    


def individual(solution_num, df_dp, df_ft, df_he, dic_pc,
               demand_options, demand_list=0, he_list=0):
    # import relevant tables
    dic_dp = df_dp.set_index('id').T.to_dict('dic')
    
    # get list of all demands with pc and he options 
    if demand_list == 0:
        dlist_allocate = demand_options['demands_ready_for_allocation']
    else:
        dlist_allocate = demand_list
    
    ddic_notes = {}
    ddic_solution_2 = {}
    note = ''
    d_count = 0
    ddic_solution = {}
    llist_usedlugs = []
    cdic_chromosome = {}
    cdic_chromosome2 = {}
    clist_chromosome2 = []
    clist_chromosome2_d = []
    cdic_fitness = {'km':0,'kg':0, 'obj1': 0, 'obj2': 0}
    
    absolute_diff = 0
    for d in dlist_allocate:
        ddic_metadata = demand_options['demands_metadata'][d]
        kg = 0
        dkg_raw = dic_dp[d]['kg_raw']

        # list of he's and lugs for demand he
        ddic_he = demand_options['demands_he'][d]
        # get a list of all available he's (without lugs)
        dlist_he = list(ddic_he.keys())
        
        # allocate lugs to d
        cd_he = {}
        cd_he2 = []
        he_count = 0
        while dkg_raw >= 0:
            # get a random position in available he estimates and select he
            if he_list == 0:
                if len(dlist_he) == 0:
                    note = 'no he available'
                    break                
                else:
                    hepos = random.randint(0,len(dlist_he)-1)
                    he = dlist_he[hepos]
                    dlist_he.remove(he)  # remove he from list to not reuse it

            else:
                if len(he_list[d_count]) > he_count:
                    he = he_list[d_count][he_count]
                    
                else:
                    break
            
            he_count = he_count + 1
            
            # get list of all lugs available in the he
            dlist_he_lugs = ddic_he[he]
            
            #ensure lugs can be packed
            dlist_he_lugs_s = [x for x in dlist_he_lugs if x not in llist_usedlugs]
    
            # get closest pc for he from available pc's
            df_het = df_he[df_he['id'] == he].reset_index(drop=True)
            block_id = df_het.block_id[0]
            
            # variables to determine speed  -> add calculate the number of hours spent on 
            va_id = df_het.va_id[0]
            pack_type_id = ddic_metadata['pack_type_id']
            
            df_ftt = df_ft[df_ft['block_id'] == block_id].reset_index(drop=True)
            df_ftt = df_ftt.filter(['packhouse_id','km'])
            
            # loop through available lugs of he only if lugs are available
            cd_he_lug = []
            if len(dlist_he_lugs_s) > 0:
                for l in dlist_he_lugs_s:
                    if dkg_raw >= 0:
                        dkg_raw = dkg_raw - variables.s_unit
                        kg = kg + variables.s_unit
                        llist_usedlugs.append(l) 
                        # get all available pc's for lug and sort from closest to furthest
                        df_pct = aloc.allocate_pc(dic_pc,df_ftt,ddic_metadata)
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
                        cd_he_lug.append(l)

                        ddic_solution.update({l:{'pack_capacity_id':lug_pc,
                                                 'demand_id': d,
                                                 'harvest_estimate_id':he,
                                                 'demand_id': d,
                                                 'lug_id':l,
                                                 'km': lug_km,
                                                 'kg_raw': variables.s_unit,
                                                 'kg': kg_nett,
                                                 'stdunits': kg_nett/variables.stdunit}})

                        cdic_fitness['kg'] =  cdic_fitness['kg'] + kg_nett
                        cdic_fitness['km'] =  cdic_fitness['km'] + lug_km
                    else:
                        note = 'no more lugs available in he'
                        break
                
                cd_he.update({he:cd_he_lug})
                cd_he2.append(he)
        
        absolute_diff = absolute_diff + (abs(dic_dp[d]['kg_raw'] - dkg_raw))
        d_count = d_count + 1
        ddic_notes.update({d:note})
        cdic_chromosome.update({d:cd_he})
        clist_chromosome2.append(cd_he2)
        clist_chromosome2_d.append(d)
        cdic_chromosome2.update({'clist_chromosome2':clist_chromosome2,
                                 'clist_chromosome2_d':clist_chromosome2_d})
        
    cdic_fitness['obj1'] = absolute_diff
    ddic_solution_2.update({solution_num: {'ddic_solution':ddic_solution,
                                      'ddic_notes':ddic_notes,
                                      'cdic_chromosome':cdic_chromosome,
                                      'cdic_chromosome2':cdic_chromosome2,                                      
                                      'cdic_fitness':cdic_fitness}})

    ddf_solution = pd.DataFrame.from_dict(ddic_solution, orient='index')
    ddf_solution['solution_num'] = solution_num
    return(ddic_solution_2)
    
def population(demand_options_imgga, df_dp_imgga, df_ft_imgga, df_he_imgga, dic_pc_imgga):
        
    demand_options_im = copy.deepcopy(demand_options_imgga)
    df_dp_im = df_dp_imgga.reset_index(drop=True)
    df_ft_im = df_ft_imgga.reset_index(drop=True)
    df_he_im = df_he_imgga.reset_index(drop=True)
    dic_pc_im = copy.deepcopy(dic_pc_imgga)    
    
    
    pdic_solution = {}
    p_fitness = {}
    
    print('start pop: ' + str(datetime.datetime.now()))
    
#    print('### generating population ###')
    for p in range(variables.population_size):
#        print('-creating individual ' + str(p))
        # make deep copies of dictionaries so as not to update main
        dic_pc_p = copy.deepcopy(dic_pc_im)
        demand_options_p = copy.deepcopy(demand_options_im)
        
        # create individual
        cdic_solution = individual(solution_num = p,
                                       df_dp = df_dp_im,
                                       df_ft = df_ft_im,
                                       df_he = df_he_im,
                                       dic_pc = dic_pc_p,
                                       demand_options = demand_options_p)
        
        # add individual to population
        pdic_solution.update(cdic_solution)
        
        # update fitness tracker
        p_fitness.update({p:[cdic_solution[p]['cdic_fitness']['km'],
                             cdic_solution[p]['cdic_fitness']['kg']]})
    population = {'pdic_solution':pdic_solution,
                  'p_fitness':p_fitness}
    print('finish pop: ' + str(datetime.datetime.now()))
    return(population)