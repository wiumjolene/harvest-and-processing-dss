import pandas as pd
from scipy import stats


path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\hyperareas.xlsx"
df_long = pd.read_excel(path, 'Sheet1')
#print(df_long)

df = df_long.pivot(index='sample',columns='population', values='hyperarea')
#print(df)

s, p = stats.wilcoxon(df['yes'],df['pareto'])

print(p)


s, p = stats.ranksums(df['yes'],df['pareto'])

print(p)

print(df.describe())