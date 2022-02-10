import os
import random
import sys

import pandas as pd


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.utils.connect import DatabaseModelsClass

sql_select = """
    SELECT *
    FROM dss.interim_options_he;
"""

database_instance = DatabaseModelsClass('PHDDATABASE_URL')
df = database_instance.select_query(sql_select)

rule1_sql = f"""SELECT client_id, va_id, 1 as exclude
                FROM dss.rules_refuse_client_va;"""
df_exclude = database_instance.select_query(rule1_sql)

df
#for r in range(0,len(rules1)):
    

