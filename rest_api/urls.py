from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_api import views

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^services/$', views.service_list, name='services'),
    url(r'^instances/$', views.app_list, name='instances'),
    url(r'^authentication/$', views.user_authent),
]

urlpatterns = format_suffix_patterns(urlpatterns)
