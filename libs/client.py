from __future__ import unicode_literals
# -*- coding: UTF-8 -*-
from .user import *
from clients.models import Client
from stats.models import *
from jobs.models import Job
from django.db.models import Count
from config.confinfo import *


def getClientStatus_a(name='ibadmin'):
    """ Asynchronous client status from stat_status table """
    param = 'bacula.client.' + name + '.status'
    try:
        out = StatStatus.objects.get(parid__name=param).nvalue
    except ObjectDoesNotExist:
        out = 0
    if out is None:
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


def getClientsDefinednr(request):
    if not hasattr(request, "ibadminclientsdefinednr"):
        request.ibadminclientsdefinednr = getUserClients(request).count()
    return request.ibadminclientsdefinednr


def updateClientsDefinednr(request, context):
    val = getClientsDefinednr(request)
    context.update({'clientsnr': val})


def updateClientres(clientres):
    name = clientres['Name']
    try:
        uname = Client.objects.get(name=name).uname
    except ObjectDoesNotExist:
        uname = 'Unknown'
    clientres.update({'Uname': uname})
    clientres.update({'Status': getClientStatus_a(name)})


def getClientsOSnrlist(request, dircompid=None, allclients=None):
    if allclients is None or allclients == 0:
        allclients = 1
    if dircompid is None:
        dircompid = getDIRcompid(request)
    userclients = getUserClients(request, dircompid=dircompid)
    query = ConfParameter.objects.filter(resid__in=userclients, name='.OS').all().values('value')\
        .annotate(osnr=Count('value'))
    offset = 0.0
    clientslist = []
    for os in query:
        val = os['osnr'] * 100 / allclients
        param = {
            'OS': os['value'],
            'Nr': os['osnr'],
            'Proc': int(val),
            'Offset': int(offset)
        }
        clientslist.append(param)
        offset += val * 3.6
    return clientslist


def updateClientsOSnrlist(request, context):
    clientlist = getClientsOSnrlist(request, allclients=context.get('clientsnr'))
    context.update({'OSstatuslist': clientlist})


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


def checkClientname(name=None):
    if name is None:
        return True
    if ConfResource.objects.filter(compid__type='D', type__name='Client', name=name).count() == 1:
        return False
    return True


def clientparamsaddresskey(clientparams):
    return getparamskey(clientparams, 'Address')


def clientparamsnamekey(clientparams):
    return clientparams['Name']


def clientparamsdescrkey(clientparams):
    return clientparams['Descr']


def clientparamsoskey(clientparams):
    return getparamskey(clientparams, '.OS')


def clientparamsclusterkey(clientparams):
    return getparamskey(clientparams, '.Cluster')


def clientparamsdepartkey(clientparams):
    return getparamskey(clientparams, '.Department')


def jobparamsstatuskey(clientparams):
    return clientparams['Status']


def getDIRClientsListfiltered(request, dircompid=None, cols=(), os=None):
    if dircompid is None:
        dircompid = getDIRcompid(request)
    # List of the all Clients resources available
    search = request.GET['search[value]']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    userclients = getUserClients(request, dircompid=dircompid)
    if os is not None:
        userclients = userclients.filter(confparameter__name='.OS', confparameter__value=os)
    total = userclients.count()
    if search != '':
        f = Q(name__icontains=search) | Q(description__icontains=search)
        filtered = userclients.filter(f).count()
        clientsres = userclients.filter(f).order_by('name')
    else:
        filtered = total
        clientsres = userclients.order_by('name')
    clientslist = []
    for cr in clientsres:
        clientparams = getDIRClientparams(clientres=cr)
        updateClientres(clientparams)
        clientslist.append(clientparams)
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = True if 'desc' == request.GET['order[0][dir]'] else False
    sclientslist = sorted(clientslist, key=order_col, reverse=order_dir)[offset:offset + limit]
    return sclientslist, total, filtered


def getDIRClientJobsList(request, dircompid=None, client=None):
    if client is None:
        return None
    if dircompid is None:
        dircompid = getDIRcompid(request)
    # List of the all jobs resources for a client
    userjobs = getUserJobs(request).filter(confparameter__name='Client', confparameter__value=client)
    jobslist = []
    for jr in userjobs:
        jobparams = getDIRJobparams(request, dircompid=dircompid, jobres=jr)
        jobslist.append(jobparams)
    return jobslist


def removedepartclient(depart):
    departs = ConfParameter.objects.filter(name='.Department', value=depart)
    departs.delete()


def changedepartclient(olddepart, newdepart):
    departs = ConfParameter.objects.filter(name='.Department', value=olddepart)
    departs.update(value=newdepart)
