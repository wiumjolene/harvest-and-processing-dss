# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 08:28:37 2019

@author: Jolene
"""

from population import population
from genetic_algorithm import genetic_algorithm
from population import create_options
import source_etl as setl
import pandas as pd
import variables



df_dp_imgga = setl.demand_plan()
df_ft_imgga = setl.from_to()
df_he_imgga = setl.harvest_estimate()
dic_pc_imgga = setl.pack_capacity_dic()
df_pc_imgga = setl.pack_capacity()
df_lugs_imgga = setl.lug_generation()
demand_options_imgga = create_options(df_dp_imgga, df_pc_imgga,
                                          df_he_imgga, df_lugs_imgga)


def greedy_ga(ggapopulation0,ggapopulation1):  
    ggd0 = genetic_algorithm(dic_solution = ggapopulation0['pdic_solution'], 
                         fitness = ggapopulation0['p_fitness'], 
                         dic_pc_im = dic_pc_imgga, 
                         demand_options_im = demand_options_imgga,
                         df_dp_im = df_dp_imgga, 
                         df_ft_im = df_ft_imgga, 
                         df_he_im = df_he_imgga, 
                         ga_num = 0)
    
    ggd1 = genetic_algorithm(dic_solution = ggapopulation1['pdic_solution'], 
                         fitness = ggapopulation1['p_fitness'], 
                         dic_pc_im = dic_pc_imgga, 
                         demand_options_im = demand_options_imgga,
                         df_dp_im = df_dp_imgga, 
                         df_ft_im = df_ft_imgga, 
                         df_he_im = df_he_imgga, 
                         ga_num = 1) 
    
    ggafitness0_df = pd.DataFrame.from_dict(ggd0[0]['p_fitness'], orient='index')  
    ggafitness0_df['source'] = 0
    
    ggafitness1_df = pd.DataFrame.from_dict(ggd1[1]['p_fitness'], orient='index')  
    ggafitness1_df['source'] = 1
    
    ggafitness01_df = ggafitness0_df.append(ggafitness1_df)
    ggafitness01_df['kg_rank'] = ggafitness01_df[1].rank(method='min')
    ggafitness01_df = ggafitness01_df.sort_values(by=['kg_rank',0],ascending=False)
    
    ggafitness01_df = ggafitness01_df.tail(int(variables.population_size)).reset_index(drop=False)
    
    gga_dic_solution = {}
    gga_fitness = {}
    for i in range(0,len(ggafitness01_df)):
        source = ggafitness01_df.source[i]
        source_id = ggafitness01_df['index'][i]
        
        if source == 0:
            p_fitness = ggd0[0]['p_fitness'][source_id]
            pdic_solution = ggd0[0]['pdic_solution'][source_id]
            gga_dic_solution.update({i:pdic_solution})
            gga_fitness.update({i:p_fitness})
        
        if source == 1:
            p_fitness = ggd1[1]['p_fitness'][source_id]
            pdic_solution = ggd1[1]['pdic_solution'][source_id]
            gga_dic_solution.update({i:pdic_solution})
            gga_fitness.update({i:p_fitness})
            
    new_pop = {'p_fitness': gga_fitness,
               'pdic_solution':gga_dic_solution}
    
    return(new_pop)
    

ggapopulation0 = population(demand_options_imgga, 
                              df_dp_imgga, 
                              df_ft_imgga, 
                              df_he_imgga, 
                              dic_pc_imgga)

ggapopulation1 = population(demand_options_imgga, 
                              df_dp_imgga, 
                              df_ft_imgga, 
                              df_he_imgga, 
                              dic_pc_imgga)

ggapopulation2 = population(demand_options_imgga, 
                              df_dp_imgga, 
                              df_ft_imgga, 
                              df_he_imgga, 
                              dic_pc_imgga)

ggapopulation3 = population(demand_options_imgga, 
                              df_dp_imgga, 
                              df_ft_imgga, 
                              df_he_imgga, 
                              dic_pc_imgga)


winner1 = greedy_ga(ggapopulation0,ggapopulation1)

winner2 = greedy_ga(ggapopulation2,ggapopulation3)

winner3 = greedy_ga(winner1,winner2)



