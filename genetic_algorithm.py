# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 11:00:30 2019

@author: Jolene
"""
import random
import copy

import pandas as pd

import population as pop
import variables
import allocate
import source_etl as setl
from connect import engine_phd

df_dp_imgga = setl.demand_plan()
df_ft_imgga = setl.from_to()
df_he_imgga = setl.harvest_estimate()
dic_pc_imgga = setl.pack_capacity_dic()
df_pc_imgga = setl.pack_capacity()
#df_lugs_imgga = setl.lug_generation()
dic_speed = setl.speed()
demand_options_imgga = pop.create_options(df_dp_imgga, df_pc_imgga,
                                          df_he_imgga)


def genetic_algorithm(dic_solution, fitness, dic_pc_im, demand_options_im,
                      df_dp_im, df_ft_im, df_he_im, ga_num):
    pdic_solution = {}
    p_fitness = {}
          
    pdic_solution = copy.deepcopy(dic_solution)
    p_fitness = copy.deepcopy(fitness)
#    id_num = max(list(pdic_solution.keys())) + 1
    id_num = variables.population_size + 1
    chrom_order = pdic_solution[0]['cdic_chromosome2']['clist_chromosome2_d']
    
    for g in range(variables.generations):
        # make deep copies of dictionaries so as not to update main
        dic_pc_g = copy.deepcopy(dic_pc_im)
        dic_pc_g2 = copy.deepcopy(dic_pc_im)
        dic_pc_g3 = copy.deepcopy(dic_pc_im)
        demand_options_p = copy.deepcopy(demand_options_im)
        
        # create a random to determine if mutation should happen
        mutation_random = random.randint(0,100)
        
        # create new child 1
        child1_nb_gen = allocate.cross_over(pdic_solution, chrom_order,
                                            df_dp_im = df_dp_im,
                                            df_ft_im = df_ft_im,
                                            df_he_im = df_he_im,
                                            dic_pc = dic_pc_g,
                                            dic_pc2 = dic_pc_g2,
                                            dic_speed = dic_speed,
                                            demand_options_x = demand_options_p)
        
        child1_nb = {id_num: child1_nb_gen[0][0]}
        
        # mutate if generation meets mutation criteria
        if mutation_random <= variables.mutation_rate:
            child1_m = allocate.mutation(child1_nb, id_num, 
                                         demand_options_m = demand_options_p,
                                         df_dp_im = df_dp_im,
                                         df_ft_im = df_ft_im,
                                         df_he_im = df_he_im,
                                         dic_pc = dic_pc_g3,
                                         dic_speed = dic_speed)
            
            child1 = child1_m
            
        else:
            child1 = child1_nb
    
        
        # check child1 fitness to assess if it is an improvement
        p_fitness_df = pd.DataFrame.from_dict(p_fitness, orient='index')
        p_fitness_df.loc[(p_fitness_df[0] >= child1[id_num]['cdic_fitness']['obj1']), 'c1obj1eval'] = 1
        p_fitness_df.loc[(p_fitness_df[1] >= child1[id_num]['cdic_fitness']['obj2']), 'c1obj2eval'] = 1
        p_fitness_df['c1eval'] = p_fitness_df['c1obj1eval'] + p_fitness_df['c1obj2eval']
        p_fitness_df = p_fitness_df[p_fitness_df['c1eval'] > 0]
       
        # if it is an improvement in 1 or more objectives, keep and replace with a less suitable
        if len(p_fitness_df) > 0:
            p_fitness_df = p_fitness_df.sort_values(by=['c1eval'],ascending=False).reset_index(drop=False)
            drop_id1 = p_fitness_df['index'][0]
            del p_fitness[drop_id1]
            del pdic_solution[drop_id1]        
        
            pdic_solution.update(child1)
            p_fitness.update({id_num:[child1[id_num]['cdic_fitness']['obj1'],
                                 child1[id_num]['cdic_fitness']['obj2'],
                                 child1[id_num]['cdic_fitness']['kg'],
                                 child1[id_num]['cdic_fitness']['stdunits'],
                                 child1[id_num]['cdic_fitness']['km'],
                                 child1[id_num]['cdic_fitness']['workhours'],
                                 id_num]})
    
    
        id_num = id_num + 1
    
        # create new child 2
        child2 = {id_num: child1_nb_gen[1][0]}
        
        # check child2 fitness to assess if it is an improvemnet
        p_fitness_df2 = pd.DataFrame.from_dict(p_fitness, orient='index')
        p_fitness_df2.loc[(p_fitness_df2[0] >= child2[id_num]['cdic_fitness']['obj1']), 'c2obj1eval'] = 1
        p_fitness_df2.loc[(p_fitness_df2[1] >= child2[id_num]['cdic_fitness']['obj2']), 'c2obj2eval'] = 1
        p_fitness_df2['c2eval'] = p_fitness_df2['c2obj1eval'] + p_fitness_df2['c2obj2eval']
        p_fitness_df2 = p_fitness_df2[p_fitness_df2['c2eval'] > 0]
        
        
        
        # if it is an improvement in 1 or more objectives, keep and replace with a less suitable
        if len(p_fitness_df2) > 0:
            p_fitness_df2 = p_fitness_df2.sort_values(by=['c2eval'],ascending=False).reset_index(drop=False)
            drop_id2 = p_fitness_df2['index'][0]
#            print(p_fitness_df2)
#            print('drop_id = ' + str(drop_id2))
            del p_fitness[drop_id2]
            del pdic_solution[drop_id2]
        
            pdic_solution.update(child2)
            p_fitness.update({id_num:[child2[id_num]['cdic_fitness']['obj1'],
                                 child2[id_num]['cdic_fitness']['obj2'],
                                 child2[id_num]['cdic_fitness']['kg'],
                                 child2[id_num]['cdic_fitness']['stdunits'],
                                 child2[id_num]['cdic_fitness']['km'],
                                 child2[id_num]['cdic_fitness']['workhours'],
                                 id_num]})

        id_num = id_num + 1
               
        
        print('-generation ' + str(int(g)))
    
    ga_dic = {ga_num: {'p_fitness':p_fitness,
                       'pdic_solution': pdic_solution}}
    return(ga_dic)        


ggapopulation = pop.population(demand_options_imgga, 
                              df_dp_imgga, 
                              df_ft_imgga, 
                              df_he_imgga, 
                              dic_pc_imgga,
                              dic_speed)



ggd = genetic_algorithm(dic_solution = ggapopulation['pdic_solution'], 
                             fitness = ggapopulation['p_fitness'], 
                             dic_pc_im = dic_pc_imgga, 
                             demand_options_im = demand_options_imgga,
                             df_dp_im = df_dp_imgga, 
                             df_ft_im = df_ft_imgga, 
                             df_he_im = df_he_imgga, 
                             ga_num = 0)



psur_df = pd.DataFrame.from_dict(ggd[0]['p_fitness'], orient='index')
psur_df['s_source'] = 'generation'
pop_df2 = pd.DataFrame.from_dict(ggapopulation['p_fitness'], orient='index')
pop_df2['s_source'] = 'population'

fitness = pd.concat([pop_df2,psur_df]).reset_index(drop=False)
fitness = fitness.rename(columns={0: 'obj1',1:'obj2',2:'kg',3:'stdunits',4:'km',5:'workhours','index':'solution_num'})

fitness.to_sql('sol_pop_fitness',engine_phd,index_label = 'id',if_exists='replace')


pdic_solution_ids = ggd[0]['pdic_solution']
pdic_solution_ids = list(ggd[0]['pdic_solution'].keys())
solution_df = pd.DataFrame({})
for k in pdic_solution_ids:
    solution = pd.DataFrame.from_dict(ggd[0]['pdic_solution'][k]['ddic_solution'], orient='index')
    solution['solution_num'] = k
    solution_df = pd.concat([solution_df,solution]).reset_index(drop=True)

solution_df.to_sql('sol_solution',engine_phd,index_label = 'id',if_exists='replace')    