# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from subprocess import call
from django.contrib.auth.models import Group, Permission
from .system import *
from .tapelib import detectlibs
from config.conflib import getDIRcompid


def disableall(form):
    for key, value in form.fields.items():
        value.disabled = True


def preparestorages():
    storages = (('file', 'Disk based File storage'),)
    if detectdedup():
        storages += (('dedup', 'Disk based Global Deduplication storage'),)
    else:
        storages += (('dedup', {'label': 'Disk based Global Deduplication storage', 'disabled': True}),)
    libs = detectlibs()
    for l in libs:
        storages += (('tape' + l['id'], l['name'] + l['id']),)
    return storages


def stopallservices():
    # stop all services
    call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-dir'])
    call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-sd'])
    call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-fd'])
    call([SUDOCMD, SYSTEMCTL, 'stop', 'ibadstatd'])


def createconfigfiles(dirname='ibadmin'):
    # create config files
    with open('/opt/bacula/etc/bacula-dir.conf', 'w') as f:
        f.write(str('@|"/opt/ibadmin/utils/ibadconf.py -d"\n'))
        f.close()
    with open('/opt/bacula/etc/bacula-sd.conf', 'w') as f:
        f.write(str('@|"/opt/ibadmin/utils/ibadconf.py -s %s"\n' % dirname))
        f.close()
    with open('/opt/bacula/etc/bacula-fd.conf', 'w') as f:
        f.write(str('@|"/opt/ibadmin/utils/ibadconf.py -f %s"\n' % dirname))
        f.close()
    with open('/opt/bacula/etc/bconsole.conf', 'w') as f:
        f.write(str('@|"/opt/ibadmin/utils/ibadconf.py -c"\n'))
        f.close()


def startallservices():
    # start all services
    call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-dir'])
    call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-sd'])
    call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-fd'])
    call([SUDOCMD, SYSTEMCTL, 'start', 'ibadstatd'])


def createsystemrole(name='Default Role', descr='System Role', color='bg-blue', permlist=()):
    role = Group.objects.create(name=name)
    role.roles.description = descr
    role.roles.color = color
    role.roles.internal = True
    roleperms = Permission.objects.filter(content_type__model='permissions', codename__in=permlist)
    role.permissions.set(roleperms)
    role.save()


def createsystemroleifrequired(name='Default Role', descr='System Role', color='bg-blue', permlist=()):
    group = Group.objects.filter(name=name)
    if group.count() > 0:
        if group[0].roles.internal is False:
            group.delete()
            createsystemrole(name=name, descr=descr, color=color, permlist=permlist)
    else:
        createsystemrole(name=name, descr=descr, color=color, permlist=permlist)


def createDefaultRole():
    name = 'Default Role'
    descr = 'System Default Role for minimal usable user access.'
    permlist = ('view_jobs', 'status_jobs', 'view_clients', 'status_clients', 'view_job_stats')
    createsystemroleifrequired(name=name, descr=descr, permlist=permlist)


def postinitial(request):
    """
    Executed when application was initialized and needs to make some final adjustments.
    :param request: django request
    :return: no
    """
    # print ("PostInitial")
    createDefaultRole()


def postupgrade(request):
    """
    Executed on every login to check if we need to apply some upgrade procedures.
    :return: no
    """
    # print ("PostUpgrade")
    createDefaultRole()
