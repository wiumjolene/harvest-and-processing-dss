# -*- coding: utf-8 -*-
import logging
from src.utils.connect import DatabaseModelsClass
from src.utils import config


class CreateOptions:
    logger = logging.getLogger(f"{__name__}.CreateOptions")
    database_instance = DatabaseModelsClass('PHDDATABASE_URL')

    def make_options(self):
        self.logger.info('Get all data sets for options')
        demands = self.get_demand_plan()
        harvest = self.get_harvest_estimate()
        capacity = self.get_pack_capacity()

        self.logger.info('Make options')
        return [demands, harvest, capacity]

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

        s= f"""SELECT he.id, he.va_id, he.block_id, w.id AS time_id, he.kg_raw
            FROM dss.f_harvest_estimate he
            LEFT JOIN dim_week w ON he.packweek = w.week
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
