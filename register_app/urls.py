'''
Created on Mar 12, 2013

@author: JianMin
'''
from django.conf.urls import patterns
from register_app import views as register

urlpatterns = patterns('register_app.view',

    # Main web portal entrance.
    (r'^$', register.registerView),
    #(r'^reg_success/$', register.addUser),

)