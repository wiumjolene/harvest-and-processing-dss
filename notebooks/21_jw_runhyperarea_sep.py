import pandas as pd
import sys
import os
import random
import numpy as np


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.features.build_features import ParetoFeatures
from src.models.run_tests import StatsTests
from src.utils import config

base = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1"
test = 'zdt1'
alg = 'nsga2'

pt = ParetoFeatures()

pareto = pd.read_excel(os.path.join(base,f"fitness_nsga2_{0}.xlsx"))
pareto = pareto[pareto['population'] == 'pareto']

hyperarea = pd.DataFrame()
all = pd.DataFrame()
for s in range(0,1):
    fitness_df = pd.read_excel(os.path.join(base,f"fitness_nsga2_{s}.xlsx"))
    fitness_df = fitness_df[fitness_df['population'] == 'yes']
    fitness_df = fitness_df.drop_duplicates(['obj1', 'obj2'], keep='first').reset_index(drop=True)

    fitness_df = pd.concat([pareto, fitness_df]).reset_index(drop=True)
    fitness_df['sample'] = s
    fitness_df['sample_id'] = fitness_df['sample'].astype(str) + "-" + fitness_df['id'].astype(str)

    hyperareat = pt.calculate_hyperarea(fitness_df)
    hyperareat['sample'] = s
    
    hyperarea=pd.concat([hyperarea, hyperareat]).reset_index(drop=True)
    all=pd.concat([all, fitness_df]).reset_index(drop=True)

#hyperarea = hyperarea.pivot(index="sample", columns="population", values="hyperarea")
hyperarea.to_excel(os.path.join(base,f"hyperarea_{alg}_NEW.xlsx"), index=False)
all.to_excel(os.path.join(base,f"all_fitness_{alg}.xlsx"), index=False)


stats = StatsTests()
stats.run_friedman(hyperarea, alg, test)



