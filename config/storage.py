# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from .director import *
from libs.system import getdevsymlink
import os


def createSDStorage(sdcompid=None, name='ibadmin', address='localhost', dedupdir=None, dedupindx=None, descr=''):
    if sdcompid is None:
        return
    # create resource
    resid = createSDresStorage(sdcompid=sdcompid, name=name, descr=descr)
    # add parameters
    sdaddrsid = createSDsubresource(sdcompid=sdcompid, resid=resid, rtype=ResType.SDAddresses)
    addSDStorageAddress(sdcompid=sdcompid, resid=sdaddrsid, address=address)
    # static BEE parameters
    addparameterstr(resid, 'WorkingDirectory', '/opt/bacula/working')
    addparameterstr(resid, 'PidDirectory', '/opt/bacula/working')
    addparameterstr(resid, 'PluginDirectory', '/opt/bacula/plugins')
    addparameter(resid, 'MaximumConcurrentJobs', 11)
    # optional parameters for dedup
    if dedupdir is not None and dedupindx is not None:
        addparameterstr(resid, 'DedupDirectory', dedupdir)
        addparameterstr(resid, 'DedupIndexDirectory', dedupindx)


def addSDStorageAddress(sdcompid=None, resid=None, address='localhost'):
    if sdcompid is None:
        return
    if resid is None:
        resid = getresourceid(sdcompid, name='', restype=ResType.SDAddresses)
    # check if already defined
    isdef = ConfResource.objects.filter(sub=resid, type__name='IP', confparameter__value=address).count()
    if isdef == 0:
        # ok, not available, create
        ipresid = createSDsubresource(sdcompid=sdcompid, resid=resid, rtype=ResType.IP)
        addparameter(ipresid, 'Port', 9103)
        addparameter(ipresid, 'Addr', address)


def deleteSDStorageAddress(sdcompid=None, address='localhost'):
    if sdcompid is None:
        return
    sdaddrsid = getresourceid(sdcompid, name='', restype=ResType.SDAddresses)
    resquery = ConfResource.objects.filter(sub=sdaddrsid, type=ResType.IP, confparameter__value=address)
    resquery.delete()


def createSDDirector(sdcompid=None, dirname=None, name='ibadmin', password='ibadminpassword', descr=''):
    # create resource
    resid = createSDresDirector(sdcompid=sdcompid, dirname=dirname, descr=descr)
    # add parameters
    encpass = getencpass(name, password)
    addparameterenc(resid, 'Password', encpass)


def createSDMessages(sdcompid=None, dirname=None):
    # create resource
    resid = createSDresMessages(sdcompid=sdcompid, name='Standard', descr='Default Messages to Director')
    # add parameters
    addparameter(resid, 'Director', dirname + ' = All, !Debug, !Skipped, !Restored')


def createSDAutochanger(sdcompid=None, name='File1', changerdev='/dev/null', changercmd='', devices=None, descr=''):
    # check required data
    if sdcompid is None or devices is None:
        return
    # create resource
    resid = createSDresAutochanger(sdcompid=sdcompid, name=name, descr=descr)
    # add parameters
    addparameterstr(resid, 'ChangerCommand', changercmd)
    addparameterstr(resid, 'ChangerDevice', changerdev)
    for dev in devices:
        addparameterstr(resid, 'Device', dev['name'])


def createSDDevice(sdcompid=None, dtype='File', device=None):
    if sdcompid is None or device is None:
        return
    # create resource
    resid = createSDresDevice(sdcompid=sdcompid, name=device['name'])
    # add parameters
    addparameter(resid, 'AlwaysOpen', 'Yes')
    addparameterstr(resid, 'ArchiveDevice', device['archdir'])
    addparameter(resid, 'Autochanger', 'Yes')
    addparameter(resid, 'AutomaticMount', 'Yes')
    addparameter(resid, 'DeviceType', dtype)
    addparameter(resid, 'DriveIndex', device['devindex'])
    addparameterstr(resid, 'MediaType', device['mediatype'])
    if dtype == 'Tape':
        addparameter(resid, 'RandomAccess', 'No')
        addparameter(resid, 'RemovableMedia', 'Yes')
    else:
        addparameter(resid, 'RandomAccess', 'Yes')
        addparameter(resid, 'RemovableMedia', 'No')
        addparameter(resid, 'LabelMedia', 'Yes')
    addparameterstr(resid, 'SpoolDirectory', '/opt/bacula/working')
    addparameter(resid, 'MaximumConcurrentJobs', 1)


def createStorage(dircompid=None, dirname=None, storname='ibadmin', address='localhost', descr='', stortype='file',
                  archdir='/tmp', dedupdir=None, dedupidxdir=None, internal=False, tapelib=None):
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    if stortype == 'file':
        archdirn = os.path.abspath(archdir)
        return createStoragefile(dircompid=dircompid, dirname=dirname, storname=storname, address=address, descr=descr,
                                 archdir=archdirn, internal=internal)
    if stortype == 'dedup':
        dedupdirn = os.path.abspath(dedupdir)
        dedupidxdirn = os.path.abspath(dedupidxdir)
        return createStoragededup(dircompid=dircompid, dirname=dirname, storname=storname, address=address, descr=descr,
                                  dedupdir=dedupdirn, dedupidxdir=dedupidxdirn, internal=internal)
    if stortype == 'tape':
        return createStoragetape(dircompid=dircompid, dirname=dirname, storname=storname, address=address, descr=descr,
                                 tapelib=tapelib, internal=internal)
    return None


def createStoragefile(dircompid=None, dirname=None, storname='ibadmin', address='localhost', descr='', archdir='/tmp',
                      internal=False):
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    devtype = 'File'
    mediatype = devtype + getnextStorageid()
    dirstorname = storname + '-' + mediatype
    # generate password
    password = randomstr()
    # insert new Storage {} resource into Dir conf
    createDIRStorage(dircompid=dircompid, dirname=dirname, name=dirstorname, password=password, address=address,
                     descr=descr, device=mediatype, mediatype=mediatype, internal=internal, sdcomponent=storname,
                     sddirdevice=archdir)
    # create SD component
    sdcompid = createSDcomponent(name=storname)
    # insert new Director {} resource into SD conf
    createSDDirector(sdcompid=sdcompid, dirname=dirname, name=storname, password=password, descr=descr)
    # insert new Storage {} resource into SD conf
    createSDStorage(sdcompid=sdcompid, name=storname, descr=descr, address=address)
    # insert new Messages {} resource into SD conf
    createSDMessages(sdcompid=sdcompid, dirname=dirname)
    # create a list of archive devices
    devices = []
    for nr in range(0, 9):
        devices.append({
            'name': mediatype + 'Dev' + str(nr),
            'archdir': archdir,
            'devindex': nr,
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev='/dev/null', changercmd='', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype=devtype, device=dev)
    return dirstorname


def createStoragetape(dircompid=None, dirname=None, storname='ibadmin', address='localhost', descr='', tapelib=None,
                      internal=False):
    if tapelib is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    devtype = 'Tape'
    mediatype = devtype + getnextStorageid()
    dirstorname = storname + '-' + mediatype
    # generate password
    password = randomstr()
    sddirdevice = tapelib['Lib']['name'] + tapelib['Lib']['id']
    sddirtapeid = tapelib['Lib']['id']
    # insert new Storage {} resource into Dir conf
    createDIRStorage(dircompid=dircompid, dirname=dirname, name=dirstorname, password=password, address=address,
                     descr=descr, device=mediatype, mediatype=mediatype, internal=internal, sdcomponent=storname,
                     sddirdevice=sddirdevice, sddirtapeid=sddirtapeid)
    # create SD component
    sdcompid = createSDcomponent(name=storname)
    # insert new Director {} resource into SD conf
    createSDDirector(sdcompid=sdcompid, dirname=dirname, name=storname, password=password, descr=descr)
    # insert new Storage {} resource into SD conf
    createSDStorage(sdcompid=sdcompid, name=storname, descr=descr, address=address)
    # insert new Messages {} resource into SD conf
    createSDMessages(sdcompid=sdcompid, dirname=dirname)
    # create a list of archive devices
    devices = []
    for dev in tapelib['Devices']:
        devices.append({
            'name': mediatype + 'Dev' + str(dev['DriveIndex']),
            'archdir': getdevsymlink(dev['Tape']['dev']),
            'devindex': dev['DriveIndex'],
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev=getdevsymlink(tapelib['Lib']['dev']),
                        changercmd='/opt/bacula/scripts/mtx-changer %c %o %S %a %d', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype=devtype, device=dev)
    return dirstorname


def createStoragededup(dircompid=None, dirname=None, storname='ibadmin', address='localhost', descr='', dedupdir='/tmp',
                       dedupidxdir='/tmp', internal=False):
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    devtype = 'Dedup'
    mediatype = devtype + getnextStorageid()
    dirstorname = storname + '-' + mediatype
    # TODO: removed until we will know how to handle this
    # archdir = dedupdir + '/volumes'
    archdir = dedupdir
    # generate password
    password = randomstr()
    # insert new Storage {} resource into Dir conf
    createDIRStorage(dircompid=dircompid, dirname=dirname, name=dirstorname, password=password, address=address,
                     descr=descr, device=mediatype, mediatype=mediatype, internal=internal, sdcomponent=storname,
                     sddirdevice=archdir, sddirdedupidx=dedupidxdir)
    # create SD component
    sdcompid = createSDcomponent(name=storname)
    # insert new Director {} resource into SD conf
    createSDDirector(sdcompid=sdcompid, dirname=dirname, name=storname, password=password, descr=descr)
    # insert new Storage {} resource into SD conf
    createSDStorage(sdcompid=sdcompid, name=storname, descr=descr, address=address, dedupdir=dedupdir,
                    dedupindx=dedupidxdir)
    # insert new Messages {} resource into SD conf
    createSDMessages(sdcompid=sdcompid, dirname=dirname)
    # create a list of archive devices
    devices = []
    for nr in range(0, 9):
        devices.append({
            'name': mediatype + 'Dev' + str(nr),
            'archdir': archdir,
            'devindex': nr,
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev='/dev/null', changercmd='', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype=devtype, device=dev)
    return dirstorname


def extendStoragefile(dircompid=None, dirname=None, sdcompid=None, storname=None, descr='', sdcomponent=None,
                      archdir='/tmp', departments=None):
    if storname is None or (sdcomponent is None and sdcompid is None):
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    devtype = 'File'
    mediatype = devtype + getnextStorageid()
    archdirn = os.path.abspath(archdir)
    encpass = getSDStorageEncpass(sdcompid=sdcompid, name=sdcomponent)
    password = getdecpass(comp=sdcomponent, encpass=encpass)
    address = getDIRInternalStorageAddress()
    # insert new Storage {} resource into Dir conf
    createDIRStorage(dircompid=dircompid, dirname=dirname, name=storname, password=password, address=address,
                     descr=descr, device=mediatype, mediatype=mediatype, sdcomponent=sdcomponent, sddirdevice=archdirn,
                     departments=departments)
    # TODO: extend maximumconcurrentjobs for SD
    # create a list of archive devices
    devices = []
    for nr in range(0, 9):
        devices.append({
            'name': mediatype + 'Dev' + str(nr),
            'archdir': archdirn,
            'devindex': nr,
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev='/dev/null', changercmd='', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype=devtype, device=dev)


def extendStoragetape(dircompid=None, dirname=None, sdcompid=None, storname=None, descr='', sdcomponent=None,
                      tapelib=None):
    if storname is None or (sdcomponent is None and sdcompid is None) or tapelib is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    devtype = 'Tape'
    mediatype = devtype + getnextStorageid()
    encpass = getSDStorageEncpass(sdcompid=sdcompid, name=sdcomponent)
    password = getdecpass(comp=sdcomponent, encpass=encpass)
    address = getDIRInternalStorageAddress()
    sddirdevice = tapelib['Lib']['name'] + tapelib['Lib']['id']
    sddirtapeid = tapelib['Lib']['id']
    # insert new Storage {} resource into Dir conf
    createDIRStorage(dircompid=dircompid, dirname=dirname, name=storname, password=password, address=address,
                     descr=descr, device=mediatype, mediatype=mediatype, sdcomponent=sdcomponent,
                     sddirdevice=sddirdevice, sddirtapeid=sddirtapeid)
    # TODO: extend maximumconcurrentjobs for SD
    # create a list of archive devices
    devices = []
    for dev in tapelib['Devices']:
        devices.append({
            'name': mediatype + 'Dev' + str(dev['DriveIndex']),
            'archdir': getdevsymlink(dev['Tape']['dev']),
            'devindex': dev['DriveIndex'],
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev=getdevsymlink(tapelib['Lib']['dev']),
                        changercmd='/opt/bacula/scripts/mtx-changer %c %o %S %a %d', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype=devtype, device=dev)


def extendStoragededup(dircompid=None, dirname=None, sdcompid=None, storname=None, descr='', sdcomponent=None,
                       dedupdir='/tmp', dedupidxdir='/tmp', departments=None):
    if storname is None or (sdcomponent is None and sdcompid is None):
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    devtype = 'Dedup'
    mediatype = devtype + getnextStorageid()
    dedupdirn = os.path.abspath(dedupdir)
    dedupidxdirn = os.path.abspath(dedupidxdir)
    encpass = getSDStorageEncpass(sdcompid=sdcompid, name=sdcomponent)
    password = getdecpass(comp=sdcomponent, encpass=encpass)
    address = getDIRInternalStorageAddress()
    # insert new Storage {} resource into Dir conf
    createDIRStorage(dircompid=dircompid, dirname=dirname, name=storname, password=password, address=address,
                     descr=descr, device=mediatype, mediatype=mediatype, sdcomponent=sdcomponent, sddirdevice=dedupdirn,
                     sddirdedupidx=dedupidxdirn, departments=departments)
    # TODO: extend maximumconcurrentjobs for SD
    # create a list of archive devices
    devices = []
    for nr in range(0, 9):
        devices.append({
            'name': mediatype + 'Dev' + str(nr),
            'archdir': dedupdirn,
            'devindex': nr,
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev='/dev/null', changercmd='', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype=devtype, device=dev)
    resid = getresourceid(sdcompid, name=sdcomponent, restype=ResType.Storage)
    addparameterstr(resid, ParamType.DedupDirectory, dedupdirn)
    addparameterstr(resid, ParamType.DedupIndexDirectory, dedupidxdirn)


def createStorageAlias(request, dircompid=None, storname=None, descr='', storage=None, address='localhost',
                       department=None):
    if storname is None or storage is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    storageid = getresourceid(dircompid, name=storage, restype=ResType.Storage)
    sdcomponent = getparameter(storageid, '.StorageComponent')
    sdcompid = getSDcompid(sdcomponent)
    # insert new Storage {} resource into Dir conf
    resid = createDIRresStorage(dircompid=dircompid, name=storname, descr=descr)
    # insert parameters
    addparameter(resid, ParamType.ibadAlias, storage)
    addparameterstr(resid, ParamType.Address, address)
    if department is not None and department not in ('', ' ', '#'):
        addparameterstr(resid, ParamType.ibadDepartment, department)
    # copy other parameters
    storparams = ConfParameter.objects.filter(resid=storageid).exclude(name=ParamType.Address)\
        .exclude(name='.InternalStorage').exclude(name=ParamType.ibadDepartment)
    for param in storparams:
        if param.name.startswith('.StorageDir'):
            continue
        np = ConfParameter(resid_id=resid, name=param.name, value=param.value, str=param.str, enc=param.enc)
        np.save()
    # add SD address if required
    addSDStorageAddress(sdcompid=sdcompid, address=address)


def updateStorageTapelib(dircompid=None, sdcompid=None, sdcomponent=None, storname=None, tapelib=None):
    if storname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if sdcomponent is None:
        data = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type=ResType.Storage, resid__name=storname,
                                         name='.StorageComponent')
        sdcomponent = data.value
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    mediatype = getDIRStorageMediatype(name=storname)
    devtype = 'Tape'
    # delete Autochanger and Devices
    deleteSDAutochanger(sdcompid=sdcompid, autoname=mediatype)
    deleteSDDevices(sdcompid=sdcompid, mediatype=mediatype)
    # create a list of archive devices
    devices = []
    for dev in tapelib['Devices']:
        devices.append({
            'name': mediatype + 'Dev' + str(dev['DriveIndex']),
            'archdir': getdevsymlink(dev['Tape']['dev']),
            'devindex': dev['DriveIndex'],
            'mediatype': mediatype,
        })
    # create new Autochanger {} resource in SD conf
    createSDAutochanger(sdcompid=sdcompid, name=mediatype, changerdev=getdevsymlink(tapelib['Lib']['dev']),
                        changercmd='/opt/bacula/scripts/mtx-changer %c %o %S %a %d', devices=devices)
    for dev in devices:
        createSDDevice(sdcompid=sdcompid, dtype=devtype, device=dev)


def updateStorageArchdir(request, dircompid=None, sdcompid=None, sdcomponent=None, storname=None, archdir='/tmp'):
    if storname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    if sdcomponent is None:
        data = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type=ResType.Storage, resid__name=storname,
                                         name='.StorageComponent')
        sdcomponent = data.value
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    archdirn = os.path.abspath(archdir)
    mediatype = getDIRStorageMediatype(name=storname)
    res = ConfResource.objects.filter(compid_id=sdcompid, type=ResType.Device, confparameter__name=ParamType.MediaType,
                                      confparameter__value=mediatype)
    params = ConfParameter.objects.filter(resid__in=res, name=ParamType.ArchiveDevice)
    params.update(value=archdirn)
    updateparameter(dircompid, storname, ResType.Storage, '.StorageDirDevice', archdirn)


def updateStorageDedupdir(dircompid=None, sdcompid=None, sdcomponent=None, storname=None, dedupdir='/tmp'):
    if storname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if sdcomponent is None:
        data = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type=ResType.Storage, resid__name=storname,
                                         name='.StorageComponent')
        sdcomponent = data.value
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    dedupdirn = os.path.abspath(dedupdir)
    mediatype = getDIRStorageMediatype(name=storname)
    res = ConfResource.objects.filter(compid_id=sdcompid, type=ResType.Device, confparameter__name=ParamType.MediaType,
                                      confparameter__value=mediatype)
    params = ConfParameter.objects.filter(resid__in=res, name=ParamType.ArchiveDevice)
    params.update(value=dedupdirn)
    updateparameter(sdcompid, sdcomponent, ResType.Storage, 'DedupDirectory', dedupdirn)
    updateparameter(dircompid, storname, ResType.Storage, '.StorageDirDevice', dedupdirn)


def updateStorageDedupidxdir(dircompid=None, sdcompid=None, sdcomponent=None, storname=None, dedupidxdir='/tmp'):
    if storname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if sdcomponent is None:
        data = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type=ResType.Storage, resid__name=storname,
                                         name='.StorageComponent')
        sdcomponent = data.value
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    dedupidxdirn = os.path.abspath(dedupidxdir)
    updateparameter(sdcompid, sdcomponent, ResType.Storage, ParamType.DedupIndexDirectory, dedupidxdirn)
    updateparameter(dircompid, storname, ResType.Storage, '.StorageDirDedupidx', dedupidxdirn)


def updateSDAddresses(sdcompid=None, address='localhost'):
    addSDStorageAddress(sdcompid=sdcompid, address=address)


def updateStorageAddress(dircompid=None, sdcompid=None, sdcomponent=None, address='localhost'):
    if dircompid is None:
        dircompid = getDIRcompid()
    params = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__type=ResType.Storage,
                                          name=ParamType.Address)
    params.update(value=address)
    if sdcomponent is None:
        res = ConfResource.objects.get(compid_id=dircompid, type__name='Storage',
                                       confparameter__name='.InternalStorage')
        data = ConfParameter.objects.get(resid=res, name='.StorageComponent')
        sdcomponent = data.value
    if sdcompid is None:
        sdcompid = getSDcompid(name=sdcomponent)
    # Yes, SDComponent:name and SDComponent:Storage:name are always the same
    # TODO: update to match new sdaddresses schema
    updateSDAddresses(sdcompid=sdcompid, address=address)


def updateStorageAliasAddress(dircompid=None, storname=None, address='localhost'):
    if dircompid is None:
        dircompid = getDIRcompid()
    param = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__type__name='Storage', resid__name=storname,
                                         name='Address')
    param.update(value=address)
    sdcomponent = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type__name='Storage',
                                            resid__name=storname, name='.StorageComponent')
    sdcompid = getSDcompid(name=sdcomponent.value)
    updateSDAddresses(sdcompid=sdcompid, address=address)


def deleteSDAutochanger(sdcompid=None, sdname=None, autoname=None):
    if sdname is None and sdcompid is None:
        return None
    if autoname is None:
        return None
    if sdcompid is None:
        sdcompid = getSDcompid(sdname)
    resid = getresourceid(compid=sdcompid, name=autoname, restype=ResType.Autochanger)
    # delete Autochanger resource and parameters
    deleteresource(resid)


def deleteSDDevices(sdcompid=None, sdname=None, mediatype=None):
    if sdname is None and sdcompid is None:
        return None
    if mediatype is None:
        return None
    if sdcompid is None:
        sdcompid = getSDcompid(sdname)
    devices = ConfResource.objects.filter(compid_id=sdcompid, type=ResType.Device,
                                          confparameter__name=ParamType.MediaType,
                                          confparameter__value=mediatype)
    for dev in devices:
        resid = dev.resid
        # delete Autochanger resource and parameters
        deleteresource(resid)
