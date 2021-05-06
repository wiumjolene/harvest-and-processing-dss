import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
import numpy as np

from src.features.build_features import Population
from src.utils.visualize import Visualize
from src.utils import config

graph = Visualize()
pop = Population()

path = r'C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\fitness.xlsx'
fitness_df = pd.read_excel(path)
domination = {}
front = []

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

            if (obj1x <= obj1 and obj2x <= obj2) and (obj1x < obj1 or obj2x < obj2):
                domcount = domcount + 1
            else:
                domset.append(idx)

    domination.update({id:domset})

    fitness_df.loc[(fitness_df['id']==id), 'domcount'] = domcount

    if domcount == 0:
        fitness_df.loc[(fitness_df['id']==id), 'front'] = 1
        front.append(id)


fc=1
size = 0
while len(front) > 0:
    q1= []

    for p in front:
        sp = domination[p]
        #TODO: Only for as many fronts as needed to full popsize

        for q in domination[p]:
            dc = fitness_df['domcount'][fitness_df['id'] == q].iloc[0]
            dc = dc - 1
            fitness_df.loc[(fitness_df['id']==q), 'domcount'] = dc

            if dc == 0:
                q1.append(q)
                fitness_df.loc[(fitness_df['id']==q), 'front'] = fc+1
    
    fc = fc + 1
    front = q1
    size = size + len(front)



# Crowding distance sorting
nfront = fitness_df.front.unique()
fitness_dff = fitness_df[fitness_df['front']==3].reset_index(drop=True)

objs = ['obj1', 'obj2']
fitness_df['cdist'] = 0
for m in objs:
    df = fitness_dff.sort_values(by=m,ascending=False ).reset_index(drop=True)

    for i in range(len(fitness_dff)):
        id = fitness_dff.id[i]

        if i == 0 or i == len(fitness_dff)-1:
            fitness_df.loc[(fitness_df['id']==id),'cdist']= np.inf
        
        else:
            max = df[m][df.index == 0].iloc[0]
            min = df[m][df.index == len(fitness_dff) - 1].iloc[0]

            oneup = df[m][df.index == (i-1)].iloc[0]
            onedown = df[m][df.index == (i+1)].iloc[0]

            distance = (oneup - onedown) / (max - min)


            print(f"{i}-{oneup}-{onedown}")

            fitness_df.loc[(fitness_df['id']==id),'cdist']=fitness_df['cdist']+distance










# TODO: check this logic - it feels like it is evaluating too many q's
fitness_df['colour']=fitness_df['front'].astype(int).astype(str)
#graph.scatter_plot2(fitness_df, 'html.html')