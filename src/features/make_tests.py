import numpy as np
from src.utils import config


class Tests:
    D = config.D

    def ZDT1(self, x):
        f1 = x[0]  # objective 1
        g = 1 + ((9 / (config.D - 1)) * (np.sum(x[1:])))
        f2 = g * (1- (np.sqrt(f1/g))) # objective 2
        return [[f1, f2]]

    def ZDT1_pareto(self, x):
        f1 = x[0]  # objective 1
        g = 1 
        f2 = g * (1- (np.sqrt(f1/g))) # objective 2
        return [[f1, f2]]

    def ZDT2(self, x):
        f1 = x[0] # objective 1
        g = 1 + 9 * np.sum(x[1:self.D] / (self.D-1))
        h = 1 - (f1 / g) ** 2
        f2 = g * h # objective 2
        return [[f1, f2]]