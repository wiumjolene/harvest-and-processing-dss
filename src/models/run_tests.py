import datetime
import logging
import os

import numpy as np
import pandas as pd
#import pingouin

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

    def make_ga_test(self, alg_path, test_name):
        #dirpath=os.path.join('data','interim','tests', f"{alg}")
        #alg_path=os.path.join('data','interim','tests',test_name,alg)
        #alg_path = f"{test_name}/{alg}"
        fitness_df = self.population(0, config.POPUATION, alg_path, test_name)
        fitness_df['population'] = 'yes'

        if 'vega' in alg_path:
        #if alg == 'vega':
            fitness_df = self.ga1.pareto_vega(fitness_df)
            alg='vega'

        if 'nsga2' in alg_path:
        #if alg == 'nsga2':
            fitness_df = self.ga2.pareto_nsga2(fitness_df)
            alg='nsga2'

        #if alg == 'moga':
        if 'moga' in alg_path:
            fitness_df = self.ga3.pareto_moga(fitness_df)
            alg='moga'

        init_pop = fitness_df

        #FIXME:
        filename_html=f"{test_name}_{alg}"
        #filename_html=os.path.join('reports','figures',f"genetic_algorithm_{test_name}_{alg}.html")
        #filename_html = f"reports/figures/genetic_algorithm_{test_name}_{alg}.html"

        #avobs=[]
        for i in range(config.ITERATIONS):
            self.logger.info(f"ITERATION {i}")

            self.logger.debug(f"- starting crossover")

            fitness_df = self.gag.crossover(fitness_df,alg_path,test=True,test_name=test_name)

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
            pareto_indivst=pd.DataFrame(data=x,columns=['value'])
            pareto_indivst['time_id']=pareto_indivst.index
            pareto_indivst['id']=max_id + pp
            path=os.path.join(alg_path,f"id_{max_id + pp}")
            pareto_indivst.to_pickle(path, protocol=5)

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
        
        if config.SHOW:
            self.graph.scatter_plot2(fitness_df, filename_html, 'population', f"{alg_path}-final")

        return fitness_df

    def run_tests(self, alg, test, monitor):
        ga = RunTests()
        pt = ParetoFeatures()

        alg_path=os.path.join(config.ROOTDIR,'data','interim','tests',test,alg)
        if not os.path.exists(alg_path):
            os.makedirs(alg_path)
        #if not os.path.exists(f"data/interim/tests/{test}/{alg}"):
        #    os.makedirs(f"data/interim/tests/{test}/{alg}")

        hyperarea = pd.DataFrame()
        for s in range(config.SAMPLESTART, config.SAMPLEEND):
            start=datetime.datetime.now()
            fitness_df=ga.make_ga_test(alg_path, test)
            filepath=os.path.join(alg_path,f"fitness_{alg}_{s}.xlsx")
            fitness_df.to_excel(filepath, index=False)
            finish=datetime.datetime.now()

            temp = pd.DataFrame(data=[(f"{alg}_{test}", start, finish, (finish-start), s)],
                    columns=['model', 'start', 'finish', 'diff','samplenumber'])

            monitor=pd.concat([monitor, temp])

            hyperareat = pt.calculate_hyperarea(fitness_df)
            hyperareat['sample'] = s
            
            hyperarea=pd.concat([hyperarea, hyperareat]).reset_index(drop=True)

        filepath=os.path.join(alg_path, f"hyperarea_{alg}.xlsx")
        hyperarea.to_excel(filepath, index=False)
        stats = StatsTests()
        #stats.run_friedman(hyperarea, alg, test)
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
        #pgRes = pingouin.friedman(data=hyperarea,
        #                dv='hyperarea',
        #                within='population',
        #                subject='sample',
        #                method='chisq'
        #                #method='f'
        #                )

        #print(pgRes)

        #alpha = 0.05
        #if pgRes['p-unc'][0] > alpha:
        #    print('Same distributions (fail to reject H0)')
        #else:
        #    print('Different distributions (reject H0)')

        #pgRes.to_excel(f"data/interim/tests/{test}/{alg}/result_friedman_{alg}.xlsx")

        return