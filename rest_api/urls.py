from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
from rest_api import views

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^services$', views.service_list, name='services'),
    url(r'^projects$', views.project_list, name='instances'),
    url(r'^auth$', obtain_auth_token),
]

urlpatterns = format_suffix_patterns(urlpatterns)
