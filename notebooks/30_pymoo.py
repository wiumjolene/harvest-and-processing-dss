import numpy as np
from pymoo.problems import get_problem
from pymoo.visualization.scatter import Scatter
from pymoo.indicators.hv import HV
import os
import pandas as pd
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.features.build_features import ParetoFeatures

# The pareto front of a scaled zdt1 problem
pf = get_problem("zdt2").pareto_front()

path = os.path.join(r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\external","20220907","zdt3",f"fitness_nsga2_1.xlsx")
df = pd.read_excel(path)
df=df[['obj1','obj2']]
A = df.to_numpy()
print(len(pf))

#Scatter(legend=True).add(pf, label="Pareto-front").show()

ref_point = np.array([1.2, 1.2])

ind = HV(ref_point=ref_point)
print("HV", ind(A))
print("HV", ind(pf))

huperarea = pd.DataFrame()
for i in range(0,30):
    path = os.path.join(r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\external","20220908","zdt2",f"fitness_nsga2_1.xlsx")

    pareto = pd.DataFrame(pf, columns=['obj1','obj2'])
    pareto['population'] ='pareto'
    pareto['id'] = pareto.index

    pt = ParetoFeatures()
    
    hyperareas = pt.calculate_hyperarea(pareto)
    hyperareas['sample'] = i
    huperarea=pd.concat([huperarea,hyperareas])

huperarea.to_excel(f"hyperarea_nsga2_2.xlsx")