import os, sys
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


infile = open(f"{path}\data\interim\ddic_metadata",'rb')
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

