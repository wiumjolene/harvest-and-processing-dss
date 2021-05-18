import os
import random
import sys
import logging
import math

import pandas as pd
import numpy as np
from src.features.build_features import Individual
from src.features.build_features import Population
from src.features.build_features import GeneticAlgorithmGenetics
from src.utils.visualize import Visualize
from src.utils import config


class GeneticAlgorithmVega:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmVega")
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

        fitness_df.to_excel('data/interim/fitness_vega.xlsx', index=False)
        filename_html = 'reports/figures/genetic_algorithm_vega.html'
        self.graph.scatter_plot2(fitness_df, filename_html)
        return

    def pareto_vega(self, fitness_df):
        """ Decide if new child is worthy of pareto membership 
        Shaffer 1985
        """
        self.logger.info(f"- getting fitness")
        popsize = config.POPUATION
        # TODO: check legitimacy of this!
        fitness_df=fitness_df.groupby(['obj1','obj2'])['id'].min().reset_index(drop=False)
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

        # TODO: to keep population small uncomment
        #fitness_df = fitness_df[fitness_df['population'] == 'yes']  

        return fitness_df


class GeneticAlgorithmNsga2:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmNsga2")
    gag = GeneticAlgorithmGenetics()
    graph = Visualize()

    def nsga2(self):
        """ Function that manages the NSGA2. """
        self.logger.info(f"Non Dominated Sorting Genetic Algorithm")
        
        p = Population()
        fitness_df = p.population(config.POPUATION, 'nsga2')
        
        # Make child pop out of main population
        while len(fitness_df) < (config.POPUATION * 2):
            fitness_df = self.gag.crossover(fitness_df, 'nsga2')
            self.logger.info(f"making child pop 2n {len(fitness_df)}")

        fitness_df['population'] = 'yes'

        self.logger.info(f"starting NSGA2 search")
        for _ in range(config.ITERATIONS):
            fitness_df = fitness_df[fitness_df['population'] == 'yes'].reset_index(drop=True)
            fitness_df = self.gag.crossover(fitness_df, 'nsga2')
            fitness_df = self.pareto_nsga2(fitness_df)

        fitness_df.to_excel('data/interim/fitness_nsga2.xlsx', index=False)
        filename_html = 'reports/figures/genetic_algorithm_nsga2.html'
        fitness_df['colour'] = fitness_df['front'].astype(str)
        self.graph.scatter_plot2(fitness_df, filename_html, colour='colour')
        return

    def crowding_distance(self, fitness_df, fc, size):
        """ Crowding distance sorting """ 
        fitness_dff = fitness_df[fitness_df['front']==fc].reset_index(drop=True)

        if fc==1:
            space = config.POPUATION
        else:
            space = config.POPUATION - size

        objs = ['obj1', 'obj2']
        fitness_df['cdist'] = 0
        for m in objs:
            df = fitness_dff.sort_values(by=m,ascending=False ).reset_index(drop=True)

            for i in range(len(fitness_dff)):
                id = fitness_dff.id[i]

                if i == 0 or i == len(fitness_dff)-1:
                    fitness_df.loc[(fitness_df['id']==id),'cdist']= np.inf
                
                else:
                    max = df[m][df.index == 0].iloc[0]
                    min = df[m][df.index == len(fitness_dff) - 1].iloc[0]

                    oneup = df[m][df.index == (i-1)].iloc[0]
                    onedown = df[m][df.index == (i+1)].iloc[0]
                    distance = (oneup - onedown) / (max - min)

                    fitness_df.loc[(fitness_df['id']==id),'cdist']=fitness_df['cdist']+distance

        fitness_df = fitness_df.sort_values(by=['cdist'], ascending=False).reset_index(drop=True)
        fitness_df.loc[(fitness_df.index < space),'population']='yes' 
        return fitness_df

    def pareto_nsga2(self, fitness_df):
        """ Decide if new child is worthy of pareto membership 
        Deb 2002
        """
        self.logger.info(f"- getting fitness")
        fitness_df=fitness_df.groupby(['obj1','obj2'])['id'].min().reset_index(drop=False)

        fitness_df['population'] = 'none'
        domination = {}
        front = []
        # Initiate domination count and dominated by list
        for i in range(len(fitness_df)):
            id = fitness_df.id[i]
            obj1 = fitness_df.obj1[i]
            obj2 = fitness_df.obj2[i]
            domcount = 0  # number of sols that dominate cur sol
            domset = []  # set of sols cursol dominates

            for j in range(len(fitness_df)):
                idx = fitness_df.id[j]

                if idx != id:
                    obj1x = fitness_df.obj1[j]
                    obj2x = fitness_df.obj2[j]      

                    if (obj1x <= obj1 and obj2x <= obj2) and (obj1x < obj1 or obj2x < obj2):
                        domcount = domcount + 1
                    else:
                        domset.append(idx)

            domination.update({id:domset})
            fitness_df.loc[(fitness_df['id']==id), 'domcount'] = domcount

            if domcount == 0:  # if part of front 1
                fitness_df.loc[(fitness_df['id']==id), 'front'] = 1
                front.append(id)

        ###################################################
        # Get front count and determine population status #
        ###################################################

        # Size of selected solutions
        size = len(fitness_df[fitness_df['front'] == 1])

        # Check of set of sols in front 1 will fit into new population?
        if size >= config.POPUATION:
            fitness_df=self.crowding_distance(fitness_df, 1, size)

        # Else continue assigning fronts to solutions
        else:
            fitness_df.loc[(fitness_df['front']==1), 'population'] = 'yes'
            fc=2
            while len(front) > 0:
                q1= []  # Solutions in new front

                for p in front:
                    for q in domination[p]:
                        dc = fitness_df['domcount'][fitness_df['id'] == q].iloc[0]
                        dc = dc - 1
                        fitness_df.loc[(fitness_df['id']==q), 'domcount'] = dc

                        if dc == 0:
                            q1.append(q)
                            fitness_df.loc[(fitness_df['id']==q), 'front'] = fc

                # Only for as many fronts as needed to fill popsize
                if size + len(front) >= config.POPUATION:
                    fitness_df=self.crowding_distance(fitness_df, fc, size)
                    
                    break

                else:
                    fitness_df.loc[(fitness_df['front']==fc), 'population'] = 'yes'

                fc = fc + 1
                front = q1
                size = size + len(front)

        fitness_df['front'] = fitness_df['front'].fillna(-99)
        fitness_df=fitness_df.drop(columns=['cdist', 'domcount'])

        return fitness_df



class GeneticAlgorithmMoga:
    logger = logging.getLogger(f"{__name__}.GeneticAlgorithmMoga")
    gag = GeneticAlgorithmGenetics()
    graph = Visualize()

    def moga(self):
        """ Function that manages the MOGA. """
        self.logger.info(f"Multi Objective Genetic Algorithm")
        
        p = Population()
        fitness_df = p.population(config.POPUATION, 'moga')

        fitness_df['population'] = 'yes'

        self.logger.info(f"starting MOGA search")
        for _ in range(config.ITERATIONS):
            fitness_df = self.gag.crossover(fitness_df, 'moga')
            fitness_df = self.pareto_moga(fitness_df)

        fitness_df.to_excel('data/interim/fitness_moga.xlsx', index=False)
        filename_html = 'reports/figures/genetic_algorithm_moga.html'
        fitness_df['colour'] = fitness_df['fitness'].astype(str)
        self.graph.scatter_plot2(fitness_df, filename_html, colour='colour')
        return

    def pareto_moga(self, fitness_df):

        fitness_df = fitness_df[fitness_df['population'] != 'none'].reset_index(drop=True)
        fitness_df=fitness_df.groupby(['obj1','obj2'])['id'].min().reset_index(drop=False)
        fitness_df= fitness_df.sort_values(by=['obj1','obj2']).reset_index(drop=True)

        sshare = config.SSHARE

        ##############################################################################
        # 1. Assign rank based on non-dominated
        #    - rank(indiv, generation) = 1 + number of indivs that dominate indiv
        ##############################################################################
        domination = {}
        # Initiate domination count and dominated by list
        for i in range(len(fitness_df)):
            id = fitness_df.id[i]
            obj1 = fitness_df.obj1[i]
            obj2 = fitness_df.obj2[i]
            domcount = 1  # number of sols that dominate cursol
            domset = []  # set of sols cursol dominates

            for j in range(len(fitness_df)):
                idx = fitness_df.id[j]

                if idx != id:
                    obj1x = fitness_df.obj1[j]
                    obj2x = fitness_df.obj2[j]      

                    if (obj1x <= obj1 and obj2x <= obj2) and (obj1x < obj1 or obj2x < obj2):
                        domcount = domcount + 1
                    else:
                        domset.append(idx)

            domination.update({id:domset})
            fitness_df.loc[(fitness_df['id']==id), 'rank'] = domcount
        #graph.scatter_plot2(fitness_df,'moga.html','rank')

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

        fitness_df.loc[(fitness_df.index < config.POPUATION),'population']='yes'
        fitness_df.loc[(fitness_df.index >= config.POPUATION),'population']='none'

        return fitness_df