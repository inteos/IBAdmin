# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.db.models import Max, Q
from .conflib import *
from storages.models import Storage


def getDIRdescr(request=None, dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid(request)
    dirres = ConfResource.objects.get(compid_id=dircompid, type=ResType.Director)
    return dirres.description


def getDIRCatalog(request=None):
    compid = getDIRcompid(request)
    resource = ConfResource.objects.get(compid_id=compid, type=ResType.Catalog)
    return resource.name


def getFDcompid(name):
    try:
        component = ConfComponent.objects.get(type='F', name=name)
    except ObjectDoesNotExist:
        return None
    return component.compid


def getSDcompid(name):
    try:
        component = ConfComponent.objects.get(type='S', name=name)
    except ObjectDoesNotExist:
        return None
    return component.compid


def getnextStorageid():
    out = Storage.objects.aggregate(maxstorid=Max('storageid'))
    storageid = out['maxstorid']
    if storageid is None:
        # first storage defined
        return '1'
    return str(storageid + 1)


def getDIRPoolid(request=None, dircompid=None, name='Default'):
    if dircompid is None:
        dircompid = getDIRcompid(request)
    return getresourceid(compid=dircompid, name=name, restype=ResType.Pool)


def getDIRJobparams(request, dircompid=None, jobres=None):
    if jobres is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    jdname = getparameter(jobres.resid, 'JobDefs')
    jdid = getresourceid(dircompid, name=jdname, restype=ResType.JobDefs)
    jobtype = getparameter(jdid, 'Type')
    jobparams = {'Name': jobres.name, 'Descr': jobres.description, 'Type': jobtype,
                 'Params': getparameters(jobres.resid)}
    return jobparams


def getDIRJobType(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    jd = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__name=name, resid__type=ResType.Job,
                                      name='JobDefs').first()
    if jd is not None:
        return jd.value
    return None


def getDIRJobDefs(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    jd = ConfResource.objects.filter(compid_id=dircompid, name=name, type=ResType.JobDefs).first()
    if jd is not None:
        return jd
    return None


def getDIRClientparams(clientres=None):
    if clientres is None:
        return None
    clientparams = {'Name': clientres.name, 'Descr': clientres.description, 'Params': getparameters(clientres.resid)}
    return clientparams


def getDIRClientsClusterEncpass(cluster=None):
    if cluster is None:
        return None
    resid = ConfParameter.objects.filter(name=ParamType.ibadClusterName, value=cluster)[0].resid_id
    encpass = ConfParameter.objects.get(resid_id=resid, name=ParamType.Password).value
    return encpass


def getDIRStorageparams(storageres):
    if storageres is None:
        return None
    storageparams = {'Name': storageres.name, 'Descr': storageres.description,
                     'Params': getparameters(storageres.resid)}
    return storageparams


def getDIRStorageList(request, dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid(request)
    # list of the all Storages available
    storageres = ConfResource.objects.filter(compid_id=dircompid, type=ResType.Storage).order_by('name')
    storagelist = []
    for sr in storageres:
        storageparams = getDIRStorageparams(sr)
        storagelist.append(storageparams)
    return storagelist


def getDIRStorageinfo(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    try:
        storageres = ConfResource.objects.get(compid_id=dircompid, type=ResType.Storage, name=name)
    except:
        return None
    return getDIRStorageparams(storageres)


def getSDDevicesList(component=None, storage=None):
    """
    
    :param component: this is a storage SD name (component)
    :param storage: this is a name of the Autochanger device from DIR->Storge->Device
    :return: 
    """
    if storage is None or component is None:
        return None
    compid = getSDcompid(component)
    devicenamelist = ConfParameter.objects.filter(resid__compid=compid, resid__type=ResType.Autochanger,
                                                  resid__name=storage,
                                                  name=ParamType.Device).order_by('value').all().values()
    if devicenamelist.count() == 0:
        return []
    devicelist = []
    for dev in devicenamelist:
        devicelist.append(dev['value'])
    return devicelist


def getSDDevicesListex(component=None, storage=None):
    """

    :param component: this is a storage SD name (component)
    :param storage: this is a name of the Autochanger device from DIR->Storge->Device
    :return:
    """
    if storage is None or component is None:
        return None
    compid = getSDcompid(component)
    devicenamelist = ConfParameter.objects.filter(resid__compid=compid, resid__type=ResType.Autochanger,
                                                  resid__name=storage, name=ParamType.Device).order_by('value').all()
    if devicenamelist.count() == 0:
        return []
    devicelist = []
    for dev in devicenamelist:
        drvindx = ConfParameter.objects.get(resid__name=dev.value, name='DriveIndex').value
        devicelist.append({'name': dev.value, 'driveindex': drvindx})
    return devicelist


def getDIRStorageTapeids(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    return ConfParameter.objects.filter(resid__compid_id=dircompid, resid__type=ResType.Storage,
                                        name='.StorageDirTapeid').values_list('value', flat=True)


def getDIRFSparams(dircompid=None, name=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    if name is None:
        return None
    resid = getresourceid(compid=dircompid, name=name, restype=ResType.Fileset)
    includeid = getsubresourceid(resid=resid, restype=ResType.Include)
    incparams = getparameters(includeid)
    optionid = getsubresourceid(resid=includeid, restype=ResType.Options)
    options = getparameters(optionid)
    excludeid = getsubresourceid(resid=resid, restype=ResType.Exclude)
    exclparams = getparameters(excludeid)
    return incparams, exclparams, options


def getDIRFSoptions(dircompid=None, name=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    if name is None:
        return None
    resid = getresourceid(compid=dircompid, name=name, restype=ResType.Fileset)
    includeid = getsubresourceid(resid=resid, restype=ResType.Include)
    optionid = getsubresourceid(resid=includeid, restype=ResType.Options)
    options = getparameters(optionid)
    return options


def getDefaultStorage(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    # TODO: rewrite to single query
    storages = ConfResource.objects.filter(compid_id=dircompid, type=ResType.Storage).all()
    stor = ConfParameter.objects.get(resid__in=storages, name='.InternalStorage')
    return stor.resid.name


def getDIRClientEncpass(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    encpass = ConfParameter.objects.get(resid__compid_id=dircompid, resid__name=name, resid__type=ResType.Client,
                                        name='Password')
    return encpass.value


def getDIRStorageEncpass(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    encpass = ConfParameter.objects.get(resid__compid_id=dircompid, resid__name=name, resid__type__name='Storage',
                                        name='Password')
    return encpass.value


def getSDStorageEncpass(sdcompid=None, name=None):
    if name is None:
        return None
    if sdcompid is None:
        sdcompid = getSDcompid(name=name)
    encpass = ConfParameter.objects.get(resid__compid_id=sdcompid, resid__type__name='Director', name='Password')
    return encpass.value


def getDIRClientAddress(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    address = ConfParameter.objects.get(resid__compid_id=dircompid, resid__name=name, resid__type__name='Client',
                                        name='Address')
    return address.value


def getDIRStorageAddress(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    address = ConfParameter.objects.get(resid__compid_id=dircompid, resid__name=name, resid__type__name='Storage',
                                        name='Address')
    return address.value


def getDIRInternalStorageAddress(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    resid = ConfResource.objects.get(compid_id=dircompid, confparameter__name='.InternalStorage')
    address = ConfParameter.objects.get(resid=resid, resid__type__name='Storage', name='Address')
    return address.value


def getDIRStorageMediatype(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    address = ConfParameter.objects.get(resid__compid_id=dircompid, resid__name=name, resid__type__name='Storage',
                                        name='MediaType')
    return address.value


def getSDStorageAddress(sdcompid=None, sdname=None):
    if sdname is None and sdcompid is None:
        return None
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdname)
    address = ConfParameter.objects.get(resid__compid_id=sdcompid, resid__type__name='Storage', name='.SDAddress')
    return address.value


def getFDClientAddress(fdcompid=None, name=None):
    if name is None:
        return None
    if fdcompid is None:
        fdcompid = getFDcompid(name=name)
    address = ConfParameter.objects.get(resid__compid_id=fdcompid, resid__name=name, resid__type=ResType.FileDaemon,
                                        name='FDAddress')
    return address.value


def getDIRClientOS(request, dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    os = ConfParameter.objects.get(resid__compid_id=dircompid, resid__name=name, resid__type=ResType.Client,
                                   name=ParamType.ibadOS)
    return os.value


def getClientDefinedJobs(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    query = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__type=ResType.Job, name=ParamType.Client,
                                         value=name)
    jobs = [t.resid.name for t in query]
    return jobs


def getDIRClusterClientname(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    node = ConfParameter.objects.filter(resid__compid_id=dircompid, name=ParamType.ibadClusterName, value=name).first()
    if node is None:
        return None
    return node.resid.name


def getDIRadminemail(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    param = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type=ResType.Messages, name=ParamType.Mail,
                                      resid__name='Standard')
    email = param.value.split('=')[0].rstrip()
    return email


def getStorageisDedup(storname=None):
    if storname is None:
        return False
    return ConfParameter.objects.filter(resid__name=storname, name=ParamType.MediaType,
                                        value__contains='Dedup').count() > 0


def getDIRStorageType(dircompid=None, storname=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    if storname is not None:
        mtype = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__name=storname,
                                             resid__type=ResType.Storage, name=ParamType.MediaType)
        if len(mtype) > 0:
            if mtype[0].value.startswith('Tape'):
                return 'tape'
    return 'disk'


def getDIRJobStorage(dircompid=None, name=None):
    if name is not None:
        if dircompid is None:
            dircompid = getDIRcompid()
        storname = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__name=name, resid__type__name='Job',
                                                name='Storage')
        if len(storname) > 0:
            return storname[0].value;
    return None
