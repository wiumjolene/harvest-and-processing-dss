import os
import sys
from pymoo.problems import get_problem
from pymoo.indicators.hv import HV
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
import numpy as np
import datetime

from src.features.build_features import ParetoFeatures

pt = ParetoFeatures()

base_path = os.path.join(r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\external","20220909","zdt2",'nsga2')

ref_point = np.array([1.2, 1.2])
ind = HV(ref_point=ref_point)
hypervolume = pd.DataFrame()


# The pareto front of a scaled zdt1 problem
pf = get_problem("zdt2").pareto_front()
pareto = pd.DataFrame(pf, columns=['obj1','obj2'])
pareto['population'] ='pareto'
pareto['id'] = pareto.index
pareto=pareto[['obj1','obj2']]
pareto = pareto.to_numpy()


dir_list = os.listdir(base_path)
for i, file in enumerate(dir_list):
    if file[:7] == 'fitness':
        path = os.path.join(base_path, file)

        fitness_df = pd.read_excel(path)
        fitness_df = fitness_df[fitness_df['population'] == 'yes']

        fitness_df=fitness_df[['obj1','obj2']]
        A = fitness_df.to_numpy()
        hyperv = pd.DataFrame([[ind(A),i,'yes']],columns=['hyperarea', 'sample', 'population'])
        phyperv = pd.DataFrame([[ind(pareto),i,'pareto']],columns=['hyperarea', 'sample', 'population'])

        hypervolume=pd.concat([hypervolume, hyperv, phyperv])

hypervolume.to_excel(os.path.join(base_path,f"hypervolume_nsga2.xlsx"))    


