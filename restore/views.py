# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.urls import reverse
from libs.client import *
from libs.job import *
from libs.menu import updateMenuNumbers
from libs.bconsole import *
from libs.restore import *
from libs.appdata import *
from config.conf import *
from django.db.models import Avg, Max, Min, Q
from datetime import *
from tags.templatetags.ibadtexts import bytestext
from .forms import *
from users.decorators import *
from libs.ibadmin import *
from time import sleep
import re


def client(request, name=None):
    if name is None:
        return redirect('clientsdefined')
    clientres = getDIRClientinfo(request, name=name)
    if clientres is None:
        raise Http404()
    updateClientres(clientres)
    clientp = extractclientparams(clientres)
    if clientp.get('Disabledfordelete', None):
        # the job is disabled so redirect to defined jobs
        return redirect('clientsdefined')
    jobslist = getDIRClientJobsList(request, client=name)
    jobdefined = []
    for jobres in jobslist:
        jobparams = extractjobparams(jobres)
        jobdefined.append(jobparams)
    context = {'contentheader': 'Restore', 'contentheadersmall': 'Client ' + name,
               'apppath': ['Restore', 'Client', name], 'Client': clientp, 'ClientJobsdefined': jobdefined}
    updateMenuNumbers(request, context)
    return render(request, 'restore/client.html', context)


def job(request, name=None):
    if name is None:
        return redirect('jobsdefined')
    jobres = getDIRJobinfo(request, name=name)
    if jobres is None:
        raise Http404()
    jobparams = extractjobparams(jobres)
    if jobparams.get('Disabledfordelete', None):
        # the job is disabled so redirect to defined jobs
        return redirect('jobsdefined')
    jobminmax = Job.objects.filter(name=name, jobstatus__in=['T', 'I']).aggregate(Max('endtime'), Min('endtime'))
    jobmin = jobminmax['endtime__min']
    if jobmin is None:
        jobmin = datetime.today()+timedelta(days=1)
    jobmax = jobminmax['endtime__max']
    if jobmax is None:
        jobmax = datetime.today()+timedelta(days=-1)
    context = {'contentheader': 'Restore', 'contentheadersmall': 'Job ' + name, 'apppath': ['Restore', 'Job', name],
               'Job': jobparams, 'jobmin': jobmin, 'jobmax': jobmax}
    updateMenuNumbers(request, context)
    return render(request, 'restore/job.html', context)


def jobidre(request, jobid=None):
    if jobid is None:
        raise Http404()
    jobp = getJobidinfo(request, jobid)
    if jobp is None:
        raise Http404()
    jobtype = getDIRJobType(name=jobp['Name'])
    backurl = request.GET.get('b', None)
    response = None
    if jobtype == 'jd-backup-files':
        response = redirect('restorejobidfiles', jobid)
    if jobtype == 'jd-backup-proxmox':
        response = redirect('restorejobidproxmox', jobid)
    if jobtype == 'jd-backup-xen':
        response = redirect('restorejobidxenserver', jobid)
    if jobtype == 'jd-backup-esx':
        response = redirect('restorejobidvmware', jobid)
    if jobtype == 'jd-backup-kvm':
        response = redirect('restorejobidkvm', jobid)
    if jobtype == 'jd-backup-catalog':
        response = redirect('restorejobidcatalog', jobid)
    if response is not None:
        if backurl is not None:
            response['Location'] += '?b=' + backurl
        return response
    raise Http404()


def jobidfiles(request, jobid=None):
    if jobid is None:
        raise Http404()
    jobp = getJobidinfo(request, jobid)
    if jobp is None:
        raise Http404()
    jobids = bvfs_get_jobids(jobid)
    if jobids is not None:
        jobidlist = [int(j) for j in jobids.split(',')]
        jobidsparams = []
        for j in jobidlist:
            jj = Job.objects.get(jobid=j)
            jobidsparams.append({
                'jobid': j,
                'level': jj.level,
            })
    else:
        jobids = 'unavl'
        jobidsparams = []
    cl = getDIRClientsNames(request)
    clients = ()
    for c in cl:
        clients += ((c, c),)
    client = jobp['Client']
    form = RestoreFilesForm(clients=clients, initial={'client': client, 'restoreclient': client})
    context = {'contentheader': 'Restore', 'contentheadersmall': 'JobId: ' + str(jobp['JobId']),
               'apppath': ['Restore', 'JobId', jobp['JobId']], 'Job': jobp, 'Jobidsparams': jobidsparams,
               'Jobids': jobids, 'form': form, 'JobTypeURL': reverse('restoretree', args=[jobids, 'root']),
               'JobTypeQueryURL': reverse('restoretree_rel', args=[jobids]),
               'JobTypePrepareURL': reverse('restoreprepare', args=[jobids])}
    updateMenuNumbers(request, context)
    return render(request, 'restore/jobidfiles.html', context)


def jobidproxmox(request, jobid=None):
    if jobid is None:
        raise Http404()
    jobp = getJobidinfo(request, jobid)
    if jobp is None:
        raise Http404()
    jobids = bvfs_get_jobids(jobid)
    if jobids is not None:
        jobidlist = [int(j) for j in jobids.split(',')]
        jobidsparams = []
        for j in jobidlist:
            jj = Job.objects.get(jobid=j)
            jobidsparams.append({
                'jobid': j,
                'level': jj.level,
            })
    else:
        jobids = 'unavl'
        jobidsparams = []
    cl = getDIRClientsNames(request, os='proxmox')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    clnt = jobp['Client']
    form = RestoreProxmoxForm(clients=clients,
                              initial={'client': clnt, 'restoreclient': clnt, 'where': '/tmp/bacula/restores'})
    context = {'contentheader': 'Restore', 'contentheadersmall': 'JobId: ' + str(jobp['JobId']),
               'apppath': ['Restore', 'JobId', jobp['JobId']], 'Job': jobp, 'Jobidsparams': jobidsparams,
               'Jobids': jobids, 'form': form, 'JobTypeURL': reverse('restoretreeproxmox', args=[jobids, 'root']),
               'JobTypeQueryURL': reverse('restoretreeproxmox_rel', args=[jobids]),
               'JobTypePrepareURL': reverse('restoreprepareproxmox', args=[jobids])}
    updateMenuNumbers(request, context)
    return render(request, 'restore/jobidproxmox.html', context)


def jobidxenserver(request, jobid=None):
    if jobid is None:
        raise Http404()
    jobp = getJobidinfo(request, jobid)
    if jobp is None:
        raise Http404()
    jobids = bvfs_get_jobids(jobid)
    if jobids is not None:
        jobidlist = [int(j) for j in jobids.split(',')]
        jobidsparams = []
        for j in jobidlist:
            jj = Job.objects.get(jobid=j)
            jobidsparams.append({
                'jobid': j,
                'level': jj.level,
            })
    else:
        jobids = 'unavl'
        jobidsparams = []
    cl = getDIRClientsNames(request, os='xen')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    clnt = jobp['Client']
    form = RestoreXenserverForm(clients=clients, initial={'client': clnt, 'restoreclient': clnt,
                                                          'where': '/tmp/bacula/restores'})
    context = {'contentheader': 'Restore', 'contentheadersmall': 'JobId: ' + str(jobp['JobId']),
               'apppath': ['Restore', 'JobId', jobp['JobId']], 'Job': jobp, 'Jobidsparams': jobidsparams,
               'Jobids': jobids, 'form': form, 'JobTypeURL': reverse('restoretreexenserver', args=[jobids, 'root']),
               'JobTypeQueryURL': reverse('restoretreexenserver_rel', args=[jobids]),
               'JobTypePrepareURL': reverse('restorepreparexenserver', args=[jobids])}
    updateMenuNumbers(request, context)
    return render(request, 'restore/jobidxenserver.html', context)


def jobidvmware(request, jobid=None):
    if jobid is None:
        raise Http404()
    jobp = getJobidinfo(request, jobid)
    if jobp is None:
        raise Http404()
    jobids = bvfs_get_jobids(jobid)
    if jobids is not None:
        jobidlist = [int(j) for j in jobids.split(',')]
        jobidsparams = []
        for j in jobidlist:
            jj = Job.objects.get(jobid=j)
            jobidsparams.append({
                'jobid': j,
                'level': jj.level,
            })
    else:
        jobids = 'unavl'
        jobidsparams = []
    cl = getDIRClientsNames(request, os='vmware')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    clnt = jobp['Client']
    form = RestoreVMwareForm(clients=clients, initial={'client': clnt, 'restoreclient': clnt,
                                                       'where': '/tmp/bacula/restores'})
    context = {'contentheader': 'Restore', 'contentheadersmall': 'JobId: ' + str(jobp['JobId']),
               'apppath': ['Restore', 'JobId', jobp['JobId']], 'Job': jobp, 'Jobidsparams': jobidsparams,
               'Jobids': jobids, 'form': form, 'JobTypeURL': reverse('restoretreevmware', args=[jobids, 'root']),
               'JobTypeQueryURL': reverse('restoretreevmware_rel', args=[jobids]),
               'JobTypePrepareURL': reverse('restorepreparevmware', args=[jobids])}
    updateMenuNumbers(request, context)
    return render(request, 'restore/jobidvmware.html', context)


def jobidcatalog(request, jobid=None):
    if jobid is None:
        raise Http404()
    jobp = getJobidinfo(request, jobid)
    if jobp is None:
        raise Http404()
    jobids = bvfs_get_jobids(jobid)
    if jobids is not None:
        jobidlist = [int(j) for j in jobids.split(',')]
        jobidsparams = []
        for j in jobidlist:
            jj = Job.objects.get(jobid=j)
            jobidsparams.append({
                'jobid': j,
                'level': jj.level,
            })
    else:
        jobids = 'unavl'
        jobidsparams = []
    cl = getDIRClientsNames(request)
    clients = ()
    for c in cl:
        clients += ((c, c),)
    client = jobp['Client']
    form = RestoreFilesForm(clients=clients, initial={'client': client, 'restoreclient': client})
    context = {'contentheader': 'Restore', 'contentheadersmall': 'JobId: ' + str(jobp['JobId']),
               'apppath': ['Restore', 'JobId', jobp['JobId']], 'Job': jobp, 'Jobidsparams': jobidsparams,
               'Jobids': jobids, 'form': form, 'JobTypeURL': reverse('restoretreecatalog', args=[jobids, 'root']),
               'JobTypeQueryURL': reverse('restoretree_rel', args=[jobids]),
               'JobTypePrepareURL': reverse('restoreprepare', args=[jobids])}
    updateMenuNumbers(request, context)
    return render(request, 'restore/jobidcatalog.html', context)


def jobidkvm(request, jobid=None):
    if jobid is None:
        raise Http404()
    jobp = getJobidinfo(request, jobid)
    if jobp is None:
        raise Http404()
    jobids = bvfs_get_jobids(jobid)
    if jobids is not None:
        jobidlist = [int(j) for j in jobids.split(',')]
        jobidsparams = []
        for j in jobidlist:
            jj = Job.objects.get(jobid=j)
            jobidsparams.append({
                'jobid': j,
                'level': jj.level,
            })
    else:
        jobids = 'unavl'
        jobidsparams = []
    cl = getDIRClientsNames(request)
    clients = ()
    for c in cl:
        clients += ((c, c),)
    clientname = jobp['Client']
    form = RestoreFilesForm(clients=clients, initial={'client': clientname, 'restoreclient': clientname})
    context = {'contentheader': 'Restore', 'contentheadersmall': 'JobId: ' + str(jobp['JobId']),
               'apppath': ['Restore', 'JobId', jobp['JobId']], 'Job': jobp, 'Jobidsparams': jobidsparams,
               'Jobids': jobids, 'form': form, 'JobTypeURL': reverse('restoretreekvm', args=[jobids, 'root']),
               'JobTypeQueryURL': reverse('restoretreekvm_rel', args=[jobids]),
               'JobTypePrepareURL': reverse('restoreprepare', args=[jobids])}
    updateMenuNumbers(request, context)
    return render(request, 'restore/jobidkvm.html', context)


def updatecache(request, jobids=None):
    if jobids is None:
        return JsonResponse(False, safe=False)
    bvfs_update(jobids)
    return JsonResponse(True, safe=False)


def historydata(request, name):
    """ JSON for jobs history datatable """
    cols = ['jobid', 'jobid', 'endtime', 'level', 'jobfiles', 'jobbytes']
    draw = request.GET['draw']
    datefilter = request.GET['datefilter']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Job.objects.filter(name=name, jobstatus__in=['T', 'I']).all().count()
    orderstr = order_dir + order_col
    if datefilter != '':
        datestart = datetime.strptime(datefilter, '%d-%m-%Y')
        dateend = datestart + timedelta(days=1)
        filtered = Job.objects.filter(name=name, jobstatus__in=['T', 'I'], endtime__range=[datestart, dateend]).count()
        query = Job.objects.filter(name=name, jobstatus__in=['T', 'I'], endtime__range=[datestart, dateend]).order_by(orderstr, '-jobid')[
                offset:offset + limit]
    elif search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        filtered = Job.objects.filter(Q(name=name, jobstatus__in=['T', 'I']), f).count()
        query = Job.objects.filter(Q(name=name, jobstatus__in=['T', 'I']), f).order_by(orderstr, '-jobid')[offset:offset + limit]
    else:
        filtered = total
        query = Job.objects.filter(name=name, jobstatus__in=['T', 'I']).all().order_by(
            orderstr, '-jobid')[offset:offset + limit]
    data = []
    for j in query:
        if j.endtime is None:
            estr = None
        else:
            estr = j.endtime.strftime('%Y-%m-%d %H:%M:%S')
        data.append([j.jobid, j.jobid, estr, ibadmin_render_joblevel(j.level, j.type), j.jobfiles, j.jobbytes])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def displayfs(request, name=None):
    if name is None:
        raise Http404()
    jobres = getDIRJobinfo(request, name=name)
    if jobres is None:
        raise Http404()
    jobparams = extractjobparams(jobres)
    if jobparams['JobDefs'] == 'jd-backup-catalog':
        fsdata = catalog_fsdata()
    elif jobparams['JobDefs'] == 'jd-backup-proxmox':
        fsdata = proxmox_fsdata(jobparams)
    elif jobparams['JobDefs'] == 'jd-backup-xen':
        fsdata = xenserver_fsdata(jobparams)
    elif jobparams['JobDefs'] == 'jd-backup-esx':
        fsdata = vmware_fsdata(jobparams)
    else:
        fsdata = files_fsdata(jobparams)
    context = {'FSData': fsdata}
    return render(request, 'restore/displayfs.html', context)


def updatecontextnodata(context, text='No valid files found'):
    context.append({
        'id': 'NO',
        'icon': 'fa fa-calendar-times-o',
        'text': text,
        'state': 'disabled',
        'children': False,
    })


def displaytree(request, jobids, pathid=None):
    if pathid is None:
        raise Http404()
    context = []
    if pathid == 'root':
        if jobids == 'unavl':
            files = None
        else:
            files = bvfs_lsdirs_root(jobids)
        if files is not None:
            for ff in files:
                f = ff.split('\t')
                n = f[5]
                if n == '.' or n == '..':
                    continue
                context.append({
                    'id': 'P' + f[0],
                    'icon': 'fa fa-hdd-o',
                    'text': n,
                    'state': 'closed',
                    'children': True,
                })
        if files is None or len(context) == 0:
            updatecontextnodata(context)
    else:
        pathpid = 0
        if len(pathid) > 1:
            # pathtype = pathid[0]
            pathpid = pathid[1:]
        dirs = bvfs_lsdirs_pathid(pathpid, jobids)
        if dirs is not None:
            for ff in dirs:
                try:
                    f = ff.split('\t')
                except UnicodeDecodeError:
                    f = ff.decode('utf-8').split('\t')
                n = f[5]
                if n == '.' or n == '..':
                    continue
                context.append({
                    'id': 'P' + f[0],
                    'icon': dirtypeicon(n),
                    'text': n,
                    'state': 'closed',
                    'children': True,
                })
        files = bvfs_lsfiles_pathid(pathpid, jobids)
        if files is not None:
            for ff in files:
                try:
                    f = ff.split('\t')
                except UnicodeDecodeError:
                    f = ff.decode('utf-8').split('\t')
                lstat = f[4]
                ltable = decodelstat(lstat)
                if getltable_islink(ltable):
                    icon = 'fa fa-external-link'
                    n = f[5]
                else:
                    n = f[5]
                    icon = filetypeicon(n)
                    n = n + ' <span class="badge bg-green">' + bytestext(getltable_size(ltable)) + '</span>'
                context.append({
                    'id': 'F' + f[2],
                    'icon': icon,
                    'text': n,
                    'state': 'closed',
                    'children': False,
                })
    return JsonResponse(context, safe=False)


def displaytreecatalog(request, jobids, pathid=None):
    if pathid is None:
        raise Http404()
    context = []
    if pathid == 'root':
        if jobids == 'unavl':
            fcat = None
        else:
            fcat = bvfs_lsfiles_path('/opt/bacula/working/', jobids)
        if fcat is not None:
            f = fcat[0].split('\t')
            lstat = f[4]
            ltable = decodelstat(lstat)
            context.append({
                'id': 'F' + f[2],
                'icon': catalogfs_get_icon('catsql'),
                'text': catalogfs_get_text('catsql') + ' <span class="badge bg-aqua">' + bytestext(getltable_size(ltable)) + '</span>',
                'state': 'closed',
                'children': False,
            })
            dirs = bvfs_lsdirs_path('/opt/bacula/', jobids)
            if dirs is not None:
                for ff in dirs:
                    f = ff.split('\t')
                    n = f[5]
                    if n == 'bsr/':
                        context.append({
                            'id': 'P' + f[0],
                            'icon': catalogfs_get_icon('bsr'),
                            'text': catalogfs_get_text('bsr'),
                            'state': 'closed',
                            'children': True,
                        })
                    if n == 'scripts/':
                        context.append({
                            'id': 'P' + f[0],
                            'icon': catalogfs_get_icon('scripts'),
                            'text': catalogfs_get_text('scripts'),
                            'state': 'closed',
                            'children': True,
                        })
        else:
            updatecontextnodata(context)
    return JsonResponse(context, safe=False)


def displaytreeproxmox(request, jobids, pathid=None):
    if pathid is None:
        raise Http404()
    context = []
    if pathid == 'root':
        if jobids == 'unavl':
            qemuvms = None
            lxcvms = None
        else:
            qemuvms = bvfs_lsdirs_path('/@proxmox/qm/', jobids)
            lxcvms = bvfs_lsdirs_path('/@proxmox/lxc/', jobids)
        if qemuvms is not None:
            for vm in qemuvms:
                f = vm.split('\t')
                vmname = f[5].replace('/', '')
                if vmname == '.' or vmname == '..':
                    continue
                context.append({
                    'id': 'Q' + f[0],
                    'icon': proxmoxfs_get_icon('qemu'),
                    'text': vmname,
                    'state': 'closed',
                    'children': True,
                })
        if lxcvms is not None:
            for vm in lxcvms:
                f = vm.split('\t')
                vmname = f[5].replace('/', '')
                if vmname == '.' or vmname == '..':
                    continue
                context.append({
                    'id': 'C' + f[0],
                    'icon': proxmoxfs_get_icon('lxc'),
                    'text': vmname,
                    'state': 'closed',
                    'children': True,
                })
        if qemuvms is None and lxcvms is None:
            updatecontextnodata(context)
    else:
        pathpid = 0
        pathtype = ''
        if len(pathid) > 1:
            pathtype = pathid[0]
            pathpid = pathid[1:]
        if pathtype == 'Q':
            vms = bvfs_lsfiles_pathid(pathpid, jobids)
            if vms is not None:
                for vm in vms:
                    f = vm.split('\t')
                    lstat = f[4]
                    ltable = decodelstat(lstat)
                    vmid = f[5].replace('.vma', '')
                    context.append({
                        'id': 'q' + f[1],
                        'icon': proxmoxfs_get_icon('qemu'),
                        'text': vmid + ' <span class="badge bg-green">' + bytestext(getltable_size(ltable)) + '</span>',
                        'state': 'closed',
                        'children': False,
                    })
        if pathtype == 'C':
            confid = ''
            vms = bvfs_lsfiles_pathid(pathpid, jobids)
            if vms is not None:
                for vm in vms:
                    f = vm.split('\t')
                    if f[5].endswith('.conf'):
                        confid = f[2]
                    if f[5].endswith('.tar'):
                        lstat = f[4]
                        ltable = decodelstat(lstat)
                        vmid = f[5].replace('.tar', '')
                        context.append({
                            'id': 'c' + f[2] + ':' + confid,
                            'icon': proxmoxfs_get_icon('lxc'),
                            'text': vmid + ' <span class="badge bg-aqua">' + bytestext(getltable_size(ltable)) + '</span>',
                            'state': 'closed',
                            'children': False,
                        })
    return JsonResponse(context, safe=False)


def displaytreexenserver(request, jobids, pathid=None):
    if pathid is None:
        raise Http404()
    context = []
    if pathid == 'root':
        if jobids == 'unavl':
            vms = None
        else:
            vms = bvfs_lsdirs_path('/@xen/', jobids)
        if vms is not None:
            for vm in vms:
                f = vm.split('\t')
                vmname = f[5].replace('/', '')
                if vmname == '.' or vmname == '..':
                    continue
                context.append({
                    'id': 'V' + f[0],
                    'icon': 'fa fa-desktop',
                    'text': vmname,
                    'state': 'closed',
                    'children': True,
                })
        if vms is None:
            updatecontextnodata(context)
    else:
        pathpid = 0
        pathtype = ''
        if len(pathid) > 1:
            pathtype = pathid[0]
            pathpid = pathid[1:]
        if pathtype == 'V':
            vms = bvfs_lsfiles_pathid(pathpid, jobids)
            if vms is not None:
                for vm in vms:
                    f = vm.split('\t')
                    lstat = f[4]
                    ltable = decodelstat(lstat)
                    vmid = f[5].replace('.xva', '')
                    context.append({
                        'id': 'q' + f[1],
                        'icon': 'fa fa-cube',
                        'text': vmid + ' <span class="badge bg-green">' + bytestext(getltable_size(ltable)) + '</span>',
                        'state': 'closed',
                        'children': False,
                    })
    return JsonResponse(context, safe=False)


def displaytreevmware(request, jobids, pathid=None):
    if pathid is None:
        raise Http404()
    context = []
    if pathid == 'root':
        if jobids == 'unavl':
            vms = None
        else:
            vms = bvfs_lsfiles_path('/@vsphere/', jobids)
        if vms is not None:
            for vm in vms:
                f = vm.split('\t')
                v = f[5].split('-')
                vmdir = v[0] + '-' + v[1]
                vmname = '-'.join(v[2:]) + ' (' + vmdir + ')'
                dvms = bvfs_lsdirs_path('/@vsphere/'+vmdir+'/', jobids)
                rd = 'L' + f[1]
                for vmd in dvms:
                    fd = vmd.split('\t')
                    if fd[5] == '.':
                        rd = 'V' + fd[0] + rd
                context.append({
                    'id': rd,
                    'icon': 'fa fa-desktop',
                    'text': vmname,
                    'state': 'closed',
                    'children': True,
                })
        if vms is None:
            updatecontextnodata(context)
    else:
        pathpid = 0
        pathtype = ''
        label = ''
        if pathid is not None and len(pathid) > 1:
            ltab = pathid.split('L')
            pathtype = ltab[0][0]
            pathpid = ltab[0][1:]
            if len(ltab) > 1:
                label = 'L' + ltab[1]
        if pathtype == 'V':
            vms = bvfs_lsfiles_pathid(pathpid, jobids)
            if vms is not None:
                for vm in vms:
                    f = vm.split('\t')
                    if f[5].endswith('.bvmdk') or f[5].endswith('.ovf'):
                        lstat = f[4]
                        ltable = decodelstat(lstat)
                        icon = 'fa fa-database'
                        if f[5].endswith('.ovf'):
                            icon = 'fa fa-cubes'
                        context.append({
                            'id': 'V' + str(pathpid) + 'F' + f[1] + label,
                            'icon': icon,
                            'text': f[5] + ' <span class="badge bg-green">' + bytestext(getltable_size(ltable)) + '</span>',
                            'state': 'closed',
                            'children': False,
                        })
    return JsonResponse(context, safe=False)


def displaytreekvm(request, jobids, pathid=None):
    if pathid is None:
        raise Http404()
    context = []
    if pathid == 'root':
        if jobids == 'unavl':
            vms = None
        else:
            vms = bvfs_lsdirs_path('/', jobids)
        if vms is not None:
            for ff in vms:
                f = ff.split('\t')
                n = f[5]
                if n == '.' or n == '..':
                    continue
                context.append({
                    'id': 'V' + f[0],
                    'icon': 'fa fa-desktop',
                    'text': n.replace('/', ''),
                    'state': 'closed',
                    'children': True,
                })
        if vms is None or len(context) == 0:
            updatecontextnodata(context)
    elif pathid.startswith('V'):
        pathpid = 0
        if len(pathid) > 1:
            pathpid = pathid[1:]
        files = bvfs_lsdirs_pathid(pathpid, jobids)
        pattern = re.compile(r'^[a-zA-Z]:')
        if files is not None:
            for ff in files:
                try:
                    f = ff.split('\t')
                except UnicodeDecodeError:
                    f = ff.decode('utf-8').split('\t')
                n = f[5]
                if n == '.' or n == '..':
                    continue
                if pattern.match(n):
                    context.append({
                        'id': 'P' + f[0],
                        'icon': 'fa fa-hdd-o',
                        'text': n,
                        'state': 'closed',
                        'children': True,
                    })
            if len(context) == 0:
                context.append({
                    'id': 'P' + pathpid,
                    'icon': 'fa fa-hdd-o',
                    'text': '/',
                    'state': 'closed',
                    'children': True,
                })
    else:
        pathpid = 0
        if len(pathid) > 1:
            pathpid = pathid[1:]
        dirs = bvfs_lsdirs_pathid(pathpid, jobids)
        if dirs is not None:
            for ff in dirs:
                try:
                    f = ff.split('\t')
                except UnicodeDecodeError:
                    f = ff.decode('utf-8').split('\t')
                n = f[5]
                if n == '.' or n == '..':
                    continue
                context.append({
                    'id': 'P' + f[0],
                    'icon': dirtypeicon(n),
                    'text': n,
                    'state': 'closed',
                    'children': True,
                })
        files = bvfs_lsfiles_pathid(pathpid, jobids)
        if files is not None:
            for ff in files:
                try:
                    f = ff.split('\t')
                except UnicodeDecodeError:
                    f = ff.decode('utf-8').split('\t')
                lstat = f[4]
                ltable = decodelstat(lstat)
                if getltable_islink(ltable):
                    icon = 'fa fa-external-link'
                    n = f[5]
                else:
                    n = f[5]
                    icon = filetypeicon(n)
                    n = n + ' <span class="badge bg-green">' + bytestext(getltable_size(ltable)) + '</span>'
                context.append({
                    'id': 'F' + f[2],
                    'icon': icon,
                    'text': n,
                    'state': 'closed',
                    'children': False,
                })
    return JsonResponse(context, safe=False)


def preparerestorefiles(request, jobids):
    if request.method == 'POST':
        cl = getDIRClientsNames(request)
        clients = ()
        for c in cl:
            clients += ((c, c),)
        form = RestoreFilesForm(clients=clients, data=request.POST)
        if form.is_valid():
            # print form.cleaned_data
            paths = []
            files = []
            for f in form.cleaned_data['rselected'].split(','):
                if f.startswith('P'):
                    paths.append(f[1:])
                if f.startswith('F'):
                    files.append(f[1:])
            pathids = ','.join(paths)
            fileids = ','.join(files)
            # print "P:", pathids, "F:", fileids
            status, pathtable, out = bvfs_restore_prepare(pathids=pathids, fileids=fileids, jobids=jobids)
            if not status:
                logi = Log(jobid_id=0, logtext='Preparing Restore problem: "' + '\n'.join(out))
                logi.save()
                bvfs_restore_cleanup(pathtable)
                return JsonResponse([False, logi.logid], safe=False)
            cl = form.cleaned_data['client']
            restoreclient = form.cleaned_data['restoreclient']
            where = form.cleaned_data['where']
            replace = form.cleaned_data['replace']
            comment = form.cleaned_data['comment']
            # do restore job
            out = doRestore(cl, restoreclient, where=where, replace=replace, comment=comment, pathtable=pathtable)
            if 'Job queued. JobId=' not in out[-1]:
                # we have a problem making restore log it
                logi = Log(jobid_id=0, logtext='Executing Restore problem: "' + '\n'.join(out))
                logi.save()
                bvfs_restore_cleanup(pathtable)
                return JsonResponse([False, logi.logid], safe=False)
            rjobid = out[-1].split('=')[-1]
            # wait a moment to job to run
            sleep(2)
            bvfs_restore_cleanup(pathtable)
            return JsonResponse([True, rjobid], safe=False)
    return JsonResponse([False, 0], safe=False)


def preparerestoreproxmox(request, jobids):
    if request.method == 'POST':
        cl = getDIRClientsNames(request, os='proxmox')
        clients = ()
        for c in cl:
            clients += ((c, c),)
        form = RestoreProxmoxForm(clients=clients, data=request.POST)
        if form.is_valid():
            # print form.cleaned_data
            paths = []
            files = []
            for f in form.cleaned_data['rselected'].split(','):
                if f.startswith('C') or f.startswith('Q'):
                    paths.append(f[1:])
                if f.startswith('c'):
                    vmf = f[1:].split(':')
                    files.append(vmf[0])
                    files.append(vmf[1])
                if f.startswith('q'):
                    files.append(f[1:])
            pathids = ','.join(paths)
            fileids = ','.join(files)
            status, pathtable, out = bvfs_restore_prepare(pathids=pathids, fileids=fileids, jobids=jobids)
            if not status:
                logi = Log(jobid_id=0, logtext='Preparing Restore problem: "' + '\n'.join(out))
                logi.save()
                bvfs_restore_cleanup(pathtable)
                return JsonResponse([False, logi.logid], safe=False)
            robjid = getrestoreobjectid(jobids)
            cl = form.cleaned_data['client']
            restoreclient = form.cleaned_data['restoreclient']
            comment = form.cleaned_data['comment']
            proxmoxstorage = form.cleaned_data['proxmoxstorage']
            proxmoxpool = form.cleaned_data['proxmoxpool']
            conffile = None
            if proxmoxstorage != '' or proxmoxpool != '':
                conffile = getpluginconffilename()
                with open(conffile, 'w') as f:
                    if proxmoxstorage != '':
                        f.write(str('storage="' + proxmoxstorage + '"\n'))
                    if proxmoxpool != '':
                        f.write(str('pool="' + proxmoxpool + '"\n'))
                    f.close()
            # do restore job
            if form.cleaned_data['localrestore']:
                where = form.cleaned_data['where']
                replace = form.cleaned_data['replace']
                out = doRestore(cl, restoreclient, where=where, replace=replace, comment=comment, pathtable=pathtable)
            else:
                out = doRestore(cl, restoreclient, comment=comment, pathtable=pathtable, conffile=conffile,
                                robjid=robjid)
            if 'Job queued. JobId=' not in out[-1]:
                # we have a problem making restore log it
                logi = Log(jobid_id=0, logtext='Executing Restore problem: "' + '\n'.join(out))
                logi.save()
                bvfs_restore_cleanup(pathtable)
                return JsonResponse([False, logi.logid], safe=False)
            rjobid = out[-1].split('=')[-1]
            # wait a moment to job to run
            sleep(2)
            bvfs_restore_cleanup(pathtable)
            return JsonResponse([True, rjobid], safe=False)
    return JsonResponse([False, 0], safe=False)


def preparerestorevmware(request, jobids):
    if request.method == 'POST':
        cl = getDIRClientsNames(request, os='vmware')
        clients = ()
        for c in cl:
            clients += ((c, c),)
        form = RestoreVMwareForm(clients=clients, data=request.POST)
        if form.is_valid():
            # print form.cleaned_data
            paths = []
            files = []
            for f in form.cleaned_data['rselected'].split(','):
                vl = f.split('L')
                if form.cleaned_data['localrestore'] and len(vl) > 1:
                    files.append(vl[1])
                vd = vl[0].split('F')
                if len(vd) == 1:
                    paths.append(vd[0][1:])
                elif form.cleaned_data['localrestore']:
                    files.append(vd[1])
                else:
                    paths.append(vd[0][1:])
            pathids = ','.join(paths)
            fileids = ','.join(files)
            status, pathtable, out = bvfs_restore_prepare(pathids=pathids, fileids=fileids, jobids=jobids)
            if not status:
                logi = Log(jobid_id=0, logtext='Preparing Restore problem: "' + '\n'.join(out))
                logi.save()
                bvfs_restore_cleanup(pathtable)
                return JsonResponse([False, logi.logid], safe=False)
            robjid = getrestoreobjectid(jobids)
            cl = form.cleaned_data['client']
            restoreclient = form.cleaned_data['restoreclient']
            comment = form.cleaned_data['comment']
            datastore = form.cleaned_data['datastore']
            restoreesx = form.cleaned_data['restoreesx']
            conffile = None
            if datastore != '' or restoreesx != '':
                conffile = getpluginconffilename()
                with open(conffile, 'w') as f:
                    if datastore != '':
                        f.write(str('datastore="' + datastore + '"\n'))
                    if restoreesx != '':
                        f.write(str('restore_host="' + restoreesx + '"\n'))
                    f.close()
            # do restore job
            if form.cleaned_data['localrestore']:
                where = form.cleaned_data['where']
                replace = form.cleaned_data['replace']
                out = doRestore(cl, restoreclient, where=where, replace=replace, comment=comment, pathtable=pathtable)
            else:
                out = doRestore(cl, restoreclient, comment=comment, pathtable=pathtable, conffile=conffile,
                                robjid=robjid)
            if 'Job queued. JobId=' not in out[-1]:
                # we have a problem making restore log it
                logi = Log(jobid_id=0, logtext='Executing Restore problem: "' + '\n'.join(out))
                logi.save()
                bvfs_restore_cleanup(pathtable)
                return JsonResponse([False, logi.logid], safe=False)
            rjobid = out[-1].split('=')[-1]
            # wait a moment to job to run
            sleep(2)
            bvfs_restore_cleanup(pathtable)
            return JsonResponse([True, rjobid], safe=False)
    return JsonResponse([False, 0], safe=False)


def preparerestorexenserver(request, jobids):
    if request.method == 'POST':
        cl = getDIRClientsNames(request, os='xen')
        clients = ()
        for c in cl:
            clients += ((c, c),)
        form = RestoreXenserverForm(clients=clients, data=request.POST)
        if form.is_valid():
            # print form.cleaned_data
            paths = []
            files = []
            for f in form.cleaned_data['rselected'].split(','):
                if f.startswith('V'):
                    paths.append(f[1:])
                if f.startswith('q'):
                    files.append(f[1:])
            pathids = ','.join(paths)
            fileids = ','.join(files)
            status, pathtable, out = bvfs_restore_prepare(pathids=pathids, fileids=fileids, jobids=jobids)
            if not status:
                logi = Log(jobid_id=0, logtext='Preparing Restore problem: "' + '\n'.join(out))
                logi.save()
                bvfs_restore_cleanup(pathtable)
                return JsonResponse([False, logi.logid], safe=False)
            robjid = getrestoreobjectid(jobids)
            cl = form.cleaned_data['client']
            restoreclient = form.cleaned_data['restoreclient']
            comment = form.cleaned_data['comment']
            xenstorage = form.cleaned_data['xenstorage']
            xenpreserve = form.cleaned_data['xenpreserve']
            conffile = None
            if xenstorage != '' or xenpreserve:
                conffile = getpluginconffilename()
                with open(conffile, 'w') as f:
                    if xenstorage != '':
                        f.write(str('storage_res="' + xenstorage + '"\n'))
                    if xenpreserve:
                        f.write(str('preserve=yes\n'))
                    f.close()
            # do restore job
            if form.cleaned_data['localrestore']:
                where = form.cleaned_data['where']
                replace = form.cleaned_data['replace']
                out = doRestore(cl, restoreclient, where=where, replace=replace, comment=comment, pathtable=pathtable)
            else:
                out = doRestore(cl, restoreclient, comment=comment, pathtable=pathtable, conffile=conffile,
                                robjid=robjid)
            if 'Job queued. JobId=' not in out[-1]:
                # we have a problem making restore log it
                logi = Log(jobid_id=0, logtext='Executing Restore problem: "' + '\n'.join(out))
                logi.save()
                bvfs_restore_cleanup(pathtable)
                return JsonResponse([False, logi.logid], safe=False)
            rjobid = out[-1].split('=')[-1]
            # wait a moment to job to run
            sleep(2)
            bvfs_restore_cleanup(pathtable)
            return JsonResponse([True, rjobid], safe=False)
    return JsonResponse([False, 0], safe=False)


def preparerestorekvm(request, jobids):
    if request.method == 'POST':
        cl = getDIRClientsNames(request)
        clients = ()
        for c in cl:
            clients += ((c, c),)
        form = RestoreFilesForm(clients=clients, data=request.POST)
        if form.is_valid():
            # print form.cleaned_data
            paths = []
            files = []
            for f in form.cleaned_data['rselected'].split(','):
                if f.startswith('P'):
                    paths.append(f[1:])
                if f.startswith('F'):
                    files.append(f[1:])
            pathids = ','.join(paths)
            fileids = ','.join(files)
            # print "P:", pathids, "F:", fileids
            status, pathtable, out = bvfs_restore_prepare(pathids=pathids, fileids=fileids, jobids=jobids)
            if not status:
                logi = Log(jobid_id=0, logtext='Preparing Restore problem: "' + '\n'.join(out))
                logi.save()
                bvfs_restore_cleanup(pathtable)
                return JsonResponse([False, logi.logid], safe=False)
            cl = form.cleaned_data['client']
            restoreclient = form.cleaned_data['restoreclient']
            where = form.cleaned_data['where']
            replace = form.cleaned_data['replace']
            comment = form.cleaned_data['comment']
            # do restore job
            out = doRestore(cl, restoreclient, where=where, replace=replace, comment=comment, pathtable=pathtable)
            if 'Job queued. JobId=' not in out[-1]:
                # we have a problem making restore log it
                logi = Log(jobid_id=0, logtext='Executing Restore problem: "' + '\n'.join(out))
                logi.save()
                bvfs_restore_cleanup(pathtable)
                return JsonResponse([False, logi.logid], safe=False)
            rjobid = out[-1].split('=')[-1]
            # wait a moment to job to run
            sleep(2)
            bvfs_restore_cleanup(pathtable)
            return JsonResponse([True, rjobid], safe=False)
    return JsonResponse([False, 0], safe=False)

