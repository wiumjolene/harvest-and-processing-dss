# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 14:45:09 2019

@author: Jolene
"""

import pandas as pd
import variables
import individual as ind
import allocate as gaf
import random
import copy


def allocate_pc(dic_pc,df_ftt,ddic_metadata):
    df_pc = pd.DataFrame.from_dict(dic_pc, orient='index')
    df_pct = df_pc.merge(df_ftt, on = 'packhouse_id')  # get distance from block
    df_pct = df_pct[df_pct['time_id'] == ddic_metadata['time_id']]
    df_pct = df_pct[df_pct['km'] < variables.travel_restriction]
    df_pct = df_pct[df_pct['pack_type_id'] == ddic_metadata['pack_type_id']]
    df_pct = df_pct[df_pct['kg_remain'] >= variables.s_unit]
    df_pctf = df_pct.sort_values(['km']).reset_index(drop=True)
    return(df_pctf)
    
    
def tournament_select(tour_size, pdic_solution):
    highest_fitness = 0
    list_options = list(pdic_solution.keys())
    
    for i in range(tour_size):
        
        option_num = random.randint(0,len(list_options)-1)
        option = list_options[option_num]
        option_fitness = pdic_solution[option]['cdic_fitness']['km']
            
        if option_fitness > highest_fitness:
            highest_fitness == option_fitness
            parent = option
            
    if highest_fitness == 0:
        parent = option
            
    return(parent)

########################################
    # cross over functionality #
########################################
def cross_over(pdic_solution, chrom_order, df_dp_im, df_ft_im, df_he_im, 
               dic_pc, dic_pc2, demand_options_x):
    
    chrom_len = len(chrom_order)
    xover_point = random.randint(0,chrom_len-1)
    
    # select parents with tournament
    parent1 = gaf.tournament_select(3,pdic_solution)
    parent2 = gaf.tournament_select(3,pdic_solution)
    
    # get encoding for two parents
    parent1_he = pdic_solution[parent1]['cdic_chromosome2']['clist_chromosome2']
    parent2_he = pdic_solution[parent2]['cdic_chromosome2']['clist_chromosome2']
    
    # crossover to create children
    child1_he = parent1_he[0:xover_point] + parent2_he[xover_point:chrom_len]
    child2_he = parent2_he[0:xover_point] + parent1_he[xover_point:chrom_len]
    
    # create solution for each child
    child1_dic = ind.individual(solution_num = 0,
                                      demand_list = chrom_order,
                                      df_dp = df_dp_im,
                                      df_ft = df_ft_im,
                                      df_he = df_he_im,
                                      dic_pc = dic_pc,
                                      he_list = child1_he,
                                      demand_options = copy.deepcopy(demand_options_x))
    
    child2_dic = ind.individual(solution_num = 0, 
                                      demand_list = chrom_order,
                                      df_dp = df_dp_im,
                                      df_ft = df_ft_im,
                                      df_he = df_he_im,
                                      dic_pc = dic_pc2,
                                      he_list = child2_he,
                                      demand_options = copy.deepcopy(demand_options_x))
    
    xover_result = [child1_dic,child2_dic]

    return(xover_result)

########################################
    # mutation functionality #
    ## mutatuion of child
########################################
def mutation(mutate_individual, id_num, demand_options_m, df_dp_im, df_ft_im, 
             df_he_im, dic_pc):
    print('---- mutation ----')
    demand_options = copy.deepcopy(demand_options_m)
    mutation_he = mutate_individual[id_num]['cdic_chromosome2']['clist_chromosome2']
    chrom_order = mutate_individual[id_num]['cdic_chromosome2']['clist_chromosome2_d']
    chrom_len = len(chrom_order)
    #set a mutation point
#    mut_point = random.randint(0,len(chrom_order)-1)
    mut_point = int(round(0.8 * chrom_len,0))
    mut_d = chrom_order[mut_point]
    mut_current = mutation_he[mut_point][0]
    ddic_he = demand_options['demands_he'][mut_d]
    dlist_he = list(ddic_he.keys())
    dlist_he.remove(mut_current)
    hepos = random.randint(0,len(dlist_he)-1)
    he = dlist_he[hepos]
    mutation_he[mut_point][0] = he
    # create individual with new gene in encoding
    mut_dic = ind.individual(solution_num = 0,
                                      demand_list = chrom_order,
                                      df_dp = df_dp_im,
                                      df_ft = df_ft_im,
                                      df_he = df_he_im,
                                      dic_pc = dic_pc,
                                      demand_options = demand_options,
                                      he_list = mutation_he)
    
    return(mut_dic)