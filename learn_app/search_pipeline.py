'''
Created on Apr 26, 2013

@author: ACHIRA
'''
import os
import traceback
import MySQLdb as mdb
from math import sqrt
import MySQLdb.cursors


from ConfigParser import SafeConfigParser

class SearchPipeline:
    
    def __init__(self, data_bundle):
        self.learner_id = data_bundle['learner_id']   
        self.language_name = data_bundle['language_name']
        self.pref_reading = int(data_bundle['pref_reading'])
        self.pref_speaking = int(data_bundle['pref_speaking'])
        self.pref_writing = int(data_bundle['pref_writing'])      
    
    
    def __getDatabaseConnection(self, cursorType):
    
        parser = SafeConfigParser()
        parser.read("C:\Users\ACHIRA\workspace\colloquy\config.ini")
        db_ip = parser.get('database_info', 'ip')
        db_user = parser.get('database_info', 'user')
        db_pass = parser.get('database_info', 'password')
        db_name = parser.get('database_info', 'db')
        
        conn = mdb.connect(db_ip, db_user, db_pass, db_name, cursorclass = cursorType, use_unicode = True, charset = 'utf8')
        return conn


    def findBestMatch(self):
        
        teacher_ids = []
        score_bundle = self.languageAndRatingsFilter()
        
        score_bundle = self.preferedRatingFilter(score_bundle)
        
        for i in score_bundle:
            teacher_ids.append((i, self.calculateWilsonScore(score_bundle[i][0], score_bundle[i][1])))            
        
        teacher_ids =  sorted(teacher_ids,key=lambda x: x[1],reverse=True)
        
        return teacher_ids
    
    
    def languageAndRatingsFilter(self):
        
        conn = None
        score_bundle = {}
        try:
            conn = self.__getDatabaseConnection(MySQLdb.cursors.DictCursor)    
            query = "SELECT t1.user_id,SUM(t1.pos_value) AS pos_value, SUM(t1.neg_value) AS neg_value FROM (SELECT * FROM \
                    (SELECT user_id, SUM(pos_value*(weight/100)) AS pos_value, SUM(neg_value*(weight/100)) AS neg_value \
                    FROM (SELECT * FROM colloquy_db.rating_attributes WHERE type='U' AND role<>'S') AS user_rating_attr ,colloquy_db.user_ratings \
                    WHERE user_rating_attr.id=user_ratings.attr_id AND user_id IN (SELECT user_id FROM colloquy_db.proficiency,colloquy_db.languages \
                                                                                    WHERE proficiency.lang_id=languages.id AND role<>'student' AND Language=%s) \
                    GROUP BY user_id) AS lang_rating\
                    UNION\
                    (SELECT user_id, SUM(pos_value*(weight/100)) AS pos_value, SUM(neg_value*(weight/100)) AS neg_value \
                    FROM (SELECT * FROM colloquy_db.rating_attributes WHERE type='U' AND role<>'S') AS lang_rating_attr, \
                                                            (SELECT user_id, attr_id, pos_value, neg_value FROM colloquy_db.language_ratings,colloquy_db.languages \
                                                            WHERE language_ratings.lang_id=languages.id AND Language=%s) AS lang_attr_id \
                    WHERE lang_rating_attr.id=lang_attr_id .attr_id AND user_id IN (SELECT user_id FROM colloquy_db.proficiency,colloquy_db.languages \
                                                                                    WHERE proficiency.lang_id=languages.id AND role<>'student' AND Language=%s) \
                    GROUP BY user_id)) as t1 \
                    WHERE t1.user_id <> %s\
                    GROUP BY t1.user_id"
            
            values = (self.language_name, self.language_name, self.language_name, self.learner_id)  
            cur = conn.cursor()
            cur.execute(query, values)  
            rows = cur.fetchall()

            for row in rows:
                #print str(row['user_id']) + '\t '+ str(self.doWilsonScore(row['pos_value'], row['neg_value']))                           
                score_bundle[row['user_id']] = [float(row['pos_value']), float(row['neg_value'])]#self.doWilsonScore(row['pos_value'], row['neg_value'])
                   
        except:
            print traceback.format_exc()
        finally:
            if conn: conn.close()  
    
        return score_bundle
    
    
    def preferedRatingFilter(self, old_score_bundle):
        
        score_bundle = old_score_bundle
        normalize = {1:[0,1,2], 2:[3,4], 3:[5,6], 4:[7,8], 5:[9,10]}
        weights = {5:1.50, 4:1.45, 3:1.40, 2:1.35, 1:1.30, 0:1.25, -5:1.50, -4:1.45, -3:1.40, -2:1.35, -1:1.30}
        
        try:
            conn = self.__getDatabaseConnection(MySQLdb.cursors.DictCursor)
            ids = tuple(score_bundle.keys())    
            if len(score_bundle) == 1:
                ids = "(" +  str(ids[0])  + ")"
            else:
                ids = str(tuple([str(i) for i in ids]))
              
            query = "SELECT user_id, Language, speaking, reading, writing, isNative FROM colloquy_db.proficiency, colloquy_db.languages\
                        WHERE lang_id = languages.id AND user_id IN %s AND Language='%s'" % (ids, self.language_name)
            #print query
            cur = conn.cursor()
            cur.execute(query)  
            rows = cur.fetchall()
            

                    
            for row in rows:
                if row['user_id'] in score_bundle:
                    
                    for i in normalize:
                        if int(row['speaking']) in normalize[i]:
                            row['speaking']  = i
                        if int(row['reading']) in normalize[i]:
                            row['reading']  = i
                        if int(row['writing']) in normalize[i]:
                            row['writing']  = i
                                                   
                    speaking_diff = row['speaking'] - self.pref_speaking
                    reading_diff = row['reading'] - self.pref_reading
                    writing_diff = row['writing'] - self.pref_writing
                    
                    score_bundle[row['user_id']][1 if speaking_diff < 0 else 0] *= weights[speaking_diff]
                    score_bundle[row['user_id']][1 if reading_diff < 0 else 0] *= weights[speaking_diff]
                    score_bundle[row['user_id']][1 if writing_diff < 0 else 0] *= weights[speaking_diff]                   
                          
            
            return score_bundle      
                    
                    
            
        except:
            print traceback.format_exc()
        finally:
            if conn: conn.close()  
        
    
    
    
    def __confidence(self, ups, downs):
        n = float(ups + downs)
    
        if n == 0:
            return 0
        
        #Confidence Interval
        z = 1.6 #1.0 = 85%, 1.6 = 95%
        phat = float(ups) / n
        return ((phat + z*z/(2*n) - z * sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n))
    
    
    def calculateWilsonScore(self, positive, negative):
        
        if positive + negative == 0:
            return 0
        else:
            return self.__confidence(positive, negative)
        
        
        
        
if __name__ == "__main__":
    
    data_bundle = {}
    data_bundle['learner_id'] = 24   
    data_bundle['language_name'] = 'English'
    data_bundle['pref_reading'] = 1
    data_bundle['pref_speaking'] = 1
    data_bundle['pref_writing'] = 5
    
    pipeline = SearchPipeline(data_bundle)
    #print pipeline.preferedRatingFilter({24:[10,50],26:[50,20]})
    print pipeline.findBestMatch()
    pass    
        