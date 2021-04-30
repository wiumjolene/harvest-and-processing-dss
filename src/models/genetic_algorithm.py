import os
import random
import sys
import logging
import math

import pandas as pd
from src.features.build_features import Individual
from src.features.build_features import Population
from src.utils.visualize import Visualize
from src.utils import config


class GeneticAlgorithm:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithm")
    graph = Visualize()

    def genetic_algorithm(self):
        """ Function that manages the GA. """
        self.logger.info(f"- genetic_algorithm")
        
        p = Population()
        fitness_df = p.population(config.POPUATION)
        
        for _ in range(config.ITERATIONS):
            fitness_df = self.crossover(fitness_df)

        fitness_df.to_excel('data/interim/fitness.xlsx', index=False)
        filename_html = 'reports/figures/genetic_algorithm.html'
        self.graph.scatter_plot2(fitness_df, filename_html)
        return

    def tournament_selection(self, fitness_df):
        """ GA: choose parents to take into crossover"""

        self.logger.info(f"--- tournament_selection")

        #TODO: filter on population

        high_fit1 = 0
        high_fit2 = 0

        for _ in range(config.TOURSIZE):
            option_num = random.randint(0,len(fitness_df)-1)
            option_id = fitness_df.id[option_num]
            fit1 = fitness_df.obj1[option_num]
            fit2 = fitness_df.obj2[option_num]

            if fit1 >= high_fit1 or fit2 >= high_fit2:
                high_fit1 = fit1
                high_fit2 = fit2
                parent = option_id

        if high_fit1 == 0 and high_fit2 == 0:
            parent = option_id
            
        parent_path = f"data/interim/id_{parent}.xlsx" #TODO: Make pickle
        parent_df = pd.read_excel(parent_path)
        #parent_df = pd.read_pickle(parent_path) #TODO: Make pickle
        parent_df['parent'] = parent
        
        return parent_df

    def mutation(self, df_mutate, times):
        """ GA mutation function to diversify gene pool. """

        self.logger.info(f"-- mutation")

        mutation_random = random.randint(0,100)

        if mutation_random <= config.MUTATIONRATE:
            self.logger.info(f"--- mutation activated")

            # Get mutation point
            mp = random.randint(0,len(times)-1)
            mp_time = times[mp]

            df_genex = df_mutate[df_mutate['time_id'] == mp_time]
            demand_list = list(df_genex.demand_id.unique())

            ix = Individual()
            df_genenew = ix.make_individual(get_dlist=False, dlist=demand_list)

            df_mutate1 = df_mutate[df_mutate['time_id'] != mp_time]
            df_mutate2 = pd.concat([df_mutate1, df_genenew])

        else:
            
            df_mutate2 = df_mutate

        return df_mutate2

    def pareto_moga(self, fitness_df):
        """ Decide if new child is worthy of pareto membership 
        Fonseca and Flemming 1993
        """
        fitness_df1 = fitness_df[fitness_df['population'] != 'none'].reset_index(drop=True)

        for i in range(len(fitness_df1)):
            id = fitness_df1.id[i]
            obj1 = fitness_df1.obj1[i]
            obj2 = fitness_df1.obj2[i]
            r = 1

            for j in range(len(fitness_df1)):
                obj1x = fitness_df1.obj1[j]
                obj2x = fitness_df1.obj2[j]      

                if obj1x < obj1 and obj2x < obj2:
                    r = r + 1

            fitness_df.loc[(fitness_df['id']==id), 'rank'] = r

        fitness_df= fitness_df.sort_values(by='rank').reset_index(drop=True)

        fitness_df.loc[(fitness_df.index<=config.POPUATION), 'population'] = 'population'
        fitness_df.loc[(fitness_df['rank']==1), 'population'] = 'pareto'
        fitness_df.loc[(fitness_df.index>config.POPUATION), 'population'] = 'none'

        # NB: average out those with the same value
        return fitness_df

    def pareto_vega(self, fitness_df):
        """ Decide if new child is worthy of pareto membership 
        Shaffer 1985
        """
        # FIXME: only evaluate child and old pareto pop
        pareto = math.floor(config.POPUATION/2)
        fitness_df['pareto'] = 'n'

        # Sort along obj1 1
        fitness_df1 = fitness_df.sort_values(by=['obj1'])
        fitness_df1 = list(fitness_df1.obj1[pareto-1:pareto])[0]
        fitness_df.loc[(fitness_df['obj1'] <= fitness_df1), 'population'] = 'pareto'

        # Sort along obj1 2
        fitness_df2 = fitness_df.sort_values(by=['obj2'])
        fitness_df2 = list(fitness_df2.obj2[pareto-1:pareto])[0]
        fitness_df.loc[(fitness_df['obj2'] <= fitness_df2), 'population'] = 'pareto'        

        return fitness_df

    def crossover(self, fitness_df):
        """ GA crossover genetic material for diversivication"""

        self.logger.info(f"-- crossover")

        ix = Individual()
        max_id = fitness_df.id.max()

        ddf_metadata = pd.read_pickle('data/processed/ddf_metadata')
        times = list(ddf_metadata.time_id.unique())

        # Get cross over point
        xp = random.randint(0,len(times)-1)
        xp_time = times[xp]

        # Select parents with tournament
        pareto_df = fitness_df[fitness_df['population'] != 'none'].reset_index(drop=True)
        parent1 = self.tournament_selection(pareto_df)
        parent2 = self.tournament_selection(pareto_df)

        # Get parental parts
        parent1a = parent1[parent1['time_id']<xp_time]
        parent1b = parent1[parent1['time_id']>=xp_time]

        parent2a = parent2[parent2['time_id']<xp_time]
        parent2b = parent2[parent2['time_id']>=xp_time]

        # Create new children
        child1 = pd.concat([parent1a, parent2b]).reset_index(drop=True)
        child2 = pd.concat([parent2a, parent1b]).reset_index(drop=True)

        # Bring mutatation opportunity in
        child1 = self.mutation(child1, times)
        child2 = self.mutation(child2, times)

        # Register child on fitness_df
        child1_f = ix.individual(number=max_id+1, get_indiv=False, indiv=child1)
        child2_f = ix.individual(number=max_id+2, get_indiv=False, indiv=child2)

        child1_f['population'] = 'child'
        child2_f['population'] = 'child'

        fitness_df = pd.concat([fitness_df, child1_f, child2_f]).reset_index(drop=True)

        fitness_df = self.pareto_moga(fitness_df)

        return fitness_df

