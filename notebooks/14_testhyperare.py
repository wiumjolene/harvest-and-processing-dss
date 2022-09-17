import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
import numpy as np
import datetime

from src.features.build_features import ParetoFeatures

pt = ParetoFeatures()

test = 'zdt1'
folder = 'thesis'

base_path = os.path.join(r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\external", folder)

dir_list = os.listdir(os.path.join(base_path, test))

huperarea = pd.DataFrame()
for count, i in enumerate(dir_list):

    if i[:7] == 'fitness':
        path = os.path.join(base_path, test, i)
        fitness_df = pd.read_excel(path)
        
        hyperareas = pt.calculate_hyperarea(fitness_df)
        hyperareas['sample'] = count
        huperarea=pd.concat([huperarea,hyperareas])

huperarea.to_excel(os.path.join(base_path, f"hyperarea_{test}.xlsx"), index=False)    


