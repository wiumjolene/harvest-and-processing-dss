import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
import numpy as np
import datetime

from src.features.build_features import ParetoFeatures


path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1\fitness_nsga2.xlsx"
path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1\fitness_nsga2_real.xlsx"
path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\external\20220901\fitness_nsga2_0.xlsx"


huperarea = pd.DataFrame()
for i in range(0,9):
    path = os.path.join(r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\external","20220902",f"fitness_nsga2_{i}.xlsx")
    #path = f"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\external\20220901\fitness_nsga2_{i}.xlsx"
    fitness_df = pd.read_excel(path)
    pt = ParetoFeatures()
    hyperareas = pt.calculate_hyperarea(fitness_df)
    hyperareas['sample'] = i
    huperarea=pd.concat([huperarea,hyperareas])

huperarea.to_excel('hyperareas.xlsx')    
    