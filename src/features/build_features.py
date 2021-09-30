# -*- coding: utf-8 -*-
import logging
import random
import datetime

import pandas as pd
import numpy as np

from src.data.make_dataset import ImportOptions
from src.utils import config
from src.utils.visualize import Visualize 
from src.features.make_tests import Tests


class Individual:
    """ Class to generate an individual solution. """
    logger = logging.getLogger(f"{__name__}.Individual")
    individual_df = pd.DataFrame()
    dlistt=[]

    def individual(self, number, alg_path, get_indiv=True, indiv=individual_df, test=False, test_name='zdt1'):
        """ Function to define indiv and fitness """
        #self.logger.info(f"- individual: {number}")
        if test:
            t=Tests()
            if get_indiv:
                x = np.random.rand(config.D)
                indiv = pd.DataFrame(x, columns=['value'])
                indiv['time_id'] = indiv.index

            else:
                x = list(indiv.value)

            # Choose which test to use
            if test_name == 'zdt1':
                fitness = t.ZDT1(x)

            if test_name == 'zdt2':
                fitness = t.ZDT2(x)

            if test_name == 'zdt3':
                fitness = t.ZDT3(x)

        else:
            if get_indiv:
                indiv = self.make_individual()

            fitness = self.make_fitness(indiv)

        ind_fitness = pd.DataFrame(fitness, columns=['obj1', 'obj2'])
        ind_fitness['id'] = number

        indiv.to_pickle(f"data/interim/{alg_path}/id_{number}", protocol = 5) 
        return ind_fitness

    def make_individual(self, get_dlist=True, dlist=dlistt):
        """ Function to make problem specific  individual solution """

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

    def population(self, size, alg_path):
        self.logger.info(f"population ({size})")
        pop=pd.DataFrame()
        
        for i in range(size):
            ind = self.indv.individual(i, alg_path)
            pop=pop.append(ind).reset_index(drop=True)

        pop['population'] = 'population'

        return pop    

            
class GeneticAlgorithmGenetics:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmGenetics")

    def tournament_selection(self, fitness_df, alg):
        """ GA: choose parents to take into crossover"""

        self.logger.info(f"--- tournament_selection")
        fitness_df=fitness_df[fitness_df['population']!='none'].reset_index(drop=True)

        high_fit1 = np.inf 
        high_fit2 = np.inf 

        for _ in range(config.TOURSIZE):
            option_num = random.randint(0,len(fitness_df)-1)
            option_id = fitness_df.id[option_num]
            fit1 = fitness_df.obj1[option_num]
            fit2 = fitness_df.obj2[option_num]

            if (fit1 <= high_fit1 and fit2 <= high_fit2) and (fit1 < high_fit1 or fit2 < high_fit2):  
                high_fit1 = fit1
                high_fit2 = fit2
                parent = option_id
            
        parent_path = f"data/interim/{alg}/id_{parent}"
        parent_df = pd.read_pickle(parent_path)  # FIXME: Optimise
                
        return parent_df

    def nondom_selection(self, fitness_df, alg):
        """This selection method makes use of the nondominated soting front to choose 
        parents. 
        NB: Only for NSGA-II. Moga etc has different structure. 
        TODO: Update for moga and VEGA. 
        TODO: Also remember to swop crossover and pareto select for real iterations.
        """

        pareto_set = fitness_df[fitness_df['front']==1].reset_index(drop=True)
        option_num = random.randint(0,len(pareto_set)-1)
        option_id = pareto_set.at[option_num, 'id']
        parent_path = f"data/interim/{alg}/id_{option_id}"
        parent_df = pd.read_pickle(parent_path)  # FIXME: Optimise
        #parent_df.to_excel(f"data/check/parent_{option_id}.xlsx")
        return parent_df

    def mutation(self, df_mutate, times, test):
        """ GA mutation function to diversify gene pool. """

        self.logger.info(f"-- mutation check")
        ix = Individual()

        if random.random() <= config.MUTATIONRATE:
            self.logger.info(f"--- mutation activated")

            df_mutate1=pd.DataFrame()
            for m in times:
                df_gene = df_mutate[df_mutate['time_id'] == m]
                if random.random() < config.MUTATIONRATE2:
                    # If test then make new gene here
                    if test:
                        x = np.random.rand(1)
                        df_gene = pd.DataFrame(x, columns=['value'])
                        df_gene['time_id'] = m
                    
                    # Else get only gene alternate
                    else:  
                        demand_list = list(df_gene.demand_id.unique())
                        df_gene = ix.make_individual(get_dlist=False, dlist=demand_list)  # FIXME:

                df_mutate1 = pd.concat([df_mutate1, df_gene]).reset_index(drop=True)

        else:
            df_mutate1 = df_mutate

        return df_mutate1

    def crossover(self, fitness_df, alg, test=False, test_name='zdt1'):
        """ GA crossover genetic material for diversification"""
        self.logger.info(f"-- crossover")

        ix = Individual()
        max_id = fitness_df.id.max()

        if test:
            times = list(range(config.D))

        else:
            ddf_metadata = pd.read_pickle('data/processed/ddf_metadata')
            times = list(ddf_metadata.time_id.unique())

        # Select parents with tournament
        #if alg == 'zdt1/nsga2':  # TODO: make universal
        if alg == '':
            pareto_df = fitness_df[fitness_df['front'] == 1].reset_index(drop=True)
            parent1 = self.nondom_selection(pareto_df, alg)
            parent2 = self.nondom_selection(pareto_df, alg)

        else:
            pareto_df = fitness_df[fitness_df['population'] != 'none'].reset_index(drop=True)
            parent1 = self.tournament_selection(pareto_df, alg)
            parent2 = self.tournament_selection(pareto_df, alg)

        # Uniform crossover
        child1=pd.DataFrame()
        child2=pd.DataFrame()
        for g in times:
            gene1 = parent1[parent1['time_id']==g]
            gene2 = parent2[parent2['time_id']==g]
            
            if random.random() < config.CROSSOVERRATE:
                child1 = pd.concat([child1,gene2]).reset_index(drop=True)
                child2 = pd.concat([child2,gene1]).reset_index(drop=True)

            else:
                child1 = pd.concat([child1,gene1]).reset_index(drop=True)
                child2 = pd.concat([child2,gene2]).reset_index(drop=True)                

        # If test then make new test individual gene
        if test:
            # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=test)
            child2 = self.mutation(child2, times, test=test)

            # Register child on fitness_df
            #print(test_name)
            child1_f = ix.individual(max_id+1, alg, get_indiv=False, indiv=child1, 
                            test=test, test_name=test_name)
            child2_f = ix.individual(max_id+2, alg, get_indiv=False, indiv=child2, 
                            test=test, test_name=test_name) 

        else:
           # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=False)
            child2 = self.mutation(child2, times, test=False)

            # Register child on fitness_df
            child1_f = ix.individual(max_id+1, alg, get_indiv=False, indiv=child1)
            child2_f = ix.individual(max_id+2, alg, get_indiv=False, indiv=child2)

        child1_f['population'] = 'child'
        child2_f['population'] = 'child'

        fitness_df = pd.concat([fitness_df, child1_f, child2_f]).reset_index(drop=True)
        return fitness_df

    def dominates(objset1, objset2, sign=[1, 1]):
        """
        DEPRICATED
        Return true if each objective of *self* is not strictly worse than
                the corresponding objective of *other* and at least one objective is
                strictly better.
            **no need to care about the equal cases
            (Cuz equal cases mean they are non-dominators)
        :param obj1: a list of multiple objective values
        :type obj1: numpy.ndarray
        :param obj2: a list of multiple objective values
        :type obj2: numpy.ndarray
        :param sign: target types. positive means maximize and otherwise minimize.
        :type sign: list
        FROM DEAP
        """
        #print(f"{objset1[0]},{objset1[1]} - {objset1[0]},{objset2[1]}")
        indicator = False
        for a, b, sign in zip(objset1, objset2, sign):
            if a * sign < b * sign:
                indicator = True
            # if one of the objectives is dominated, then return False
            elif a * sign > b * sign:
                return False
        return indicator
