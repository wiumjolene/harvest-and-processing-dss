import numpy as np
import pandas as pd
import plotly.graph_objects as go
import platypus as plat



problem = plat.ZDT1()
algorithm = plat.NSGAII(problem)

algorithm.run(2000)

for solution in algorithm.result:
    print(solution.objectives)


objective_values = np.empty((0, 2))
for solution in algorithm.result:
    y = solution.objectives
    objective_values = np.vstack([objective_values, y])

# convert to DataFrame
objective_values = pd.DataFrame(objective_values, columns=['f1','f2'])

fig = go.Figure()
fig.add_scatter(x=objective_values.f1, y=objective_values.f2, mode='markers')
fig.show()


##############################################################################

problem = plat.ZDT1()
solution = plat.Solution(problem)

D = 30
x = np.random.rand(D)
N = 50

solutions = []
for i in range(N):
    solution = plat.Solution(problem)
    solution.variables = np.random.rand(D)
    solution.evaluate()
    solutions.append(solution)


plat.nondominated_sort(solutions)

solutions_df = pd.DataFrame(index=range(N),columns=['f1','f2','front_rank'])

for i in range(N):
    solutions_df.loc[i].f1 = solutions[i].objectives[0]
    solutions_df.loc[i].f2 = solutions[i].objectives[1]
    solutions_df.loc[i].front_rank = solutions[i].rank




##############################################################################

def ZDT1(x):
    f1 = x[0] # objective 1
    g = 1 + 9 * np.sum(x[1:D] / (D-1))
    h = 1 - np.sqrt(f1/g)
    f2 = g * h # objective 2
    return [f1, f2]

N = 50
D = 30
D_lower = np.zeros((1, D))
D_upper = np.ones((1, D))
M = 2

X = pd.DataFrame(np.random.uniform(low=D_lower, high=D_upper, size=(N,D)))
X.head(5) # Show only the first 5 solutions

Y = np.empty((0, 2))
for n in range(N):
    y = ZDT1(X.iloc[n])
    Y = np.vstack([Y, y])

# convert to DataFrame
Y = pd.DataFrame(Y, columns=['f1','f2'])
Y.head(5) # Shows only first 5 sets of objective values

fig = go.Figure(layout=dict(xaxis=dict(title='f1'),yaxis=dict(title='f2')))
# This is not how we would normally plot this data.
# Here, it is done this way so that the colours match those in the
# visualisation below.
for index, row in Y.iterrows():
    fig.add_scatter(x=[row.f1], y=[row.f2],
        name=f'solution {index+1}', mode='markers')
fig.show()