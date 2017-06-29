from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^backup/jobs/$', views.backup_jobs, name='statsbackupjobs'),
    url(r'^backup/volumes/$', views.backup_volumes, name='statsbackupvolumes'),
    url(r'^backup/tapes/$', views.backup_tapes, name='statsbackuptapes'),
    url(r'^backup/sizes/$', views.backup_sizes, name='statsbackupsizes'),

    url(r'^system/cpu/$', views.system_cpu, name='statssystemcpu'),
    url(r'^system/memory/$', views.system_memory, name='statssystemmemory'),
    url(r'^system/swap/$', views.system_swap, name='statssystemswap'),
    url(r'^system/disks/$', views.system_disks, name='statssystemdisks'),
    url(r'^system/fs/$', views.system_fs, name='statssystemfs'),
    url(r'^system/net/$', views.system_net, name='statssystemnet'),

    url(r'^server/$', views.stats_server, name='statsserver'),
    url(r'^clients/$', views.stats_client, name='statsclients'),

    url(r'^job/(?P<name>.*)/$', views.stats_job, name='statsjob'),

    url(r'^data/(?P<name>.*)/(?P<starttime>\d+)/(?P<endtime>\d+)/(?P<chart>\d)/(?P<valdiv>\d+)/$', views.statdata, name='statsdata'),
    url(r'^data/(?P<name>.*)/$', views.statdata, name='statsdata_rel'),
    url(r'^sizedata/(?P<name>.*)/(?P<level>.*)/(?P<last>\d+)/(?P<chart>\d)/(?P<valdiv>\d+)/$', views.statsizedata, name='statssizedata'),
    url(r'^sizedata/(?P<name>.*)/(?P<level>.*)/$', views.statsizedata, name='statssizedata_rel'),
    url(r'^filedata/(?P<name>.*)/(?P<level>.*)/(?P<last>\d+)/(?P<chart>\d)/(?P<valdiv>\d+)/$', views.statfiledata, name='statsfiledata'),
    url(r'^filedata/(?P<name>.*)/(?P<level>.*)/$', views.statfiledata, name='statsfiledata_rel'),
    url(r'^timedata/(?P<name>.*)/(?P<level>.*)/(?P<last>\d+)/(?P<chart>\d)/(?P<valdiv>\d+)/$', views.stattimedata, name='statstimedata'),
    url(r'^timedata/(?P<name>.*)/(?P<level>.*)/$', views.stattimedata, name='statstimedata_rel'),
    url(r'^avgdata/(?P<name>.*)/(?P<level>.*)/(?P<last>\d+)/(?P<chart>\d)/(?P<valdiv>\d+)/$', views.statavgdata, name='statsavgdata'),
    url(r'^avgdata/(?P<name>.*)/(?P<level>.*)/$', views.statavgdata, name='statsavgdata_rel'),
]
