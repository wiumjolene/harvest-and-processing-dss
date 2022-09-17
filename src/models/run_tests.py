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
    pt = ParetoFeatures()

    def population(self, start, size, alg_path, test_name):

        population = {}
        fitness_df = pd.DataFrame()
        for p in range(size * 3):
            individual = self.indiv.individual(start + p, alg_path, test=True, test_name=test_name)
            population[p] = individual[1]

            pop = pd.DataFrame.from_dict(individual[0], orient='index', columns=['obj1','obj2'])
            fitness_df = pd.concat([fitness_df, pop])

        fitness_df['id'] = fitness_df.index
        return fitness_df, population

    def make_ga_test(self, alg_path, test_name):
        pop = self.population(0, config.POPUATION, alg_path, test_name)
        fitness_df = pop[0]

        if 'vega' in alg_path:
            fitness_df = self.ga1.pareto_vega(fitness_df)
            alg='vega'

        if 'nsga2' in alg_path:
            fitness_df = self.ga2.pareto_nsga2(fitness_df)
            alg='nsga2'

        if 'moga' in alg_path:
            fitness_df = self.ga3.pareto_moga(fitness_df)
            alg='moga'

        
        init_pop = fitness_df
        population = pop[1]
        hyperarea = pd.DataFrame()
        for i in range(config.ITERATIONS):
            self.logger.debug(f"ITERATION {i}")
            new_life = self.gag.make_children(fitness_df, alg_path, test=True, 
                                                test_name=test_name, population=population)

            fitness_df = new_life[0]
            population = new_life[1]

            if alg == 'vega':
                fitness_df = self.ga1.pareto_vega(fitness_df)

            if alg == 'nsga2':
                fitness_df = self.ga2.pareto_nsga2(fitness_df)

            if alg == 'moga':
                fitness_df = self.ga3.pareto_moga(fitness_df)

            if i % config.SHOWRATE == 0:
                filename_html=f"{test_name}_{alg}"
                fitness_df['population'] = 'yes'
                if config.SHOW:
                    self.graph.scatter_plot2(fitness_df, filename_html, 'population', f"{alg_path}-{i}")
                    hyperareat = self.pt.calculate_hyperarea(fitness_df)
                    hyperarea = pd.concat([hyperarea, hyperareat])
                    print(hyperarea)

                else:
                    hyperareat = self.pt.calculate_hyperarea(fitness_df)
                    self.logger.info(f"- CURRENT HYPERAREA: {hyperareat.hyperarea[0]}")

        fitness_df['population'] = 'yes'
        max_id = fitness_df.id.max() + 1
        t=Tests()

        p_true = t.get_pareto_true(test_name)
        # Get pareto optimal set
        #for pp in range(config.POPUATION):
        for pp in range(len(p_true)):
            x = np.random.rand(t.variables(test_name))
            pareto_indivst=pd.DataFrame(data=x,columns=['value'])
            pareto_indivst['time_id']=pareto_indivst.index
            pareto_indivst['id']=max_id + pp

            # Choose which test to use
            if test_name == 'zdt1':
                #fitness = t.ZDT1_pareto(x)
                fitness = [list(p_true[pp])]

            elif test_name == 'zdt2':
                fitness = [list(p_true[pp])]

            elif test_name == 'zdt3':
                #fitness = t.ZDT3_pareto(x)
                fitness = [list(p_true[pp])]

            elif test_name == 'zdt4':
                #fitness = t.ZDT4_pareto(x)
                fitness = [list(p_true[pp])]

            elif test_name == 'zdt5':
                #fitness = t.ZDT5_pareto(x)
                fitness = [list(p_true[pp])]
                

            elif test_name == 'zdt6':
                #fitness = t.ZDT6_pareto(x)
                fitness = [list(p_true[pp])]

            pareto = pd.DataFrame(data = fitness, columns=['obj1', 'obj2'])
            pareto['population'] = 'pareto'
            pareto['front'] = 1
            pareto['id'] = max_id + pp

            fitness_df = fitness_df.append(pareto).reset_index(drop=True)
        
        init_pop['population'] = 'initial'
        
        if config.SHOW:
            print(fitness_df)
            self.graph.scatter_plot2(fitness_df, filename_html, 'population', f"{alg_path}-final")
            

        return fitness_df

    def run_tests(self, alg, test, monitor):
        ga = RunTests()

        alg_path=os.path.join(config.ROOTDIR,'data','interim','tests',test,alg)
        if not os.path.exists(alg_path):
            os.makedirs(alg_path)

        hyperarea = pd.DataFrame()
        for s in range(config.SAMPLESTART, config.SAMPLEEND):
            start=datetime.datetime.now()
            self.logger.info(f"{test}: {s}")
            fitness_df=ga.make_ga_test(alg_path, test)
            filepath=os.path.join(alg_path,f"fitness_{alg}_{s}.xlsx")
            fitness_df.to_excel(filepath, index=False)
            finish=datetime.datetime.now()

            temp = pd.DataFrame(data=[(f"{alg}_{test}", start, finish, (finish-start), s)],
                    columns=['model', 'start', 'finish', 'diff','samplenumber'])

            monitor=pd.concat([monitor, temp])

            hyperareat = self.pt.calculate_hyperarea(fitness_df)
            hyperareat['sample'] = s
            
            hyperarea=pd.concat([hyperarea, hyperareat]).reset_index(drop=True)

        filepath=os.path.join(alg_path, f"hyperarea_{alg}.xlsx")
        hyperarea.to_excel(filepath, index=False)
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

        #print(pgRes)

        alpha = 0.05
        if pgRes['p-unc'][0] > alpha:
            print('Same distributions (fail to reject H0)')
        else:
            print('Different distributions (reject H0)')

        path=os.path.join(config.ROOTDIR, 'data', 'interim', 'tests', test, alg, f"result_friedman_{alg}.xlsx")
        pgRes.to_excel(path)

        return