# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^vcenter/$', views.vcenterdefined, name='vmsvcenterdefined'),
    url(r'^vcenterdata/$', views.vcenterdefineddata, name='vmsvcenterdefineddata'),
    url(r'^vcenterclientdata/$', views.vcenterclientdefineddata, name='vmsvcenterclientdefineddata'),
    url(r'^proxmox/$', views.proxmoxdefined, name='vmsproxmoxdefined'),
    url(r'^proxmoxdata/$', views.proxmoxdefineddata, name='vmsproxmoxdefineddata'),
    url(r'^xenserver/$', views.xenserverdefined, name='vmsxenserverdefined'),
    url(r'^xenserverdata/$', views.xenserverdefineddata, name='vmsxenserverdefineddata'),
    url(r'^kvmhost/$', views.kvmhostdefined, name='vmskvmhostdefined'),
    url(r'^kvmhostdata/$', views.kvmhostdefineddata, name='vmskvmhostdefineddata'),

    url(r'^proxmoxvmlist/(?P<name>.*)/$', views.proxmoxvmlist, name='vmsproxmoxvmlist'),
    url(r'^proxmoxvmlist/$', views.proxmoxvmlist, name='vmsproxmoxvmlist_ref'),
    url(r'^xenservervmlist/(?P<name>.*)/$', views.xenservervmlist, name='vmsxenservervmlist'),
    url(r'^xenservervmlist/$', views.xenservervmlist, name='vmsxenservervmlist_rel'),

    url(r'^addvcenter/$', views.addvcenter, name='vmsaddvcenter'),
    url(r'^addproxmox/$', views.addproxmox, name='vmsaddproxmox'),
    url(r'^addxenserver/$', views.addxenserver, name='vmsaddxenserver'),
    url(r'^addkvmhost/$', views.addkvmhost, name='vmsaddkvmhost'),
    url(r'^addvcenterclient/$', views.addvcenterclient, name='vmsaddvcenterclient'),
    url(r'^editvcenter/(?P<name>.*)/$', views.editvcenter, name='vmsvcenteredit'),
    url(r'^editvcenter/$', views.editvcenter, name='vmsvcenteredit_rel'),
    url(r'^vcentername/$', views.vcentername, name='vmsvcentername'),
    url(r'^vcenterthp/$', views.getvcenterthumbprint, name='vmsgetvcenterthumbprint'),
    url(r'^vcenterinfo/(?P<name>.*)/$', views.vcenterinfo, name='vmsvcenterinfo'),
    url(r'^vcenterinfo/$', views.vcenterinfo, name='vmsvcenterinfo_rel'),
    url(r'^makedelete/vcenter/$', views.makedeletevcenter, name='vcenterdelete_rel'),
    url(r'^makedelete/vcenter/(?P<name>.*)/$', views.makedeletevcenter, name='vcenterdelete'),
]
