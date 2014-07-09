'''
Created on Mar 14, 2013

@author: ACHIRA
'''
from django.conf.urls import patterns, include
from profile_app import views as profile

urlpatterns = patterns('profile_app.view',

    # Main web portal entrance.
    #(r'^$', register.register_view),
    (r'^$', profile.profileView),
    (r'^updated/$', profile.updateRecord),
    (r'^delete/$', profile.deleteRecord),
    (r'^video/$', profile.showVideo),
    (r'^language/', include('language_app.urls')),
    (r'^teach/', include('teach_app.urls')),
    (r'^learn/', include('learn_app.urls')),
)