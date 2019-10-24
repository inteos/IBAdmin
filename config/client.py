# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from .storage import *
from libs.client import extractclientparams
from ibadmin.ibadlic import *
from pprint import pprint


def updateClientDescr(request, dircompid=None, name=None, descr=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    updateresdescription(dircompid, name, 'Client', descr)
    fdcompid = getFDcompid(name)
    updateresdescription(fdcompid, name, 'FileDaemon', descr)


def updateClientDepartment(request, dircompid=None, name=None, department=None):
    # get required data
    if name is None:
        return None
    if department is not None and department in ['', ' ', '#']:
        department = None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    # TODO: change to common functions
    param = ConfParameter.objects.filter(resid__compid=dircompid, resid__name=name, resid__type=ResType.Client,
                                         name='.Department')
    if param.count() > 0:
        # Client-Department already exist
        depart = param[0]
        if department is not None:
            # update parameter
            depart.value = department
            depart.save()
        else:
            # remove parameter
            depart.delete()
    else:
        if department is not None:
            # add new Client parameter
            clientres = ConfResource.objects.get(name=name, type__name=ResType.Client)
            addparameter(clientres.resid, '.Department', department)


def updateClientCluster(request, dircompid=None, name=None, cluster=''):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    updateparameter(dircompid, name, ResType.Client, ParamType.ibadClusterService, cluster)
    # get cluster node info
    clientname = getDIRClusterClientname(dircompid=dircompid, name=cluster)
    clientinfo = getDIRUserClientinfo(request, name=clientname)
    clientparams = extractclientparams(clientinfo)
    encpass = clientparams['Password']
    updateparameter(dircompid, name, ResType.Client, ParamType.Password, encpass)


def updateClientAddress(request, dircompid=None, name=None, address='localhost'):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    clients = getDIRClientAliases(request, clientname=name)
    clients += (name,)
    for cl in clients:
        updateDIRClientAddress(dircompid=dircompid, name=cl, address=address)
    fdcompid = getFDcompid(name)
    updateparameter(fdcompid, name, ResType.FileDaemon, ParamType.FDAddress, address)


def updateClientAlias(request, dircompid=None, name='ibadmin', alias='ibadmin'):
    # get required data
    if dircompid is None:
        dircompid = getDIRcompid(request)
    address = getDIRClientAddress(dircompid=dircompid, name=alias)
    updateparameter(dircompid, name, ResType.Client, ParamType.Address, address)
    updateparameter(dircompid, name, ResType.Client, ParamType.ibadAlias, alias)
    encpass = getDIRClientEncpass(dircompid=dircompid, name=alias)
    updateparameter(dircompid, name, ResType.Client, ParamType.Password, encpass)
    clientos = getDIRClientOS(request, dircompid=dircompid, name=alias)
    updateparameter(dircompid, name, ResType.Client, ParamType.ibadOS, clientos)


def updateClientEnabled(request, dircompid=None, name=None, enabled=True):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    enastr = 'No'
    if enabled:
        enastr = 'Yes'
    updateDIREnabledClient(dircompid=dircompid, name=name, enabled=enastr)


def updateClientPassword(request, dircompid=None, name=None):
    # get required data
    if name is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    fdclients = getDIRClusterNodes(request, dircompid, clientname=name)
    aliasclients = getDIRClientAliases(request, clientname=name)
    serviceclients = getDIRClusterServices(request, clientname=name)
    clients = fdclients + aliasclients + serviceclients
    # generate a new password
    password = randomstr()
    dirname = getDIRname(request, dircompid=dircompid)
    direncpass = getencpass(dirname, password)
    # now update all client and aliases passwords
    for cl in clients:
        updateparameter(dircompid, cl, ResType.Client, ParamType.Password, direncpass)
    for cl in fdclients:
        fdencpass = getencpass(cl, password)
        fdcompid = getFDcompid(cl)
        updateparameter(fdcompid, dirname, ResType.Director, ParamType.Password, fdencpass)
