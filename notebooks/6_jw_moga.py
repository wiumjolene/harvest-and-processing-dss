import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from src.utils.visualize import Visualize
from src.utils import config

graph = Visualize()

p = r'C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\fitness.xlsx'
fitness_df = pd.read_excel(p)

fitness_df1 = fitness_df[fitness_df['population'] != 'none'].reset_index(drop=True)
fitness_df1= fitness_df1.sort_values(by=['obj1','obj2']).reset_index(drop=True)

fitness_df1=fitness_df1.groupby(['obj1','obj2'])['id'].min().reset_index(drop=False)

for i in range(len(fitness_df1)):
    id = fitness_df1.id[i]
    obj1 = fitness_df1.obj1[i]
    obj2 = fitness_df1.obj2[i]
    r = 1

    for j in range(len(fitness_df1)):
        idx = fitness_df1.id[j]
        obj1x = fitness_df1.obj1[j]
        obj2x = fitness_df1.obj2[j]      

        if obj1x < obj1 and obj2x < obj2:
            r = r + 1

    fitness_df.loc[(fitness_df['id']==id), 'rank'] = r

fitness_df= fitness_df.sort_values(by='rank').reset_index(drop=True)

fitness_df.loc[(fitness_df.index<=config.POPUATION), 'population'] = 'population'
fitness_df.loc[(fitness_df['rank']==1), 'population'] = 'pareto'
fitness_df.loc[(fitness_df.index>config.POPUATION), 'population'] = 'none'

graph.scatter_plot2(fitness_df, 'html.html')