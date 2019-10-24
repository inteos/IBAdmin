# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.db import transaction, DatabaseError
from libs.client import *
from libs.vmhosts import *
from libs.menu import updateMenuNumbers
from libs.bconsole import *
from .forms import *
from config.conf import *
from config.models import ConfResource
from users.decorators import *


@perm_required('virtual.view_vmware')
def vcenterdefined(request):
    """ Defined VM Hosts table - list """
    context = {'contentheader': 'VMware vCenter Hosts', 'contentheadersmall': 'currently defined',
               'apppath': ['Virtual', 'VMware']}
    updateMenuNumbers(request, context)
    return render(request, 'vmhosts/vcenter.html', context)


@perm_required('virtual.view_vmware')
def vcenterdefineddata(request):
    """ JSON for vCenter hosts """
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    # order_col = cols[int(request.GET['order[0][column]'])]
    # order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    vcquery = getUservCenters(request)
    total = vcquery.count()
    if search != '':
        f = Q(name__icontains=search) | Q(description__icontains=search)
        filtered = vcquery.filter(f).count()
        vcenters = vcquery.filter(f).order_by('name')[offset:offset + limit]
    else:
        filtered = total
        vcenters = vcquery.order_by('name')[offset:offset + limit]
    data = []
    for vc in vcenters:
        dname, dcolor = getdepartmentlabel(vc.department)
        data.append([vc.name, vc.description, vc.address, [dcolor, dname], [vc.name]])
    draw = request.GET['draw']
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('virtual.view_vmware')
def vcenterclientdefineddata(request):
    """ JSON for Proxmox hosts """
    cols = [clientparamsnamekey, clientparamsdescrkey, clientparamsvcenterkey, clientparamsdepartkey,
            jobparamsstatuskey]
    (clientslist, total, filtered) = getUserDIRClientsList_filtered(request, cols=cols, os='vmware')
    data = []
    for clientres in clientslist:
        updateClientres(clientres)
        clientparams = extractclientparams(clientres)
        dname, dcolor = getdepartmentlabel(clientparams.get('Department'))
        data.append([clientparams['Name'], clientparams.get('Descr'),
                     clientparams.get('vCenterName'),
                     [dcolor, dname],
                     clientparams.get('Status'),
                     [clientparams['Name'], clientparams.get('InternalClient')],
                     ])
    draw = request.GET['draw']
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('virtual.view_proxmox')
def proxmoxdefined(request):
    """ Defined VM Hosts table - list """
    context = {'contentheader': 'Proxmox Hosts', 'contentheadersmall': 'currently defined',
               'apppath': ['Virtual', 'Proxmox']}
    updateMenuNumbers(request, context)
    return render(request, 'vmhosts/proxmox.html', context)


@perm_required('virtual.view_proxmox')
def proxmoxdefineddata(request):
    """ JSON for Proxmox hosts """
    cols = [clientparamsnamekey, clientparamsaddresskey, clientparamsdescrkey, clientparamsdepartkey,
            clientparamsclusterkey, jobparamsstatuskey]
    (clientslist, total, filtered) = getUserDIRClientsList_filtered(request, cols=cols, os='proxmox')
    data = []
    for clientres in clientslist:
        updateClientres(clientres)
        clientparams = extractclientparams(clientres)
        # print clientparams
        dname, dcolor = getdepartmentlabel(clientparams.get('Department'))
        data.append([clientparams['Name'], [clientparams.get('Address'), clientparams.get('Alias')],
                     clientparams.get('Descr'),
                     [dcolor, dname],
                     [clientparams.get('ClusterName'), clientparams.get('ClusterService')],
                     clientparams.get('Status'),
                     [clientparams['Name'], clientparams.get('InternalClient')],
                     ])
    draw = request.GET['draw']
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('virtual.list_proxmox')
def proxmoxvmlist(request, name=None):
    clientres = getDIRUserClientinfo(request, name=name)
    if clientres is None:
        raise Http404()
    vmlist, err = getproxmoxvmlist(name)
    jobsres = ConfResource.objects.filter(confparameter__name='Client', confparameter__value=name)
    objslist = ConfParameter.objects.filter(resid__in=jobsres, name='.Objsinclude')
    objvmlist = []
    for obj in objslist:
        for vm in obj.value.split(':'):
            objvmlist.append(vm)
    data = []
    if vmlist is not None:
        for vm in vmlist:
            bjlab = ['bg-gray', 'Unprotected']
            if vm['vmname'] in objvmlist or 'vmid=' + vm['vmid'] in objvmlist:
                bjlab = ['label-success', 'Defined']
            data.append([
                [vm['vmname'], name],
                [vm['vmid'], name],
                bjlab,
                vm['size'],
            ])
    context = {'data': data, 'err': err}
    return JsonResponse(context)


@perm_required('virtual.view_xen')
def xenserverdefined(request):
    """ Defined VM Hosts table - list """
    context = {'contentheader': 'XenServer Hosts', 'contentheadersmall': 'currently defined',
               'apppath': ['Virtual', 'XenServer']}
    updateMenuNumbers(request, context)
    return render(request, 'vmhosts/xenserver.html', context)


@perm_required('virtual.view_xen')
def xenserverdefineddata(request):
    """ JSON for XenServer hosts """
    cols = [clientparamsnamekey, clientparamsaddresskey, clientparamsdescrkey, clientparamsdepartkey,
            clientparamsclusterkey, jobparamsstatuskey]
    (clientslist, total, filtered) = getUserDIRClientsList_filtered(request, cols=cols, os='xen')
    data = []
    for clientres in clientslist:
        updateClientres(clientres)
        clientparams = extractclientparams(clientres)
        # print clientparams
        dname, dcolor = getdepartmentlabel(clientparams.get('Department'))
        data.append([clientparams['Name'], [clientparams.get('Address'), clientparams.get('Alias')],
                     clientparams.get('Descr'),
                     [dcolor, dname],
                     [clientparams.get('ClusterName'), clientparams.get('ClusterService')],
                     clientparams.get('Status'),
                     [clientparams['Name'], clientparams.get('InternalClient')],
                     ])
    draw = request.GET['draw']
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('virtual.list_xen')
def xenservervmlist(request, name=None):
    clientres = getDIRUserClientinfo(request, name=name)
    if clientres is None:
        raise Http404()
    vmlist, err = getxenservervmlist(name)
    jobsres = ConfResource.objects.filter(confparameter__name='Client', confparameter__value=name)
    objslist = ConfParameter.objects.filter(resid__in=jobsres, name='.Objsinclude')
    objvmlist = []
    for obj in objslist:
        for vm in obj.value.split(':'):
            objvmlist.append(vm)
    data = []
    if vmlist is not None:
        for vm in vmlist:
            bjlab = ['bg-gray', 'Unprotected']
            if vm['vmname'] in objvmlist or 'vmid=' + vm['vmid'] in objvmlist:
                bjlab = ['label-success', 'Defined']
            data.append([
                [vm['vmname'], name],
                [vm['vmid'], name],
                bjlab,
                vm['size'],
            ])
    context = {'data': data, 'err': err}
    return JsonResponse(context)


@perm_required('virtual.view_kvm')
def kvmhostdefined(request):
    """ Defined VM Hosts table - list """
    context = {'contentheader': 'XenServer Hosts', 'contentheadersmall': 'currently defined',
               'apppath': ['Virtual', 'KVM']}
    updateMenuNumbers(request, context)
    return render(request, 'vmhosts/kvmhost.html', context)


@perm_required('virtual.view_kvm')
def kvmhostdefineddata(request):
    """ JSON for KVM hosts """
    cols = [clientparamsnamekey, clientparamsaddresskey, clientparamsdescrkey, clientparamsdepartkey,
            clientparamsclusterkey, jobparamsstatuskey]
    (clientslist, total, filtered) = getUserDIRClientsList_filtered(request, cols=cols, os='kvm')
    data = []
    for clientres in clientslist:
        updateClientres(clientres)
        clientparams = extractclientparams(clientres)
        # print clientparams
        dname, dcolor = getdepartmentlabel(clientparams.get('Department'))
        data.append([clientparams['Name'], [clientparams.get('Address'), clientparams.get('Alias')],
                     clientparams.get('Descr'),
                     [dcolor, dname],
                     [clientparams.get('ClusterName'), clientparams.get('ClusterService')],
                     clientparams.get('Status'),
                     [clientparams['Name'], clientparams.get('InternalClient')],
                     ])
    draw = request.GET['draw']
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('virtual.add_vcenter')
def vcentername(request):
    """
        JSON for vcenter name
        when client name already exist then return false
    """
    name = request.GET.get('name', '').encode('ascii', 'ignore')
    check = True
    if vCenterHosts.objects.filter(name=name).count() == 1:
        check = False
    return JsonResponse(check, safe=False)


@perm_required('virtual.view_vmware')
def vcenterinfo(request, name):
    """ Client info """
    vcenter = get_object_or_404(vCenterHosts, name=name)
    clnr = ConfParameter.objects.filter(name='.vCenterName', value=name).count()
    context = {'contentheader': 'Virtual', 'apppath': ['Virtual', 'vCenter', 'Info'], 'vCenter': vcenter,
               'vcenterproxynr': clnr}
    updateMenuNumbers(request, context)
    return render(request, 'vmhosts/vcenterinfo.html', context)


@perm_required('virtual.add_vcenter')
def addvcenter(request):
    departments = getUserDepartmentsList(request)
    cl = getDIRClientsNames(request, os='rhel')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        form = vCenterForm(clients=clients, departments=departments)
        context = {'contentheader': 'Virtual', 'apppath': ['Virtual', 'Add', 'vCenter'], 'form': form}
        updateMenuNumbers(request, context)
        updateClientsOSnrlist(request, context)
        return render(request, 'vmhosts/addvcenter.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = vCenterForm(data=request.POST, clients=clients, departments=departments)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                encpass = getencpass(name, password)
                address = form.cleaned_data['address']
                url = form.cleaned_data['url']
                thumbprint = form.cleaned_data['thumbprint']
                clients = form.cleaned_data['client']
                depart = form.cleaned_data['departments']
                if depart in ['', ' ', '#']:
                    depart = None
                # create a Client resource and a Client component and all required resources
                with transaction.atomic():
                    vcenter = vCenterHosts(name=name, description=descr, username=username, password=encpass,
                                           address=address, url=url, thumbprint=thumbprint, department=depart)
                    vcenter.save()
                    for cl in clients:
                        clname = 'vmware-' + name + '-' + cl
                        createVMwareAlias(request, name=clname, client=cl, descr='VMware Proxy Client for ' + name,
                                          vcenter=name, department=depart)
                directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('vmsvcenterdefined')


@any_perm_required('virtual.add_vcenter', 'virtual.change_vcenter')
def getvcenterthumbprint(request):
    out = [False, None]
    if request.method == 'GET':
        url = request.GET.get('url')
        if url is not None:
            addr, port = urlparse(url)
            thp = getssltumbprint(addr, port)
            if thp is not None:
                out = [True, thp]
    return JsonResponse(out, safe=False)


@perm_required('virtual.add_vmware')
def addvcenterclient(request):
    departments = getUserDepartmentsList(request)
    clesx = getDIRClientsNamesesx(request)
    cl = getDIRClientsNames(request, os='rhel') + clesx
    clients = ()
    for c in cl:
        clients += ((c, c),)
    vcn = getUservCenters(request).order_by('name')
    vcenters = ()
    for vc in vcn:
        vcenters += ((vc.name, vc.name),)
    if request.method == 'GET':
        form = vCenterClientForm(clients=clients, vcenter=vcenters, departments=departments)
        context = {'contentheader': 'Virtual', 'apppath': ['Virtual', 'vCenter Assign'], 'form': form,
                   'vCenter': {'name': 'Assign'}}
        updateMenuNumbers(request, context)
        updateClientsOSnrlist(request, context)
        return render(request, 'vmhosts/assignvcenter.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = vCenterClientForm(data=request.POST, clients=clients, vcenter=vcenters, departments=departments)
            if form.is_valid():
                name = form.cleaned_data['vcenter']
                clients = form.cleaned_data['client']
                # create a Client resource and a Client component and all required resources
                try:
                    with transaction.atomic():
                        for cl in clients:
                            depart = form.cleaned_data['departments']
                            if cl in clesx:
                                clname = cl
                            else:
                                clname = 'vmware-' + name + '-' + cl
                            clientexist = ConfResource.objects.filter(name=clname, type__name='Client')
                            if len(clientexist) > 0:
                                updateDirClientVMware(clientres=clientexist[0], vcenter=name, department=depart)
                                messages.info(request,
                                              "VMware Proxy Client <b>%s</b> already exist. Parameters updated!" %
                                              clname,
                                              extra_tags='Updated!')
                            else:
                                createVMwareAlias(request, name=clname, client=cl,
                                                  descr='VMware Proxy Client for ' + name,
                                                  vcenter=name, department=depart)
                                messages.success(request, "VMware Proxy Client <b>%s</b> created." % clname,
                                                 extra_tags=' Success!')
                    directorreload()
                except DatabaseError as e:
                    messages.error(request, "Database error: %s" % e, extra_tags='Error')
            else:
                messages.error(request, "Cannot parse form: %s" % form.errors.as_data(), extra_tags='Error')
    return redirect('vmsvcenterdefined')


@perm_required('virtual.add_proxmox')
def addproxmox(request):
    departments = getUserDepartmentsList(request)
    if request.method == 'GET':
        form = VMhostForm(departments=departments)
        context = {'contentheader': 'Add VM Host', 'apppath': ['Virtual', 'Add', 'Proxmox'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'vmhosts/addproxmox.html', context)
    else:
        # print request.POST
        checkDIRProxmoxJobDef()
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = VMhostForm(data=request.POST, departments=departments)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                address = form.cleaned_data['address']
                defjob = form.cleaned_data['defjob']
                depart = form.cleaned_data['departments']
                # create a Client resource based on a Client component
                with transaction.atomic():
                    createClient(name=name, address=address, os='proxmox', descr=descr, department=depart)
                    if defjob:
                        checkDIRProxmoxJobDef()
                        createDefaultProxmoxJob(clientname=name)
                directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('vmsproxmoxdefined')


@perm_required('virtual.add_xen')
def addxenserver(request):
    departments = getUserDepartmentsList(request)
    if request.method == 'GET':
        # initialclient = request.GET.get('c', None)
        form = VMhostForm(departments=departments)
        context = {'contentheader': 'Add VM Host', 'apppath': ['Virtual', 'Add', 'XenServer'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'vmhosts/addxenserver.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = VMhostForm(data=request.POST, departments=departments)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                address = form.cleaned_data['address']
                defjob = form.cleaned_data['defjob']
                depart = form.cleaned_data['departments']
                # create a Client resource based on a Client component
                with transaction.atomic():
                    createClient(name=name, address=address, os='xen', descr=descr, department=depart)
                    if defjob:
                        checkDIRXenServerJobDef()
                        createDefaultXenServerJob(clientname=name)
                directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('vmsxenserverdefined')


@perm_required('virtual.add_kvm')
def addkvmhost(request):
    departments = getUserDepartmentsList(request)
    if request.method == 'GET':
        # initialclient = request.GET.get('c', None)
        form = VMhostForm(departments=departments)
        context = {'contentheader': 'Add VM Host', 'apppath': ['Virtual', 'Add', 'KVM'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'vmhosts/addkvmhost.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = VMhostForm(data=request.POST, departments=departments)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                address = form.cleaned_data['address']
                defjob = form.cleaned_data['defjob']
                depart = form.cleaned_data['departments']
                # create a Client resource based on a Client component
                with transaction.atomic():
                    createClient(name=name, address=address, os='kvm', descr=descr, department=depart)
                    if defjob:
                        checkDIRKVMJobDef()
                        createDefaultKVMJob(clientname=name)
                directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('vmskvmhostdefined')


@perm_required('virtual.change_vcenter')
def editvcenter(request, name):
    departments = getUserDepartmentsList(request)
    vcenter = get_object_or_404(vCenterHosts, name=name)
    data = {
        'name': vcenter.name,
        'descr': vcenter.description,
        'username': vcenter.username,
        'password': '***notchanged***',
        'address': vcenter.address,
        'url': vcenter.url,
        'thumbprint': vcenter.thumbprint,
        'client': [],
        'departments': vcenter.department,
    }
    if request.method == 'GET':
        form = vCenterForm(initial=data, departments=departments)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Virtual', 'apppath': ['Virtual', 'vCenter', 'Edit'], 'form': form,
                   'vCenter': vcenter}
        updateMenuNumbers(request, context)
        updateClientsOSnrlist(request, context)
        return render(request, 'vmhosts/editvcenter.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            form = vCenterForm(data=post, initial=data, departments=departments)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... "
                    with transaction.atomic():
                        if 'descr' in form.changed_data:
                            vcenter.description = form.cleaned_data['descr']
                        if 'username' in form.changed_data:
                            vcenter.username = form.cleaned_data['username']
                        if 'password' in form.changed_data:
                            password = form.cleaned_data['password']
                            encpass = getencpass(name, password)
                            vcenter.password = encpass
                        if 'address' in form.changed_data:
                            vcenter.address = form.cleaned_data['address']
                        if 'url' in form.changed_data:
                            vcenter.url = form.cleaned_data['url']
                        if 'thumbprint' in form.changed_data:
                            vcenter.thumbprint = form.cleaned_data['thumbprint']
                        if 'departments' in form.changed_data:
                            depart = form.cleaned_data['departments']
                            if depart in ['', ' ', '#']:
                                depart = None
                            vcenter.department = depart
                        vcenter.save()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('vmsvcenterdefined')


@perm_required('virtual.delete_vcenter')
def makedeletevcenter(request, name):
    vcenter = get_object_or_404(vCenterHosts, name=name)
    clients = ConfParameter.objects.filter(name='.vCenterName', value=name)
    with transaction.atomic():
        vcenter.delete()
        clients.delete()
    context = {'status': True}
    return JsonResponse(context, safe=False)
