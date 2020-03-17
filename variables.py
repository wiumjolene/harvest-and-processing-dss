# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 10:18:12 2019

@author: Jolene
"""

stdunit = 4.5 # each stdunit is so many kg of produce
truck = 300 # 1 * truck carries so many kg of produce
giveaway = 0.05 # % giveaway
lug = 11 # weight (kg) of a lug
s_unit = truck

if s_unit == truck:
    lug = truck
else:
    lug = lug

travel_restriction = 4000

population_size = 5
generations = 8

mutation_rate = 0.05

print('### Assumptions ###')
print('-A lug weights ' + str(lug) + 'Kg,')
print('-' + str(truck/lug) + ' lugs fit into a truck,')
print('-One stdunit requires ' + str(round(stdunit * (1+giveaway),1)) 
        + 'Kg of raw produce')
print('-mutation rate: ' + str(mutation_rate))
print('-population size: ' + str(population_size))
print('-generations: ' + str(generations))
print()