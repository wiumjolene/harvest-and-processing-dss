import numpy as np


class Tests:
    D = 30

    def ZDT1(self, x):
        f1 = x[0]  # objective 1
        g = 1 + 9 * np.sum(x[1:self.D] / (self.D-1))
        h = 1 - np.sqrt(f1/g)
        f2 = g * h  # objective 2
        return [[f1, f2]]

    def ZDT2(self, x):
        f1 = x[0] # objective 1
        g = 1 + 9 * np.sum(x[1:self.D] / (self.D-1))
        h = 1 - (f1 / g) ** 2
        f2 = g * h # objective 2
        return [[f1, f2]]