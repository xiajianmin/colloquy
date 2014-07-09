# Create your views here.
import os
import io
import uuid
import hashlib
import traceback
import MySQLdb as mdb
import MySQLdb.cursors

from forms import RegisterForm
from django.shortcuts import render
from ConfigParser import SafeConfigParser


def __getDatabaseConnection(cursorType):
    
    parser = SafeConfigParser()
    parser.read(os.path.join(os.getcwd(), "colloquy","config.ini"))

    db_ip = parser.get('database_info', 'ip')
    db_user = parser.get('database_info', 'user')
    db_pass = parser.get('database_info', 'password')
    db_name = parser.get('database_info', 'db')
    
    conn = mdb.connect(db_ip, db_user, db_pass, db_name, cursorclass = cursorType)
    return conn


def getCountryList():
    
    country_list = []
    return country_list


def registerView(request):    

    frontend = {'reg_success':False,
                'status_msg':""}
    
    if request.method == 'POST':
        return registerNewUser(request, frontend)                   
    else:
        frontend['form'] = RegisterForm()
        return render(request,'register_app/registration.html', frontend)


def registerNewUser(request, frontend): 
    
    form = RegisterForm(request.POST)
    frontend['form'] = form
    if form.is_valid():        
        cleaned_data = form.cleaned_data
        if __isDuplicateUser(cleaned_data['email']):
            frontend['status_msg'] = "A User With The Same Email Already Exists!"
        else:
            frontend['reg_success'] = addNewUser(cleaned_data)
            
            if frontend['reg_success']:
                frontend['status_msg'] = "Registration Successful! Please Login Now."
                return render(request, 'login_app/login.html', frontend)
            else:
                frontend['status_msg'] = "Something Went Wrong! :( Please Try to Register Again." 
            
    return render(request,'register_app/registration.html', frontend)
    

def addNewUser(data_bundle): 
   
    #Salt and get hash of password
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512(data_bundle['password'] + salt).hexdigest() 
          
    conn = None;
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.Cursor)
        user_image = __getDefaultUserImage(data_bundle['sex'])
        
        #TODO make it into a transaction
        query = "INSERT INTO user(first_name, last_name, dob, sex, email, pic) VALUES(%s, %s, %s, %s, %s, %s)"  
        values = (data_bundle['first_name'],
                 data_bundle['last_name'],
                 data_bundle['dob'],
                 data_bundle['sex'],
                 data_bundle['email'],
                 user_image)
             
        cur = conn.cursor()
        cur.execute(query, values)
        conn.commit()    
 
        user_id = cur.lastrowid
        query = "INSERT INTO trash(user_id, email, pass, salt) VALUES(%s, %s, %s, %s)"
        values = (user_id, data_bundle['email'], hashed_password, salt)
        cur.execute(query, values)
        conn.commit()    
        return True
    
    except mdb.Error, e:  
        conn.rollback()
        print "Error %d: %s" % (e.args[0],e.args[1])    
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()
                    
    return False


def __isDuplicateUser(user_email):
    
    ret = False
    conn = None;
    try:
        conn = __getDatabaseConnection(MySQLdb.cursors.Cursor)
        query = "SELECT EXISTS(SELECT 1 FROM user WHERE email = %s)"
        values = (user_email, )
        cur = conn.cursor()
        cur.execute(query, values)
        
        if cur.fetchone()[0] == 1:
            ret = True
    except:
        print traceback.format_exc()
    finally:
        if conn: conn.close()
        
    return ret


def __getDefaultUserImage(sex):
    
    
    file_name = ""
    
    if sex == "Male" :
        file_name = "blank_male.jpg"
    elif sex == "Female":
        file_name = "blank_female.jpg"
    elif sex == "Other":
        file_name = "blank_transgender.jpg"
    else:
        return None
        
    try:
        file_path = os.path.join(os.getcwd(), "colloquy", "colloquy", "static", file_name)
        with io.open(file_path, 'rb') as f:
            image_data = f.read()
    except:
        print traceback.format_exc()
        return None
        
    return image_data   
    
            
        
if __name__ == "__main__":
    
    data_bundle = {}
    data_bundle['first_name'] = "Sohan"
    data_bundle['last_name'] = "Rao"
    data_bundle['dob'] = "1978-04-17"
    data_bundle['sex'] = "Male"
    data_bundle['email'] = "rao21@illinois.edu"
    data_bundle['password'] = "sohanrao"
    #addNewUser(data_bundle)
    
    #print os.path.join(os.path.abspath(os.path.dirname(__file__)),r"a","b")   
    pass    

        
        
        
        
        