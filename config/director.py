# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from libs.conf import *
from libs.client import extractclientparams
from libs.plat import getOStype
from libs.system import getdevsymlink
from .conflib import *
from .confinfo import *


def createBCDirector(compid, name, address, password):
    # create resource
    resid = createBCresDirector(compid, name)
    # add parameters
    addparameter(resid, 'DirPort', 9101)
    addparameter(resid, 'Address', address)
    # encrypt password
    encpass = getencpass(name, password)
    addparameterenc(resid, 'Password', encpass)


def createDIRCatalog(dircompid=None, dirname=None, dbname='bacula', dbuser='bacula', dbpassword=''):
    # create resource
    resid = createDIRresCatalog(dircompid)
    # add parameters
    addparameterstr(resid, 'dbname', dbname)
    addparameterstr(resid, 'dbuser', dbuser)
    addparameterstr(resid, 'dbaddress', 'localhost')
    if dirname is None:
        dirname = getDIRname()
    encpass = getencpass(dirname, dbpassword)
    addparameterenc(resid, 'dbpassword', encpass)


def createDIRMessages(dircompid, name, email='root@localhost', log='bacula.log', descr='', fatal=True):
    # create resource
    resid = createDIRresMessages(dircompid, name, descr)
    # add parameters
    addparameterstr(resid, 'MailCommand',
                    '/opt/bacula/bin/bsmtp -h localhost -f \\"(Inteos Backup) <%r>\\" -s \\"ibad: %t %e of %n %l\\" %r')
    # addparameterstr(resid,'OperatorCommand','/opt/bacula/bin/bsmtp -h localhost -f \"(Bacula) <%r>\" -s \"IBackup:
    # Intervention needed for %j\" %r')
    if fatal:
        addparameter(resid, 'Mail', email + ' = All, !Debug, !Skipped, !Restored')
    else:
        addparameter(resid, 'Mail', email + ' = All, !Fatal, !Debug, !Skipped, !Restored')
    # addparameter(resid,'Operator','root@localhost=All,!Debug,!Skipped')
    addparameter(resid, 'Catalog', 'All')
    addparameter(resid, 'Append', "/opt/bacula/log/" + log + " = All, !Debug, !Skipped")


def createDIRDirector(dircompid=None, name='ibadmin', descr=''):
    # create resource
    resid = createDIRresDirector(dircompid, name, descr)
    # add parameters
    addparameter(resid, 'MaximumConcurrentJobs', 50)
    addparameterstr(resid, 'Messages', 'Daemon')
    addparameterstr(resid, 'PidDirectory', '/opt/bacula/working')
    addparameterstr(resid, 'QueryFile', '/opt/bacula/scripts/query.sql')
    addparameterstr(resid, 'WorkingDirectory', '/opt/bacula/working')
    # TODO: może wymagane będą poniższe parametry:
    # MaximumReloadRequests = <number>
    # Statistics Retention = <time>
    # VerId = <string>
    # generate password
    password = randomstr()
    encpass = getencpass(name, password)
    addparameterenc(resid, 'Password', encpass)
    # bconsole config here because we have a generated password
    bconsoleid = createBCcomponent(name)
    createBCDirector(bconsoleid, name, 'localhost', password)


def createDIRClient(dircompid=None, dirname=None, name='ibadmin', password='ibadminpassword', address='localhost',
                    os='rhel', catalog='Catalog', descr='', internal=False, encpass=None, cluster=None, alias=None,
                    service=None):
    # create resource
    resid = createDIRresClient(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    addparameterstr(resid, 'Address', address)
    addparameterstr(resid, 'Catalog', catalog)
    if os == 'win32' or os == 'win64':
        maxjobs = 1
    else:
        maxjobs = 10
    addparameter(resid, 'MaximumConcurrentJobs', maxjobs)
    addparameterstr(resid, '.OS', os)
    addparameterstr(resid, 'AutoPrune', 'No')
    addparameterstr(resid, 'Enabled', 'Yes')
    if encpass is None:
        encpass = getencpass(dirname, password)
    addparameterenc(resid, 'Password', encpass)
    if internal:
        addparameterstr(resid, '.InternalClient', 'Yes')
    if cluster is not None:
        addparameterstr(resid, '.ClusterName', cluster)
    if alias is not None:
        addparameterstr(resid, '.Alias', alias)
    if service is not None:
        addparameterstr(resid, '.ClusterService', service)


def createDIRPool(dircompid=None, name='Default', disktype=False, retention=None, useduration=None, nextpool=None,
                  storage=None, descr='', cleaning=False):
    if dircompid is None:
        dircompid = getDIRcompid()
    # create resource
    resid = createDIRresPool(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    addparameter(resid, 'PoolType', 'Backup')
    addparameter(resid, 'AutoPrune', 'No')
    addparameter(resid, 'Recycle', 'Yes')
    addparameter(resid, 'VolumeRetention', retention or '2 weeks')
    if useduration is not None:
        addparameter(resid, 'VolumeUseDuration', useduration)
    if disktype:
        addparameterstr(resid, 'LabelFormat', 'DiskVol')
        addparameter(resid, 'ActionOnPurge', 'Truncate')
    if nextpool is not None:
        addparameterstr(resid, 'NextPool', nextpool)
    if storage is not None:
        addparameterstr(resid, 'Storage', storage)
    if cleaning or not disktype:
        addparameterstr(resid, 'CleaningPrefix', "CLN")


def createDIRStorage(dircompid=None, dirname=None, name='ibadmin', password='ibadminpassword', address='localhost',
                     device='ibadmin-File1', mediatype='File', descr='', internal=False, sdcomponent='ibadmin',
                     encpass=None, sddirdevice=None, sddirdedupidx=None, sddirtapeid=None):
    # create resource
    resid = createDIRresStorage(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    addparameterstr(resid, 'Address', address)
    addparameter(resid, 'SDPort', 9103)
    addparameterstr(resid, 'Device', device)
    addparameterstr(resid, 'MediaType', mediatype)
    # it is BEE only directive, I think?
    addparameter(resid, 'Autochanger', 'Yes')
    addparameter(resid, 'MaximumConcurrentJobs', 10)
    if encpass is None:
        encpass = getencpass(dirname, password)
    addparameterenc(resid, 'Password', encpass)
    if internal:
        addparameter(resid, '.InternalStorage', 'Yes')
    addparameter(resid, '.StorageComponent', sdcomponent)
    if sddirdevice is not None:
        addparameter(resid, '.StorageDirDevice', sddirdevice)
    if sddirdedupidx is not None:
        addparameter(resid, '.StorageDirDedupidx', sddirdedupidx)
    if sddirtapeid is not None:
        addparameter(resid, '.StorageDirTapeid', sddirtapeid)


def updateDIRdefaultStorage(dircompid=None, storname=None):
    if storname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    # get storage which is internal right now
    curintstorres = ConfResource.objects.filter(confparameter__name='.InternalStorage')
    curmediatype = ConfParameter.objects.get(resid=curintstorres, name='MediaType').value
    # delete current InternalStorage parameter
    query = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type__name='Storage', name='.InternalStorage')
    query.delete()
    res = ConfResource.objects.get(compid_id=dircompid, type__name='Storage', name=storname)
    newmediatype = ConfParameter.objects.get(resid=res, name='MediaType').value
    addparameter(res.resid, '.InternalStorage', 'Yes')
    updateparameter(dircompid, 'SYS-Backup-Catalog', 'Job', 'Storage', storname)
    cm = curmediatype[:4]
    if cm == 'Dedu':
        cm = 'File'
    nm = newmediatype[:4]
    if nm == 'Dedu':
        nm = 'File'
    if cm != nm:
        # media type has changed, update Default Pool
        dpresid = getresourceid(dircompid, 'Default', 'Pool')
        if nm == 'Tape':
            deleteparameter(dpresid, 'LabelFormat')
            deleteparameter(dpresid, 'ActionOnPurge')
            deleteparameter(dpresid, 'VolumeUseDuration')
            addparameterstr(dpresid, 'CleaningPrefix', 'CLN')
        else:
            addparameterstr(dpresid, 'LabelFormat', 'DiskVol')
            addparameter(dpresid, 'ActionOnPurge', 'Truncate')
            addparameter(dpresid, 'VolumeUseDuration', '1 day')
            deleteparameter(dpresid, 'CleaningPrefix')

