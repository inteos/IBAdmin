# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.defined, name='usersdefined'),
    url(r'^data/$', views.defineddata, name='usersdefineddata'),
    url(r'^info/$', views.info, name='usersinfo_rel'),
    url(r'^info/(?P<username>.*)/$', views.info, name='usersinfo'),
    url(r'^infodeparts/(?P<username>.*)/$', views.infodeparts, name='usersinfodeparts'),
    url(r'^inforoles/(?P<username>.*)/$', views.inforoles, name='usersinforoles'),
    url(r'^adddepart/(?P<username>.*)/$', views.adddepart, name='usersadddepart'),
    url(r'^departdelete/(?P<username>.*)/(?P<name>.*)/$', views.departdelete, name='usersdepartdelete'),
    url(r'^departdelete/(?P<username>.*)/$', views.departdelete, name='usersdepartdelete_rel'),
    url(r'^addroles/(?P<username>.*)/$', views.addroles, name='usersaddroles'),
    url(r'^rolesdelete/(?P<username>.*)/(?P<name>.*)/$', views.rolesdelete, name='usersrolesdelete'),
    url(r'^rolesdelete/(?P<username>.*)/$', views.rolesdelete, name='usersrolesdelete_rel'),
    url(r'^profile/$', views.userprofile, name='usersprofile'),
    url(r'^profile/edit/$', views.userprofileedit, name='usersprofileedit'),
    url(r'^profile/dashboard/(?P<stat>on|off)/$', views.userprofiledash, name='usersprofiledash_rel'),
    url(r'^profile/dashboard/(?P<stat>on|off)/(?P<widgetid>.*)/$', views.userprofiledash, name='usersprofiledash'),
    url(r'^add/$', views.adduser, name='usersadd'),
    url(r'^edit/$', views.edit, name='usersedit_rel'),
    url(r'^edit/(?P<username>.*)/$', views.edit, name='usersedit'),
    url(r'^username/$', views.checkusername, name='usersname'),
    url(r'^lock/$', views.userlock, name='userslock_rel'),
    url(r'^lock/(?P<username>.*)/$', views.userlock, name='userslock'),
    url(r'^unlock/$', views.userunlock, name='usersunlock_rel'),
    url(r'^unlock/(?P<username>.*)/$', views.userunlock, name='usersunlock'),
    url(r'^delete/$', views.userdelete, name='usersdelete_rel'),
    url(r'^delete/(?P<username>.*)/$', views.userdelete, name='usersdelete'),
]

