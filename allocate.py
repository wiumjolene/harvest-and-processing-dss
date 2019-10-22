# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 14:45:09 2019

@author: Jolene
"""

import pandas as pd
import variables
import feasible_options as fo
import source_etl as setl
import random


def allocate_pc(dic_pc,df_ftt,ddic_metadata):
    df_pc = pd.DataFrame.from_dict(dic_pc, orient='index')
    df_pct = df_pc.merge(df_ftt, on = 'packhouse_id')  # get distance from block
    df_pct = df_pct[df_pct['time_id'] == ddic_metadata['time_id']]
    df_pct = df_pct[df_pct['km'] < variables.travel_restriction]
    df_pct = df_pct[df_pct['pack_type_id'] == ddic_metadata['pack_type_id']]
    df_pct = df_pct[df_pct['kg_remain'] >= variables.s_unit]
    df_pctf = df_pct.sort_values(['km']).reset_index(drop=True)
    return(df_pctf)
    
    
def tournament_select(tour_size,population_size,pdic_solution):
    highest_fitness = 0
    for i in range(0,tour_size):
        option = random.randint(0,(population_size-1))
        option_fitness = pdic_solution[option]['cdic_fitness']['km']
        if option_fitness > highest_fitness:
            highest_fitness == option_fitness
            parent = option
    return(parent)
