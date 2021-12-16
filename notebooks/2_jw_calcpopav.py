import os, sys
import pickle
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


""" infile = open(f"{path}\data\interim\ddic_metadata",'rb')
ddic_metadata = pickle.load(infile)
infile.close()

infile = open(f"{path}\data\interim\dlist_ready",'rb')
dlist_ready = pickle.load(infile)
infile.close()

infile = open(f"{path}\data\interim\ddic_pc",'rb')
ddic_pc = pickle.load(infile)
infile.close()

infile = open(f"{path}\data\interim\ddic_he",'rb')
ddic_he = pickle.load(infile)
infile.close() 

infile = open(path + r'\data\processed\dic_speed','rb')
dic_speed = pickle.load(infile)
infile.close()

#print(dic_speed)
"""

avs=[]
val_2=[]
for i in range(0, 33295):
    #infile = open(f"{path}\data\interim\nsga2\id_0",'rb')
    infile = open(f"{path}\data\interim\zdt1\\nsga2\id_{i}",'rb')
    individualdf = pickle.load(infile)
    infile.close()

    vals=list(individualdf.value)
    val_2.append(vals[2])

    if i % 1000 == 0:
        print(i)
        avs.append(sum(val_2)/len(val_2))
        val_2=[]


averages=pd.DataFrame(data=avs, columns=['averages'])

averages.to_excel('averages.xlsx')