from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_api import views

urlpatterns = [
    url(r'^service/$', views.service_list),
    url(r'^app/$', views.app_list),
    url(r'^login/$', views.user_authent),
]

urlpatterns = format_suffix_patterns(urlpatterns)
