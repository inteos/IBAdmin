from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='initial'),
    url(r'^setup$', views.initalize, name='initialsetup'),
    url(r'^archivedir$', views.archivedir, name='initialarchivedir'),
]

