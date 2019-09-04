# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.defined, name='storagedefined'),
    url(r'^info/$', views.info, name='storageinfo_rel'),
    url(r'^info/(?P<name>.*)/$', views.info, name='storageinfo'),
    url(r'^historydata/(?P<name>.*)/$', views.historydata, name='storagehistorydata'),
    url(r'^status/$', views.status, name='storagestatus_rel'),
    url(r'^status/(?P<name>.*)/$', views.status, name='storagestatus'),
    url(r'^statusheader/(?P<name>.*)/$', views.statusheader, name='storagestatusheader'),
    url(r'^statusdevices/(?P<name>.*)/$', views.statusdevices, name='storagestatusdevices'),

    url(r'^enabledevice/(?P<storage>.*)/(?P<device>.*)/$', views.enabledevice, name='storageenabledevice'),
    url(r'^enabledevice/(?P<storage>.*)/$', views.enabledevice, name='storageenabledevice_rel'),
    url(r'^disabledevice/(?P<storage>.*)/(?P<device>.*)/$', views.disabledevice, name='storagedisabledevice'),
    url(r'^disabledevice/(?P<storage>.*)/$', views.umountdevice, name='storagedisabledevice_rel'),
    url(r'^umountdevice/(?P<storage>.*)/(?P<slot>.*)/(?P<device>.*)/$', views.umountdevice, name='storageumountdevice'),
    url(r'^umountdevice/(?P<storage>.*)/$', views.umountdevice, name='storageumountdevice_rel'),

    url(r'^dedup/(?P<name>.*)/$', views.dedup, name='storagededup'),
    url(r'^dedupdata/(?P<name>.*)/$', views.dedupdata, name='storagededupdata'),
    url(r'^label/(?P<storage>.*)/$', views.labeltape, name='storagelabel'),

    url(r'^name/$', views.sdname, name='storagename'),
    url(r'^address/$', views.address, name='storageaddress'),
    url(r'^archivedir$', views.archivedir, name='storagearchivedir'),

    url(r'^adddisk/$', views.adddisk, name='storageadddisk'),
    url(r'^adddedup/$', views.adddedup, name='storageadddedup'),
    url(r'^addtape/$', views.addtape, name='storageaddtape'),
    url(r'^addalias/$', views.addalias, name='storageaddalias'),

    url(r'^tapelibdetect/$', views.tapedetectlib, name='storagetapedetect_rel'),
    url(r'^tapelibdetect/(?P<tapeid>.*)/$', views.tapedetectlib, name='storagetapedetect'),
    url(r'^tapelibrescan/(?P<name>.*)/(?P<tapeid>.*)/$', views.taperescanlib, name='storagetaperescan'),
    url(r'^tapelibrescan/(?P<name>.*)/$', views.taperescanlib, name='storagetaperescan_rel'),
    url(r'^taskprogress/$', views.detectprogress, name='storagetapetaskprogress_rel'),
    url(r'^taskprogress/(?P<taskid>.*)/$', views.detectprogress, name='storagetapetaskprogress'),

    url(r'^edit/(?P<name>.*)/$', views.edit, name='storageedit'),
    url(r'^editdisk/(?P<name>.*)/$', views.editdisk, name='storageeditdisk'),
    url(r'^editdedup/(?P<name>.*)/$', views.editdedup, name='storageeditdedup'),
    url(r'^edittape/(?P<name>.*)/$', views.edittape, name='storageedittape'),
    url(r'^editalias/(?P<name>.*)/$', views.editalias, name='storageeditalias'),

    url(r'^volume/$', views.volinfo, name='storagevolumeinfo_rel'),
    url(r'^volume/(?P<name>.*)/$', views.volinfo, name='storagevolumeinfo'),
    url(r'^volumes/$', views.volumes, name='storagevolumes'),
    url(r'^volumesdata/$', views.volumesdata, name='storagevolumesdata'),
    url(r'^volumesnumber/$', views.storagevolumesnr, name='storagevolumesnr'),

    url(r'^vol/makeused/$', views.makeused, name='storagemakeused_rel'),
    url(r'^vol/makeused/(?P<name>.*)/$', views.makeused, name='storagemakeused'),
    url(r'^vol/makeappend/$', views.makeappend, name='storagemakeappend_rel'),
    url(r'^vol/makeappend/(?P<name>.*)/$', views.makeappend, name='storagemakeappend'),
    url(r'^vol/makepurged/$', views.makepurged, name='storagemakepurged_rel'),
    url(r'^vol/makepurged/(?P<name>.*)/$', views.makepurged, name='storagemakepurged'),
    url(r'^vol/makedelete/$', views.makedeletevolume, name='storagemakedeletevolume_rel'),
    url(r'^vol/makedelete/(?P<name>.*)/$', views.makedeletevolume, name='storagemakedeletevolume'),
    url(r'^vol/comment/$', views.comment, name='storagevolcomment_rel'),
    url(r'^vol/comment/(?P<name>.*)/$', views.comment, name='storagevolcomment'),

    url(r'^vol/historydata/(?P<name>.*)/$', views.volhistorydata, name='volumeshistorydata'),
    url(r'^vol/logdata/(?P<name>.*)/$', views.vollogdata, name='volumeslogdata'),
]
