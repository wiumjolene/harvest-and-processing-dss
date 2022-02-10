import haversine as hs
import pandas as pd
import datetime
from connect import DatabaseModelsClass

db = DatabaseModelsClass('PHDDATABASE_URL')
def get_packhouse():
    sql = """
        SELECT id, longitude, latitude 
        FROM dss.dim_packhouse
        -- WHERE id = 22
        ;
    """
    df = db.select_query(sql)
    return(df)

def get_block():
    sql = """
        SELECT id, longitude, latitude FROM dss.dim_fc
        -- WHERE id = 29
        ;
    """
    df = db.select_query(sql)
    return(df)

def get_from_to(fc_id, packhouse_id):
    sql = f"""
        SELECT * FROM dss.f_from_to
        WHERE fc_id = {fc_id} and packhouse_id = {packhouse_id};
    """
    df = db.select_query(sql)

    if len(df) > 0:
        update = False

    else:
        update = True
    
    return update


packhouse = get_packhouse()
block = get_block()




for p in range(len(packhouse)):
    packhouse_id=packhouse.id[p]
    plong=packhouse.longitude[p]
    plat=packhouse.latitude[p]

    ploc = (plong, plat)
    df=[]

    for b in range(len(block)):
        block_id=block.id[b]
        blong=block.longitude[b]
        blat=block.latitude[b]
        print(f"check from block {block_id} to packhouse {packhouse_id}")

        if get_from_to(block_id, packhouse_id):

            print(f"-- UPDATE from block ")

            if blong < 1:
                x = 10000
                allowed = 0
            
            else:
                bloc = (blong, blat)
                x = round(hs.haversine(ploc,bloc),2)
                allowed = 0

            df.append([packhouse_id,block_id,x,allowed])

    df=pd.DataFrame(data=df,columns=['packhouse_id','fc_id','km','allowed'])
    if len(df)>0:
        df['add_datetime'] = datetime.datetime.now()
        db.insert_table(df, 'f_from_to', 'dss', if_exists='append')