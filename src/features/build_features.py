# -*- coding: utf-8 -*-
import datetime
import logging
import os
import pickle
import random
from collections import defaultdict
from operator import itemgetter

import numpy as np
import pandas as pd
from sqlalchemy import column
from src.data.make_dataset import (GetLocalData,
                                   ImportOptions)
from src.features.make_tests import Tests
from src.utils import config
from src.utils.connect import DatabaseModelsClass
from src.utils.visualize import Visualize


class PrepModelData:
    """ Class to make features of ... """
    logger = logging.getLogger(f"{__name__}.PrepModelData")
    gld = GetLocalData()
    database_dss = DatabaseModelsClass('PHDDATABASE_URL')
    #mf = MakeFeatures()

    def prep_harvest_estimates(self, plan_date, weeks_str):
        self.logger.info(f"- Prep harvest estimate")

        try:
            fc = self.gld.get_he_fc()
            if len(fc) > 0:
                self.database_dss.insert_table(fc, 'dim_fc', 'dss', if_exists='append')
                self.logger.info(f"-- Added {len(fc)} fcs")

            block = self.gld.get_he_block()
            if len(block) > 0:
                self.database_dss.insert_table(block, 'dim_block', 'dss', if_exists='append')
                self.logger.info(f"-- Added {len(block)} blocks")

            va = self.gld.get_he_va()
            if len(va) > 0:
                self.database_dss.insert_table(va, 'dim_va', 'dss', if_exists='append')
                self.logger.info(f"-- Added {len(va)} vas")

            he = self.gld.get_local_he(plan_date, weeks_str)
            self.database_dss.execute_query(f"DELETE FROM `dss`.`f_harvest_estimate` WHERE (`plan_date` = '{plan_date}');")
            he['add_datetime'] = datetime.datetime.now()
            self.database_dss.insert_table(he, 'f_harvest_estimate', 'dss', if_exists='append')
            success = True

        except:
            success = False
            self.logger.info(f"-- Prep harvest estimate failed")
            
        return success

    def prep_demand_plan(self, plan_date, weeks_str):
        self.logger.info(f"- Prep demand plan")

        try:
            client = self.gld.get_dp_client()
            if len(client) > 0:
                self.database_dss.insert_table(client, 'dim_client', 'dss', if_exists='append')
                self.logger.info(f"-- Added {len(client)} clients")

            self.database_dss.execute_query(f"DELETE FROM `dss`.`f_demand_plan` WHERE (`plan_date` = '{plan_date}');")
            dp = self.gld.get_local_dp(plan_date, weeks_str)
            dp['add_datetime'] = datetime.datetime.now()
            self.database_dss.insert_table(dp, 'f_demand_plan', 'dss', if_exists='append')
            success = True
        
        except:
            success = False
            self.logger.info(f"-- Prep demand failed")

        return success

    def prep_pack_capacity(self, plan_date, weeks_str):
        self.logger.info(f"- Prep pack capacities")

        try:
            packhouse = self.gld.get_pc_packhouse()
            if len(packhouse) > 0:
                self.database_dss.insert_table(packhouse, 'dim_packhouse', 'dss', if_exists='append')
                self.logger.info(f"-- Added {len(packhouse)} packhouses")

            #pc = self.gld.get_local_pc(plan_date, weeks_str) #FIXME: Set on variable to create day pc
            pc = self.gld.get_local_pc_day(plan_date, weeks_str)

            self.database_dss.execute_query(f"DELETE FROM `dss`.`f_pack_capacity` WHERE (`plan_date` = '{plan_date}');")
            pc['add_datetime'] = datetime.datetime.now()
            self.database_dss.insert_table(pc, 'f_pack_capacity', 'dss', if_exists='append')
            success = True

        except:
            success = False
            self.logger.info(f"-- Prep pack failed")

        return success


class Individual:
    """ Class to generate an individual solution. """
    logger = logging.getLogger(f"{__name__}.Individual")
    t=Tests()
    options = ImportOptions()
    individual_df = pd.DataFrame()
    dlistt=[]

    def individual(self, number, alg_path, get_indiv=True, 
                    indiv=individual_df, test=False, 
                    test_name='zdt1'):

        """ Function to define indiv and fitness """
        self.logger.debug(f"- individual: {number}")
        if test:
            #t=Tests()
            if get_indiv:
                if test_name == 'zdt5':
                    x = self.t.ZDT5_indiv()
                    indiv = dict(enumerate(x))

                else:    
                    x = np.random.rand(self.t.variables(test_name))
                    indiv = dict(enumerate(x))

            else:
                x = list(indiv.values())

            # Choose which test to use
            if test_name == 'zdt1':
                fitness = self.t.ZDT1(x)

            elif test_name == 'zdt2':
                fitness = self.t.ZDT2(x)

            elif test_name == 'zdt3':
                fitness = self.t.ZDT3(x)

            elif test_name == 'zdt4':
                fitness = self.t.ZDT4(x)

            elif test_name == 'zdt5':
                fitness = self.t.ZDT5(x)

            elif test_name == 'zdt6':
                fitness = self.t.ZDT6(x)

            ind_fitness = {number: fitness[0]}

        else:
            if get_indiv:
                indiv = self.make_individual()

            path=os.path.join(alg_path, f"id_{number}")
            indiv.to_pickle(path, protocol=5)

            fitness = self.make_fitness(indiv)

            ind_fitness = {number: fitness[0]}

        return ind_fitness, indiv

    def make_individual(self, get_dlist=True, dlist=dlistt):
        """ Function to make problem specific individual solution """

        self.logger.debug('-> make_individual')

        # Import all data sets from pickel files.
        self.logger.debug('--> get demand options')
        
        week_demand = self.options.easy_demand()
        week_he = self.options.easy_harvest()
        week_pc = self.options.easy_pc()
        from_to = self.options.easy_ft()

        #from_to = self.options.easy_ft()

        if get_dlist:
            weeks = list(week_demand.keys())

        else:
            weeks = [dlist]
        
        individualdf = pd.DataFrame()
        genes = []
        for week in weeks:
            priorities = list(week_demand[week].keys())

            for prior in priorities:
                demands = list(week_demand[week][prior].keys())

                while len(demands)> 0:
                    d = random.choice(demands)
                    vacat_id = week_demand[week][prior][d]['vacat_id']
                    pack_type_id = week_demand[week][prior][d]['pack_type_id']
                    dkg = week_demand[week][prior][d]['kg_rem']
                    preference = week_demand[week][prior][d]['preference']
                    exclude = week_demand[week][prior][d]['exclude']

                    try:
                        hes = list(week_he[week][vacat_id].keys())

                        if len(preference) > 0:
                            preference = [i for i in preference if i in hes]
                            hes = [i for i in hes if i not in preference]
                            hes = preference + hes
                            pref = True

                        else:
                            pref = False

                        if len(exclude) > 0:
                            hes = [x for x in hes if x not in exclude]

                    except:
                        break

                    while dkg > 0:                   
                        if len(hes) > 0:

                            if pref:
                                he = hes[0]

                            else:
                                he = random.choice(hes)
                            
                            block_id = week_he[week][vacat_id][he]['block_id']
                            he_kg_rem = week_he[week][vacat_id][he]['kg_rem']

                            # Calculate kg potential that can be packed
                            if he_kg_rem > dkg:
                                to_pack = dkg

                            else:
                                to_pack = he_kg_rem
                                
                            try:
                                sites_available = list(week_pc[week][pack_type_id].keys())

                            except:
                                pass
                            
                            while to_pack > 0:
                                if len(sites_available) > 0:
                                    sites_ft = from_to[block_id]
                                    siteav = [x for x in sites_ft if x[0] in sites_available]

                                    if len(siteav) > 0:
                                        sortedl = sorted(siteav, key=itemgetter(1))
                                        s = sortedl[0][0]
                                        km = sortedl[0][1]

                                        pc = week_pc[week][pack_type_id][s]['pc_id']
                                        pckg_rem = week_pc[week][pack_type_id][s]['kg_rem']

                                        if pckg_rem > to_pack:
                                            packed = to_pack
                                            pckg_rem = pckg_rem - to_pack
                                            to_pack = 0
                                            week_pc[week][pack_type_id][s]['kg_rem'] = pckg_rem

                                        else:
                                            packed = pckg_rem
                                            to_pack = to_pack - pckg_rem
                                            pckg_rem = 0
                                            del week_pc[week][pack_type_id][s]
                                            
                                            
                                        # Update demand tables with updated capacity
                                        he_kg_rem=he_kg_rem-packed
                                        week_he[week][vacat_id][he]['kg_rem'] = he_kg_rem
                                        
                                        sites_available.remove(s)
                                        
                                        dkg = dkg - packed

                                        genes.append([week, d, he, pc, packed, packed*km])

                                    else:
                                        break                                   

                                else:
                                    break

                            hes.remove(he)
                            if week_he[week][vacat_id][he]['kg_rem'] < 10:
                                del week_he[week][vacat_id][he]
                                
                        else:
                            genes.append([week, d, 0, 0, 0, 0])
                            
                            break

                    demands.remove(d)  

        individualdf = pd.DataFrame(genes, columns=['time_id', 'demand_id', 'he', 'pc', 'kg', 'kgkm'])
        individualdf = individualdf.reset_index(drop=True)

        return individualdf

    def make_fitness(self, individualdf):
        self.logger.debug('-> make_fitness')
        options = ImportOptions()

        individualdf1 = individualdf.copy()

        ddf_metadata = options.demand_metadata_df()
        ddf_metadata.rename(columns={'kg':'dkg'},inplace=True)

        individualdf1['kg2'] = 0
        individualdf1.loc[(individualdf1['kgkm']>0), 'kg2'] = individualdf1['kg']
        total_cost = individualdf1.kgkm.sum() / individualdf1.kg2.sum()


        individualdf2 = individualdf.groupby('demand_id', sort=False)['kg'].sum()
        individualdf2 = individualdf2.reset_index(drop=False)

        
        individualdf3 = pd.merge(ddf_metadata, individualdf2, how='left', \
                            left_on='id', right_on='demand_id')
        individualdf3['kg'].fillna(0, inplace=True)

        individualdf3['deviation'] =  individualdf3['dkg']-individualdf3['kg']
        individualdf3.loc[(individualdf3['deviation'] < 0), 'deviation'] == 0
        
        total_dev = individualdf3.deviation.sum()

        return [[total_cost, total_dev]]


class Population:
    """ Class to generate a population of solutions. """
    logger = logging.getLogger(f"{__name__}.Population")
    indv = Individual()
    graph = Visualize()

    def population(self, size, alg_path):
        self.logger.debug(f"population ({size})")
        pop=pd.DataFrame()
        fitness_df=pd.DataFrame()
        
        for i in range(size):
            ind = self.indv.individual(i, alg_path)
            pop = pd.DataFrame.from_dict(ind[0], orient='index', columns=['obj1','obj2'])
            fitness_df = pd.concat([fitness_df, pop])

        fitness_df['population'] = 'population'
        fitness_df['id'] = fitness_df.index

        return fitness_df    


class GeneticAlgorithmGenetics:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmGenetics")
    ix = Individual()
    options = ImportOptions()
    t=Tests()

    def selection(self, fitness_df, alg_path, test, population):

        if config.SELECTION == 'tournament':
            parent_df=self.tournament_selection(fitness_df, alg_path, test, population)

        if config.SELECTION == 'nondom':
            parent_df=self.nondom_selection(fitness_df, alg_path, test, population)

        return parent_df 

    def tournament_selection(self, fitness_df, alg_path, test, population):
        """ 
        GA: choose parents to take into crossover
        
        """
        self.logger.debug(f"--- tournament_selection")
        fitness_df=fitness_df[fitness_df['population']!='none'].reset_index(drop=True)
        #fitness_df=fitness_df[fitness_df['front']==1].reset_index(drop=True)

        high_fit1 = np.inf 
        high_fit2 = np.inf 

        objs1 = fitness_df.obj1.values
        objs2 = fitness_df.obj2.values
        ids = fitness_df.id.values

        for _ in range(config.TOURSIZE):
            option_num = random.randint(0,len(fitness_df)-1)

            option_id = ids[option_num]
            fit1 = objs1[option_num]
            fit2 = objs2[option_num]

            #if self.dominates((fit1, fit2), (high_fit1, high_fit2)):
            if ((fit1 <= high_fit1 and fit2 <= high_fit2) and (fit1 < high_fit1 or fit2 < high_fit2)):  
                high_fit1 = fit1
                high_fit2 = fit2
                parent = option_id
            
        
        parent_path=os.path.join(alg_path, f"id_{option_id}")
        parent_df = pd.read_pickle(parent_path)
        #parent_df = pd.read_json(parent_path, orient='index')


        parent_df = parent_df.sort_values(by=['time_id'])
                
        return parent_df

    def nondom_selection(self, pareto_set, alg_path, test, population):
        """This selection method makes use of the nondominated soting front to choose 
        parents.

        NB: Only for NSGA-II. Moga etc has different structure.  
        NB: Tests = DICT, Real = DATAFRAME
        """
        option_num = random.randint(0,len(pareto_set)-1)
        option_id = pareto_set[option_num]
        
        if test:
            parent = population[option_id]

        else:
            parent_path=os.path.join(alg_path, f"id_{option_id}")
            parent = pd.read_pickle(parent_path)

        return parent

    def mutation(self, df_mutate, times, test, test_name=''):
        """ GA mutation function to diversify gene pool. """
        
        self.logger.debug(f"-- mutation check")
        #ix = Individual()

        if random.random() <= config.MUTATIONRATE:
            self.logger.debug(f"--- mutation activated")
                       
            if test:
                times = df_mutate.keys()

                for m in times:
                    self.logger.debug(f"---- mutation for {m}")

                    if random.random() < config.MUTATIONRATE2:
                        if test_name == 'zdt5':
                            df_mutate = self.t.ZDT5_mutate(df_mutate, m)
                        
                        else:
                            df_mutate[m] = np.random.rand()
            
            else:
                times.sort()
                df_mutate=df_mutate.sort_values(by=['time_id']).reset_index(drop=True)
                df_mutate1=pd.DataFrame()
                mutates = []
                for m in times:
                    self.logger.debug(f"---- mutation for {m}")
                    update = True

                    if random.random() < config.MUTATIONRATE2:
                        update = False
                        #df_gener =  df_mutate[df_mutate['time_id']==m]
                        #demand_list = list(df_gener.demand_id.unique())
                        df_gene = self.ix.make_individual(get_dlist=False, dlist=m)
                        df_mutate1 = pd.concat([df_mutate1, df_gene]).reset_index(drop=True)
                
                    mutates.append([update, m])

                mutated = pd.DataFrame(data=mutates, columns=['mutate', 'time_id'])
                df_mutate = pd.merge(df_mutate, mutated, on=['time_id'], how='left')
                df_keep = df_mutate[df_mutate["mutate"]]
                
                df_mutate = pd.concat([df_mutate1, df_keep]).reset_index(drop=True)
                df_mutate=df_mutate.drop(columns=['mutate'])

        return df_mutate

    def crossover_BITFLIP(self, pareto_set, ids, alg_path, test, test_name, population, times):
        """ GA crossover genetic material for diversification"""
        self.logger.debug(f"2. crossover start")

        fitness = {}
        # Select parents with tournament
        parent1 = self.selection(pareto_set, alg_path, test, population)
        parent2 = self.selection(pareto_set, alg_path, test, population)

        if test:
            times = parent1.keys()
            child1 = {}
            child2 = {}
            for _ in times:
                if random.random() < config.CROSSOVERRATE:
                    child1[_] = parent2[_]
                    child2[_] = parent1[_]

                else:
                    child1[_] = parent1[_]
                    child2[_] = parent2[_]
        else:
            #times = list(parent1.time_id.unique()) 
            #week_demand = self.options.easy_demand() 
            #times =  list(week_demand.keys())
            #print(times)       
            crossover = []      
            for _ in times:
                if random.random() < config.CROSSOVERRATE:
                    crossover.append([True, _])
                
                else:
                    crossover.append([False, _])
                    
            crossoverd = pd.DataFrame(data=crossover, columns=['crossover', 'time_id'])
            parent1 = pd.merge(crossoverd, parent1, on=['time_id'], how='left')
            parent2 = pd.merge(crossoverd, parent2, on=['time_id'], how='left')

            child1a = parent1[parent1["crossover"]]
            child1b = parent1[~parent1["crossover"]]
            child2a = parent2[parent2["crossover"]]
            child2b = parent2[~parent2["crossover"]]

            child1 = pd.concat([child1a, child2b]).reset_index(drop=True)
            child2 = pd.concat([child1b, child2a]).reset_index(drop=True)

            child1=child1.drop(columns=['crossover'])
            child2=child2.drop(columns=['crossover'])

        # If test then make new test individual gene
        if test:
            # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=test, test_name=test_name)
            child2 = self.mutation(child2, times, test=test, test_name=test_name)

            # Register child on fitness_df
            child1_id = self.ix.individual(ids[0], alg_path, get_indiv=False, indiv=child1, 
                            test=test, test_name=test_name)
            child2_id = self.ix.individual(ids[1], alg_path, get_indiv=False, indiv=child2, 
                            test=test, test_name=test_name) 
            
            population[ids[0]] = child1_id[1]
            population[ids[1]] = child2_id[1]

            fitness[ids[0]] = child1_id[0][ids[0]]
            fitness[ids[1]] = child2_id[0][ids[1]]

        else:
           # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=False)
            child2 = self.mutation(child2, times, test=False)

            # Register child on fitness_df
            child1_id = self.ix.individual(ids[0], alg_path, get_indiv=False, indiv=child1)
            child2_id = self.ix.individual(ids[1], alg_path, get_indiv=False, indiv=child2)

            #fitness = pd.concat([fitness, child1_f, child2_f]).reset_index(drop=True)
            fitness[ids[0]] = child1_id[0][ids[0]]
            fitness[ids[1]] = child2_id[0][ids[1]]
        
        self.logger.debug(f"2. crossover finish")
        return fitness, population

    def make_children(self, fitness_df, alg_paths, test=False, test_name='', population={}):
        """ GA crossover genetic material for diversification"""
        self.logger.info(f" Making children")

        week_demand = self.options.easy_demand() 
        times =  list(week_demand.keys())

        used_ids = list(fitness_df.id)
        poplist = list(range(0, config.POPUATION + config.CHILDREN + 1))
        available_ids = [x for x in poplist if x not in used_ids]

        fitness = {}
        alloc_id = 0
        for _ in range(int(config.CHILDREN/2)):
            ids = [available_ids[alloc_id], available_ids[alloc_id+1]]
            crossover=self.crossover(used_ids, ids, alg_paths, times, test, test_name, population)
            fitness.update(crossover[0])
            population = crossover[1]

            alloc_id = alloc_id + 2

        fitness_dft = pd.DataFrame.from_dict(fitness, orient='index', columns=['obj1','obj2'])
        fitness_dft['id'] = fitness_dft.index
        fitness_df = pd.concat([fitness_df, fitness_dft])

        return fitness_df, population

    def crossover_CROSSGEN(self, fitness_df, ids, alg_path, test, test_name, population):
        """ GA crossover genetic material for diversification
        # TODO: If you want to use UPDATE TO FIT DATASTRUCTURES as in bitflip
        """
        self.logger.debug(f"-- crossover_CROSSGEN")

        ix = Individual()
        pareto_set = list(fitness_df.id)

        # Select parents with tournament
        parent1 = self.selection(pareto_set, alg_path, population)
        parent2 = self.selection(pareto_set, alg_path, population)

        times = list(parent1.time_id.unique())      
        r = random.randint(0, len(times)-1)
        crossover = ([True] * r) + ([False] * (len(times)-r))
        
        crossoverd = pd.DataFrame({'crossover':crossover, 'time_id':times})

        if test:
            parent1.set_index('time_id')
            parent2.set_index('time_id')
            crossoverd.set_index('time_id', inplace=True)

            parent1 = parent1.join(crossoverd, how='left')
            parent2 = parent2.join(crossoverd, how='left')

        else:
            parent1 = pd.merge(parent1, crossoverd, on=['time_id'], how='left')
            parent2 = pd.merge(parent2, crossoverd, on=['time_id'], how='left')


        child1a = parent1[parent1["crossover"]] # new
        child1b = parent1[~parent1["crossover"]] # new
        child2a = parent2[parent2["crossover"]] # new
        child2b = parent2[~parent2["crossover"]] # new

        child1 = pd.concat([child1a,child2b])
        child2 = pd.concat([child1b,child2a])

        child1=child1.drop(columns=['crossover'])
        child2=child2.drop(columns=['crossover'])

        if test:
            # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=test)
            child2 = self.mutation(child2, times, test=test)

            # Register child on fitness_df
            child1_f = ix.individual(ids[0], alg_path, get_indiv=False, indiv=child1, 
                            test=test, test_name=test_name)
            child2_f = ix.individual(ids[1], alg_path, get_indiv=False, indiv=child2, 
                            test=test, test_name=test_name) 

        else:
           # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=False)
            child2 = self.mutation(child2, times, test=False)

            # Register child on fitness_df
            child1_f = ix.individual(ids[0], alg_path, get_indiv=False, indiv=child1)
            child2_f = ix.individual(ids[1], alg_path, get_indiv=False, indiv=child2)

        child1_f['population'] = 'child'
        child2_f['population'] = 'child'

        fitness_df = pd.concat([fitness_df, child1_f, child2_f]).reset_index(drop=True)
        return fitness_df

    def crossover(self, fitness_df, ids, alg_path, times, test=False, test_name='zdt1', population={}):
        if config.CROSSOVERTYPE == 'crossover_BITFLIP':
            new_life=self.crossover_BITFLIP(fitness_df, ids, alg_path, test, test_name, population, times)
            fitness_df = new_life[0]
            population = new_life[1]

        #if config.CROSSOVERTYPE == 'crossover_CROSSGEN':
        #    fitness_df=self.crossover_CROSSGEN(fitness_df, ids, alg_path, test, test_name, population)

        return fitness_df, population

    def get_domcount(self, fitness_df):
        front1 = []

        dominating_fits = [0] * len(fitness_df)  # n (The number of people that dominate you)
        dominated_fits = defaultdict(list)  # Sp (The people you dominate)
        
        fits = list(fitness_df.id)
        obj1s = fitness_df['obj1'].values
        obj2s = fitness_df['obj2'].values
        for i, id in enumerate(fits):
            obj1 = obj1s[i]
            obj2 = obj2s[i]

            for ix, idx in enumerate(fits[i + 1:]):
                obj1x = obj1s[i + ix + 1]
                obj2x = obj2s[i + ix + 1]
                
                if (obj1 <= obj1x and obj2 < obj2x):
                    dominating_fits[i + ix + 1] += 1 
                    dominated_fits[id].append(idx) 

                elif (obj1 >= obj1x and obj2 > obj2x):
                    dominating_fits[i] += 1
                    dominated_fits[idx].append(id)    

                elif (obj1 == obj1x and obj2 == obj2x):
                    # prevent duplicates
                    dominating_fits[i + ix + 1] += 100
                    #dominated_fits[idx].append(id) 

            if dominating_fits[i] == 0:
                front1.append(id)

        return front1

    def crossover_BITFLIP_DEPRICATE(self, fitness_df, ids, alg_path, test, test_name, population):
        """ GA crossover genetic material for diversification"""
        self.logger.debug(f"2. crossover start")

        pareto_set = list(fitness_df.id)
        pareto_set = list(fitness_df.id)

        # Select parents with tournament
        parent1 = self.selection(pareto_set, alg_path, test, population)
        parent2 = self.selection(pareto_set, alg_path, test, population)

        if test:
            times = parent1.keys()
            child1 = {}
            child2 = {}
            for _ in times:
                if random.random() < config.CROSSOVERRATE:
                    child1[_] = parent2[_]
                    child2[_] = parent1[_]

                else:
                    child1[_] = parent1[_]
                    child2[_] = parent2[_]
        else:
            times = list(parent1.time_id.unique())          
            
            crossover = []      
            for _ in times:
                if random.random() < config.CROSSOVERRATE:
                    crossover.append([True, _])
                
                else:
                    crossover.append([False, _])
                    
            crossoverd = pd.DataFrame(data=crossover, columns=['crossover', 'time_id'])
            parent1 = pd.merge(parent1, crossoverd, on=['time_id'], how='left')
            parent2 = pd.merge(parent2, crossoverd, on=['time_id'], how='left')

            child1a = parent1[parent1["crossover"]]
            child1b = parent1[~parent1["crossover"]]
            child2a = parent2[parent2["crossover"]]
            child2b = parent2[~parent2["crossover"]]

            child1 = pd.concat([child1a,child2b])
            child2 = pd.concat([child1b,child2a])

            child1=child1.drop(columns=['crossover'])
            child2=child2.drop(columns=['crossover'])

        self.logger.debug(f"--- crossover 2")

        # If test then make new test individual gene
        if test:
            # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=test)
            child2 = self.mutation(child2, times, test=test)

            # Register child on fitness_df
            child1_id = self.ix.individual(ids[0], alg_path, get_indiv=False, indiv=child1, 
                            test=test, test_name=test_name)
            child2_id = self.ix.individual(ids[1], alg_path, get_indiv=False, indiv=child2, 
                            test=test, test_name=test_name) 
            
            child1_f = child1_id[0]
            child2_f = child2_id[0]

            population[ids[0]] = child1_id[1]
            population[ids[1]] = child2_id[1]

        else:
           # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=False)
            child2 = self.mutation(child2, times, test=False)

            # Register child on fitness_df
            child1_f = self.ix.individual(ids[0], alg_path, get_indiv=False, indiv=child1)[0]
            child2_f = self.ix.individual(ids[1], alg_path, get_indiv=False, indiv=child2)[0]


        fitness_df = pd.concat([fitness_df, child1_f, child2_f]).reset_index(drop=True)
        self.logger.debug(f"2. crossover finish")
        return fitness_df, population

    def get_domcount_DEPRICATED(self, fitness_df):
        front1 = []

        #fitness_df = fitness_df.sort_values(by=['id']).reset_index(drop=True)
        fits = list(fitness_df.id)

        fitness_df['population'] = 'none'
        fitness_df['domcount'] = 0 

        dominating_fits = [0] * len(fitness_df)  # n (The number of people that dominate you)
        dominated_fits = defaultdict(list)  # Sp (The people you dominate)
        
        fitness_df=fitness_df.set_index('id')
        fitness_df['id'] = fitness_df.index

        obj1s = fitness_df['obj1'].values
        obj2s = fitness_df['obj2'].values
        for i, id in enumerate(fits):
            obj1 = obj1s[i]
            obj2 = obj2s[i]

            for ix, idx in enumerate(fits[i + 1:]):
                obj1x = obj1s[i + ix + 1]
                obj2x = obj2s[i + ix + 1]
                
                #if build_features.GeneticAlgorithmGenetics.dominates((obj1, obj2), (obj1x, obj2x)):
                if (obj1 <= obj1x and obj2 < obj2x):
                    dominating_fits[i + ix + 1] += 1 
                    dominated_fits[id].append(idx) 

                #if build_features.GeneticAlgorithmGenetics.dominates((obj1x, obj2x), (obj1, obj2)):
                if (obj1 >= obj1x and obj2 > obj2x):
                    dominating_fits[i] += 1
                    dominated_fits[idx].append(id)    

            if dominating_fits[i] == 0:
                front1.append(id)

        fitness_df['domcount'] = dominating_fits
        fitness_df.loc[(fitness_df.domcount==0), 'front'] = 1
        return fitness_df

    def mutation_20220904(self, df_mutate, times, test):
        """ GA mutation function to diversify gene pool. """
        
        self.logger.debug(f"-- mutation check")
        ix = Individual()

        if random.random() <= config.MUTATIONRATE:
            self.logger.debug(f"--- mutation activated")
                       
            times.sort()
            df_mutate=df_mutate.sort_values(by=['time_id']).reset_index(drop=True)

            df_mutate1=pd.DataFrame()
            mutates = []
            for m in times:
                self.logger.debug(f"---- mutation for {m}")
                update = True

                if random.random() < config.MUTATIONRATE2:
                    update = False
                    
                    # If test then make new gene here
                    if test:
                        x = np.random.rand()
                        df_gene = pd.DataFrame(data=[x], columns=['value'])
                        df_gene['time_id'] = m
                        df_mutate1 = pd.concat([df_mutate1, df_gene]).reset_index(drop=True)
                    
                    # Else get only gene alternate
                    else: 
                        df_gener =  df_mutate[df_mutate['time_id']==m]
                        demand_list = list(df_gener.demand_id.unique())
                        df_gene = ix.make_individual(get_dlist=False, dlist=demand_list)
                        df_mutate1 = pd.concat([df_mutate1, df_gene]).reset_index(drop=True)
                        
                mutates.append([update, m])
                
            mutated = pd.DataFrame(data=mutates, columns=['mutate', 'time_id'])
            df_mutate = pd.merge(df_mutate, mutated, on=['time_id'], how='left')
            df_keep = df_mutate[df_mutate["mutate"]]
            
            df_mutate1 = pd.concat([df_mutate1, df_keep]).reset_index(drop=True)
            df_mutate1=df_mutate1.drop(columns=['mutate'])

        else:
            df_mutate1 = df_mutate

        return df_mutate1


class ParetoFeatures:
    """ Class to manage pareto front """
    logger = logging.getLogger(f"{__name__}.ParetoFeatures")

    def non_dominated_sort(self, fitness_df):
        dominating_fits = defaultdict(int)  # n (The number of people that dominate you)
        dominated_fits = defaultdict(list)  # Sp (The people you dominate)

        fitness_df=fitness_df.groupby(['obj1', 'obj2', 'population'])['id'].min().reset_index(drop=False)
        fitness_df['domcount'] = 0
        fits = list(fitness_df.id)
        fitness_df.set_index("id", inplace = True)
        fitness_df['id'] = fitness_df.index
        
        for i, id in enumerate(fits):
            obj1 = fitness_df.at[id, 'obj1']
            obj2 = fitness_df.at[id, 'obj2']

            for idx in fits[i + 1:]:
                obj1x = fitness_df.at[idx, 'obj1']
                obj2x = fitness_df.at[idx, 'obj2']
                
                if (obj1 <= obj1x and obj2 <= obj2x) and (obj1 < obj1x or obj2 < obj2x):
                    dominating_fits[idx] += 1 
                    fitness_df.at[idx, 'domcount'] += 1
                    dominated_fits[id].append(idx) 
 
                if (obj1x <= obj1 and obj2x <= obj2) and (obj1x < obj1 or obj2x < obj2):
                    dominating_fits[id] += 1
                    fitness_df.at[id, 'domcount'] += 1
                    dominated_fits[idx].append(id)    

            if dominating_fits[id] == 0:
                fitness_df.loc[(fitness_df.index==id), 'front'] = 1

        return fitness_df

    def calculate_hyperarea_DEPRICATED(self, fitness_df):
        """
        Calculate the area under the pareto front
        relative to the min of each objective
        """

        fitness_df = fitness_df.filter(['id', 'obj1', 'obj2', 'population'])

        sets = ['yes', 'pareto']
        hyperarea = pd.DataFrame()

        #ref_obj2 = fitness_df.obj2.min()
        #ref_obj1 = fitness_df.obj1.min()
        #ref_obj2 = 0
        #ref_obj1 = 0

        for set in sets:
            set_df = fitness_df[fitness_df['population'] == set]
            
            df = self.non_dominated_sort(set_df)
            df = df[df['front'] == 1].reset_index(drop=True)
            df = df.sort_values(by=['obj1','obj2'], ascending=[True,False]).reset_index(drop=True)

            name = df.population[0]

            #ref_obj2 = df.obj2.min()
            ref_obj2 = 0
            ref_obj1 = df.obj1.min()

            prev_obj2 = ref_obj2
            prev_obj1 = ref_obj1

            area = 0
            for i in range(1, len(df) - 1):
                
                objective1 = df.obj1[i]
                objective2 = df.obj2[i]

                print(f"{i} - {objective1} - {objective2}")

                objective1_diff = abs(objective1 - prev_obj1)
                objective2_diff = abs(objective2 - prev_obj2)
                area = area + (objective1_diff * objective2_diff)      

                #prev_obj2 = 0
                prev_obj1 = objective1

            #print(f"{name}: {area}")
            temp = pd.DataFrame(data=[(name, area)],
                    columns=['population', 'hyperarea'])

            hyperarea=pd.concat([hyperarea, temp]).reset_index(drop=True)

        return hyperarea

    def calculate_hyperarea_BEKKER(self, fitness_df):
        """
        Calculate the area under the pareto front
        relative to the min of each objective
        """
        fitness_df = fitness_df.filter(['id', 'obj1', 'obj2', 'population'])

        sets = ['yes', 'pareto']
        hyperarea = pd.DataFrame()

        for set in sets:
            set_df = fitness_df[fitness_df['population'] == set]
            
            df = self.non_dominated_sort(set_df)
            df = df[df['front'] == 1].reset_index(drop=True)
            df = df.sort_values(by=['obj1','obj2'], ascending=[True,False]).reset_index(drop=True)

            objs1 = df.obj1.values
            objs2 = df.obj2.values
            ids = df.id.values
            area = 0
            for count, id in enumerate(ids):

                if (count == 0 or count == (len(ids)-1)):
                    continue

                else:
                    objective1_diff = abs(objs1[count] - objs1[count - 1])
                    #objective2_diff = abs(objs2[count] - objs2[count - 1])
                    
                    #area = area + (objective1_diff * objective2_diff)
                    area = area + (objective1_diff * objs2[count])

            temp = pd.DataFrame(data=[(set, area)],
                    columns=['population', 'hyperarea'])

            hyperarea=pd.concat([hyperarea, temp]).reset_index(drop=True)

        print(hyperarea)
        return hyperarea

    def calculate_hyperarea(self, fitness_df):
        """
        Calculate the area under the pareto front
        relative to the min of each objective
        """
        fitness_df = fitness_df.filter(['id', 'obj1', 'obj2', 'population'])

        sets = ['yes', 'pareto']
        sets = list(fitness_df['population'].unique())
        hyperarea = pd.DataFrame()

        for set in sets:
            set_df = fitness_df[fitness_df['population'] == set]
            
            df = self.non_dominated_sort(set_df)
            #df = df[df['front'] >= 1].reset_index(drop=True)
            df = df.sort_values(by=['obj1','obj2'], ascending=[True,False]).reset_index(drop=True)

            objs1 = df.obj1.values
            objs2 = df.obj2.values
            ids = df.id.values
            area = 0
            for count, id in enumerate(ids):

                if (count == 0):
                    objective1_diff = objs1[count]
                    objective2_diff = objs2[count]

                else:
                    objective2_diff = objs2[count]
                    objective1_diff = abs(objs1[count] - objs1[count - 1])
                    #objective2_diff = abs(objs2[count] - objs2[count - 1])
                    
                area = area + (objective1_diff * objective2_diff)


            temp = pd.DataFrame(data=[(set, area)],
                    columns=['population', 'hyperarea'])

            hyperarea=pd.concat([hyperarea, temp]).reset_index(drop=True)

        #print(hyperarea)
        return hyperarea


class PrepManPlan:
    """ Class to prepare Manual PackPlan for comparison"""
    logger = logging.getLogger(f"{__name__}.PrepManPlan")

    database_instance = DatabaseModelsClass('PHDDATABASE_URL')
    indiv = Individual()
    graph = Visualize()

    def clear_old_result(self, plan_date, alg=''):
        self.logger.info(f"clear old data tables (sol_fitness & sol_pareto_individuals)")

        if alg != '':
            sql1=f"""
            DELETE FROM `dss`.`sol_fitness` WHERE (`alg` = '{alg}' AND `plan_date`='{plan_date}');
            """
            sql2=f"""
            DELETE FROM `dss`.`sol_pareto_individuals` WHERE (`alg` = '{alg}' AND `plan_date`='{plan_date}');
            """
            sql3=f"""
            DELETE FROM `dss`.`sol_kobus_plan` WHERE (`plan_date`='{plan_date}');
            """
            sql4=f"""
            DELETE FROM `dss`.`sol_actual_plan` WHERE (`plan_date`='{plan_date}');
            """

        else:
            sql1=f"""
            DELETE FROM `dss`.`sol_fitness`;
            """
            sql2="""
            DELETE FROM `dss`.`sol_pareto_individuals`;
            """
            sql3=f"""
            DELETE FROM `dss`.`sol_kobus_plan`;
            """
            sql4=f"""
            DELETE FROM `dss`.`sol_actual_plan`;
            """

        self.database_instance.execute_query(sql1)
        self.database_instance.execute_query(sql2)
        self.database_instance.execute_query(sql3)
        self.database_instance.execute_query(sql4)

        return

    def prep_results(self, alg_path, fitness_df, init_pop, plan_date, week_str):
        """function to convert final pareto front to sql data 
            here with manplan and actual"""

        self.logger.info(f"prepare results and send to sql")

        if 'vega' in alg_path:
            alg='vega'

        if 'nsga2' in alg_path:
            alg='nsga2'

        if 'moga' in alg_path:
            alg='moga'
        
        self.clear_old_result(plan_date, alg)

        pareto_indivs = list(fitness_df.id)
        popdf=pd.DataFrame()
        for id in pareto_indivs:
            path=os.path.join(alg_path,f"id_{id}")
            infile = open(path,'rb')
            individualdf = pickle.load(infile)
            infile.close()
            individualdf['indiv_id'] = id
            popdf=popdf.append(individualdf).reset_index(drop=True)

        popdf['alg'] = alg
        popdf['plan_date'] = plan_date

        kobus_plan = self.kobus_plan(plan_date, week_str)
        
        kobus_fit = self.indiv.individual(1000000, 
                    alg_path = alg_path, 
                    get_indiv=False, 
                    indiv=kobus_plan, 
                    test=False)
        kobus_fit = pd.DataFrame.from_dict(kobus_fit[0], orient='index', columns=['obj1','obj2'])
        kobus_fit['id'] = kobus_fit.index
        print(kobus_fit)

        kobus_fit['population'] = 'manplan'
        kobus_fit['result'] = 'manplan'

        init_pop['result'] = 'init pop'
        fitness_df['result'] = 'final result'
        
        fitness_df = pd.concat([fitness_df, init_pop, kobus_fit])
        print(fitness_df)
   
        fitness_df['alg'] = alg
        fitness_df['plan_date'] = plan_date
        kobus_plan['plan_date'] = plan_date

        fitness_df = fitness_df.rename(columns={"id": "indiv_id"})
        fitness_df = fitness_df[['indiv_id', 'obj1', 'obj2', 
                'population', 'result', 'alg', 'plan_date']]
        
        self.database_instance.insert_table(fitness_df, 'sol_fitness', 'dss', if_exists='append')
        self.database_instance.insert_table_chunks(popdf, 'sol_pareto_individuals', 'dss', if_exists='append', chunk_size=5000)
        self.database_instance.insert_table(kobus_plan, 'sol_kobus_plan', 'dss', if_exists='append')
        
        return

    def kobus_plan(self, plan_date, week_str):

        if config.LEVEL == 'DAY':
            sql_query = f"""
                SELECT f_demand_plan.id as demand_id
                        , f_pack_capacity.id as pc
                        , dim_fc.id as fc_id
                        , dim_va.id as va_id
                        , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_kg * -1) / dim_week.workdays)  * dim_time.workday), 0)  as kg
                        , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_standardctns * -1) / dim_week.workdays)  * dim_time.workday), 0)  as stdunits
                        -- , (pd.qty_kg * -1) as kg
                        -- , (pd.qty_standardctns * -1) as stdunits
                        , distance.km
                        -- , (pd.qty_kg * -1) * distance.km as 'kgkm'
                        , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_kg * -1) / dim_week.workdays)  * dim_time.workday), 0) * distance.km as 'kgkm'
                        , 12 as speed
                FROM dss.planning_data pd
                LEFT JOIN dim_fc ON (pd.grower = dim_fc.name)
                LEFT JOIN dim_packhouse ON (pd.packsite = dim_packhouse.name)
                LEFT JOIN (SELECT id, upper(name) as name FROM dss.dim_pack_type) pack_type  
                    ON (pd.format = pack_type.name)
                LEFT JOIN dim_va ON (pd.variety = dim_va.name)
                LEFT JOIN dim_week ON (pd.packweek = dim_week.week)
                LEFT JOIN (SELECT f_from_to.packhouse_id, f_from_to.fc_id, AVG(f_from_to.km) as km
                                FROM dss.f_from_to
                                GROUP BY f_from_to.packhouse_id, f_from_to.fc_id) distance 
                                ON (distance.packhouse_id = dim_packhouse.id 
                                    AND distance.fc_id = dim_fc.id)
                LEFT JOIN f_pack_capacity
                    ON (f_pack_capacity.packhouse_id = dim_packhouse.id 
                        AND f_pack_capacity.pack_type_id = pack_type.id
                        AND f_pack_capacity.packweek = dim_week.week
                        AND f_pack_capacity.plan_date ='{plan_date}')
                LEFT JOIN f_demand_plan
                    ON (pd.demandid = f_demand_plan.demand_id
                        AND f_demand_plan.plan_date ='{plan_date}')
                LEFT JOIN dim_time 
                    ON (dim_time.week = pd.packweek
                        AND weekday(dim_time.day) = f_pack_capacity.weekday)
                WHERE recordtype = 'PLANNED'
                AND dim_fc.packtopackplans=1
                AND extract_datetime = (SELECT MAX(extract_datetime) 
                    FROM dss.planning_data WHERE date(extract_datetime)='{plan_date}')
                AND f_pack_capacity.stdunits is not null
                AND pd.packweek in ({week_str})
                ;
            """
        
        else:
            sql_query = f"""
                SELECT f_demand_plan.id as demand_id
                        , f_pack_capacity.id as pc
                        , dim_fc.id as fc_id
                        , dim_va.id as va_id
                        -- , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_kg * -1) / dim_week.workdays)  * dim_time.workday), 0)  as kg
                        -- , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_standardctns * -1) / dim_week.workdays)  * dim_time.workday), 0)  as stdunits
                        , (pd.qty_kg * -1) as kg
                        , (pd.qty_standardctns * -1) as stdunits
                        , distance.km
                        , (pd.qty_kg * -1) * distance.km as 'kgkm'
                        -- , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_kg * -1) / dim_week.workdays)  * dim_time.workday), 0) * distance.km as 'kgkm'
                        , 12 as speed
                FROM dss.planning_data pd
                LEFT JOIN dim_fc ON (pd.grower = dim_fc.name)
                LEFT JOIN dim_packhouse ON (pd.packsite = dim_packhouse.name)
                LEFT JOIN (SELECT id, upper(name) as name FROM dss.dim_pack_type) pack_type  
                    ON (pd.format = pack_type.name)
                LEFT JOIN dim_va ON (pd.variety = dim_va.name)
                LEFT JOIN dim_week ON (pd.packweek = dim_week.week)
                LEFT JOIN (SELECT f_from_to.packhouse_id, f_from_to.fc_id, AVG(f_from_to.km) as km
                                FROM dss.f_from_to
                                GROUP BY f_from_to.packhouse_id, f_from_to.fc_id) distance 
                                ON (distance.packhouse_id = dim_packhouse.id 
                                    AND distance.fc_id = dim_fc.id)
                LEFT JOIN f_pack_capacity
                    ON (f_pack_capacity.packhouse_id = dim_packhouse.id 
                        AND f_pack_capacity.pack_type_id = pack_type.id
                        AND f_pack_capacity.packweek = dim_week.week
                        AND f_pack_capacity.plan_date ='{plan_date}')
                LEFT JOIN f_demand_plan
                    ON (pd.demandid = f_demand_plan.demand_id
                        AND f_demand_plan.plan_date ='{plan_date}')
                -- LEFT JOIN dim_time 
                --    ON (dim_time.week = pd.packweek
                --        AND weekday(dim_time.day) = f_pack_capacity.weekday)
                WHERE recordtype = 'PLANNED'
                AND dim_fc.packtopackplans=1
                AND extract_datetime = (SELECT MAX(extract_datetime) 
                    FROM dss.planning_data WHERE date(extract_datetime)='{plan_date}')
                AND f_pack_capacity.stdunits is not null
                AND pd.packweek in ({week_str})
                ;
            """            
        
        df = self.database_instance.select_query(query_str=sql_query)
        df['packhours'] = df['kg']*(1*config.GIVEAWAY)*df['speed']/60 

        return df

    def actual(self, plan_date, week_str):
        if config.LEVEL == 'DAY':
            sql_query = f"""
                SELECT pd.demandid as demand_id
                        , f_pack_capacity.id as pc
                        , dim_fc.id as fc_id
                        -- , dim_packhouse.id as packhouse_id
                        -- , dim_week.id as time_id
                        -- , pack_type.id as pack_type_id
                        , dim_va.id as va_id
                        , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_kg * -1) / dim_week.workdays)  * dim_time.workday), 0)  as kg
                        , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_standardctns * -1) / dim_week.workdays)  * dim_time.workday), 0)  as stdunits
                        -- , (pd.qty_kg * -1) as kg
                        -- , (pd.qty_standardctns * -1) as stdunits
                        , distance.km
                        -- , (pd.qty_kg * -1) * distance.km as 'kgkm'
                        , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_kg * -1) / dim_week.workdays)  * dim_time.workday), 0) * distance.km as 'kgkm'
                        , 12 as speed
                FROM dss.planning_data pd
                LEFT JOIN dim_fc ON (pd.grower = dim_fc.name)
                LEFT JOIN dim_packhouse ON (pd.packsite = dim_packhouse.name)
                LEFT JOIN (SELECT id, upper(name) as name FROM dss.dim_pack_type) pack_type  
                    ON (pd.format = pack_type.name)
                LEFT JOIN dim_va ON (pd.variety = dim_va.name)
                LEFT JOIN dim_week ON (pd.packweek = dim_week.week)
                LEFT JOIN (SELECT f_from_to.packhouse_id, f_from_to.fc_id, AVG(f_from_to.km) as km
                                FROM dss.f_from_to
                                GROUP BY f_from_to.packhouse_id, f_from_to.fc_id) distance 
                                ON (distance.packhouse_id = dim_packhouse.id 
                                    AND distance.fc_id = dim_fc.id)
                LEFT JOIN f_pack_capacity
                    ON (f_pack_capacity.packhouse_id = dim_packhouse.id 
                        AND f_pack_capacity.pack_type_id = pack_type.id
                        AND f_pack_capacity.packweek = dim_week.week
                        AND f_pack_capacity.plan_date ='{plan_date}')
                LEFT JOIN dim_time 
                    ON (dim_time.week = pd.packweek
                        AND weekday(dim_time.day) = f_pack_capacity.weekday)
                WHERE recordtype = '_PACKED'
                AND dim_fc.packtopackplans=1
                AND extract_datetime = (SELECT MAX(extract_datetime) 
                    FROM dss.planning_data WHERE date(extract_datetime)='{plan_date}')
                AND f_pack_capacity.stdunits is not null
                AND pd.packweek in ({week_str});
            """

        else:
            sql_query = f"""
                SELECT pd.demandid as demand_id
                        , f_pack_capacity.id as pc
                        , dim_fc.id as fc_id
                        -- , dim_packhouse.id as packhouse_id
                        -- , dim_week.id as time_id
                        -- , pack_type.id as pack_type_id
                        , dim_va.id as va_id
                        -- , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_kg * -1) / dim_week.workdays)  * dim_time.workday), 0)  as kg
                        -- , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_standardctns * -1) / dim_week.workdays)  * dim_time.workday), 0)  as stdunits
                        , (pd.qty_kg * -1) as kg
                        , (pd.qty_standardctns * -1) as stdunits
                        , distance.km
                        , (pd.qty_kg * -1) * distance.km as 'kgkm'
                        -- , if((pd.qty_kg * -1) > 0, ROUND(((pd.qty_kg * -1) / dim_week.workdays)  * dim_time.workday), 0) * distance.km as 'kgkm'
                        , 12 as speed
                FROM dss.planning_data pd
                LEFT JOIN dim_fc ON (pd.grower = dim_fc.name)
                LEFT JOIN dim_packhouse ON (pd.packsite = dim_packhouse.name)
                LEFT JOIN (SELECT id, upper(name) as name FROM dss.dim_pack_type) pack_type  
                    ON (pd.format = pack_type.name)
                LEFT JOIN dim_va ON (pd.variety = dim_va.name)
                LEFT JOIN dim_week ON (pd.packweek = dim_week.week)
                LEFT JOIN (SELECT f_from_to.packhouse_id, f_from_to.fc_id, AVG(f_from_to.km) as km
                                FROM dss.f_from_to
                                GROUP BY f_from_to.packhouse_id, f_from_to.fc_id) distance 
                                ON (distance.packhouse_id = dim_packhouse.id 
                                    AND distance.fc_id = dim_fc.id)
                LEFT JOIN f_pack_capacity
                    ON (f_pack_capacity.packhouse_id = dim_packhouse.id 
                        AND f_pack_capacity.pack_type_id = pack_type.id
                        AND f_pack_capacity.packweek = dim_week.week
                        AND f_pack_capacity.plan_date ='{plan_date}')
                -- LEFT JOIN dim_time 
                --    ON (dim_time.week = pd.packweek
                --        AND weekday(dim_time.day) = f_pack_capacity.weekday)
                WHERE recordtype = '_PACKED'
                AND dim_fc.packtopackplans=1
                AND extract_datetime = (SELECT MAX(extract_datetime) 
                    FROM dss.planning_data WHERE date(extract_datetime)='{plan_date}')
                AND f_pack_capacity.stdunits is not null
                -- AND dim_fc.packtopackplans = 1
                AND pd.packweek in ({week_str});
            """


        df = self.database_instance.select_query(query_str=sql_query)
        df['packhours'] = df['kg']*(1*config.GIVEAWAY)*df['speed']/60

        return df

