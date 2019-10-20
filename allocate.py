# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 14:45:09 2019

@author: Jolene
"""

import pandas as pd
import variables


def allocate_pc(dic_pc,df_ftt,ddic_metadata):
    df_pc = pd.DataFrame.from_dict(dic_pc, orient='index')
    df_pct = df_pc.merge(df_ftt, on = 'packhouse_id')  # get distance from block
    df_pct = df_pct[df_pct['time_id'] == ddic_metadata['time_id']]
    df_pct = df_pct[df_pct['km'] < variables.travel_restriction]
    df_pct = df_pct[df_pct['pack_type_id'] == ddic_metadata['pack_type_id']]
    df_pct = df_pct[df_pct['kg_remain'] >= variables.s_unit]
    df_pctf = df_pct.sort_values(['km']).reset_index(drop=True)
    return(df_pctf)