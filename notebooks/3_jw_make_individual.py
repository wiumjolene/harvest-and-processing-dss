import os
import random
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.data.make_dataset import ImportOptions

# Import all data sets from pickel files.
options = ImportOptions()

ddic_he = options.demand_harvest()
ddic_pc = options.demand_capacity()
ddic_metadata = options.demand_metadata()
dlist_allocate = options.demand_ready()

he_dic = options.harvest_estimate()
pc_dic = options.pack_capacity()
pc_df = pd.DataFrame.from_dict(pc_dic, orient='index')
pc_df['id'] = pc_df.index
ft_df = options.from_to()

for d in dlist_allocate:
    print(d)
    print(ddic_he[d])
    print(ddic_pc[d])
    print('------------------------')
    print(' ')

    dkg = ddic_metadata[d]['kg']

    while dkg > 0:
        if len(ddic_he[d]) > 0:
            hepos = random.randint(0, len(ddic_he[d])-1)
            he = ddic_he[d][hepos]

            if he_dic[he]['kg_rem'] == 0:
                ddic_he[d].remove(he)  # remove he from list to not reuse it
                continue

        else:
            break

        # Calculate kg
        if he_dic[he]['kg_rem'] > dkg:
            # Get the kg that will be packed
            to_pack = dkg
            # Subtract demand from he
            he_dic[he]['kg_rem'] = he_dic[he]['kg_rem'] - dkg
            dkg = 0
            
        else:
            # Get the kg that will be packed
            to_pack = he_dic[he]['kg_rem']
            # Subtract he from demand
            dkg = dkg - he_dic[he]['kg_rem']
            he_dic[he]['kg_rem'] = 0
            ddic_he[d].remove(he)


        # Get closest pc for he from available pc's
        block_id = he_dic[he]['block_id']
        
        # Variables to determine speed  -> add calculate the number of hours 
        va_id = he_dic[he]['va_id']
        packtype_id = ddic_metadata[d]['pack_type_id']
        
        ft_dft = ft_df[ft_df['block_id'] == block_id]

        # Allocate to_pack to pack capacities
        while to_pack > 0:
            pc_dft = pc_df[pc_df['time_id'] == ddic_metadata[d]['time_id']]
            pc_dft = pc_dft[pc_dft['pack_type_id'] == packtype_id]
            pc_dft = pc_dft[pc_dft['kg_rem'] > 0]

            if len(ft_dft) > 0 and len(pc_dft):
                pc_dft = pc_dft.merge(ft_dft, on='packhouse_id', how='left')
                pcf_dft = pc_dft.sort_values(['km']).reset_index(drop=True)

                # allocate closest pc to block
                dhe_pc = pcf_dft.id[0]
                packhouse_id = pcf_dft.packhouse_id[0]
                km = pcf_dft.km[0]
                pckg_rem = pcf_dft.kg_rem[0]

                if pckg_rem > to_pack:
                    pckg_rem = pckg_rem - to_pack
                    to_pack = 0

                else:
                    to_pack = to_pack - pckg_rem
                    pckg_rem = 0


            else:
                break
            
            