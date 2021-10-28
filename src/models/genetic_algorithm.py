import os
import random
import sys
import logging
import math
from collections import defaultdict

import pandas as pd
import numpy as np
from src.features.build_features import Individual
from src.features.build_features import Population
from src.features.build_features import GeneticAlgorithmGenetics
from src.features import build_features
from src.utils.visualize import Visualize
from src.utils import config


class GeneticAlgorithmVega:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmVega")
    gag = GeneticAlgorithmGenetics()
    graph = Visualize()

    def vega(self):
        """ Function that manages the GA. """
        self.logger.debug(f"Vector Evaluated Genetic Algorthm")
        
        p = Population()
        init_pop = p.population(config.POPUATION, 'vega')
        fitness_df = init_pop
        fitness_df['population'] = 'yes'

        self.logger.debug(f"starting VEGA search")
        for _ in range(config.ITERATIONS):
            self.logger.debug(f"ITERATION {_}")
            fitness_df = self.gag.crossover(fitness_df, 'vega')
            fitness_df = self.pareto_vega(fitness_df)

        init_pop['result'] = 'init pop'
        fitness_df['result'] = 'final result'
        
        fitness_df = pd.concat([fitness_df, init_pop])

        fitness_df.to_excel('data/interim/fitness_vega.xlsx', index=False)
        filename_html = 'reports/figures/genetic_algorithm_vega.html'
        self.graph.scatter_plot2(fitness_df, filename_html, 'result', 
                'Vector Evaluated Genetic Algorithm (VEGA)')

        best_obj1 = fitness_df['obj1'].min()
        best_obj2 = fitness_df['obj2'].min()
        return [best_obj1, best_obj2]

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
    graph = Visualize()

    def nsga2(self):
        """ Function that manages the NSGA2. """
        self.logger.debug(f"Non Dominated Sorting Genetic Algorithm")
        
        p = Population()
        init_pop = p.population(config.POPUATION * 2, 'nsga2')
        fitness_df = init_pop

        # Make child pop out of main population
        #while len(fitness_df) < (config.POPUATION * 2):
        #    fitness_df = self.gag.crossover(fitness_df, 'nsga2')
        #    self.logger.debug(f"making child pop 2n {len(fitness_df)}")

        fitness_df['population'] = 'yes'

        self.logger.debug(f"starting NSGA2 search")
        for _ in range(config.ITERATIONS):
            self.logger.debug(f"ITERATION {_}")
            fitness_df = self.gag.crossover(fitness_df, 'nsga2')
            fitness_df = self.pareto_nsga2(fitness_df)

        init_pop['result'] = 'init pop'
        fitness_df['result'] = 'final result'
        
        fitness_df = pd.concat([fitness_df, init_pop])        
        
        fitness_df.to_excel('data/interim/fitness_nsga2.xlsx', index=False)
        filename_html = 'reports/figures/genetic_algorithm_nsga2.html'
        self.graph.scatter_plot2(fitness_df, filename_html, 'result', 
                'Nondominted Sorting Genetic Algorithm2 (NSGA2)')

        best_obj1 = fitness_df['obj1'].min()
        best_obj2 = fitness_df['obj2'].min()
        return [best_obj1, best_obj2]

    def crowding_distance(self, fitness_df, fc, size):
        """ Crowding distance sorting """ 
        self.logger.debug(f"-- crowding distance activated")
        #fitness_df.to_excel('three.xlsx')
        fitness_dff = fitness_df[fitness_df['front']==fc].reset_index(drop=True)
        fitness_dff['cdist'] = 0

        #print(fitness_dff)
        
        # Evaluate how much space is available for the crowding distance
        if fc==1:
            space = config.POPUATION

        else:
            space = config.POPUATION - size

        #print(f"front: {fc}, size: {size}, space: {space}")
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
                    distance = (onedown - oneup) / (max - min)

                    cdists[i] = cdists[i] + distance

            fitness_dff['cdist'] = cdists
                        
        fitness_dff = fitness_dff.sort_values(by=['cdist'], ascending=False).reset_index(drop=True)
        fitness_dff.loc[(fitness_dff.index < (space - 1)),'population'] = 'yes'

        fitness_df2 = fitness_df[fitness_df['front']!=fc].reset_index(drop=True)
        fitness_df3 = pd.concat([fitness_df2, fitness_dff]).reset_index(drop=True)

        fitness_df3 = fitness_df3.set_index('id')
        fitness_df3['id'] = fitness_df3.index

        return fitness_df3

    def crowding_distance_DEPRICATED(self, fitness_df, fc, size):
        # TODO: Use 'at' instead of loc to improve speed
        """ Crowding distance sorting """ 
        self.logger.debug(f"-- crowding distance activated")

        fitness_dff = fitness_df[fitness_df['front']==fc].reset_index(drop=True)

        # Evaluate how much space is available for the crowding distance
        if fc==1:
            space = config.POPUATION

        else:
            space = config.POPUATION - size

        objs = ['obj1', 'obj2']
        fitness_df['cdist'] = 0
        for m in objs:
            # Sort by objective (m) 
            df = fitness_dff.sort_values(by=m, ascending=True).reset_index(drop=True) 

            for i in range(len(df)):
                id = df.id[i]

                if i == 0 or i == len(df)-1:
                    fitness_df.loc[(fitness_df['id']==id),'cdist']= np.inf
                
                else:
                    min = df[m][df.index == 0].iloc[0]
                    max = df[m][df.index == len(df) - 1].iloc[0]

                    oneup = df[m][df.index == (i-1)].iloc[0]
                    onedown = df[m][df.index == (i+1)].iloc[0]
                    distance = (onedown - oneup) / (max - min) 

                    fitness_df.loc[(fitness_df['id']==id),'cdist']=fitness_df['cdist']+distance

        fitness_df = fitness_df.sort_values(by=['cdist'], ascending=False).reset_index(drop=True)
        fitness_df.loc[(fitness_df.index < space),'population']='yes'
        fitness_df = fitness_df.set_index('id')
        fitness_df['id'] = fitness_df.index
        return fitness_df

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
                
                if build_features.GeneticAlgorithmGenetics.dominates((obj1, obj2), (obj1x, obj2x)):
                #if ((obj1 <= obj1x and obj2 <= obj2x) and (obj1 < obj1x or obj2 < obj2x)):
                    dominating_fits[i + ix + 1] += 1 
                    dominated_fits[id].append(idx) 

                if build_features.GeneticAlgorithmGenetics.dominates((obj1x, obj2x), (obj1, obj2)):
                #if ((obj1 >= obj1x and obj2 >= obj2x) and (obj1 > obj1x or obj2 > obj2x)):
                    dominating_fits[i] += 1
                    dominated_fits[idx].append(id)    

            if dominating_fits[i] == 0:
                front.append(id)

        fitness_df['domcount'] = dominating_fits
        fitness_df.loc[(fitness_df.domcount==0), 'front'] = 1
        return fitness_df, front, dominated_fits

    def pareto_nsga2(self, fitness_df):
        """ Decide if new child is worthy of pareto membership 
        Deb 2002
        """
        self.logger.debug(f"- getting fitness")
        
        # Initiate domination count and dominated by list
        self.logger.debug(f"-- getting domcount")

        fitness_df = fitness_df[['id','obj1','obj2']]
        doms = self.get_domcount(fitness_df)
        fitness_df = doms[0]
        front = doms[1]
        dominated_fits = doms[2]

        ###################################################
        # Get front count and determine population status #
        ###################################################
        self.logger.debug(f"-- getting front count")

        # Size of selected solutions
        size = len(fitness_df[fitness_df['front'] == 1])

        # Check if set of sols in front 1 will fit into new population?
        if size > config.POPUATION:
            fitness_df=self.crowding_distance(fitness_df, 1, size)

        elif size == config.POPUATION:
            fitness_df.loc[(fitness_df['front']==1), 'population'] = 'yes'

        # Else continue assigning fronts to solutions
        else:
            fitness_df.loc[(fitness_df['front']==1), 'population'] = 'yes'
            
            fc=2
            while len(front) > 0:
                q1= []  # Solutions in new front
                # Visit each member of previous front
                for p in front:
                    # Visit each member that is dominated by p
                    for q in dominated_fits[p]:
                        dc = fitness_df.at[q, 'domcount']
                        dc = dc - 1
                        fitness_df.at[q, 'domcount'] = dc

                        # Add to the next front if no further domination
                        if dc == 0:
                            q1.append(q)
                            fitness_df.at[q, 'front'] = fc

                # Only for as many fronts as needed to fill popsize
                if (size + len(front)) < config.POPUATION:
                    fitness_df.loc[(fitness_df['front']==fc), 'population'] = 'yes'
                    fc = fc + 1

                # Only for as many fronts as needed to fill popsize
                if ((size + len(front)) > config.POPUATION and len(q1) > 0):
                #if ((size + len(front)) > config.POPUATION and len(front) > 0):
                # TODO: This migh be an issue: check len(q1)
                    fitness_df=self.crowding_distance(fitness_df, fc, size)
                    front = []
                    q1 = []
                    break

                if (size + len(front)) == config.POPUATION:
                    fitness_df.loc[(fitness_df['front']==fc), 'population'] = 'yes'
                    front = []
                    q1 = []
                    break

                size = size + len(front)
                front = q1

        fitness_df=fitness_df[fitness_df['population']=='yes'].reset_index(drop=True)
        return fitness_df


class GeneticAlgorithmMoga:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmMoga")
    gag = GeneticAlgorithmGenetics()
    graph = Visualize()

    def moga(self):
        """ Function that manages the MOGA. """
        self.logger.debug(f"Multi Objective Genetic Algorithm")
        
        p = Population()
        init_pop = p.population(config.POPUATION, 'moga')
        fitness_df = init_pop

        fitness_df['population'] = 'yes'

        self.logger.debug(f"starting MOGA search")
        for _ in range(config.ITERATIONS):
            self.logger.debug(f"ITERATION {_}")
            fitness_df = self.gag.crossover(fitness_df, 'moga')
            fitness_df = self.pareto_moga(fitness_df)

        init_pop['result'] = 'init pop'
        fitness_df['result'] = 'final result'
        
        fitness_df = pd.concat([fitness_df, init_pop])

        fitness_df.to_excel('data/interim/fitness_moga.xlsx', index=False)
        filename_html = 'reports/figures/genetic_algorithm_moga.html'
        self.graph.scatter_plot2(fitness_df, filename_html, 'result', 
                'Multi Objective Genetic Algorithm (MOGA)')

        best_obj1 = fitness_df['obj1'].min()
        best_obj2 = fitness_df['obj2'].min()
        return [best_obj1, best_obj2]

    def pareto_moga(self, fitness_df):
        # TODO: Update with 'at' instead of 'loc' for speed.
        self.logger.debug(f"- getting fitness")

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