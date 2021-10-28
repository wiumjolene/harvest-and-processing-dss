import pandas as pd
import sys
import os
import random
import numpy as np


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.features.build_features import Individual
from src.utils import config

test = True
df_mutate = pd.read_pickle(r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1\nsga2\id_0")
times = list(range(config.D))

""" GA mutation function to diversify gene pool. """

#self.logger.debug(f"-- mutation check")
ix = Individual()

if random.random() <= config.MUTATIONRATE:
    #self.logger.debug(f"--- mutation activated")
    
    df_mutate1=pd.DataFrame()
    for m in times:
        df_gene = df_mutate[df_mutate['time_id'] == m]

        if random.random() < config.MUTATIONRATE2:
            # If test then make new gene here
            if test:
                x = np.random.rand()
                df_gene = pd.DataFrame(data=[x], columns=['value'])
                df_gene['time_id'] = m
            
            # Else get only gene alternate
            else:  
                demand_list = list(df_gene.demand_id.unique())
                df_gene = ix.make_individual(get_dlist=False, dlist=demand_list)  # FIXME:

        df_mutate1 = pd.concat([df_mutate1, df_gene]).reset_index(drop=True)

else:
    df_mutate1 = df_mutate

