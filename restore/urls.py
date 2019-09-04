# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^client/$', views.client, name='restoreclient_rel'),
    url(r'^client/(?P<name>.*)/$', views.client, name='restoreclient'),
    url(r'^job/$', views.job, name='restorejob_rel'),
    url(r'^job/(?P<name>.*)/$', views.job, name='restorejob'),
    url(r'^jobid/$', views.jobidre, name='restorejobid_rel'),
    url(r'^jobid/(?P<jobid>\d+)/$', views.jobidre, name='restorejobid'),
    url(r'^jobidfiles/$', views.jobidfiles, name='restorejobidfiles_rel'),
    url(r'^jobidfiles/(?P<jobid>\d+)/$', views.jobidfiles, name='restorejobidfiles'),
    url(r'^jobidproxmox/$', views.jobidproxmox, name='restorejobidproxmox_rel'),
    url(r'^jobidproxmox/(?P<jobid>\d+)/$', views.jobidproxmox, name='restorejobidproxmox'),
    url(r'^jobidxenserver/$', views.jobidxenserver, name='restorejobidxenserver_rel'),
    url(r'^jobidxenserver/(?P<jobid>\d+)/$', views.jobidxenserver, name='restorejobidxenserver'),
    url(r'^jobidvmware/$', views.jobidvmware, name='restorejobidvmware_rel'),
    url(r'^jobidvmware/(?P<jobid>\d+)/$', views.jobidvmware, name='restorejobidvmware'),
    url(r'^jobidkvm/$', views.jobidkvm, name='restorejobidkvm_rel'),
    url(r'^jobidkvm/(?P<jobid>\d+)/$', views.jobidkvm, name='restorejobidkvm'),
    url(r'^jobidcatalog/$', views.jobidcatalog, name='restorejobidcatalog_rel'),
    url(r'^jobidcatalog/(?P<jobid>\d+)/$', views.jobidcatalog, name='restorejobidcatalog'),

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
    url(r'^treexenserver/(?P<jobids>.*)/(?P<pathid>.*)/$', views.displaytreexenserver, name='restoretreexenserver'),
    url(r'^treexenserver/(?P<jobids>.*)/$', views.displaytreexenserver, name='restoretreexenserver_rel'),
    url(r'^treevmware/(?P<jobids>.*)/(?P<pathid>.*)/$', views.displaytreevmware, name='restoretreevmware'),
    url(r'^treevmware/(?P<jobids>.*)/$', views.displaytreevmware, name='restoretreevmware_rel'),
    url(r'^treekvm/(?P<jobids>.*)/(?P<pathid>.*)/$', views.displaytreekvm, name='restoretreekvm'),
    url(r'^treekvm/(?P<jobids>.*)/$', views.displaytreekvm, name='restoretreekvm_rel'),

    url(r'^prepare/(?P<jobids>.*)/$', views.preparerestorefiles, name='restoreprepare'),
    url(r'^prepareproxmox/(?P<jobids>.*)/$', views.preparerestoreproxmox, name='restoreprepareproxmox'),
    url(r'^preparexenserver/(?P<jobids>.*)/$', views.preparerestorexenserver, name='restorepreparexenserver'),
    url(r'^preparevmware/(?P<jobids>.*)/$', views.preparerestorevmware, name='restorepreparevmware'),
    url(r'^preparekvm/(?P<jobids>.*)/$', views.preparerestorekvm, name='restorepreparekvm'),
]
