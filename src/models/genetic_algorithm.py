import os
import random
import sys
import logging

import pandas as pd
from src.features.build_features import Individual
from src.utils import config

class GeneticAlgorithm:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithm")

    def tournament_selection(self, fitness_df):
        """ GA: choose parents to take into crossover"""

        self.logger.info(f"- tournament_selection")

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

        self.logger.info(f"- mutation")

        mutation_random = random.randint(0,100)

        if mutation_random <= config.MUTATIONRATE:
            print('MUTATION') # TODO: log mutation!

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
            print('NO MUTATION')
            df_mutate2 = df_mutate

        return df_mutate2

    def crossover(self, fitness_df):
        """ GA crossover genetic material for diversivication"""

        self.logger.info(f"- crossover")

        ix = Individual()
        max_id = fitness_df.id.max()

        ddf_metadata = pd.read_pickle('data/processed/ddf_metadata')
        times = list(ddf_metadata.time_id.unique())

        # Get cross over point
        xp = random.randint(0,len(times)-1)
        xp_time = times[xp]

        # Select parents with tournament
        parent1 = tournament_selection(fitness_df)
        parent2 = tournament_selection(fitness_df)

        # Get parental parts
        parent1a = parent1[parent1['time_id']<xp_time]
        parent1b = parent1[parent1['time_id']>=xp_time]

        parent2a = parent2[parent2['time_id']<xp_time]
        parent2b = parent2[parent2['time_id']>=xp_time]

        # Create new children
        child1 = pd.concat([parent1a, parent2b])
        child2 = pd.concat([parent2a, parent1b])

        #########
        #add mutation function here
        child1 = mutation(child1, times)
        child2 = mutation(child2, times)
        #########

        # Register child on fitness_df
        child1_f = ix.individual(number=max_id+1, get_indiv=False, indiv=child1)
        child2_f = ix.individual(number=max_id+2, get_indiv=False, indiv=child2)

        fitness_df = pd.concat([fitness_df, child1_f, child2_f])
        return fitness_df

