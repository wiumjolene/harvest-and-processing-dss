import math

# show graphs
SHOW=True  #TODO:
SHOWRATE = 10000

STDUNIT=4.5 # each stdunit is so many kg of produce
GIVEAWAY=0.05 # % giveaway
TRUCK=1500 # 1 * truck carries so many kg of produce
LUG=11 # weight (kg) of a lug
SEASON=2020

ZAR_HR=20
ZAR_KM=3.16/1000

########################################################
# GA CONFIG
########################################################
TOURSIZE=3  # NB NSGI2 requires binary tournament selection
MUTATIONRATE=0.05
MUTATIONRATE2=0.05
CROSSOVERRATE=0.6
POPUATION=80 #TODO:
ITERATIONS=10000 #TODO:


########################################################
# MOGA CONFIG
########################################################
SSHARE = 1/(math.sqrt(POPUATION)-1)


########################################################
# TESTS
########################################################
D = 30

SAMPLESTART = 0
SAMPLEEND = 1 # number of tests for t-test sample #TODO:

