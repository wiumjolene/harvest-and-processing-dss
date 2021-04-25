import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from src.data.make_dataset import CreateOptions


v = CreateOptions()
df = v.get_demand_plan()
df1 = v.get_harvest_estimate()
df2 = v.get_pack_capacity()


