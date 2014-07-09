from django.conf.urls import patterns, include
from teach_app import views as teach

urlpatterns = patterns('langauge_app.view',

    # Main web portal entrance.
    #(r'^$', register.register_view),
    (r'^$', teach.selectLangaugeView),
    (r'^video/$', teach.videoView),

)