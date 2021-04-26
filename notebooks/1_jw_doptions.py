import os, sys
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from src.data.make_dataset import CreateOptions


v = CreateOptions()
df_dp = v.get_demand_plan()
df_he = v.get_harvest_estimate()
df_pc = v.get_pack_capacity()

ddic_pc = {}
ddic_he = {}
ddic_metadata={}
dlist_ready = []

# Loop through demands and get he & pc
for d in range(0,len(df_dp)):
    ddemand_id = df_dp.id[d]
    dvacat_id = df_dp.vacat_id[d]
    dtime_id = int(df_dp.time_id[d])
    dpack_type_id = df_dp.pack_type_id[d]
    dkg_raw = df_dp.kg_raw[d]

    # Find all available harvest estimates for demand 
    ddf_he = df_he[df_he['vacat_id']==dvacat_id]
    ddf_he = ddf_he[ddf_he['time_id']==dtime_id].reset_index(drop=True)
    dlist_he = ddf_he['id'].tolist()
    ddic_he.update({ddemand_id: dlist_he})

    # find all available pack_capacities for demand    
    ddf_pc = df_pc[df_pc['time_id']==dtime_id]
    ddf_pc = ddf_pc[ddf_pc['pack_type_id']==dpack_type_id].reset_index(drop=True)
    dlist_pc = ddf_pc['id'].tolist()
    ddic_pc.update({ddemand_id: dlist_pc})

    # Check if demand has a harvest estimate and pack capacity
    if len(dlist_he) > 0 and len(dlist_pc) > 0:
        ready = 1
        dlist_ready.append(ddemand_id)

    else:
        ready = 0

    # Update metadata
    ddic_metadata.update({ddemand_id: {'vacat_id': dvacat_id,
                                    'time_id': dtime_id,
                                    'pack_type_id': dpack_type_id,
                                    'kg_raw':dkg_raw,
                                    'ready': ready}})

