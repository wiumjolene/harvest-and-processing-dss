import datetime
import logging
import os

import numpy as np
import pandas as pd
import pingouin

from src.features.build_features import (GeneticAlgorithmGenetics, Individual,
                                         ParetoFeatures)
from src.features.make_tests import Tests
from src.models.genetic_algorithm import (GeneticAlgorithmMoga,
                                          GeneticAlgorithmNsga2,
                                          GeneticAlgorithmVega)
from src.utils import config
from src.utils.visualize import Visualize


class RunTests:
    logger = logging.getLogger(f"{__name__}.TestCases")

    gag = GeneticAlgorithmGenetics()
    test=Tests()
    graph = Visualize()
    ga1=GeneticAlgorithmVega()
    ga2=GeneticAlgorithmNsga2()
    ga3=GeneticAlgorithmMoga()
    indiv = Individual()

    def population(self, start, size, alg_path, test_name):
        pop=pd.DataFrame()
        for p in range(size):
            ind = self.indiv.individual(start + p, alg_path, test=True, test_name=test_name)
            pop=pop.append(ind).reset_index(drop=True)
        return pop

    def make_ga_test(self, alg, test_name):

        alg_path = f"{test_name}/{alg}"

        fitness_df = self.population(0, config.POPUATION, alg_path, test_name)
        fitness_df['population'] = 'yes'

        if alg == 'vega':
            fitness_df = self.ga1.pareto_vega(fitness_df)

        if alg == 'nsga2':
            fitness_df = self.ga2.pareto_nsga2(fitness_df)

        if alg == 'moga':
            fitness_df = self.ga3.pareto_moga(fitness_df)

        init_pop = fitness_df

        filename_html = f"reports/figures/genetic_algorithm_{test_name}_{alg}.html"

        for i in range(config.ITERATIONS):
            self.logger.info(f"ITERATION {i}")

            self.logger.debug(f"- starting crossover")

            fitness_df = self.gag.crossover(fitness_df, alg_path, test=True, test_name=test_name)

            #fitness_df = fitness_df.drop_duplicates(['obj1', 'obj2'], keep='first').reset_index(drop=True)
            #fitness_df=fitness_df.groupby(['obj1', 'obj2'])['id'].min().reset_index(drop=False)

            self.logger.debug(f"- initiate pareto check")
            if alg == 'vega':
                fitness_df = self.ga1.pareto_vega(fitness_df)

            if alg == 'nsga2':
                fitness_df = self.ga2.pareto_nsga2(fitness_df)

            if alg == 'moga':
                fitness_df = self.ga3.pareto_moga(fitness_df)

            if i % config.SHOWRATE == 0 and config.SHOW:
                self.graph.scatter_plot2(fitness_df, filename_html, 'population', f"{alg_path}-{i}")

        max_id = fitness_df.id.max() + 1
        t=Tests()
        # Get pareto optimal set
        for pp in range(config.POPUATION):
            x = np.random.rand(config.D)

            # Choose which test to use
            if test_name == 'zdt1':
                fitness = t.ZDT1_pareto(x)

            if test_name == 'zdt2':
                fitness = t.ZDT2_pareto(x)

            if test_name == 'zdt3':
                fitness = t.ZDT3_pareto(x)

            pareto = pd.DataFrame(fitness, columns=['obj1', 'obj2'])
            pareto['population'] = 'pareto'
            pareto['id'] = max_id + pp

            fitness_df=fitness_df.append(pareto).reset_index(drop=True)
        
        init_pop['population'] = 'initial'
        #fitness_df=fitness_df.append(init_pop).reset_index(drop=True)
        
        if config.SHOW:
            self.graph.scatter_plot2(fitness_df, filename_html, 'population', f"{alg_path}-final")

        return fitness_df

    def run_tests(self, alg, test, monitor):
        ga = RunTests()
        pt = ParetoFeatures()

        if not os.path.exists(f"data/interim/{test}/{alg}"):
            os.makedirs(f"data/interim/{test}/{alg}")

        hyperarea = pd.DataFrame()
        for s in range(config.SAMPLESTART, config.SAMPLEEND):
            start=datetime.datetime.now()
            # TODO: Add number of tests to run
            fitness_df=ga.make_ga_test(alg, test)
            fitness_df.to_excel(f"data/interim/{test}/fitness_{alg}_{s}.xlsx", index=False)
            finish=datetime.datetime.now()

            temp = pd.DataFrame(data=[(f"{alg}_{test}", start, finish, (finish-start), s)],
                    columns=['model', 'start', 'finish', 'diff','samplenumber'])

            monitor=pd.concat([monitor, temp])

            hyperareat = pt.calculate_hyperarea(fitness_df)
            hyperareat['sample'] = s
            
            hyperarea=pd.concat([hyperarea, hyperareat]).reset_index(drop=True)

        #hyperarea = hyperarea.pivot(index="sample", columns="population", values="hyperarea")
        hyperarea.to_excel(f"data/interim/{test}/hyperarea_{alg}.xlsx", index=False)
        stats = StatsTests()
        stats.run_friedman(hyperarea, alg, test)
        return monitor


class StatsTests:
    """ Class to manage Friedman tests 
    and evaluate statistical significance. """
    logger = logging.getLogger(f"{__name__}.StatsTests")

    def run_friedman(self, hyperarea, alg, test):
        """
        Pingouin package. Data in long format.

        The default assumption, or null hypothesis, 
        is that the multiple paired samples have the 
        same distribution. A rejection of the null 
        hypothesis indicates that one of the paired 
        samples has a different distribution.
        """
        pgRes = pingouin.friedman(data=hyperarea,
                        dv='hyperarea',
                        within='population',
                        subject='sample',
                        method='chisq'
                        #method='f'
                        )

        print(pgRes)

        alpha = 0.05
        if pgRes['p-unc'][0] > alpha:
            print('Same distributions (fail to reject H0)')
        else:
            print('Different distributions (reject H0)')

        pgRes.to_excel(f"data/interim/{test}/result_friedman_{alg}.xlsx")

        return