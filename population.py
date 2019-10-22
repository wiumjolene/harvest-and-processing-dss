# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 11:00:30 2019

@author: Jolene
"""

import individual as ind
import pandas as pd
import random

population_size = 5

pdic_solution = {}
for p in range(population_size):
    print('-----------------------------')
    print('Generating solution ' + str(p))
    cdic_solution = ind.individual(solution_num = p)
    pdic_solution.update(cdic_solution)

# replace with tournament selection
parent1 = random.randint(0,population_size)
parent2 = random.randint(0,population_size)

chrom_order = pdic_solution[parent1]['cdic_chromosome2']['clist_chromosome2_d']
chrom_len = len(chrom_order)
xover_point = int(round(0.3 * chrom_len,0))

# get encoding for two parents
parent1_he = pdic_solution[parent1]['cdic_chromosome2']['clist_chromosome2']
parent2_he = pdic_solution[parent2]['cdic_chromosome2']['clist_chromosome2']

# crossover to create children
child1_he = parent1_he[0:xover_point] + parent2_he[xover_point:chrom_len]
child2_he = parent2_he[0:xover_point] + parent1_he[xover_point:chrom_len]

child1_dic = ind.individual(solution_num=0,
                                  demand_list=chrom_order,
                                  he_list=child1_he)

child2_dic = ind.individual(solution_num=0,
                                  demand_list=chrom_order,
                                  he_list=child2_he)

child1_fitness = child1_dic[0]['cdic_fitness']['km']
child2_fitness = child2_dic[0]['cdic_fitness']['km']

print(child1_fitness)
print(child2_fitness)
