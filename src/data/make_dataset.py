# -*- coding: utf-8 -*-
import logging
import os
import pickle
import json
import sys
import datetime

import pandas as pd
from src.utils import config
from src.utils.connect import DatabaseModelsClass


class ManageSeasonRun:
    """ Class to manage the data for 
        a complete season run
    """
    database_dss = DatabaseModelsClass('PHDDATABASE_URL')

    def get_season_run(self):
        sql=f"""
        SELECT plan_date, week, make_plan, horizon
        FROM dss.run_season
        WHERE horizon = 1
        ORDER BY plan_date
        ;
        """
        df=self.database_dss.select_query(sql)
        return df

    def get_plan_dates(self):
        sql=f"""
        SELECT plan_date, week, make_plan, horizon
        FROM dss.run_season
        WHERE make_plan = 1
        ORDER BY plan_date
        ;
        """
        df=self.database_dss.select_query(sql)
        return df

    def update_plan_complete(self, plan_date):
        sql=f"""
        UPDATE `dss`.`run_season` 
        SET `runtime` = now(), `make_plan` = '0', `horizon` = '0'
        WHERE (`plan_date` = '{plan_date}');
        """
        self.database_dss.execute_query(sql)
        return

    def update_horizon_complete(self):
        sql=f"""
        UPDATE `dss`.`run_season` 
        SET `horizon` = '0';
        """
        self.database_dss.execute_query(sql)
        return


class GetLocalData:
    """ Class to extract planning data from local backups
        into model structures.
    """
    logger = logging.getLogger(f"{__name__}.GetLocalData")
    database_dss = DatabaseModelsClass('PHDDATABASE_URL')
    
    def get_local_he(self, plan_date, weeks_str):
        sql2=f"""
            SELECT dim_block.id as block_id
                , dim_va.id as va_id
                , Week as packweek
                -- , ROUND(SUM(GrossEstimate * 1000),1) as kg_raw
                , SUM(kgGross) as kg_raw
            FROM dss.harvest_estimate_0638_data as he
            LEFT JOIN dim_fc ON (he.Grower = dim_fc.name)
            LEFT JOIN dim_block 
				ON ((CASE WHEN Orchard = '' THEN concat(Grower,"-",Variety) ELSE Orchard END) = dim_block.name 
					AND dim_block.fc_id = dim_fc.id)
            LEFT JOIN dim_va ON (he.Variety = dim_va.name)
            WHERE extract_datetime = (SELECT MAX(extract_datetime) 
                FROM dss.harvest_estimate_0638_data WHERE date(extract_datetime)='{plan_date}')
            AND estimatetype = 'ADJUSTMENT'
            AND kgGross > 0
            AND he.Week in ({weeks_str})
            GROUP BY dim_fc.id, dim_block.id, dim_va.id, Week
            ;         
        """

        sql2=f"""
            SELECT dim_block.id as block_id
                , dim_va.id as va_id
                , week as packweek
                , SUM(kg) as kg_raw
            FROM dss.harvest_estimate_quicadj_data as he
            LEFT JOIN dim_va ON (he.va = dim_va.name)
            LEFT JOIN dim_fc ON (he.fc = dim_fc.name)
            LEFT JOIN dim_block 
			ON ((CASE WHEN oc = '' THEN concat(fc,"-",va) ELSE oc END) = dim_block.name 
			 		AND dim_block.fc_id = dim_fc.id
			 		AND dim_block.va_id = dim_va.id)
            WHERE extract_datetime = (SELECT MAX(extract_datetime) 
               FROM dss.harvest_estimate_quicadj_data WHERE date(extract_datetime)='{plan_date}')
            AND kg > 0
            AND he.week in ({weeks_str})
            GROUP BY dim_block.id, dim_va.id, week;       
        """

        sql=f"""
            SELECT dim_block.id as block_id
                , dim_va.id as va_id
                , week as packweek
                , SUM(kg) as kg_raw
            FROM dss.harvest_estimate_budget as he
            LEFT JOIN dim_va ON (he.va = dim_va.name)
            LEFT JOIN dim_fc ON (he.fc = dim_fc.name)
            LEFT JOIN dim_block 
			ON ((CASE WHEN oc = '' THEN concat(fc,"-",va) ELSE oc END) = dim_block.name 
			 		AND dim_block.fc_id = dim_fc.id
			 		AND dim_block.va_id = dim_va.id)
            WHERE extract_datetime = (SELECT MAX(extract_datetime) 
               FROM dss.harvest_estimate_budget WHERE date(extract_datetime)='{plan_date}')
            AND kg > 0
            AND he.week in ({weeks_str})
            AND (dim_fc.management in ('Karsten', 'Manage') OR fc = 'Y0294')
            GROUP BY dim_block.id, dim_va.id, week;       
        """

        df = self.database_dss.select_query(sql)
        df['plan_date'] = plan_date
        return df

    def get_he_fc(self):
        sql="""
            SELECT DISTINCT Grower as name
                , dim_fc.id
            FROM dss.harvest_estimate_0638_data
            LEFT JOIN dim_fc ON (harvest_estimate_0638_data.Grower = dim_fc.name)
            WHERE dim_fc.id is NULL
            AND extract_datetime = (SELECT MAX(extract_datetime) FROM dss.harvest_estimate_0638_data);   
        """
        df = self.database_dss.select_query(sql)
        df['add_datetime'] = datetime.datetime.now()
        return df

    def get_he_block(self):
        sql="""
              SELECT DISTINCT CASE WHEN Orchard = '' THEN concat(Grower,"-",Variety) ELSE Orchard END as name
				, dim_productionunit.id as pu_id
                , dim_fc.id as fc_id
                , dim_va.id as va_id
            FROM dss.harvest_estimate_0638_data
            LEFT JOIN dim_fc ON (harvest_estimate_0638_data.Grower = dim_fc.name)
            LEFT JOIN dim_productionunit ON (harvest_estimate_0638_data.Farm = dim_productionunit.name AND dim_fc.id = dim_productionunit.fc_id)
            LEFT JOIN dim_block 
				ON ((CASE WHEN Orchard = '' THEN concat(Grower,"-",Variety) ELSE Orchard END) = dim_block.name AND dim_block.fc_id = dim_fc.id)
            LEFT JOIN dim_va ON (harvest_estimate_0638_data.Variety = dim_va.name)
            WHERE dim_block.id is NULL
            AND extract_datetime = (SELECT MAX(extract_datetime)
                FROM dss.harvest_estimate_0638_data);
        """
        df = self.database_dss.select_query(sql)
        df['add_datetime'] = datetime.datetime.now()
        return df

    def get_he_va(self):
        sql="""
			SELECT DISTINCT Variety as name
            FROM dss.harvest_estimate_0638_data
            LEFT JOIN dim_va ON (harvest_estimate_0638_data.Variety = dim_va.name)
            WHERE (dim_va.id is NULL and Variety is not NULL)
            AND extract_datetime = (SELECT MAX(extract_datetime)FROM dss.harvest_estimate_0638_data); 
        """
        df = self.database_dss.select_query(sql)
        df['add_datetime'] = datetime.datetime.now()
        return df

    def get_dp_client(self):
        sql="""
            SELECT DISTINCT targetmarket as name
            FROM dss.planning_data
            LEFT JOIN dim_client ON (planning_data.targetmarket = dim_client.name)
            WHERE dim_client.id is NULL
            AND extract_datetime = (SELECT MAX(extract_datetime)FROM dss.planning_data)
            AND recordtype = 'DEMAND';
        """
        df = self.database_dss.select_query(sql)
        df['add_datetime'] = datetime.datetime.now()
        return df

    def get_local_dp(self, plan_date, weeks_str):
        sql=f"""
            SELECT demandid as demand_id
                , dim_client.id as client_id
                , dim_vacat.id as vacat_id
                , dim_pack_type.id as pack_type_id
                , dim_client.priority
                -- , IF(priority= "-", 0, priority) as priority
                , demand_arrivalweek as arrivalweek
                , dim_time.week as packweek
                -- , dim_client.transitdays as transitdays
                , transitdays.transitdays
                , concat(cartontype, "-", innerpacking, "-", brand) as packaging
                , round(qty_standardctns) as stdunits
            FROM dss.planning_data
            LEFT JOIN dim_client ON (planning_data.targetmarket = dim_client.name)
            LEFT JOIN dim_vacat ON (planning_data.varietygroup = dim_vacat.name)
            LEFT JOIN dim_week ON (planning_data.demand_arrivalweek = dim_week.week)
            LEFT JOIN transitdays ON (planning_data.demandid = transitdays.recordno AND date(extract_datetime) = transitdays.plan_date)
            LEFT JOIN dim_time ON ((date_sub(dim_week.weekstart,  INTERVAL transitdays.transitdays DAY)) = dim_time.day)
            LEFT JOIN dim_pack_type ON ((IF((SUBSTR(cartontype, 1, 1) = 'A'),
                        IF((cartontype = 'A75F'),
                            'LOOSE',
                            'PUNNET'),
                        'LOOSE')) = dim_pack_type.name)
            WHERE extract_datetime = (SELECT MAX(extract_datetime)
                                        FROM dss.planning_data WHERE date(extract_datetime)='{plan_date}')
            AND dim_time.week in ({weeks_str})
            AND recordtype = 'DEMAND'
            ;
        """
        
        df = self.database_dss.select_query(sql)
        df['plan_date'] = plan_date
        return df

    def get_pc_packhouse(self):
        sql=f"""
            SELECT distinct phc as name
            FROM dss.pack_capacity_data
            LEFT JOIN dim_packhouse ON (pack_capacity_data.phc = dim_packhouse.name)
            WHERE dim_packhouse.id is NULL
            AND extract_datetime = (SELECT MAX(extract_datetime)
                FROM dss.pack_capacity_data);
        """
        df = self.database_dss.select_query(sql)
        df['add_datetime'] = datetime.datetime.now()
        return df

    def get_local_pc_TRUNCATE(self, plan_date, weeks_str):
        sql=f"""
            SELECT dim_packhouse.id as packhouse_id
                , dim_pack_type.id as pack_type_id
                , packweek
                , noofstdcartons as stdunits
                , noofstdcartons as stdunits_source
            FROM dss.pack_capacity_data
            LEFT JOIN dim_packhouse ON (pack_capacity_data.phc = dim_packhouse.name)
            LEFT JOIN dim_pack_type ON (pack_capacity_data.packformat = dim_pack_type.name)
            WHERE extract_datetime = (SELECT MAX(extract_datetime)
                FROM dss.pack_capacity_data WHERE date(extract_datetime)='{plan_date}')
            AND pack_capacity_data.packweek in ({weeks_str});
        """
        
        df = self.database_dss.select_query(sql)
        df['plan_date'] = plan_date
        return df

    def get_local_pc_day_TRUNCATE(self, plan_date, weeks_str):
        sql=f"""
            SELECT dim_packhouse.id as packhouse_id
                , dim_pack_type.id as pack_type_id
                , packweek
                , weekday(dim_time.day) as weekday
                , if(noofstdcartons>0, ROUND((noofstdcartons / workdays.workdays)  * dim_time.workday), 0)  as stdunits
                , noofstdcartons as stdunits_source
            FROM dss.pack_capacity_data
            LEFT JOIN dim_packhouse ON (pack_capacity_data.phc = dim_packhouse.name)
            LEFT JOIN dim_pack_type ON (pack_capacity_data.packformat = dim_pack_type.name)
            LEFT JOIN dim_time ON (dim_time.week = pack_capacity_data.packweek)
            LEFT JOIN (SELECT week, sum(workday) as workdays
                FROM dss.dim_time
                GROUP BY week) workdays ON (workdays.week = pack_capacity_data.packweek)
            WHERE extract_datetime = (SELECT MAX(extract_datetime)
                FROM dss.pack_capacity_data WHERE date(extract_datetime)='{plan_date}')
            AND dim_time.workday > 0
            AND pack_capacity_data.packweek in ({weeks_str})
            ORDER BY packhouse_id, pack_type_id, packweek, weekday;
        """

        df = self.database_dss.select_query(sql)
        df['plan_date'] = plan_date
        return df

    def get_local_pc_day(self, plan_date, weeks_str):

        if config.LEVEL == 'DAY':
            sql=f"""
                SELECT * FROM (
                    SELECT dim_packhouse.id as packhouse_id
                        , dim_pack_type.id as pack_type_id
                        , packweek
                        , weekday(dim_time.day) as weekday
                        , if(noofstdcartons>0, ROUND((noofstdcartons / workdays.workdays)  * dim_time.workday), 0)  as stdunits
                        , noofstdcartons as stdunits_source
                    FROM dss.pack_capacity_data
                    LEFT JOIN dim_packhouse ON (pack_capacity_data.phc = dim_packhouse.name)
                    LEFT JOIN dim_pack_type ON (pack_capacity_data.packformat = dim_pack_type.name)
                    LEFT JOIN dim_time ON (dim_time.week = pack_capacity_data.packweek)
                    LEFT JOIN (SELECT week, sum(workday) as workdays
                        FROM dss.dim_time
                        GROUP BY week) workdays ON (workdays.week = pack_capacity_data.packweek)
                    WHERE extract_datetime = (SELECT MAX(extract_datetime)
                        FROM dss.pack_capacity_data WHERE date(extract_datetime)='{plan_date}')
                    AND dim_time.workday > 0
                    AND pack_capacity_data.packweek in ({weeks_str})

                    UNION ALL
                    
                    SELECT DISTINCT 69 as packhouse_id
                        , dim_pack_type.id as pack_type_id
                        , packweek
                        , weekday(dim_time.day) as weekday
                        , 1000000  as stdunits
                        , 1000000 as stdunits_source
                    FROM dss.pack_capacity_data
                    LEFT JOIN dim_packhouse ON (pack_capacity_data.phc = dim_packhouse.name)
                    LEFT JOIN dim_pack_type ON (pack_capacity_data.packformat = dim_pack_type.name)
                    LEFT JOIN dim_time ON (dim_time.week = pack_capacity_data.packweek)
                    LEFT JOIN (SELECT week, sum(workday) as workdays
                        FROM dss.dim_time
                        GROUP BY week) workdays ON (workdays.week = pack_capacity_data.packweek)
                    WHERE extract_datetime = (SELECT MAX(extract_datetime)
                        FROM dss.pack_capacity_data WHERE date(extract_datetime)='{plan_date}')
                    AND dim_time.workday > 0
                    AND pack_capacity_data.packweek in ({weeks_str})) as pc
                ORDER BY packhouse_id, pack_type_id, packweek, weekday;
            """

        else:
            sql=f"""
                SELECT dim_packhouse.id as packhouse_id
                    , dim_pack_type.id as pack_type_id
                    , packweek
                    , 0 as weekday
                    , noofstdcartons as stdunits
                    , noofstdcartons as stdunits_source
                FROM dss.pack_capacity_data
                LEFT JOIN dim_packhouse ON (pack_capacity_data.phc = dim_packhouse.name)
                LEFT JOIN dim_pack_type ON (pack_capacity_data.packformat = dim_pack_type.name)
                WHERE extract_datetime = (SELECT MAX(extract_datetime)
                    FROM dss.pack_capacity_data WHERE date(extract_datetime)='{plan_date}')
                AND pack_capacity_data.packweek in ({weeks_str})
                
                UNION ALL
                
                SELECT DISTINCT 69 as packhouse_id
                    , dim_pack_type.id as pack_type_id
                    , packweek
                    , 0 as weekday
                    , 1000000 as stdunits
                    , 1000000 as stdunits_source
                FROM dss.pack_capacity_data
                LEFT JOIN dim_packhouse ON (pack_capacity_data.phc = dim_packhouse.name)
                LEFT JOIN dim_pack_type ON (pack_capacity_data.packformat = dim_pack_type.name)
                WHERE extract_datetime = (SELECT MAX(extract_datetime)
                    FROM dss.pack_capacity_data WHERE date(extract_datetime)='{plan_date}')
                AND pack_capacity_data.packweek in ({weeks_str});
            """

        df = self.database_dss.select_query(sql)
        df['plan_date'] = plan_date
        return df


class CreateOptions:
    """ Class to generate base of possibiities for demand. """
    logger = logging.getLogger(f"{__name__}.CreateOptions")
    database_instance = DatabaseModelsClass('PHDDATABASE_URL')

    def make_easy(self, plan_date):
        df_dp = self.get_demand_plan(plan_date)
        df_dp.loc[(df_dp['priority']==0), 'priority'] = 1000
        df_he = self.get_harvest_estimate(plan_date)
        df_pc = self.get_pack_capacity(plan_date)
        
        df_ft = self.get_from_to()
        df_exclude = self.get_rules_exlude()
        df_prioritise = self.get_rules_prioritise()

        dic_pc = {}
        dic_he = {}
        dic_demand = {}

        times = list(df_dp.time_id.unique())

        for time in times:
            df_dpt = df_dp[df_dp['time_id']==time].reset_index(drop=True)
            df_het = df_he[df_he['time_id']==time].reset_index(drop=True)
            df_pct = df_pc[df_pc['time_id']==time].reset_index(drop=True)

            # Loop through demands and get he & pc
            dt = {}
            priors = list(df_dpt.priority.unique())
            priors.sort()
            for prior in priors:
                df_dptp = df_dpt[df_dpt['priority']==prior].reset_index(drop=True)

                dt1 = {}
                for d in range(0,len(df_dptp)):
                    ddemand_id = df_dptp.id[d]
                    dclient_id = df_dptp.client_id[d]
                    dvacat_id = df_dptp.vacat_id[d]
                    dtime_id = int(df_dptp.time_id[d])
                    dpack_type_id = df_dptp.pack_type_id[d]
                    dkg = df_dptp.kg[d]

                    dt1.update({int(ddemand_id):{'vacat_id': int(dvacat_id),
                                            'time_id': int(dtime_id),
                                            'pack_type_id': int(dpack_type_id),
                                            'client_id': int(dclient_id),
                                            'kg': int(dkg),
                                            'kg_rem': int(dkg)}})
                if prior == 0:
                    dt.update({1000: dt1})
                
                else:
                    dt.update({int(prior): dt1})

            he3 = {}
            vagrps = list(df_het.vacat_id.unique())
            for vagrp in vagrps:
                df_hetvag = df_het[df_het['vacat_id']==vagrp].reset_index(drop=True)
                    
                he1 = {}
                #df_hetvagva = df_hetvag[df_hetvag['va_id']==va].reset_index(drop=True)
                for he in range(len(df_hetvag)):
                    id = df_hetvag.id[he]
                    block_id = df_hetvag.block_id[he]
                    va_id = df_hetvag.va_id[he]
                    kg = df_hetvag.kg[he]
                
                    he1.update({int(id):{'va_id': int(va_id), 'block_id': int(block_id), 'kg': int(kg), 'kg_rem': int(kg)}})                
                    
                    #he2.update({int(va):he1})

                he3.update({int(vagrp):he1})

            pc2 = {}
            pcktyps = list(df_pct.pack_type_id.unique())
            for pcktyp in pcktyps:
                df_pctpt = df_pct[df_pct['pack_type_id']==pcktyp].reset_index(drop=True)

                pc1 = {}
                for pc in range(len(df_pctpt)):
                    id = df_pctpt.id[pc]
                    packhouse_id = df_pctpt.packhouse_id[pc]
                    kg = df_pctpt.kg[pc]
                    pc1.update({int(packhouse_id):{'pc_id': int(id), 'kg': int(kg), 'kg_rem': int(kg)}})
                
                pc2.update({int(pcktyp): pc1})

            dic_demand.update({int(time): dt})
            dic_he.update({int(time): he3})
            dic_pc.update({int(time): pc2})

        ft2 = {}
        blocks = list(df_ft.block_id.unique())
        for block in blocks:
            df_ftb = df_ft[df_ft['block_id'] == block].reset_index(drop=True)

            #ft1 = {}
            sites_l = []
            for s in range(len(df_ftb)):
                #block_id = int(df_ftb.block_id[s])
                packsite = int(df_ftb.packhouse_id[s])
                km = int(df_ftb.km[s])
                sites_l.append([packsite, km])


            ft2.update({int(block): sites_l})


        # EXCLUDE RULES
        c_refuse = df_exclude.client_id.unique()
        ref_rule={}
        for client in c_refuse:
            ccref = df_exclude[df_exclude['client_id']==client].reset_index(drop=True)
            vas = list(ccref.va_id)

            ref_rule.update({client: vas})

        # PREFERENCE
        c_pref = df_prioritise.client_id.unique()
        pref_rule={}
        for client in c_pref:
            ccpref = df_prioritise[df_prioritise['client_id']==client].reset_index(drop=True)
            ccpref=ccpref.sort_values(by=['priority'])
            vas = list(ccpref.va_id)

            pref_rule.update({client: vas})



        path = os.path.join(config.ROOTDIR,'data','processed')

        outfile = open(os.path.join(path, "easy_refuse"),'wb')
        pickle.dump(ref_rule, outfile)
        outfile.close()

        outfile = open(os.path.join(path, "easy_preference"),'wb')
        pickle.dump(pref_rule, outfile)
        outfile.close()

        outfile = open(os.path.join(path, "week_demand"),'wb')
        pickle.dump(dic_demand, outfile)
        outfile.close()

        with open(os.path.join(path, "week_demand.json"), "w") as outfile:
            json.dump(dic_demand, outfile)

        outfile = open(os.path.join(path, "week_he"),'wb')
        pickle.dump(dic_he, outfile)
        outfile.close()

        with open(os.path.join(path, "week_he.json"), "w") as outfile:
            json.dump(dic_he, outfile)

        outfile = open(os.path.join(path, "week_pc"),'wb')
        pickle.dump(dic_pc, outfile)
        outfile.close()

        with open(os.path.join(path, "week_pc.json"), "w") as outfile:
            json.dump(dic_pc, outfile)

        outfile = open(os.path.join(path, "easy_ft"),'wb')
        pickle.dump(ft2, outfile)
        outfile.close()

        with open(os.path.join(path, "easy_ft.json"), "w") as outfile:
            json.dump(ft2, outfile)

        return 
  

    def make_options(self, plan_date):
        df_dp = self.get_demand_plan(plan_date)
        df_he = self.get_harvest_estimate(plan_date)
        df_pc = self.get_pack_capacity(plan_date)
        self.get_from_to()
        self.get_speed()

        df_exclude = self.get_rules_exlude()
        df_prioritise = self.get_rules_prioritise()

        self.logger.info('- make_options')
        ddic_pc = {}
        ddf_he =pd.DataFrame()
        ddf_pc =pd.DataFrame()
        ddic_metadata={}
        dlist_ready = []

        # Loop through demands and get he & pc
        for d in range(0,len(df_dp)):
            self.logger.debug(f'-- make_options: {d}/{len(df_dp)}')
            ddemand_id = df_dp.id[d]
            dclient_id = df_dp.client_id[d]
            dvacat_id = df_dp.vacat_id[d]
            dtime_id = int(df_dp.time_id[d])
            dpriority = int(df_dp.priority[d])
            dpack_type_id = df_dp.pack_type_id[d]
            dkg = df_dp.kg[d]

            # Find all available harvest estimates for demand 
            ddf_het = df_he[df_he['vacat_id']==dvacat_id]
            ddf_het = ddf_het[ddf_het['time_id']==dtime_id]
            ddf_het['demand_id'] = ddemand_id
            ddf_het['client_id'] = dclient_id
            ddf_he = pd.concat([ddf_he, ddf_het]).reset_index(drop=True)
            dlist_he = ddf_het.id.tolist()

            # find all available pack_capacities for demand    
            ddf_pct = df_pc[df_pc['time_id']==dtime_id]
            ddf_pct = ddf_pct[ddf_pct['pack_type_id']==dpack_type_id]
            ddf_pct['demand_id'] = ddemand_id
            ddf_pc = pd.concat([ddf_pc, ddf_pct]).reset_index(drop=True)
            dlist_pc = ddf_pct.index.tolist()
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
                                            'kg':dkg,
                                            'priority': dpriority,
                                            'ready': ready}})

        ### RULES EXCLUDE he_demand options
        # Filter out options that are not feasible according to rules engine
        # 26 January 2022 Conversation with Kobus Jonas
        # https://www.evernote.com/shard/s187/sh/18e91ca0-a95b-b02d-865a-0b676523ce27/34794bda0a8bffb9835819f539b4b729
        ddf_he=pd.merge(ddf_he, df_exclude, on=['client_id', 'va_id'], how='left')
        ddf_he=ddf_he[ddf_he['exclude']!=1].reset_index(drop=True)
        ddf_he=ddf_he.drop(columns=['exclude'])

        ### RULES PRIORITISE
        ddf_he=pd.merge(ddf_he, df_prioritise, on=['client_id', 'va_id'], how='left')
        ddf_he=ddf_he.sort_values(by=['priority'])

        path = os.path.join(config.ROOTDIR,'data','processed','ddic_metadata')
        outfile = open(path,'wb')
        pickle.dump(ddic_metadata,outfile)
        outfile.close()

        path = os.path.join(config.ROOTDIR,'data','processed','ddf_metadata')
        df_dp.to_pickle(path)

        path = os.path.join(config.ROOTDIR,'data','processed','ddf_he')
        ddf_he.to_pickle(path)

        path = os.path.join(config.ROOTDIR,'data','processed','ddf_pc')
        ddf_pc.to_pickle(path)

        path = os.path.join(config.ROOTDIR,'data','processed','dlist_ready')
        outfile = open(path,'wb')
        pickle.dump(dlist_ready,outfile)
        outfile.close()

        return 
    
    def get_demand_plan(self, plan_date): 
        """ Extract demand requirement from database. """
        self.logger.info('- get_demand_plan')

        s = f"""
        SELECT 
                fdp.id,
                fdp.client_id,
                fdp.vacat_id,
                fdp.pack_type_id,
                fdp.priority,
                fdp.arrivalweek,
                fdp.packweek,
                fdp.stdunits,
                fdp.transitdays,
                w.id as time_id
            FROM
                dss.f_demand_plan fdp
                    LEFT JOIN
                dim_week w ON (fdp.packweek = w.week)
                WHERE stdunits > 100
                AND plan_date = '{plan_date}'
                ORDER BY fdp.priority
                ;
            """

        df_dp = self.database_instance.select_query(query_str=s)
        df_dp['kg'] = df_dp['stdunits'] * config.STDUNIT * (1 + config.GIVEAWAY)
        df_dp = df_dp.sort_values(by=['time_id', 'priority']).reset_index(drop=True)

        return df_dp

    def get_harvest_estimate(self, plan_date): 
        """ Get harvest estimate. """
        self.logger.info('- get_harvest_estimate')

        s= f"""
            SELECT he.id
                , he.va_id
                , va.vacat_id
                , he.block_id
                , w.id AS time_id
                , dim_fc.packtopackplans
                , he.kg_raw as kg
            FROM dss.f_harvest_estimate he
            LEFT JOIN dim_week w ON (he.packweek = w.week)
            LEFT JOIN dim_va va ON (he.va_id = va.id)
            LEFT JOIN dim_block ON (he.block_id = dim_block.id)
            LEFT JOIN dim_fc ON (dim_block.fc_id=dim_fc.id)
            WHERE kg_raw>0
            AND plan_date = '{plan_date}'
            AND dim_fc.packtopackplans=1
            ;
            """

        df_he = self.database_instance.select_query(query_str=s)
        df_he = df_he.set_index('id')
        df_he['id'] = df_he.index
        df_he['stdunits'] = (df_he['kg'] * (1-config.GIVEAWAY))/config.STDUNIT
        df_he['kg_rem'] = df_he['kg']

        he_dic = df_he.to_dict(orient='index')

        path = os.path.join(config.ROOTDIR,'data','processed','he_dic')
        outfile = open(path,'wb')
        pickle.dump(he_dic,outfile)
        outfile.close()
        return df_he

    def get_pack_capacity(self, plan_date): 
        """ Get pack capacities. """
        self.logger.info('- get_pack_capacity')

        s = f"""SELECT 
            pc.id,
            pc.packhouse_id,
            pc.pack_type_id,
            w.id AS time_id,
            -- pc.kg,
            pc.stdunits,
            (pc.stdunits / (5.5 * 8)) * 12 / 60 as stdunits_hour
        FROM
            dss.f_pack_capacity pc
        LEFT JOIN
            dim_week w ON pc.packweek = w.week
        WHERE plan_date = '{plan_date}'
            AND pc.stdunits > 0;
            """

        df_pc = self.database_instance.select_query(query_str=s)
        df_pc = df_pc.set_index('id')
        df_pc['id'] = df_pc.index
        #df_pc['stdunits'] = df_pc['kg'] / config.STDUNIT
        df_pc['kg'] = df_pc['stdunits'] * config.STDUNIT
        df_pc['kg_rem'] = df_pc['kg']
        
        pc_dic = df_pc.to_dict(orient='index')
        path = os.path.join(config.ROOTDIR,'data','processed','pc_dic')
        outfile = open(path,'wb')
        pickle.dump(pc_dic,outfile)
        outfile.close()
        return df_pc 

    def get_from_to(self): 
        """ Get from to data. """
        self.logger.info('- get_from_to')

        s = """
        SELECT packhouse_id,
                dim_block.id as block_id,
                IF(packhouse_id=69, 0, km) as km 
            FROM dss.f_from_to
            LEFT JOIN dim_block ON (dim_block.fc_id = f_from_to.fc_id)
            WHERE allowed=1
            AND dim_block.id is not NULL
            ORDER BY km;
            """

        df_ft = self.database_instance.select_query(query_str=s)
        path = os.path.join(config.ROOTDIR,'data','processed','ft_df')
        df_ft.to_pickle(path)       
        return  df_ft

    def get_speed(self):
        self.logger.info('- get_speed')
        s = """SELECT * FROM dss.f_speed;"""
        df_speed = self.database_instance.select_query(query_str=s)
        
        dic_speed = {}
        packhouses = df_speed.filter(['packhouse_id']).drop_duplicates()
        packhouses = packhouses['packhouse_id'].tolist()
        for p in packhouses:
            
            df_speed1 = df_speed[df_speed['packhouse_id']==p].reset_index(drop=True)
            packtypes = df_speed1.filter(['packtype_id']).drop_duplicates()
            packtypes = packtypes['packtype_id'].tolist()
            
            dic_packtypes = {}
            for pt in packtypes:
            
                df_speed2 = df_speed1[df_speed1['packtype_id']==pt].reset_index(drop=True)
                vas = df_speed2.filter(['va_id']).drop_duplicates()
                vas = vas['va_id'].tolist()   
                
                dic_vas = {}
                for va in vas:
                    df_speed3 = df_speed2[df_speed2['va_id']==va].reset_index(drop=True)
                    speed = df_speed3.speed[0]
                    
                    dic_vas.update({va: speed})
                dic_packtypes.update({pt:dic_vas})
            dic_speed.update({p:dic_packtypes})

        path = os.path.join(config.ROOTDIR,'data','processed','dic_speed')
        outfile = open(path,'wb')
        pickle.dump(dic_speed,outfile)
        outfile.close()
        return

    def get_rules_exlude(self): 
        """ Rules that determine client may NOT rceive cultivar """
        self.logger.info('- get_rules_exlude')

        s = f"""SELECT client_id, va_id, 1 as exclude
                FROM dss.rules_refuse_client_va;
            """

        df = self.database_instance.select_query(query_str=s)

        path = os.path.join(config.ROOTDIR,'data','processed','rules_refuse')
        df.to_pickle(path)
        return df 

    def get_rules_prioritise(self): 
        """ Rules that determine client must prioritise cultivar """
        self.logger.info('- get_rules_exlude')

        s = f"""SELECT client_id, va_id, priority
                FROM dss.rules_prioritse_client_va;
            """
        df = self.database_instance.select_query(query_str=s)
        path = os.path.join(config.ROOTDIR,'data','processed','rules_prioritise')
        df.to_pickle(path)
        return df 


class ImportOptions:
    """ Class to get data in pickle format. """
    logger = logging.getLogger(f"{__name__}.CreateOptions")
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path = os.path.dirname(path)

    def easy_preference(self):
        path=os.path.join(config.ROOTDIR,'data','processed','easy_preference')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def easy_refuse(self):
        path=os.path.join(config.ROOTDIR,'data','processed','easy_refuse')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def easy_ft(self):
        path=os.path.join(config.ROOTDIR,'data','processed','easy_ft')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def easy_harvest(self):
        path=os.path.join(config.ROOTDIR,'data','processed','week_he')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def easy_pc(self):
        path=os.path.join(config.ROOTDIR,'data','processed','week_pc')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def easy_demand(self):
        path=os.path.join(config.ROOTDIR,'data','processed','week_demand')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def demand_harvest(self):
        path=os.path.join(config.ROOTDIR,'data','processed','ddf_he')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def demand_capacity(self):
        path=os.path.join(config.ROOTDIR,'data','processed','ddf_pc')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def demand_metadata(self):
        path=os.path.join(config.ROOTDIR,'data','processed','ddic_metadata')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def demand_metadata_df(self):
        path=os.path.join(config.ROOTDIR,'data','processed','ddf_metadata')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def demand_ready(self):
        path=os.path.join(config.ROOTDIR,'data','processed','dlist_ready')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def harvest_estimate(self):
        path=os.path.join(config.ROOTDIR,'data','processed','he_dic')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def pack_capacity(self):
        path=os.path.join(config.ROOTDIR,'data','processed','pc_dic')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def from_to(self):
        path=os.path.join(config.ROOTDIR,'data','processed','ft_df')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def speed(self):
        path=os.path.join(config.ROOTDIR,'data','processed','dic_speed')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def rules_he_prioritise(self):
        path=os.path.join(config.ROOTDIR,'data','processed','rules_prioritise')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def rules_he_refuse(self):
        path=os.path.join(config.ROOTDIR,'data','processed','rules_refuse')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data


class AdjustPlanningData:
    """ Class to manipulate planning data to match 
        Kobus Jonas for comparison"""
    logger = logging.getLogger(f"{__name__}.GetLocalData")
    database_dss = DatabaseModelsClass('PHDDATABASE_URL')
    
    def adjust_pack_capacities(self, week_str, plan_date):
        """
        1. Adjust according to % split; consider tw pcs in week
            - Capacity for specific pack type < planned; 
            - Total capacity > planned; 
            - Two pcs in week (packtype pc != week pc)

        2. Adjust upwards capcity two pcs for week
            - Capacity for specific pack type < planned; 
            - Total capacity < planned; 
            - Two pcs in week (packtype pc != week pc)

        3. Adjust upwards capcity one pc for week
            - Capacity for specific pack type < planned; 
            - Total capacity < planned; 
            - One pc in week (packtype pc == week pc)

        4. Add additional pcs for pactype, packhouse, week
            - No pc register for 
                - week
                - packtype
                - packhouse
        """
        self.logger.info('- Adjusting pack cpacities according to Kobus plan')

        sql=f"""
            SELECT dim_packhouse.id as packhouse_id
                    , pack_type.id as pack_type_id
                    , pd.packweek
                    , SUM(ROUND(pd.qty_standardctns * -1)) as stdunits
            FROM dss.planning_data pd
            LEFT JOIN dim_packhouse ON (pd.packsite = dim_packhouse.name)
            LEFT JOIN (SELECT id, upper(name) as name FROM dss.dim_pack_type) pack_type  
                ON (pd.format = pack_type.name)
            LEFT JOIN dim_week ON (pd.packweek = dim_week.week)
            WHERE recordtype = 'PLANNED'
            AND extract_datetime = (SELECT MAX(extract_datetime) 
                FROM dss.planning_data WHERE date(extract_datetime)='{plan_date}')
            AND pd.packweek in ({week_str})
            AND dim_packhouse.id > 0
            GROUP BY dim_packhouse.id
                    , pack_type.id
                    , pd.packweek 
                    ;
        """
        # get Kobus Jonas plan for each packhouse
        df_kj = self.database_dss.select_query(sql)
        df_kjsum=df_kj.groupby(['packhouse_id', 'packweek'])['stdunits'].sum().reset_index(drop=False)
        df_kjsum=df_kjsum.rename(columns={'stdunits':'weektotal'})
        df_kj2=pd.merge(df_kj, df_kjsum, on=['packhouse_id', 'packweek'], how='left')

        s=f"""
        SELECT a.packhouse_id, a.packweek, a.pack_type_id, a.stdunits_source, b.stdunits as weektotal
        FROM dss.f_pack_capacity a
        LEFT JOIN (SELECT packhouse_id, packweek, sum(stdunits_source) as stdunits 
            FROM dss.f_pack_capacity
            WHERE plan_date='{plan_date}'
            GROUP BY packhouse_id, packweek) b ON (a.packhouse_id=b.packhouse_id AND a.packweek=b.packweek)
        WHERE a.plan_date='{plan_date}'
        """
        df_pc = self.database_dss.select_query(s)

        for k in range(0,len(df_kj2)):
            packhouse_id = df_kj2.packhouse_id[k]
            packweek = df_kj2.packweek[k]
            pack_type_id = df_kj2.pack_type_id[k]
            stdunits_kj = df_kj2.stdunits[k]
            weektotal_kj = df_kj2.weektotal[k]
            now=datetime.datetime.now()

            if pack_type_id == 1:
                pack_type_idb = 2

            if pack_type_id == 2:
                pack_type_idb = 1

            df_pct=df_pc[(df_pc['packhouse_id']==packhouse_id) & \
                (df_pc['packweek']==packweek) & \
                (df_pc['pack_type_id']==pack_type_id)].reset_index(drop=True)

            # Check if any pc is logged for this combination
            if len(df_pct) > 0:
                stdunits_cap = df_pct.stdunits_source[0]
                weektotal_cap = df_pct.weektotal[0]

                ######## Two packtypes for week ########
                # Where kj has more cap for packtype, not weektotal
                if (weektotal_cap > weektotal_kj) & \
                    (stdunits_cap < stdunits_kj) & \
                    (weektotal_cap != stdunits_cap):
                    self.logger.info('-- Rule1')

                    a = stdunits_kj
                    b = weektotal_cap - stdunits_kj

                    sa=f"""
                    UPDATE `dss`.`f_pack_capacity` 
                    SET `stdunits` = '{a}'
                        , `adjusted` = '1'
                        , `add_datetime` = '{now}' 
                    WHERE (packhouse_id = {packhouse_id} 
                        AND pack_type_id = {pack_type_id} 
                        AND packweek = '{packweek}'
                        AND plan_date = '{plan_date}');
                    """
                    self.database_dss.execute_query(sa)

                    sb=f"""
                    UPDATE `dss`.`f_pack_capacity` 
                    SET `stdunits` = '{b}'
                        , `adjusted` = '1'
                        , `add_datetime` = '{now}' 
                    WHERE (packhouse_id = {packhouse_id} 
                        AND pack_type_id = {pack_type_idb} 
                        AND packweek = '{packweek}'
                        AND plan_date = '{plan_date}');
                    """
                    self.database_dss.execute_query(sb)

                # Where kj has more cap for packtype and weektotal
                if (weektotal_cap < weektotal_kj) & \
                    (stdunits_cap < stdunits_kj) & \
                    (weektotal_cap != stdunits_cap):
                    self.logger.info('-- Rule2')

                    a = stdunits_kj
                    b = weektotal_kj - stdunits_kj

                    sa=f"""
                    UPDATE `dss`.`f_pack_capacity` 
                    SET `stdunits` = '{a}'
                        , `adjusted` = '2'
                        , `add_datetime` = '{now}' 
                    WHERE (packhouse_id = {packhouse_id} 
                        AND pack_type_id = {pack_type_id} 
                        AND packweek = '{packweek}'
                        AND plan_date = '{plan_date}');
                    """
                    self.database_dss.execute_query(sa)

                    sb=f"""
                    UPDATE `dss`.`f_pack_capacity` 
                    SET `stdunits` = '{b}'
                        , `adjusted` = '2'
                        , `add_datetime` = '{now}' 
                    WHERE (packhouse_id = {packhouse_id} 
                        AND pack_type_id = {pack_type_idb} 
                        AND packweek = '{packweek}'
                        AND plan_date = '{plan_date}');
                    """
                    self.database_dss.execute_query(sb)

                ######## Only one packtype for week ########
                # Where kj has more cap for packtype and weektotal,
                if (weektotal_cap < weektotal_kj) & \
                    (stdunits_cap < stdunits_kj) & \
                    (weektotal_cap == stdunits_cap):
                    self.logger.info('-- Rule3')

                    a = stdunits_kj
                    b = weektotal_kj - stdunits_kj

                    sa=f"""
                    UPDATE `dss`.`f_pack_capacity` 
                    SET `stdunits` = '{a}'
                        , `adjusted` = '3'
                        , `add_datetime` = '{now}' 
                    WHERE (packhouse_id = {packhouse_id} 
                        AND pack_type_id = {pack_type_id} 
                        AND packweek = '{packweek}'
                        AND plan_date = '{plan_date}');
                    """
                    self.database_dss.execute_query(sa)


            # Else add pc for this combination
            else:
                s2=f"""
                    INSERT INTO `dss`.`f_pack_capacity` 
                    (`packhouse_id`, `pack_type_id`, `packweek`, 
                    `stdunits`, `stdunits_source`, `adjusted`, `add_datetime`, `plan_date`) 
                    VALUES ({packhouse_id},{pack_type_id},'{packweek}', 
                    {stdunits_kj},0,'4','{now}', '{plan_date}');
                """
                self.logger.info('-- Rule4')
                self.database_dss.execute_query(s2)

        return 
    
    def adjust_harvest_estimates(self):
        # TODO: This cannot be updated as KJ planning data not at orchard level
        self.logger.info('- Adjusting harvest estimates according to Kobus plan')

        return


class GetOperationalData:
    """ Class to generate data for operational model. """
    logger = logging.getLogger(f"{__name__}.GetOperationalData")
    database_instance = DatabaseModelsClass('PHDDATABASE_URL')    

    def get_chosen_individual(self): 
        """ Get from to data. """
        self.logger.info('- get_chosen_individual')

        s = """
            SELECT sol_pareto_individuals.demand_id
                -- , sol_pareto_individuals.he 
                , sol_pareto_individuals.pc 
                , f_demand_plan.packaging
                , ROUND(SUM(sol_pareto_individuals.kg), 1) as kg
            FROM dss.sol_pareto_individuals
            LEFT JOIN f_demand_plan ON (f_demand_plan.id = sol_pareto_individuals.demand_id)
            LEFT JOIN sol_fitness ON (sol_pareto_individuals.indiv_id = sol_fitness.indiv_id 
                AND sol_pareto_individuals.alg = sol_fitness.alg 
                AND sol_pareto_individuals.plan_date = sol_fitness.plan_date
                AND sol_fitness.result = 'final result')
            WHERE kg > 0
            AND sol_pareto_individuals.plan_date = '2021-12-08'
            AND sol_pareto_individuals.time_id = 1076
            AND sol_fitness.id = 387
            -- AND pc = 4722
            GROUP BY sol_pareto_individuals.demand_id, 
            f_demand_plan.packaging,
            -- sol_pareto_individuals.he, 
            sol_pareto_individuals.pc;
            """

        df = self.database_instance.select_query(query_str=s)
        path = os.path.join(config.ROOTDIR,'data','raw','operational_individual')
        df.to_pickle(path)       
        return  df

    def get_daily_capacity(self): 
        """ Get daily capacity. """
        self.logger.info('- get_daily_capacity')

        s = """
            SELECT f_pack_capacity.id as pc
            -- , f_pack_capacity.packhouse_id
            -- , f_pack_capacity.pack_type_id
            -- , f_pack_capacity.stdunits
            , dim_time.id as day_id
            , IF(stdunits>0, ROUND((stdunits / dim_week.workdays)  * dim_time.workday), 0)  as stdunits_day
            , IF(stdunits>0, ROUND((stdunits / dim_week.workdays)  * dim_time.workday), 0) * 4.5  as kg_day
            -- , dim_week.id as time_id
            FROM dss.f_pack_capacity
            LEFT JOIN dim_week on (dim_week.week = f_pack_capacity.packweek)
            LEFT JOIN dim_time on (dim_time.week = f_pack_capacity.packweek)
            WHERE f_pack_capacity.plan_date = '2021-12-08'
            AND dim_time.workday > 0
            AND dim_week.id = 1076
            -- AND f_pack_capacity.id = 4722
            ORDER BY packhouse_id, pack_type_id
            ;
            """

        df = self.database_instance.select_query(query_str=s)


        path = os.path.join(config.ROOTDIR,'data','raw','operational_daily_capacity')
        df.to_pickle(path)       
        return df