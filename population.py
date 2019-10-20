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

chromosome_len = len(pdic_solution[parent1]['cdic_chromosome2']['clist_chromosome2_d'])
crossover_point = int(round(0.3 * chromosome_len,0))
