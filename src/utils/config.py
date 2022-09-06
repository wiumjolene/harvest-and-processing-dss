import math
import os

# show graphs
SHOW=True 
SHOWRATE = 5000

STDUNIT=4.5 # each stdunit is so many kg of produce
GIVEAWAY=0.05 # % giveaway
TRUCK=1500 # 1 * truck carries so many kg of produce
LUG=11 # weight (kg) of a lug
SEASON=2022

#ZAR_HR=20
ZAR_HR=0
ZAR_KM=3.16/1000

########################################################
# GA CONFIG
########################################################
#SELECTION='tournament'
SELECTION='nondom'
TOURSIZE=2  # NB NSGI2 requires binary tournament selection


MUTATIONRATE=0.3
MUTATIONRATE2=0.08
CROSSOVERRATE=0.39

"""
MUTATIONRATE=0.12
MUTATIONRATE2=0.08
CROSSOVERRATE=0.35
"""


CROSSOVERTYPE='crossover_BITFLIP'
#CROSSOVERTYPE='crossover_CROSSGEN'


POPUATION=80 #TODO:
CHILDREN = 80
ITERATIONS=30000 #TODO:
#LEVEL='DAY'
LEVEL='WEEK'

########################################################
# MOGA CONFIG
########################################################
SSHARE = 1/(math.sqrt(POPUATION)-1)


########################################################
# TESTS
########################################################
#D = 30

SAMPLESTART = 25
SAMPLEEND = 30 # number of tests for t-test sample #TODO:

ROOTDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
print(ROOTDIR)