# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 11:00:30 2019

@author: Jolene
"""

import solution
import pandas as pd

population_size = 5

ddf_solution_p = pd.DataFrame({})
for p in range(0,population_size):
    print('-----------------------------')
    print('Generation solution ' + str(p))
    ddf_solution = solution.population(solution_num = p)
    ddf_solution_p = ddf_solution_p.append(ddf_solution)
    

ddf_solution_p_result = ddf_solution_p.groupby(['solution_num'])['stdunits','km'].sum().reset_index()


print('Results: ')
print(ddf_solution_p_result)