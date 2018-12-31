# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db.models import Max, Q
from django.db import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .restype import RESTYPE
from storages.models import Storage
# import traceback
#    print "======================================================="
#    traceback.print_stack(limit=6)


def getDIRcompid(request=None):
    """ Returns -1 when no configuration available """
    if request is not None:
        if hasattr(request, 'ibadmindircompid'):
            return request.ibadmindircompid
    try:
        component = ConfComponent.objects.get(type='D')
    except OperationalError:
        return None
    except ObjectDoesNotExist:
        return -1
    if request is not None:
        request.ibadmindircompid = component.compid
    return component.compid


def getDIRname(request=None, dircompid=None):
    """ Returns None when no configuration available """
    if dircompid is None:
        dircompid = getDIRcompid(request)
    try:
        component = ConfComponent.objects.get(compid=dircompid)
    except ObjectDoesNotExist:
        return None
    return component.name


def getDIRdescr(request=None, dircompid=None):
    if dircompid is None:
        dircompid = getDIRcompid(request)
    dirres = ConfResource.objects.get(compid_id=dircompid, type=RESTYPE['Director'])
    return dirres.description


def getDIRCatalog(request=None):
    compid = getDIRcompid(request)
    resource = ConfResource.objects.get(compid_id=compid, type=RESTYPE['Catalog'])
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
    except ObjectDoesNotExist:
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
    except ObjectDoesNotExist:
        return None
    return list(param)


def getparameters(resid):
    try:
        param = ConfParameter.objects.filter(resid_id=resid).values()
    except ObjectDoesNotExist:
        return None
    return list(param)


def getresourceid(compid, name, typename):
    try:
        resource = ConfResource.objects.get(compid_id=compid, name=name, type__name=typename)
    except ObjectDoesNotExist:
        return None
    return resource.resid


def getsubresourceid(resid, typename):
    try:
        resource = ConfResource.objects.get(sub=resid, type__name=typename)
    except ObjectDoesNotExist:
        return None
    return resource.resid


def getparamskey(paramsdic, key):
    """
    function used for 'sorted()' as 'Params' key
    :param paramsdic: jobparams or clientparams dicts with 'Params' table
    :param key: a parameter key to sorted
    :return: key to sorted
    """
    params = paramsdic['Params']
    val = ''
    for a in params:
        if a['name'] == key:
            val = a['value']
    return val


def getDIRPoolid(request=None, dircompid=None, name='Default'):
    if dircompid is None:
        dircompid = getDIRcompid(request)
    return getresourceid(compid=dircompid, name=name, typename='Pool')


def getDIRJobparams(request, dircompid=None, jobres=None):
    if jobres is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    jdname = getparameter(jobres.resid, 'JobDefs')
    jdid = getresourceid(dircompid, jdname, 'JobDefs')
    jobtype = getparameter(jdid, 'Type')
    jobparams = {'Name': jobres.name, 'Descr': jobres.description, 'Type': jobtype,
                 'Params': getparameters(jobres.resid)}
    return jobparams


def getDIRJobType(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    jd = ConfParameter.objects.filter(resid__compid_id=dircompid, resid__name=name, resid__type=RESTYPE['Job'],
                                      name='JobDefs').first()
    if jd is not None:
        return jd.value
    return None


def getDIRJobDefs(dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid()
    jd = ConfResource.objects.filter(compid_id=dircompid, name=name, type=RESTYPE['JobDefs']).first()
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
    resid = ConfParameter.objects.filter(name='.ClusterName', value=cluster)[0].resid_id
    encpass = ConfParameter.objects.get(resid_id=resid, name='Password').value
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
    storageres = ConfResource.objects.filter(compid_id=dircompid, type__name='Storage').order_by('name')
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
    address = ConfParameter.objects.get(resid__compid_id=fdcompid, resid__name=name, resid__type__name='FileDaemon',
                                        name='FDAddress')
    return address.value


def getDIRClientOS(request, dircompid=None, name=None):
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
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
    return ConfParameter.objects.filter(resid__name=storname, name='MediaType', value__contains='Dedup').count() > 0


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
