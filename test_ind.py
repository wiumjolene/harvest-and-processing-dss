# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 14:37:16 2020

@author: Jolene
"""

import random

import pandas as pd
import matplotlib.pyplot as plt
import datetime

import population as pop
import variables
import allocate as aloc
import source_etl as setl

df_dp = setl.demand_plan()
df_ft = setl.from_to()
df_he = setl.harvest_estimate()
dic_pc = setl.pack_capacity_dic()
df_pc_imgga = setl.pack_capacity()
df_lugs_imgga = setl.lug_generation()
demand_options = pop.create_options(df_dp, df_pc_imgga, df_he, df_lugs_imgga)
dic_speed = setl.speed()

solution_num = 0
start_ind = datetime.datetime.now()
demand_list=0
he_list=0

# import relevant tables
dic_dp = df_dp.set_index('id').T.to_dict('dic')
df_he['kg_raw_remain'] = df_he['kg_raw']
dic_he = df_he.set_index('id').T.to_dict('dic')

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
cdic_chromosome = {}
cdic_chromosome2 = {}
clist_chromosome2 = []
clist_chromosome2_d = []
cdic_fitness = {'km':0,'kg':0, 'obj1': 0, 'obj2': 0, 'stdunits': 0,
                'workhours': 0}

absolute_diff = 0
l = 0
for d in dlist_allocate:
    kg = 0
    dkg_raw = demand_options['demands_metadata'][d]['kg_raw']

    # get a list of all available he's (without lugs)
    dlist_he = list(demand_options['demands_he'][d].keys())
    
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

        # get closest pc for he from available pc's
        block_id = dic_he[he]['block_id']
        
        # variables to determine speed  -> add calculate the number of hours spent on 
        va_id = dic_he[he]['va_id']
        packtype_id = demand_options['demands_metadata'][d]['pack_type_id']
        
        df_ftt = df_ft[df_ft['block_id'] == block_id].reset_index(drop=True)
        df_ftt = df_ftt.filter(['packhouse_id','km'])
        
    
        he_kg_raw = dic_he[he]['kg_raw_remain']
        
        if dic_he[he]['kg_raw_remain'] > dkg_raw:
            # subtract demand from he
            dic_he[he]['kg_raw_remain'] = dic_he[he]['kg_raw_remain'] - dkg_raw
            dkg_raw = 0
            
        else:
            # subtract he from demand
            dkg_raw = dkg_raw - dic_he[he]['kg_raw_remain']
            dic_he[he]['kg_raw_remain'] = 0
            
        he_kg_allocated = he_kg_raw - dic_he[he]['kg_raw_remain']
        
        cd_he_lug = []    
        kg = kg + variables.s_unit  
        # loop through pc until you allocate all he
        while he_kg_allocated > 0:
            if dkg_raw >= 0:
                # get all available pc's for lug and sort from closest to furthest
                df_pct = aloc.allocate_pc(dic_pc,df_ftt,demand_options['demands_metadata'][d])
                if len(df_pct) > 0:
                    # allocate closest pc to block
                    dhe_pc = df_pct.id[0]
                    packhouse_id = df_pct.packhouse_id[0]
                    lug_km = df_pct.km[0]
                    
                    he_pc_1 = dic_pc[dhe_pc]['kg_remain']
                    if dic_pc[dhe_pc]['kg_remain'] > he_kg_allocated:
                        dic_pc[dhe_pc]['kg_remain'] = dic_pc[dhe_pc]['kg_remain'] - he_kg_allocated
                        he_kg_allocated = 0
                    else:
                        he_kg_allocated = he_kg_allocated - dic_pc[dhe_pc]['kg_remain']
                        dic_pc[dhe_pc]['kg_remain'] = 0
                    
                    he_pc_allocated = he_pc_1 - dic_pc[dhe_pc]['kg_remain']
                    
                else:
                    dhe_pc = 0
                    he_pc_allocated = 0
                    note = 'no pc available'
                    break
                
                kg_nett = he_pc_allocated * (1 - variables.giveaway)
                stdunits = kg_nett/variables.stdunit
                
                try:
                    speed = dic_speed[packhouse_id][packtype_id][va_id]
                except:
                    speed = 12
                    
                l = l + 1
                cd_he_lug.append(l)
                ddic_solution.update({l:{'pack_capacity_id':dhe_pc,
                                         'demand_id': d,
                                         'harvest_estimate_id':he,
                                         'demand_id': d,
                                         'va_id':va_id,
                                         'packtype_id':packtype_id,
                                         'packhouse_id':packhouse_id,
                                         'lug_id':l,
                                         'speed':speed,
                                         'workhours': (stdunits * speed)/60,
                                         'km': lug_km,
                                         'kg_raw': he_pc_allocated,
                                         'kg': kg_nett,
                                         'stdunits': kg_nett/variables.stdunit}})

                cdic_fitness['kg'] =  cdic_fitness['kg'] + kg_nett
                cdic_fitness['km'] =  cdic_fitness['km'] + lug_km
                cdic_fitness['stdunits'] =  cdic_fitness['stdunits'] + stdunits
                cdic_fitness['workhours'] =  cdic_fitness['workhours'] + ((stdunits * speed)/60)
                    
            else:
                note = 'no more lugs available in he'
                break
            
            
            cd_he.update({he:cd_he_lug})
            cd_he2.append(he)
    
    absolute_diff = absolute_diff + (abs(dic_dp[d]['kg_raw'] - kg))
    d_count = d_count + 1
    ddic_notes.update({d:note})
    cdic_chromosome.update({d:cd_he})
    clist_chromosome2.append(cd_he2)
    clist_chromosome2_d.append(d)
    cdic_chromosome2.update({'clist_chromosome2':clist_chromosome2,
                             'clist_chromosome2_d':clist_chromosome2_d})
    
cdic_fitness['obj1'] = absolute_diff
cdic_fitness['obj2'] =  (cdic_fitness['workhours'] * variables.zar_workhour)
                        
ddic_solution_2.update({solution_num: {'ddic_solution':ddic_solution,
                                  'ddic_notes':ddic_notes,
                                  'cdic_chromosome':cdic_chromosome,
                                  'cdic_chromosome2':cdic_chromosome2,                                      
                                  'cdic_fitness':cdic_fitness}})

ddf_solution = pd.DataFrame.from_dict(ddic_solution, orient='index')
ddf_solution['solution_num'] = solution_num
ddf_solution['s_datetime'] = datetime.datetime.now()



end_ind = datetime.datetime.now()
print('time to create 1 ind: ' + str(end_ind - start_ind))