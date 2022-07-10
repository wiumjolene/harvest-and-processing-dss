import os, sys
import pickle
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print(path)

id = 49
infile = open(f"{path}\data\interim\\nsga2\\id_{id}",'rb')

individualdf = pickle.load(infile)
infile.close()

individualdf.to_excel(f"plan_bestsol.xlsx")




infile = open(f"{path}/data/processed/ddf_he",'rb')

df = pickle.load(infile)
infile.close()

#df.to_excel(f"ddf_he.xlsx")
