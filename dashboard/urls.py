from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^lastjobswidget/$', views.lastjobswidget, name='lastjobswidget'),
    url(r'^cpuutilwidget/$', views.cpuutilwidget, name='cpuutilwidget'),
    url(r'^backupsizewidget/$', views.backupsizewidget, name='backupsizewidget'),
    url(r'^runningjobswidget/$', views.runningjobswidget, name='runningjobswidget'),
    url(r'^alljobswidget/$', views.alljobswidget, name='alljobswidget'),
    url(r'^allfileswidget/$', views.allfileswidget, name='allfileswidget'),
    url(r'^goeswrong/$', views.goeswrong, name='goeswrong'),
]
