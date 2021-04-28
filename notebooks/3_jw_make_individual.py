import os
import random
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.data.make_dataset import ImportOptions
from src.utils import config

# Import all data sets from pickel files.
options = ImportOptions()

ddf_he = options.demand_harvest()
ddf_he['evaluated'] = 0
ddf_pc = options.demand_capacity()
ddic_metadata = options.demand_metadata()
dlist_allocate = options.demand_ready()
he_dic = options.harvest_estimate()
ft_df = options.from_to()
dic_speed = options.speed()

individualdf = pd.DataFrame()

while len(dlist_allocate) > 0:

    # Randomly choose which d to allocate first
    dpos = random.randint(0, len(dlist_allocate)-1)
    d = dlist_allocate[dpos]
    dkg = ddic_metadata[d]['kg']

    indd_he = []
    indd_pc = []
    indd_kg = []
    indd_kgkm = []
    indd_hrs = []
    while dkg > 0:
        # Filter demand_he table according to d and kg.
        # Check that combination of d_he has not yet been used.
        ddf_het = ddf_he[(ddf_he['demand_id']==d)&(ddf_he['kg_rem']>0)& \
            (ddf_he['evaluated']==0)]

        dhes = ddf_het['id'].tolist()
        dhe_kg_rem = ddf_het['kg_rem'].tolist()

        if len(dhes) > 0:
            # Randomly choose a he that is suitable
            hepos = random.randint(0, len(dhes)-1)
            he = dhes[hepos]
            he_kg_rem = dhe_kg_rem[hepos]

            print(f"he ({he}) -> {int(he_kg_rem)} kg_rem")

            # Calculate kg potential that can be packed
            if he_kg_rem > dkg:
                to_pack = dkg

            else:
                to_pack = he_kg_rem

            # Get closest pc for he from available pc's
            block_id = he_dic[he]['block_id']
            va_id = he_dic[he]['va_id']
            
            # Variables to determine speed -> add calculate the number of hours 
            packtype_id = ddic_metadata[d]['pack_type_id']
            ft_dft = ft_df[ft_df['block_id'] == block_id]

            # Allocate to_pack to pack capacities
            # FIXME: All blocks must be able to go to all packhouses
            while to_pack > 0:
                ddf_pct = ddf_pc[(ddf_pc['demand_id']==d) & (ddf_pc['kg_rem']>0)]
                ddf_pct = ddf_pct.merge(ft_dft, on='packhouse_id', how='left')
                
                # Drop pc with no from to for block
                ddf_pct = ddf_pct.dropna()

                if len(ft_dft) > 0 and len(ddf_pct) > 0:
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

                    try:
                        speed = dic_speed[packhouse_id][packtype_id][va_id]
                    except:
                        speed = 12

                    # Update demand tables with updated capacity
                    ddf_pc.loc[(ddf_pc['id'] == pc), 'kg_rem'] = pckg_rem
                    ddf_he.loc[(ddf_he['id'] == he), 'kg_rem'] = he_kg_rem - packed
                    dkg = dkg - packed

                    indd_he.append(he)
                    indd_pc.append(pc)
                    indd_kg.append(packed)
                    indd_kgkm.append(packed*km)
                    indd_hrs.append(packed*(1*config.GIVEAWAY)*speed/60)

                else:
                    ddf_he.loc[(ddf_he['id'] == he) & (ddf_he['demand_id'] == d), 'evaluated'] = 1
                    break
                        
        else:
            break
    
    dindividual = {'he':indd_he, 'pc':indd_pc, 'kg': indd_kg,
                    'kgkm': indd_kgkm, 'packhours': indd_hrs} 
    individualdft = pd.DataFrame(data=dindividual)      
    individualdft['demand_id'] = d
    individualdft['time_id'] = ddic_metadata[d]['time_id']
    individualdf = pd.concat([individualdf,individualdft])

    # Remove d from list to not alocate it again
    dlist_allocate.remove(d)


# TODO: Calculate fitness
# TODO: Save to disk



# ---------------- FITNESS ---------------- #
#individualdf.to_excel('individualdf.xlsx')

# FIXME: dont pull data everytime 
pc_dic = options.pack_capacity()
pc_df = pd.DataFrame.from_dict(pc_dic, orient='index')

ddic_metadata = options.demand_metadata()
ddf_metadata = pd.DataFrame.from_dict(ddic_metadata, orient='index')
ddf_metadata = ddf_metadata.reset_index(drop=False)
ddf_metadata.rename(columns={'kg':'dkg'},inplace=True)


total_kgkm = individualdf.kgkm.sum()


individualdf2 = individualdf.groupby('pc')['demand_id'].nunique()
individualdf2 = individualdf2.reset_index(drop=False)
individualdf3 = individualdf2.merge(pc_df, left_on='pc', right_on='id', how='left')
individualdf3['changes'] = individualdf3['stdunits_hour'] * individualdf3['demand_id'] 

total_packhours2 = individualdf.packhours.sum() + individualdf3.changes.sum()

total_cost = (total_packhours2*config.ZAR_HR) + (total_kgkm*config.ZAR_KM)

individualdf2 = individualdf.groupby('demand_id')['kg'].sum()
individualdf2 = individualdf2.reset_index(drop=False)
individualdf3 = ddf_metadata.merge(individualdf2, how='left', left_index=True, right_index=True)
individualdf3['kg'].fillna(0, inplace=True)
individualdf3['deviation'] =  abs(individualdf3['dkg'] - individualdf3['kg'])

total_dev = individualdf3.deviation.sum()
# TODO: minimise deviation from demand