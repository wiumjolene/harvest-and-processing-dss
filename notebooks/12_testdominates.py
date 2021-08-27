
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from src.features import build_features
import numpy as np

obj1 = [(5, 5)]
obj2 = [(1, 5)]
sign = [1,1]


#comparison = obj1 == obj2
comparison = build_features.GeneticAlgorithmGenetics.dominates(obj1, obj2)
print(comparison)

obj1x = obj2[0][0]
obj2x = obj2[0][1]
obj1a = obj1[0][0]
obj2a = obj1[0][1]

if (obj1a<=obj1x and obj2a<=obj2x) and (obj1a<obj1x or obj2a<obj2x):
    print(True)

else:
    print(False)