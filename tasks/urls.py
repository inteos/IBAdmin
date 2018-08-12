from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='taskslist'),
    url(r'^clearall/$', views.clearall, name='tasksclearall'),
    url(r'^historydata/$', views.historydata, name='taskshistorydata'),
    url(r'^statuswidget/$', views.statuswidget, name='tasksstatuswidget'),
    url(r'^statusnr/$', views.statusnr, name='tasksstatusnr'),
    url(r'^progress/$', views.progress, name='tasksprogress_rel'),
    url(r'^progress/(?P<taskid>[0-9]+)/$', views.progress, name='tasksprogress'),
    url(r'^status/$', views.status, name='tasksstatus_rel'),
    url(r'^status/(?P<taskid>[0-9]+)/$', views.status, name='tasksstatus'),
    url(r'^statusdata/(?P<taskid>[0-9]+)/$', views.statusdata, name='tasksstatusdata'),
    url(r'^delete/$', views.delete, name='tasksdelete_rel'),
    url(r'^delete/(?P<taskid>[0-9]+)/$', views.delete, name='tasksdelete'),
    url(r'^cancel/$', views.cancel, name='taskscancel_rel'),
    url(r'^cancel/(?P<taskid>[0-9]+)/$', views.cancel, name='taskscancel'),
]
