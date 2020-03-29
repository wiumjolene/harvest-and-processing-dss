# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 17:15:32 2020

@author: Jolene
"""

import pandas as pd
from connect import engine_phd

speed = pd.read_excel('venue_speed.xlsx')


dim_va = pd.read_sql('SELECT id as va_id, name as va FROM dss.dim_va;',engine_phd)
dim_packhouse = pd.read_sql('SELECT id as packhouse_id, name as venue FROM dss.dim_packhouse;',engine_phd)
dim_packtype = pd.read_sql('SELECT id as packtype_id, name as s_format FROM dss.dim_pack_type;',engine_phd)

speed['s_format'] = speed['s_format'].str.lower()
speed2 = pd.merge(speed, dim_va, how='left', on='va')
speed2 = pd.merge(speed2, dim_packhouse, how='left', on='venue')
speed2 = pd.merge(speed2, dim_packtype, how='left', on='s_format')

speed2['stdunits.manhour'] = speed2['stdunits.manhour'].round(3)
speed2['speed'] = 60 / speed2['stdunits.manhour']
speed2['speed'] = speed2['speed'].round(3)
speed2['id'] = speed2['id'] + 1

speed3 = speed2.filter(['id', 'packhouse_id', 'packtype_id', 'va_id', 'stdunits.manhour', 'speed'])
speed3.to_sql('f_speed',engine_phd,if_exists='replace',index=False)