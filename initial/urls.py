# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='initial'),
    url(r'^setup/$', views.initialsetup, name='initialsetup'),
    url(r'^setup2/$', views.initialsetup2, name='initialsetup2'),
    url(r'^libdetect/$', views.libdetect, name='initiallibdetect'),
    url(r'^taskprogress/$', views.taskprogress, name='initialtaskprogress'),
    url(r'^archivedir/$', views.archivedir, name='initialarchivedir'),
]

