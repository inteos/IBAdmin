# coding=utf-8
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from libs.client import *
from libs.system import *
from libs.job import *
from libs.menu import updateMenuNumbers
from libs.bconsole import *
from django.db.models import Q
from django.db import transaction
from .forms import *
from jobs.models import Job
from config.conf import *
from config.models import ConfResource
from operator import itemgetter
from tasks.models import *
import os


def defined(request):
    """ Defined Clients table - list """
    context = {'contentheader': 'Clients', 'contentheadersmall': 'currently defined', 'apppath': ['Clients', 'Defined']}
    updateMenuNumbers(context)
    updateClientsOSnrlist(context)
    return render(request, 'clients/defined.html', context)


def defineddata(request):
    """ JSON for warning jobs datatable """
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    # order_col = cols[int(request.GET['order[0][column]'])]
    # order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    (clientslist, total, filtered) = getDIRClientsListfiltered(search=search, offset=offset, limit=limit)
    data = []
    for clientres in clientslist:
        updateClientres(clientres)
        clientparams = extractclientparams(clientres)
        # print clientparams
        data.append([clientparams['Name'], [clientparams.get('Address'), clientparams.get('Alias')],
                     clientparams.get('Descr'), clientparams.get('OS'),
                     [clientparams.get('ClusterName'), clientparams.get('ClusterService')],
                     clientparams.get('Status'),
                     [clientparams['Name'], clientparams.get('InternalClient')],
                     ])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def info(request, name):
    """ Client info """
    clientres = getDIRClientinfo(name=name)
    if clientres is None:
        raise Http404()
    updateClientres(clientres)
    client = extractclientparams(clientres)
    if client.get('Disabledfordelete', None):
        # the job is disabled so redirect to defined jobs
        return redirect('clientsdefined')
    context = {'contentheader': 'Clients', 'apppath': ['Clients', 'Info', name], 'Client': client,
               'clientstatusdisplay': 1}
    updateMenuNumbers(context)
    updateClientsOSnrlist(context)
    return render(request, 'clients/client.html', context)


def infodefineddata(request, name):
    """ JSON for warning jobs datatable """
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    # order_col = cols[int(request.GET['order[0][column]'])]
    # order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    (jobslist, total, filtered) = getDIRClientJobsListfiltered(client=name, search=search, offset=offset, limit=limit)
    data = []
    for jobres in jobslist:
        jobparams = extractjobparams(jobres)
        # print jobparams
        schparam = jobparams.get('Scheduleparam')
        if schparam:
            scheduletext = getscheduletext(schparam) + ' at ' + jobparams.get('Scheduletime')
        else:
            scheduletext = None
        pool = jobparams.get('Pool')
        if pool:
            pooltext = getretentiontext(pool)
        else:
            pooltext = None
        data.append([jobparams['Name'], [jobparams.get('Enabled'), scheduletext], pooltext, jobparams.get('Storage'),
                     [jobparams.get('Level'), jobparams.get('Type')], jobparams.get('Descr'),
                     [jobparams['Name'], jobparams.get('Type'), jobparams.get('InternalJob')],
                     ])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def status(request, name):
    """ Client online status """
    clientres = getDIRClientinfo(name=name)
    if clientres is None:
        raise Http404()
    clientname = clientres.get('Name', 'Undefined')
    if getClientDisabledfordelete(name=clientname):
        return redirect('clientsdefined')
    context = {'contentheader': 'Clients', 'apppath': ['Clients', 'Status', name],
               'Client': extractclientparams(clientres), 'clientstatusdisplay': 1}
    updateMenuNumbers(context)
    updateClientsOSnrlist(context)
    return render(request, 'clients/status.html', context)


def statusheader(request, name):
    """ wywołanie ajax dla parametrów klienta """
    stat = getClientStatus(name)
    if stat is None:
        st = 0
        context = {'Client': {'Status': 0, 'Name': name}}
    else:
        st = 1
        client = {
            'Name': name,
            'Agent': stat['name'],
            'Status': 1,
            'Version': stat['version'],
            'Started': stat['started'],
            'RunJobs': stat['jobs_run'],
            'JobsRunning': stat['jobs_running'],
            'Plugins': stat['plugins'].replace(',', '<br>'),
        }
        context = {'Client': client}
    csname = 'bacula.client.' + name + '.status'
    cs = StatStatus.objects.filter(parid__name=csname).first()
    if cs is not None:
        cs.nvalue = st
        cs.save()
    return render(request, 'clients/statusheader.html', context)


def statusrunning(request, name):
    """ wywołanie ajax dla aktualnie uruchomionych zadań na kliencie """
    clientjobs = getClientrunningJobs(name)

    cols = ['JobId', 'Job', 'StartTime', 'Level', 'JobFiles', 'JobBytes', 'Bytessec', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = True if 'desc' == request.GET['order[0][dir]'] else False
    search = request.GET['search[value]']
    total = len(clientjobs)
    if search != '':
        # TODO zrobić filtrowanie
        # [elem for elem in list if warunek]
        filtered = total
        query = sorted(clientjobs, key=itemgetter(order_col), reverse=order_dir)[offset:offset + limit]
    else:
        filtered = total
        query = sorted(clientjobs, key=itemgetter(order_col), reverse=order_dir)[offset:offset + limit]
    data = []
    for j in query:
        # print j
        jobid = j.get('JobId', 0)
        job = j.get('Job', '')
        starttime = j.get('StartTime', '-')
        level = j.get('Level', 'Unknown')
        typ = j.get('JobType', '')
        files = j.get('JobFiles', 0)
        bytes = j.get('JobBytes', 0)
        bytessec = j.get('Bytessec', 0)
        status = j.get('Status', '')
        data.append([jobid, job, starttime, [level, typ], files, bytes,
                     bytessec, [jobid, job, typ, status]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def historydata(request, name):
    """ wywołanie ajax dla datatables podający zadania uruchomione dla danego klienta """
    cols = ['jobid', 'name', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', 'jobstatus', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Job.objects.filter(clientid__name=name).all().count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        filtered = Job.objects.filter(Q(clientid__name=name), f).count()
        query = Job.objects.filter(Q(clientid__name=name), f).order_by(orderstr, '-jobid')[offset:offset + limit]
    else:
        filtered = total
        query = Job.objects.filter(clientid__name=name).all().order_by(
            orderstr, '-jobid')[offset:offset + limit]
    data = []
    for j in query:
        if j.starttime is None:
            sstr = None
        else:
            sstr = j.starttime.strftime('%Y-%m-%d %H:%M:%S')
        if j.endtime is None:
            estr = None
        else:
            estr = j.endtime.strftime('%Y-%m-%d %H:%M:%S')
        data.append([j.jobid, j.name, [sstr, j.schedtime.strftime('%Y-%m-%d %H:%M:%S')], estr,
                     [j.level, j.type], j.jobfiles, j.jobbytes, [j.jobstatus, j.joberrors],
                     [j.jobid, j.name, j.type, j.jobstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def address(request):
    """ JSON for host address """
    addr = request.GET.get('address', '')
    return JsonResponse(checkAddress(addr), safe=False)


def name(request):
    """
        JSON for client name
        when client name already exist then return false
    """
    client = request.GET.get('name', '').encode('ascii', 'ignore')
    check = True
    if ConfResource.objects.filter(compid__type='D', type__name='Client', name=client).count() == 1:
        check = False
    return JsonResponse(check, safe=False)


def clustername(request):
    """
        JSON for cluster name
        when cluster name already exist then return false
    """
    cluster = request.GET.get('cluster', '')  # .encode('ascii', 'ignore')
    check = True
    if ConfParameter.objects.filter(resid__compid__type='D', resid__type__name='Client', name='.ClusterName',
                                    value=cluster).count() > 0:
        check = False
    return JsonResponse(check, safe=False)


def addstd(request):
    if request.method == 'GET':
        form = ClientForm()
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Add', 'Standalone'], 'form': form}
        updateMenuNumbers(context)
        updateClientsOSnrlist(context)
        return render(request, 'clients/addstd.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = ClientForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                address = form.cleaned_data['address']
                os = form.cleaned_data['os']
                defjob = form.cleaned_data['defjob']
                # create a Client resource and a Client component and all required resources
                with transaction.atomic():
                    createClient(name=name, address=address, os=os, descr=descr)
                    if defjob:
                        createDefaultClientJob(name=name, os=os)
                directorreload()
                return redirect('clientsinfo', name)
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('clientsdefined')


def addnode(request):
    cl = getDIRClientsClusters()
    clusters = (('', ''),)
    # clusters = ()
    for c in cl:
        clusters += ((c, c),)
    if request.method == 'GET':
        form = ClientNodeForm(clusters=clusters)
        if len(clusters) == 0:
            form.fields['clusterlist'].disabled = True
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Add', 'Cluster node'], 'form': form}
        updateMenuNumbers(context)
        updateClientsOSnrlist(context)
        return render(request, 'clients/addnode.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = ClientNodeForm(data=request.POST, clusters=clusters)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                cluster = form.cleaned_data.get('cluster', None)
                if cluster is not None:
                    cluster = cluster.encode('ascii', 'ignore')
                clusterlist = form.cleaned_data.get('clusterlist', None)
                address = form.cleaned_data['address']
                os = form.cleaned_data['os']
                defjob = form.cleaned_data['defjob']
                # create a Client resource and a Client component and all required resources
                with transaction.atomic():
                    createClientNode(name=name, address=address, os=os, descr=descr, cluster=cluster,
                                     clusterlist=clusterlist)
                    if defjob:
                        createDefaultClientJob(name=name, os=os)
                directorreload()
                return redirect('clientsinfo', name)
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('clientsdefined')


def addservice(request):
    cl = getDIRClientsClusters()
    if not len(cl):
        return redirect('clientsaddnode')
    clusters = ()
    for c in cl:
        clusters += ((c, c),)
    if request.method == 'GET':
        form = ClientServiceForm(clusters=clusters)
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Add', 'Cluster service'], 'form': form}
        updateMenuNumbers(context)
        updateClientsOSnrlist(context)
        return render(request, 'clients/addservice.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = ClientServiceForm(data=request.POST, clusters=clusters)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                address = form.cleaned_data['address']
                cluster = form.cleaned_data['cluster']
                defjob = form.cleaned_data['defjob']
                # create a Client resource and a Client component and all required resources
                with transaction.atomic():
                    createClientService(name=name, address=address, cluster=cluster, descr=descr)
                    if defjob:
                        createDefaultClientJob(name=name, client=name)
                directorreload()
                return redirect('clientsinfo', name)
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('clientsdefined')


def addalias(request):
    cl = getDIRClientsNamesnalias()
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        # initialclient = request.GET.get('c', None)
        form = ClientAliasForm(clients=clients)
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Add', 'Alias'], 'form': form}
        updateMenuNumbers(context)
        updateClientsOSnrlist(context)
        return render(request, 'clients/addalias.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = ClientAliasForm(clients=clients, data=request.POST)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                client = form.cleaned_data['client']
                defjob = form.cleaned_data['defjob']
                # create a Client resource based on a Client component
                with transaction.atomic():
                    createClientAlias(name=name, client=client, descr=descr)
                    if defjob:
                        createDefaultClientJob(name=name, client=name)
                directorreload()
                return redirect('clientsinfo', name)
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('clientsdefined')


def makeinitialdata(name, client):
    data = {
        'name': name,
        'descr': client['Descr'],
        'address': client['Address'],
        'os': client['OS'],
        'client': client.get('Alias'),
        'cluster': client.get('ClusterService'),
    }
    return data


def edit(request, name):
    backurl = request.GET.get('b', None)
    clientres = getDIRClientinfo(name=name)
    if clientres is None:
        raise Http404()
    client = extractclientparams(clientres)
    if client.get('Alias') is not None:
        response = redirect('clientseditalias', name)
        if backurl is not None:
            response['Location'] += '?b=' + backurl
        return response
    if client.get('ClusterService') is not None:
        response = redirect('clientseditservice', name)
        if backurl is not None:
            response['Location'] += '?b=' + backurl
        return response
    response = redirect('clientseditstd', name)
    if backurl is not None:
        response['Location'] += '?b=' + backurl
    return response


def editstd(request, name):
    clientres = getDIRClientinfo(name=name)
    if clientres is None:
        raise Http404()
    client = extractclientparams(clientres)
    if request.method == 'GET':
        data = makeinitialdata(name, client)
        form = ClientForm(initial=data)
        form.fields['name'].disabled = True
        form.fields['os'].disabled = True
        if client.get('InternalClient'):
            form.fields['address'].disabled = True
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Edit', name], 'clientstatusdisplay': 1,
                   'Client': client, 'form': form, 'OS': client['OS']}
        updateMenuNumbers(context)
        updateClientsOSnrlist(context)
        return render(request, 'clients/editstd.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            post['os'] = client['OS']
            if client.get('InternalClient'):
                post['address'] = client['Address']
            data = makeinitialdata(name, client)
            form = ClientForm(data=post, initial=data)
            if form.is_valid() and form.has_changed():
                # print "form valid and changed ... "
                if 'descr' in form.changed_data:
                    # update description
                    # print "Update description"
                    with transaction.atomic():
                        updateClientDescr(name=name, descr=form.cleaned_data['descr'])
                if 'address' in form.changed_data:
                    # update address
                    # print "Update address"
                    with transaction.atomic():
                        updateClientAddress(name=name, address=form.cleaned_data['address'])
                if 'os' in form.changed_data:
                    # update os
                    # print "Update OS"
                    # TODO: To nie skonczone, i trzeba zastanowic się jak to zrobic i czy robic?
                    # chwilowo jest to wyłączone
                    # updateClientOS(name=name, os=form.cleaned_data['os'])
                    pass
                directorreload()
                return redirect('clientsinfo', name)
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('clientsinfo', name)


def editservice(request, name):
    cl = getDIRClientsClusters()
    if not len(cl):
        return redirect('clientsaddnode')
    clusters = ()
    for c in cl:
        clusters += ((c, c),)
    clientres = getDIRClientinfo(name=name)
    if clientres is None:
        raise Http404()
    client = extractclientparams(clientres)
    if request.method == 'GET':
        data = makeinitialdata(name, client)
        form = ClientServiceForm(initial=data, clusters=clusters)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Edit', name], 'clientstatusdisplay': 1,
                   'Client': client, 'form': form, 'OS': client['OS']}
        updateMenuNumbers(context)
        updateClientsOSnrlist(context)
        return render(request, 'clients/editservice.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            data = makeinitialdata(name, client)
            form = ClientServiceForm(data=post, initial=data, clusters=clusters)
            if form.is_valid() and form.has_changed():
                # print "form valid and changed ... "
                if 'descr' in form.changed_data:
                    # update description
                    # print "Update description"
                    with transaction.atomic():
                        updateClientDescr(name=name, descr=form.cleaned_data['descr'])
                if 'address' in form.changed_data:
                    # update address
                    # print "Update address"
                    with transaction.atomic():
                        updateClientAddress(name=name, address=form.cleaned_data['address'])
                if 'cluster' in form.changed_data:
                    # update cluster
                    # print "Update cluster"
                    with transaction.atomic():
                        updateClientCluster(name=name, cluster=form.cleaned_data['cluster'])
                directorreload()
                return redirect('clientsinfo', name)
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('clientsdefined')


def editalias(request, name):
    cl = getDIRClientsNamesnalias()
    clients = ()
    for c in cl:
        clients += ((c, c),)
    clientres = getDIRClientinfo(name=name)
    if clientres is None:
        raise Http404()
    client = extractclientparams(clientres)
    if client.get('Alias') is None:
        return redirect('clientsedit')
    if request.method == 'GET':
        data = makeinitialdata(name, client)
        form = ClientAliasForm(initial=data, clients=clients)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Edit', name], 'clientstatusdisplay': 1,
                   'Client': client, 'form': form}
        updateMenuNumbers(context)
        updateClientsOSnrlist(context)
        return render(request, 'clients/editalias.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            data = makeinitialdata(name, client)
            form = ClientAliasForm(data=post, initial=data, clients=clients)
            if form.is_valid() and form.has_changed():
                # print "form valid and changed ... "
                if 'descr' in form.changed_data:
                    # update description
                    # print "Update description"
                    with transaction.atomic():
                        updateClientDescr(name=name, descr=form.cleaned_data['descr'])
                if 'client' in form.changed_data:
                    # update alias
                    # print "Update alias"
                    with transaction.atomic():
                        updateClientAlias(name=name, alias=form.cleaned_data['client'])
                directorreload()
                return redirect('clientsinfo', name)
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('clientsdefined')


def makedelete(request, name):
    """ Kasuje definicję klienta wraz ze zdefiniowanymi zadaniami i historią """
    client = get_object_or_404(ConfResource, name=name, type__name='Client')
    isrunning = checkClientJobisrunning(name=name)
    # 0 - single client no jobs defined, simple delete
    # 1 - job still running, display info modal
    # 2 - multiple jobs and jobids history found, display progress modal
    # 3 - client aliases found, display warning modal
    # 4 - client is last in cluster and has defined services, display warning modal
    st = 0
    taskid = 0
    if not isrunning:
        hasaliases = checkClienthasaliases(name=name)
        if not hasaliases:
            cluster = checkClientlastcluster(name=name)
            if not cluster:
                jobs = getClientDefinedJobs(name=name)
                nrjobs = len(jobs)
                if nrjobs > 0:
                    logi = Log(jobid_id=0, logtext='User deleted Backup Client "' + name + '" with ' + str(nrjobs) +
                                                   ' defined job(s).')
                    logi.save()
                    # has jobs defined, first disable these Jobs
                    for j in jobs:
                        disableDIRJob(name=j)
                    directorreload()
                    # disable client
                    disableDIRClient(name=name)
                    # prepare a background task
                    task = Tasks(name='Deleting Client: ' + name, proc=2, params=name)
                    task.save()
                    taskid = task.taskid
                    os.system('/opt/ibadmin/utils/ibadtasks.py ' + str(taskid))
                    st = 2
                else:
                    # no jobs history, so simple delete a client from configuration
                    logi = Log(jobid_id=0, logtext='User deleted Backup Client "' + name + '".')
                    logi.save()
                    with transaction.atomic():
                        deleteDIRClient(client=client)
                        deleteFDClient(name=name)
                    directorreload()
            else:
                st = 4
        else:
            st = 3
    else:
        st = 1
    context = {'status': st, 'taskid': taskid}
    return JsonResponse(context, safe=False)
