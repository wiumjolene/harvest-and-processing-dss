# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 08:28:37 2019

@author: Jolene
"""

import genetic_algorithm as ga
import feasible_options as fo
import source_etl as setl
import pandas as pd
import variables

demand_options_imgga = fo.create_options()
df_dp_imgga = setl.demand_plan()
df_ft_imgga = setl.from_to()
df_he_imgga = setl.harvest_estimate()
dic_pc_imgga = setl.pack_capacity_dic()

ggapopulation1 = ga.population(demand_options_imgga, 
                              df_dp_imgga, 
                              df_ft_imgga, 
                              df_he_imgga, 
                              dic_pc_imgga)
ggd1 = ga.genetic_algorithm(dic_solution = ggapopulation1['pdic_solution'], 
                     fitness = ggapopulation1['p_fitness'], 
                     dic_pc_im = dic_pc_imgga, 
                     demand_options_im = demand_options_imgga,
                     df_dp_im = df_dp_imgga, 
                     df_ft_im = df_ft_imgga, 
                     df_he_im = df_he_imgga, 
                     ga_num = 0)

ggapopulation2 = ga.population(demand_options_imgga, 
                              df_dp_imgga, 
                              df_ft_imgga, 
                              df_he_imgga, 
                              dic_pc_imgga)
ggd2 = ga.genetic_algorithm(dic_solution = ggapopulation2['pdic_solution'], 
                     fitness = ggapopulation2['p_fitness'], 
                     dic_pc_im = dic_pc_imgga, 
                     demand_options_im = demand_options_imgga,
                     df_dp_im = df_dp_imgga, 
                     df_ft_im = df_ft_imgga, 
                     df_he_im = df_he_imgga, 
                     ga_num = 1) 

ggafitness1_df = pd.DataFrame.from_dict(ggapopulation1['p_fitness'], orient='index')  
ggafitness1_df['source'] = 1

ggafitness2_df = pd.DataFrame.from_dict(ggapopulation2['p_fitness'], orient='index')  
ggafitness2_df['source'] = 2

ggafitness12_df = ggafitness1_df.append(ggafitness2_df).reset_index(drop=True)
ggafitness12_df['kg_rank'] = ggafitness12_df[1].rank(method='min')
ggafitness12_df = ggafitness12_df.sort_values(by=['kg_rank',0],ascending=False).reset_index(drop=True)

ggafitness12_df = ggafitness12_df.tail(int(variables.population_size))

check if in




