import pandas as pd
#from scipy.stats import friedmanchisquare
#from pingouin import friedman
import pingouin

path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\hyperareas.xlsx"
hyperarea = pd.read_excel(path, 'Sheet1')

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