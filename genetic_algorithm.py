# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 11:00:30 2019

@author: Jolene
"""
import random
import copy

import pandas as pd
import matplotlib.pyplot as plt
import json

import population as pop
import variables
import allocate
import source_etl as setl

df_dp_imgga = setl.demand_plan()
df_ft_imgga = setl.from_to()
df_he_imgga = setl.harvest_estimate()
dic_pc_imgga = setl.pack_capacity_dic()
df_pc_imgga = setl.pack_capacity()
df_lugs_imgga = setl.lug_generation()
demand_options_imgga = pop.create_options(df_dp_imgga, df_pc_imgga,
                                          df_he_imgga, df_lugs_imgga)


def genetic_algorithm(dic_solution, fitness, dic_pc_im, demand_options_im,
                      df_dp_im, df_ft_im, df_he_im, ga_num):
    pdic_solution = {}
    p_fitness = {}
          
    pdic_solution = copy.deepcopy(dic_solution)
    p_fitness = copy.deepcopy(fitness)
    id_num = max(list(pdic_solution.keys())) + 1
    chrom_order = pdic_solution[0]['cdic_chromosome2']['clist_chromosome2_d']
    
    for g in range(variables.generations):
        # make deep copies of dictionaries so as not to update main
        dic_pc_g = copy.deepcopy(dic_pc_im)
        dic_pc_g2 = copy.deepcopy(dic_pc_im)
        dic_pc_g3 = copy.deepcopy(dic_pc_im)
        demand_options_p = copy.deepcopy(demand_options_im)
        
        # create a random to determine if mutation should happen
        mutation_random = random.randint(0,100)/100
        
        # create new child 1
        child1_nb_gen = allocate.cross_over(pdic_solution, chrom_order,
                                            df_dp_im = df_dp_im,
                                            df_ft_im = df_ft_im,
                                            df_he_im = df_he_im,
                                            dic_pc = dic_pc_g,
                                            dic_pc2 = dic_pc_g2,
                                            demand_options_x = demand_options_p)
        
        child1_nb = {id_num: child1_nb_gen[0][0]}
        
        # mutate if generation meets mutation criteria
        if mutation_random <= variables.mutation_rate:
            child1_m = allocate.mutation(child1_nb, id_num, 
                                         demand_options_m = demand_options_p,
                                         df_dp_im = df_dp_im,
                                         df_ft_im = df_ft_im,
                                         df_he_im = df_he_im,
                                         dic_pc = dic_pc_g3)
            
            child1 = child1_m
            
        else:
            child1 = child1_nb
    
        pdic_solution.update(child1)
        p_fitness.update({id_num:[child1[id_num]['cdic_fitness']['obj1'],
                                  child1[id_num]['cdic_fitness']['obj2']]})
        id_num = id_num + 1
    
        # create new child 2
        child2 = {id_num: child1_nb_gen[1][0]}
        pdic_solution.update(child2)
        p_fitness.update({id_num:[child2[id_num]['cdic_fitness']['obj1'],
                                  child2[id_num]['cdic_fitness']['obj2']]})
        id_num = id_num + 1
        
        # get best kg
        p_fitness_df = pd.DataFrame.from_dict(p_fitness, orient='index')
        p_fitness_df['obj1_rank'] = p_fitness_df[0].rank(method='min')
        
        # find weakest individuals
        p_fitness_df = p_fitness_df.sort_values(by=[0],ascending=False)  # sort according to obj1_rank   
        drop_id1 = p_fitness_df.index[0]
        drop_id2 = p_fitness_df.index[1]
            
        # best fitness
        best_indi = p_fitness_df.index[(len(p_fitness_df) - 1)]
        best_obj1 = pdic_solution[best_indi]['cdic_fitness']['obj1']
        worst_obj1 = pdic_solution[drop_id1]['cdic_fitness']['obj1']
        best_obj2 = pdic_solution[best_indi]['cdic_fitness']['obj2']
        
        
        print('-generation ' + str(int(g))
                + ': best ' + str(int(best_obj1)) 
                + ' - worst ' +  str(int(worst_obj1))
                + ', kg: ' +  str(int(best_obj2)))
        
        # remove weakest individuals
        del p_fitness[drop_id1]
        del p_fitness[drop_id2]    
        del pdic_solution[drop_id1]
        del pdic_solution[drop_id2] 
    
        
    ga_dic = {ga_num: {'p_fitness':p_fitness,
                       'pdic_solution': pdic_solution}}
    return(ga_dic)        


ggapopulation = pop.population(demand_options_imgga, 
                              df_dp_imgga, 
                              df_ft_imgga, 
                              df_he_imgga, 
                              dic_pc_imgga)


ggd = genetic_algorithm(dic_solution = ggapopulation['pdic_solution'], 
                             fitness = ggapopulation['p_fitness'], 
                             dic_pc_im = dic_pc_imgga, 
                             demand_options_im = demand_options_imgga,
                             df_dp_im = df_dp_imgga, 
                             df_ft_im = df_ft_imgga, 
                             df_he_im = df_he_imgga, 
                             ga_num = 0)


best_solution = ggd[0]['pdic_solution'][max(ggd[0]['pdic_solution'])]['ddic_solution']
best_solution_df = pd.DataFrame.from_dict(best_solution, orient='index')
best_solution_df['solution_num'] = max(ggd[0]['pdic_solution'])
best_solution_df.to_csv(r'output_data/solution.csv',index = False)