import os
import random
import sys
import logging
import math

import pandas as pd
from src.features.build_features import Individual
from src.features.build_features import Population
from src.features.build_features import GeneticAlgorithmGenetics
from src.utils.visualize import Visualize
from src.utils import config


class GeneticAlgorithmVega:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmGenetics")
    gag = GeneticAlgorithmGenetics()
    graph = Visualize()

    def vega(self):
        """ Function that manages the GA. """
        self.logger.info(f"Vector Evaluated Genetic Algorthm")
        
        p = Population()
        fitness_df = p.population(config.POPUATION, 'vega')
        fitness_df['population'] = 'yes'

        self.logger.info(f"starting VEGA search")
        for _ in range(config.ITERATIONS):
            fitness_df = self.gag.crossover(fitness_df, 'vega')
            fitness_df = self.pareto_vega(fitness_df)

        fitness_df.to_excel('data/interim/fitness.xlsx', index=False)
        filename_html = 'reports/figures/genetic_algorithm.html'
        self.graph.scatter_plot2(fitness_df, filename_html)
        return

    def pareto_vega(self, fitness_df):
        """ Decide if new child is worthy of pareto membership 
        Shaffer 1985
        """
        self.logger.info(f"- getting fitness")
        # FIXME: 
        popsize = config.POPUATION
        fitness_df=fitness_df.groupby(['obj1','obj2'])['id'].min().reset_index(drop=False)
        fitness_df['population'] = 'none'

        # Random select objective to sort
        objective = random.randint(0,1)
        objective = ['obj1', 'obj2'][objective]

        # Sort along objective
        fitness_df1 = fitness_df.sort_values(by=[objective])
        fitness_df1 = list(fitness_df1.obj1[popsize-1:popsize])[0]
        fitness_df.loc[(fitness_df[objective] <= fitness_df1), 'population'] = 'yes'      

        #fitness_df = fitness_df[fitness_df['population'] == 'yes']  

        return fitness_df

