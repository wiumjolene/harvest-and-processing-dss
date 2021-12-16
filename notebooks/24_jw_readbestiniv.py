import os, sys
import pickle
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


id = 8122
infile = open(f"{path}\data\interim\\nsga2\\id_{id}",'rb')

individualdf = pickle.load(infile)
infile.close()

individualdf.to_excel(f"plan_bestsol.xlsx")