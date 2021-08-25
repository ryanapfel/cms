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
    if 'mediaId' in params:
        mediaId = params['mediaId']
    else:
        return {}

    returnDict = {}
    engine = Engine(mediaId, user, password)
    # get title
    returnDict['exists'] = engine.mediaItemExists()
    returnDict['title'] = engine.getTitle()
    returnDict['rating'] = engine.getRating()
    returnDict['demand'] = engine.getDemand()
    returnDict['prefs'] = engine.getPreferences()
    returnDict['client_titles'] = engine.getClientComps()
    returnDict['client_engagment'] = engine.getEngagement()
    returnDict['demographics'] = engine.getDemographics()
    return returnDict
    

class Engine:
    def __init__(self, id, user, password):
        self.id = id
        self.engine = sqlalchemy.create_engine(f"mysql+pymysql://{user}:{password}@mysql/ml")
    def load(self, sql, serialize=True):
        if serialize:
            return pd.read_sql(sql, self.engine).to_json()
        else:
            return pd.read_sql(sql, self.engine)
    
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
                WHERE main.media_item_id IN (SELECT mi.media_item_id 
                                            FROM media m 
                                            INNER JOIN media_item mi 
                                            ON mi.media_id = m.media_id 
                                            WHERE m.client_id = (SELECT mm.client_id 
                                                                FROM media mm 
                                                                INNER JOIN media_item mmi ON mmi.media_id = mm.media_id 
                                                                WHERE mmi.media_item_id = {self.id}));'''
        return self.load(sql)

    def getDemand(self):
        sql = f'''
        SELECT main.media_item_id, main.count, main.mean, main.std
        FROM media_demand main
        JOIN (SELECT media_item_id, MAX(date_appended) as date FROM media_demand GROUP BY media_item_id) sub
        ON main.media_item_id = sub.media_item_id AND main.date_appended = sub.date
        WHERE main.media_item_id IN (SELECT mi.media_item_id 
                                    FROM media m 
                                    INNER JOIN media_item mi 
                                    ON mi.media_id = m.media_id 
                                    WHERE m.client_id = (SELECT mm.client_id 
                                                        FROM media mm 
                                                        INNER JOIN media_item mmi ON mmi.media_id = mm.media_id 
                                                        WHERE mmi.media_item_id = {self.id}))'''
        return self.load(sql)
    
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
                  WHERE m.client_id = (SELECT mm.client_id FROM media mm 
                                      INNER JOIN media_item mmi 
                                      ON mmi.media_id = mm.media_id 
                                      WHERE mmi.media_item_id = {self.id})
                  ORDER BY release_date DESC;'''
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
            WHERE main.media_item_id IN (SELECT mi.media_item_id 
                            FROM media m 
                            INNER JOIN media_item mi 
                            ON mi.media_id = m.media_id 
                            WHERE m.client_id = (SELECT mm.client_id 
                                                FROM media mm 
                                                INNER JOIN media_item mmi 
                                                ON mmi.media_id = mm.media_id 
                                                WHERE mmi.media_item_id = {self.id}));'''
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