# Create your views here.

import os
import hashlib
import traceback
import MySQLdb as mdb
import MySQLdb.cursors

from django.shortcuts import render
from ConfigParser import SafeConfigParser
from django.http import HttpResponseRedirect


class InvalidEmail(Exception):
    print "User entered email not found in db!"


def __getDatabaseConnection(cursorType):
    
    parser = SafeConfigParser()
    parser.read(os.getcwd() + '\colloquy\config.ini')
    db_ip = parser.get('database_info', 'ip')
    db_user = parser.get('database_info', 'user')
    db_pass = parser.get('database_info', 'password')
    db_name = parser.get('database_info', 'db')
    
    conn = mdb.connect(db_ip, db_user, db_pass, db_name, cursorclass = cursorType)
    return conn

#TODO
def __sanatizeInput():
    pass

def loginView(request):
    
    frontend = {'valid_user':False,
                'status_msg':""}  
        
    if request.method == "POST":
        return authenticate(request, frontend)
    else:    
        return render(request, 'login_app/login.html')


def authenticate(request, frontend):    
     
        
    email = request.POST.get('email')
    raw_password = request.POST.get('password')
    user_id = ""
    conn = None;

    try:
        #Get user_id for associated email address
        conn = __getDatabaseConnection(MySQLdb.cursors.DictCursor)           
        cur = conn.cursor()   
                 
        query = "SELECT * FROM trash WHERE trash.email = %s"
        values = (email)
        rows = cur.execute(query, values)
        if(rows != 1):                
            raise InvalidEmail    
        record = cur.fetchone()
        
        
        #Salt and get hash of password
        salt = record['salt']
        user_id = record['user_id']
        hashed_password = hashlib.sha512(raw_password + salt).hexdigest()                      
        
        if(hashed_password == record['pass']):
            frontend['valid_user'] = True                          
        
    except:
        frontend['valid_user'] = False            
        print traceback.format_exc()
    finally:
        #context_instance = RequestContext(request,frontend)
        if conn: conn.close()        
            
    if frontend['valid_user']:
        return HttpResponseRedirect("/profile/?user_id="+str(user_id))
    else:
        frontend['status_msg'] = "Incorrect E-mail or Password!" 

    #return render_to_response('login_app/login.html',context_instance)
    return render(request, 'login_app/login.html', frontend)
 




