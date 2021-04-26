# -*- coding: utf-8 -*-
import logging
import pickle

from src.utils import config
from src.utils.connect import DatabaseModelsClass


class CreateOptions:
    logger = logging.getLogger(f"{__name__}.CreateOptions")
    database_instance = DatabaseModelsClass('PHDDATABASE_URL')

    def make_options(self):
        df_dp = self.get_demand_plan()
        df_he = self.get_harvest_estimate()
        df_pc = self.get_pack_capacity()

        self.logger.info('- make_options')
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
                dlist_ready.append(d)

            else:
                ready = 0

            # Update metadata
            ddic_metadata.update({ddemand_id: {'vacat_id': dvacat_id,
                                            'time_id': dtime_id,
                                            'pack_type_id': dpack_type_id,
                                            'kg_raw':dkg_raw,
                                            'ready': ready}})

        # Save nb datasets to interim for use in algorithms
        outfile = open('data/interim/ddic_metadata','wb')
        pickle.dump(ddic_metadata,outfile)
        outfile.close()

        outfile = open('data/interim/ddic_he','wb')
        pickle.dump(ddic_he,outfile)
        outfile.close()

        outfile = open('data/interim/ddic_pc','wb')
        pickle.dump(ddic_pc,outfile)
        outfile.close()

        outfile = open('data/interim/dlist_ready','wb')
        pickle.dump(dlist_ready,outfile)
        outfile.close()

        return 

    def get_demand_plan(self): 
        """ Extract demand requirment from database. """
        self.logger.info('- get_demand_plan')

        s = f"""SELECT 
                fdp.id,
                fdp.client_id,
                fdp.vacat_id,
                fdp.pack_type_id,
                fdp.priority,
                fdp.arrivalweek,
                w.id AS arrival_time_id,
                fdp.stdunits,
                fdp.transitdays,
                w.id - (ceiling(fdp.transitdays/7) * 7) as time_id
            FROM
                dss.f_demand_plan fdp
                    LEFT JOIN
                dim_week w ON fdp.arrivalweek = w.week
            WHERE w.season = {config.SEASON}
            """
            
        df_dp = self.database_instance.select_query(query_str=s)
        df_dp['kg_raw'] = df_dp['stdunits'] * config.STDUNIT * (1 + config.GIVEAWAY)
        df_dp = df_dp.sort_values(by=['time_id', 'priority']).reset_index(drop=True)
        df_dp['trucks_raw'] = df_dp['kg_raw'] /config.TRUCK
        return df_dp

    def get_harvest_estimate(self): 
        """ Get harvest estimate. """
        self.logger.info('- get_harvest_estimate')

        s= f"""SELECT he.id, he.va_id, va.vacat_id, he.block_id, w.id AS time_id, he.kg_raw
            FROM dss.f_harvest_estimate he
            LEFT JOIN dim_week w ON he.packweek = w.week
            LEFT JOIN dim_va va ON he.va_id = va.id
            WHERE kg_raw>0 AND w.season={config.SEASON};
            """

        df_he = self.database_instance.select_query(query_str=s)
        df_he['stdunits'] = (df_he['kg_raw'] * (1 - config.GIVEAWAY)) / config.STDUNIT
        df_he['trucks_raw'] = df_he['kg_raw'] / config.TRUCK
        df_he['lugs_raw'] = df_he['kg_raw'] / config.LUG
        return df_he

    def get_pack_capacity(self): 
        """ Get pack capacities. """
        self.logger.info('- get_pack_capacity')

        s = f"""SELECT 
            pc.id,
            pc.packhouse_id,
            pc.pack_type_id,
            w.id AS time_id,
            pc.kg,
            pc.stdunits
        FROM
            dss.f_pack_capacity pc
                LEFT JOIN
            dim_week w ON pc.packweek = w.week
            WHERE w.season = {config.SEASON};
            """

        df_pc = self.database_instance.select_query(query_str=s)
        df_pc['stdunits'] = df_pc['kg'] / config.STDUNIT
        df_pc['trucks_raw'] = (df_pc['kg'] * (1 + config.GIVEAWAY))/config.TRUCK
        return df_pc 
