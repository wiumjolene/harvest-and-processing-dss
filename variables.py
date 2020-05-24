# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 10:18:12 2019

@author: Jolene
"""

stdunit = 4.5 # each stdunit is so many kg of produce
truck = 1500 # 1 * truck carries so many kg of produce
giveaway = 0.05 # % giveaway
lug = 11 # weight (kg) of a lug
s_unit = truck
zar_workhour = 20
zar_km = 3.16
min_hepc = 800 # minumum % that should be allocated from a specific he to a packhouse


if s_unit == truck:
    lug = truck
else:
    lug = lug

travel_restriction = 400

population_size = 20
generations = 100

mutation_rate = 5

print('### Assumptions ###')
print('-A lug weights ' + str(lug) + 'Kg,')
print('-' + str(truck/lug) + ' lugs fit into a truck,')
print('-One stdunit requires ' + str(round(stdunit * (1+giveaway),1)) 
        + 'Kg of raw produce')
print('-mutation rate: ' + str(mutation_rate))
print('-population size: ' + str(population_size))
print('-generations: ' + str(generations))
print()