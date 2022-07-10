import os
import random
import sys
from datetime import datetime as dt
import datetime
import pandas as pd


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.utils.connect import DatabaseModelsClass

sql_select = """
SELECT a.recordno, date(serverdatetime) as plan_date, transitdays
FROM dss.transitdays_log a
LEFT JOIN (
		SELECT recordno, date(serverdatetime), max(serverdatetime) as time , 1 as filter
		FROM dss.transitdays_log
		GROUP BY recordno, date(serverdatetime)) b
    ON	(a.recordno = b.recordno AND a.serverdatetime = b.time)
WHERE b.filter = 1
-- AND a.recordno = 12408;
"""

sql_select2 = """
SELECT DISTINCT demandid 
FROM dss.planning_data
-- WHERE demandid in (12408)
;
"""

database_instance = DatabaseModelsClass('PHDDATABASE_URL')
df = database_instance.select_query(sql_select)
df['plan_date'] = pd.to_datetime(df['plan_date'])

df2 = database_instance.select_query(sql_select2)

demandids = list(df2.demandid.unique())
#demandids = [1,2,3,4,5]

START_DATE = dt.strptime('2019-01-01', '%Y-%m-%d')
END_DATE = dt.strptime('2022-06-01', '%Y-%m-%d')
START_DATE = datetime.datetime(2019,1,1)
END_DATE = datetime.datetime(2022,5,30)

date_range = pd.date_range(start=START_DATE, end=END_DATE, freq='D')

df_base = pd.DataFrame({})
for v in demandids:
    print(v)
    dft = df[df['recordno'] == v].reset_index(drop=True)

    df_base_t = pd.DataFrame({'plan_date': date_range})
    df_base_t['recordno'] = v

    df_base_t['plan_date'] = pd.to_datetime(df_base_t['plan_date'])
    dft['plan_date'] = pd.to_datetime(dft['plan_date'])


    df_base_t = pd.merge(df_base_t, dft, how='left', on=['plan_date','recordno'])
    df_base_t.sort_values(by=['plan_date']).reset_index(drop=True)

    df_base_t['transitdays'].fillna(method = 'ffill', inplace = True)

    df_base_t = df_base_t[df_base_t['plan_date'] > datetime.datetime(2021,10,30)]

    
    df_base = pd.concat([df_base, df_base_t])

print(df_base)

database_instance.insert_table(df_base, 'transitdays2', 'dss', if_exists='replace')