# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 11:00:30 2019

@author: Jolene
"""

import solution
import pandas as pd
import json

population_size = 5

ddf_solution_p = pd.DataFrame({})
ddic_solution_p = {}
for p in range(0,population_size):
    print('-----------------------------')
    print('Generation solution ' + str(p))
    ddic_solution_2 = solution.population(solution_num = p)
    ddic_solution_p.update(ddic_solution_2)
    ddf_solution_p_result = pd.DataFrame.from_dict(ddic_solution_2[p]['ddic_solution'], orient='index')
    ddf_solution_p_result['solution_num'] = p
    ddf_solution_p = ddf_solution_p.append(ddf_solution_p_result)
    

ddf_solution_p_result = ddf_solution_p.groupby(['solution_num'])['stdunits','km'].sum().reset_index()


print('Results: ')
print(ddf_solution_p_result)



with open(r'output_data/solution.json', 'w') as f:
    json.dump(ddic_solution_p, f)

