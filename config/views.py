# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render, get_object_or_404
from django.template import loader, Context
from django.http import HttpResponse
from django.db.models import Q
from libs.client import *
from libs.conf import getdecpass
from users.decorators import *
from virtual.models import *


# Create your views here.
@perm_required('clients.get_configfile')
def clientconfig(request, name):
    get_object_or_404(ConfComponent, name=name, type='F')
    dirres = ConfResource.objects.get(compid__name=name, compid__type='F', type__name='Director')
    dirp = ConfParameter.objects.filter(resid=dirres)
    dirparams = {}
    for p in dirp:
        if p.name.startswith('.'):
            continue
        if p.name == 'Password':
            encpass = p.value
            password = getdecpass(name, encpass)
            dirparams['Password'] = password
        else:
            dirparams[p.name] = p.value
    fdres = ConfResource.objects.get(compid__name=name, compid__type='F', type__name='FileDaemon')
    fdp = ConfParameter.objects.filter(resid=fdres)
    fdparams = {}
    for p in fdp:
        if p.name.startswith('.'):
            continue
        else:
            fdparams[p.name] = p.value

    messres = ConfResource.objects.get(compid__name=name, compid__type='F', type__name='Messages')
    messp = ConfParameter.objects.filter(resid=messres)
    messparams = {}
    for p in messp:
        if p.name.startswith('.'):
            continue
        else:
            messparams[p.name] = p.value

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="bacula-fd.conf"'
    temp = loader.get_template('config/bacula-fd.txt')
    context = {
        'Dir': dirres,
        'Dirparams': dirparams,
        'FD': fdres,
        'FDparams': fdparams,
        'Mess': messres,
        'Messparams': messparams,
    }
    response.write(temp.render(context))
    return response


def vsphereconfig(request, name):
    client = get_object_or_404(ConfComponent, name=name, type='F')
    query = ConfResource.objects.filter(Q(confparameter__name='.Alias', confparameter__value=name) |
                                        Q(name=client.name, type__name='Client'))
    vsnames = ConfParameter.objects.filter(resid__in=query, name='.vCenterName').values('value')
    vspheres = vCenterHosts.objects.filter(name__in=vsnames)
    for vc in vspheres:
        encpass = vc.password
        password = getdecpass(vc.name, encpass)
        vc.password = password
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="vsphere_global.conf"'
    temp = loader.get_template('config/vsphere_global.conf')
    context = Context({
        'vcenters': vspheres,
    })
    response.write(temp.render(context))
    return response
