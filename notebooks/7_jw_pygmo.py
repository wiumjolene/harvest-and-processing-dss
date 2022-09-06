import numpy as np # for multi-dimensional containers
import pandas as pd # for DataFrames
import plotly.graph_objects as go # for data visualisation
import platypus as plat # multi-objective optimisation framework
import plotly.express as px

problem = plat.ZDT1()
D = 30
N = 50

solutions = []
for i in range(N):
    solution = plat.Solution(problem)
    solution.variables = np.random.rand(D)
    solution.evaluate()
    
    solutions.append(solution)

x = solutions[0]

print(x)