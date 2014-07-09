# Create your views here.
import os
import traceback
import MySQLdb as mdb
import MySQLdb.cursors

from django.shortcuts import render
from learn_app.forms import LearnForm, TeacherEvaluationForm
from learn_app.search_pipeline import SearchPipeline 
from ConfigParser import SafeConfigParser
from django.template import RequestContext
from django.http import HttpResponseRedirect


def __getDatabaseConnection(cursorType):
    
    parser = SafeConfigParser()
    parser.read(os.path.join(os.getcwd(), "colloquy","config.ini"))
    db_ip = parser.get('database_info', 'ip')
    db_user = parser.get('database_info', 'user')
    db_pass = parser.get('database_info', 'password')
    db_name = parser.get('database_info', 'db')
    
    conn = mdb.connect(db_ip, db_user, db_pass, db_name, cursorclass = cursorType, use_unicode = True, charset = 'utf8')
    return conn


def learnView(request):    

    user_id = request.GET.get('user_id','')
    
    frontend = {'status_msg':""}
    frontend['user_id'] = user_id
    
    languages = getAvailableLangauges()
    if request.method == 'POST' and "search" in request.POST:
        
        form = LearnForm(request.POST, choices=languages)
        frontend['form'] = form
        if form.is_valid():   
            
            data_bundle = form.cleaned_data           
            language_name_id = data_bundle['language_name']
            language_name = language_name_id.split("_")[1]
            language_id = language_name_id.split("_")[0]
            frontend['language_name'] = language_name
            frontend['language_id'] = language_id 
            
            params = {}
            params['learner_id'] = user_id   
            params['language_name'] = language_name
               
            params['pref_reading'] = data_bundle['reading']
            params['pref_speaking'] = data_bundle['speaking']
            params['pref_writing'] = data_bundle['writing']
            search_pipeline = SearchPipeline(params)
            teacher_ids = search_pipeline.findBestMatch()
            
            teacher_details = getTeacherDetails(teacher_ids, language_name)              
            frontend['form_teacher_details'] = LearnForm(choices=teacher_details)
            if len(teacher_details) == 0:
                frontend['status_msg'] = "Sorry No Partners Found :( Please Try Again Later."
            frontend['teacher_details'] = teacher_details
            
    elif request.method == 'POST' and "talk" in request.POST:
        frontend['teacher_id'] = request.POST.get('teachers','') 
        frontend['language_name'] = request.GET.get('lang_name','')
        frontend['language_id'] = request.GET.get('lang_id','')
        print frontend['language_id']
        frontend['teacher_eval_form'] = TeacherEvaluationForm(attr_list=getEvaluationAttributes())
       
        return render(request,'learn_app/learn_video.html', frontend)
    
    elif request.method == 'POST' and "eval" in request.POST: 
        form = TeacherEvaluationForm(request.POST, attr_list=getEvaluationAttributes())
        frontend['form'] = LearnForm(choices=languages)
        if form.is_valid():            
            data_bundle = form.cleaned_data
            user_id = request.GET.get('user_id','')
            language_id = request.GET.get('lang_id','')
            ret = saveTeacherEvaluation(data_bundle, user_id, language_id) 
            if ret:
                frontend['status_msg'] = "Thank-You for Your Evaluation!"
            else:
                frontend['status_msg'] = "Something Went Could Not Save Your Evaluation"
                
            #print data_bundle
                    
    else:
        frontend['form'] = LearnForm(choices=languages)
    
    return render(request,'learn_app/learn.html', frontend)
    
    

def getEvaluationAttributes():
    
    attr_list = []
    conn = None
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.DictCursor)    
        query = "SELECT * FROM colloquy_db.rating_attributes WHERE role <> 'S' ORDER BY type"          
        cur = conn.cursor()
        cur.execute(query)  
        rows = cur.fetchall()
        
        for row in rows:    
            attr_list.append([row['id'], row['name'], row['type']])
               
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()
        
    return attr_list


def saveTeacherEvaluation(data_bundle, user_id, language_id):
    
    ret = True
    conn = None

    for i in data_bundle:
        sign,val = data_bundle[i].split("_") 
        data_bundle[i] = [int(val) if sign=='pos' else 0 , int(val) if sign=='neg' else 0,i.split("_")[0],i.split("_")[1]]
        
    
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.DictCursor)
        
        for i in data_bundle:
            cur = conn.cursor()
            #print data_bundle[i]
            if data_bundle[i][2] == "L":    
                query = "INSERT INTO colloquy_db.language_ratings\
                            VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE\
                            pos_value = pos_value + %s,\
                            neg_value = pos_value + %s"
                            #WHERE user_id=%s AND lang_id IN (SELECT id FROM colloquy_db.languages WHERE Language=%s) AND\
                            #attr_id=%s"
                values = (user_id, language_id, data_bundle[i][3], data_bundle[i][0], data_bundle[i][1], data_bundle[i][0], data_bundle[i][1])
                cur.execute(query, values) 
            else:
                query = "INSERT INTO colloquy_db.user_ratings VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE\
                            pos_value = pos_value + %s,\
                            neg_value = pos_value + %s"
                            #WHERE user_id=%s AND attr_id=%s"
                values = (user_id, data_bundle[i][3], data_bundle[i][0], data_bundle[i][1], data_bundle[i][0], data_bundle[i][1])
                cur.execute(query, values) 
            conn.commit()     

               
    except:
        print traceback.format_exc()
        ret = False
    finally:
        if conn: conn.close()    
    return ret    


def getAvailableLangauges():
    
    languages =[]    
    conn = None
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.DictCursor)    
        query = "SELECT DISTINCT Languages.Language, lang_id FROM colloquy_db.proficiency, colloquy_db.languages \
                    WHERE role<>'student' and languages.id=lang_id"
          
        cur = conn.cursor()
        cur.execute(query)  
        rows = cur.fetchall()
        
        for row in rows:    
            languages.append((str(row['lang_id']) +"_"+row['Language'], row['Language']))
               
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()      
    return languages


def getTeacherDetails(teacher_ids, language_name):
    
    teacher_details = [] 
    scores = {}
    for i in teacher_ids:
        scores[i[0]] = round(i[1]*100,1)
    
    conn = None
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.DictCursor)
        if len(teacher_ids) == 1:
            ids = "(" + str(teacher_ids[0][0]) + ")"
        else:
            ids = str(tuple([str(i[0]) for i in teacher_ids]))
                   
        query = "SELECT user_id,first_name, Language, speaking, reading, writing, isNative \
                FROM colloquy_db.proficiency, colloquy_db.languages, colloquy_db.user  \
                WHERE proficiency.lang_id=languages.id AND user.id = proficiency.user_id   \
                AND languages.Language='%s' AND user.id IN %s" % (language_name, ids)
        
        cur = conn.cursor()
        cur.execute(query)

        temp = {}
        rows = cur.fetchall()
        if len(rows) != 0:
            for row in rows:
                key = str(row['user_id'])
                data = (row['first_name'], row['Language'], str(row['speaking']), str(row['reading']),
                         str(row['writing']), ("Yes" if row['isNative'] == '1' else "No"), scores[row['user_id']])
                
                value = "Name: %s | Language: %s | Speaking: %s | Reading: %s | Writing: %s | Native: %s | Score: %s"%(data)
                temp[row['user_id']] = (key,value)
                #print temp
                
            for teacher_id in teacher_ids:
                if teacher_id[0] in temp:  
                    teacher_details.append(temp[teacher_id[0]])
                        
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()

    return teacher_details

