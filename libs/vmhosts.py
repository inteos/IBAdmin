# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from .system import detectvsphere
from django.db.models import Count
from libs.bconsole import get_lsplugin
from libs.user import *


VMHOSTSOSTYPES = (
    "proxmox",
    "xen",
    "kvm",
    "vmware",
)


def updateVMhostsdetectvsphere(request, context):
    context.update({'vmhostsdetectvsphere': detectvsphere()})


def getClientsVMnrlist(request):
    if not hasattr(request, "ibadminclientsvmnrlist"):
        userclients = getUserClients(request)
        query = ConfParameter.objects.filter(resid__in=userclients, name='.OS', value__in=VMHOSTSOSTYPES) \
            .values('value').annotate(vmnr=Count('value'))
        clientslist = []
        vmnrcontext = {}
        allvm = 0
        for vm in query:
            vmtype = vm['value']
            nr = vm['vmnr']
            param = {
                'VM': vmtype,
                'Nr': nr,
            }
            vmnrcontext[vmtype + 'hostnr'] = nr
            clientslist.append(param)
            allvm += nr
        vmnrcontext['allvmshostsnr'] = allvm
        offset = 0.0
        for vm in clientslist:
            val = vm['Nr'] * 100 / allvm
            vm.update({
                'Proc': int(val),
                'Offset': int(offset)
            })
            offset += val * 3.6
        request.ibadminclientsvmnrlist = {
            'clientslist': clientslist,
            'vmnrcontext': vmnrcontext,
        }
    return request.ibadminclientsvmnrlist['clientslist'], request.ibadminclientsvmnrlist['vmnrcontext']


def updateClientsVMnrlist(request, context):
    vmlist, hostnr = getClientsVMnrlist(request)
    context.update({'VMstatuslist': vmlist})
    context.update(hostnr)
    departs = getUserDepartmentsval(request)
    vcquery = vCenterHosts.objects.all()
    if departs.count() > 0:
        vcquery = vcquery.filter(department__in=departs)
    context.update({'vcenterhostsnr': vcquery.count()})


def getvmhostsvmlist(client=None, plugin=None, path=None):
    vmlist = []
    err = None
    if client is not None and plugin is not None and path is not None:
        out = get_lsplugin(client=client, plugin=plugin, path=path)
        if out is not None:
            for line in out:
                if line.startswith('Failed to connect to Client.'):
                    err = 1
                    break
                if line.find('Command plugin') > 0 and line.find('not found') > 0:
                    err = 2
                    break
                data = line.split()
                size = data[4]
                vmid = data[7]
                vmname = data[9]
                vmlist.append({
                    'vmname': vmname,
                    'vmid': vmid,
                    'size': size,
                })
    return vmlist, err


def getproxmoxvmlist(client=None):
    vmlist = []
    err = None
    if client is not None:
        vmlist, err = getvmhostsvmlist(client=client, plugin="proxmox:", path="vmid")
    return vmlist, err


def getxenservervmlist(client=None):
    vmlist = []
    err = None
    if client is not None:
        vmlist, err = getvmhostsvmlist(client=client, plugin="xenserver:", path="uuid")
    return vmlist, err


def clientparamsvcenterkey(clientparams):
    return getparamskey(clientparams, '.vCenterName')


def removedepartvcenter(depart):
    vCenterHosts.objects.filter(department=depart).update(department=None)


def changedepartvcenter(olddepart, newdepart):
    vCenterHosts.objects.filter(department=olddepart).update(department=newdepart)
