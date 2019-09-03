# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^client/(?P<name>.*)/$', views.clientconfig, name='confclientconfig'),
    url(r'^vsphere/(?P<name>.*)/$', views.vsphereconfig, name='confvsphereconfig'),
]
