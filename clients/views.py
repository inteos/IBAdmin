# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from libs.client import *
from libs.system import *
from libs.job import *
from libs.menu import updateMenuNumbers
from libs.bconsole import *
from django.contrib import messages
from django.db import transaction
from .forms import *
from jobs.models import Job
from config.conf import *
from config.models import ConfResource
from operator import itemgetter
from tasks.models import *
from users.decorators import *
from libs.ibadmin import *
from libs.vmhosts import VMHOSTSOSTYPES
import os


@perm_required('clients.view_clients')
def defined(request):
    """ Defined Clients table - list """
    context = {'contentheader': 'Clients', 'contentheadersmall': 'currently defined', 'apppath': ['Clients', 'Defined']}
    updateMenuNumbers(request, context)
    updateClientsOSnrlist(request, context)
    return render(request, 'clients/defined.html', context)


@perm_required('clients.view_clients')
def defineddata(request):
    """ JSON for warning jobs datatable """
    cols = [clientparamsnamekey, clientparamsaddresskey, clientparamsdescrkey, clientparamsdepartkey, clientparamsoskey,
            clientparamsclusterkey, jobparamsstatuskey]
    (clientslist, total, filtered) = getDIRClientsListfiltered(request, cols=cols)
    data = []
    for clientres in clientslist:
        clientparams = extractclientparams(clientres)
        # print clientparams
        dname, dcolor = getdepartmentlabel(clientparams.get('Department'))
        data.append([clientparams['Name'], [clientparams.get('Address'), clientparams.get('Alias')],
                     clientparams.get('Descr'), [dcolor, dname],
                     ibadmin_render_os(clientparams.get('OS')),
                     [clientparams.get('ClusterName'), clientparams.get('ClusterService')],
                     clientparams.get('Status'),
                     [clientparams['Name'], clientparams.get('InternalClient')],
                     ])
    draw = request.GET['draw']
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('clients.view_clients')
def info(request, name):
    """ Client info """
    clientres = getDIRClientinfo(request, name=name)
    if clientres is None:
        raise Http404()
    updateClientres(clientres)
    client = extractclientparams(clientres)
    if client.get('Disabledfordelete', None):
        # the job is disabled so redirect to defined jobs
        return redirect('clientsdefined')
    depart = client.get('Department')
    if depart is not None:
        client.update({'Department': getDepartment(depart)})
    clientvmhost = False
    clientos = client.get('OS', None)
    if clientos in VMHOSTSOSTYPES:
        clientvmhost = True
    context = {'contentheader': 'Clients', 'apppath': ['Clients', 'Info', name], 'Client': client,
               'clientstatusdisplay': 1, 'clientvmhost': clientvmhost}
    updateMenuNumbers(request, context)
    updateClientsOSnrlist(request, context)
    return render(request, 'clients/client.html', context)


@any_perm_required('clients.view_clients')
@perm_required('jobs.view_jobs')
def infodefineddata(request, name):
    """ JSON for warning jobs datatable """
    cols = [jobparamsnamekey, None, jobparamspoolkey, jobparamsstoragekey, jobparamslevelkey, jobparamsdescrkey]
    (jobslist, total, filtered) = getDIRJobsListfiltered(request, client=name, cols=cols)
    data = []
    for jobres in jobslist:
        jobparams = extractjobparams(jobres)
        # print jobparams
        schparam = jobparams.get('Scheduleparam')
        if schparam:
            scheduletext = '%s at %s' % (getscheduletext(schparam), jobparams.get('Scheduletime'))
        else:
            scheduletext = None
        pool = jobparams.get('Pool')
        if pool:
            pooltext = getretentiontext(pool)
        else:
            pooltext = None
        data.append([jobparams['Name'], [jobparams.get('Enabled'), scheduletext], pooltext, jobparams.get('Storage'),
                     ibadmin_render_joblevel(jobparams.get('Level'), jobparams.get('Type')),
                     jobparams.get('Descr'),
                     [jobparams['Name'], jobparams.get('Type'), jobparams.get('InternalJob')],
                     ])
    draw = request.GET['draw']
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('clients.status_clients')
def status(request, name):
    """ Client online status """
    clientres = getDIRClientinfo(request, name=name)
    if clientres is None:
        raise Http404()
    client = extractclientparams(clientres)
    if client.get('Disabledfordelete', None):
        # the job is disabled so redirect to defined jobs
        return redirect('clientsdefined')
    clientvmhost = False
    clientos = client.get('OS', None)
    if clientos in VMHOSTSOSTYPES:
        clientvmhost = True
    context = {'contentheader': 'Clients', 'apppath': ['Clients', 'Status', name], 'Client': client,
               'clientstatusdisplay': 1, 'clientvmhost': clientvmhost}
    updateMenuNumbers(request, context)
    updateClientsOSnrlist(request, context)
    return render(request, 'clients/status.html', context)


@perm_required('clients.status_clients')
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
            'Plugins': stat['plugins'].split(','),
        }
        context = {'Client': client}
    csname = 'bacula.client.' + name + '.status'
    cs = StatStatus.objects.filter(parid__name=csname).first()
    if cs is not None:
        cs.nvalue = st
        cs.save()
    return render(request, 'clients/statusheader.html', context)


@perm_required('clients.status_clients')
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
        data.append([jobid, job, starttime, ibadmin_render_joblevel(level, typ), files, bytes,
                     bytessec, [jobid, job, typ, status]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('clients.view_clients')
@perm_required('jobs.view_jobs')
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
                     ibadmin_render_joblevel(j.level, j.type), j.jobfiles, j.jobbytes,
                     ibadmin_render_jobstatus(j.jobstatus, j.joberrors),
                     [j.jobid, j.name, j.type, j.jobstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@any_perm_required('clients.add_clients', 'clients.change_clients', 'clients.add_node_clients',
                   'virtual.add_vmware', 'virtual.add_proxmox',
                   'virtual.add_xen', 'virtual.add_kvm', 'virtual.add_hyperv')
def clientsname(request):
    """
        JSON for client name
        when client name already exist then return false
    """
    client = request.GET.get('name', '').encode('ascii', 'ignore')
    return JsonResponse(checkClientname(client), safe=False)


@any_perm_required('clients.add_clients', 'clients.change_clients')
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


@perm_required('clients.add_clients')
def addstd(request):
    departments = getUserDepartmentsList(request)
    if request.method == 'GET':
        form = ClientStdForm(departments=departments)
        backurl = request.GET.get('b', None)
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Add', 'Standalone'], 'form': form}
        updateMenuNumbers(request, context)
        updateClientsOSnrlist(request, context)
        return render(request, 'clients/addstd.html', context)
    else:
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if add and not cancel:
            form = ClientStdForm(data=request.POST, departments=departments)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                address = form.cleaned_data['address']
                os = form.cleaned_data['os']
                defjob = form.cleaned_data['defjob']
                depart = form.cleaned_data['departments']
                # check if default department selected = No department in config
                if depart == ' ':
                    depart = None
                # create a Client resource and a Client component and all required resources
                with transaction.atomic():
                    createClient(name=name, address=address, os=os, department=depart, descr=descr)
                    if defjob:
                        createDefaultClientJob(request, name=name, clientos=os)
                directorreload()
                return redirect('clientsinfo', name)
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    if backurl is not None and backurl != '':
        return redirect(backurl)
    return redirect('clientsdefined')


@perm_required('clients.add_node_clients')
def clusterparam(request, clustername):
    clusternodes = ConfResource.objects.filter(confparameter__name='.ClusterName', confparameter__value=clustername)
    params = {}
    if clusternodes.count() > 0:
        params = {
            'os': ConfParameter.objects.filter(resid_id__in=clusternodes, name='.OS')[:1][0].value,
            'department': ConfParameter.objects.filter(resid_id__in=clusternodes, name='.Department')[:1][0].value,
        }
    return JsonResponse(params, safe=False)


@perm_required('clients.add_node_clients')
def addnode(request):
    departments = getUserDepartmentsList(request)
    cl = getDIRClientsClusters(request)
    clusters = (('', ''),)
    for c in cl:
        clusters += ((c, c),)
    if request.method == 'GET':
        form = ClientNodeForm(clusters=clusters, departments=departments)
        if len(clusters) == 0:
            form.fields['clusterlist'].disabled = True
        backurl = request.GET.get('b', None)
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Add', 'Cluster node'], 'form': form}
        updateMenuNumbers(request, context)
        updateClientsOSnrlist(request, context)
        return render(request, 'clients/addnode.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if add and not cancel:
            form = ClientNodeForm(data=request.POST, clusters=clusters, departments=departments)
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
                depart = form.cleaned_data['departments']
                # check if default department selected = No department in config
                if depart == ' ':
                    depart = None
                # create a Client resource and a Client component and all required resources
                with transaction.atomic():
                    createClientNode(name=name, address=address, os=os, descr=descr, cluster=cluster,
                                     clusterlist=clusterlist, department=depart)
                    if defjob:
                        createDefaultClientJob(request, name=name, clientos=os)
                directorreload()
                return redirect('clientsinfo', name)
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    if backurl is not None and backurl != '':
        return redirect(backurl)
    return redirect('clientsdefined')


@perm_required('clients.add_service_clients')
def addservice(request):
    departments = getUserDepartmentsList(request)
    cl = getDIRClientsClusters(request)
    if not len(cl):
        messages.info(request, "No clusters defined, so cannot add a cluster service. Add cluster node first.",
                      extra_tags="Info!")
        return redirect('clientsaddnode')
    clusters = ()
    for c in cl:
        clusters += ((c, c),)
    if request.method == 'GET':
        form = ClientServiceForm(clusters=clusters, departments=departments)
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Add', 'Cluster service'], 'form': form}
        updateMenuNumbers(request, context)
        updateClientsOSnrlist(request, context)
        return render(request, 'clients/addservice.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = ClientServiceForm(data=request.POST, clusters=clusters, departments=departments)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                address = form.cleaned_data['address']
                cluster = form.cleaned_data['cluster']
                defjob = form.cleaned_data['defjob']
                depart = form.cleaned_data['departments']
                # check if default department selected = No department in config
                if depart == ' ':
                    depart = None
                # create a Client resource and a Client component and all required resources
                with transaction.atomic():
                    createClientService(request, name=name, address=address, cluster=cluster, descr=descr, department=depart)
                    if defjob:
                        createDefaultClientJob(request, name=name, client=name)
                directorreload()
                return redirect('clientsinfo', name)
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('clientsdefined')


@perm_required('clients.add_alias_clients')
def addalias(request):
    departments = getUserDepartmentsList(request)
    cl = getDIRClientsNamesnAlias(request)
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        # initialclient = request.GET.get('c', None)
        form = ClientAliasForm(clients=clients, departments=departments)
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Add', 'Alias'], 'form': form}
        updateMenuNumbers(request, context)
        updateClientsOSnrlist(request, context)
        return render(request, 'clients/addalias.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = ClientAliasForm(data=request.POST, clients=clients, departments=departments)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                client = form.cleaned_data['client']
                defjob = form.cleaned_data['defjob']
                depart = form.cleaned_data['departments']
                # check if default department selected = No department in config
                if depart == ' ':
                    depart = None
                # create a Client resource based on a Client component
                with transaction.atomic():
                    createClientAlias(request, name=name, client=client, descr=descr, department=depart)
                    if defjob:
                        createDefaultClientJob(request, name=name, client=name)
                directorreload()
                return redirect('clientsinfo', name)
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('clientsdefined')


def makeinitialdata(name, client, backurl):
    data = {
        'name': name,
        'descr': client['Descr'],
        'address': client['Address'],
        'os': client['OS'],
        'client': client.get('Alias'),
        'cluster': client.get('ClusterService'),
        'departments': client.get('Department'),
        'backurl': backurl,
    }
    return data


@module_perms_required('clients')
def edit(request, name):
    backurl = request.GET.get('b', None)
    clientres = getDIRClientinfo(request, name=name)
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


@perm_required('clients.change_clients')
def editstd(request, name):
    clientres = getDIRClientinfo(request, name=name)
    if clientres is None:
        raise Http404()
    departments = getUserDepartmentsList(request)
    client = extractclientparams(clientres)
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        data = makeinitialdata(name, client, backurl)
        form = ClientStdForm(initial=data, departments=departments)
        form.fields['name'].disabled = True
        form.fields['os'].disabled = True
        if client.get('InternalClient'):
            form.fields['address'].disabled = True
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Edit', name], 'clientstatusdisplay': 1,
                   'Client': client, 'form': form, 'OS': client['OS']}
        updateMenuNumbers(request, context)
        updateClientsOSnrlist(request, context)
        return render(request, 'clients/editstd.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if backurl is None or backurl == '':
            backurl = 'clientsinfo'
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            post['os'] = client['OS']
            if client.get('InternalClient'):
                post['address'] = client['Address']
            data = makeinitialdata(name, client, backurl)
            form = ClientStdForm(data=post, initial=data, departments=departments)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... "
                    with transaction.atomic():
                        if 'descr' in form.changed_data:
                            # print "Update description"
                            updateClientDescr(request, name=name, descr=form.cleaned_data['descr'])
                        if 'address' in form.changed_data:
                            # print "Update address"
                            updateClientAddress(request, name=name, address=form.cleaned_data['address'])
                        if 'departments' in form.changed_data:
                            # update department
                            depart = form.cleaned_data['departments']
                            # check if default department selected = No department in config
                            if depart == ' ':
                                depart = None
                            updateClientDepartment(request, name=name, department=depart)
                        if 'os' in form.changed_data:
                            # print "Update OS"
                            # TODO: Unsupported right now. Do we really want to support this feature?
                            # updateClientOS(name=name, os=form.cleaned_data['os'])
                            pass
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect(backurl, name)


@perm_required('clients.change_clients')
def editservice(request, name):
    clientres = getDIRClientinfo(request, name=name)
    if clientres is None:
        raise Http404()
    client = extractclientparams(clientres)
    departments = getUserDepartmentsList(request)
    cl = getDIRClientsClusters(request)
    if not len(cl):
        messages.error(request, "No clusters defined! Report it to service!", extra_tags="Error!")
        return redirect('clientsaddnode')
    clusters = ()
    for c in cl:
        clusters += ((c, c),)
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        data = makeinitialdata(name, client, backurl)
        form = ClientServiceForm(initial=data, clusters=clusters, departments=departments)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Edit', name], 'clientstatusdisplay': 1,
                   'Client': client, 'form': form, 'OS': client['OS']}
        updateMenuNumbers(request, context)
        updateClientsOSnrlist(request, context)
        return render(request, 'clients/editservice.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if backurl is None or backurl == '':
            backurl = 'clientsinfo'
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            data = makeinitialdata(name, client, backurl)
            form = ClientServiceForm(data=post, initial=data, clusters=clusters, departments=departments)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... "
                    with transaction.atomic():
                        if 'descr' in form.changed_data:
                            # print "Update description"
                            updateClientDescr(request, name=name, descr=form.cleaned_data['descr'])
                        if 'address' in form.changed_data:
                            # print "Update address"
                            updateClientAddress(request, name=name, address=form.cleaned_data['address'])
                        if 'cluster' in form.changed_data:
                            # print "Update cluster"
                            updateClientCluster(request, name=name, cluster=form.cleaned_data['cluster'])
                        if 'departments' in form.changed_data:
                            # update department
                            depart = form.cleaned_data['departments']
                            updateClientDepartment(request, name=name, department=depart)
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect(backurl, name)


@perm_required('clients.change_clients')
def editalias(request, name):
    clientres = getDIRClientinfo(request, name=name)
    if clientres is None:
        raise Http404()
    client = extractclientparams(clientres)
    departments = getUserDepartmentsList(request)
    cl = getDIRClientsNamesnAlias(request)
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if client.get('Alias') is None:
        return redirect('clientsedit')
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        data = makeinitialdata(name, client, backurl)
        form = ClientAliasForm(initial=data, clients=clients, departments=departments)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Client', 'apppath': ['Clients', 'Edit', name], 'clientstatusdisplay': 1,
                   'Client': client, 'form': form}
        updateMenuNumbers(request, context)
        updateClientsOSnrlist(request, context)
        return render(request, 'clients/editalias.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if backurl is None or backurl == '':
            backurl = 'clientsinfo'
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            data = makeinitialdata(name, client, backurl)
            form = ClientAliasForm(data=post, initial=data, clients=clients, departments=departments)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... "
                    with transaction.atomic():
                        if 'descr' in form.changed_data:
                            # print "Update description"
                            updateClientDescr(request, name=name, descr=form.cleaned_data['descr'])
                        if 'client' in form.changed_data:
                            # print "Update alias"
                            updateClientAlias(request, name=name, alias=form.cleaned_data['client'])
                        if 'departments' in form.changed_data:
                            # update department
                            depart = form.cleaned_data['departments']
                            updateClientDepartment(request, name=name, department=depart)
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect(backurl, name)


@perm_required('clients.delete_clients')
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
