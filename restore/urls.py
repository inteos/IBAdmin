from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^client/$', views.client, name='restoreclient_rel'),
    url(r'^client/(?P<name>.*)/$', views.client, name='restoreclient'),
    url(r'^job/$', views.job, name='restorejob_rel'),
    url(r'^job/(?P<name>.*)/$', views.job, name='restorejob'),
    url(r'^jobid/$', views.jobidre, name='restorejobid_rel'),
    url(r'^jobid/(?P<jobid>.*)/$', views.jobidre, name='restorejobid'),
    url(r'^jobidfiles/$', views.jobidfiles, name='restorejobidfiles_rel'),
    url(r'^jobidfiles/(?P<jobid>.*)/$', views.jobidfiles, name='restorejobidfiles'),
    url(r'^jobidproxmox/$', views.jobidproxmox, name='restorejobidproxmox_rel'),
    url(r'^jobidproxmox/(?P<jobid>.*)/$', views.jobidproxmox, name='restorejobidproxmox'),
    url(r'^jobidcatalog/$', views.jobidcatalog, name='restorejobidcatalog_rel'),
    url(r'^jobidcatalog/(?P<jobid>.*)/$', views.jobidcatalog, name='restorejobidcatalog'),

    url(r'^historydata/(?P<name>.*)/$', views.historydata, name='restorehistorydata'),
    url(r'^displayfs/$', views.displayfs, name='restoredisplayfs_rel'),
    url(r'^displayfs/(?P<name>.*)/$', views.displayfs, name='restoredisplayfs'),
    url(r'^updatecache/(?P<jobids>.*)/$', views.updatecache, name='restoreupdatecache'),
    url(r'^tree/(?P<jobids>.*)/(?P<pathid>.*)/$', views.displaytree, name='restoretree'),
    url(r'^tree/(?P<jobids>.*)/$', views.displaytree, name='restoretree_rel'),
    url(r'^treecatalog/(?P<jobids>.*)/(?P<pathid>.*)/$', views.displaytreecatalog, name='restoretreecatalog'),
    url(r'^treecatalog/(?P<jobids>.*)/$', views.displaytreecatalog, name='restoretreecatalog_rel'),
    url(r'^treeproxmox/(?P<jobids>.*)/(?P<pathid>.*)/$', views.displaytreeproxmox, name='restoretreeproxmox'),
    url(r'^treeproxmox/(?P<jobids>.*)/$', views.displaytreeproxmox, name='restoretreeproxmox_rel'),

    url(r'^prepare/(?P<jobids>.*)/$', views.preparerestorefiles, name='restoreprepare'),
    url(r'^prepareproxmox/(?P<jobids>.*)/$', views.preparerestoreproxmox, name='restoreprepareproxmox'),
]
