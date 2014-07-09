# Create your views here.
import os
import traceback
import MySQLdb as mdb
import MySQLdb.cursors

from language_app.forms import AddLanguageForm, ModifyLanguageForm
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


def addLanguageView(request):
    
    frontend = {'status_msg':""}
    country_list = []
    user_id = request.GET.get('user_id','')
    language_name = request.GET.get('language','')
    
    if language_name != "":
        country_list = [(i[0], i[1]) for i in getCountryList(language_name)]      
        frontend['form'] = AddLanguageForm(choices=country_list)     

    frontend['language_name'] = language_name    
    frontend['user_id'] = user_id
    frontend['language_list'] = getLanguageList()    

    
    if request.method == 'POST' and "add_language" in request.POST:
        
        form = AddLanguageForm(request.POST, choices=country_list)
        frontend['form'] = form
        if form.is_valid():
            data_bundle = form.cleaned_data
            data_bundle['user_id'] = user_id
            data_bundle['language_name'] = language_name
            if addNewLanguage(frontend, data_bundle):
                del frontend['form']
                frontend['language_name'] = ""
            elif frontend['status_msg'] == "":
                frontend['status_msg'] = "Something Went Horribly Wrong! Try Again."      
            
    #Get added languages
    frontend['form_added_languages'] = ModifyLanguageForm(choices = getAddedLanguages(user_id)) 
    return render(request,'language_app/language.html', frontend)


def getAddedLanguages(user_id):    
    
    added_languages=[]
    conn = None
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.DictCursor)
        query = "SELECT * FROM colloquy_db.proficiency, colloquy_db.languages WHERE proficiency.lang_id=languages.id AND user_id=%s"
        values = (user_id,)        
        cur = conn.cursor()
        rows_affected = cur.execute(query, values)
        if rows_affected == 0:
            return added_languages
        
        rows = cur.fetchall()
        for row in rows:
            key = str(row['user_id']) + "_ "+ str(row['lang_id'])
            data = (row['Language'], str(row['speaking']), str(row['reading']), str(row['writing']), ("Yes" if row['isNative'] == '1' else "No"))
            value = "Name: %s Speaking: %s Reading: %s Writing: %s Native: %s"%(data)
            added_languages.append((key,value))
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()
    return added_languages
        
        
def addNewLanguage(frontend, data_bundle):
    
    conn = None
    ret = False
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.Cursor)
        
        #Get lang_id
        query = "SELECT id FROM colloquy_db.languages WHERE CountryCode=%s AND Language=%s"
        values = (data_bundle['country'], data_bundle['language_name'])        
        cur = conn.cursor()
        rows_affected = cur.execute(query, values)
        if rows_affected == 0:
            return False
        lang_id = cur.fetchone()[0]
        
        
        #Check if user has entered language before
        if __isUserLanguageExist(data_bundle['user_id'], lang_id):
            frontend['status_msg'] = "This Language is Already Added for User."
            return False     
        
        #Update language table , Insert to proficiency table   
        if data_bundle['role'] == "teacher": 
            role = ("1","0")
        elif data_bundle['role'] == "student": 
            role = ("0","1")
        elif data_bundle['role'] == "both":
            role = ("1","1")
        else:
            role = ("0","0")  
            
        cur = conn.cursor()
        query = "UPDATE colloquy_db.languages SET Teachers=Teachers+"+ role[0] +", Students=Students+"+ role[1] +" WHERE id=%s"
        values = (lang_id,) 
        cur.execute(query, values)        
        
        query = "INSERT INTO colloquy_db.proficiency (user_id, lang_id, speaking, reading, writing, isNative, role)\
                    VALUES(%s, %s, %s, %s, %s, %s, %s)"
        values = (data_bundle['user_id'], lang_id,
                  data_bundle['speaking'], data_bundle['reading'],
                  data_bundle['writing'], data_bundle['native'],
                  data_bundle['role'])           
        cur.execute(query, values)
        conn.commit()
        ret = True
    
    except mdb.Error, e: 
        print traceback.format_exc()
        conn.rollback()
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()
            
    return ret


def __isUserLanguageExist(user_id, lang_id):
    
    conn = None
    ret = True
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.Cursor)
        
        query = "SELECT EXISTS(SELECT 1 FROM colloquy_db.proficiency WHERE user_id= %s AND lang_id= %s )"
        values = (user_id, lang_id)        
        cur = conn.cursor()
        cur.execute(query, values)        
        if cur.fetchone()[0] == 0: 
            ret = False                
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()
    
    return ret


def getLanguageList():
    
    language_list = []
    conn = None
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.Cursor)
        query = "SELECT DISTINCT languages.Language FROM colloquy_db.languages ORDER BY Language ASC" 
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        
        for language in rows:          
            language_list.append(language[0]) 
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()   
            
    return language_list


def getCountryList(language_name):
    
    country_list = []
    conn = None
    language_name = language_name.replace("_"," ")
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.Cursor)
        query = "SELECT CountryCode, Name FROM country, colloquy_db.languages \
                    WHERE country.Code=languages.CountryCode AND Language=%s \
                    ORDER BY Name ASC"   
        values = (language_name,)       
        
        cur = conn.cursor()
        cur.execute(query, values)
        rows = cur.fetchall()
        
        for country in rows:          
            country_list.append([country[0], country[1]])
        
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()  

    return country_list



