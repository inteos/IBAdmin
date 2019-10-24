# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from libs.conf import *
from .confinfo import *
from libs.user import *


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


def createDIRMessages(dircompid, name, email=None, log='bacula.log', descr='', fatal=True):
    # create resource
    resid = createDIRresMessages(dircompid, name, descr)
    # add parameters
    if email is not None:
        addparameterstr(resid, 'MailCommand',
                        '/opt/bacula/bin/bsmtp -h localhost -f \\"(Inteos Backup) '
                        '<%r>\\" -s \\"ibad: %t %e of %n %l\\" %r')
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
    addparameter(resid, 'MaximumReloadRequests', 6400)
    addparameterstr(resid, 'Messages', 'Daemon')
    addparameterstr(resid, 'PidDirectory', '/opt/bacula/working')
    addparameterstr(resid, 'QueryFile', '/opt/bacula/scripts/query.sql')
    addparameterstr(resid, 'WorkingDirectory', '/opt/bacula/working')
    # TODO: może wymagane będą poniższe parametry:
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
                    service=None, vcenter=None, department=None):
    # create resource
    resid = createDIRresClient(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    addparameterstr(resid, ParamType.Address, address)
    addparameterstr(resid, ParamType.Catalog, catalog)
    if os == 'win32' or os == 'win64':
        maxjobs = 1
    else:
        maxjobs = 10
    addparameter(resid, 'MaximumConcurrentJobs', maxjobs)
    addparameterstr(resid, ParamType.ibadOS, os)
    addparameterstr(resid, 'AutoPrune', 'No')
    addparameterstr(resid, ParamType.Enabled, 'Yes')
    if encpass is None:
        encpass = getencpass(dirname, password)
    addparameterenc(resid, 'Password', encpass)
    if internal:
        addparameterstr(resid, '.InternalClient', 'Yes')
    if cluster is not None:
        addparameterstr(resid, ParamType.ibadClusterName, cluster)
    if alias is not None:
        addparameterstr(resid, ParamType.ibadAlias, alias)
    if service is not None:
        addparameterstr(resid, ParamType.ibadClusterService, service)
    if vcenter is not None:
        addparameter(resid, ParamType.ibadvCenterName, vcenter)
    if department is not None and department not in ('', ' ', '#'):
        addparameterstr(resid, ParamType.ibadDepartment, department)


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
                     encpass=None, sddirdevice=None, sddirdedupidx=None, sddirtapeid=None, departments=None):
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
    if departments is not None:
        if type(departments) is list:
            # multiple departments to add
            for d in departments:
                addparameter(resid, '.Department', d)
        else:
            addparameter(resid, '.Department', departments)


def updateDIRdefaultStorage(dircompid=None, storname=None):
    if storname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    # get storage which is internal right now
    curintstorres = ConfResource.objects.filter(confparameter__name='.InternalStorage')
    curmediatype = ConfParameter.objects.get(resid=curintstorres, name=ParamType.MediaType).value
    # delete current InternalStorage parameter
    query = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type=ResType.Storage, name='.InternalStorage')
    query.delete()
    res = ConfResource.objects.get(compid_id=dircompid, type=ResType.Storage, name=storname)
    newmediatype = ConfParameter.objects.get(resid=res, name=ParamType.MediaType).value
    addparameter(res.resid, '.InternalStorage', ParamValue.Yes)
    updateparameter(dircompid, 'SYS-Backup-Catalog', ResType.Job, ParamType.Storage, storname)
    cm = curmediatype[:4]
    if cm == 'Dedu':
        cm = 'File'
    nm = newmediatype[:4]
    if nm == 'Dedu':
        nm = 'File'
    if cm != nm:
        # media type has changed, update Default Pool
        dpresid = getresourceid(dircompid, name='Default', restype=ResType.Pool)
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


def createDIRFileSetFile(dircompid=None, name='fs-default', vss=False, dedup=False, include=None, exclude=None,
                         descr=''):
    # create resource
    resid = createDIRresFileSet(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    if vss:
        addparameterstr(resid, 'EnableVss', 'Yes')
    # Include {} subresource
    includeid = createDIRresFSInclude(dircompid, resid, dedup=dedup)
    createFSIncludeFile(resid=includeid, include=include)
    # Exclude {} subresource
    excludeid = createDIRresFSExclude(dircompid, resid)
    createFSExclude(excludeid, exclude)


def createDIRFileSetPlugin(dircompid=None, name='fs-default', include=None, dedup=False, descr=''):
    # create resource
    resid = createDIRresFileSet(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    # Include {} subresource
    includeid = createDIRresFSInclude(dircompid, resid, dedup=dedup)
    createFSIncludePlugin(includeid, include)


def createDIRJob(dircompid=None, name='SYS-Default', jd='jd-backup-files', descr='', client=None, pool=None,
                 storage=None, fileset=None, schedule=None, level=None, maxfullinterval=None, internal=False,
                 scheduleparam=None, scheduletime=None, scheduleweek=None, schedulemonth=None,
                 allobjs=None, objsinclude=None, objsexclude=None, abortonerror=None, mcj=None):
    # TODO: change all parameters to list of parameters
    # create resource
    resid = createDIRresJob(dircompid=dircompid, name=name, descr=descr)
    # add parameters
    addparameterstr(resid, 'JobDefs', jd)
    if level is not None:
        addparameterstr(resid, 'Level', getlevelname(level))
    if client is not None:
        addparameterstr(resid, 'Client', client)
    if storage is not None:
        addparameterstr(resid, 'Storage', storage)
    if pool is not None:
        addparameterstr(resid, 'Pool', pool)
    if fileset is not None:
        addparameterstr(resid, 'FileSet', fileset)
    if schedule is not None:
        addparameterstr(resid, 'Schedule', schedule)
    if scheduleparam is not None:
        addparameter(resid, '.Scheduleparam', scheduleparam)
    if scheduletime is not None:
        addparameter(resid, '.Scheduletime', scheduletime)
    if scheduleweek is not None:
        addparameter(resid, '.Scheduleweek', scheduleweek)
    if schedulemonth is not None:
        addparameter(resid, '.Schedulemonth', schedulemonth)
    if maxfullinterval is not None:
        addparameter(resid, 'MaxFullInterval', maxfullinterval)
    if mcj is not None:
        addparameter(resid, 'MaximumConcurrentJobs', mcj)
    if internal:
        addparameter(resid, '.InternalJob', 'Yes')
    if allobjs is not None:
        addparameter(resid, '.Allobjs', allobjs)
    if objsinclude is not None:
        addparameter(resid, '.Objsinclude', objsinclude)
    if objsexclude is not None:
        addparameter(resid, '.Objsexclude', objsexclude)
    if abortonerror is not None:
        addparameter(resid, '.AbortOnError', abortonerror)
    addparameter(resid, 'Enabled', 'Yes')


def createDIRSchDay(resid=None, params=None):
    if resid is None or params is None:
        return
    level = getlevelname(params['level'])
    timestr = number2time(params['time'], 0)
    sch = level + ' at ' + timestr
    addparameter(resid, 'Run', sch)


def createDIRSchHours(resid=None, params=None):
    if resid is None or params is None:
        return
    cycle = params['backuprepeat']
    if cycle == 'r24':
        # hack when createDIRSchDay was not fired directly
        return createDIRSchDay(resid, params)
    level = getlevelname(params['level'])
    times = params['time']
    if cycle == 'r1':
        # every hour
        addparameter(resid, 'Run', level + ' hourly at ' + number2time(times, 0))
        return
    if cycle == 'r2':
        # every 2H, so 12 entries
        for h in range(0, 12):
            sch = level + ' at ' + number2time(times, h * 2)
            addparameter(resid, 'Run', sch)
        return
    if cycle == 'r3':
        # every 3H, so 8 entries
        for h in range(0, 8):
            sch = level + ' at ' + number2time(times, h * 3)
            addparameter(resid, 'Run', sch)
        return
    if cycle == 'r4':
        # every 4H, so 6 entries
        for h in range(0, 6):
            sch = level + ' at ' + number2time(times, h * 4)
            addparameter(resid, 'Run', sch)
        return
    if cycle == 'r6':
        # every 6H, so 4 entries
        for h in range(0, 4):
            sch = level + ' at ' + number2time(times, h * 6)
            addparameter(resid, 'Run', sch)
        return
    if cycle == 'r8':
        # every 8H, so 3 entries
        for h in range(0, 3):
            sch = level + ' at ' + number2time(times, h * 8)
            addparameter(resid, 'Run', sch)
        return
    if cycle == 'r12':
        # every 12H, so 2 entries
        for h in range(0, 2):
            sch = level + ' at ' + number2time(times, h * 12)
            addparameter(resid, 'Run', sch)
        return


def createDIRSchWeek(resid=None, params=None):
    """ 'scheduleweek': u'off:off:off:off:off:off:off:off', """
    # get required data
    SCHWEEKDAYS = (
        'mon',
        'tue',
        'wed',
        'thu',
        'fri',
        'sat',
        'sun',
    )
    dlist = params['scheduleweek'].split(':')
    time = params['time']
    # insert parameters
    if dlist[-1] != 'off':
        # everylevel
        level = getlevelname(dlist[-1])
        sch = level + " at " + params['time']
        addparameter(resid, 'Run', sch)
    else:
        for i, lvl in enumerate(dlist[:-1]):
            if lvl != 'off':
                level = getlevelname(lvl)
                sch = level + " " + SCHWEEKDAYS[i] + " at " + time
                addparameter(resid, 'Run', sch)


def createDIRSchMonth(resid=None, params=None):
    """ 'schedulemonth': u'off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off'
                          ':off:off:off:off:off:off:off:off:off' """
    # insert parameters
    dlist = params['schedulemonth'].split(':')
    time = params['time']
    if dlist[-1] != 'off':
        # everylevel
        level = getlevelname(dlist[-1])
        sch = level + " at " + time
        addparameter(resid, 'Run', sch)
    else:
        for i, lvl in enumerate(dlist[:-1]):
            if lvl != 'off':
                level = getlevelname(lvl)
                sch = level + " on " + str(i + 1) + " at " + time
                addparameter(resid, 'Run', sch)


def createDIRSchedule(dircompid=None, name='sch-default', cycle='Hours', params=None, descr=''):
    """
    Creates a full schedule based on supplied parameters. When cycle is unknown (or None) the a routine has no effect.
    This means it creates a schedule resource but with no Run schedule parameters.
    :param dircompid: director component id
    :param name: name of the schedule
    :param cycle: defined schedule cycle, allowed values: Hours, Day, Week, Month
    :param params: schedule parameters as dict, i.e. 'level', 'time', 'scheduleweek', 'schedulemonth', 'backuprepeat'
    :param descr: description of the resource
    :return: none
    """
    # create resource
    resid = createDIRresSchedule(dircompid=dircompid, name=name, descr=descr)
    # add parameters based on cycle
    if cycle == 'Hours':
        # c1 - cycle during Day, every xx hours
        createDIRSchHours(resid, params)
        return
    if cycle == 'Day':
        # used only for single day schedule
        createDIRSchDay(resid, params)
        return
    if cycle == 'Week':
        # c2 - cycle during Week
        createDIRSchWeek(resid, params)
        return
    if cycle == 'Month':
        # c3 - cycle during Month
        createDIRSchMonth(resid, params)
        return


def deleteDIRClient(dircompid=None, name=None, client=None):
    if name is None and client is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if client is not None:
        resid = client.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, restype=ResType.Client)
    # delete Client resource and parameters
    deleteresource(resid)


def deleteDIRFileSet(dircompid=None, fsname=None):
    if fsname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    resid = getresourceid(compid=dircompid, name=fsname, restype=ResType.Fileset)
    # delete options subresource of include subresource
    includeid = getsubresourceid(resid=resid, restype=ResType.Include)
    deletesubresource(includeid, 'Options')
    deletesubresource(resid, 'Include')
    # delete exclude subresource
    deletesubresource(resid, 'Exclude')
    # delete fileset resource
    deleteresource(resid)


def deleteDIRJob(dircompid=None, name=None, job=None):
    if name is None and job is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if job is not None:
        name = job.name
        resid = job.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, restype=ResType.Job)
    # delete FileSet
    fsname = 'fs-' + name
    deleteDIRFileSet(dircompid=dircompid, fsname=fsname)
    # delete Schedule
    schname = 'sch-' + name
    deleteDIRSchedule(dircompid=dircompid, schname=schname)
    # delete Job resource and parameters
    deleteresource(resid)


def deleteDIRSchedule(dircompid=None, schname=None):
    if schname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    resid = getresourceid(compid=dircompid, name=schname, restype=ResType.Schedule)
    deleteresource(resid)


def disableDIRJob(dircompid=None, name=None, job=None):
    if name is None and job is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if job is not None:
        resid = job.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, restype=ResType.Job)
    # change Enabed parameter to No
    updateparameterresid(resid=resid, name='Enabled', value='No')
    addparameter(resid=resid, name='.Disabledfordelete', value='Yes')


def updateDIREnabledClient(dircompid=None, name=None, client=None, enabled=ParamValue.Yes):
    if name is None and client is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if client is not None:
        resid = client.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, restype=ResType.Client)
    if getparameter(resid=resid, name=ParamType.Enabled) is not None:
        # update existing
        updateparameterresid(resid=resid, name=ParamType.Enabled, value=enabled)
    else:
        addparameter(resid=resid, name=ParamType.Enabled, value=enabled)


def disableDIRClient(dircompid=None, name=None, client=None):
    if name is None and client is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if client is not None:
        resid = client.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, restype=ResType.Client)
    addparameter(resid=resid, name='.Disabledfordelete', value=ParamValue.Yes)
    updateDIREnabledClient(dircompid=dircompid, name=name, client=client, enabled=ParamValue.No)


def updateDIRadminemail(dircompid=None, dirname=None, email=''):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    emailstr = email + ' = All, !Debug, !Skipped, !Restored'
    updateparameter(dircompid, 'Standard', ResType.Messages, ParamType.Mail, emailstr)
    emailstr = email + ' = All, !Fatal, !Debug, !Skipped, !Restored'
    updateparameter(dircompid, 'Daemon', ResType.Messages, ParamType.Mail, emailstr)


def updateDIRClientAddress(dircompid=None, name=None, address='localhost'):
    if name is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    updateparameter(dircompid, name, ResType.Client, ParamType.Address, address)


def updateDIRJobDescr(dircompid=None, name=None, descr=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    updateresdescription(dircompid, name, 'Job', descr)


def updateDIRDescr(dircompid=None, dirname=None, descr=''):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    updateresdescription(dircompid, dirname, 'Director', descr)


def updateDIRClientDescr(dircompid=None, name='ibadmin', descr=''):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    updateresdescription(dircompid, name, 'Client', descr)


def updateDIRStorageDescr(request, dircompid=None, name=None, descr=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    updateresdescription(dircompid, name, 'Storage', descr)


def updateDirClientVMware(dircompid=None, client=None, clientres=None, vcenter=None, department=None):
    if (client is None and clientres is None) or vcenter is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    if clientres is None:
        clientres = ConfResource.objects.filter(compid=dircompid, name=client, type__name='Client')
    param = ConfParameter.objects.filter(resid=clientres, name='.vCenterName')
    if len(param) > 0:
        vcenterparam = param[0]
        vcenterparam.value = vcenter
    else:
        vcenterparam = ConfParameter(resid=clientres, name='.vCenterName', value=vcenter)
    vcenterparam.save()
    param = ConfParameter.objects.filter(resid=clientres, name='.OS')
    if len(param) > 0:
        clientos = param[0]
        clientos.value = 'vmware'
    else:
        clientos = ConfParameter(resid=client, name='.OS', value='vmware')
    clientos.save()
    param = ConfParameter.objects.filter(resid=clientres, name='.Department')
    if department is not None and department not in ['', ' ', '#']:
        if len(param) > 0:
            depart = param[0]
            depart.value = department
        else:
            depart = ConfParameter(resid=client, name='.Department', value=department)
        depart.save()
    else:
        param.delete()


def getDIRUserClient(request, dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    userclients = getUserClientsNames(request, dircompid=dircompid)
    clientres = ConfResource.objects.filter(compid_id=dircompid, type=ResType.Client, name__in=userclients,
                                            name=name)
    return clientres[0] if len(clientres) > 0 else None


def getDIRUserClientinfo(request, dircompid=None, name=None):
    clientres = getDIRUserClient(request, dircompid, name)
    if clientres is not None:
        return getDIRClientparams(clientres)
    return None


def getDIRClientPasswordParam(request, dircompid=None, name=None, resid=None):
    if name is None and resid is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    if resid is None:
        resid = getresourceid(compid=dircompid, name=name, restype=ResType.Client)
    passparam = ConfParameter.objects.filter(resid_id=resid, name=ParamType.Password)
    return passparam[0] if len(passparam) > 0 else None


def getDIRJobinfo(request, dircompid=None, name=None):
    if name is None:
        return None
    jobs = getUserJobs(request, dircompid)
    jobres = jobs.filter(name=name)
    return getDIRJobparams(request, dircompid=dircompid, jobres=jobres[0]) if len(jobres) > 0 else None


def getDIRUserClients(request, dircompid=None, os=None):
    if dircompid is None:
        dircompid = getDIRcompid(request)
    # List of the all Clients resources available
    userclients = getUserClients(request, dircompid=dircompid)
    if os is not None:
        userclients = userclients.filter(confparameter__name=ParamType.ibadOS, confparameter__value=os)
    return userclients


def extractclientsnames(clientsres):
    clientsnames = ()
    if clientsres is not None:
        for cr in clientsres:
            clientsnames += (cr.name,)
    return clientsnames


def getDIRClientsNames(request, dircompid=None, os=None):
    userclients = getDIRUserClients(request, dircompid=dircompid, os=os)
    clientsres = userclients.order_by('name')
    return extractclientsnames(clientsres)


def getDIRClientsNamesesx(request, dircompid=None):
    userclients = getDIRUserClients(request, dircompid=dircompid, os='vmware')
    clientsres = userclients.exclude(confparameter__name=ParamType.ibadvCenterName).order_by('name')
    return extractclientsnames(clientsres)


def getDIRClientsNamesnAlias(request, dircompid=None):
    userclients = getDIRUserClients(request, dircompid=dircompid)
    clientsres = userclients.exclude(confparameter__name=ParamType.ibadAlias)\
        .exclude(confparameter__name=ParamType.ibadClusterService).order_by('name')
    return extractclientsnames(clientsres)


def getDIRUserClusters(request, dircompid=None):
    userclients = getUserClients(request, dircompid=dircompid)
    clientsres = ConfParameter.objects.filter(resid__in=userclients, name=ParamType.ibadClusterName).distinct('value')
    clusters = ()
    for cr in clientsres:
        clusters += (cr.value,)
    return clusters


def getDIRClientAliases(request, dircompid=None, clientname=None):
    if clientname is None:
        return None
    # get required data
    userclients = getUserClients(request, dircompid=dircompid)
    clientsres = userclients.filter(confparameter__name=ParamType.ibadAlias,
                                    confparameter__value=clientname).order_by('name')
    return extractclientsnames(clientsres)


def updateDIRStorageDepartments(request, dircompid=None, name=None, departments=()):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    resid = getresourceid(dircompid, name, restype=ResType.Storage)
    stparams = ConfParameter.objects.filter(resid=resid, name=ParamType.ibadDepartment)
    stparams.delete()
    for dept in departments:
        if dept not in ('', ' ', '#'):
            addparameter(resid, '.Department', dept)


def getDIRClusterName(request,  dircompid=None, clientname=None):
    if clientname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    clustername = ConfParameter.objects.filter(name=ParamType.ibadClusterName, resid__compid=dircompid,
                                               resid__type=ResType.Client, resid__name=clientname)
    if len(clustername) > 0:
        return clustername[0].value
    else:
        return None


def getDIRClusterNodes(request, dircompid=None, clustername=None, clientname=None):
    if clustername is None and clientname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    if clustername is None:
        clustername = getDIRClusterName(request, dircompid, clientname)
        if clustername is None:
            return None
    clientsres = ConfResource.objects.filter(confparameter__name=ParamType.ibadClusterName,
                                             confparameter__value=clustername).order_by('name')
    return extractclientsnames(clientsres)


def getDIRClusterServices(request, dircompid=None, clustername=None, clientname=None):
    if clustername is None and clientname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    if clustername is None:
        clustername = getDIRClusterName(request, dircompid, clientname)
        if clustername is None:
            return None
    clientsres = ConfResource.objects.filter(confparameter__name=ParamType.ibadClusterService,
                                             confparameter__value=clustername).order_by('name')
    return extractclientsnames(clientsres)
