import logging
from collections import defaultdict
import pandas as pd
import time

path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1\fitness_nsga2_0.xlsx"
fitness_df = pd.read_excel(path)

fitness_df = fitness_df[fitness_df['population'] == 'yes']

fitness_df['population'] = 'none'
fitness_df['domcount'] = 0 


def one(fitness_df):
    front = []
    fits = list(fitness_df.id)

    fitness_df['population'] = 'none'
    fitness_df['domcount'] = 0 

    dominating_fits = [0] * len(fitness_df)  # n (The number of people that dominate you)
    dominated_fits = defaultdict(list)  # Sp (The people you dominate)
    fitness_df=fitness_df.set_index('id')
    fitness_df['id'] = fitness_df.index

    obj1s = fitness_df['obj1'].values
    obj2s = fitness_df['obj2'].values

    for i, id in enumerate(fits):

        for ix, idx in enumerate(fits[i + 1:]):
            
            if ((obj1s[i] <= obj1s[i + ix] and obj2s[i] <= obj2s[i + ix]) 
                and (obj1s[i] < obj1s[i + ix] or obj2s[i] < obj2s[i + ix])):
                
                dominating_fits[i + ix] += 1 
                dominated_fits[id].append(idx) 
    
            if ((obj1s[i] >= obj1s[i + ix] and obj2s[i] >= obj2s[i + ix]) 
                and (obj1s[i] > obj1s[i + ix] or obj2s[i] > obj2s[i + ix])):
                
                dominating_fits[i] += 1
                dominated_fits[idx].append(id)    

        if dominating_fits[i] == 0:
            front.append(id)

    fitness_df['domcount'] = dominating_fits
    fitness_df.loc[(fitness_df.domcount==0), 'front'] = 1
    return fitness_df


def two(fitness_df):
    fitness_df['domcount'] = 0
    front = []
    fits = list(fitness_df.id)

    fitness_df['population'] = 'none'
    fitness_df['domcount'] = 0 

    dominating_fits = defaultdict(int)  # n (The number of people that dominate you)
    dominated_fits = defaultdict(list)  # Sp (The people you dominate)
    fitness_df=fitness_df.set_index('id')
    fitness_df['id'] = fitness_df.index

    for i, id in enumerate(fits):
        obj1 = fitness_df.at[id, 'obj1']
        obj2 = fitness_df.at[id, 'obj2']

        for idx in fits[i + 1:]:
            obj1x = fitness_df.at[idx, 'obj1']
            obj2x = fitness_df.at[idx, 'obj2']
            
            if ((obj1 <= obj1x and obj2 <= obj2x) and (obj1 < obj1x or obj2 < obj2x)):
                dominating_fits[idx] += 1 
                fitness_df.at[idx, 'domcount'] += 1
                dominated_fits[id].append(idx) 
    
            if ((obj1 >= obj1x and obj2 >= obj2x) and (obj1 > obj1x or obj2 > obj2x)):
                dominating_fits[id] += 1
                fitness_df.at[id, 'domcount'] += 1
                dominated_fits[idx].append(id)    

        if dominating_fits[id] == 0:
            fitness_df.loc[(fitness_df.index==id), 'front'] = 1
            front.append(id)

    return fitness_df


number = 100

start = time.time()
for _ in range(number):
    fitness_df1 = one(fitness_df)

fitness_df1.to_excel('one.xlsx')

end = time.time()
print((end - start)/number)

start = time.time()
for _ in range(number):
    fitness_df2 = two(fitness_df)

fitness_df2.to_excel('two.xlsx')

end = time.time()
print((end - start)/number)