from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^client/(?P<name>.*)/$', views.clientconfig, name='confclientconfig'),
]
