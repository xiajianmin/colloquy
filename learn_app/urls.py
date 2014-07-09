'''
Created on Mar 12, 2013

@author: JianMin
'''
from django.conf.urls import patterns, include
from learn_app import views as learn

urlpatterns = patterns('login_app.view',

    # Main web portal entrance.
    (r'^$', learn.learnView),

    #(r'searchTutor/^$', learn.searchTutor),

)