# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.defined, name='departsdefined'),
    url(r'^data/$', views.defineddata, name='departsdefineddata'),
    url(r'^info/$', views.info, name='departsinfo_rel'),
    url(r'^info/(?P<name>.*)/$', views.info, name='departsinfo'),
    url(r'^add/$', views.adddep, name='departsadd'),
    url(r'^edit/$', views.editdep, name='departsedit_rel'),
    url(r'^edit/(?P<name>.*)/$', views.editdep, name='departsedit'),
    url(r'^makedelete/$', views.makedelete, name='departsmakedelete_rel'),
    url(r'^makedelete/(?P<name>.*)/$', views.makedelete, name='departsmakedelete'),
    url(r'^name/$', views.deptname, name='departsname'),
    url(r'^nameother/(?P<name>.*)/$', views.nameother, name='departsnameother'),
    url(r'^shortname/$', views.shortname, name='departsshortname'),
    url(r'^shortnameother/(?P<name>.*)/$', views.shortnameother, name='departsshortnameother'),
    url(r'^infoadmins/(?P<shortdname>.*)/$', views.infoadmins, name='departsinfoadmins'),
    url(r'^infousers/(?P<shortdname>.*)/$', views.infousers, name='departsinfousers'),
    url(r'^addmember/(?P<shortdname>.*)/$', views.addmember, name='departsaddmember'),
    url(r'^deletemember/(?P<shortdname>.*)/(?P<username>.*)/$', views.deletemember, name='departsdeletemember'),
    url(r'^deletemember/(?P<shortdname>.*)/$', views.deletemember, name='departsdeletemember_rel'),
]

