import pandas as pd
import platypus as plat
from collections import defaultdict

path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1\fitness_nsga2.xlsx"
path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1\fitness_nsga2_real.xlsx"
fitness_df = pd.read_excel(path)

def non_dominated_sort(fitness_df):
    dominating_fits = defaultdict(int)  # n (The number of people that dominate you)
    dominated_fits = defaultdict(list)  # Sp (The people you dominate)
    
    fitness_df['domcount'] = 0
    fitness_df['id'] = fitness_df.index
    fits = list(fitness_df.id)

    for i, id in enumerate(fits):
        obj1 = fitness_df.at[id, 'obj1']
        obj2 = fitness_df.at[id, 'obj2']

        #for j in range(len(fitness_df)):
        for idx in fits[i + 1:]:
            obj1x = fitness_df.at[idx, 'obj1']
            obj2x = fitness_df.at[idx, 'obj2']
            
            #if build_features.GeneticAlgorithmGenetics.dominates(objset1, objset2):
            if (obj1 <= obj1x and obj2 <= obj2x) and (obj1 < obj1x or obj2 < obj2x):
                dominating_fits[idx] += 1 
                fitness_df.at[idx, 'domcount'] += 1
                dominated_fits[id].append(idx) 

            #elif build_features.GeneticAlgorithmGenetics.dominates(objset2, objset1):  
            if (obj1x <= obj1 and obj2x <= obj2) and (obj1x < obj1 or obj2x < obj2):
                dominating_fits[id] += 1
                fitness_df.at[id, 'domcount'] += 1
                dominated_fits[idx].append(id)    

        if dominating_fits[id] == 0:
            fitness_df.loc[(fitness_df.index==id), 'front'] = 1
            #front.append(id)

    #fitness_df['rank'] = fitness_df['domcount'] + 1
    return fitness_df

fitness_df = fitness_df.filter(['obj1', 'obj2', 'population'])

sets = ['yes', 'pareto']

for set in sets:
    set_df = fitness_df[fitness_df['population'] == set]
    df = set_df.drop_duplicates()
    df = non_dominated_sort(df)
    df = df[df['front'] == 1].reset_index(drop=True)
    df = df.sort_values(by=['obj1','obj2'], ascending=[False,False]).reset_index(drop=True)

    name = df.population[0]

    prev_obj2 = 0
    prev_obj1 = 0

    prev_obj2 = df.obj2.min()
    prev_obj1 = df.obj1.min()

    area = 0
    for i in range(len(df)):
        objective1 = df.obj1[i]
        objective2 = df.obj2[i]

        objective2_diff = abs(objective2 - prev_obj2)
        objective1_diff = abs(objective1 - prev_obj1)
        area = area + (objective1_diff * objective2_diff)      

        prev_obj2 = objective2
        #prev_obj1 = objective1

    print(f"{name}: {area}")