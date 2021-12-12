from collections import defaultdict
import pandas as pd


path=r'C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\check.xlsx'

fitness_df=pd.read_excel(path)

front = []
fitness_df = fitness_df.sort_values(by=['id']).reset_index(drop=True)

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
    obj1 = obj1s[i]
    obj2 = obj2s[i]

    for ix, idx in enumerate(fits[i + 1:]):
        obj1x = obj1s[i + ix + 1]
        obj2x = obj2s[i + ix + 1]
        
        #if build_features.GeneticAlgorithmGenetics.dominates((obj1, obj2), (obj1x, obj2x)):
        #if ((obj1 <= obj1x and obj2 <= obj2x) and (obj1 < obj1x or obj2 < obj2x)):
        if (obj1 <= obj1x and obj2 < obj2x):
            dominating_fits[i + ix + 1] += 1 
            dominated_fits[id].append(idx) 

        #if build_features.GeneticAlgorithmGenetics.dominates((obj1x, obj2x), (obj1, obj2)):
        #if ((obj1 >= obj1x and obj2 >= obj2x) and (obj1 > obj1x or obj2 > obj2x)):
        if (obj1 >= obj1x and obj2 > obj2x):
            dominating_fits[i] += 1
            dominated_fits[idx].append(id)    

    if dominating_fits[i] == 0:
        front.append(id)

fitness_df['domcount'] = dominating_fits
fitness_df.loc[(fitness_df.domcount==0), 'front'] = 1
fitness_df = fitness_df.sort_values(by=['domcount']).reset_index(drop=True)
print(fitness_df)

print(dominated_fits[idx])