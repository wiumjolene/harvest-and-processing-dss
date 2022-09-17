import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
import numpy as np
import datetime

from src.features.build_features import PrepManPlan
from src.features.build_features import Individual

mp = PrepManPlan()
indiv = Individual()


plan_date='2021-11-15'
week_str="""'21-46','21-47','21-48','21-49','21-50','21-51','21-52','22-01','22-02','22-03','22-04','22-05','22-06','22-07','22-08','22-09','22-10','22-11','22-12','22-13','22-14'"""
kp = mp.kobus_plan(plan_date, week_str)

#print(kp)


kobus_fit = indiv.individual(1000000, 
            alg_path = '', 
            get_indiv=False, 
            indiv=kp, 
            test=False)


kobus_fit = pd.DataFrame.from_dict(kobus_fit[0], orient='index', columns=['obj1','obj2'])

print(kobus_fit)