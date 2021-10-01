import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
import numpy as np
import datetime

from src.features.build_features import ParetoFeatures


path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1\fitness_nsga2.xlsx"
path = r"C:\Users\Jolene Wium\Documents\personal\studies\phd\model\model\data\interim\zdt1\fitness_nsga2_real.xlsx"
fitness_df = pd.read_excel(path)

pt = ParetoFeatures()
hyperarea = pt.calculate_hyperarea(fitness_df)