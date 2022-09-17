import os
import sys
from pymoo.problems import get_problem
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
import numpy as np
import datetime

from src.features.build_features import ParetoFeatures

pt = ParetoFeatures()

base_path = os.path.join(r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\external","20220909","zdt2",'nsga2')

huperarea = pd.DataFrame()
for i in range(0,6):
    path = os.path.join(base_path,f"fitness_nsga2_{i}.xlsx")

    fitness_df = pd.read_excel(path)
    fitness_df = fitness_df[fitness_df['population'] == 'yes']

    hyperareas = pt.calculate_hyperarea(fitness_df)
    hyperareas['sample'] = i
    huperarea=pd.concat([huperarea,hyperareas])

    pf = get_problem("zdt2").pareto_front()
    pareto = pd.DataFrame(pf, columns=['obj1','obj2'])
    pareto['population'] ='pareto'
    pareto['id'] = pareto.index

    hyperareas = pt.calculate_hyperarea(pareto)
    hyperareas['sample'] = i
    huperarea=pd.concat([huperarea,hyperareas])

huperarea.to_excel(os.path.join(base_path,f"hyperarea_nsga2.xlsx"))    


