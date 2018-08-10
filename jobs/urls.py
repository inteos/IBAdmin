from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.defined, name='jobsdefined'),
    url(r'^data/$', views.defineddata, name='jobsdefineddata'),
    url(r'^running/$', views.running, name='jobsrunning'),
    url(r'^runningdata/$', views.runningdata, name='jobsrunningdata'),
    url(r'^finished/$', views.finished, name='jobsfinished'),
    url(r'^finisheddata/$', views.finisheddata, name='jobsfinisheddata'),
    url(r'^errors/$', views.errors, name='jobserrors'),
    url(r'^errorsdata/$', views.errorsdata, name='jobserrorsdata'),
    url(r'^warning/$', views.warning, name='jobswarning'),
    url(r'^warningdata/$', views.warningdata, name='jobswarningdata'),
    url(r'^queued/$', views.queued, name='jobsqueued'),
    url(r'^queueddata/$', views.queueddata, name='jobsqueueddata'),
    url(r'^last/$', views.jobslast, name='jobslast'),
    url(r'^lastdata/$', views.jobslastdata, name='jobslastdata'),

    url(r'^log/$', views.log, name='jobslog_rel'),
    url(r'^log/(?P<jobid>\d+)/$', views.log, name='jobslog'),
    url(r'^status/$', views.status, name='jobsstatus_rel'),
    url(r'^status/(?P<jobid>\d+)/$', views.status, name='jobsstatus'),
    url(r'^statusheader/$', views.statusheader, name='jobsstatusheader_rel'),
    url(r'^statusheader/(?P<jobid>\d+)/$', views.statusheader, name='jobsstatusheader'),
    url(r'^statusjoblog/$', views.statusjoblog, name='jobsstatusjoblog_rel'),
    url(r'^statusjoblog/(?P<jobid>\d+)/$', views.statusjoblog, name='jobsstatusjoblog'),
    url(r'^statusvolumes/$', views.statusvolumes, name='jobsstatusvolumes_rel'),
    url(r'^statusvolumes/(?P<jobid>\d+)/$', views.statusvolumes, name='jobsstatusvolumes'),
    url(r'^statusfinished/$', views.checkstatusfinished, name='jobsstatusfinished_rel'),
    url(r'^statusfinished/(?P<jobid>\d+)/$', views.checkstatusfinished, name='jobsstatusfinished'),
    url(r'^restorefiles/(?P<jobid>\d+)/$', views.restorefilesdata, name='jobsrestorefilesdata'),
    url(r'^backupfiles/(?P<jobid>\d+)/$', views.backupfilesdata, name='jobsbackupfilesdata'),

    url(r'^info/$', views.info, name='jobsinfo_rel'),
    url(r'^info/(?P<name>.*)/$', views.info, name='jobsinfo'),
    url(r'^historydata/(?P<name>.*)/$', views.historydata, name='jobshistorydata'),

    url(r'^makerun/$', views.makerun, name='jobsrun_rel'),
    url(r'^makerun/(?P<name>.*)/$', views.makerun, name='jobsrun'),
    url(r'^makedelete/$', views.makedelete, name='jobsdelete_rel'),
    url(r'^makedelete/(?P<name>.*)/$', views.makedelete, name='jobsdelete'),

    url(r'^id/makedelete/$', views.makedeleteid, name='jobsiddelete_rel'),
    url(r'^id/makedelete/(?P<jobid>\d+)/$', views.makedeleteid, name='jobsiddelete'),
    url(r'^id/makecancel/$', views.makecancelid, name='jobsidcancel_rel'),
    url(r'^id/makecancel/(?P<jobid>\d+)/$', views.makecancelid, name='jobsidcancel'),
    url(r'^id/makestop/$', views.makestopid, name='jobsidstop_rel'),
    url(r'^id/makestop/(?P<jobid>\d+)/$', views.makestopid, name='jobsidstop'),
    url(r'^id/makerestart/$', views.makerestartid, name='jobsidrestart_rel'),
    url(r'^id/makerestart/(?P<jobid>\d+)/$', views.makerestartid, name='jobsidrestart'),
    url(r'^id/comment/$', views.commentid, name='jobsidcomment_rel'),
    url(r'^id/comment/(?P<jobid>\d+)/$', views.commentid, name='jobsidcomment'),

    url(r'^statusnr/$', views.statusnr, name='jobsstatusnr'),
    url(r'^statuswidget/$', views.statuswidget, name='jobsstatuswidget'),

    url(r'^add/files/$', views.addfiles, name='jobsaddfiles'),
    url(r'^add/proxmox/$', views.addproxmox, name='jobsaddproxmox'),
    url(r'^editre/$', views.edit, name='jobsedit_rel'),
    url(r'^editre/(?P<name>.*)/$', views.edit, name='jobsedit'),
    url(r'^edit/files/(?P<name>.*)/$', views.editfiles, name='jobseditfiles'),
    url(r'^edit/proxmox/(?P<name>.*)/$', views.editproxmox, name='jobseditproxmox'),

    url(r'^advancedre/(?P<name>.*)/$', views.advanced, name='jobsadvanced'),
    url(r'^advanced/files/(?P<name>.*)/$', views.filesadvanced, name='jobsfilesadvanced'),
    url(r'^advanced/proxmox/(?P<name>.*)/$', views.proxmoxadvanced, name='jobsproxmoxadvanced'),
    url(r'^advanced/admin/(?P<name>.*)/$', views.adminadvanced, name='jobsadminadvanced'),
    url(r'^advanced/catalog/(?P<name>.*)/$', views.catalogdvanced, name='jobscatalogadvanced'),

    url(r'^name/$', views.jname, name='jobsname'),
]
