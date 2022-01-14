# -*- coding: utf-8 -*-
import logging
import os
import pickle
import sys
import datetime

import pandas as pd
from src.utils import config
from src.utils.connect import DatabaseModelsClass


class CreateOptions:
    """ Class to generate base of possibiities for demand. """
    logger = logging.getLogger(f"{__name__}.CreateOptions")
    database_instance = DatabaseModelsClass('PHDDATABASE_URL')

    def make_options(self):
        df_dp = self.get_demand_plan()
        df_he = self.get_harvest_estimate()
        df_pc = self.get_pack_capacity()
        #print(df_pc)
        self.get_from_to()
        self.get_speed()

        self.logger.info('- make_options')
        ddic_pc = {}
        ddic_he = {}
        ddf_he =pd.DataFrame()
        ddf_pc =pd.DataFrame()
        ddic_metadata={}
        dlist_ready = []

        # Loop through demands and get he & pc
        for d in range(0,len(df_dp)):
            ddemand_id = df_dp.id[d]
            dvacat_id = df_dp.vacat_id[d]
            dtime_id = int(df_dp.time_id[d])
            dpack_type_id = df_dp.pack_type_id[d]
            dkg = df_dp.kg[d]

            # Find all available harvest estimates for demand 
            ddf_het = df_he[df_he['vacat_id']==dvacat_id]
            ddf_het = ddf_het[ddf_het['time_id']==dtime_id]
            ddf_het['demand_id'] = ddemand_id
            ddf_he = pd.concat([ddf_he, ddf_het]).reset_index(drop=True)
            dlist_he = ddf_he.id.tolist()
            ddic_he.update({ddemand_id: dlist_he})

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
                                            'ready': ready}})

        # Save nb datasets to processed for use in algorithms
        path = os.path.join('data','processed','ddic_dp')
        #outfile = open('data/processed/ddic_dp','wb') #FIXME: Why is the name and the dic different?
        outfile = open(path,'wb') #FIXME: Why is the name and the dic different?
        pickle.dump(ddic_metadata,outfile)
        outfile.close()

        path = os.path.join('data','processed','ddic_metadata')
        #outfile = open('data/processed/ddic_metadata','wb')
        outfile = open(path,'wb')
        pickle.dump(ddic_metadata,outfile)
        outfile.close()

        path = os.path.join('data','processed','ddf_metadata')
        #df_dp.to_pickle('data/processed/ddf_metadata')
        df_dp.to_pickle(path)

        #ddf_he.to_pickle('data/processed/ddf_he')
        path = os.path.join('data','processed','ddf_he')
        ddf_he.to_pickle(path)

        #ddf_pc.to_pickle('data/processed/ddf_pc')
        path = os.path.join('data','processed','ddf_pc')
        ddf_pc.to_pickle(path)

        #outfile = open('data/processed/dlist_ready','wb')
        path = os.path.join('data','processed','dlist_ready')
        outfile = open(path,'wb')
        pickle.dump(dlist_ready,outfile)
        outfile.close()

        return 

    def get_demand_plan(self): 
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
                WHERE packweek in ('22-01','22-02','22-03','22-04')
                AND stdunits > 100;
            """

        df_dp = self.database_instance.select_query(query_str=s)
        df_dp['kg'] = df_dp['stdunits'] * config.STDUNIT * (1 + config.GIVEAWAY)
        df_dp = df_dp.sort_values(by=['time_id', 'priority']).reset_index(drop=True)
        df_dp['trucks'] = df_dp['kg'] /config.TRUCK
        return df_dp

    def get_harvest_estimate(self): 
        """ Get harvest estimate. """
        self.logger.info('- get_harvest_estimate')

        s= f"""
            SELECT he.id
                , he.va_id
                , va.vacat_id
                , he.block_id
                , w.id AS time_id
                , he.kg_raw as kg
            FROM dss.f_harvest_estimate he
            LEFT JOIN dim_week w ON (he.packweek = w.week)
            LEFT JOIN dim_va va ON (he.va_id = va.id)
            LEFT JOIN dim_block ON (he.block_id = dim_block.id)
            LEFT JOIN dim_fc ON (dim_block.fc_id=dim_fc.id)
            WHERE kg_raw>0
            AND dim_fc.packtopackplans=1;
            """

        df_he = self.database_instance.select_query(query_str=s)
        df_he = df_he.set_index('id')
        df_he['id'] = df_he.index
        df_he['stdunits'] = (df_he['kg'] * (1-config.GIVEAWAY))/config.STDUNIT
        df_he['kg_rem'] = df_he['kg']

        he_dic = df_he.to_dict(orient='index')

        path = os.path.join('data','processed','he_dic')
        outfile = open(path,'wb')
        pickle.dump(he_dic,outfile)
        outfile.close()
        return df_he

    def get_pack_capacity(self): 
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
            dim_week w ON pc.packweek = w.week;
            """

        df_pc = self.database_instance.select_query(query_str=s)
        df_pc = df_pc.set_index('id')
        df_pc['id'] = df_pc.index
        #df_pc['stdunits'] = df_pc['kg'] / config.STDUNIT
        df_pc['kg'] = df_pc['stdunits'] * config.STDUNIT
        df_pc['kg_rem'] = df_pc['kg']
        
        pc_dic = df_pc.to_dict(orient='index')
        path = os.path.join('data','processed','pc_dic')
        #outfile = open('data/processed/pc_dic','wb')
        outfile = open(path,'wb')
        pickle.dump(pc_dic,outfile)
        outfile.close()
        return df_pc 

    def get_from_to(self): 
        """ Get from to data. """
        self.logger.info('- get_from_to')

        s = """SELECT packhouse_id,
                block_id,
                km 
                FROM dss.f_from_to
                WHERE history=1
                ORDER BY km;"""

        df_ft = self.database_instance.select_query(query_str=s)
        path = os.path.join('data','processed','ft_df')
        df_ft.to_pickle(path)
        #df_ft.to_pickle('data/processed/ft_df')
        
        return  

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

        path = os.path.join('data','processed','dic_speed')
        outfile = open(path,'wb')
        #outfile = open('data/processed/dic_speed','wb')
        pickle.dump(dic_speed,outfile)
        outfile.close()
        return


class ImportOptions:
    """ Class to get data. """
    logger = logging.getLogger(f"{__name__}.CreateOptions")
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path = os.path.dirname(path)

    def demand_harvest(self):
        #infile = open(f"{self.path}/data/processed/ddf_he",'rb')
        path=os.path.join('data','processed','ddf_he')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def demand_capacity(self):
        path=os.path.join('data','processed','ddf_pc')
        infile = open(path,'rb')
        #infile = open(f"{self.path}/data/processed/ddf_pc",'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def demand_metadata(self):
        path=os.path.join('data','processed','ddic_metadata')
        infile = open(path,'rb')
        #infile = open(f"{self.path}/data/processed/ddic_metadata",'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def demand_ready(self):
        path=os.path.join('data','processed','dlist_ready')
        infile = open(path,'rb')
        #infile = open(f"{self.path}/data/processed/dlist_ready",'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def harvest_estimate(self):
        path=os.path.join('data','processed','he_dic')
        infile = open(path,'rb')
        #infile = open(f"{self.path}/data/processed/he_dic",'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def pack_capacity(self):
        path=os.path.join('data','processed','pc_dic')
        infile = open(path,'rb')
        #infile = open(f"{self.path}/data/processed/pc_dic",'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def from_to(self):
        #infile = open(f"{self.path}/data/processed/ft_df",'rb')
        path=os.path.join('data','processed','ft_df')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data

    def speed(self):
        #infile = open(f"{self.path}/data/processed/dic_speed",'rb')
        path=os.path.join('data','processed','dic_speed')
        infile = open(path,'rb')
        data = pickle.load(infile)
        infile.close()
        return data


class GetLocalData:
    """ Class to extract planning data"""
    logger = logging.getLogger(f"{__name__}.GetLocalData")
    database_dss = DatabaseModelsClass('PHDDATABASE_URL')

    def get_local_he(self):
        sql1="""
            SELECT dim_block.id as block_id
                , dim_va.id as va_id
                , Week as packweek
                , ROUND(SUM(GrossEstimate * 1000),1) as kg_raw
            FROM dss.harvest_estimate_data
            LEFT JOIN dim_fc ON (harvest_estimate_data.Grower = dim_fc.name)
            LEFT JOIN dim_block ON (harvest_estimate_data.ProductionUnit = dim_block.name AND dim_block.fc_id = dim_fc.id)
            LEFT JOIN dim_va ON (harvest_estimate_data.Variety = dim_va.name)
            WHERE extract_datetime = (SELECT MAX(extract_datetime)FROM dss.harvest_estimate_data)
            AND estimatetype = 'BUDGET2'
            GROUP BY dim_fc.id, dim_block.id, dim_va.id, Week;        
        """
        sql="""
            SELECT dim_block.id as block_id
                , dim_va.id as va_id
                , Week as packweek
                -- , ROUND(SUM(GrossEstimate * 1000),1) as kg_raw
                , SUM(kgGross) as kg_raw
            FROM dss.harvest_estimate_0638_data as he
            LEFT JOIN dim_fc ON (he.Grower = dim_fc.name)
            LEFT JOIN dim_block ON (he.Farm = dim_block.name AND dim_block.fc_id = dim_fc.id)
            LEFT JOIN dim_va ON (he.Variety = dim_va.name)
            WHERE extract_datetime = (SELECT MAX(extract_datetime) FROM dss.harvest_estimate_0638_data)
            AND estimatetype = 'ADJUSTMENT'
            AND kgGross > 0
            GROUP BY dim_fc.id, dim_block.id, dim_va.id, Week
            ;         
        """
        df = self.database_dss.select_query(sql)
        return df

    def get_he_fc(self):
        sql1="""
            SELECT DISTINCT Grower as name
                , dim_fc.id
            FROM dss.harvest_estimate_data
            LEFT JOIN dim_fc ON (harvest_estimate_data.Grower = dim_fc.name)
            WHERE dim_fc.id is NULL
            AND extract_datetime = (SELECT MAX(extract_datetime) FROM dss.harvest_estimate_data);      
        """
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
        sql1="""
            SELECT DISTINCT ProductionUnit as name
                , dim_fc.id as fc_id
            FROM dss.harvest_estimate_data
            LEFT JOIN dim_fc ON (harvest_estimate_data.Grower = dim_fc.name)
            LEFT JOIN dim_block ON (harvest_estimate_data.ProductionUnit = dim_block.name AND dim_block.fc_id = dim_fc.id)
            WHERE dim_block.id is NULL
            AND extract_datetime = (SELECT MAX(extract_datetime)FROM dss.harvest_estimate_data);;   
        """
        sql="""
            SELECT DISTINCT Farm as name
                , dim_fc.id as fc_id
            FROM dss.harvest_estimate_0638_data
            LEFT JOIN dim_fc ON (harvest_estimate_0638_data.Grower = dim_fc.name)
            LEFT JOIN dim_block ON (harvest_estimate_0638_data.Farm = dim_block.name AND dim_block.fc_id = dim_fc.id)
            WHERE dim_block.id is NULL
            AND extract_datetime = (SELECT MAX(extract_datetime)FROM dss.harvest_estimate_0638_data);  
        """
        df = self.database_dss.select_query(sql)
        df['add_datetime'] = datetime.datetime.now()
        return df

    def get_he_va(self):
        sql1="""
             SELECT DISTINCT Variety as name
            FROM dss.harvest_estimate_data
            LEFT JOIN dim_va ON (harvest_estimate_data.Variety = dim_va.name)
            WHERE dim_va.id is NULL
            AND extract_datetime = (SELECT MAX(extract_datetime)FROM dss.harvest_estimate_data); 
        """
        sql="""
			SELECT DISTINCT Variety as name
            FROM dss.harvest_estimate_0638_data
            LEFT JOIN dim_va ON (harvest_estimate_0638_data.Variety = dim_va.name)
            WHERE dim_va.id is NULL
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

    def get_local_dp(self):
        sql="""
            SELECT demandid as id
                , dim_client.id as client_id
                , dim_vacat.id as vacat_id
                , dim_pack_type.id as pack_type_id
                , IF(priority= "-", 0, priority) as priority
                , demand_arrivalweek as arrivalweek
                , dim_time.week as packweek
                , dim_client.transitdays as transitdays
                , round(qty_standardctns) as stdunits
            FROM dss.planning_data
            LEFT JOIN dim_client ON (planning_data.targetmarket = dim_client.name)
            LEFT JOIN dim_vacat ON (planning_data.varietygroup = dim_vacat.name)
            LEFT JOIN dim_week ON (planning_data.demand_arrivalweek = dim_week.week)
            LEFT JOIN dim_time ON ((date_sub(dim_week.weekstart,  INTERVAL dim_client.transitdays DAY)) = dim_time.day)
            LEFT JOIN dim_pack_type ON ((IF((SUBSTR(cartontype, 1, 1) = 'A'),
                        IF((cartontype = 'A75F'),
                            'LOOSE',
                            'PUNNET'),
                        'LOOSE')) = dim_pack_type.name)
            WHERE extract_datetime = (SELECT MAX(extract_datetime)FROM dss.planning_data)
            AND recordtype = 'DEMAND'
            ;
        """
        df = self.database_dss.select_query(sql)
        return df

    def get_pc_packhouse(self):
        sql="""
            SELECT distinct phc as name
            FROM dss.pack_capacity_data
            LEFT JOIN dim_packhouse ON (pack_capacity_data.phc = dim_packhouse.name)
            WHERE dim_packhouse.id is NULL
            AND extract_datetime = (SELECT MAX(extract_datetime)FROM dss.pack_capacity_data);
        """
        df = self.database_dss.select_query(sql)
        df['add_datetime'] = datetime.datetime.now()
        return df

    def get_local_pc(self):
        sql="""
            SELECT dim_packhouse.id as packhouse_id
                , dim_pack_type.id as pack_type_id
                , packweek
                , noofstdcartons as stdunits
                , noofstdcartons as stdunits_source
            FROM dss.pack_capacity_data
            LEFT JOIN dim_packhouse ON (pack_capacity_data.phc = dim_packhouse.name)
            LEFT JOIN dim_pack_type ON (pack_capacity_data.packformat = dim_pack_type.name)
            WHERE extract_datetime = (SELECT MAX(extract_datetime)FROM dss.pack_capacity_data);
        """
        df = self.database_dss.select_query(sql)
        return df


class AdjustPlanningData:
    """ Class to manipulate planning data to match 
        Kobus Jonas for comparison"""
    logger = logging.getLogger(f"{__name__}.GetLocalData")
    database_dss = DatabaseModelsClass('PHDDATABASE_URL')

    def adjust_pack_capacities(self):
        self.logger.info('- Adjusting pack cpacities according to Kobus plan')
        sql="""
            SELECT dim_packhouse.id as packhouse_id
                    -- , dim_week.id as time_id
                    , pack_type.id as pack_type_id
                    -- , pd.format
                    , pd.packweek
                    -- , pd.packsite
                    , SUM(ROUND(pd.qty_standardctns * -1)) as stdunits
            FROM dss.planning_data pd
            LEFT JOIN dim_packhouse ON (pd.packsite = dim_packhouse.name)
            LEFT JOIN (SELECT id, upper(name) as name FROM dss.dim_pack_type) pack_type  
                ON (pd.format = pack_type.name)
            LEFT JOIN dim_week ON (pd.packweek = dim_week.week)
            WHERE recordtype = 'PLANNED'
            AND extract_datetime = (SELECT MAX(extract_datetime) FROM dss.planning_data)
            -- AND pd.packweek in ('22-01','22-02','22-03','22-04')
            AND dim_packhouse.id > 0
            GROUP BY dim_packhouse.id
                    -- , dim_week.id
                    , pack_type.id
                    -- , pd.format
                    , pd.packweek
                    -- , pd.packsite 
                    ;
        """
        # get Kobus Jonas plan for each packhouse
        df = self.database_dss.select_query(sql)
        for k in range(0,len(df)):
            packhouse_id = df.packhouse_id[k]
            packweek = df.packweek[k]
            pack_type_id = df.pack_type_id[k]
            stdunits_kj = df.stdunits[k]
            now=datetime.datetime.now()

            s=f"""
            SELECT * FROM dss.f_pack_capacity
            WHERE (packhouse_id = {packhouse_id} 
            AND pack_type_id = {pack_type_id} 
            AND packweek = '{packweek}');
            """
            pc = self.database_dss.select_query(s)

            if len(pc) > 0:
                stdunits_cap = pc.stdunits[0]

                if stdunits_kj > stdunits_cap:
                    s1=f"""
                    UPDATE `dss`.`f_pack_capacity` 
                    SET `stdunits` = '{stdunits_kj}'
                        , `adjusted` = '1'
                        , `add_datetime` = '{now}' 
                    WHERE (packhouse_id = {packhouse_id} 
                        AND pack_type_id = {pack_type_id} 
                        AND packweek = '{packweek}');
                    """
                    self.database_dss.execute_query(s1)

            else:
                s2=f"""
                    INSERT INTO `dss`.`f_pack_capacity` 
                    (`packhouse_id`, `pack_type_id`, `packweek`, 
                    `stdunits`, `stdunits_source`, `adjusted`, `add_datetime`) 
                    VALUES ({packhouse_id},{pack_type_id},'{packweek}', 
                    {stdunits_kj},0,'2','{now}');
                """
                self.database_dss.execute_query(s2)

        return 

    def adjust_harvest_estimates(self):
        self.logger.info('- Adjusting harvest estimates according to Kobus plan')
        sql="""
            SELECT dim_packhouse.id as packhouse_id
                    -- , dim_week.id as time_id
                    , pack_type.id as pack_type_id
                    -- , pd.format
                    , pd.packweek
                    -- , pd.packsite
                    , SUM(ROUND(pd.qty_standardctns * -1)) as stdunits
            FROM dss.planning_data pd
            LEFT JOIN dim_packhouse ON (pd.packsite = dim_packhouse.name)
            LEFT JOIN (SELECT id, upper(name) as name FROM dss.dim_pack_type) pack_type  
                ON (pd.format = pack_type.name)
            LEFT JOIN dim_week ON (pd.packweek = dim_week.week)
            WHERE recordtype = 'PLANNED'
            AND extract_datetime = (SELECT MAX(extract_datetime) FROM dss.planning_data)
            -- AND pd.packweek in ('22-01','22-02','22-03','22-04')
            AND dim_packhouse.id > 0
            GROUP BY dim_packhouse.id
                    -- , dim_week.id
                    , pack_type.id
                    -- , pd.format
                    , pd.packweek
                    -- , pd.packsite 
                    ;
        """
        # get Kobus Jonas plan for each packhouse
        df = self.database_dss.select_query(sql)
        for k in range(0,len(df)):
            packhouse_id = df.packhouse_id[k]
            packweek = df.packweek[k]
            pack_type_id = df.pack_type_id[k]
            stdunits_kj = df.stdunits[k]
            now=datetime.datetime.now()

            s=f"""
            SELECT * FROM dss.f_pack_capacity
            WHERE (packhouse_id = {packhouse_id} 
            AND pack_type_id = {pack_type_id} 
            AND packweek = '{packweek}');
            """
            pc = self.database_dss.select_query(s)

            if len(pc) > 0:
                stdunits_cap = pc.stdunits[0]

                if stdunits_kj > stdunits_cap:
                    s1=f"""
                    UPDATE `dss`.`f_pack_capacity` 
                    SET `stdunits` = '{stdunits_kj}'
                        , `adjusted` = '1'
                        , `add_datetime` = '{now}' 
                    WHERE (packhouse_id = {packhouse_id} 
                        AND pack_type_id = {pack_type_id} 
                        AND packweek = '{packweek}');
                    """
                    self.database_dss.execute_query(s1)

            else:
                s2=f"""
                    INSERT INTO `dss`.`f_pack_capacity` 
                    (`packhouse_id`, `pack_type_id`, `packweek`, 
                    `stdunits`, `stdunits_source`, `adjusted`, `add_datetime`) 
                    VALUES ({packhouse_id},{pack_type_id},'{packweek}', 
                    {stdunits_kj},0,'2','{now}');
                """
                self.database_dss.execute_query(s2)

        return