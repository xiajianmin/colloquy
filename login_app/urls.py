'''
Created on Mar 12, 2013

@author: JianMin
'''
from django.conf.urls import patterns, include
from login_app import views as login

urlpatterns = patterns('login_app.view',

    # Main web portal entrance.
    (r'^$', login.loginView),

)