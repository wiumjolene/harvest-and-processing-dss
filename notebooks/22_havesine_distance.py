import haversine as hs
import pandas as pd
from connect import DatabaseModelsClass

db = DatabaseModelsClass('PHDDATABASE_URL')
def get_packhouse():
    sql = """
        SELECT id, longitude, latitude 
        FROM dss.dim_packhouse
        WHERE id = 38;
    """
    df = db.select_query(sql)
    return(df)

def get_block():
    sql = """
        SELECT id, longitude, latitude 
        FROM dss.dim_block
        WHERE id = 94;
    """
    df = db.select_query(sql)
    return(df)


packhouse = get_packhouse()
block = get_block()

#print(block)

df=[]
for p in range(len(packhouse)):
    packhouse_id=packhouse.id[p]
    plong=packhouse.longitude[p]
    plat=packhouse.latitude[p]

    ploc = (plong, plat)

    for b in range(len(block)):
        block_id=block.id[b]
        blong=block.longitude[b]
        blat=block.latitude[b]

        if blong < 1:
            x = 10000
            allowed = 0
        
        else:
            bloc = (blong, blat)
            x = round(hs.haversine(ploc,bloc),2)
            allowed = 1

        #print(x)

        df.append([packhouse_id,block_id,x,allowed])

df=pd.DataFrame(data=df,columns=['packhouse_id','block_id','km','allowed'])
print(df)

db.insert_table(df, 'f_from_to', 'dss', if_exists='append')