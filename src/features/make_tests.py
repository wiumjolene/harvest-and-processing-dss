import logging

import numpy as np
import math
from src.utils import config


class Tests:
    logger = logging.getLogger(f"{__name__}.TestCases")
    D = config.D

    ###############################################################
    # ZDT1
    ###############################################################
    def ZDT1(self, x):
        self.logger.info(f"-- ZDT1 test")
        f1 = x[0]  # objective 1
        g = 1 + ((9 / (config.D - 1)) * (np.sum(x[1:])))
        f2 = g * (1- (np.sqrt(f1/g))) # objective 2
        return [[f1, f2]]

    def ZDT1_pareto(self, x):
        self.logger.info(f"-- ZDT1 pareto")
        f1 = x[0]  # objective 1
        g = 1 
        f2 = g * (1- (np.sqrt(f1/g))) # objective 2
        return [[f1, f2]]

    ###############################################################
    # ZDT2
    ###############################################################
    def ZDT2(self, x):
        self.logger.info(f"-- ZDT2 test")
        f1 = x[0] # objective 1
        #g = 1 + (9 * (np.sum(x[1:config.D]) / (config.D-1)))
        g1 = 9 / (config.D-1)
        g2 = np.sum(x[1:config.D])
        g = 1 + (g1 * g2)
        h = 1 - (f1 / g) ** 2
        f2 = g * h # objective 2
        return [[f1, f2]]

    def ZDT2_pareto(self, x):
        self.logger.info(f"-- ZDT2 pareto")
        f1 = x[0] # objective 1
        g = 1
        h = 1 - (f1 / g) ** 2
        f2 = g * h # objective 2
        return [[f1, f2]]

    ###############################################################
    # ZDT3
    ###############################################################
    def ZDT3(self, x):
        self.logger.info(f"-- ZDT3 test")
        f1 = x[0] # objective 1

        g1 = 9 / (config.D-1)
        g2 = np.sum(x[1:config.D])
        g = 1 + (g1 * g2)

        h = 1 - np.sqrt(f1/g) - ((f1/g) * (math.sin(10 * math.pi * f1)))

        f2 = g * h # objective 2
        return [[f1, f2]]

    def ZDT3_pareto(self, x):
        self.logger.info(f"-- ZDT3 pareto")
        f1 = x[0] # objective 1
        g = 1
        h = 1 - np.sqrt(f1/g) - ((f1/g) * (math.sin(10 * math.pi * f1)))
        f2 = g * h # objective 2
        return [[f1, f2]]