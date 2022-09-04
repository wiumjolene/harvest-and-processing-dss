import pandas as pd
#from scipy.stats import friedmanchisquare
#from pingouin import friedman
import pingouin

path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\hyperareas2.xlsx"
hyperarea = pd.read_excel(path, 'Sheet1')
#df = pd.read_excel(path, 'Sheet3')

"""
from scipy.stats import friedmanchisquare

df1 = pd.DataFrame({
   'hyperarea': {0: 10, 1: 8, 2: 7, 3: 9, 4: 7, 5: 4, 6: 5, 7: 6, 8: 5, 9: 10, 10: 4, 11: 7}})
df1['population'] = 1

df2 = pd.DataFrame({
   'hyperarea': {0: 7, 1: 5, 2: 8, 3: 6, 4: 5, 5: 7, 6: 9, 7: 6, 8: 4, 9: 6, 10: 7, 11: 3}})
df2['population'] = 2

df3 = pd.DataFrame({
   'hyperarea': {0: 8, 1: 5, 2: 6, 3: 4, 4: 7, 5: 5, 6: 3, 7: 7, 8: 6, 9: 4, 10: 4, 11: 3}})
df3['population'] = 3

#hyperarea=pd.concat([df1, df2])
#hyperarea['sample']=hyperarea.index
"""
print(hyperarea)

pgRes = pingouin.friedman(data=hyperarea,
                dv='hyperarea',
                within='population',
                subject='sample',
                method='chisq')
print(pgRes)

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

#pgRes.to_excel(r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\result_friedman_nsga2.xlsx")