import logging
import math
import os
import random
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
from src.features import build_features
from src.features.build_features import (GeneticAlgorithmGenetics, Individual,
                                         Population, PrepManPlan)
from src.utils import config
from src.utils.visualize import Visualize

from operator import itemgetter

class GeneticAlgorithmVega:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmVega")
    gag = GeneticAlgorithmGenetics()
    manplan = PrepManPlan()
    #graph = Visualize()

    def vega(self):
        """ Function that manages the GA. """
        self.logger.debug(f"Vector Evaluated Genetic Algorthm")

        alg_path=os.path.join(config.ROOTDIR,'data','interim','vega')
        
        p = Population()
        init_pop = p.population(config.POPUATION, alg_path)
        fitness_df = init_pop
        fitness_df['population'] = 'yes'

        self.logger.debug(f"starting VEGA search")
        for _ in range(config.ITERATIONS):
            self.logger.debug(f"ITERATION {_}")
            fitness_df = self.gag.crossover(fitness_df, alg_path)
            fitness_df = self.pareto_vega(fitness_df)

        init_pop['result'] = 'init pop'
        fitness_df['result'] = 'final result'

        return [alg_path, fitness_df, init_pop]

    def pareto_vega(self, fitness_df):
        """ Decide if new child is worthy of pareto membership 
        Shaffer 1985
        """
        self.logger.debug(f"- getting fitness")
        popsize = config.POPUATION

        fitness_df['population'] = 'none'

        # Random select objective to sort
        objective = random.randint(0,1)
        objective = ['obj1', 'obj2'][objective]

        # Sort along objectives
        halfpop = int(popsize/2)
        objective = 'obj1'
        fitness_df1 = fitness_df.sort_values(by=[objective])
        #objval = list(fitness_df1[objective][popsize-1:popsize])[0]
        objval = list(fitness_df1[objective][halfpop-1:halfpop])[0]
        fitness_df.loc[(fitness_df[objective] <= objval), 'population'] = 'yes'      

        objective = 'obj2'
        fitness_df1 = fitness_df.sort_values(by=[objective])
        #objval = list(fitness_df1[objective][popsize-1:popsize])[0]
        objval = list(fitness_df1[objective][halfpop-1:halfpop])[0]
        fitness_df.loc[(fitness_df[objective] <= objval), 'population'] = 'yes'

        fitness_df = fitness_df[fitness_df['population'] == 'yes']  

        return fitness_df


class GeneticAlgorithmNsga2:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmNsga2")
    gag = GeneticAlgorithmGenetics()
    manplan = PrepManPlan()
    indiv = Individual()

    def nsga2(self):
        """ Function that manages the NSGA2. """
        self.logger.info(f"Non Dominated Sorting Genetic Algorithm")

        alg_path=os.path.join(config.ROOTDIR,'data','interim','nsga2')
        
        p = Population()
        init_pop = p.population(config.POPUATION, alg_path)
        init_pop = self.gag.make_children(init_pop, alg_path)[0]
            
        fitness_df = self.pareto_nsga2(init_pop)
        self.logger.info(f"starting NSGA2 search")
        for _ in range(config.ITERATIONS):
            self.logger.info(f"ITERATION {_}")
            fitness_df = self.gag.make_children(fitness_df, alg_path)[0]
            fitness_df = self.pareto_nsga2(fitness_df)

        return [alg_path, fitness_df, init_pop]

    def crowding_distance(self, fitness_df, fc, size):
        """ Crowding distance sorting """ 
        self.logger.debug(f"-- crowding distance activated")
        fitness_df['population']='yes'
        fitness_df['cdist'] = 0

        vals_obj1 = np.array(fitness_df['obj1'])
        vals_obj2 = np.array(fitness_df['obj2'])

        # Evaluate how much space is available for the crowding distance
        if fc==1:
            space = config.POPUATION

        else:
            space = config.POPUATION - size

        objs = ['obj1', 'obj2']
        for m in objs:
            # Sort by objective (m) 
            fitness_df = fitness_df.sort_values(by=m, ascending=True).reset_index(drop=True)
            vals = np.array(fitness_df[m])
            cdists = list(fitness_df['cdist'])
            
            if m == 'obj1':
                min = np.min(vals_obj1)
                max = np.max(vals_obj1)

            else:
                min = np.min(vals_obj2)
                max = np.max(vals_obj2)

            for i in range(len(fitness_df)):

                if i == 0 or i == len(fitness_df)-1:
                    cdists[0] = np.inf
                    cdists[-1] = np.inf

                else:
                    oneup = vals[i-1]
                    onedown = vals[i+1]

                    if (max - min) > 0:
                        distance = (onedown - oneup) / (max - min)
                    
                    else:
                        distance = (onedown - oneup) / (min)

                    cdists[i] = cdists[i] + distance

            fitness_df['cdist'] = cdists
                        
        fitness_df = fitness_df.sort_values(by=['cdist'], ascending=False).reset_index(drop=True)
        fitness_df=fitness_df[fitness_df.index < (space)]

        return fitness_df

    def pareto_nsga2(self, fitness_df):
        """ Decide if new child is worthy of pareto membership 
        Deb 2002
        """        
        # Initiate domination count and dominated by list
        fitness_df = fitness_df[['id','obj1','obj2']]
        front1 = self.gag.get_domcount(fitness_df)
        fitness_df = fitness_df[fitness_df['id'].isin(front1)].reset_index(drop=True)

        ###################################################
        # Get front count and determine population status #
        ###################################################
        # Size of selected solutions
        size = len(front1)

        # Check if set of sols in front 1 will fit into new population?
        if size > config.POPUATION:
            fitness_df=self.crowding_distance(fitness_df, 1, size)

        return fitness_df

    def pareto_nsga2_DEPRICATED(self, fitness_df):
        """ Decide if new child is worthy of pareto membership 
        Deb 2002
        """
        self.logger.debug(f"- getting NSGA2 fitness")
        
        # Initiate domination count and dominated by list
        self.logger.debug(f"-- getting domcount")

        fitness_df = fitness_df[['id','obj1','obj2']]
        fitness_df=fitness_df.drop_duplicates(subset=['obj1','obj2'], keep='last')
        fitness_df = self.gag.get_domcount(fitness_df)

        ###################################################
        # Get front count and determine population status #
        ###################################################
        self.logger.debug(f"-- getting front count")

        # Size of selected solutions
        size = len(fitness_df[fitness_df['front'] == 1])

        # Check if set of sols in front 1 will fit into new population?
        if size > config.POPUATION:
            fitness_df=self.crowding_distance(fitness_df, 1, size)

        else: # size == config.POPUATION:
            fitness_df.loc[(fitness_df['front']==1), 'population'] = 'yes'


        fitness_df=fitness_df[fitness_df['population']=='yes'].reset_index(drop=True)
        return fitness_df

    def crowding_distance_DEPRICATED(self, fitness_df, fc, size):
        """ Crowding distance sorting """ 
        self.logger.debug(f"-- crowding distance activated")
        fitness_df['front']=1
        fitness_df['population']='yes'
        fitness_df['cdist'] = 0
        fitness_dff = fitness_df[fitness_df['front']==fc].reset_index(drop=True)
        
        # Evaluate how much space is available for the crowding distance
        if fc==1:
            space = config.POPUATION

        else:
            space = config.POPUATION - size

        objs = ['obj1', 'obj2']
        for m in objs:
            # Sort by objective (m) 
            fitness_dff = fitness_dff.sort_values(by=m, ascending=True).reset_index(drop=True)
            vals = np.array(fitness_dff[m])
            ids = np.array(fitness_dff['id'])
            cdists = list(fitness_dff['cdist'])
            
            min = np.min(vals)
            max = np.max(vals)

            for i in range(len(ids)):

                if i == 0 or i == len(ids)-1:
                    cdists[0] = np.inf
                    cdists[-1] = np.inf

                else:
                    oneup = vals[i-1]
                    onedown = vals[i+1]

                    if (max - min) > 0:
                        distance = (onedown - oneup) / (max - min)
                    
                    else:
                        distance = (onedown - oneup) / (min)

                    cdists[i] = cdists[i] + distance

            fitness_dff['cdist'] = cdists
                        
        fitness_dff = fitness_dff.sort_values(by=['cdist'], ascending=False).reset_index(drop=True)
        fitness_dff.loc[(fitness_dff.index > space),'population'] = 'no'
        fitness_dff=fitness_dff[fitness_dff.index < (space - 1)]

        fitness_df2 = fitness_df[fitness_df['front']!=fc].reset_index(drop=True)
        fitness_df3 = pd.concat([fitness_df2, fitness_dff]).reset_index(drop=True)

        fitness_df3 = fitness_df3.set_index('id')
        fitness_df3['id'] = fitness_df3.index

        return fitness_df3

    def crowding_distance_DEPRICATED2(self, fitness_df, fc, size):
        """ Crowding distance sorting """ 
        self.logger.debug(f"-- crowding distance activated")
        
        fitness_df['population']='yes'
        fitness_df['cdist'] = 0

        cols = list(fitness_df.columns)
        
        dist_pos = cols.index('cdist')
        fitness = fitness_df.to_numpy().tolist()
        vals_obj1 = np.array(fitness_df['obj1'])
        vals_obj2 = np.array(fitness_df['obj2'])
        
        # Evaluate how much space is available for the crowding distance
        if fc==1:
            space = config.POPUATION

        else:
            space = config.POPUATION - size

        objs = ['obj1', 'obj2']
        for obj in objs:
            m = cols.index(obj)
            # Sort by objective (m) 
            fitness=sorted(fitness, key=itemgetter(m))
            
            if obj == 'obj1':
                min = np.min(vals_obj1)
                max = np.max(vals_obj1)

            else:
                min = np.min(vals_obj2)
                max = np.max(vals_obj2)

            for i in range(len(fitness)):

                if i == 0 or i == len(fitness)-1:
                    fitness[0][dist_pos] = np.inf
                    fitness[-1][dist_pos] = np.inf

                else:
                    oneup = fitness[i-1][m]
                    onedown = fitness[i+1][m]

                    if (max - min) > 0:
                        distance = (onedown - oneup) / (max - min)
                    
                    else:
                        distance = (onedown - oneup) / (min)

                    fitness[i][dist_pos] = fitness[i][dist_pos] + distance

        fitness=sorted(fitness, key=itemgetter(dist_pos))
        fitness=fitness[:space]
        fitness_df = pd.DataFrame(data=fitness, columns=cols)

        return fitness_df


class GeneticAlgorithmMoga:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmMoga")
    gag = GeneticAlgorithmGenetics()
    #graph = Visualize()
    manplan = PrepManPlan()

    def moga(self):
        """ Function that manages the MOGA. """
        self.logger.info(f"Multi Objective Genetic Algorithm")

        alg_path=os.path.join(config.ROOTDIR,'data','interim','moga')
        
        p = Population()
        init_pop = p.population(config.POPUATION, alg_path)
        fitness_df = init_pop

        fitness_df['population'] = 'yes'

        self.logger.info(f"starting MOGA search")
        for _ in range(config.ITERATIONS):
            self.logger.info(f"ITERATION {_}")
            fitness_df = self.pareto_moga(fitness_df)
            fitness_df = self.gag.crossover(fitness_df, alg_path)
            
        fitness_df = self.pareto_moga(fitness_df)
        
        return [alg_path, fitness_df, init_pop]

    def pareto_moga(self, fitness_df):
        # TODO: Update with 'at' instead of 'loc' for speed.
        self.logger.info(f"- getting MOGA fitness")

        fitness_df = fitness_df[fitness_df['population'] != 'none'].reset_index(drop=True)
        fitness_df= fitness_df.sort_values(by=['obj1','obj2']).reset_index(drop=True)

        sshare = config.SSHARE

        ##############################################################################
        # 1. Assign rank based on non-dominated
        #    - rank(indiv, generation) = 1 + number of indivs that dominate indiv
        ##############################################################################
        fitness_df = self.gag.get_domcount(fitness_df)[0] #FIXME: updated and moved domcount to gag
        fitness_df['rank'] = fitness_df['domcount'] + 1

        ##############################################################################
        # 2. PARETO RANKING
        ##############################################################################
        fitness_df=fitness_df.sort_values(by=['rank']).reset_index(drop=True)
        ranks = fitness_df['rank'].unique()
        N = len(fitness_df)

        for r in ranks:
            solk = len(fitness_df[fitness_df['rank']==r]) - 1
            nk = len(fitness_df[fitness_df['rank'] < r])
            fitness_df.loc[(fitness_df['rank']==r), 'solk'] = solk
            fitness_df.loc[(fitness_df['rank']==r), 'nk'] = nk
            
        fitness_df['fitness'] = N - fitness_df['nk'] - (fitness_df['solk'] * 0.5)

        ##############################################################################
        # 3. STANDARD FITNESS SHARE
        ##############################################################################
        # 3.1 Normalised distance between any two indivs in same rank

        obj1_min=fitness_df.obj1.min()
        obj1_max=fitness_df.obj1.max()
        obj2_min=fitness_df.obj2.min()
        obj2_max=fitness_df.obj2.max()

        for r in ranks:
            df=fitness_df[fitness_df['rank']==r].reset_index(drop=True)
            ids=list(df.id)


            obj1s = df['obj1'].values
            obj2s = df['obj2'].values

            for i, id_i in enumerate(ids):
            #for i in range(len(df)):
                #id_i = df.id[i]
                #obj1_i = df.obj1[i]
                #obj2_i = df.obj2[i]
                obj1_i = obj1s[i]
                obj2_i = obj2s[i]
                nc=0

                for j, id_j in enumerate(ids):
                #for j in range(len(df)):
                    #print(f"{i} - {j}")
                    #id_j = df.id[j]
                    #obj1_j = df.obj1[j]
                    #obj2_j = df.obj2[j]
                    obj1_j = obj1s[j]
                    obj2_j = obj2s[j]

                    obj1_dij = ((obj1_i-obj1_j)/(obj1_max-obj1_min))**2    
                    obj2_dij = ((obj2_i-obj2_j)/(obj2_max-obj2_min))**2

                    dij = math.sqrt(obj1_dij+obj2_dij)

        # 3.2 The standard sharing function suggested by Goldberg and Richardson
        #       with a normalized niche radius σshare

                    if dij < sshare:
                        shdij = 1-(dij/sshare)

                    else: 
                        shdij = 0

        # 3.3 Niche count is calculated by indiv by summing up sharing 
        #       by indivs with same rank
                    
                    nc=nc+shdij

                #FIXME: optimise
                fitness_df.loc[(fitness_df['id']==id_i), 'nc'] = nc
                
        # 3.4 Finally, the assigned fitness is reduced by dividing the fitness Fi given 
        #       in step 2 by the niche count as follows

        fitness_df['fitness']=fitness_df['fitness']/fitness_df['nc']
        fitness_df = fitness_df.sort_values(by=['fitness'], ascending=[False]).reset_index(drop=True)

        fitness_df.loc[(fitness_df.index < config.POPUATION),'population']='yes'
        fitness_df.loc[(fitness_df.index >= config.POPUATION),'population']='none'

        return fitness_df


    def pareto_moga_DEPRICATED(self, fitness_df):
        # TODO: Update with 'at' instead of 'loc' for speed.
        self.logger.info(f"- getting MOGA fitness")

        fitness_df = fitness_df[fitness_df['population'] != 'none'].reset_index(drop=True)
        fitness_df= fitness_df.sort_values(by=['obj1','obj2']).reset_index(drop=True)

        sshare = config.SSHARE

        ##############################################################################
        # 1. Assign rank based on non-dominated
        #    - rank(indiv, generation) = 1 + number of indivs that dominate indiv
        ##############################################################################
        dominating_fits = defaultdict(int)  # n (The number of people that dominate you)
        dominated_fits = defaultdict(list)  # Sp (The people you dominate)
        fits = list(fitness_df.id)
        fitness_df=fitness_df.set_index('id')
        fitness_df['id'] = fitness_df.index
        fitness_df['domcount'] = 0

        for i, id in enumerate(fits):
            obj1 = fitness_df.at[id, 'obj1']
            obj2 = fitness_df.at[id, 'obj2']

            #for j in range(len(fitness_df)):
            for idx in fits[i + 1:]:
                obj1x = fitness_df.at[idx, 'obj1']
                obj2x = fitness_df.at[idx, 'obj2']
                
                #if build_features.GeneticAlgorithmGenetics.dominates(objset1, objset2):
                if (obj1 <= obj1x and obj2 <= obj2x) and (obj1 < obj1x or obj2 < obj2x):
                    dominating_fits[idx] += 1 
                    fitness_df.at[idx, 'domcount'] += 1
                    dominated_fits[id].append(idx) 

                #elif build_features.GeneticAlgorithmGenetics.dominates(objset2, objset1):  
                if (obj1x <= obj1 and obj2x <= obj2) and (obj1x < obj1 or obj2x < obj2):
                    dominating_fits[id] += 1
                    fitness_df.at[id, 'domcount'] += 1
                    dominated_fits[idx].append(id)    

            if dominating_fits[id] == 0:
                fitness_df.loc[(fitness_df.index==id), 'front'] = 1
                #front.append(id)

        fitness_df['rank'] = fitness_df['domcount'] + 1

        ##############################################################################
        # 2. PARETO RANKING
        ##############################################################################
        fitness_df=fitness_df.sort_values(by=['rank']).reset_index(drop=True)
        ranks = fitness_df['rank'].unique()
        N = len(fitness_df)

        for r in ranks:
            solk = len(fitness_df[fitness_df['rank']==r]) - 1
            nk = len(fitness_df[fitness_df['rank'] < r])
            fitness_df.loc[(fitness_df['rank']==r), 'solk'] = solk
            fitness_df.loc[(fitness_df['rank']==r), 'nk'] = nk
            
        fitness_df['fitness'] = N - fitness_df['nk'] - (fitness_df['solk'] * 0.5)

        ##############################################################################
        # 3. STANDARD FITNESS SHARE
        ##############################################################################
        # 3.1 Normalised distance between any two indivs in same rank

        obj1_min=fitness_df.obj1.min()
        obj1_max=fitness_df.obj1.max()
        obj2_min=fitness_df.obj2.min()
        obj2_max=fitness_df.obj2.max()

        for r in ranks:
            df=fitness_df[fitness_df['rank']==r].reset_index(drop=True)
            
            for i in range(len(df)):
                id_i = df.id[i]
                obj1_i = df.obj1[i]
                obj2_i = df.obj2[i]
                nc=0

                for j in range(len(df)):
                    #print(f"{i} - {j}")
                    id_j = df.id[j]
                    obj1_j = df.obj1[j]
                    obj2_j = df.obj2[j]

                    obj1_dij = ((obj1_i-obj1_j)/(obj1_max-obj1_min))**2    
                    obj2_dij = ((obj2_i-obj2_j)/(obj2_max-obj2_min))**2

                    dij = math.sqrt(obj1_dij+obj2_dij)

        # 3.2 The standard sharing function suggested by Goldberg and Richardson
        #       with a normalized niche radius σshare

                    if dij < sshare:
                        shdij = 1-(dij/sshare)

                    else: 
                        shdij = 0

        # 3.3 Niche count is calculated by indiv by summing up sharing 
        #       by indivs with same rank
                    
                    nc=nc+shdij

                fitness_df.loc[(fitness_df['id']==id_i), 'nc'] = nc

        # 3.4 Finally, the assigned fitness is reduced by dividing the fitness Fi given 
        #       in step 2 by the niche count as follows

        fitness_df['fitness']=fitness_df['fitness']/fitness_df['nc']
        fitness_df = fitness_df.sort_values(by=['fitness'], ascending=[False]).reset_index(drop=True)

        fitness_df.loc[(fitness_df.index < config.POPUATION),'population']='yes'
        fitness_df.loc[(fitness_df.index >= config.POPUATION),'population']='none'

        return fitness_df
