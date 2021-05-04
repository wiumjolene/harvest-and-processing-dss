import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd

from src.features.build_features import Population
from src.utils.visualize import Visualize
from src.utils import config

graph = Visualize()
p = Population()

p = r'C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\fitness.xlsx'
fitness_df = pd.read_excel(p)
domination = {}

for i in range(len(fitness_df)):
    id = fitness_df.id[i]
    obj1 = fitness_df.obj1[i]
    obj2 = fitness_df.obj2[i]
    domcount = 0
    domset = []

    for j in range(len(fitness_df)):
        idx = fitness_df.id[j]

        if idx != id:
            obj1x = fitness_df.obj1[j]
            obj2x = fitness_df.obj2[j]      

            if obj1x <= obj1 and obj2x <= obj2:
                domcount = domcount + 1

            else:
                domset.append(idx)

    domination.update({id:domset})

    fitness_df.loc[(fitness_df['id']==id), 'front'] = domcount



#graph.scatter_plot2(fitness_df, 'html.html')