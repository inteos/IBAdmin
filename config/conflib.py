# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from .restype import RESTYPE
from .confinfo import *


def createcomponent(name='ibadmin', rtype='D'):
    component = ConfComponent(name=name, type=rtype)
    component.save()
    return component.compid


def createresource(compid, name, rtype, descr=''):
    resource = ConfResource(compid_id=compid, name=name, type_id=rtype, description=descr)
    resource.save()
    return resource.resid


def createsubresource(compid, name, subres, rtype, descr=''):
    resource = ConfResource(compid_id=compid, name=name, sub=subres, type_id=rtype, description=descr)
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
    subid = getsubresourceid(resid=resid, typename=rtype)
    paramsquery = ConfParameter.objects.filter(resid=subid)
    # delete all subresource parameters
    paramsquery.delete()
    resquery = ConfResource.objects.filter(resid=subid)
    # delete subresource itself
    resquery.delete()


def createDIRcomponent(name='ibadmin'):
    return createcomponent(name=name, rtype='D')


def createFDcomponent(name='ibadmin'):
    return createcomponent(name=name, rtype='F')


def createBCcomponent(name='ibadmin'):
    return createcomponent(name=name, rtype='C')


def createSDcomponent(name='ibadmin'):
    return createcomponent(name=name, rtype='S')


def createDIRresource(dircompid=None, name='resource', rtype=None, descr=''):
    if dircompid is None:
        dircompid = getDIRcompid()
    return createresource(compid=dircompid, name=name, rtype=rtype, descr=descr)


def createDIRsubresource(dircompid=None, resid=None, name='', rtype=None, descr=''):
    if dircompid is None:
        dircompid = getDIRcompid()
    if resid is None:
        return None
    return createsubresource(compid=dircompid, name=name, subres=resid, rtype=rtype, descr=descr)


def createDIRresDirector(dircompid=None, name=None, descr=''):
    if name is None:
        name = getDIRname()
    return createDIRresource(dircompid=dircompid, name=name, rtype=RESTYPE['Director'], descr=descr)


def createDIRresCatalog(dircompid=None):
    return createDIRresource(dircompid=dircompid, name='Catalog', rtype=RESTYPE['Catalog'])


def createDIRresClient(dircompid=None, name='ibadmin', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, rtype=RESTYPE['Client'], descr=descr)


def createDIRresStorage(dircompid=None, name='ibadmin', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, rtype=RESTYPE['Storage'], descr=descr)


def createDIRresJobDefs(dircompid=None, name='jd-default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, rtype=RESTYPE['JobDefs'], descr=descr)


def createDIRresJob(dircompid=None, name='SYS-default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, rtype=RESTYPE['Job'], descr=descr)


def createDIRresMessages(dircompid=None, name='Standard', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, rtype=RESTYPE['Messages'], descr=descr)


def createDIRresPool(dircompid=None, name='Default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, rtype=RESTYPE['Pool'], descr=descr)


def createDIRresFileSet(dircompid=None, name='fs-default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, rtype=RESTYPE['Fileset'], descr=descr)


def createDIRresFSInclude(dircompid=None, resid=None, dedup=False):
    if resid is None:
        return None
    # create subresource
    includeid = createDIRsubresource(dircompid=dircompid, resid=resid, rtype=RESTYPE['Include'])
    optionid = createDIRsubresource(dircompid=dircompid, resid=includeid, rtype=RESTYPE['Options'])
    addparameter(optionid, 'Signature', 'MD5')
    if dedup:
        addparameter(optionid, 'Dedup', 'BothSides')
    return includeid


def createDIRresFSExclude(dircompid=None, resid=None):
    if resid is None:
        return None
    # create subresource
    return createDIRsubresource(dircompid=dircompid, resid=resid, rtype=RESTYPE['Exclude'])


def createDIRresSchedule(dircompid=None, name='sch-default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, rtype=RESTYPE['Schedule'], descr=descr)


def createDIRresConsole(dircompid=None, name='Default', descr=''):
    return createDIRresource(dircompid=dircompid, name=name, rtype=RESTYPE['Console'], descr=descr)


def createBCresDirector(compid=None, name=None, descr=''):
    if name is None:
        name = getDIRname()
    return createresource(compid=compid, name=name, rtype=RESTYPE['Director'], descr=descr)


def createFDresDirector(fdcompid=None, dirname=None, descr=''):
    if fdcompid is None:
        return None
    if dirname is None:
        dirname = getDIRname()
    return createresource(compid=fdcompid, name=dirname, rtype=RESTYPE['Director'], descr=descr)


def createFDresFileDaemon(fdcompid=None, name='ibadmin', descr=''):
    if fdcompid is None:
        return None
    return createresource(compid=fdcompid, name=name, rtype=RESTYPE['FileDaemon'], descr=descr)


def createFDresMessages(fdcompid=None, name='Standard', descr=''):
    if fdcompid is None:
        return None
    return createresource(compid=fdcompid, name=name, rtype=RESTYPE['Messages'], descr=descr)


def createSDresDirector(sdcompid=None, dirname=None, descr=''):
    if sdcompid is None:
        return None
    if dirname is None:
        dirname = getDIRname()
    return createresource(compid=sdcompid, name=dirname, rtype=RESTYPE['Director'], descr=descr)


def createSDsubresource(sdcompid=None, resid=None, name='', rtype=None, descr=''):
    if sdcompid is None:
        return None
    if resid is None:
        return None
    return createsubresource(compid=sdcompid, name=name, subres=resid, rtype=rtype, descr=descr)


def createSDresMessages(sdcompid=None, name='Standard', descr=''):
    if sdcompid is None:
        return None
    return createresource(compid=sdcompid, name=name, rtype=RESTYPE['Messages'], descr=descr)


def createSDresStorage(sdcompid=None, name='ibadmin', descr=''):
    if sdcompid is None:
        return None
    return createresource(compid=sdcompid, name=name, rtype=RESTYPE['Storage'], descr=descr)


def createSDresDevice(sdcompid=None, name='File', descr=''):
    if sdcompid is None:
        return None
    return createresource(compid=sdcompid, name=name, rtype=RESTYPE['Device'], descr=descr)


def createSDresAutochanger(sdcompid=None, name='File', descr=''):
    if sdcompid is None:
        return None
    return createresource(compid=sdcompid, name=name, rtype=RESTYPE['Autochanger'], descr=descr)


def updateparameter(compid, resname, restype, name, value):
    if compid is None or resname is None or restype is None or name is None or value is None:
        return None
    param = ConfParameter.objects.get(resid__compid_id=compid, resid__name=resname, resid__type__name=restype,
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

