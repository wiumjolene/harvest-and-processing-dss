# -*- coding: utf-8 -*-
import datetime
import logging
import os
import pickle
import random
from collections import defaultdict

import numpy as np
import pandas as pd
from src.data.make_dataset import ImportOptions, GetLocalData
from src.features.make_tests import Tests
from src.utils import config
from src.utils.connect import DatabaseModelsClass
from src.utils.visualize import Visualize


class Individual:
    """ Class to generate an individual solution. """
    logger = logging.getLogger(f"{__name__}.Individual")
    individual_df = pd.DataFrame()
    dlistt=[]

    def individual(self,number,alg_path,get_indiv=True,indiv=individual_df,test=False,test_name='zdt1'):
        """ Function to define indiv and fitness """
        self.logger.info(f"- individual: {number}")
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

            if (len(x) < config.D or len(x) > config.D): 
                print(f"number {number}: len {len(x)}")
                exit()

        else:
            if get_indiv:
                indiv = self.make_individual()

            fitness = self.make_fitness(indiv)

        ind_fitness = pd.DataFrame(fitness, columns=['obj1', 'obj2'])
        ind_fitness['id'] = number
        
        #indiv.to_pickle(f"data/interim/{alg_path}/id_{number}", protocol = 5) 
        path=os.path.join(alg_path, f"id_{number}")
        indiv.to_pickle(path, protocol=5)
        return ind_fitness

    def make_individual(self, get_dlist=True, dlist=dlistt):
        """ Function to make problem specific individual solution """

        self.logger.debug('-> make_individual')

        # Import all data sets from pickel files.
        self.logger.debug('--> get demand options')
        options = ImportOptions()

        # Get all demands ready for allocation
        if get_dlist:
            dlist_allocate = options.demand_ready()
           
        else:  # Or use custom list
            dlist_allocate = dlist
        
        self.logger.debug('--> import options')
        ddf_he = options.demand_harvest()
        ddf_he['evaluated'] = 0
        
        ddf_pc = options.demand_capacity()
        ddic_metadata = options.demand_metadata()
        he_dic = options.harvest_estimate()
        ft_df = options.from_to()
        dic_speed = options.speed()

        individualdf = pd.DataFrame()
        self.logger.debug(f"--> loop through new dlist_allocate ({len(dlist_allocate)})")
        while len(dlist_allocate) > 0:
            self.logger.debug(f"---> get new allocation")

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
                self.logger.debug(f"----> dkg ({dkg}) for demand: {d}")
                # Filter demand_he table according to d and kg.
                # Check that combination of d_he has not yet been used.
                ddf_het = ddf_he[(ddf_he['demand_id']==d)&(ddf_he['kg_rem']>0)& \
                    (ddf_he['evaluated']==0)]
                
                dhes = ddf_het['id'].tolist()
                dhe_kg_rem = ddf_het['kg_rem'].tolist()

                self.logger.debug(f"----> get harevest estimate")
                if len(dhes) > 0:
                    # Randomly choose a he that is suitable
                    hepos = random.randint(0, len(dhes)-1)
                    he = dhes[hepos]
                    he_kg_rem = dhe_kg_rem[hepos]
                    self.logger.debug(f"-----> assign he {he}")

                    # Calculate kg potential that can be packed
                    if he_kg_rem > dkg:
                        to_pack = dkg

                    else:
                        to_pack = he_kg_rem
                    
                    self.logger.debug(f"-----> get pack capacity")
                    # Get closest pc for he from available pc's
                    block_id = he_dic[he]['block_id']
                    va_id = he_dic[he]['va_id']
                    
                    # Variables to determine speed -> add calculate the number of hours 
                    packtype_id = ddic_metadata[d]['pack_type_id']
                    ft_dft = ft_df[ft_df['block_id'] == block_id]

                    # Allocate to_pack to pack capacities
                    while to_pack > 0:
                        ddf_pct = ddf_pc[(ddf_pc['demand_id']==d) & (ddf_pc['kg_rem']>0)]
                        ddf_pct = ddf_pct.merge(ft_dft, on='packhouse_id', how='left')
                        
                        # Drop pc with no from to for block
                        ddf_pct = ddf_pct.dropna()

                        if (len(ft_dft) > 0) and (len(ddf_pct) > 0):
                            ddf_pct = ddf_pct.sort_values(['km'], ascending=True).reset_index(drop=True)

                            # Allocate closest pc to block                    
                            #pc = ddf_pct.id[0]
                            pc = ddf_pct.at[0, 'id']

                            #packhouse_id = ddf_pct.packhouse_id[0]
                            packhouse_id = ddf_pct.at[0, 'packhouse_id']

                            #km = ddf_pct.km[0]
                            km = ddf_pct.at[0, 'km']

                            #pckg_rem = ddf_pct.kg_rem[0]
                            pckg_rem = ddf_pct.at[0, 'kg_rem']

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
                            he_kg_rem=he_kg_rem-packed
                            ddf_pc.loc[(ddf_pc['id']==pc),'kg_rem']=pckg_rem
                            ddf_he.loc[(ddf_he['id']==he),'kg_rem']=he_kg_rem
                            dkg = dkg - packed

                            indd_he.append(he)
                            indd_pc.append(pc)
                            indd_kg.append(packed)
                            indd_kgkm.append(packed*km)
                            indd_hrs.append(packed*(1*config.GIVEAWAY)*speed/60)

                        else:
                            ddf_he.loc[((ddf_he['id'] == he) & (ddf_he['demand_id'] == d)), 'evaluated'] = 1
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
        self.logger.debug('-> make_fitness')
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

        # FIXME: Bring something in to account for number of changes
        #individualdf3['changes'] = individualdf3['stdunits_hour'] * individualdf3['demand_id'] 

        #total_cost = ((individualdf.packhours.sum() \
        #                + individualdf3.changes.sum())*config.ZAR_HR) \
        #                + (individualdf.kgkm.sum()*config.ZAR_KM)

        #total_cost = ((individualdf.packhours.sum()*config.ZAR_HR) \
        #                + (individualdf.kgkm.sum()*config.ZAR_KM)) / individualdf.kg.sum()

        total_cost = individualdf.kgkm.sum() / individualdf.kg.sum()

        #total_cost = ((individualdf.packhours.sum()*config.ZAR_HR) \
        #                + (individualdf.kgkm.sum()*config.ZAR_KM))

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
        self.logger.debug(f"population ({size})")
        pop=pd.DataFrame()
        
        for i in range(size):
            ind = self.indv.individual(i, alg_path)
            pop=pop.append(ind).reset_index(drop=True)

        pop['population'] = 'population'

        return pop    


class GeneticAlgorithmGenetics:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmGenetics")


    def selection(self, fitness_df, alg_path):

        if config.SELECTION == 'tournament':
            fitness_df=self.tournament_selection(fitness_df, alg_path)

        if config.SELECTION == 'nondom':
            fitness_df=self.nondom_selection(fitness_df, alg_path)

        return fitness_df 

    def tournament_selection(self, fitness_df, alg_path):
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
        parent_df = parent_df.sort_values(by=['time_id'])
                
        return parent_df

    def nondom_selection(self, fitness_df, alg_path):
        """This selection method makes use of the nondominated soting front to choose 
        parents. 
        NB: Only for NSGA-II. Moga etc has different structure. 
        TODO: Update for moga and VEGA. 
        TODO: Also remember to swop crossover and pareto select for real iterations.
        """

        pareto_set = fitness_df[fitness_df['front']==1].reset_index(drop=True)
        option_num = random.randint(0,len(pareto_set)-1)
        option_id = pareto_set.at[option_num, 'id']
        #parent_path = f"data/interim/{alg}/id_{option_id}"
        parent_path=os.path.join(alg_path, f"id_{option_id}")
        parent_df = pd.read_pickle(parent_path)

        return parent_df

    def mutation_TRUNCATE(self, df_mutate, times, test):
        """ GA mutation function to diversify gene pool. """
        
        self.logger.debug(f"-- mutation check")
        ix = Individual()

        if random.random() <= config.MUTATIONRATE:
            self.logger.debug(f"--- mutation activated")
            
            df_mutate1=pd.DataFrame()
            mutate = []
            for m in times:
                #df_gene = df_mutate[df_mutate['time_id'] == m]
                update = False

                if random.random() < config.MUTATIONRATE2:
                    update = True
                    
                    # If test then make new gene here
                    if test:
                        x = np.random.rand()
                        df_gene = pd.DataFrame(data=[x], columns=['value'])
                        df_gene['time_id'] = m
                        df_mutate1 = pd.concat([df_mutate1, df_gene]).reset_index(drop=True)
                    
                    # Else get only gene alternate
                    else:  
                        demand_list = list(df_gene.demand_id.unique())
                        df_gene = ix.make_individual(get_dlist=False, dlist=demand_list)  # FIXME:
                        df_mutate1 = pd.concat([df_mutate1, df_gene]).reset_index(drop=True)
                        
                mutate.append(update)
                
            df_mutate['mutate'] = mutate
            df_mutate = df_mutate.set_index('mutate')
            df_keep = df_mutate.loc[False]
            df_mutate1 = pd.concat([df_mutate1, df_keep]).reset_index(drop=True)

        else:
            df_mutate1 = df_mutate
            
        return df_mutate1

    def mutation(self, df_mutate, times, test):
        """ GA mutation function to diversify gene pool. """
        
        self.logger.debug(f"-- mutation check")
        ix = Individual()

        if random.random() <= config.MUTATIONRATE:
            self.logger.debug(f"--- mutation activated")
            
            df_mutate1=pd.DataFrame()
            #mutate = []
            mutates = [] #new

           
            times.sort()
            df_mutate=df_mutate.sort_values(by=['time_id']).reset_index(drop=True)
            #df_mutate['status'] = 'original'

            #print(times)
            #print(df_mutate)

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
                        #df_gene['status'] = 'mutated'
                        df_mutate1 = pd.concat([df_mutate1, df_gene]).reset_index(drop=True)
                    
                    # Else get only gene alternate
                    else: 
                        df_gener =  df_mutate[df_mutate['time_id']==m] #new
                        demand_list = list(df_gener.demand_id.unique())
                        df_gene = ix.make_individual(get_dlist=False, dlist=demand_list)
                        df_mutate1 = pd.concat([df_mutate1, df_gene]).reset_index(drop=True)
                        
                #mutate.append(update) # new
                mutates.append([update, m])
                
            mutated = pd.DataFrame(data=mutates, columns=['mutate', 'time_id']) # new
            df_mutate = pd.merge(df_mutate, mutated, on=['time_id'], how='left') # new
            df_keep = df_mutate[df_mutate["mutate"]] # new
            
            df_mutate1 = pd.concat([df_mutate1, df_keep]).reset_index(drop=True)
            df_mutate1=df_mutate1.drop(columns=['mutate'])
            #print(df_mutate1)

        else:
            df_mutate1 = df_mutate

        path=os.path.join('data','raw', f"mutation.xlsx")
        #df_mutate1.to_excel(path)

        return df_mutate1

    def crossover_TRUNCATE(self, fitness_df, alg, test, test_name):
        """ GA crossover genetic material for diversification"""
        self.logger.debug(f"-- crossover")

        ix = Individual()
        max_id = fitness_df.id.max()

        if test:
            times = list(range(config.D))

        else:
            ddf_metadata = pd.read_pickle('data/processed/ddf_metadata')
            times = list(ddf_metadata.time_id.unique())

        # Select parents with tournament
        pareto_df = fitness_df[fitness_df['population'] != 'none'].reset_index(drop=True)
        parent1 = self.tournament_selection(pareto_df, alg)
        parent2 = self.tournament_selection(pareto_df, alg)

        # Uniform crossover 
        self.logger.debug(f"--- uniform crossover")
        # FIXME: Not sure if this will work for real problem as 
        # times = unique and there might be several for one time?
        
        index = []      
        for _ in times:
            if random.random() < config.CROSSOVERRATE:
                index.append(True)
            
            else:
                index.append(False)

        parent1['index'] = index
        parent1 = parent1.set_index('index')
        parent2['index'] = index
        parent2 = parent2.set_index('index')

        child1a = parent1.loc[True]
        child1b = parent1.loc[False]
        child2a = parent2.loc[True]
        child2b = parent2.loc[False]

        child1 = pd.concat([child1a,child2b]).reset_index(drop=True)
        child2 = pd.concat([child1b,child2a]).reset_index(drop=True)

        path=os.path.join('data','raw', f"parent1.xlsx")
        #parent1.to_excel(path)
        path=os.path.join('data','raw', f"parent2.xlsx")
        #parent2.to_excel(path)

        path=os.path.join('data','raw', f"child1.xlsx")
        #child1.to_excel(path)
        path=os.path.join('data','raw', f"child2.xlsx")
        #child2.to_excel(path)

        # If test then make new test individual gene
        if test:
            # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=test)
            child2 = self.mutation(child2, times, test=test)

            # Register child on fitness_df
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

    def crossover_BITFLIP(self, fitness_df, alg_path, test, test_name):
        """ GA crossover genetic material for diversification"""
        self.logger.debug(f"-- crossover")

        ix = Individual()
        max_id = fitness_df.id.max()

        # Select parents with tournament
        parent1 = self.selection(fitness_df, alg_path)
        parent2 = self.selection(fitness_df, alg_path)

        times = list(parent1.time_id.unique())
        times_check = list(parent2.time_id.unique())

        if len(times) != len(times_check):
            exit()

        # Uniform crossover 
        self.logger.debug(f"--- uniform crossover")
        
        crossover = []      
        for _ in times:
            if random.random() < config.CROSSOVERRATE:
                crossover.append([True, _])
            
            else:
                crossover.append([False, _])
                
        crossoverd = pd.DataFrame(data=crossover, columns=['crossover', 'time_id']) # new
        parent1 = pd.merge(parent1, crossoverd, on=['time_id'], how='left') # new
        parent2 = pd.merge(parent2, crossoverd, on=['time_id'], how='left') # new

        child1a = parent1[parent1["crossover"]] # new
        child1b = parent1[~parent1["crossover"]] # new
        child2a = parent2[parent2["crossover"]] # new
        child2b = parent2[~parent2["crossover"]] # new

        child1 = pd.concat([child1a,child2b]).reset_index(drop=True)
        child2 = pd.concat([child1b,child2a]).reset_index(drop=True)

        child1=child1.drop(columns=['crossover'])
        child2=child2.drop(columns=['crossover'])

        path=os.path.join('data','raw', f"parent1.xlsx")
        path=os.path.join('data','raw', f"parent2.xlsx")

        path=os.path.join('data','raw', f"child1.xlsx")
        path=os.path.join('data','raw', f"child2.xlsx")

        # If test then make new test individual gene
        if test:
            # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=test)
            child2 = self.mutation(child2, times, test=test)

            # Register child on fitness_df
            child1_f = ix.individual(max_id+1, alg_path, get_indiv=False, indiv=child1, 
                            test=test, test_name=test_name)
            child2_f = ix.individual(max_id+2, alg_path, get_indiv=False, indiv=child2, 
                            test=test, test_name=test_name) 

        else:
           # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=False)
            child2 = self.mutation(child2, times, test=False)

            # Register child on fitness_df
            child1_f = ix.individual(max_id+1, alg_path, get_indiv=False, indiv=child1)
            child2_f = ix.individual(max_id+2, alg_path, get_indiv=False, indiv=child2)

        child1_f['population'] = 'child'
        child2_f['population'] = 'child'

        fitness_df = pd.concat([fitness_df, child1_f, child2_f]).reset_index(drop=True)
        return fitness_df

    def crossover_CROSSGEN(self, fitness_df, alg_path, test, test_name):
        """ GA crossover genetic material for diversification"""
        self.logger.debug(f"-- crossover")

        ix = Individual()
        max_id = fitness_df.id.max()

        # Select parents with tournament
        parent1 = self.selection(fitness_df, alg_path)
        parent2 = self.selection(fitness_df, alg_path)

        times = list(parent1.time_id.unique())
        times_check = list(parent2.time_id.unique())

        if len(times) != len(times_check):
            exit()

        # Uniform crossover 
        self.logger.debug(f"--- uniform crossover")
        
        crossover = []
        r = random.randint(0, len(times)-1)

        for count, _ in enumerate(times):
            if count <= r:
                crossover.append([True, _])
            
            else:
                crossover.append([False, _])
                
        crossoverd = pd.DataFrame(data=crossover, columns=['crossover', 'time_id']) # new
        parent1 = pd.merge(parent1, crossoverd, on=['time_id'], how='left') # new
        parent2 = pd.merge(parent2, crossoverd, on=['time_id'], how='left') # new

        child1a = parent1[parent1["crossover"]] # new
        child1b = parent1[~parent1["crossover"]] # new
        child2a = parent2[parent2["crossover"]] # new
        child2b = parent2[~parent2["crossover"]] # new

        child1 = pd.concat([child1a,child2b]).reset_index(drop=True)
        child2 = pd.concat([child1b,child2a]).reset_index(drop=True)

        child1=child1.drop(columns=['crossover'])
        child2=child2.drop(columns=['crossover'])

        path=os.path.join('data','raw', f"parent1.xlsx")
        path=os.path.join('data','raw', f"parent2.xlsx")

        path=os.path.join('data','raw', f"child1.xlsx")
        path=os.path.join('data','raw', f"child2.xlsx")

        # If test then make new test individual gene
        if test:
            # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=test)
            child2 = self.mutation(child2, times, test=test)

            # Register child on fitness_df
            child1_f = ix.individual(max_id+1, alg_path, get_indiv=False, indiv=child1, 
                            test=test, test_name=test_name)
            child2_f = ix.individual(max_id+2, alg_path, get_indiv=False, indiv=child2, 
                            test=test, test_name=test_name) 

        else:
           # Bring mutatation opportunity in
            child1 = self.mutation(child1, times, test=False)
            child2 = self.mutation(child2, times, test=False)

            # Register child on fitness_df
            child1_f = ix.individual(max_id+1, alg_path, get_indiv=False, indiv=child1)
            child2_f = ix.individual(max_id+2, alg_path, get_indiv=False, indiv=child2)

        child1_f['population'] = 'child'
        child2_f['population'] = 'child'

        fitness_df = pd.concat([fitness_df, child1_f, child2_f]).reset_index(drop=True)

        path=os.path.join('data','raw', f"child1_m.xlsx")
        path=os.path.join('data','raw', f"child2_m.xlsx")

        return fitness_df

    def crossover(self, fitness_df, alg_path, test=False, test_name='zdt1'):
        if config.CROSSOVERTYPE == 'crossover_BITFLIP':
            fitness_df=self.crossover_BITFLIP(fitness_df, alg_path, test, test_name)

        if config.CROSSOVERTYPE == 'crossover_CROSSGEN':
            fitness_df=self.crossover_CROSSGEN(fitness_df, alg_path, test, test_name)

        return fitness_df   

    def dominates_TRUNCATE(objset1, objset2, sign=[1, 1]):
        """
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
        indicator = False
        for a, b, sign in zip(objset1, objset2, sign):
            if a * sign < b * sign:
                indicator = True
            # if one of the objectives is dominated, then return False
            elif a * sign > b * sign:
                return False

            elif a * sign == b * sign:
                return False
                
        return indicator

    def get_domcount(self, fitness_df):
        front = []
        fitness_df = fitness_df.sort_values(by=['id']).reset_index(drop=True)

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
                #if ((obj1 <= obj1x and obj2 <= obj2x) and (obj1 < obj1x or obj2 < obj2x)):
                if (obj1 <= obj1x and obj2 < obj2x):
                    dominating_fits[i + ix + 1] += 1 
                    dominated_fits[id].append(idx) 

                #if build_features.GeneticAlgorithmGenetics.dominates((obj1x, obj2x), (obj1, obj2)):
                #if ((obj1 >= obj1x and obj2 >= obj2x) and (obj1 > obj1x or obj2 > obj2x)):
                if (obj1 >= obj1x and obj2 > obj2x):
                    dominating_fits[i] += 1
                    dominated_fits[idx].append(id)    

            if dominating_fits[i] == 0:
                front.append(id)

        fitness_df['domcount'] = dominating_fits
        fitness_df.loc[(fitness_df.domcount==0), 'front'] = 1
        return fitness_df, front, dominated_fits

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

    def calculate_hyperarea(self, fitness_df):
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
                    area = area + (objective1_diff * objs2[count])

            temp = pd.DataFrame(data=[(set, area)],
                    columns=['population', 'hyperarea'])

            hyperarea=pd.concat([hyperarea, temp]).reset_index(drop=True)

        print(hyperarea)
        return hyperarea


class PrepManPlan:
    """ Class to prepare Manual PackPlan for comparison"""
    logger = logging.getLogger(f"{__name__}.CreateOptions")
    #co = CreateOptions()
    database_instance = DatabaseModelsClass('PHDDATABASE_URL')
    indiv = Individual()
    graph = Visualize()

    def clear_old_result(self):
        self.logger.info(f"clear old data tables (sol_fitness & sol_pareto_individuals)")

        sql="""
        TRUNCATE `dss`.`sol_fitness`;
        """
        self.database_instance.execute_query(sql)

        sql="""
        DROP TABLE `dss`.`sol_pareto_individuals`;
        """
        self.database_instance.execute_query(sql)

        return

    def prep_results(self, alg_path, fitness_df, init_pop):
        """function to convert final pareto front to sql data 
            here with manplan and actual"""

        self.logger.info(f"prepare results and send to sql")
        pareto_indivs = list(fitness_df.id)
        popdf=pd.DataFrame()
        for id in pareto_indivs:
            infile = open(f"data/interim/{alg_path}/id_{id}",'rb')
            individualdf = pickle.load(infile)
            infile.close()
            individualdf['indiv_id'] = id
            popdf=popdf.append(individualdf).reset_index(drop=True)

        popdf['alg'] = alg_path

        kobus_plan = self.kobus_plan()
        kobus_fit = self.indiv.individual(1000000, 
                    alg_path = alg_path, 
                    get_indiv=False, 
                    indiv=kobus_plan, 
                    test=False)
        kobus_fit['population'] = 'manplan'
        kobus_fit['result'] = 'manplan'

        #actual_plan = self.actual()
        #actual_fit = self.indiv.individual(1000001, 
        #            alg_path = alg_path, 
        #            get_indiv=False, 
        #            indiv=actual_plan, 
        #            test=False)
        #actual_fit['population'] = 'actualplan'
        #actual_fit['result'] = 'actualplan'

        init_pop['result'] = 'init pop'
        fitness_df['result'] = 'final result'
        
        #fitness_df = pd.concat([fitness_df, init_pop, kobus_fit, actual_fit])   
        fitness_df = pd.concat([fitness_df, init_pop, kobus_fit])      
        fitness_df['alg'] = alg_path
        fitness_df = fitness_df.rename(columns={"id": "indiv_id"})
        fitness_df = fitness_df[['indiv_id', 'obj1', 'obj2', 'population', 'result', 'alg']]
        
        self.database_instance.insert_table(fitness_df, 'sol_fitness', 'dss', if_exists='append')
        self.database_instance.insert_table(popdf, 'sol_pareto_individuals', 'dss', if_exists='append')
        self.database_instance.insert_table(kobus_plan, 'sol_kobus_plan', 'dss', if_exists='replace')
        #self.database_instance.insert_table(actual_plan, 'sol_actual_plan', 'dss', if_exists='replace')

        filename_html = f"reports/figures/genetic_algorithm_{alg_path}.html"
        self.graph.scatter_plot2(fitness_df, filename_html, 'result', 
                alg_path)
        
        return

    def kobus_plan(self):
        sql_query = """
            SELECT pd.demandid as demand_id
                    , f_pack_capacity.id as pc
                    , dim_fc.id as fc_id
                    -- , dim_packhouse.id as packhouse_id
                    -- , dim_week.id as time_id
                    -- , pack_type.id as pack_type_id
                    , dim_va.id as va_id
                    , (pd.qty_kg * -1) as kg
                    , (pd.qty_standardctns * -1) as stdunits
                    , distance.km
                    , (pd.qty_kg * -1) * distance.km as 'kgkm'
                    , IF(f_speed.speed is NULL, 12, f_speed.speed) as speed
                    -- , pd.variety
                    -- , pd.format
                    -- , pd.packweek
                    -- , pd.packsite
                    -- , pd.grower
            FROM dss.planning_data pd
            LEFT JOIN dim_fc ON (pd.grower = dim_fc.name)
            LEFT JOIN dim_packhouse ON (pd.packsite = dim_packhouse.name)
            LEFT JOIN (SELECT id, upper(name) as name FROM dss.dim_pack_type) pack_type  
                ON (pd.format = pack_type.name)
            LEFT JOIN dim_va ON (pd.variety = dim_va.name)
            LEFT JOIN dim_week ON (pd.packweek = dim_week.week)
            LEFT JOIN (SELECT f_from_to.packhouse_id, dim_block.fc_id, AVG(f_from_to.km) as km
                            FROM dss.f_from_to
                            LEFT JOIN dim_block ON (dim_block.id = f_from_to.block_id)
                            GROUP BY f_from_to.packhouse_id, dim_block.fc_id) distance 
                            ON (distance.packhouse_id = dim_packhouse.id 
                                AND distance.fc_id = dim_fc.id)
            LEFT JOIN f_speed 
				ON (f_speed.packhouse_id = dim_packhouse.id 
                    AND f_speed.packtype_id = pack_type.id 
					AND f_speed.va_id = dim_va.id)
			LEFT JOIN f_pack_capacity
				ON (f_pack_capacity.packhouse_id = dim_packhouse.id 
					AND f_pack_capacity.pack_type_id = pack_type.id
                    AND f_pack_capacity.packweek = dim_week.week)
            -- WHERE extract_datetime = '2021-11-08 13:29:36'
            WHERE recordtype = 'PLANNED'
            AND extract_datetime = (SELECT MAX(extract_datetime) FROM dss.planning_data)
            AND f_pack_capacity.stdunits is not null
            AND pd.packweek in ('22-01','22-02','22-03','22-04')
            ;
        """
        
        df = self.database_instance.select_query(query_str=sql_query)
        df['packhours'] = df['kg']*(1*config.GIVEAWAY)*df['speed']/60 

        return df

    def actual(self):
        sql_query = """
            SELECT pd.demandid as demand_id
                    , f_pack_capacity.id as pc
                    , dim_fc.id as fc_id
                    -- , dim_packhouse.id as packhouse_id
                    -- , dim_week.id as time_id
                    -- , pack_type.id as pack_type_id
                    , dim_va.id as va_id
                    , (pd.qty_kg * -1) as kg
                    , (pd.qty_standardctns * -1) as stdunits
                    , distance.km
                    , (pd.qty_kg * -1) * distance.km as 'kgkm'
                    , IF(f_speed.speed is NULL, 12, f_speed.speed) as speed
                    -- , pd.variety
                    -- , pd.format
                    -- , pd.packweek
                    -- , pd.packsite
                    -- , pd.grower
            FROM dss.planning_data pd
            LEFT JOIN dim_fc ON (pd.grower = dim_fc.name)
            LEFT JOIN dim_packhouse ON (pd.packsite = dim_packhouse.name)
            LEFT JOIN (SELECT id, upper(name) as name FROM dss.dim_pack_type) pack_type  
                ON (pd.format = pack_type.name)
            LEFT JOIN dim_va ON (pd.variety = dim_va.name)
            LEFT JOIN dim_week ON (pd.packweek = dim_week.week)
            LEFT JOIN (SELECT f_from_to.packhouse_id, dim_block.fc_id, AVG(f_from_to.km) as km
                            FROM dss.f_from_to
                            LEFT JOIN dim_block ON (dim_block.id = f_from_to.block_id)
                            GROUP BY f_from_to.packhouse_id, dim_block.fc_id) distance 
                            ON (distance.packhouse_id = dim_packhouse.id 
                                AND distance.fc_id = dim_fc.id)
            LEFT JOIN f_speed 
				ON (f_speed.packhouse_id = dim_packhouse.id 
                    AND f_speed.packtype_id = pack_type.id 
					AND f_speed.va_id = dim_va.id)
			LEFT JOIN f_pack_capacity
				ON (f_pack_capacity.packhouse_id = dim_packhouse.id 
					AND f_pack_capacity.pack_type_id = pack_type.id
                    AND f_pack_capacity.packweek = dim_week.week)
            -- WHERE extract_datetime = '2021-11-08 13:29:36'
            WHERE recordtype = '_PACKED'
            AND extract_datetime = (SELECT MAX(extract_datetime) FROM dss.planning_data)
            AND f_pack_capacity.stdunits is not null
            AND pd.packweek in ('22-01','22-02','22-03','22-04')
            AND dim_fc.packtopackplans = 1;
        """
        
        df = self.database_instance.select_query(query_str=sql_query)
        df['packhours'] = df['kg']*(1*config.GIVEAWAY)*df['speed']/60  # TODO: CHECK CALC!!!!

        return df


class PrepModelData:
    """ Class to make features of ... """
    logger = logging.getLogger(f"{__name__}.PrepModelData")
    gld = GetLocalData()
    database_dss = DatabaseModelsClass('PHDDATABASE_URL')
    #mf = MakeFeatures()

    def prep_harvest_estimates(self):
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

            he = self.gld.get_local_he()
            self.database_dss.execute_query('TRUNCATE `dss`.`f_harvest_estimate`;')
            he['add_datetime'] = datetime.datetime.now()
            self.database_dss.insert_table(he, 'f_harvest_estimate', 'dss', if_exists='append')
            success = True

        except:
            success = False
            #self.mf.notify(False, 'prep_harvest_estimates')
            self.logger.info(f"-- Prep harvest estimate failed")
            
        return success

    def prep_demand_plan(self):
        self.logger.info(f"- Prep demand plan")

        try:
            client = self.gld.get_dp_client()
            if len(client) > 0:
                self.database_dss.insert_table(client, 'dim_client', 'dss', if_exists='append')
                self.logger.info(f"-- Added {len(client)} clients")

            dp = self.gld.get_local_dp()
            self.database_dss.execute_query('TRUNCATE `dss`.`f_demand_plan`;')
            dp['add_datetime'] = datetime.datetime.now()
            self.database_dss.insert_table(dp, 'f_demand_plan', 'dss', if_exists='append')
            success = True
        
        except:
            success = False
            #self.mf.notify(False, 'prep_demand_plan')
            self.logger.info(f"-- Prep demand failed")

        return success

    def prep_pack_capacity(self):
        self.logger.info(f"- Prep pack capacities")

        try:
            packhouse = self.gld.get_pc_packhouse()
            if len(packhouse) > 0:
                self.database_dss.insert_table(packhouse, 'dim_packhouse', 'dss', if_exists='append')
                self.logger.info(f"-- Added {len(packhouse)} packhouses")

            pc = self.gld.get_local_pc()
            self.database_dss.execute_query('TRUNCATE `dss`.`f_pack_capacity`;')
            pc['add_datetime'] = datetime.datetime.now()
            self.database_dss.insert_table(pc, 'f_pack_capacity', 'dss', if_exists='append')
            success = True

        except:
            success = False
            #self.mf.notify(False, 'prep_pack_capacity')
            self.logger.info(f"-- Prep pack failed")

        return success