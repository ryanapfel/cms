import pandas as pd
import os
import sqlalchemy
import pymysql


def validMediaId(params, user, password):
    if "mediaId" in params:
        mediaId = params["mediaId"]
    else:
        return False

    engine = sqlalchemy.create_engine(f"mysql+pymysql://{user}:{password}@mysql/ml")
    sql = f"""SELECT `media_item_id` FROM `media_item`"""
    df = pd.read_sql(sql, engine)
    validlist = df["media_item_id"].to_list()
    if mediaId in validlist:
        return True
    else:
        return False


def retrieve(mediaId, client, user, password):
    try:

        returnDict = {}

        engine = Engine(mediaId, client, user, password)
        # get title
        returnDict["mediaId"] = mediaId
        returnDict["client"] = client
        returnDict["exists"] = engine.mediaItemExists()
        returnDict["title"] = engine.getTitle()
        returnDict["allRatings"] = engine.getAllRatings()
        returnDict["rating"] = engine.getRating()
        returnDict["demand"] = engine.getDemand()
        returnDict["client_titles"] = engine.getClientComps()
        returnDict["client_engagment"] = engine.getEngagement()
        returnDict["demographics"] = engine.getDemographics()
        returnDict["videoInfo"] = engine.getVideoInfo()

        return returnDict
    except:
        return {}


class Engine:
    def __init__(self, id, clientId, queryString):
        self.id = id
        self.clientId = clientId
        self.engine = sqlalchemy.create_engine(queryString)

    def load(self, sql, serialize=True):
        if serialize:
            return pd.read_sql(sql, self.engine).to_json()
        else:
            return pd.read_sql(sql, self.engine)

    def getClientAndSelf(self, limit=False):
        limit = f"""LIMIT {limit}""" if limit else ""
        sql = f""" SELECT mmm.media_item_id 
                FROM media_item mmm 
                WHERE mmm.media_item_id = {self.id}
                UNION
                (SELECT mi.media_item_id 
                FROM media m 
                INNER JOIN media_item mi 
                ON mi.media_id = m.media_id 
                WHERE m.client_id = {self.clientId}
                ORDER BY media_item_id DESC
                {limit})
                ORDER BY 1 DESC
                """
        return sql

    def getTitle(self):
        #    INNER JOIN media_video mv ON media_item.media_item_id = mv.media_item_id ---- mv.duration, mv.framerate, mv.width, mv.height
        sql = f"""SELECT media.`media_id`,`media_type_id`,`client_id`,`title`,`release_date` , media_item.media_item_id, media_item.url_1
                  FROM `media` 
                  INNER JOIN media_item 
                  ON media.media_id = media_item.media_id 
                  WHERE media_item.media_item_id = {self.id}
                  ;"""
        return self.load(sql)

    def getRating(self):
        sql = f"""SELECT main.media_item_id, main.count, main.mean, main.std
                FROM media_ratings main
                JOIN (SELECT media_item_id, MAX(date_appended) as date FROM media_ratings GROUP BY media_item_id) sub
                ON main.media_item_id = sub.media_item_id AND main.date_appended = sub.date
                WHERE main.media_item_id IN (SELECT * FROM ({self.getClientAndSelf()}) as v1);"""

        df = pd.read_sql(sql, self.engine)
        df["count_percentile"] = df["count"].rank(pct=True)
        df["count_rank"] = df["count"].rank()

        df["mean_percentile"] = df["mean"].rank(pct=True)
        df["mean_rank"] = df["mean"].rank()
        return df.to_json()

    def getDemand(self):
        sql = f"""
        SELECT main.media_item_id, main.count, main.mean, main.std
        FROM media_demand main
        JOIN (SELECT media_item_id, MAX(date_appended) as date FROM media_demand GROUP BY media_item_id) sub
        ON main.media_item_id = sub.media_item_id AND main.date_appended = sub.date
        WHERE main.media_item_id IN (SELECT * FROM ({self.getClientAndSelf()}) as v1);"""

        df = pd.read_sql(sql, self.engine)
        df["count_percentile"] = df["count"].rank(pct=True)
        df["count_rank"] = df["count"].rank()

        df["mean_percentile"] = df["mean"].rank(pct=True)
        df["mean_rank"] = df["mean"].rank()
        return df.to_json()

    def getPreferences(self):
        sql = f"""SELECT `media_item_id`,`platform`,`count` 
                  FROM `raw_platform` 
                  WHERE media_item_id = {self.id};"""
        return self.load(sql)

    def mediaItemExists(self):
        sql = f"""SELECT COUNT(1) as `exists` FROM media_item WHERE media_item_id = {self.id};"""
        df = self.load(sql, serialize=False)
        return df["exists"].item()

    def getClientComps(self, limit=False):
        limit = limit if limit else False
        sql = f"""SELECT m.title, m.media_id, mi.media_item_id, m.release_date 
                  FROM media m 
                  INNER JOIN media_item mi 
                  ON mi.media_id = m.media_id 
                  WHERE mi.media_item_id IN (SELECT * FROM ({self.getClientAndSelf(limit)}) as v1);"""
        return self.load(sql)

    """
    Query gets the most recent engagement data (updated daily) for every title that shares 
    the same client as the target title (self.id)
    """

    def getEngagementOld(self):
        sql = f"""SELECT main.media_item_id, main.percentile, main.count, main.normalized
            FROM media_engagement main
            JOIN (SELECT media_item_id, MAX(date_appended) as date FROM media_engagement GROUP BY media_item_id) sub
            ON main.media_item_id = sub.media_item_id AND main.date_appended = sub.date
            WHERE main.media_item_id IN (SELECT * FROM ({self.getClientAndSelf(limit=250)}) as v1);"""
        return self.load(sql)

    def getEngagement(self):
        sql = f"""SELECT  media_item_id, percentile, count, normalized
                  FROM media_engagement 
                  WHERE date_appended >= (SELECT DATE(MAX(date_appended)) as day FROM media_engagement) 
                  AND media_item_id IN (SELECT * FROM ({self.getClientAndSelf(limit=250)}) as v1)"""
        return self.load(sql)

    def getScenes(self):
        sql = f"""SELECT * 
                FROM media_scenes
                WHERE media_item_id IN (SELECT * FROM ({self.getClientAndSelf(250)}) as temp)
                """
        return self.load(sql)

    def getVideoInfo(self):
        sql = f"""SELECT * FROM media_video"""
        return self.load(sql)

    def getRawEngagement(self):
        sql = f"""SELECT user_id, meta_value, meta_key, timestamp 
                  FROM raw_responses 
                  WHERE media_item_id = {self.id}"""
        return self.load(sql)

    def getDemographics(self):
        sql = f"""
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
                                                        WHERE mmi.media_item_id = {self.id}));"""
        return self.load(sql)

    def getAllRatings(self):
        sql = f"""
        SELECT main.media_item_id, main.`overall-rating`, main.user_id, raw.ethnicity, raw.sex, raw.income
        FROM raw_ratings main
        JOIN ({self.getClientAndSelf(limit=100)}) sub
        ON sub.media_item_id = main.media_item_id
        JOIN raw_user raw
        ON main.user_id = raw.user_id
        """
        return self.load(sql)
