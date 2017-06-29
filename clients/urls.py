from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.defined, name='clientsdefined'),
    url(r'^data/$', views.defineddata, name='clientsdefineddata'),
    url(r'^info/$', views.info, name='clientsinfo_rel'),
    url(r'^info/(?P<name>.*)/$', views.info, name='clientsinfo'),
    url(r'^infodata/(?P<name>.*)/$', views.infodefineddata, name='clientsinfodefineddata'),
    url(r'^historydata/(?P<name>.*)/$', views.historydata, name='clientshistorydata'),
    url(r'^status/$', views.status, name='clientsstatus_rel'),
    url(r'^status/(?P<name>.*)/$', views.status, name='clientsstatus'),
    url(r'^statusheader/$', views.statusheader, name='clientsstatusheader_rel'),
    url(r'^statusheader/(?P<name>.*)/$', views.statusheader, name='clientsstatusheader'),
    url(r'^statusrunning/$', views.statusrunning, name='clientsstatusrunning_rel'),
    url(r'^statusrunning/(?P<name>.*)/$', views.statusrunning, name='clientsstatusrunning'),
    url(r'^add/$', views.addstd, name='clientsadd'),
    url(r'^addstd/$', views.addstd, name='clientsaddstd'),
    url(r'^addnode/$', views.addnode, name='clientsaddnode'),
    url(r'^addservice/$', views.addservice, name='clientsaddservice'),
    url(r'^addalias/$', views.addalias, name='clientsaddalias'),
    url(r'^edit/$', views.edit, name='clientsedit_rel'),
    url(r'^edit/(?P<name>.*)/$', views.edit, name='clientsedit'),
    url(r'^editstd/(?P<name>.*)/$', views.editstd, name='clientseditstd'),
    url(r'^editservice/(?P<name>.*)/$', views.editservice, name='clientseditservice'),
    url(r'^editalias/(?P<name>.*)/$', views.editalias, name='clientseditalias'),
    url(r'^address/$', views.address, name='clientsaddress'),
    url(r'^name/$', views.name, name='clientsname'),
    url(r'^clustername/$', views.clustername, name='clientsclustername'),
    url(r'^makedelete/$', views.makedelete, name='clientsdelete_rel'),
    url(r'^makedelete/(?P<name>.*)/$', views.makedelete, name='clientsdelete'),
]
