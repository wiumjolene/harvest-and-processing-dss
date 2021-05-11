# -*- coding: utf-8 -*-
import logging
import os
import pickle
import random
import sys
import datetime

import pandas as pd
from src.data.make_dataset import ImportOptions
from src.utils import config
from src.utils.visualize import Visualize 


class Individual:
    """ Class to generate an individual solution. """
    logger = logging.getLogger(f"{__name__}.Individual")
    individual_df = pd.DataFrame()
    dlistt=[]

    def individual(self, number, alg, get_indiv=True, indiv=individual_df):
        self.logger.info(f"- individual: {number}")

        if get_indiv:
            indiv = self.make_individual()

        fitness = self.make_fitness(indiv)

        ind_fitness = pd.DataFrame(fitness, columns=['obj1', 'obj2'])
        ind_fitness['id'] = number
        ind_fitness['datetime'] = datetime.datetime.now()

        indiv.to_pickle(f"data/interim/{alg}/id_{number}") 
        return ind_fitness

    def make_individual(self, get_dlist=True, dlist=dlistt):
        self.logger.info('-> make_individual')

        # Import all data sets from pickel files.
        options = ImportOptions()

        # Get all demands ready for allocation
        if get_dlist:
            dlist_allocate = options.demand_ready()
           
        else:  # Or use custom list
            dlist_allocate = dlist

        ddf_he = options.demand_harvest()
        ddf_he['evaluated'] = 0
        ddf_pc = options.demand_capacity()
        ddic_metadata = options.demand_metadata()
        he_dic = options.harvest_estimate()
        ft_df = options.from_to()
        dic_speed = options.speed()

        individualdf = pd.DataFrame()

        while len(dlist_allocate) > 0:
            # Randomly choose which d to allocate first
            dpos = random.randint(0, len(dlist_allocate)-1)
            d = dlist_allocate[dpos]
            dkg = ddic_metadata[d]['kg']

            indd_he = []
            indd_pc = []
            indd_kg = []
            indd_kgkm = []
            indd_hrs = []
            while dkg > 0:
                # Filter demand_he table according to d and kg.
                # Check that combination of d_he has not yet been used.
                ddf_het = ddf_he[(ddf_he['demand_id']==d)&(ddf_he['kg_rem']>0)& \
                    (ddf_he['evaluated']==0)]
                    
                dhes = ddf_het['id'].tolist()
                dhe_kg_rem = ddf_het['kg_rem'].tolist()

                if len(dhes) > 0:
                    # Randomly choose a he that is suitable
                    hepos = random.randint(0, len(dhes)-1)
                    he = dhes[hepos]
                    he_kg_rem = dhe_kg_rem[hepos]

                    # Calculate kg potential that can be packed
                    if he_kg_rem > dkg:
                        to_pack = dkg

                    else:
                        to_pack = he_kg_rem

                    # Get closest pc for he from available pc's
                    block_id = he_dic[he]['block_id']
                    va_id = he_dic[he]['va_id']
                    
                    # Variables to determine speed -> add calculate the number of hours 
                    packtype_id = ddic_metadata[d]['pack_type_id']
                    ft_dft = ft_df[ft_df['block_id'] == block_id]
                    # TODO: All blocks must be able to pack at all sites

                    # Allocate to_pack to pack capacities
                    while to_pack > 0:
                        ddf_pct = ddf_pc[(ddf_pc['demand_id']==d) & (ddf_pc['kg_rem']>0)]
                        ddf_pct = ddf_pct.merge(ft_dft, on='packhouse_id', how='left')
                        
                        # Drop pc with no from to for block
                        ddf_pct = ddf_pct.dropna()

                        if len(ft_dft) > 0 and len(ddf_pct) > 0:
                            ddf_pct = ddf_pct.sort_values(['km']).reset_index(drop=True)

                            # Allocate closest pc to block
                            pc = ddf_pct.id[0]
                            packhouse_id = ddf_pct.packhouse_id[0]
                            km = ddf_pct.km[0]
                            pckg_rem = ddf_pct.kg_rem[0]

                            if pckg_rem > to_pack:
                                packed = to_pack
                                pckg_rem = pckg_rem - to_pack
                                to_pack = 0

                            else:
                                packed = pckg_rem
                                to_pack = to_pack - pckg_rem
                                pckg_rem = 0

                            try:
                                speed = dic_speed[packhouse_id][packtype_id][va_id]
                            except:
                                speed = 12

                            # Update demand tables with updated capacity
                            ddf_pc.loc[(ddf_pc['id']==pc),'kg_rem']=pckg_rem
                            ddf_he.loc[(ddf_he['id']==he),'kg_rem']=he_kg_rem-packed
                            dkg = dkg - packed

                            indd_he.append(he)
                            indd_pc.append(pc)
                            indd_kg.append(packed)
                            indd_kgkm.append(packed*km)
                            indd_hrs.append(packed*(1*config.GIVEAWAY)*speed/60)

                        else:
                            ddf_he.loc[(ddf_he['id'] == he) & (ddf_he['demand_id'] == d), 'evaluated'] = 1
                            break
                                
                else:
                    if dkg == ddic_metadata[d]['kg']:
                        indd_he.append(0)
                        indd_pc.append(0)
                        indd_kg.append(0)
                        indd_kgkm.append(0)
                        indd_hrs.append(0)
                    break
            
            dindividual = {'he':indd_he, 'pc':indd_pc, 'kg': indd_kg,
                            'kgkm': indd_kgkm, 'packhours': indd_hrs} 

            individualdft = pd.DataFrame(data=dindividual)      
            individualdft['demand_id'] = d
            individualdft['time_id'] = ddic_metadata[d]['time_id']
            individualdf = pd.concat([individualdf,individualdft])

            # Remove d from list to not alocate it again
            dlist_allocate.remove(d)

        individualdf = individualdf.reset_index(drop=True)
        return individualdf

    def make_fitness(self, individualdf):
        self.logger.info('-> make_fitness')
        options = ImportOptions()

        # TODO: dont pull data everytime 
        pc_dic = options.pack_capacity()
        pc_df = pd.DataFrame.from_dict(pc_dic, orient='index')

        ddic_metadata = options.demand_metadata()
        ddf_metadata = pd.DataFrame.from_dict(ddic_metadata, orient='index')
        ddf_metadata = ddf_metadata.reset_index(drop=False)
        ddf_metadata.rename(columns={'kg':'dkg'},inplace=True)

        individualdf2 = individualdf.groupby('pc')['demand_id'].nunique()
        individualdf2 = individualdf2.reset_index(drop=False)
        individualdf3 = individualdf2.merge(pc_df, left_on='pc', right_on='id', how='left')
        individualdf3['changes'] = individualdf3['stdunits_hour'] * individualdf3['demand_id'] 

        total_cost = ((individualdf.packhours.sum() \
                        + individualdf3.changes.sum())*config.ZAR_HR) \
                        + (individualdf.kgkm.sum()*config.ZAR_KM)

        individualdf2 = individualdf.groupby('demand_id')['kg'].sum()
        individualdf2 = individualdf2.reset_index(drop=False)
        individualdf3 = ddf_metadata.merge(individualdf2, how='left', \
                            left_index=True, right_index=True)
        individualdf3['kg'].fillna(0, inplace=True)
        individualdf3['deviation'] =  abs(individualdf3['dkg']-individualdf3['kg'])

        total_dev = individualdf3.deviation.sum()
        total_dev = (total_dev * (1 - config.GIVEAWAY)) / config.STDUNIT 

        return [[total_cost, total_dev]]


class Population:
    """ Class to generate a population of solutions. """
    logger = logging.getLogger(f"{__name__}.Population")
    indv = Individual()
    graph = Visualize()

    def population(self, size, alg):
        self.logger.info(f"population ({size})")
        pop=pd.DataFrame()
        
        for i in range(size):
            ind = self.indv.individual(i, alg)
            pop=pop.append(ind).reset_index(drop=True)

        pop['population'] = 'population'

        return pop    

            
class GeneticAlgorithmGenetics:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmGenetics")

    def tournament_selection(self, fitness_df, alg):
        """ GA: choose parents to take into crossover"""

        self.logger.info(f"--- tournament_selection")
        fitness_df=fitness_df[fitness_df['population']!='none'].reset_index(drop=True)

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
            
        parent_path = f"data/interim/{alg}/id_{parent}"
        #parent_df = pd.read_excel(parent_path + ".xlsx")
        parent_df = pd.read_pickle(parent_path) 
        #parent_df['parent'] = parent
        
        return parent_df

    def mutation(self, df_mutate, times, alg):
        """ GA mutation function to diversify gene pool. """

        self.logger.info(f"-- mutation check")
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
            df_mutate2 = pd.concat([df_mutate1, df_genenew]).reset_index(drop=True)

        else:
            
            df_mutate2 = df_mutate

        return df_mutate2

    def crossover(self, fitness_df, alg):
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
        parent1 = self.tournament_selection(pareto_df, alg)
        parent2 = self.tournament_selection(pareto_df, alg)

        # Get parental parts
        parent1a = parent1[parent1['time_id']<xp_time]
        parent1b = parent1[parent1['time_id']>=xp_time]

        parent2a = parent2[parent2['time_id']<xp_time]
        parent2b = parent2[parent2['time_id']>=xp_time]

        # Create new children
        child1 = pd.concat([parent1a, parent2b]).reset_index(drop=True)
        child2 = pd.concat([parent2a, parent1b]).reset_index(drop=True)

        # Bring mutatation opportunity in
        child1 = self.mutation(child1, times, alg)
        child2 = self.mutation(child2, times, alg)

        # Register child on fitness_df
        child1_f = ix.individual(max_id+1, alg, get_indiv=False, indiv=child1)
        child2_f = ix.individual(max_id+2, alg, get_indiv=False, indiv=child2)

        child1_f['population'] = 'child'
        child2_f['population'] = 'child'

        fitness_df = pd.concat([fitness_df, child1_f, child2_f]).reset_index(drop=True)

        return fitness_df
