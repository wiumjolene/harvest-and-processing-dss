import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
import numpy as np
import datetime

from src.utils import config

print(datetime.datetime.now())

path = r'C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\fitness_nsga2.xlsx'

fitness_df = pd.read_excel(path)
fitness_df=fitness_df[fitness_df['front']==1].reset_index(drop=True)

def makepath(id,x):
    path = f"C:/Users/Jolene Wium/Documents/personal/studies/phd/model/model/data/interim/moga/id_{id}{x}"
    return path

ids = ['286']

for i in ids:
    id = i

    df=pd.read_pickle(makepath(id,''))

    df.to_excel(makepath(id,'.xlsx'))

    
