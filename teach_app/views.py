# Create your views here.
import os
import traceback
import MySQLdb as mdb
import MySQLdb.cursors

from django.shortcuts import render
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


def selectLangaugeView(request):
    
    user_id = request.GET.get('user_id','')
    frontend = {'status_msg':""}
    frontend['user_id'] = user_id
    frontend["language_list"] = getTeacherLangauges(user_id)
    
    if len(frontend["language_list"]) == 0:
        frontend['status_msg'] = "You Have No Languages Added Where You are a Teacher!"
    return render(request,'teach_app/teach.html', frontend)


def videoView(request):

    user_id = request.GET.get('user_id','')
    language = request.GET.get('language','')
    
    frontend = {'status_msg':""}
    frontend['user_id'] = user_id
    frontend["language_name"] = language
    return render(request,'teach_app/teach_video.html', frontend)    
    

def getTeacherLangauges(user_id):
    
    teacher_language_list = []
    conn = None
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.DictCursor)    
        query = "SELECT DISTINCT Languages.Language FROM colloquy_db.proficiency, colloquy_db.languages \
                    WHERE user_id=%s AND role<>'student' and languages.id=lang_id"
        values = (user_id)        
        cur = conn.cursor()
        cur.execute(query, values)  
        rows = cur.fetchall()
        
        for row in rows:
            print row
            teacher_language_list.append(row['Language'])
               
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()
        
        
    return teacher_language_list
    
    
    
    
    