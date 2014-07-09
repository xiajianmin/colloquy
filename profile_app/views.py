# Create your views here.
import os
import cStringIO
import MySQLdb as mdb
import MySQLdb.cursors
import traceback

from ConfigParser import SafeConfigParser
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render


#user_id = None

def __getDatabaseConnection(cursorType):
    
    parser = SafeConfigParser()
    parser.read(os.path.join(os.getcwd(), "colloquy","config.ini"))
    db_ip = parser.get('database_info', 'ip')
    db_user = parser.get('database_info', 'user')
    db_pass = parser.get('database_info', 'password')
    db_name = parser.get('database_info', 'db')
    
    conn = mdb.connect(db_ip, db_user, db_pass, db_name, cursorclass = cursorType)
    return conn


def profileView(request):
    
    
    frontend = {'user_id':request.GET.get('user_id','')}
    #global user_id 
    #user_id = frontend['user_id']
    
    conn = None;
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.DictCursor)
        query = "SELECT * FROM user WHERE user.id = %s"
        values = (long(frontend['user_id']), )
        cur = conn.cursor()
        cur.execute(query, values)
        
        record = cur.fetchone()
        
        frontend["first_name"] = record['first_name']
        frontend["last_name"] = record['last_name']
        frontend["sex"] = record['sex']
        frontend["dob"] = record['dob']
        frontend["email"] = record['email']
        frontend["image"] = ""
        
        if record["pic"] is not None:
            img_stream = cStringIO.StringIO(record["pic"]) 
            data_uri = 'data:image/jpg;base64,'
            data_uri += img_stream.getvalue().encode('base64').replace('\n', '') 
            frontend["image"] = data_uri      
 
    except:        
        print traceback.format_exc()        
    finally:
        if conn: conn.close()
        
    #context_instance = RequestContext(request,frontend)  
    return render(request, 'profile_app/profile.html/', frontend)


def updateRecord(request):
        
    if request.method == 'POST':
        data_bundle = request.POST.copy()
        user_id = data_bundle['user_id']
        conn = None;
        try:
            conn = __getDatabaseConnection(MySQLdb.cursors.Cursor)
            query = "UPDATE user SET email = %s WHERE id = %s"
            values = (data_bundle['email'], user_id)
            
            cur = conn.cursor()
            cur.execute(query, values)
            conn.commit()
            
        except mdb.Error, e:  
            conn.rollback()
            print "Error %d: %s" % (e.args[0],e.args[1])         
        except:
            print traceback.format_exc()
        finally:
            if conn: conn.close()        
            
    return HttpResponseRedirect("/profile/?user_id="+str(user_id))



def deleteRecord(request):
    
    
    if request.method == 'POST':        
        user_id = request.POST.get('user_id','')
        conn = None;
        try:
            conn = __getDatabaseConnection(MySQLdb.cursors.Cursor)
            query = "DELETE FROM user WHERE id = %s"
            values = (long(user_id), )
            cur = conn.cursor()
            cur.execute(query, values)
            
            #query = "DELETE FROM trash WHERE user_id=%d"%(long(user_id))
            #cur = conn.cursor()
            #cur.execute(query)
            
            conn.commit()
            user_id = None 
        except mdb.Error, e:  
            conn.rollback()
            print "Error %d: %s" % (e.args[0],e.args[1])            
        except:
            print traceback.format_exc()            
        finally:
            if conn: conn.close()
        
            
    return HttpResponseRedirect("/login")
    
 
def showVideo(request):
    user_id = request.GET.get('user_id','')
    frontend = {'user_id': user_id}
    return render(request, "profile_app/video.html/", frontend)
               
            