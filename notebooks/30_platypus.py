import numpy as np # for multi-dimensional containers
import pandas as pd # for DataFrames
import plotly.graph_objects as go # for data visualisation
import platypus as plat # multi-objective optimisation framework
import plotly.express as px


import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
import numpy as np
import datetime

from src.features.build_features import ParetoFeatures
from src.utils import config
from src.features.make_tests import Tests

t=Tests()


def result(i):
    test_name = 'zdt1'

    problem = plat.ZDT1()
    algorithm = plat.NSGAII(problem)
    algorithm.run(15000)

    objective_values = np.empty((0, 2))
    for solution in algorithm.result:
        y = solution.objectives
        objective_values = np.vstack([objective_values, y])
        objective_values = pd.DataFrame(objective_values, columns=['obj1','obj2'])

    objective_values['population'] = 'yes'
    objective_values['id'] = objective_values.index
    print(objective_values)


    max_id = objective_values['id'].max()
    for pp in range(config.POPUATION):
        x = np.random.rand(config.D)
        pareto_indivst=pd.DataFrame(data=x,columns=['value'])
        pareto_indivst['time_id']=pareto_indivst.index
        pareto_indivst['id']=max_id + pp

        # Choose which test to use
        if test_name == 'zdt1':
            fitness = t.ZDT1_pareto(x)

        if test_name == 'zdt2':
            fitness = t.ZDT2_pareto(x)

        if test_name == 'zdt3':
            fitness = t.ZDT3_pareto(x)

        pareto = pd.DataFrame(fitness, columns=['obj1', 'obj2'])
        pareto['population'] = 'pareto'
        pareto['id'] = max_id + pp

        objective_values=objective_values.append(pareto).reset_index(drop=True)

    pt = ParetoFeatures()
    hyperareas = pt.calculate_hyperarea(objective_values)
    hyperareas['sample'] = i
    print(hyperareas)
    return hyperareas


all_hyperareas = pd.DataFrame()
for i in range(30):
    hyperarea = result(i)

    all_hyperareas = pd.concat([all_hyperareas,hyperarea])

all_hyperareas.to_excel('hyperareas2.xlsx')