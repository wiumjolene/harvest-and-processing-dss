# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 10:18:12 2019

@author: Jolene
"""

stdunit = 1.5 # each stdunit is so many kg of produce
truck = 5 # 1 * truck carries so many kg of produce
giveaway = 0.05 # % giveaway
lug = 1 # weight (kg) of a lug
s_unit = lug
travel_restriction = 100

print('### Assumptions ###')
print('A lug weights ' + str(lug) + 'Kg,')
print(str(truck/lug) + ' lugs fit into a truck,')
print('One stdunit requires ' + str(round(stdunit * (1+giveaway),1)) + 'Kg of raw produce')
