##############################################################################
##############################################################################
#                                      MOGA
# Definition: New fitness sharing approach for multi-objective GA's
# Kim, Hyoungjin
##############################################################################
##############################################################################
import pandas as pd
import math
import sys
import os
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from src.utils.visualize import Visualize
from src.utils import config
from src.models.run_tests import RunTests
from src.features import build_features 

graph = Visualize()
rt = RunTests()

# TODO: dynamically calc sshare
sshare = 1/(math.sqrt(config.POPUATION)-1)

p = r'C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\fitness_df.xlsx'
fitness_df = pd.read_excel(p)

#test_name = 'zdt1'
#alg = 'moga'
#alg_path = f"{test_name}/{alg}"

#fitness_df = rt.population(0, config.POPUATION, alg_path, test_name)

fitness_df['population'] = 'yes'
#fitness_df.to_excel('fitness_df.xlsx')

fitness_df = fitness_df[fitness_df['population'] != 'none'].reset_index(drop=True)
#fitness_df= fitness_df.sort_values(by=['obj1','obj2']).reset_index(drop=True)

##############################################################################
# 1. Assign rank based on non-dominated
#    - rank(indiv, generation) = 1 + number of indivs that dominate indiv
##############################################################################
dominating_fits = defaultdict(int)  # n (The number of people that dominate you)
dominated_fits = defaultdict(list)  # Sp (The people you dominate)
fits = list(fitness_df.id)
fitness_df=fitness_df.set_index('id')
fitness_df['id'] = fitness_df.index
fitness_df['domcount'] = 0

for i, id in enumerate(fits):
    obj1 = fitness_df.at[id, 'obj1']
    obj2 = fitness_df.at[id, 'obj2']

    #for j in range(len(fitness_df)):
    for idx in fits[i + 1:]:
        obj1x = fitness_df.at[idx, 'obj1']
        obj2x = fitness_df.at[idx, 'obj2']

        objset1 = (obj1, obj2)
        objset2 = (obj1x, obj2x)
        
        if build_features.GeneticAlgorithmGenetics.dominates(objset1, objset2):
        #if (obj1 <= obj1x and obj2 <= obj2x) and (obj1 < obj1x or obj2 < obj2x):
            dominating_fits[idx] += 1 
            fitness_df.at[idx, 'domcount'] += 1
            dominated_fits[id].append(idx) 

        elif build_features.GeneticAlgorithmGenetics.dominates(objset2, objset1):  
        #if (obj1x <= obj1 and obj2x <= obj2) and (obj1x < obj1 or obj2x < obj2):
            dominating_fits[id] += 1
            fitness_df.at[id, 'domcount'] += 1
            dominated_fits[idx].append(id)    

fitness_df['rank'] = fitness_df['domcount'] + 1
fitness_df.to_excel('check1.xlsx')
print('yes')

##############################################################################
# 2. PARETO RANKING
##############################################################################
fitness_df=fitness_df.sort_values(by=['rank']).reset_index(drop=True)
ranks = fitness_df['rank'].unique()
N = len(fitness_df)

for r in ranks:
    solk = len(fitness_df[fitness_df['rank']==r]) - 1
    nk = len(fitness_df[fitness_df['rank'] <= (r-1)])
    fitness_df.loc[(fitness_df['rank']==r), 'solk'] = solk
    fitness_df.loc[(fitness_df['rank']==r), 'nk'] = nk
    
fitness_df['fitness'] = N - fitness_df['nk'] - (fitness_df['solk'] * 0.5)
fitness_df.to_excel('check2.xlsx')
##############################################################################
# 3. STANDARD FITNESS SHARE
##############################################################################
# 3.1 Normalised distance between any two indivs in same rank

obj1_min=fitness_df.obj1.min()
obj1_max=fitness_df.obj1.max()
obj2_min=fitness_df.obj2.min()
obj2_max=fitness_df.obj2.max()

for r in ranks:
    df=fitness_df[fitness_df['rank']==r].reset_index(drop=True)
    for i in range(len(df)):
        id_i = df.id[i]
        obj1_i = df.obj1[i]
        obj2_i = df.obj2[i]
        nc=0
        for j in range(len(df)):
            id_j = df.id[j]
            obj1_j = df.obj1[j]
            obj2_j = df.obj2[j]

            obj1_dij = ((obj1_i-obj1_j)/(obj1_max-obj1_min))**2    
            obj2_dij = ((obj2_i-obj2_j)/(obj2_max-obj2_min))**2

            dij = math.sqrt(obj1_dij+obj2_dij)

# 3.2 The standard sharing function suggested by Goldberg and Richardson
#       with a normalized niche radius σshare

            if dij < sshare:
                shdij = 1-(dij/sshare)

            else: 
                shdij = 0

# 3.3 Niche count is calculated by indiv by summing up sharing 
#       by indivs with same rank
            
            nc=nc+shdij

        fitness_df.loc[(fitness_df['id']==id_i), 'nc'] = nc

# 3.4 Finally, the assigned fitness is reduced by dividing the fitness Fi given 
#       in step 2 by the niche count as follows
fitness_df['fitness2']=fitness_df['fitness']/fitness_df['nc']
fitness_df.to_excel('check3.xlsx')

fitness_df = fitness_df.sort_values(by=['fitness2'], ascending=[False]).reset_index(drop=True)
fitness_df.loc[(fitness_df.index<=config.POPUATION),'population']='yes'
fitness_df.loc[(fitness_df.index>config.POPUATION),'population']='none'

fitness_df.to_excel('check4.xlsx')
graph.scatter_plot2(fitness_df,'moga.html','population','title')


# TODO: implement into new GA with mating and cross over
# TODO: create dymanic sigma_share