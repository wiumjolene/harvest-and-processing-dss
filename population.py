# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 11:00:30 2019

@author: Jolene
"""
import random
import copy

import pandas as pd
import matplotlib.pyplot as plt

import individual as ind
import feasible_options as fo
import variables
import allocate
import source_etl as setl


demand_options_im = fo.create_options()
df_dp_im = setl.demand_plan()
df_ft_im = setl.from_to()
df_he_im = setl.harvest_estimate()
dic_pc_im = setl.pack_capacity_dic()

pdic_solution = {}
p_fitness = {}
for p in range(variables.population_size):
    print('Generating individual ' + str(p))
    # make deep copies of dictionaries so as not to update main
    dic_pc_p = copy.deepcopy(dic_pc_im)
    demand_options_p = copy.deepcopy(demand_options_im)
    
    # create individual
    cdic_solution = ind.individual(solution_num = p,
                                   df_dp = df_dp_im,
                                   df_ft = df_ft_im,
                                   df_he = df_he_im,
                                   dic_pc = dic_pc_p,
                                   demand_options = demand_options_p)
    
    # add individual to population
    pdic_solution.update(cdic_solution)
    
    # update fitness tracker
    p_fitness.update({p:cdic_solution[p]['cdic_fitness']['km']})

id_num = variables.population_size
chrom_order = pdic_solution[0]['cdic_chromosome2']['clist_chromosome2_d']

fitness_tracker = {}
for g in range(variables.generations):
    # make deep copies of dictionaries so as not to update main
    dic_pc_g = copy.deepcopy(dic_pc_im)
    dic_pc_g2 = copy.deepcopy(dic_pc_im)
    dic_pc_g3 = copy.deepcopy(dic_pc_im)
    demand_options_g = copy.deepcopy(demand_options_im)
    
    # create a random to determine if mutation should happen
    mutation_random = random.randint(0,100)/100
    
    # create new child 1
    child1_nb_gen = allocate.cross_over(pdic_solution, chrom_order,
                                        df_dp_im = df_dp_im,
                                        df_ft_im = df_ft_im,
                                        df_he_im = df_he_im,
                                        dic_pc = dic_pc_g,
                                        dic_pc2 = dic_pc_g2,
                                        demand_options_x = copy.deepcopy(demand_options_im))
    
    child1_nb = {id_num: child1_nb_gen[0][0]}
    
    # mutate if generation meets mutation criteria
    if mutation_random <= variables.mutation_rate:
        child1_m = allocate.mutation(child1_nb, id_num, 
                                     demand_options_m = copy.deepcopy(demand_options_im),
                                     df_dp_im = df_dp_im,
                                     df_ft_im = df_ft_im,
                                     df_he_im = df_he_im,
                                     dic_pc = dic_pc_g3)
        
        child1 = child1_m
        
    else:
        child1 = child1_nb

    pdic_solution.update(child1)
    p_fitness.update({id_num:child1[id_num]['cdic_fitness']['km']})
    id_num = id_num + 1

    # create new child 2
    child2 = {id_num: child1_nb_gen[1][0]}
    pdic_solution.update(child2)
    p_fitness.update({id_num:child2[id_num]['cdic_fitness']['km']})
    id_num = id_num + 1
    
    # find weakest individuals
    p_fitness_df = pd.DataFrame.from_dict(p_fitness, orient='index')
    p_fitness_df = p_fitness_df.sort_values(by=[0],ascending=False)
    
    drop_id1 = p_fitness_df.index[0]
    drop_id2 = p_fitness_df.index[1]
        
    # best fitness
    best_indi = p_fitness_df.index[(len(p_fitness_df) - 1)]
    best_fitness = pdic_solution[best_indi]['cdic_fitness']['km']
    worst_fitness = pdic_solution[drop_id1]['cdic_fitness']['km']
    print('generation ' + str(g)
            + ': best ' + str(best_fitness) 
            + ' - worst ' +  str(worst_fitness))
    
    # remove weakest individuals
    del p_fitness[drop_id1]
    del p_fitness[drop_id2]    
    del pdic_solution[drop_id1]
    del pdic_solution[drop_id2]    

    fitness_tracker.update({g: [best_fitness, worst_fitness]})

fitness_tracker_df = pd.DataFrame.from_dict(fitness_tracker, orient='index') 
fitness_tracker_df = fitness_tracker_df.reset_index()
fitness_tracker_df = fitness_tracker_df.rename(columns={"index": "generation",
                                                           0: "best fitness",
                                                           1: "worst fitness"})

fitness_tracker_df.plot(kind = 'scatter', x = 'generation', y = 'best fitness', 
                        color='green',figsize=(8,6),fontsize = 14)
plt.title('best fitness')
plt.show()

fitness_tracker_df.plot(kind = 'scatter', x = 'generation', y = 'worst fitness', 
                        color='red',figsize=(10,8),fontsize = 14)
plt.title('worst fitness')
plt.show()

best_solution = pdic_solution[best_indi]['ddic_solution']
best_solution_df = pd.DataFrame.from_dict(best_solution, orient='index')
best_solution_df['solution_num'] = best_indi
best_solution_df.to_csv(r'output_data/solution.csv',index = False)
