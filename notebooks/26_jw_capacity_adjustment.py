import os
import random
import sys

import pandas as pd
import datetime


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.utils.connect import DatabaseModelsClass


database_dss = DatabaseModelsClass('PHDDATABASE_URL')

week_str = "'22-01', '22-02', '22-03', '22-04'"
plan_date = '2022-01-05'

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
df_kj = database_dss.select_query(sql)
df_kjsum=df_kj.groupby(['packhouse_id', 'packweek'])['stdunits'].sum().reset_index(drop=False)
df_kjsum=df_kjsum.rename(columns={'stdunits':'weektotal'})
df_kj2=pd.merge(df_kj, df_kjsum, on=['packhouse_id', 'packweek'], how='left')

s=f"""
SELECT a.packhouse_id, a.packweek, a.pack_type_id, a.stdunits_source, b.stdunits as weektotal
FROM dss.f_pack_capacity a
LEFT JOIN (SELECT packhouse_id, packweek, sum(stdunits_source) as stdunits 
	FROM dss.f_pack_capacity
	GROUP BY packhouse_id, packweek) b ON (a.packhouse_id=b.packhouse_id AND a.packweek=b.packweek)
"""
df_pc = database_dss.select_query(s)

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
            print('rule1')

            a = stdunits_kj
            b = weektotal_cap - stdunits_kj

            sa=f"""
            UPDATE `dss`.`f_pack_capacity` 
            SET `stdunits` = '{a}'
                , `adjusted` = '1'
                , `add_datetime` = '{now}' 
            WHERE (packhouse_id = {packhouse_id} 
                AND pack_type_id = {pack_type_id} 
                AND packweek = '{packweek}');
            """
            database_dss.execute_query(sa)

            sb=f"""
            UPDATE `dss`.`f_pack_capacity` 
            SET `stdunits` = '{b}'
                , `adjusted` = '1'
                , `add_datetime` = '{now}' 
            WHERE (packhouse_id = {packhouse_id} 
                AND pack_type_id = {pack_type_idb} 
                AND packweek = '{packweek}');
            """
            database_dss.execute_query(sb)

        # Where kj has more cap for packtype and weektotal
        if (weektotal_cap < weektotal_kj) & \
            (stdunits_cap < stdunits_kj) & \
            (weektotal_cap != stdunits_cap):
            print('rule2')

            a = stdunits_kj
            b = weektotal_kj - stdunits_kj

            sa=f"""
            UPDATE `dss`.`f_pack_capacity` 
            SET `stdunits` = '{a}'
                , `adjusted` = '2'
                , `add_datetime` = '{now}' 
            WHERE (packhouse_id = {packhouse_id} 
                AND pack_type_id = {pack_type_id} 
                AND packweek = '{packweek}');
            """
            database_dss.execute_query(sa)

            sb=f"""
            UPDATE `dss`.`f_pack_capacity` 
            SET `stdunits` = '{b}'
                , `adjusted` = '2'
                , `add_datetime` = '{now}' 
            WHERE (packhouse_id = {packhouse_id} 
                AND pack_type_id = {pack_type_idb} 
                AND packweek = '{packweek}');
            """
            database_dss.execute_query(sb)

        ######## Only one packtype for week ########
        # Where kj has more cap for packtype and weektotal,
        if (weektotal_cap < weektotal_kj) & \
            (stdunits_cap < stdunits_kj) & \
            (weektotal_cap == stdunits_cap):
            print('rule3')

            a = stdunits_kj
            b = weektotal_kj - stdunits_kj

            sa=f"""
            UPDATE `dss`.`f_pack_capacity` 
            SET `stdunits` = '{a}'
                , `adjusted` = '3'
                , `add_datetime` = '{now}' 
            WHERE (packhouse_id = {packhouse_id} 
                AND pack_type_id = {pack_type_id} 
                AND packweek = '{packweek}');
            """
            database_dss.execute_query(sa)


    # Else add pc for this combination
    else:
        s2=f"""
            INSERT INTO `dss`.`f_pack_capacity` 
            (`packhouse_id`, `pack_type_id`, `packweek`, 
            `stdunits`, `stdunits_source`, `adjusted`, `add_datetime`) 
            VALUES ({packhouse_id},{pack_type_id},'{packweek}', 
            {stdunits_kj},0,'4','{now}');
        """
        print('rule4')
        database_dss.execute_query(s2)