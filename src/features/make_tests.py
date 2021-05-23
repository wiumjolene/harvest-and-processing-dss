import numpy as np


class Tests:

    def ZDT1(self, x):
        D = 30
        f1 = x[0]  # objective 1
        g = 1 + 9 * np.sum(x[1:D] / (D-1))
        h = 1 - np.sqrt(f1/g)
        f2 = g * h  # objective 2
        return [[f1, f2]]