# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 14:45:09 2019

@author: Jolene
"""

import random
import copy

import pandas as pd

import population as pop
#import individual as ind
import variables
#import allocate as gaf


def allocate_pc(dic_pc,df_ftt,ddic_metadata):
    df_pc = pd.DataFrame.from_dict(dic_pc, orient='index')
    df_pct = df_pc.merge(df_ftt, on = 'packhouse_id')  # get distance from block
    df_pct = df_pct[df_pct['time_id'] == ddic_metadata['time_id']]
    df_pct = df_pct[df_pct['km'] < variables.travel_restriction]
    df_pct = df_pct[df_pct['pack_type_id'] == ddic_metadata['pack_type_id']]
    df_pct = df_pct[df_pct['kg_remain'] >= variables.min_hepc]
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
               dic_pc, dic_pc2, dic_speed, demand_options_x):
    
    chrom_len = len(chrom_order)
    xover_point = random.randint(0,chrom_len-1)
    
    # select parents with tournament
    parent1 = tournament_select(3,pdic_solution)
    parent2 = tournament_select(3,pdic_solution)
    
    # get encoding for two parents
    parent1_he = pdic_solution[parent1]['cdic_chromosome2']['clist_chromosome2']
    parent2_he = pdic_solution[parent2]['cdic_chromosome2']['clist_chromosome2']
    
    # crossover to create children
    child1_he = parent1_he[0:xover_point] + parent2_he[xover_point:chrom_len]
    child2_he = parent2_he[0:xover_point] + parent1_he[xover_point:chrom_len]
    
    # create solution for each child
    child1_dic = pop.individual(solution_num = 0,
                                      demand_list = chrom_order,
                                      df_dp = df_dp_im,
                                      df_ft = df_ft_im,
                                      df_he = df_he_im,
                                      dic_pc = dic_pc,
                                      he_list = child1_he,
                                      dic_speed = dic_speed,
                                      demand_options = copy.deepcopy(demand_options_x))
    
    child2_dic = pop.individual(solution_num = 0, 
                                      demand_list = chrom_order,
                                      df_dp = df_dp_im,
                                      df_ft = df_ft_im,
                                      df_he = df_he_im,
                                      dic_pc = dic_pc2,
                                      he_list = child2_he,
                                      dic_speed = dic_speed,
                                      demand_options = copy.deepcopy(demand_options_x))
    
    xover_result = [child1_dic,child2_dic]

    return(xover_result)

########################################
    # mutation functionality #
    ## mutatuion of child
########################################
def mutation(mutate_individual, id_num, demand_options_m, df_dp_im, df_ft_im, 
             df_he_im, dic_pc, dic_speed):
    # make deep copies of dictionaries so as not to update main
    demand_options = copy.deepcopy(demand_options_m)
    
    # get mutation individual chromosome and order
    mutation_he = mutate_individual[id_num]['cdic_chromosome2']['clist_chromosome2']
    chrom_order = mutate_individual[id_num]['cdic_chromosome2']['clist_chromosome2_d']
    chrom_len = len(chrom_order)
    
    #set a mutation point
    mut_point = random.randint(0, chrom_len - 1)
    mut_d = chrom_order[mut_point]  # get demand of mutation point
    try:
        mut_current = mutation_he[mut_point][0]  # current harvest estimate

        # get list of he for this demand
        ddic_he = demand_options['demands_he'][mut_d]
        dlist_he = list(ddic_he.keys())
        
        # remove current he from list
        dlist_he.remove(mut_current)  # remove so as not to select same he
        
        # if list is greater than 0, choose a new he
        if len(dlist_he) > 0:
            print('---- mutation ----')
            hepos = random.randint(0,len(dlist_he)-1)
            he = dlist_he[hepos]
    
            # update chromosome    
            mutation_he[mut_point][0] = he
         
            # create individual with new gene in encoding
            mut_dic = pop.individual(solution_num = id_num,
                                              demand_list = chrom_order,
                                              df_dp = df_dp_im,
                                              df_ft = df_ft_im,
                                              df_he = df_he_im,
                                              dic_pc = dic_pc,
                                              demand_options = demand_options,
                                              dic_speed = dic_speed,
                                              he_list = mutation_he)
    
        else:
            # if no he's in list, use old he
            print('---- mutation, but used old he due to no alternatives ----')
            he = mut_current
            mut_dic = mutate_individual

    except:
        print('---- mutation, but used old he due to no alternatives ----')
        mut_dic = mutate_individual
        
    return(mut_dic)