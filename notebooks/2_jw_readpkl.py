import os, sys
import pickle

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
infile.close() """

infile = open(path + r'\data\processed\dic_speed','rb')
dic_speed = pickle.load(infile)
infile.close()

print(dic_speed)

#infile = open(f"{path}\data\interim\nsga2\id_0",'rb')
infile = open(path + r'\data\interim\nsga2\id_0','rb')
individualdf = pickle.load(infile)
infile.close()

individualdf.to_excel('individualdf.xlsx')