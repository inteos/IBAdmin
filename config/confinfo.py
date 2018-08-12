from __future__ import unicode_literals
# -*- coding: UTF-8 -*-
from django.db.models import Max, Q
from .models import *
from storages.models import Storage


def getDIRcompid():
    """ Returns None when no configuration available """
    try:
        component = ConfComponent.objects.get(type='D')
    except:
        return None
    return component.compid


def getDIRname():
    """ Returns None when no configuration available """
    try:
        component = ConfComponent.objects.get(type='D')
    except:
        return None
    return component.name


def getDIRdescr(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    dirres = ConfResource.objects.get(compid_id=dircompid, type__name='Director')
    return dirres.description


def isConfigured():
    if getDIRcompid() is None:
        return False
    return True


def getDIRCatalog():
    compid = getDIRcompid()
    resource = ConfResource.objects.get(compid_id=compid, type__name='Catalog')
    return resource.name


def getLicenseKey():
    dircompid = getDIRcompid()
    dirname = getDIRname()
    resid = getresourceid(dircompid, dirname, 'Director')
    return getparameter(resid, '.IBADLicenseKey')


def getFDcompid(name):
    try:
        component = ConfComponent.objects.get(type='F', name=name)
    except:
        return None
    return component.compid


def getSDcompid(name):
    try:
        component = ConfComponent.objects.get(type='S', name=name)
    except:
        return None
    return component.compid


def getnextStorageid():
    out = Storage.objects.aggregate(maxstorid=Max('storageid'))
    storageid = out['maxstorid']
    if storageid is None:
        # first storage defined
        return '1'
    return str(storageid + 1)


def getparameter(resid, name):
    """
    Gets a value of the parameter pointed by resource id and name.
    This limits usage of the function to unique parameters only (resid/name should be unique)
    :param resid: resource id where parameter is attached
    :param name: name of the parameter to get value for
    :return: value of the searched parameter or None when parameter cannot be found
    """
    try:
        param = ConfParameter.objects.get(resid_id=resid, name=name)
    except:
        return None
    return param.value


def getparameterlist(resid, name):
    """
    Gets a list of values for the parameter pointed by resource id and name.
    This function should be used for non unique parameters (where resid/name pair is not unique)
    :param resid: resource id where parameter is attached
    :param name: name of the parameter to get value for
    :return: list of values for the searched parameter or None when parameter cannot be found
    """
    try:
        param = ConfParameter.objects.filter(resid_id=resid, name=name).all().values()
    except:
        return None
    return list(param)


def getparameters(resid):
    try:
        param = ConfParameter.objects.filter(resid_id=resid).values()
    except:
        return None
    return list(param)


def getresourceid(compid, name, typename):
    try:
        resource = ConfResource.objects.get(compid_id=compid, name=name, type__name=typename)
    except:
        return None
    return resource.resid


def getsubresourceid(resid, typename):
    try:
        resource = ConfResource.objects.get(sub=resid, type__name=typename)
    except:
        return None
    return resource.resid


def getDIRPoolid(dircompid=None, name='Default'):
    if dircompid is None:
        dircompid = getDIRcompid()
    return getresourceid(compid=dircompid, name=name, typename='Pool')


def getDIRJobparams(dircompid=None, jobres=None):
    if jobres is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    jdname = getparameter(jobres.resid, 'JobDefs')
    jdid = getresourceid(dircompid, jdname, 'JobDefs')
    jobtype = getparameter(jdid, 'Type')
    jobparams = {'Name': jobres.name, 'Descr': jobres.description, 'Type': jobtype,
                 'Params': getparameters(jobres.resid)}
    return jobparams


def getDIRJobinfo(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    try:
        jobres = ConfResource.objects.get(compid_id=dircompid, type__name='Job', name=name)
    except:
        return None
    return getDIRJobparams(dircompid, jobres)


def getDIRJobsList(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    # List of the all jobs resources available
    jobsres = ConfResource.objects.filter(compid_id=dircompid, type__name='Job').exclude(confparameter__name='.Disabledfordelete').order_by('name')
    jobslist = []
    for jr in jobsres:
        jobparams = getDIRJobparams(dircompid, jr)
        jobslist.append(jobparams)
    return jobslist


def getDIRJobsListfiltered(dircompid=None, search='', offset=0, limit=0):
    if dircompid is None:
        dircompid = getDIRcompid()
    # List of the all jobs resources available
    total = ConfResource.objects.filter(compid_id=dircompid, type__name='Job').exclude(confparameter__name='.Disabledfordelete').all().count()
    if search != '':
        f = Q(name__icontains=search) | Q(description__icontains=search)
        filtered = ConfResource.objects.filter(Q(compid_id=dircompid, type__name='Job'), f).exclude(confparameter__name='.Disabledfordelete').count()
        jobsres = ConfResource.objects.filter(Q(compid_id=dircompid, type__name='Job'), f).exclude(confparameter__name='.Disabledfordelete').order_by('name')[offset:offset + limit]
    else:
        filtered = total
        jobsres = ConfResource.objects.filter(compid_id=dircompid, type__name='Job').exclude(confparameter__name='.Disabledfordelete').order_by('name')[offset:offset + limit]
    jobslist = []
    for jr in jobsres:
        jobparams = getDIRJobparams(dircompid, jr)
        jobslist.append(jobparams)
    return jobslist, total, filtered


def getDIRJobType(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    jd = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__name=name, resid__type__name='Job', name='JobDefs').first()
    if jd is not None:
        return jd.value
    return None


def getDIRJobDefs(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    jd = ConfResource.objects.filter(compid_id=dircompid, name=name, type__name='JobDefs').first()
    if jd is not None:
        return jd
    return None


def getDIRClientJobsList(dircompid=None, client=None):
    if client is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    # List of the all jobs resources for a client
    jobsres = ConfResource.objects.filter(compid_id=dircompid, type__name='Job', confparameter__name='Client',
                                          confparameter__value=client).order_by('name')
    jobslist = []
    for jr in jobsres:
        jobparams = getDIRJobparams(dircompid, jr)
        jobslist.append(jobparams)
    return jobslist


def getDIRClientJobsListfiltered(dircompid=None, client=None, search='', offset=0, limit=0):
    if client is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    # List of the all jobs resources for a client
    total = ConfResource.objects.filter(compid_id=dircompid, type__name='Job', confparameter__name='Client', confparameter__value=client).all().count()
    if search != '':
        f = Q(name__icontains=search) | Q(description__icontains=search)
        filtered = ConfResource.objects.filter(Q(compid_id=dircompid, type__name='Job', confparameter__name='Client', confparameter__value=client), f).exclude(confparameter__name='.Disabledfordelete').count()
        jobsres = ConfResource.objects.filter(Q(compid_id=dircompid, type__name='Job', confparameter__name='Client', confparameter__value=client), f).exclude(confparameter__name='.Disabledfordelete').order_by('name')[offset:offset + limit]
    else:
        filtered = total
        jobsres = ConfResource.objects.filter(compid_id=dircompid, type__name='Job', confparameter__name='Client', confparameter__value=client).exclude(confparameter__name='.Disabledfordelete').order_by('name')[offset:offset + limit]
    jobslist = []
    for jr in jobsres:
        jobparams = getDIRJobparams(dircompid, jr)
        jobslist.append(jobparams)
    return jobslist, total, filtered


def getDIRClientparams(clientres=None):
    if clientres is None:
        return None
    clientparams = {'Name': clientres.name, 'Descr': clientres.description, 'Params': getparameters(clientres.resid)}
    return clientparams


def getDIRClientinfo(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    try:
        clientres = ConfResource.objects.get(compid_id=dircompid, type__name='Client', name=name)
    except:
        return None
    return getDIRClientparams(clientres)


def getDIRClientsList(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    # List of the all Clients resources available
    clientsres = ConfResource.objects.filter(compid_id=dircompid, type__name='Client').exclude(confparameter__name='.Disabledfordelete').order_by('name')
    clientslist = []
    for cr in clientsres:
        clientparams = getDIRClientparams(cr)
        clientslist.append(clientparams)
    return clientslist


def getDIRClientsListfiltered(dircompid=None, search='', offset=0, limit=0):
    if dircompid is None:
        dircompid = getDIRcompid()
    # List of the all Clients resources available
    total = ConfResource.objects.filter(compid_id=dircompid, type__name='Client').exclude(confparameter__name='.Disabledfordelete').all().count()
    if search != '':
        f = Q(name__icontains=search) | Q(description__icontains=search)
        filtered = ConfResource.objects.filter(Q(compid_id=dircompid, type__name='Client'), f).exclude(confparameter__name='.Disabledfordelete').count()
        clientsres = ConfResource.objects.filter(Q(compid_id=dircompid, type__name='Client'), f).exclude(confparameter__name='.Disabledfordelete').order_by('name')[offset:offset + limit]
    else:
        filtered = total
        clientsres = ConfResource.objects.filter(compid_id=dircompid, type__name='Client').exclude(confparameter__name='.Disabledfordelete').order_by('name')[offset:offset + limit]
    clientslist = []
    for cr in clientsres:
        clientparams = getDIRClientparams(cr)
        clientslist.append(clientparams)
    return clientslist, total, filtered


def getDIRClientsNames(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    # List of the all Clients resources available
    clientsres = ConfResource.objects.filter(compid_id=dircompid, type__name='Client').order_by('name')
    clientsnames = ()
    for cr in clientsres:
        clientsnames += (cr.name,)
    return clientsnames


def getDIRClientsNamesos(dircompid=None, os=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    # List of the all Clients resources available
    if os is None:
        return getDIRClientsNames(dircompid)
    clientsres = ConfResource.objects.filter(compid_id=dircompid, type__name='Client', confparameter__name='.OS',
                                             confparameter__value=os).order_by('name')
    clientsnames = ()
    for cr in clientsres:
        clientsnames += (cr.name,)
    return clientsnames


def getDIRClientsNamesnalias(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    # List of the all Clients resources available
    clientsres = ConfResource.objects.filter(compid_id=dircompid, type__name='Client').exclude(confparameter__name='.Alias').exclude(confparameter__name='.ClusterService').order_by('name')
    clientsnames = ()
    for cr in clientsres:
        clientsnames += (cr.name,)
    return clientsnames


def getDIRClientsClusters(dircompid=None):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    # List of the all Clients resources available
    clientsres = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__type__name='Client',
                                              name='.ClusterName').distinct('value')
    clusters = ()
    for cr in clientsres:
        clusters += (cr.value,)
    return clusters


def getDIRClientsClusterEncpass(cluster=None):
    if cluster is None:
        return None
    resid = ConfParameter.objects.filter(name='.ClusterName', value=cluster)[0].resid_id
    encpass = ConfParameter.objects.get(resid_id=resid, name='Password').value
    return encpass


def getDIRClientAliases(dircompid=None, name=None):
    if name is None:
        return None
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid()
    params = ConfParameter.objects.filter(resid__type__name='Client', name='.Alias', value=name)
    aliases = ()
    for al in params:
        aliases += (al.resid.name,)
    return aliases


def getDIRStorageparams(storageres):
    if storageres is None:
        return None
    storageparams = {'Name': storageres.name, 'Descr': storageres.description,
                     'Params': getparameters(storageres.resid)}
    return storageparams


def getDIRStorageList(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    # list of the all Storages available
    storageres = ConfResource.objects.filter(compid_id=dircompid, type__name='Storage').order_by('name')
    storagelist = []
    for sr in storageres:
        storageparams = getDIRStorageparams(sr)
        storagelist.append(storageparams)
    return storagelist


def getDIRStorageNames(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    # list of the all Storages for clients available
    storageres = ConfResource.objects.filter(compid_id=dircompid, type__name='Storage').order_by('name')
    storagenames = ()
    for sr in storageres:
        storagenames += (sr.name,)
    return storagenames


def getStorageNames():
    # list of the all Storage components available
    storages = ConfComponent.objects.filter(type='S').order_by('name')
    storagenames = ()
    for sr in storages:
        storagenames += (sr.name,)
    return storagenames


def getDIRStorageinfo(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    try:
        storageres = ConfResource.objects.get(compid_id=dircompid, type__name='Storage', name=name)
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
    devicenamelist = ConfParameter.objects.filter(resid__compid=compid, resid__type__name='Autochanger',
                                                  resid__name=storage, name='Device').order_by('value').all().values()
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
    devicenamelist = ConfParameter.objects.filter(resid__compid=compid, resid__type__name='Autochanger',
                                                  resid__name=storage, name='Device').order_by('value').all()
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
    return ConfParameter.objects.filter(resid__compid_id=dircompid, resid__type__name='Storage',
                                        name='.StorageDirTapeid').values_list('value', flat=True)


def getDIRFSparams(dircompid=None, name=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    if name is None:
        return None
    resid = getresourceid(compid=dircompid, name=name, typename='Fileset')
    includeid = getsubresourceid(resid=resid, typename='Include')
    incparams = getparameters(includeid)
    optionid = getsubresourceid(resid=includeid, typename='Options')
    options = getparameters(optionid)
    excludeid = getsubresourceid(resid=resid, typename='Exclude')
    exclparams = getparameters(excludeid)
    return incparams, exclparams, options


def getDIRFSoptions(dircompid=None, name=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    if name is None:
        return None
    resid = getresourceid(compid=dircompid, name=name, typename='Fileset')
    includeid = getsubresourceid(resid=resid, typename='Include')
    optionid = getsubresourceid(resid=includeid, typename='Options')
    options = getparameters(optionid)
    return options


def getDefaultStorage(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    # TODO: rewrite to single query
    storages = ConfResource.objects.filter(compid_id=dircompid, type__name='Storage').all()
    stor = ConfParameter.objects.get(resid__in=storages, name='.InternalStorage')
    return stor.resid.name


def getDIRClientEncpass(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    encpass = ConfParameter.objects.get(resid__compid_id=dircompid, resid__name=name, resid__type__name='Client',
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
    address = ConfParameter.objects.get(resid__compid_id=sdcompid, resid__type__name='Storage', name='SDAddress')
    return address.value


def getFDClientAddress(fdcompid=None, name=None):
    if name is None:
        return None
    if fdcompid is None:
        fdcompid = getFDcompid(name=name)
    address = ConfParameter.objects.get(resid__compid_id=fdcompid, resid__name=name, resid__type__name='FileDaemon',
                                        name='FDAddress')
    return address.value


def getDIRClientOS(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    os = ConfParameter.objects.get(resid__compid_id=dircompid, resid__name=name, resid__type__name='Client',
                                   name='.OS')
    return os.value


def getClientDefinedJobs(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    query = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__type__name='Job', name='Client', value=name)
    jobs = [t.resid.name for t in query]
    return jobs


def getDIRClusterClientname(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    node = ConfParameter.objects.filter(resid__compid_id=dircompid, name='.ClusterName', value=name).first()
    if node is None:
        return None
    return node.resid.name


def getDIRadminemail(dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    param = ConfParameter.objects.get(resid__compid_id=dircompid, resid__type__name='Messages', name='Mail',
                                      resid__name='Standard')
    email = param.value.split('=')[0].rstrip()
    return email


def getStorageisDedup(storname=None):
    if storname is None:
        return False
    return ConfParameter.objects.filter(resid__name=storname, name='.StorageDirDedupidx').count() > 0


def getDIRStorageType(dircompid=None, storname=None):
    if dircompid is None:
        dircompid = getDIRcompid()
    if storname is not None:
        mtype = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__name=storname,
                                             resid__type__name='Storage', name='MediaType')
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
