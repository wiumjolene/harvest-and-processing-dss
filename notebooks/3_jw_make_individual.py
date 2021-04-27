import os
import random
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.data.make_dataset import ImportOptions

# Import all data sets from pickel files.
options = ImportOptions()

ddf_he = options.demand_harvest()
ddf_he['evaluated'] = 0
ddf_pc = options.demand_capacity()
ddic_metadata = options.demand_metadata()
dlist_allocate = options.demand_ready()
he_dic = options.harvest_estimate()
ft_df = options.from_to()

individualdf = pd.DataFrame()

while len(dlist_allocate) > 0:

    # Randomly choose which d to allocate first
    dpos = random.randint(0, len(dlist_allocate)-1)
    d = dlist_allocate[dpos]
    print(f"{d}: {int(ddic_metadata[d]['kg'])} kg")
    dkg = ddic_metadata[d]['kg']

    individuald_he = []
    individuald_pc = []
    individuald_kg = []
    while dkg > 0:
        # Filter demand_he table according to d and kg.
        # Check that combination of d_he has not yet been used.
        ddf_het = ddf_he[(ddf_he['demand_id']==d) & (ddf_he['kg_rem']>0) & \
            (ddf_he['evaluated']==0)]
        dhes = ddf_het['id'].tolist()
        dhe_kg_rem = ddf_het['kg_rem'].tolist()

        if len(dhes) > 0:
            # Randomly choose a he that is suitable
            hepos = random.randint(0, len(dhes)-1)
            he = dhes[hepos]
            he_kg_rem = dhe_kg_rem[hepos]

            print(f"he ({he}) -> {int(he_kg_rem)} kg_rem")

            if he_kg_rem == 0:
                ddf_he.loc[(ddf_he['id'] == he) & (ddf_he['demand_id'] == d), 'evaluated'] = 1
                continue

            # Calculate kg potential that can be packed
            if he_kg_rem > dkg:
                to_pack = dkg

            else:
                to_pack = he_kg_rem

            # Get closest pc for he from available pc's
            block_id = he_dic[he]['block_id']
            
            # Variables to determine speed -> add calculate the number of hours 
            packtype_id = ddic_metadata[d]['pack_type_id']
            ft_dft = ft_df[ft_df['block_id'] == block_id]

            # Allocate to_pack to pack capacities
            while to_pack > 0:
                ddf_pct = ddf_pc[(ddf_pc['demand_id']==d) & (ddf_pc['kg_rem']>0)]

                if len(ft_dft) > 0 and len(ddf_pct) > 0:
                    ddf_pct = ddf_pct.merge(ft_dft, on='packhouse_id', how='left')
                    ddf_pct = ddf_pct.sort_values(['km']).reset_index(drop=True)

                    # Allocate closest pc to block
                    pc = ddf_pct.id[0]
                    packhouse_id = ddf_pct.packhouse_id[0]
                    km = ddf_pct.km[0]
                    pckg_rem = ddf_pct.kg_rem[0]

                    if pckg_rem > to_pack:
                        packed = to_pack
                        pckg_rem = pckg_rem - to_pack
                        to_pack = 0

                    else:
                        packed = pckg_rem
                        to_pack = to_pack - pckg_rem
                        pckg_rem = 0

                    # Update demand tables with updated capacity
                    ddf_pc.loc[(ddf_pc['id'] == pc), 'kg_rem'] = pckg_rem
                    ddf_he.loc[(ddf_he['id'] == he), 'kg_rem'] = he_kg_rem - packed
                    dkg = dkg - packed

                    individuald_he.append(he)
                    individuald_pc.append(pc)
                    individuald_kg.append(packed)

                else:
                    ddf_he.loc[(ddf_he['id'] == he) & (ddf_he['demand_id'] == d), 'evaluated'] = 1
                    break
                        
        else:
            break
    
    dindividual = {'he':individuald_he, 'pc':individuald_pc, 'kg': individuald_kg} 
    individualdft = pd.DataFrame(data=dindividual)      
    individualdft['demand_id'] = d
    individualdft['time_id'] = ddic_metadata[d]['time_id']
    individualdf = pd.concat([individualdf,individualdft])

    # Remove d from list to not alocate it again
    dlist_allocate.remove(d)

    print(f"     {int(dkg)} not packed")
    print('------------------------')
    print(' ')

# TODO: Calculate fitness
# TODO: Save to disk