from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_api import views

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^services$', views.service_list, name='services'),
    url(r'^projects$', views.project_list, name='projects'),
    url(r'^projects/(?P<pro>\S+)$', views.project, name='project'),
    url(r'^service', views.service, name='service'),
    url(r'^log$', views.log, name='logs'),
    url(r'^monitor$', views.monitor, name='monitor'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
