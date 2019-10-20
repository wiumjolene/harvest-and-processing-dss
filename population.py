# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 11:00:30 2019

@author: Jolene
"""

import solution
import pandas as pd

population_size = 5

ddf_solution_p = pd.DataFrame({})
ddic_solution_a = {}
for p in range(0,population_size):
    print('-----------------------------')
    print('Generating solution ' + str(p))
    ddic_solution = solution.chromosome(solution_num = p)
    ddic_solution_a.update(ddic_solution)
    ddic_solution_p = ddic_solution[p]['ddic_solution']
    ddf_solution = pd.DataFrame.from_dict(ddic_solution_p, orient='index')
    ddf_solution['solution_num'] = p
    ddf_solution_p = ddf_solution_p.append(ddf_solution)
    
ddf_solution_p_result = ddf_solution_p.groupby(['solution_num'])['stdunits','km'].sum().reset_index()
print('Results: ')
print(ddf_solution_p_result)

ddf_solution_p.to_csv(r'output_data/solution.csv',index = False)
