import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
import numpy as np
import datetime

from src.features.build_features import Population
from src.utils.visualize import Visualize
from src.utils import config

print(datetime.datetime.now())

path = r'C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\fitness_nsga22.xlsx'
fitness_df = pd.read_excel(path)
fitness_df=fitness_df[fitness_df['population']=='yes'].reset_index(drop=True)

graph = Visualize()
#pop = Population()


fitness_df['population'] = 'none'
domination = {}
front = []


def crowding_distance(fitness_df, fc, size):
    """ Crowding distance sorting """ 
    #self.logger.info(f"-- crowding distance activated")

    fitness_dff = fitness_df[fitness_df['front']==fc].reset_index(drop=True)

    if fc==1:
        space = config.POPUATION
    else:
        space = config.POPUATION - size

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

                fitness_df.loc[(fitness_df['id']==id),'cdist']=fitness_df['cdist']+distance

    fitness_df = fitness_df.sort_values(by=['cdist'], ascending=False).reset_index(drop=True)
    fitness_df.loc[(fitness_df.index < space),'population']='yes'
    return fitness_df

""" Decide if new child is worthy of pareto membership 
Deb 2002
"""
#self.logger.info(f"- getting fitness")
fitness_df=fitness_df.groupby(['obj1','obj2'])['id'].min().reset_index(drop=False)

fitness_df['population'] = 'none'
domination = {}
front = []
# Initiate domination count and dominated by list
#self.logger.info(f"-- getting domcount")
for i in range(len(fitness_df)):
    id = fitness_df.id[i]
    obj1 = fitness_df.obj1[i]
    obj2 = fitness_df.obj2[i]
    domcount = 0  # number of sols that dominate cur sol
    domset = []  # set of sols cursol dominates

    for j in range(len(fitness_df)):
        idx = fitness_df.id[j]

        if idx != id:
            obj1x = fitness_df.obj1[j]
            obj2x = fitness_df.obj2[j]      

            # Calculate # of solutions that dominate obj
            if (obj1x<=obj1 and obj2x<=obj2) and (obj1x<obj1 or obj2x<obj2):
                domcount = domcount + 1
            
            # Get set of solutions that solution dominates
            if (obj1 <= obj1x and obj2 <= obj2x) and (obj1 < obj1x or obj2 < obj2x):
                domset.append(idx)

    domination.update({id:domset})
    fitness_df.loc[(fitness_df['id']==id), 'domcount'] = domcount

    if domcount == 0:  # if part of front 1
        fitness_df.loc[(fitness_df['id']==id), 'front'] = 1
        front.append(id)

###################################################
# Get front count and determine population status #
###################################################
#self.logger.info(f"-- getting front count")

# Size of selected solutions
size = len(fitness_df[fitness_df['front'] == 1])

# Check of set of sols in front 1 will fit into new population?
if size > config.POPUATION:
    fitness_df=crowding_distance(fitness_df, 1, size)

elif size == config.POPUATION:
    fitness_df.loc[(fitness_df['front']==1), 'population'] = 'yes'

# Else continue assigning fronts to solutions
else:
    fitness_df.loc[(fitness_df['front']==1), 'population'] = 'yes'
    fc=2
    while len(front) > 0:
        q1= []  # Solutions in new front

        for p in front:
            for q in domination[p]:
                dc = fitness_df['domcount'][fitness_df['id'] == q].iloc[0]
                dc = dc - 1
                fitness_df.loc[(fitness_df['id']==q), 'domcount'] = dc

                if dc == 0:
                    q1.append(q)
                    fitness_df.loc[(fitness_df['id']==q), 'front'] = fc

        # Only for as many fronts as needed to fill popsize
        if size + len(front) > config.POPUATION:
            fitness_df=crowding_distance(fitness_df, fc, size)
            break
        elif size + len(front) == config.POPUATION:
            fitness_df.loc[(fitness_df['front']==fc), 'population'] = 'yes'
            break
        else:
            fitness_df.loc[(fitness_df['front']==fc), 'population'] = 'yes'

        fc = fc + 1
        front = q1
        size = size + len(front)

fitness_df['front'] = fitness_df['front'].fillna(-99)
fitness_df=fitness_df[fitness_df['population']=='yes'].reset_index(drop=True)
#fitness_df=fitness_df.drop(columns=['cdist', 'domcount'])
#fitness_df = fitness_df[fitness_df['population'] == 'yes'].reset_index(drop=True)