# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 11:00:30 2019

@author: Jolene
"""

import solution
import pandas as pd
import random

population_size = 5

pdic_solution = {}
for p in range(population_size):
    print('-----------------------------')
    print('Generating solution ' + str(p))
    cdic_solution = solution.chromosome(solution_num = p)
    pdic_solution.update(cdic_solution)


parent1 = random.randint(0,population_size)
parent2 = random.randint(0,population_size)

chrom_order = pdic_solution[parent1]['cdic_chromosome2']['clist_chromosome2_d']
chrom_len = len(chrom_order)
xover_point = int(round(0.3 * chrom_len,0))


parent1_he = pdic_solution[parent1]['cdic_chromosome2']['clist_chromosome2']
parent2_he = pdic_solution[parent2]['cdic_chromosome2']['clist_chromosome2']


child1_he = parent1_he[0:xover_point] + parent2_he[xover_point:chrom_len]
child2_he = parent2_he[0:xover_point] + parent1_he[xover_point:chrom_len]

dic_child1 = solution.chromosome(solution_num=0,
                                  demand_list=chrom_order,
                                  he_list=child1_he)

dic_child2 = solution.chromosome(solution_num=0,
                                  demand_list=chrom_order,
                                  he_list=child2_he)

child1_fitness = dic_child1[0]['cdic_fitness']['km']
child2_fitness = dic_child2[0]['cdic_fitness']['km']
