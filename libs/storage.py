from __future__ import unicode_literals
from storages.models import *
from config.models import *
from stats.models import *
from .system import detectdedup
# from django.db import connection
# from socket import gethostbyname


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
    storageparams = {'Name': storage['Name'], 'Descr': storage['Descr'], 'Status': status}
    for param in storage['Params']:
        storageparams[param['name'].replace('.', '')] = param['value']
    storageparams['MType'] = storageparams.get('MediaType')[:4]
    return storageparams


def getStorageDefinednr():
    val = ConfResource.objects.filter(compid__type='D', type__name='Storage')
    return val.count()


def updateStorageDefinednr(context):
    val = getStorageDefinednr()
    context.update({'storagenr': val})


def getStorageVolumesnr():
    return Media.objects.count()


def updateStorageVolumesnr(context):
    val = getStorageVolumesnr()
    context.update({'storagevolumesnr': val})


def updateStoragedetectdedup(context):
    ded = ConfParameter.objects.filter(name='.StorageDirDedupidx').count()
    val = detectdedup()
    context.update({'storagedetectdedup': (ded < 1) and val})
