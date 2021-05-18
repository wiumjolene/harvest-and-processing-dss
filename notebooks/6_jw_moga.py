##############################################################################
##############################################################################
#                                      MOGA
# Definition: New fitness sharing approach for multi-objective GA's
# Kim, Hyoungjin
##############################################################################
##############################################################################
import pandas as pd
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from src.utils.visualize import Visualize
from src.utils import config

graph = Visualize()

# TODO: dynamically calc sshare
sshare = 1/(math.sqrt(config.POPUATION)-1)

p = r'C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\fitness_vega.xlsx'
fitness_df = pd.read_excel(p)

fitness_df = fitness_df[fitness_df['population'] != 'none'].reset_index(drop=True)
fitness_df=fitness_df.groupby(['obj1','obj2'])['id'].min().reset_index(drop=False)
fitness_df= fitness_df.sort_values(by=['obj1','obj2']).reset_index(drop=True)

##############################################################################
# 1. Assign rank based on non-dominated
#    - rank(indiv, generation) = 1 + number of indivs that dominate indiv
##############################################################################
domination = {}
# Initiate domination count and dominated by list
for i in range(len(fitness_df)):
    id = fitness_df.id[i]
    obj1 = fitness_df.obj1[i]
    obj2 = fitness_df.obj2[i]
    domcount = 1  # number of sols that dominate cursol
    domset = []  # set of sols cursol dominates

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
    fitness_df.loc[(fitness_df['id']==id), 'rank'] = domcount
#graph.scatter_plot2(fitness_df,'moga.html','rank')

##############################################################################
# 2. PARETO RANKING
##############################################################################
fitness_df=fitness_df.sort_values(by=['rank']).reset_index(drop=True)
ranks = fitness_df['rank'].unique()
N = len(fitness_df)

for r in ranks:
    solk = len(fitness_df[fitness_df['rank']==r]) - 1
    nk = len(fitness_df[fitness_df['rank'] < r])
    fitness_df.loc[(fitness_df['rank']==r), 'solk'] = solk
    fitness_df.loc[(fitness_df['rank']==r), 'nk'] = nk
    
fitness_df['fitness'] = N - fitness_df['nk'] - (fitness_df['solk'] * 0.5)

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
fitness_df['fitness']=fitness_df['fitness']/fitness_df['nc']

fitness_df = fitness_df.sort_values(by=['fitness']).reset_index(drop=True)
fitness_df.loc[(fitness_df.index<=config.POPUATION),'population']='yes'
fitness_df.loc[(fitness_df.index>config.POPUATION),'population']='none'


graph.scatter_plot2(fitness_df,'moga.html','fitness2')


# TODO: implement into new GA with mating and cross over
# TODO: create dymanic sigma_share