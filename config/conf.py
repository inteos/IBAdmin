# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from .director import *
from .jobdefs import *
from .storage import *
from ibadmin.settings import DATABASES


def saveLicenseKey(key=None):
    if key is None:
        return
    dircompid = getDIRcompid()
    dirname = getDIRname()
    resid = getresourceid(dircompid, dirname, 'Director')
    license = getparameter(resid, '.IBADLicenseKey')
    if license is None:
        if key == '':
            return
        addparameter(resid, '.IBADLicenseKey', key)
    else:
        if key == '':
            deleteparameter(resid, '.IBADLicenseKey')
        updateparameterresid(resid, '.IBADLicenseKey', key)


def createFDDirector(fdcompid=None, dirname=None, name='ibadmin', password='ibadminpassword', descr=''):
    # create resource
    resid = createFDresDirector(fdcompid=fdcompid, dirname=dirname, descr=descr)
    # add parameters
    encpass = getencpass(name, password)
    addparameterenc(resid, 'Password', encpass)


def createFDMessages(fdcompid=None, dirname=None):
    # create resource
    resid = createFDresMessages(fdcompid=fdcompid, name='Standard', descr='Default Messages to Director')
    # add parameters
    # wydaje się, że to może być ciekawy pomysł aby z klienta przesyłać także informacje o odtworzonych plikach
    # będzie to w logu w bazie danych oraz pliku logu, ale
    # TODO: można dodać do parametrów konfiguracyjnych opcję, czy admin chce otrzymywać tą informację mailem
    # addparameter(resid, 'Director', dirname + ' = All, !Debug, !Skipped, !Restored')
    addparameter(resid, 'Director', dirname + ' = All, !Debug, !Skipped')


def check_or_createPool(dircompid=None, storage=None, retention=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    if retention is None or storage is None:
        return 'Default'
    ptype = getDIRStorageType(dircompid, storage)
    poolname = 'Pool-' + retention.replace(' ', '-') + '-' + ptype
    poolid = getDIRPoolid(dircompid=dircompid, name=poolname)
    disktype = ptype == 'disk'
    useduration = None
    if disktype:
        useduration = '1 Day'
    if poolid is None:
        # Pool does not exist, create it
        createDIRPool(dircompid=dircompid, name=poolname, disktype=disktype, retention=retention,
                      useduration=useduration, descr='Pool for ' + retention + ' retention')
    return poolname


def createFSIncludeFile(resid, include):
    if include is not None:
        for f in include:
            addparameterstr(resid, 'File', f)


def createFSIncludePlugin(resid, include):
    if include is not None:
        for f in include:
            addparameterstr(resid, 'Plugin', f)


def createFSExclude(resid, exclude):
    if exclude is not None:
        for f in exclude:
            addparameterstr(resid, 'File', f)


def createDIRFileSetFile(dircompid=None, name='fs-default', vss=False, dedup=False, include=None, exclude=None, descr=''):
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
                 allobjs=None, objsinclude=None, objsexclude=None):
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
    if internal:
        addparameter(resid, '.InternalJob', 'Yes')
    if allobjs is not None:
        addparameter(resid, '.Allobjs', allobjs)
    if objsinclude is not None:
        addparameter(resid, '.Objsinclude', objsinclude)
    if objsexclude is not None:
        addparameter(resid, '.Objsexclude', objsexclude)
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


schmaxfulldict = {
    'c1': '1 Week',
    'c2': '1 Week',
    'c3': '1 Month'
}


schcycledict = {
    'c1': 'Hours',
    'c2': 'Week',
    'c3': 'Month'
}


def createJobFilesForm(dircompid=None, data=None, jd='jd-backup-files'):
    """{
    'name': u'asd',
    'descr': u'',
    'storage': u'ibadmin-File1',
    'backuplevel': u'full',
    'starttime': datetime.time(18, 55),
    'backuprepeat': u'r1',
    'scheduleweek': u'off:off:off:off:off:off:off:off',
    'schedulemonth': u'off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:'
                      'off:off:off:off:off:off:off:off',
    'client': u'debian',
    'exclude': u'',
    'include': u'asd',
    'backupsch': u'c1',
    'retention': u'30 days'
    }"""
    if data is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    jobname = data['name'].encode('ascii', 'ignore')
    # create Pool
    poolname = check_or_createPool(dircompid=dircompid, storage=data['storage'], retention=data['retention'])
    # create Schedule
    schname = 'sch-' + jobname
    schcycle = schcycledict[data['backupsch']]
    starttime = str(data['starttime'])[:-3]
    level = data['backuplevel']
    params = {
        'level': level,
        'time': starttime,
        'scheduleweek': data['scheduleweek'],
        'schedulemonth': data['schedulemonth'],
        'backuprepeat': data['backuprepeat'],
    }
    createDIRSchedule(dircompid=dircompid, name=schname, cycle=schcycle, params=params,
                      descr='Schedule for Job: ' + data['name'])
    # create FileSet
    include = data['include'].splitlines()
    exclude = data['exclude'].splitlines()
    clientos = getDIRClientOS(dircompid=dircompid, name=data['client'])
    vss = updateFSdefaultexclude(exclude=exclude, clientos=clientos)
    fsname = 'fs-' + jobname
    dedup = getStorageisDedup(data['storage'])
    createDIRFileSetFile(dircompid=dircompid, name=fsname, vss=vss, include=include, exclude=exclude,
                         descr='Fileset for Job: ' + data['name'], dedup=dedup)
    # create Job
    if schcycle is not 'Hours':
        level = 'Incremental'
    # schedule form parameters (backupsch, backuprepeat, starttime, scheduleweek, schedulemonth)
    schparam = data['backupsch'] + ':' + data['backuprepeat']
    createDIRJob(dircompid=dircompid, name=jobname, jd=jd, descr=data['descr'], client=data['client'],
                 pool=poolname, storage=data['storage'], fileset=fsname, schedule=schname, level=level,
                 maxfullinterval=schmaxfulldict[data['backupsch']],
                 scheduleparam=schparam, scheduletime=starttime, scheduleweek=data['scheduleweek'],
                 schedulemonth=data['schedulemonth'])


def prepareFSProxmoxPlugin(data=None):
    """

    :param data:
    {
        'exclude': u'',
        'include': u'asd',
        'allvms': True,
    }
    :return:
    """
    if data is None:
        return None
    allvms = data['allvms']
    plugin = []
    exclude = data['exclude']
    include = data['include'].splitlines()
    if allvms:
        include = []
        if exclude:
            plugin.append("proxmox: exclude=" + exclude + " abort on error")
        else:
            plugin.append("proxmox: abort on error")
    else:
        exclude = ''
        for guest in include:
            if guest.startswith('vmid='):
                plugin.append("proxmox: vmid=" + guest.split('=')[1] + " abort_on_error")
            else:
                plugin.append("proxmox: vm=" + guest + " abort_on_error")
    return plugin, ":".join(a for a in include), exclude


def createJobProxmoxForm(dircompid=None, data=None, jd='jd-backup-proxmox'):
    """{
    'name': u'asd',
    'descr': u'',
    'storage': u'ibadmin-File1',
    'starttime': datetime.time(18, 55),
    'backuprepeat': u'r1',
    'scheduleweek': u'off:off:off:off:off:off:off:off',
    'schedulemonth': u'off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:'
                      'off:off:off:off:off:off:off:off',
    'client': u'debian',
    'exclude': u'',
    'include': u'guest1\nguest2\n',
    'backupsch': u'c1',
    'retention': u'30 days'
    }"""
    if data is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    jobname = data['name'].encode('ascii', 'ignore')
    # create Pool
    poolname = check_or_createPool(dircompid=dircompid, storage=data['storage'], retention=data['retention'])
    # create Schedule
    schname = 'sch-' + jobname
    schcycle = schcycledict[data['backupsch']]
    starttime = str(data['starttime'])[:-3]
    params = {
        'level': 'full',
        'time': starttime,
        'scheduleweek': data['scheduleweek'],
        'schedulemonth': data['schedulemonth'],
        'backuprepeat': data['backuprepeat'],
    }
    createDIRSchedule(dircompid=dircompid, name=schname, cycle=schcycle, params=params,
                      descr='Schedule for Job: ' + data['name'])

    # create FileSet
    fsname = 'fs-' + jobname
    dedup = getStorageisDedup(data['storage'])
    plugin, include, exclude = prepareFSProxmoxPlugin(data)
    allvms = data['allvms']
    createDIRFileSetPlugin(dircompid=dircompid, name=fsname, include=plugin, descr='Fileset for Job: ' + data['name'],
                           dedup=dedup)
    # create Job
    schparam = data['backupsch'] + ':' + data['backuprepeat']
    createDIRJob(dircompid=dircompid, name=jobname, jd=jd, descr=data['descr'], client=data['client'],
                 pool=poolname, storage=data['storage'], fileset=fsname, schedule=schname, level='full',
                 scheduleparam=schparam, scheduletime=starttime, scheduleweek=data['scheduleweek'],
                 schedulemonth=data['schedulemonth'], maxfullinterval=schmaxfulldict[data['backupsch']],
                 allobjs=allvms, objsinclude=include, objsexclude=exclude)


def createDefaultClientJob(dircompid=None, name=None, clientos=None, client=None):
    if name is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if clientos is None and client is not None:
        clientos = getDIRClientOS(name=client)
    include = ['/', '/boot']
    if clientos is not None and clientos.startswith('win'):
        include = ['C:/']
    exclude = []
    vss = updateFSdefaultexclude(exclude=exclude, clientos=clientos)
    jobname = name + '-DefaultJob'
    storage = getDefaultStorage(dircompid)
    # create Schedule
    schname = 'sch-' + jobname
    schcycle = 'Week'
    starttime = '20:00'
    level = 'incr'
    scheduleweek = 'incr:incr:incr:incr:incr:incr:incr:incr'
    schedulemonth = 'off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:off:' \
                    'off:off:off:off:off:off:off:off'
    params = {
        'level': level,
        'time': starttime,
        'scheduleweek': scheduleweek,
        'schedulemonth': schedulemonth,
        'backuprepeat': 'r1',
    }
    createDIRSchedule(dircompid=dircompid, name=schname, cycle=schcycle, params=params,
                      descr='Schedule for Job: ' + jobname)
    # create FileSet
    fsname = 'fs-' + jobname
    createDIRFileSetFile(dircompid=dircompid, name=fsname, vss=vss, include=include, exclude=exclude,
                         descr='Fileset for Job: ' + jobname)
    # create Job
    if schcycle is not 'Hours':
        level = 'Incremental'
    # schedule form parameters (backupsch, backuprepeat, starttime, scheduleweek, schedulemonth)
    schparam = 'c2:r1'
    createDIRJob(dircompid=dircompid, name=jobname, jd='jd-backup-files', descr='Default Client Backup Job',
                 client=name, pool='Default', storage=storage, fileset=fsname, schedule=schname, level=level,
                 maxfullinterval='1 Week', scheduleparam=schparam, scheduletime=starttime, scheduleweek=scheduleweek,
                 schedulemonth=schedulemonth)


def createFDFileDaemon(fdcompid=None, name='ibadmin', descr='', address='localhost', os='rhel'):
    # create resource
    resid = createFDresFileDaemon(fdcompid=fdcompid, name=name, descr=descr)
    # add parameters
    if os == 'win32' or os == 'win64':
        maxjobs = 2
        piddir = 'C:/Program Files/Bacula/working'
        plugdir = 'C:/Program Files/Bacula/plugins'
        workdir = 'C:/Program Files/Bacula/working'
    elif os == 'osx':
        maxjobs = 10
        piddir = '/var/run'
        plugdir = '/usr/local/bacula/plugins'
        workdir = '/private/var/bacula/working'
    else:
        maxjobs = 10
        piddir = '/opt/bacula/working'
        plugdir = '/opt/bacula/plugins'
        workdir = '/opt/bacula/working'
    addparameter(resid, 'MaximumConcurrentJobs', maxjobs)
    addparameterstr(resid, '.OS', os)
    addparameterstr(resid, 'PidDirectory', piddir)
    addparameterstr(resid, 'PluginDirectory', plugdir)
    addparameterstr(resid, 'WorkingDirectory', workdir)
    addparameter(resid, 'HeartbeatInterval', 60)
    addparameter(resid, 'FDAddress', address)
    addparameter(resid, 'FDPort', 9102)


def createClientNode(dircompid=None, dirname=None, name='ibadmin', address='localhost', os='rhel', descr='',
                     cluster=None, clusterlist=None, internal=False):
    if cluster is not None and len(cluster):
        # New cluster name
        cl = cluster
        encpass = None
    else:
        # existing cluster
        cl = clusterlist
        encpass = getDIRClientsClusterEncpass(cluster=cl)
    createClient(dircompid=dircompid, dirname=dirname, name=name, address=address, os=os, cluster=cl, descr=descr,
                 internal=internal, encpass=encpass)


def createClient(dircompid=None, dirname=None, name='ibadmin', address='localhost', os='rhel', descr='',
                 internal=False, cluster=None, encpass=None):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    # generate password
    if encpass is None:
        password = randomstr()
    else:
        password = getdecpass(dirname, encpass)
    # insert new Client {} resource into Dir conf
    createDIRClient(dircompid=dircompid, dirname=dirname, name=name, password=password, address=address, os=os,
                    descr=descr, internal=internal, cluster=cluster)
    # create a FD component
    fdcompid = createFDcomponent(name=name)
    # insert new FileDaemon {} resource into FD conf
    createFDDirector(fdcompid=fdcompid, dirname=dirname, name=name, password=password)
    createFDFileDaemon(fdcompid=fdcompid, name=name, descr=descr, address=address, os=os)
    createFDMessages(fdcompid=fdcompid, dirname=dirname)


def createClientAlias(dircompid=None, dirname=None, name='ibadmin', client=None, descr=''):
    if client is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    # TODO wykorzystać funkcje jak w updateClientAlias
    clientinfo = getDIRClientinfo(name=client)
    clientparams = extractclientparams(clientinfo)
    encpass = clientparams['Password']
    address = clientparams['Address']
    os = clientparams['OS']
    # insert new Client {} resource into Dir conf
    createDIRClient(dircompid=dircompid, dirname=dirname, name=name, encpass=encpass, address=address, os=os,
                    descr=descr, alias=client)


def updateClientAlias(dircompid=None, name='ibadmin', alias='ibadmin'):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    address = getDIRClientAddress(dircompid=dircompid, name=alias)
    updateparameter(dircompid, name, 'Client', 'Address', address)
    updateparameter(dircompid, name, 'Client', '.Alias', alias)
    encpass = getDIRClientEncpass(dircompid=dircompid, name=alias)
    updateparameter(dircompid, name, 'Client', 'Password', encpass)
    os = getDIRClientOS(dircompid=dircompid, name=alias)
    updateparameter(dircompid, name, 'Client', '.OS', os)


def createClientService(dircompid=None, dirname=None, name='ibadmin', address='127.0.0.1', cluster=None, descr=''):
    if cluster is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    client = getDIRClusterClientname(dircompid=dircompid, name=cluster)
    clientinfo = getDIRClientinfo(name=client)
    clientparams = extractclientparams(clientinfo)
    encpass = clientparams['Password']
    os = clientparams['OS']
    # insert new Client {} resource into Dir conf
    createDIRClient(dircompid=dircompid, dirname=dirname, name=name, encpass=encpass, address=address, os=os,
                    descr=descr, service=cluster)


def updateDIRClientDescr(dircompid=None, name='ibadmin', descr=''):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    updateresdescription(dircompid, name, 'Client', descr)


def updateDIRStorageDescr(dircompid=None, name=None, descr=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    updateresdescription(dircompid, name, 'Storage', descr)


def updateClientDescr(dircompid=None, name=None, descr=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    updateresdescription(dircompid, name, 'Client', descr)
    fdcompid = getFDcompid(name)
    updateresdescription(fdcompid, name, 'FileDaemon', descr)


def updateClientCluster(dircompid=None, name=None, cluster=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    updateparameter(dircompid, name, 'Client', '.ClusterService', cluster)
    # get cluster node info
    client = getDIRClusterClientname(dircompid=dircompid, name=cluster)
    clientinfo = getDIRClientinfo(name=client)
    clientparams = extractclientparams(clientinfo)
    encpass = clientparams['Password']
    updateparameter(dircompid, name, 'Client', 'Password', encpass)


def updateDIRClientAddress(dircompid=None, name=None, address='localhost'):
    if name is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    updateparameter(dircompid, name, 'Client', 'Address', address)


def updateClientAddress(dircompid=None, name=None, address='localhost'):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    clients = getDIRClientAliases(name=name)
    clients += (name,)
    for cl in clients:
        updateDIRClientAddress(dircompid=dircompid, name=cl, address=address)
    fdcompid = getFDcompid(name)
    updateparameter(fdcompid, name, 'FileDaemon', 'FDAddress', address)


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


def updateDIRadminemail(dircompid=None, dirname=None, email=''):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if dirname is None:
        dirname = getDIRname()
    emailstr = email + ' = All, !Debug, !Skipped, !Restored'
    updateparameter(dircompid, 'Standard', 'Messages', 'Mail', emailstr)
    emailstr = email + ' = All, !Fatal, !Debug, !Skipped, !Restored'
    updateparameter(dircompid, 'Daemon', 'Messages', 'Mail', emailstr)


def updateJobStorage(dircompid=None, name=None, storage='ibadmin'):
    # get required data
    if name is None:
        return
    if dircompid is None:
        dircompid = getDIRcompid()
    updateparameter(dircompid, name, 'Job', 'Storage', storage)
    dedup = getStorageisDedup(storage)
    fsname = 'fs-' + name
    updateFSOptionsDedup(dircompid=dircompid, fsname=fsname, dedup=dedup)
    jobresid = getresourceid(dircompid, name, 'Job')
    cpool = getparameter(jobresid, 'Pool')
    if cpool == 'Default':
        retention = "2 weeks"
    else:
        cpooldata = cpool.split('-')
        retention = cpooldata[1] + ' ' + cpooldata[2]
    poolname = check_or_createPool(dircompid=dircompid, storage=storage, retention=retention)
    updateparameter(dircompid, name, 'Job', 'Pool', poolname)


def updateJobClient(dircompid=None, name=None, client='ibadmin'):
    if name is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    print dircompid, name, client
    updateparameter(dircompid, name, 'Job', 'Client', client)


def updateFSOptionsDedup(dircompid=None, fsname=None, includeid=None, dedup=False):
    if fsname is None:
        return
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if includeid is None:
        resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
        includeid = getsubresourceid(resid=resid, typename='Include')
    optionid = getsubresourceid(resid=includeid, typename='Options')
    dedupparam = ConfParameter.objects.filter(resid=optionid, name='Dedup').count() > 0
    if dedup is True and dedupparam is False:
        addparameter(optionid, 'Dedup', 'BothSides')
    elif dedup is False and dedupparam is True:
        deleteparameter(optionid, 'Dedup')


def updateFSOptionsCompression(dircompid=None, fsname=None, includeid=None, compression=None):
    if fsname is None:
        return
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if includeid is None:
        resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
        includeid = getsubresourceid(resid=resid, typename='Include')
    optionid = getsubresourceid(resid=includeid, typename='Options')
    comprparam = ConfParameter.objects.filter(resid=optionid, name='Compression').count() > 0
    if compression == 'no' or compression is None or compression == '':
        if comprparam is True:
            deleteparameter(optionid, 'Compression')
    else:
        compr = compression.upper()
        if comprparam is False:
            addparameter(optionid, 'Compression', compr)
        else:
            updateparameterresid(optionid, 'Compression', compr)


def updateFSIncludeFile(dircompid=None, fsname=None, include=''):
    if fsname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    includelist = include.splitlines()
    resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
    includeid = getsubresourceid(resid=resid, typename='Include')
    query = ConfParameter.objects.filter(resid=includeid)
    query.delete()
    createFSIncludeFile(resid=includeid, include=includelist)


def updateFSExclude(dircompid=None, fsname=None, exclude='', client=None):
    if fsname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    excludelist = exclude.splitlines()
    clientos = getDIRClientOS(dircompid=dircompid, name=client)
    updateFSdefaultexclude(exclude=excludelist, clientos=clientos)
    resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
    excludeid = getsubresourceid(resid=resid, typename='Exclude')
    query = ConfParameter.objects.filter(resid=excludeid)
    query.delete()
    createFSExclude(resid=excludeid, exclude=excludelist)


def updateFSIncludePlugin(dircompid=None, fsname=None, include=[]):
    if fsname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
    includeid = getsubresourceid(resid=resid, typename='Include')
    query = ConfParameter.objects.filter(resid=includeid)
    query.delete()
    createFSIncludePlugin(resid=includeid, include=include)


def updateJobEnabled(dircompid=None, name=None, enabled=True):
    if name is None:
        return
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    ena = 'No'
    if enabled:
        ena = 'Yes'
    resid = getresourceid(compid=dircompid, name=name, typename='Job')
    updateparameterresid(resid=resid, name='Enabled', value=ena)


def updateJobAllobjs(dircompid=None, name=None, allobjs=None, objsinclude=None, objsexclude=None):
    if name is None:
        return
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    updateparameter(compid=dircompid, resname=name, restype='Job', name='.Allobjs', value=allobjs)
    updateparameter(compid=dircompid, resname=name, restype='Job', name='.Objsinclude', value=objsinclude)
    updateparameter(compid=dircompid, resname=name, restype='Job', name='.Objsexclude', value=objsexclude)


def updateJobRunBefore(dircompid=None, name=None, runbefore=''):
    if name is None:
        return
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    param = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__name=name, resid__type__name='Job',
                                         name='ClientRunBeforeJob').first()
    if runbefore is not None and len(runbefore):
        # add or change runbefore
        if param is None:
            # require param to add
            resid = getresourceid(compid=dircompid, name=name, typename='Job')
            param = ConfParameter(resid_id=resid, name='ClientRunBeforeJob', value=runbefore, str=True)
        else:
            param.value = runbefore
        param.save()
    else:
        # disable runbefore
        if param is None:
            # disabled already
            return
        param.delete()


def updateJobRunAfter(dircompid=None, name=None, runafter=''):
    if name is None:
        return
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    param = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__name=name, resid__type__name='Job',
                                         name='ClientRunAfterJob').first()
    if runafter is not None and len(runafter):
        # add or change runbefore
        if param is None:
            # require param to add
            resid = getresourceid(compid=dircompid, name=name, typename='Job')
            param = ConfParameter(resid_id=resid, name='ClientRunAfterJob', value=runafter, str=True)
        else:
            param.value = runafter
        param.save()
    else:
        # disable runbefore
        if param is None:
            # disabled already
            return
        param.delete()


def deleteDIRFileSet(dircompid=None, fsname=None):
    if fsname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    resid = getresourceid(compid=dircompid, name=fsname, typename='Fileset')
    # delete options subresource of include subresource
    includeid = getsubresourceid(resid=resid, typename='Include')
    deletesubresource(includeid, 'Options')
    deletesubresource(resid, 'Include')
    # delete exclude subresource
    deletesubresource(resid, 'Exclude')
    # delete fileset resource
    deleteresource(resid)


def updateJobRetention(dircompid=None, name=None, retention=None):
    # get required data
    if name is None or retention is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    # create Pool
    storname = getDIRJobStorage(dircompid, name)
    poolname = check_or_createPool(dircompid=dircompid, storage=storname, retention=retention)
    updateparameter(compid=dircompid, resname=name, restype='Job', name='Pool', value=poolname)


def updateJobSchedule(dircompid=None, jobname=None, data=None, backupsch='', starttime='', scheduleweek='',
                   schedulemonth='', backuprepeat='', backuplevel='', forcelevel=None):
    """

    :param dircompid:
    :param jobname: Job name for which
    :param data:
    :param backupsch:
    :param starttime:
    :param scheduleweek:
    :param schedulemonth:
    :param backuprepeat:
    :param backuplevel:
    :return:
    """
    if jobname is None and data is None:
        return None
    if data is not None:
        if jobname is None:
            jobname = data['name']
        backupsch = data['backupsch']
        starttime = data['starttime']
        scheduleweek = data['scheduleweek']
        schedulemonth = data['schedulemonth']
        backuprepeat = data['backuprepeat']
        if forcelevel is None:
            backuplevel = data['backuplevel']
    if dircompid is None:
        dircompid = getDIRcompid()
    schname = 'sch-' + jobname
    resid = getresourceid(compid=dircompid, name=schname, typename='Schedule')
    query = ConfParameter.objects.filter(resid=resid)
    query.delete()
    schtime = str(starttime)[:-3]
    if forcelevel is not None:
        backuplevel = forcelevel
    params = {
        'level': backuplevel,
        'time': schtime,
        'scheduleweek': scheduleweek,
        'schedulemonth': schedulemonth,
        'backuprepeat': backuprepeat,
    }
    if backupsch == 'c1':
        # c1 - cycle during Day, every xx hours
        createDIRSchHours(resid, params)
    if backupsch == 'c2':
        # c2 - cycle during Week
        createDIRSchWeek(resid, params)
        lvl = scheduleweek.split(':')[7]
        if lvl != 'off':
            backuplevel = lvl
        else:
            backuplevel = 'incr'
    if backupsch == 'c3':
        # c3 - cycle during Month
        createDIRSchMonth(resid, params)
        lvl = schedulemonth.split(':')[31]
        if lvl != 'off':
            backuplevel = lvl
        else:
            backuplevel = 'incr'
    jresid = getresourceid(compid=dircompid, name=jobname, typename='Job')
    updateparameterresid(resid=jresid, name='Level', value=getlevelname(backuplevel))
    schparam = data['backupsch'] + ':' + data['backuprepeat']
    updateparameterresid(resid=jresid, name='.Scheduleparam', value=schparam)
    updateparameterresid(resid=jresid, name='.Scheduletime', value=schtime)
    updateparameterresid(resid=jresid, name='.Scheduleweek', value=scheduleweek)
    updateparameterresid(resid=jresid, name='.Schedulemonth', value=schedulemonth)
    updateparameterresid(resid=jresid, name='MaxFullInterval', value=schmaxfulldict[backupsch])


def updateScheduletime(dircompid=None, name=None, jobname=None, level='', starttime='05:00:00'):
    if name is None or jobname is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    schtime = str(starttime)[:-3]
    schparam = level + ' at ' + schtime
    resid = getresourceid(compid=dircompid, name=name, typename='Schedule')
    updateparameterresid(resid=resid, name='Run', value=schparam)
    jresid = getresourceid(compid=dircompid, name=jobname, typename='Job')
    updateparameterresid(resid=jresid, name='.Scheduletime', value=schtime)


def deleteDIRSchedule(dircompid=None, schname=None):
    if schname is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    resid = getresourceid(compid=dircompid, name=schname, typename='Schedule')
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
        resid = getresourceid(compid=dircompid, name=name, typename='Job')
    # delete FileSet
    fsname = 'fs-' + name
    deleteDIRFileSet(dircompid=dircompid, fsname=fsname)
    # delete Schedule
    schname = 'sch-' + name
    deleteDIRSchedule(dircompid=dircompid, schname=schname)
    # delete Job resource and parameters
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
        resid = getresourceid(compid=dircompid, name=name, typename='Job')
    # change Enabed parameter to No
    updateparameterresid(resid=resid, name='Enabled', value='No')
    addparameter(resid=resid, name='.Disabledfordelete', value='Yes')


def disableDIRClient(dircompid=None, name=None, client=None):
    if name is None and client is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if client is not None:
        resid = client.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, typename='Client')
    addparameter(resid=resid, name='.Disabledfordelete', value='Yes')
    addparameter(resid=resid, name='Enabled', value='No')


def deleteDIRClient(dircompid=None, name=None, client=None):
    if name is None and client is None:
        return None
    # get and prepare required data
    if dircompid is None:
        dircompid = getDIRcompid()
    if client is not None:
        resid = client.resid
    else:
        resid = getresourceid(compid=dircompid, name=name, typename='Client')
    # delete Client resource and parameters
    deleteresource(resid)


def deleteFDClient(name=None):
    if name is None:
        return None
    # get and prepare required data
    fdcompid = getFDcompid(name=name)
    if fdcompid is None:
        return None
    fdparams = ConfParameter.objects.filter(resid__compid_id=fdcompid)
    fdparams.delete()
    fdres = ConfResource.objects.filter(compid_id=fdcompid)
    fdres.delete()
    fdcomp = ConfComponent.objects.filter(compid=fdcompid)
    fdcomp.delete()


def initialize(name='ibadmin', descr='', email='root@localhost', password=None, stortype='File',
               address='localhost', archdir='/tmp', dedupdir=None, dedupidxdir=None, tapelib=None):
    # prepare variables
    clientip = address
    storip = address
    # create DIR component
    dircompid = createDIRcomponent(name=name)
    # create DIR Director Resource
    createDIRDirector(dircompid=dircompid, name=name, descr=descr)
    # create DIR Catalog Resource
    dbname = DATABASES['default']['NAME']
    dbuser = DATABASES['default']['USER']
    dbpass = DATABASES['default']['PASSWORD']
    createDIRCatalog(dircompid=dircompid, dbname=dbname, dbuser=dbuser, dbpassword=dbpass)
    # create DIR Messages Standard Resource
    createDIRMessages(dircompid=dircompid, name='Standard', email=email, log='bacula.log',
                      descr='Standard Job Messages')
    # create DIR Messages Daemon Resource
    createDIRMessages(dircompid=dircompid, name='Daemon', email=email, log='daemon.log', descr='Daemon Messages',
                      fatal=False)
    # create Admin Schedule
    scheduletimeadmin = '05:00'
    createDIRSchedule(dircompid=dircompid, name='sch-admin', cycle='Day', params={'level': 'full',
                                                                                  'time': scheduletimeadmin})
    # create Catalog backup Schedule
    scheduletime = '05:05'
    createDIRSchedule(dircompid=dircompid, name='sch-backup-catalog', cycle='Day',
                      params={'level': 'Full', 'time': scheduletime})
    # create default FileSet
    createDIRFileSetFile(dircompid=dircompid, name='fs-default', include=['/'],
                         exclude=['/opt/bacula/working', '/proc', '/tmp'],
                         descr='Default FileSet')
    # create Catalog backup FileSet
    createDIRFileSetFile(dircompid=dircompid, name='fs-catalog-backup',
                         include=['/opt/bacula/working/bacula.sql', '/opt/bacula/scripts', '/opt/bacula/bsr'],
                         exclude=['/opt/bacula/working'],
                         descr='Catalog backup FileSet')
    # create Client
    createClient(dircompid=dircompid, dirname=name, name=name, address=clientip, descr='Default local client',
                 internal=True, os=getOStype())
    # create Storage
    storname = createStorage(dircompid=dircompid, dirname=name, storname=name, address=storip,
                             descr='Default local storage', stortype=stortype, archdir=archdir, dedupdir=dedupdir,
                             dedupidxdir=dedupidxdir, internal=True, tapelib=tapelib)
    # create default Pool
    createDIRPool(dircompid=dircompid, name='Default', disktype=stortype != 'tape', retention='2 weeks',
                  useduration='1 day', descr='Default System Pool with 2W retention')
    # create Scratch Pool
    createDIRPool(dircompid=dircompid, name='Scratch', retention='2 weeks', descr='Management Scratch Pool',
                  cleaning=True)
    # create Admin JobDefs
    createDIRJobDefsAdmin(dircompid=dircompid, client=name, storage=storname)
    # create Restore JobDefs
    createDIRJobDefsRestore(dircompid=dircompid, client=name, storage=storname)
    # create Catalog backup JobDefs
    createDIRJobDefsCatalog(dircompid=dircompid, storage=storname)
    # create Catalog backup JobDefs
    createDIRAllJobDefs(dircompid=dircompid)
    # create Admin Job
    onceaday = 'c1:r24'     # this is en equivalent to once a day :)
    createDIRJob(dircompid=dircompid, name='SYS-Admin', jd='jd-admin', internal=True,
                 descr='Internal administration job for system maintanance',
                 scheduleparam=onceaday, scheduletime=scheduletimeadmin)
    # create Restore Job
    createDIRJob(dircompid=dircompid, name='Restore', jd='jd-restore', descr='Internal Restore Job', internal=True)
    # create Catalog backup Job
    createDIRJob(dircompid=dircompid, name='SYS-Backup-Catalog', jd='jd-backup-catalog', client=name, internal=True,
                 pool='Default', storage=storname, level='Full', descr='Internal job for backup Catalog database',
                 scheduleparam=onceaday, scheduletime=scheduletime)
