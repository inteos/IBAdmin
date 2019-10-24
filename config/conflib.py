# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from .restype import *
from .paramtype import *
from .models import *
from django.db import OperationalError
from django.core.exceptions import ObjectDoesNotExist
import logging


def createcomponent(name, comptype):
    component = ConfComponent(name=name, type=comptype)
    component.save()
    return component.compid


def createresource(compid, name, restype, descr=''):
    resource = ConfResource(compid_id=compid, name=name, type_id=restype, description=descr)
    resource.save()
    return resource.resid


def createsubresource(compid, name, subres, restype, descr=''):
    resource = ConfResource(compid_id=compid, name=name, sub=subres, type_id=restype, description=descr)
    resource.save()
    return resource.resid


def addparameter(resid, name, value=None):
    """
    Adds parameter to resource pointed by resid and resets stringify flag.
    The parameter wont be covered by '"' character during config generation.
    :param resid: resource id where parameter is added
    :param name: name of the parameter to add
    :param value: parameter value as an integer
    :return: parameter id added
    """
    param = ConfParameter(resid_id=resid, name=name, value=value, str=False)
    param.save()
    return param.parid


def addparameterstr(resid, name, value=''):
    """
    Adds parameter to resource pointed by resid and sets stringify flag.
    The parameter will be covered by '"' character during config generation.
    :param resid: resource id where parameter is added
    :param name: name of the parameter to add
    :param value: parameter value as a string
    :return: parameter id added
    """
    param = ConfParameter(resid_id=resid, name=name, value=value, str=True)
    param.save()
    return param.parid


def addparameterenc(resid, name, value=''):
    """
    Adds parameter to resource pointed by resid and sets encryption flag.
    Required value has to be encrypted before calling this function.
    The parameter will be covered by '"' character during config generation by default.
    :param resid: resource id where parameter is added
    :param name: name of the parameter to add
    :param value: encrypted and decoded value
    :return: parameter id added
    """
    param = ConfParameter(resid_id=resid, name=name, value=value, enc=True)
    param.save()
    return param.parid


def deleteparameter(resid, name):
    paramsquery = ConfParameter.objects.filter(resid=resid, name=name)
    # delete parameters
    paramsquery.delete()


def deleteresource(resid):
    paramsquery = ConfParameter.objects.filter(resid=resid)
    # delete parameters
    paramsquery.delete()
    resquery = ConfResource.objects.filter(resid=resid)
    # delete resource
    resquery.delete()


def deletesubresource(resid, rtype):
    subid = getsubresourceid(resid=resid, restype=rtype)
    paramsquery = ConfParameter.objects.filter(resid=subid)
    # delete all subresource parameters
    paramsquery.delete()
    resquery = ConfResource.objects.filter(resid=subid)
    # delete subresource itself
    resquery.delete()


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


def getresourceid(compid, name, restype):
    if isinstance(restype, str):
        logging.error("Invalid restype object!")
        import traceback
        print "======================================================="
        traceback.print_stack(limit=2)
        restype = RESTYPE[restype]
    try:
        resource = ConfResource.objects.get(compid_id=compid, name=name, type=restype)
    except ObjectDoesNotExist:
        return None
    return resource.resid


def getsubresourceid(resid, restype):
    if isinstance(restype, str):
        logging.error("Invalid restype object!")
        import traceback
        print "======================================================="
        traceback.print_stack(limit=2)
        restype = RESTYPE[restype]
    try:
        resource = ConfResource.objects.get(sub=resid, type=restype)
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


def createDIRcomponent(name):
    return createcomponent(name=name, comptype='D')


def createFDcomponent(name):
    return createcomponent(name=name, comptype='F')


def createBCcomponent(name):
    return createcomponent(name=name, comptype='C')


def createSDcomponent(name):
    return createcomponent(name=name, comptype='S')


def createDIRresource(dircompid=None, name=None, restype=None, descr=''):
    if dircompid is None:
        dircompid = getDIRcompid()
    return createresource(compid=dircompid, name=name, restype=restype, descr=descr)


def createDIRsubresource(dircompid=None, resid=None, name='', restype=None, descr=''):
    if dircompid is None:
        dircompid = getDIRcompid()
    if resid is None:
        return None
    return createsubresource(compid=dircompid, name=name, subres=resid, restype=restype, descr=descr)


def createDIRresDirector(dircompid=None, name=None, descr=''):
    if name is None:
        name = getDIRname()
    return createDIRresource(dircompid=dircompid, name=name, restype=ResType.Director, descr=descr)


def createDIRresCatalog(dircompid=None):
    return createDIRresource(dircompid=dircompid, name='Catalog', restype=ResType.Catalog)


def createDIRresClient(dircompid=None, name='ibadmin', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, restype=ResType.Client, descr=descr)


def createDIRresStorage(dircompid=None, name='ibadmin', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, restype=ResType.Storage, descr=descr)


def createDIRresJobDefs(dircompid=None, name='jd-default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, restype=ResType.JobDefs, descr=descr)


def createDIRresJob(dircompid=None, name='SYS-default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, restype=ResType.Job, descr=descr)


def createDIRresMessages(dircompid=None, name='Standard', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, restype=ResType.Messages, descr=descr)


def createDIRresPool(dircompid=None, name='Default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, restype=ResType.Pool, descr=descr)


def createDIRresFileSet(dircompid=None, name='fs-default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, restype=ResType.Fileset, descr=descr)


def createDIRresFSInclude(dircompid=None, resid=None, dedup=False):
    if resid is None:
        return None
    # create subresource
    includeid = createDIRsubresource(dircompid=dircompid, resid=resid, restype=ResType.Include)
    optionid = createDIRsubresource(dircompid=dircompid, resid=includeid, restype=ResType.Options)
    addparameter(optionid, 'Signature', 'MD5')
    if dedup:
        addparameter(optionid, 'Dedup', 'BothSides')
    return includeid


def createDIRresFSExclude(dircompid=None, resid=None):
    if resid is None:
        return None
    # create subresource
    return createDIRsubresource(dircompid=dircompid, resid=resid, restype=ResType.Exclude)


def createDIRresSchedule(dircompid=None, name='sch-default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, restype=ResType.Schedule, descr=descr)


def createDIRresConsole(dircompid=None, name='Default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, restype=ResType.Console, descr=descr)


def createBCresDirector(compid=None, name=None, descr=''):
    if name is None:
        name = getDIRname()
    return createresource(compid=compid, name=name, restype=ResType.Director, descr=descr)


def createFDresDirector(fdcompid=None, dirname=None, descr=''):
    if fdcompid is None:
        return None
    if dirname is None:
        dirname = getDIRname()
    return createresource(compid=fdcompid, name=dirname, restype=ResType.Director, descr=descr)


def createFDresFileDaemon(fdcompid=None, name='ibadmin', descr=''):
    if fdcompid is None:
        return None
    return createresource(compid=fdcompid, name=name, restype=ResType.FileDaemon, descr=descr)


def createFDresMessages(fdcompid=None, name='Standard', descr=''):
    if fdcompid is None:
        return None
    return createresource(compid=fdcompid, name=name, restype=ResType.Messages, descr=descr)


def createSDresDirector(sdcompid=None, dirname=None, descr=''):
    if sdcompid is None:
        return None
    if dirname is None:
        dirname = getDIRname()
    return createresource(compid=sdcompid, name=dirname, restype=ResType.Director, descr=descr)


def createSDsubresource(sdcompid=None, resid=None, name='', rtype=None, descr=''):
    if sdcompid is None:
        return None
    if resid is None:
        return None
    return createsubresource(compid=sdcompid, name=name, subres=resid, restype=rtype, descr=descr)


def createSDresMessages(sdcompid=None, name='Standard', descr=''):
    if sdcompid is None:
        return None
    return createresource(compid=sdcompid, name=name, restype=ResType.Messages, descr=descr)


def createSDresStorage(sdcompid=None, name='ibadmin', descr=''):
    if sdcompid is None:
        return None
    return createresource(compid=sdcompid, name=name, restype=ResType.Storage, descr=descr)


def createSDresDevice(sdcompid=None, name='File', descr=''):
    if sdcompid is None:
        return None
    return createresource(compid=sdcompid, name=name, restype=ResType.Device, descr=descr)


def createSDresAutochanger(sdcompid=None, name='File', descr=''):
    if sdcompid is None:
        return None
    return createresource(compid=sdcompid, name=name, restype=ResType.Autochanger, descr=descr)


def updateparameter(compid, resname, restype, name, value):
    if compid is None or resname is None or restype is None or name is None or value is None:
        return None
    param = ConfParameter.objects.get(resid__compid_id=compid, resid__name=resname, resid__type=restype,
                                      name=name)
    param.value = value
    param.save()


def updateparameterresid(resid, name, value):
    if resid is None or name is None or value is None:
        return None
    param = ConfParameter.objects.get(resid_id=resid, name=name)
    param.value = value
    param.save()


def updateresdescription(compid, name, restype, descr):
    if compid is None or restype is None or name is None:
        return None
    resource = ConfResource.objects.get(compid_id=compid, name=name, type__name=restype)
    resource.description = descr
    resource.save()


def updateFSdefaultexclude(exclude=[], clientos=None):
    if clientos is not None and clientos.startswith('win'):
        excludelist = [a.lower() for a in exclude]
        if 'c:/program files/bacula/working' not in excludelist:
            exclude.append('C:/Program Files/Bacula/working')
        if 'c:/windows/temp' not in excludelist:
            exclude.append('C:/Windows/Temp')
        if 'c:/pagefile.sys' not in excludelist:
            exclude.append('C:/pagefile.sys')
        if 'c:/$recycle.bin' not in excludelist:
            exclude.append('C:/$RECYCLE.BIN')
        if 'c:/system volume information' not in excludelist:
            exclude.append('C:/System Volume Information')
        vss = True
    else:
        if '/proc' not in exclude:
            exclude.append('/proc')
        if '/opt/bacula/working' not in exclude:
            exclude.append('/opt/bacula/working')
        vss = False
    return vss


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

