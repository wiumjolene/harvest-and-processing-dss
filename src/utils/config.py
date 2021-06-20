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
TOURSIZE=3  # NB NSGI2 requires binary tournament selection
MUTATIONRATE=0.08
MUTATIONRATE2=0.05
CROSSOVERRATE=0.5
POPUATION=100
ITERATIONS=20000


########################################################
# MOGA CONFIG
########################################################
SSHARE = 1/(math.sqrt(POPUATION)-1)


########################################################
# TESTS
########################################################
D = 30

# ssh root@159.65.247.178
# cd phd/workdir/
# ~/agrihub/api/env/bin/python run.py