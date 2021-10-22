import pandas as pd
import numpy as np
import time

path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1\fitness_nsga2_0.xlsx"
fitness_df = pd.read_excel(path)
fitness_df['cdist'] = 0
fitness_df['population'] = 'no'

size = 30
fc = 3
POPUATION= 34

start = time.time()


""" Crowding distance sorting """ 
#self.logger.debug(f"-- crowding distance activated")

fitness_dff = fitness_df[fitness_df['front']==fc].reset_index(drop=True)

# Evaluate how much space is available for the crowding distance
if fc==1:
    space = POPUATION

else:
    space = POPUATION - size

objs = ['obj1', 'obj2']
fitness_df['cdist'] = 0

for m in objs:
    # Sort by objective (m) 
    fitness_dff = fitness_dff.sort_values(by=m, ascending=True).reset_index(drop=True)
    vals = np.array(fitness_dff[m])
    ids = np.array(fitness_dff['id'])
    cdists = list(fitness_dff['cdist'])
    
    min = np.min(vals)
    max = np.max(vals)

    for i in range(len(ids)):

        if i == 0 or i == len(ids)-1:
            cdists[0] = np.inf
            cdists[-1] = np.inf

        else:
            oneup = vals[i-1]
            onedown = vals[i+1]
            distance = (onedown - oneup) / (max - min)

            cdists[i] = cdists[i] + distance

    fitness_dff['cdist'] = cdists
    print(fitness_dff)
    

fitness_dff = fitness_dff.sort_values(by=['cdist'], ascending=False).reset_index(drop=True)
fitness_dff.loc[(fitness_dff.index < space),'population']='yes'

fitness_df = fitness_df[fitness_df['front']!=fc].reset_index(drop=True)
fitness_df = pd.concat([fitness_df,fitness_dff]).reset_index(drop=True)

fitness_df = fitness_df.set_index('id')
fitness_df['id'] = fitness_df.index


end = time.time()
print(end - start)

