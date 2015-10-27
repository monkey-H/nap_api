from django.conf.urls import patterns, url
from filebrowser import views

urlpatterns = patterns('',
    url(r'^$', views.test_hello),
    url(r'^filebrowser/api/$', views.api),
    url(r'^filebrowser/upload/$', views.upload),
)
