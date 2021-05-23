import math

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
TOURSIZE=2  # NB NSGI2 requires binary tournament selection
MUTATIONRATE=5
POPUATION=5
ITERATIONS=20


########################################################
# MOGA CONFIG
########################################################
SSHARE = 1/(math.sqrt(POPUATION)-1)


########################################################
# TESTS
########################################################
D = 30