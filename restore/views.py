# coding=utf-8
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
from time import sleep


# Create your views here.
def client(request, name):
    clientres = getDIRClientinfo(name=name)
    if clientres is None:
        raise Http404()
    updateClientres(clientres)
    clientp = extractclientparams(clientres)
    if clientp.get('Disabledfordelete', None):
        # the job is disabled so redirect to defined jobs
        return redirect('clientsdefined')
    jobslist = getDIRClientJobsList(client=name)
    jobdefined = []
    for jobres in jobslist:
        jobparams = extractjobparams(jobres)
        jobdefined.append(jobparams)
    context = {'contentheader': 'Restore', 'contentheadersmall': 'Client ' + name,
               'apppath': ['Restore', 'Client', name], 'Client': clientp, 'ClientJobsdefined': jobdefined}
    updateMenuNumbers(context)
    return render(request, 'restore/client.html', context)


def job(request, name):
    jobres = getDIRJobinfo(name=name)
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
    updateMenuNumbers(context)
    return render(request, 'restore/job.html', context)


def jobidre(request, jobid):
    jobp = getJobidinfo(jobid)
    if jobp is None:
        raise Http404()
    jobtype = getDIRJobType(name=jobp['Name'])
    backurl = request.GET.get('b', None)
    if jobtype == 'jd-backup-files':
        response = redirect('restorejobidfiles', jobid)
        if backurl is not None:
            response['Location'] += '?b=' + backurl
        return response
    if jobtype == 'jd-backup-catalog':
        response = redirect('restorejobidcatalog', jobid)
        if backurl is not None:
            response['Location'] += '?b=' + backurl
        return response
    raise Http404()


def jobidfiles(request, jobid):
    jobp = getJobidinfo(jobid)
    if job is None:
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
    cl = getDIRClientsNames()
    clients = ()
    for c in cl:
        clients += ((c, c),)
    client = jobp['Client']
    form = RestoreForm(clients=clients, initial={'client': client, 'restoreclient': client})
    context = {'contentheader': 'Restore', 'contentheadersmall': 'JobId: ' + str(jobp['JobId']),
               'apppath': ['Restore', 'JobId', jobp['JobId']], 'Job': jobp, 'Jobidsparams': jobidsparams,
               'Jobids': jobids, 'form': form, 'JobTypeURL': reverse('restoretree', args=[jobids, 'root'])}
    updateMenuNumbers(context)
    return render(request, 'restore/jobidfiles.html', context)


def jobidcatalog(request, jobid):
    jobp = getJobidinfo(jobid)
    if job is None:
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
    cl = getDIRClientsNames()
    clients = ()
    for c in cl:
        clients += ((c, c),)
    client = jobp['Client']
    form = RestoreForm(clients=clients, initial={'client': client, 'restoreclient': client})
    context = {'contentheader': 'Restore', 'contentheadersmall': 'JobId: ' + str(jobp['JobId']),
               'apppath': ['Restore', 'JobId', jobp['JobId']], 'Job': jobp, 'Jobidsparams': jobidsparams,
               'Jobids': jobids, 'form': form, 'JobTypeURL': reverse('restoretreecatalog', args=[jobids, 'root'])}
    updateMenuNumbers(context)
    return render(request, 'restore/jobidcatalog.html', context)


def updatecache(request, jobids):
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
        data.append([j.jobid, j.jobid, estr, [j.level, j.type], j.jobfiles, j.jobbytes])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def displayfs(request, name):
    jobres = getDIRJobinfo(name=name)
    if jobres is None:
        raise Http404()
    jobparams = extractjobparams(jobres)
    context = {}
    if jobparams['JobDefs'] == 'jd-backup-catalog':
        # special hack for Catalog Backup job
        context = {
            'DisplayFS': {'FS': catalogfs_getall()},
        }
    else:
        fsname = jobparams.get('FileSet', None)
        if fsname is not None:
            fsparams = getDIRFSparams(name=fsname)
            context = {
                'Include': fsparams[0],
                'Exclude': fsparams[1],
            }
    return render(request, 'restore/displayfs.html', context)


def displaytree(request, jobids, pathid):
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
                    'id': 'P'+f[0],
                    'icon': 'fa fa-hdd-o',
                    'text': n,
                    'state': 'closed',
                    'children': True,
                })
        if files is None or len(context) == 0:
            context.append({
                'id': 'NO',
                'icon': 'fa fa-calendar-times-o',
                'text': 'No files found',
                'state': 'disabled',
                'children': False,
            })
    else:
        pathpid = 0
        if len(pathid) > 1:
            # pathtype = pathid[0]
            pathpid = pathid[1:]
        dirs = bvfs_lsdirs_pathid(pathpid, jobids)
        if dirs is not None:
            for ff in dirs:
                f = ff.split('\t')
                n = f[5]
                if n == '.' or n == '..':
                    continue
                context.append({
                    'id': 'P'+f[0],
                    'icon': 'fa fa-folder-o',
                    'text': n,
                    'state': 'closed',
                    'children': True,
                })
        files = bvfs_lsfiles_pathid(pathpid, jobids)
        if files is not None:
            for ff in files:
                f = ff.split('\t')
                lstat = f[4]
                ltable = decodelstat(lstat)
                if getltable_islink(ltable):
                    icon = 'fa fa-external-link'
                    name = f[5]
                else:
                    icon = filetypeicon(f[5])
                    name = f[5] + ' <span class="badge bg-green">' + bytestext(getltable_size(ltable)) + '</span>'
                context.append({
                    'id': 'F'+f[1],
                    'icon': icon,
                    'text': name,
                    'state': 'closed',
                    'children': False,
                })
    return JsonResponse(context, safe=False)


def displaytreecatalog(request, jobids, pathid):
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
                'id': 'F' + f[1],
                'icon': catalogfs_get_icon('catsql'),
                'text': catalogfs_get_text('catsql') + ' <span class="label label-primary">' + bytestext(getltable_size(ltable)) + '</span>',
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
            context.append({
                'id': 'NO',
                'icon': 'fa fa-calendar-times-o',
                'text': 'No valid files found',
                'state': 'disabled',
                'children': False,
            })
    return JsonResponse(context, safe=False)


def preparerestore(request, jobids):
    if request.method == 'POST':
        cl = getDIRClientsNames()
        clients = ()
        for c in cl:
            clients += ((c, c),)
        form = RestoreForm(clients=clients, data=request.POST)
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
            # TODO ogarnąć dynamiczne numery tabel dla path, tak aby potem je przeczyścić, może unixtimestamp?
            pathtable = 'b20001'
            bvfs_restore_prepare(pathids=pathids, fileids=fileids, jobids=jobids, pathtable=pathtable)
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
                return JsonResponse([False, logi.logid], safe=False)
            rjobid = out[-1].split('=')[-1]
            # wait a moment to job to run
            sleep(2)
            # TODO istnieje szansa że jak zadanie restore zostanie zakolejkowane to nie będzie już potrzebować pathtable
            bvfs_restore_cleanup(pathtable=pathtable)
            return JsonResponse([True, rjobid], safe=False)
    return JsonResponse([False, 0], safe=False)
