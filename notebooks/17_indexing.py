import pandas as pd
  
# dictionary of lists
dict = {'name':["aparna", "pankaj", "sudhir", "Geeku"],
        'degree': ["MBA", "BCA", "M.Tech", "MBA"],
        'score':[90, 40, 80, 98]}
  
df = pd.DataFrame(dict, index = [0, 1, 2, 3])
print(df)

index = [True, False, True, False]
df['index'] = index
df = df.set_index('index')

print(df)

 
print(df.loc[True])
print(df.loc[False])




parent_path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1\nsga2\id_103"
parent_df = pd.read_pickle(parent_path)  # FIXME: Optimise









