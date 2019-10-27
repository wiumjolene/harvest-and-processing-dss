# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 11:00:30 2019

@author: Jolene
"""

import individual as ind
import feasible_options as fo
import variables
import allocate
import pandas as pd
import random

demand_options = fo.create_options()

pdic_solution = {}
p_fitness = {}
for p in range(variables.population_size):
    print('Generating individual ' + str(p))
    cdic_solution = ind.individual(solution_num = p)
    pdic_solution.update(cdic_solution)
    # update fitness tracker
    p_fitness.update({p:cdic_solution[p]['cdic_fitness']['km']})

id_num = variables.population_size
chrom_order = pdic_solution[0]['cdic_chromosome2']['clist_chromosome2_d']

for g in range(variables.generations):
    # create a random to determine if mutation should happen
    mutation_random = random.randint(0,100)/100
    
    # create new child 1
    child1_nb = {id_num: allocate.cross_over(pdic_solution,chrom_order)[0][0]}
    
    # mutate if generation meets mutation criteria
    if mutation_random <= variables.mutation_rate:
        child1_m = allocate.mutation(child1_nb,id_num, demand_options)
        child1 = {id_num: child1_m[0]}
        
    else:
        child1 = child1_nb

    pdic_solution.update(child1)
    p_fitness.update({id_num:child1[id_num]['cdic_fitness']['km']})
    id_num = id_num + 1

    # create new child 2
    child2 = {id_num: allocate.cross_over(pdic_solution,chrom_order)[1][0]}
    pdic_solution.update(child2)
    p_fitness.update({id_num:child2[id_num]['cdic_fitness']['km']})
    id_num = id_num + 1
    
    # find weakest individuals
    p_fitness_df = pd.DataFrame.from_dict(p_fitness, orient='index')
    p_fitness_df = p_fitness_df.sort_values(by=[0],ascending=False)
    
    drop_id1 = p_fitness_df.index[0]
    drop_id2 = p_fitness_df.index[1]
    
    # remove weakest individuals
    del p_fitness[drop_id1]
    del p_fitness[drop_id2]    
    del pdic_solution[drop_id1]
    del pdic_solution[drop_id2]    
        
    # best fitness
    best_indi = p_fitness_df.index[(len(p_fitness_df) - 1)]
    best_fitness = pdic_solution[best_indi]['cdic_fitness']['km']
    print(best_fitness)

    
