import os, sys
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


filename = f"{path}\data\interim\ddic_metadata"
infile = open(filename,'rb')
ddic_metadata = pickle.load(infile)
infile.close()

filename = f"{path}\data\interim\dlist_ready"
infile = open(filename,'rb')
dlist_ready = pickle.load(infile)
infile.close()

filename = f"{path}\data\interim\ddic_pc"
infile = open(filename,'rb')
ddic_pc = pickle.load(infile)
infile.close()

filename = f"{path}\data\interim\ddic_he"
infile = open(filename,'rb')
ddic_he = pickle.load(infile)
infile.close()