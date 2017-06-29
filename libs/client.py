from __future__ import unicode_literals
# -*- coding: UTF-8 -*-
from config.models import *
from clients.models import Client
from stats.models import *
from jobs.models import Job
from django.db.models import Count


def getClientStatus_a(name='ibadmin'):
    """ Status asynchroniczny z tabeli stat_status """
    param = 'bacula.client.' + name + '.status'
    try:
        out = int(StatStatus.objects.get(parid__name=param).nvalue)
    except:
        out = 0
    return out


def extractclientparams(clientres):
    uname = clientres.get('Uname', 'Unknown')
    status = clientres.get('Status', 0)
    clientparams = {'Name': clientres['Name'], 'Descr': clientres['Descr'], 'Uname': uname, 'Status': status}
    for param in clientres['Params']:
        clientparams[param['name'].replace('.', '')] = param['value']
    # print clientparams
    return clientparams


def getClientsDefinednr():
    return ConfResource.objects.filter(compid__type='D', type__name='Client').exclude(confparameter__name='.Disabledfordelete').count()


def updateClientsDefinednr(context):
    val = getClientsDefinednr()
    context.update({'clientsnr': val})


def updateClientres(clientres):
    name = clientres['Name']
    try:
        uname = Client.objects.get(name=name).uname
    except:
        uname = 'Unknown'
    clientres.update({'Uname': uname})
    clientres.update({'Status': getClientStatus_a(name)})


def getClientsOSnrlist(all):
    if all is None or all == 0:
        all = 1
    query = ConfParameter.objects.filter(resid__compid__type='D', name='.OS').all().values('value').annotate(osnr=Count('value'))
    offset = 0.0
    clientslist = []
    for os in query:
        val = os['osnr'] * 100 / all
        param = {
            'OS': os['value'],
            'Nr': os['osnr'],
            'Proc': int(val),
            'Offset': int(offset)
        }
        clientslist.append(param)
        offset += val * 3.6
    return clientslist


def updateClientsOSnrlist(context):
    list = getClientsOSnrlist(context['clientsnr'])
    context.update({'OSstatuslist': list})


def getClientDisabledfordelete(name):
    return ConfParameter.objects.filter(name='.Disabledfordelete', resid__name=name, resid__type__name='Client').count()


def checkClienthasaliases(name=None):
    if name is None:
        return None
    clients = ConfParameter.objects.filter(name='.Alias', value=name).count()
    return clients


def checkClientlastcluster(name=None):
    if name is None:
        return None
    cluster = ConfParameter.objects.filter(name='.ClusterName', resid__name=name, resid__type__name='Client')
    if cluster.count() == 1:
        cluster = cluster[0]
        clients = ConfParameter.objects.filter(name='.ClusterName', value=cluster.value).count()
        if clients > 1:
            return False
        services = ConfParameter.objects.filter(name='.ClusterService', value=cluster.value).count()
        return services > 0
    else:
        return False


def getClientJobsrunningnr(name=None):
    if name is None:
        return 0
    val = Job.objects.filter(clientid__name=name, jobstatus__in=['R', 'B', 'a', 'i'])
    return val.count()

