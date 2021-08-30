import pandas as pd
import os
import sqlalchemy
import pymysql


def validMediaId(params, user, password):
    if 'mediaId' in params:
        mediaId = params['mediaId']
    else:
        return False
    
    engine = sqlalchemy.create_engine(f"mysql+pymysql://{user}:{password}@mysql/ml")
    sql = f"""SELECT `media_item_id` FROM `media_item`"""
    df = pd.read_sql(sql, engine)
    validlist = df['media_item_id'].to_list()
    if mediaId in validlist:
        return True
    else:
        return False


def retrieve(params, user, password):
    try:

        returnDict = {}

        # we need this for anything if not here it should fail
        mediaId = params['mediaId']
 
        if 'clientId' in params:
            if int(params['clientId']) == 9:
                clientId = 1
            else:
                clientId = params['clientId']
        else:
            # default is to show volkno data
            clientId = 1
        
        print(mediaId, clientId, type)
        engine = Engine(mediaId, clientId, user, password)
        # get title
        returnDict['exists'] = engine.mediaItemExists()
        returnDict['title'] = engine.getTitle()
        returnDict['allRatings'] = engine.getAllRatings()
        returnDict['rating'] = engine.getRating()
        returnDict['demand'] = engine.getDemand()
        returnDict['client_titles'] = engine.getClientComps()
        returnDict['client_engagment'] = engine.getEngagement()
        returnDict['demographics'] = engine.getDemographics()
        return returnDict
    except:
        return {}
    

class Engine:
    def __init__(self, id, clientId,  user, password):
        self.id = id
        self.clientId = clientId
        self.engine = sqlalchemy.create_engine(f"mysql+pymysql://{user}:{password}@mysql/ml")
    def load(self, sql, serialize=True):
        if serialize:
            return pd.read_sql(sql, self.engine).to_json()
        else:
            return pd.read_sql(sql, self.engine)

    def getClientAndSelf(self, limit=1000):
        sql = f''' SELECT mmm.media_item_id 
                FROM media_item mmm 
                WHERE mmm.media_item_id = {self.id}
                UNION
                (SELECT mi.media_item_id 
                FROM media m 
                INNER JOIN media_item mi 
                ON mi.media_id = m.media_id 
                WHERE m.client_id = {self.clientId}
                ORDER BY media_item_id DESC
                LIMIT {limit})
                ORDER BY 1 DESC
                '''
        return sql
    
    def getTitle(self):
        sql = f"""SELECT media.`media_id`,`media_type_id`,`client_id`,`title`,`release_date` , media_item.media_item_id
                  FROM `media` INNER JOIN media_item 
                  ON media.media_id = media_item.media_id 
                  WHERE media_item_id = {self.id};"""
        return self.load(sql)
    
    def getRating(self):
        sql = f'''SELECT main.media_item_id, main.count, main.mean, main.std
                FROM media_ratings main
                JOIN (SELECT media_item_id, MAX(date_appended) as date FROM media_ratings GROUP BY media_item_id) sub
                ON main.media_item_id = sub.media_item_id AND main.date_appended = sub.date
                WHERE main.media_item_id IN (SELECT * FROM ({self.getClientAndSelf()}) as v1);'''

        df = pd.read_sql(sql, self.engine)
        df['count_percentile'] = df['count'].rank(pct=True)
        df['count_rank'] = df['count'].rank() 

        df['mean_percentile'] = df['mean'].rank(pct=True)
        df['mean_rank'] = df['mean'].rank()                                                     
        return df.to_json()

    def getDemand(self):
        sql = f'''
        SELECT main.media_item_id, main.count, main.mean, main.std
        FROM media_demand main
        JOIN (SELECT media_item_id, MAX(date_appended) as date FROM media_demand GROUP BY media_item_id) sub
        ON main.media_item_id = sub.media_item_id AND main.date_appended = sub.date
        WHERE main.media_item_id IN (SELECT * FROM ({self.getClientAndSelf()}) as v1);'''
        
        df = pd.read_sql(sql, self.engine)
        df['count_percentile'] = df['count'].rank(pct=True)
        df['count_rank'] = df['count'].rank() 

        df['mean_percentile'] = df['mean'].rank(pct=True)
        df['mean_rank'] = df['mean'].rank()                                                     
        return df.to_json()
    
    def getPreferences(self):
        sql = f'''SELECT `media_item_id`,`platform`,`count` 
                  FROM `raw_platform` 
                  WHERE media_item_id = {self.id};'''
        return self.load(sql)

    def mediaItemExists(self):
        sql = f"""SELECT COUNT(1) as `exists` FROM media_item WHERE media_item_id = {self.id};"""
        df = self.load(sql, serialize=False)
        return df['exists'].item()
        
    def getClientComps(self):
        sql = f'''SELECT m.title, m.media_id, mi.media_item_id, m.release_date 
                  FROM media m 
                  INNER JOIN media_item mi 
                  ON mi.media_id = m.media_id 
                  WHERE mi.media_item_id IN (SELECT * FROM ({self.getClientAndSelf()}) as v1);'''
        return self.load(sql)


    '''
    Query gets the most recent engagement data (updated daily) for every title that shares 
    the same client as the target title (self.id)
    '''
    def getEngagement(self):
        sql=f'''SELECT main.media_item_id, main.percentile, main.count, main.normalized
            FROM media_engagement main
            JOIN (SELECT media_item_id, MAX(date_appended) as date FROM media_engagement GROUP BY media_item_id) sub
            ON main.media_item_id = sub.media_item_id AND main.date_appended = sub.date
            WHERE main.media_item_id IN (SELECT * FROM ({self.getClientAndSelf()}) as v1);'''
        return self.load(sql)                                        
    
    def getDemographics(self):
        sql = f'''
        SELECT main.*
        FROM media_demographics main
        JOIN (SELECT media_item_id, MAX(date_appended) as date FROM media_demographics GROUP BY media_item_id) sub
        ON main.media_item_id = sub.media_item_id AND main.date_appended = sub.date
        WHERE main.media_item_id IN (SELECT mi.media_item_id 
                                    FROM media m 
                                    INNER JOIN media_item mi 
                                    ON mi.media_id = m.media_id 
                                    WHERE m.client_id = (SELECT mm.client_id 
                                                        FROM media mm 
                                                        INNER JOIN media_item mmi ON mmi.media_id = mm.media_id 
                                                        WHERE mmi.media_item_id = {self.id}));'''
        return self.load(sql)                                                                                                            
    
    def getAllRatings(self):
        subquery = f'''SELECT mi.media_item_id, m.release_date
        FROM media m 
        INNER JOIN media_item mi 
        ON mi.media_id = m.media_id 
        WHERE m.client_id = (SELECT mm.client_id 
        FROM media mm 
        INNER JOIN media_item mmi ON mmi.media_id = mm.media_id 
        WHERE mmi.media_item_id = {self.id}) 
        ORDER BY m.release_date DESC
        LIMIT 50
        ''' 
        sql = f'''
        SELECT main.media_item_id, main.`overall-rating`
        FROM raw_ratings main
        JOIN ({subquery}) sub
        ON sub.media_item_id = main.media_item_id
        '''
        return self.load(sql)            

