# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from storages.models import *
from stats.models import *
from .user import *
from .system import detectdedup


def getStorageStatus_a(name=None):
    """ Status asynchroniczny z tabeli stat_status """
    param = 'bacula.daemon.bacula-sd.status'
    try:
        out = int(StatStatus.objects.get(parid__name=param).nvalue)
    except:
        out = 0
    return out


def extractstorageparams(storage):
    status = getStorageStatus_a()
    storageparams = {
        'Name': storage['Name'],
        'Descr': storage['Descr'],
        'Status': status
    }
    for param in storage['Params']:
        if param['name'] == '.Department':
            if 'Departments' in storageparams:
                storageparams['Departments'].append(param['value'])
            else:
                storageparams['Departments'] = [param['value'], ]
        else:
            storageparams[param['name'].replace('.', '')] = param['value']
    storageparams['MType'] = storageparams.get('MediaType', '')[:4]
    return storageparams


def getStorageDefinednr(request):
    if not hasattr(request, "ibadminstoragesdefinednr"):
        request.ibadminstoragesdefinednr = getUserStorages(request).count()
    return request.ibadminstoragesdefinednr


def updateStorageDefinednr(request, context):
    val = getStorageDefinednr(request)
    context.update({'storagenr': val})


def getStorageVolumesnr():
    return Media.objects.count()


def updateStorageVolumesnr(request, context):
    val = getStorageVolumesnr()
    context.update({'storagevolumesnr': val})


def storagededupavailable():
    ded = ConfParameter.objects.filter(name='.StorageDirDedupidx').count()
    val = detectdedup()
    return (ded < 1) and val


def updateStoragedetectdedup(request, context):
    context.update({'storagedetectdedup': storagededupavailable()})


def getDIRStorageNames(request, dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid(request)
    # list of the all Storages for clients available
    userstorages = getUserStorages(request, dircompid=dircompid)
    storagenames = ()
    for sr in userstorages.order_by('name'):
        storagenames += (sr.name,)
    return storagenames


def getDIRStorageNamesnAlias(request, dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid(request)
    # list of the all Storages for clients available
    userstorages = getUserStorages(request, dircompid=dircompid)
    storagenames = ()
    for sr in userstorages.exclude(confparameter__name='.Alias').order_by('name'):
        storagenames += (sr.name,)
    return storagenames


def getStorageNames():
    # list of the all Storage components available
    storages = ConfComponent.objects.filter(type='S').order_by('name')
    storagenames = ()
    for sr in storages:
        storagenames += (sr.name,)
    return storagenames


def makeinitialdata(name, storage):
    data = {
        'name': name,
        'descr': storage['Descr'],
        'address': storage['Address'],
        'storagelist': storage['StorageComponent'],
        'archivedir': storage.get('StorageDirDevice', 'unknown'),
        'dedupidxdir': storage.get('StorageDirDedupidx', 'unknown'),
        'dedupdir': storage.get('StorageDirDevice', 'unknown'),
        'departments': storage.get('Departments', ()),
    }
    return data


def makeinitialaliasdata(name, storage):
    data = {
        'name': name,
        'descr': storage['Descr'],
        'storagelist': storage['Alias'],
        'storageip': storage['Address'],
        'departments': storage.get('Departments')[0] if type(storage.get('Departments')) is list else ''
    }
    return data

