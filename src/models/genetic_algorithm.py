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
        fitness_df['pareto'] = 'p'
        pareto = math.floor(config.POPUATION/2)

        for _ in range(config.ITERATIONS):
            fitness_df = self.crossover(fitness_df)

            #fitness_df['pareto'] = 'n'

            #fitness_df1 = fitness_df.sort_values(by=['obj1'])
            #fitness_df1 = list(fitness_df1.obj1[pareto-1:pareto])[0]
            #fitness_df.loc[(fitness_df['obj1'] <= fitness_df1), 'pareto'] = 'p'

            #fitness_df2 = fitness_df.sort_values(by=['obj2'])
            #fitness_df2 = list(fitness_df2.obj2[pareto-1:pareto])[0]
            #fitness_df.loc[(fitness_df['obj2'] <= fitness_df2), 'pareto'] = 'p'

        fitness_df.to_excel('data/interim/fitness.xlsx', index=False)
        filename_html = 'reports/figures/genetic_algorithm.html'
        self.graph.scatter_plot2(fitness_df, filename_html)
        return

    def tournament_selection(self, fitness_df):
        """ GA: choose parents to take into crossover"""

        self.logger.info(f"--- tournament_selection")

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

    def pareto_converge(self, pareto_df, individual):
        """ Decide if new child is worthy of pareto membership """

        n_obj1 = individual.obj1[0]
        n_obj2 = individual.obj2[0]
        n_id = individual.id[0]

        none_id = -99
        pareto_id = -99
        
        for _ in range(len(pareto_df)):
            obj1 = pareto_df.obj1[_]
            obj2 = pareto_df.obj2[_]
            old_id = pareto_df.id[_]
            
            if n_obj1 < obj1 or n_obj2 < obj2:
                none_id = old_id
                pareto_id = n_id
                break
                
        return [none_id, pareto_id]

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
        pareto_df = fitness_df[fitness_df['pareto'] == 'p'].reset_index(drop=True)
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

        child1_f['pareto'] = 'n'
        child2_f['pareto'] = 'n'

        fitness_df = pd.concat([fitness_df, child1_f, child2_f]).reset_index(drop=True)

        cp1 = self.pareto_converge(pareto_df, child1_f)
        fitness_df.loc[(fitness_df['id'] == cp1[0]), 'pareto'] = 'n'
        fitness_df.loc[(fitness_df['id'] == cp1[1]), 'pareto'] = 'p'

        cp2 = self.pareto_converge(pareto_df, child2_f)
        fitness_df.loc[(fitness_df['id'] == cp2[0]), 'pareto'] = 'n'
        fitness_df.loc[(fitness_df['id'] == cp2[1]), 'pareto'] = 'p'

        return fitness_df

