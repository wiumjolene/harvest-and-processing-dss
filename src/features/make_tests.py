import logging

import numpy as np
import random
import math
from pymoo.problems import get_problem
from src.utils import config


class Tests:
    logger = logging.getLogger(f"{__name__}.TestCases")


    def variables(self, test):
        if test == 'zdt1':
            nvars = 30

        elif test == 'zdt2':
            nvars = 30

        elif test == 'zdt3':
            nvars = 30

        elif test == 'zdt4':
            nvars = 10

        elif test == 'zdt5':
            nvars = 11
            nvars2 = 5

        elif test == 'zdt6':
            nvars = 10

        return nvars

    def get_pareto_true(self, test):
        if test == 'zdt1':
            p_true = self.ZDT1_pareto_TRUE(1)

        elif test == 'zdt2':
            p_true = self.ZDT2_pareto_TRUE(1)

        elif test == 'zdt3':
            p_true = self.ZDT3_pareto_TRUE(1)

        elif test == 'zdt4':
            p_true = self.ZDT4_pareto_TRUE(1)

        elif test == 'zdt5':
            p_true = self.ZDT5_pareto_TRUE(1) #FIXME:

        elif test == 'zdt6':
            p_true = self.ZDT6_pareto_TRUE(1)

        return p_true
    ###############################################################
    # ZDT1
    ###############################################################
    def ZDT1(self, x):
        self.logger.debug(f"-- ZDT1 test: len = {len(x)}")
        nvars = self.variables('zdt1')
        f1 = x[0]  # objective 1
        g = 1 + ((9 / (nvars - 1)) * (np.sum(x[1:])))
        f2 = g * (1- (np.sqrt(f1/g))) # objective 2
        return [[f1, f2]]

    def ZDT1_pareto(self, x):
        self.logger.debug(f"-- ZDT1 pareto")
        f1 = x[0]  # objective 1
        g = 1 
        f2 = g * (1- (np.sqrt(f1/g))) # objective 2
        return [[f1, f2]]

    def ZDT1_pareto_TRUE(self, x):
        self.logger.debug(f"-- ZDT1 pareto")
        pf = get_problem("zdt1").pareto_front()
        return pf

    ###############################################################
    # ZDT2
    ###############################################################
    def ZDT2(self, x):
        self.logger.debug(f"-- ZDT2 test")
        nvars = self.variables('zdt2')
        f1 = x[0] # objective 1

        g1 = 9 / (nvars-1)
        g2 = np.sum(x[1:nvars])
        g = 1 + (g1 * g2)
        h = 1 - (f1 / g) ** 2
        f2 = g * h # objective 2
        return [[f1, f2]]

    def ZDT2_pareto(self, x):
        self.logger.debug(f"-- ZDT2 pareto")
        f1 = x[0] # objective 1
        g = 1
        h = 1 - (f1 / g) ** 2
        f2 = g * h # objective 2

        return [[f1, f2]]

    def ZDT2_pareto_TRUE(self, x):
        self.logger.debug(f"-- ZDT2 pareto")
        pf = get_problem("zdt2").pareto_front()
        return pf


    ###############################################################
    # ZDT3
    ###############################################################
    def ZDT3(self, x):
        self.logger.debug(f"-- ZDT3 test")
        nvars = self.variables('zdt3')

        f1 = x[0] # objective 1

        g1 = 9 / (nvars-1)
        g2 = np.sum(x[1:nvars])
        g = 1 + (g1 * g2)

        h = 1 - np.sqrt(f1/g) - ((f1/g) * (math.sin(10 * math.pi * f1)))

        f2 = g * h # objective 2
        return [[f1, f2]]

    def ZDT3_pareto(self, x):
        self.logger.debug(f"-- ZDT3 pareto")
        f1 = x[0] # objective 1
        g = 1
        h = 1 - np.sqrt(f1/g) - ((f1/g) * (math.sin(10 * math.pi * f1)))
        f2 = g * h # objective 2
        return [[f1, f2]]

    def ZDT3_pareto_TRUE(self, x):
        self.logger.debug(f"-- ZDT3 pareto")
        pf = get_problem("zdt3").pareto_front()
        return pf

    ###############################################################
    # ZDT4
    ###############################################################
    def ZDT4(self, x):
        self.logger.debug(f"-- ZDT4 test")
        nvars = self.variables('zdt4')
        f1 = x[0] # objective 1

        g = 1.0 + 10.0*(nvars-1) + sum([math.pow(x[i], 2.0) - 10.0*math.cos(4.0*math.pi*x[i]) for i in range(1, nvars)])
        h = 1.0 - math.sqrt(x[0] / g)

        f2 = g * h # objective 2
        return [[f1, f2]]

    def ZDT4_pareto(self, x):
        self.logger.debug(f"-- ZDT4 pareto")
        f1 = x[0] # objective 1
        g = 1
        h = 1.0 - math.sqrt(x[0] / g)
        f2 = g * h # objective 2
        return [[f1, f2]]

    def ZDT4_pareto_TRUE(self, x):
        self.logger.debug(f"-- ZDT4 pareto")
        pf = get_problem("zdt4").pareto_front()
        return pf

    ###############################################################
    # ZDT5
    ###############################################################
    def ZDT5_indiv(self):
        nvars = 11
        indiv = []
        for n in range(nvars):
            if n == 0:
                indiv.append([random.choice([False, True]) for _ in range(30)])

            else:
                indiv.append([random.choice([False, True]) for _ in range(5)])

        return indiv

    def ZDT5_mutate(self, indiv, pos):
        #print(f"before: {indiv}")
        
        if pos == 0:
            indiv[pos] = [random.choice([False, True]) for _ in range(30)]

        else:
            indiv[pos] = [random.choice([False, True]) for _ in range(5)]

        #print(f"after: {indiv}")
        return indiv

    def ZDT5(self, x):
        
        f1 = 1.0 + sum(x[0])
        g = sum([2+sum(v) if sum(v) < 5 else 1 for v in x[1:]])
        h = 1.0 / f1
        f2 = g*h

        return [[f1, f2]]

    def ZDT5_pareto(self, x):
        f1 = 0
        f2 = 0
        return [[f1, f2]]

    def ZDT5_pareto_TRUE(self, x):
        self.logger.debug(f"-- ZDT5 pareto")
        pf = get_problem("zdt5", normalize=False).pareto_front()
        return pf

    ###############################################################
    # ZDT6
    ###############################################################
    def ZDT6(self, x):
        self.logger.debug(f"-- ZDT6 test")
        nvars = self.variables('zdt6')

        f1 = 1.0 - math.exp(-4.0*x[0])*math.pow(math.sin(6.0*math.pi*x[0]), 6.0)
        g = 1.0 + 9.0*math.pow(sum(x[1:]) / (nvars-1.0), 0.25)
        h = 1.0 - math.pow(f1 / g, 2.0)
        f2 = g * h # objective 2
        
        return [[f1, f2]]

    def ZDT6_pareto(self, x):
        self.logger.debug(f"-- ZDT6 pareto")
        f1 = 1.0 - math.exp(-4.0*x[0])*math.pow(math.sin(6.0*math.pi*x[0]), 6.0) # objective 1
        g = 1
        h = 1.0 - math.pow(f1 / g, 2.0)
        #h = 1.0 - math.pow(x[0] / g, 2.0)
        f2 = g * h # objective 2
        return [[f1, f2]]

    def ZDT6_pareto_TRUE(self, x):
        self.logger.debug(f"-- ZDT6 pareto")
        pf = get_problem("zdt6").pareto_front()
        return pf