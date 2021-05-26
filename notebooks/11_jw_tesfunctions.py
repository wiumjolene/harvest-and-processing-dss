
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

p=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

import numpy as np
import pandas as pd
import platypus as plat

from src.features.make_tests import Tests
from src.features.build_features import Individual
from src.models.genetic_algorithm import GeneticAlgorithmMoga, GeneticAlgorithmNsga2, GeneticAlgorithmVega
from src.utils.visualize import Visualize
from src.utils import config
from src.features.build_features import GeneticAlgorithmGenetics

gag = GeneticAlgorithmGenetics()
test=Tests()
graph = Visualize()
ga=GeneticAlgorithmNsga2()
indiv = Individual()

def population(start, size):
    pop=pd.DataFrame()
    for p in range(size):
        ind = indiv.individual(start + p, 'zdt2', test=True)
        pop=pop.append(ind).reset_index(drop=True)
    return pop

fitness_df = population(0, config.POPUATION)
fitness_df['population'] = 'yes'

for i in range(config.ITERATIONS):
    if i % 100 == 0:
        print(i)

    fitness_df = gag.crossover(fitness_df, 'zdt2', test=True)
    fitness_df=ga.pareto_nsga2(fitness_df)

    if i % 1000 == 0:
        graph.scatter_plot2(fitness_df, 'html.html', 'population', f"ZDT1-{i}")

graph.scatter_plot2(fitness_df, 'html.html', 'population', f"ZDT1-final")