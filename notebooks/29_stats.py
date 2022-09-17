import pandas as pd
from scipy import stats
import pingouin
import os


path = os.path.join(r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\external","20220909_25k","zdt2",'nsga2','hyperarea_nsga2.xlsx')
path = os.path.join(r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\external","20220911","zdt1",'hyperarea_nsga2.xlsx')
#path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\hyperareas2.xlsx"

df_long = pd.read_excel(path, 'Sheet1')
df_long['hyperarea'] = df_long['hyperarea'].astype(float)

df = df_long.pivot(index='sample',columns='population', values='hyperarea')
#df['yes'] = df['yes'].round(5)
#df['pareto'] = df['pareto'].round(5)

s, p = stats.ranksums(df['yes'],df['pareto'])
print(f"Wilcoxon Rank Sum p-value: {p}")
#print(f"Wilcoxon Rank Sum test statistic: {s}")

s, p = stats.ttest_ind(df['yes'],df['pareto'])
print(f"T-test p-value: {p}")



pgRes = pingouin.friedman(data=df_long,
                dv='hyperarea',
                within='population',
                subject='sample',
                method='chisq')

print(f"Friedmand p-value: {pgRes['p-unc'][0]}")

"""
The default assumption, or null hypothesis, 
is that the multiple paired samples have the 
same distribution. A rejection of the null 
hypothesis indicates that one or more of the 
paired samples has a different distribution.
"""
alpha = 0.05
if pgRes['p-unc'][0] > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')


print(df.describe())