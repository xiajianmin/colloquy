from django.conf.urls import patterns, include
from language_app import views as language

urlpatterns = patterns('langauge_app.view',

    # Main web portal entrance.
    #(r'^$', register.register_view),
    (r'^$', language.addLanguageView),

)