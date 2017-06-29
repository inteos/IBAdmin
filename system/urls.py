from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^daemons/$', views.daemons, name='daemonindex'),
    url(r'^daemons/servicestatuswidget/$', views.servicestatuswidget, name='servicestatuswidget'),
    url(r'^daemons/log/master/$', views.masterlogdisplay, name='daemonmasterlog'),
    url(r'^daemons/log/sd/$', views.sdlogdisplay, name='daemonsdlog'),
    url(r'^daemons/log/fd/$', views.fdlogdisplay, name='daemonfdlog'),
    url(r'^daemons/log/ibad/$', views.ibadlogdisplay, name='daemonibadlog'),
    url(r'^daemons/stop/master/$', views.masterstop, name='daemonmasterstop'),
    url(r'^daemons/stop/storage/$', views.storagestop, name='daemonstoragestop'),
    url(r'^daemons/stop/file/$', views.filedaemonstop, name='daemonfdstop'),
    url(r'^daemons/stop/ibad/$', views.ibaddaemonstop, name='daemonibadstop'),
    url(r'^daemons/start/master/$', views.masterstart, name='daemonmasterstart'),
    url(r'^daemons/start/storage/$', views.storagestart, name='daemonstoragestart'),
    url(r'^daemons/start/file/$', views.filedaemonstart, name='daemonfdstart'),
    url(r'^daemons/start/ibad/$', views.ibaddaemonstart, name='daemonibadstart'),
    url(r'^daemons/restart/master/$', views.masterrestart, name='daemonmasterrestart'),
    url(r'^daemons/restart/storage/$', views.storagerestart, name='daemonstoragerestart'),
    url(r'^daemons/restart/file/$', views.filedaemonrestart, name='daemonfdrestart'),
    url(r'^daemons/restart/ibad/$', views.ibaddaemonrestart, name='daemonibadrestart'),
    url(r'^config/$', views.config, name='systemconfig'),
    url(r'^config/save/$', views.configsave, name='systemconfigsave'),
    url(r'^messages/$', views.messages, name='systemmessages'),
    url(r'^messages/data/$', views.messagesdata, name='systemmessagesdata'),
    url(r'^messages/clear/$', views.messagesclear, name='systemmessagesclear'),
]
