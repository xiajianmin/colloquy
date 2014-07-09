from django.conf.urls import patterns, include
from colloquy import views as index
from login_app import views as login
from register_app import views as register
from profile_app import views as profile
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
urlpatterns = patterns('',
                       (r'^$', index.indexView),
                       (r'^index/$', index.indexView),
                       (r'^login/', include('login_app.urls')),                       
                       (r'^register/', include('register_app.urls')),
                       (r'^profile/', include('profile_app.urls')),

                       #(r'^profile/$', profile.profile_view),
                       #(r'^profile/updated/$', profile.updateRecord),
                       #(r'^profile/delete/$', profile.deleteRecord),
                       
    # Examples:
    # url(r'^$', 'Colloquy.views.home', name='home'),
    # url(r'^Colloquy/', include('Colloquy.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)), 
)

urlpatterns += staticfiles_urlpatterns()
