# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.db import transaction
from libs.job import *
from libs.menu import updateMenuNumbers
from libs.appdata import catalogfs_getall
from libs.bconsole import *
from .models import *
from .forms import *
from config.conf import *
from tasks.models import *
from tags.templatetags.ibadtexts import bytestext
from libs.restore import *
import time
import os
import re


def defined(request):
    """ Defined Jobs table - list """
    context = {'contentheader': 'Jobs', 'contentheadersmall': 'currently defined', 'apppath': ['Jobs', 'Defined']}
    updateMenuNumbers(context)
    return render(request, 'jobs/defined.html', context)


def defineddata(request):
    """ JSON for warning jobs datatable """
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    # order_col = cols[int(request.GET['order[0][column]'])]
    # order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    (jobslist, total, filtered) = getDIRJobsListfiltered(search=search, offset=offset, limit=limit)
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
        data.append([jobparams['Name'], jobparams.get('Client'),
                     [jobparams.get('Enabled'), scheduletext], pooltext, jobparams.get('Storage'),
                     [jobparams.get('Level'), jobparams.get('Type')], jobparams.get('Descr'),
                     [jobparams['Name'], jobparams.get('Type'), jobparams.get('InternalJob')],
                     ])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def info(request, name):
    """ Job defined information """
    jobres = getDIRJobinfo(name=name)
    if jobres is None:
        raise Http404()
    jobparams = extractjobparams(jobres)
    if jobparams.get('Disabledfordelete', None):
        # the job is disabled so redirect to defined jobs
        return redirect('jobsdefined')
    fsdata = {}
    if jobparams['JobDefs'] == 'jd-backup-catalog':
        # special hack for Catalog Backup job
        fsdata = {'FS': catalogfs_getall()}
    else:
        fsname = jobparams.get('FileSet', None)
        if fsname is not None:
            (inclist, exclist, optionlist) = getDIRFSparams(name=fsname)
            fsdata = {
                'Include': inclist,
                'Exclude': exclist,
                'Options': optionlist,
            }
    context = {'contentheader': 'Job info', 'apppath': ['Jobs', name, 'Info'], 'Job': jobparams, 'jobstatusdisplay': 1,
               'FSData': fsdata}
    updateMenuNumbers(context)
    return render(request, 'jobs/job.html', context)


def historydata(request, name):
    """ JSON for jobs history datatable """
    cols = ['jobid', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', 'jobstatus', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Job.objects.filter(name=name).all().count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        filtered = Job.objects.filter(Q(name=name), f).count()
        query = Job.objects.filter(Q(name=name), f).order_by(orderstr, '-jobid')[offset:offset + limit]
    else:
        filtered = total
        query = Job.objects.filter(name=name).all().order_by(
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
        data.append([j.jobid, [sstr, j.schedtime.strftime('%Y-%m-%d %H:%M:%S')], estr,
                    [j.level, j.type], j.jobfiles, j.jobbytes, [j.jobstatus, j.joberrors],
                    [j.jobid, j.name, j.type, j.jobstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def statusnr(request):
    """ JSON for Jobsnr """
    context = {}
    updateJobsnr(context)
    return JsonResponse(context)


def statuswidget(request):
    """ Jobs status widget """
    context = {}
    updateJobsnr(context)
    return render(request, 'widgets/jobstatuswidget.html', context)


def running(request):
    """ Running Jobs table """
    context = {'contentheader': 'Running Jobs', 'apppath': ['Jobs', 'Running']}
    updateMenuNumbers(context)
    return render(request, 'jobs/running.html', context)


def runningdata(request):
    """ JSON for jobs running datatable """
    cols = ['jobid', 'name', 'clientid__name', 'starttime', '', 'jobfiles', 'jobbytes', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Job.objects.filter(jobstatus__in=['R', 'B', 'a', 'i']).all().count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        filtered = Job.objects.filter(Q(jobstatus__in=['R', 'B', 'a', 'i']), f).count()
        query = Job.objects.select_related('clientid').filter(Q(jobstatus__in=['R', 'B', 'a', 'i']), f).order_by(
            orderstr, '-jobid')[offset:offset + limit]
    else:
        filtered = total
        query = Job.objects.select_related('clientid').filter(jobstatus__in=['R', 'B', 'a', 'i']).all().order_by(
            orderstr, '-jobid')[offset:offset + limit]
    data = []
    for j in query:
        data.append([j.jobid, j.name, j.clientid.name, j.starttime.strftime('%Y-%m-%d %H:%M:%S'),
                    [j.level, j.type], j.jobfiles, j.jobbytes, [j.jobid, j.name, j.type]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def finished(request):
    """ Finished Jobs table """
    context = {'contentheader': 'Finished Jobs', 'apppath': ['Jobs', 'Finished']}
    updateMenuNumbers(context)
    return render(request, 'jobs/finished.html', context)


def finisheddata(request):
    """ JSON for finished jobs datatable """
    cols = ['jobid', 'name', 'clientid__name', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Job.objects.filter(jobstatus__in=['T', 'I'], joberrors=0).all().count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        filtered = Job.objects.filter(Q(jobstatus__in=['T', 'I'], joberrors=0), f).count()
        query = Job.objects.select_related('clientid').filter(Q(jobstatus__in=['T', 'I'], joberrors=0), f).order_by(
            orderstr, '-jobid')[offset:offset + limit]
    else:
        filtered = total
        query = Job.objects.select_related('clientid').filter(jobstatus__in=['T', 'I'], joberrors=0).all().order_by(
            orderstr, '-jobid')[offset:offset + limit]
    data = []
    for j in query:
        data.append([j.jobid, j.name, j.clientid.name, j.starttime.strftime('%Y-%m-%d %H:%M:%S'),
                    j.endtime.strftime('%Y-%m-%d %H:%M:%S'),
                    [j.level, j.type], j.jobfiles, j.jobbytes, [j.jobid, j.name, j.type]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def errors(request):
    """ Running Jobs table """
    context = { 'contentheader': 'Jobs finished with errors', 'apppath': ['Jobs', 'Errors']}
    updateMenuNumbers(context)
    return render(request, 'jobs/errors.html', context)


def errorsdata(request):
    """ JSON for error jobs datatable """
    cols = ['jobid', 'name', 'clientid__name', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', 'joberrors', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Job.objects.filter(jobstatus__in=['E', 'f', 'A']).all().count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        filtered = Job.objects.filter(Q(jobstatus__in=['E', 'f', 'A']), f).count()
        query = Job.objects.select_related('clientid').filter(Q(jobstatus__in=['E', 'f', 'A']), f).order_by(orderstr, '-jobid')[offset:offset + limit]
    else:
        filtered = total
        query = Job.objects.select_related('clientid').filter(jobstatus__in=['E', 'f', 'A']).all().order_by(orderstr, '-jobid')[offset:offset + limit]
    data = []
    for j in query:
        data.append([j.jobid, j.name, j.clientid.name,
                     j.starttime.strftime('%Y-%m-%d %H:%M:%S'), j.endtime.strftime('%Y-%m-%d %H:%M:%S'),
                     [j.level, j.type], j.jobfiles, j.jobbytes, [j.joberrors, j.jobstatus], [j.jobid, j.name, j.type]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def queued(request):
    """ Queued Jobs table """
    context = {'contentheader': 'Queued Jobs', 'apppath': ['Jobs', 'Queued']}
    updateMenuNumbers(context)
    return render(request, 'jobs/queued.html', context)


def queueddata(request):
    """ JSON for queued jobs datatable """
    cols = ['jobid', 'name', 'clientid__name', 'level', 'schedtime', 'joberrors', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Job.objects.filter(jobstatus__in=['C', 'F', 'S', 'd', 't', 'p']).all().count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        filtered = Job.objects.filter(Q(jobstatus__in=['C', 'F', 'S', 'd', 't', 'p']), f).count()
        query = Job.objects.select_related('clientid').filter(Q(jobstatus__in=['C', 'F', 'S', 'd', 't', 'p']), f).order_by(orderstr, '-jobid')[offset:offset + limit]
    else:
        filtered = total
        query = Job.objects.select_related('clientid').filter(jobstatus__in=['C', 'F', 'S', 'd', 't', 'p']).all().order_by(orderstr, '-jobid')[offset:offset + limit]
    data = []
    for j in query:
        data.append([j.jobid, j.name, j.clientid.name, [j.level, j.type], j.schedtime.strftime('%Y-%m-%d %H:%M:%S'),
                     [j.joberrors, j.jobstatus], [j.jobid, j.name, j.type]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def warning(request):
    """ Warning Jobs table """
    context = {'contentheader': 'Jobs with Warnings', 'apppath': ['Jobs', 'Warning']}
    updateMenuNumbers(context)
    return render(request, 'jobs/warning.html', context)


def warningdata(request):
    """ JSON for warning jobs datatable """
    cols = ['jobid', 'name', 'clientid__name', 'starttime', 'endtime', '', 'jobfiles', 'jobbytes', 'joberrors', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Job.objects.filter(jobstatus__in=['T', 'I']).exclude(joberrors=0).all().count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        filtered = Job.objects.filter(Q(jobstatus__in=['T', 'I']), f).exclude(joberrors=0).count()
        query = Job.objects.select_related('clientid').filter(Q(jobstatus__in=['T', 'I']), f).exclude(
            joberrors=0).order_by(orderstr, '-jobid')[offset:offset + limit]
    else:
        filtered = total
        query = Job.objects.select_related('clientid').filter(jobstatus__in=['T', 'I']).exclude(
            joberrors=0).all().order_by(orderstr, '-jobid')[offset:offset + limit]
    data = []
    for j in query:
        data.append([j.jobid, j.name, j.clientid.name, j.starttime.strftime('%Y-%m-%d %H:%M:%S'),
                     j.endtime.strftime('%Y-%m-%d %H:%M:%S'),
                     [j.level, j.type], j.jobfiles, j.jobbytes, [j.joberrors, j.jobstatus],
                     [j.jobid, j.name, j.type, j.jobstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def log(request, jobid):
    """ Info about JobID """
    job = getJobidinfo(jobid)
    if job is None:
        raise Http404()
    if job.get('Status', 'C') in 'CR':
        return redirect('jobsstatus', jobid)
    jobname = job.get('Name', 'Undefined')
    if getJobDisabledfordelete(name=jobname):
        return redirect('jobsdefined')
    job['InternalJob'] = getJobInternal(name=jobname)
    context = {'contentheader': 'Job log', 'apppath': ['Jobs', jobname, 'Log', job['JobId']],
               'jobstatusdisplay': 1, 'Job': job}
    updateJobidLogtext(context, jobid)
    updateJobidVolumes(context, jobid)
    updateMenuNumbers(context)
    return render(request, 'jobs/log.html', context)


def restorefilesdata(request, jobid):
    """ JSON for restorefiles datatable """
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    search = request.GET['search[value]']
    total = Log.objects.filter(jobid=jobid, logtext__regex=r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)').count()
    if search != '':
        filtered = Log.objects.filter(jobid=jobid, logtext__regex=r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)', logtext__icontains=search).count()
        query = Log.objects.filter(jobid=jobid, logtext__regex=r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)', logtext__icontains=search).order_by('logid')[offset:offset + limit]
    else:
        filtered = total
        query = Log.objects.filter(jobid=jobid, logtext__regex=r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)').all().order_by('logid')[offset:offset + limit]
    data = []
    pattern = re.compile(r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+'
                         r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.*)')
    for log in query:
        m = pattern.match(log.logtext)
        if m is None:
            # cannot match query - strange; ignore
            continue
        t = m.groups()[1:]
        data.append((t[0], t[2], t[3], bytestext(t[4]), t[5], t[6],))
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def backupfilesdata(request, jobid):
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    search = request.GET['search[value]']
    total = File.objects.filter(jobid=jobid).count()
    orderstr1 = 'pathid__path'
    orderstr2 = 'filename'
    if request.GET['order[0][dir]'] == 'desc':
        orderstr1 = '-pathid__path'
        orderstr2 = '-filename'
    if search != '':
        f = Q(filename__icontains=search) | Q(pathid__path__icontains=search)
        filtered = File.objects.filter(Q(jobid=jobid), f).count()
        query = File.objects.filter(Q(jobid=jobid), f).order_by(orderstr1, orderstr2)[offset:offset + limit]
    else:
        filtered = total
        query = File.objects.filter(jobid=jobid).all().order_by(orderstr1, orderstr2)[offset:offset + limit]
    data = []
    for file in query:
        filename = file.pathid.path + file.filename
        lstat = file.lstat
        ltable = decodelstat(lstat)
        size = getltable_size(ltable)
        mtime = getltable_mtime(ltable)
        mode = getltable_mode(ltable)
        data.append([decodeperm(mode), mtime.strftime('%Y-%m-%d %H:%M:%S'), bytestext(size), filename])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def status(request, jobid):
    """ Jobs Log + Media/Volumes + Files """
    job = getJobidinfo(jobid)
    if job is None:
        raise Http404()
    if job.get('Status', 'C') not in 'CR':
        return redirect('jobslog', jobid)
    jobname = job.get('Name', 'Undefined')
    if getJobDisabledfordelete(name=jobname):
        return redirect('jobsdefined')
    job['InternalJob'] = getJobInternal(jobname)
    context = {'contentheader': 'Job status', 'apppath': ['Jobs', jobname, 'Status', jobid],
               'jobstatusdisplay': 1, 'Job': job, 'JobClient': [], 'JobProgress': -1}
    updateJobidLogtext(context, jobid)
    updateJobidVolumes(context, jobid)
    updateMenuNumbers(context)
    return render(request, 'jobs/status.html', context)


def checkstatusfinished(request, jobid):
    """ JSON if job finished """
    job = getJobidinfo(jobid)
    if job is None:
        raise Http404()
    check = False
    if job.get('Status', 'C') not in 'CR':
        check = True
    return JsonResponse(check, safe=False)


def statusheader(request, jobid):
    """ Job Status Widget render """
    job = getJobidinfo(jobid)
    if job is None:
        raise Http404()
    jobname = job['Name']
    job['InternalJob'] = getJobInternal(jobname)
    jobclient = getClientJobiddata(job['Client'], jobid)
    jobprogress = -1
    if len(jobclient):
        jobclient = jobclient[0]
        maxfiles = getJobmaxfiles(jobname)
        if maxfiles > 0:
            filesexamined = int(jobclient['FilesExamined'])
            jobprogress = int(filesexamined * 100 / maxfiles)
            if jobprogress > 100:
                jobprogress = 99
    context = {'Job': job, 'JobClient': jobclient, 'JobProgress': jobprogress}
    return render(request, 'widgets/statusjobwidget.html', context)


def statusjoblog(request, jobid):
    job = get_object_or_404(Job, jobid=jobid)
    context = {}
    updateJobidLogtext(context, jobid)
    return render(request, 'widgets/joblogwidget.html', context)


def statusvolumes(request, jobid):
    job = get_object_or_404(Job, jobid=jobid)
    context = {}
    updateJobidVolumes(context, jobid)
    return render(request, 'widgets/datalocationwidget.html', context)


def makedelete(request, name):
    """ Kasuje definicję zadania wraz z historią wykonania zadań """
    job = get_object_or_404(ConfResource, name=name, type__name='Job')
    isrunning = checkJobisrunning(name=name)
    # 0 - single job, deleted, reload to parameter
    # 1 - job still running, display info modal
    # 2 - multiple jobids history found, display progress modal
    st = 0
    taskid = 0
    if not isrunning:
        nrjobs = Job.objects.filter(name=name).count()
        if nrjobs > 0:
            # has history, first disable the Job
            disableDIRJob(name=name)
            directorreload()
            # prepare a background task
            task = Tasks(name='Deleting Job: ' + name, proc=1, params=name)
            task.save()
            taskid = task.taskid
            logi = Log(jobid_id=0, logtext='User deleted Job "' + name + '" with ' + str(nrjobs) + ' history job(s).')
            logi.save()
            os.system('/opt/ibadmin/utils/ibadtasks.py ' + str(taskid))
            st = 2
        else:
            # no history, so simple delete a job from configuration
            logi = Log(jobid_id=0, logtext='User deleted Job "' + name + '".')
            logi.save()
            with transaction.atomic():
                deleteDIRJob(job=job)
            directorreload()
    else:
        # still running
        st = 1
    context = {'status': st, 'taskid': taskid}
    return JsonResponse(context, safe=False)


def makerun(request, name):
    """ Uruchamia zadanie o określonej nazwie """
    job = get_object_or_404(ConfResource, name=name, type__name='Job')
    out = doJobrun(name)
    if len(out) == 0:
        st = False
        href = ''
    else:
        st = True
        # [u'Job,queued.,JobId=4']
        jobid = int(out[0].split(',')[2].split('=')[1])
        href = reverse('jobsstatus', args=[jobid])
        # lets wait a moment to job really start :)
        time.sleep(2)
    context = {'status': st, 'href': href}
    return JsonResponse(context, safe=False)


def makerestartid(request, jobid):
    """ Restartuje zadanie o danym jobid """
    job = get_object_or_404(Job, jobid=jobid)
    out = doRestartJobid(jobid)
    if len(out) == 0:
        st = False
        href = ''
    else:
        st = True
        # [u'Job,queued.,JobId=4']
        jobid = int(out[0].split(',')[2].split('=')[1])
        href = reverse('jobsstatus', args=[jobid])
        # lets wait a moment to job really start :)
        time.sleep(2)
    context = {'status': st, 'href': href}
    return JsonResponse(context, safe=False)


def makedeleteid(request, jobid):
    """ Kasuje pojedyncze zadanie backuowe po JobId """
    job = get_object_or_404(Job, jobid=jobid)
    out = doDeleteJobid(jobid)
    if len(out) == 0:
        st = False
    else:
        st = True
        logi = Log(jobid_id=0, logtext='User deleted JobId: ' + jobid + ' manually.')
        logi.save()
    context = {'status': st}
    return JsonResponse(context, safe=False)


def makecancelid(request, jobid):
    """ Anuluje pojedyncze zadanie backuowe po JobId """
    job = get_object_or_404(Job, jobid=jobid)
    out = doCancelJobid(jobid)
    # 2001 Job "systemowy.2017-04-30_17.00.37_55" marked to be canceled.
    # 3000 JobId=90 Job="systemowy.2017-04-30_17.00.37_55" marked to be canceled.
    if len(out) == 0:
        st = False
    else:
        st = True
        # lets wait a moment to job realized what is going on :)
        time.sleep(2)
    context = {'status': st}
    return JsonResponse(context, safe=False)


def makestopid(request, jobid):
    """ Stopuje pojedyncze zadanie backuowe po JobId """
    job = get_object_or_404(Job, jobid=jobid)
    out = doStopJobid(jobid)
    # 2001 Job "systemowy.2017-05-01_21.22.47_48" marked to be stopped.
    # 3000 JobId=104 Job="systemowy.2017-05-01_21.22.47_48" marked to be stopped.
    if len(out) == 0:
        st = False
    else:
        st = True
        # lets wait a moment to job realized what is going on :)
        time.sleep(2)
    context = {'status': st}
    return JsonResponse(context, safe=False)


def name(request):
    """
        JSON for Job name
        when Job name already exist then return false
    """
    nam = request.GET.get('name', '').encode('ascii', 'ignore')
    check = True
    if ConfResource.objects.filter(compid__type='D', type__name='Job', name=nam).count() == 1:
        check = False
    return JsonResponse(check, safe=False)


def commentid(request, jobid):
    job = get_object_or_404(Job, jobid=jobid)
    # print ("|", job.comment, "|")
    if request.method == 'GET':
        # get comment text
        context = {'comment': job.comment or ''}
        return JsonResponse(context)
    else:
        # save comment
        # print request.POST
        job.comment = request.POST['commenttext']
        with transaction.atomic():
            job.save(update_fields=["comment"])
        return JsonResponse(True, safe=False)


def addfiles(request):
    st = getDIRStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames()
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        initialclient = request.GET.get('c', None)
        if initialclient is not None:
            # TODO zrobić weryfikację, czy już nie ma odpowiedniego zadania i odpowiednio zmienić jobname
            form = JobFilesForm(storages=storages, clients=clients, initial={'client': initialclient,
                                                                             'name': initialclient + '-Job'})
        else:
            form = JobFilesForm(storages=storages, clients=clients)
        context = {'contentheader': 'Add Files Job', 'apppath': ['Jobs', 'Add', 'Files Backup'], 'form': form}
        updateMenuNumbers(context)
        return render(request, 'jobs/addfiles.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            form = JobFilesForm(storages=storages, clients=clients, data=request.POST)
            if form.is_valid():
                # print "cleaned data", form.cleaned_data
                with transaction.atomic():
                    createJobForm(data=form.cleaned_data)
                directorreload()
                return redirect('jobsinfo', form.cleaned_data['name'].encode('ascii', 'ignore'))
            else:
                # TODO zrobic obsługę błędów albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('jobsdefined')


def edit(request, name):
    backurl = request.GET.get('b', None)
    jobres = getDIRJobinfo(name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    jd = job['JobDefs']
    if jd == 'jd-backup-files':
        response = redirect('jobseditfiles', name)
        if backurl is not None:
            response['Location'] += '?b=' + backurl
        return response
    raise Http404()


def advanced(request, name):
    jobres = getDIRJobinfo(name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    jd = job['JobDefs']
    if jd == 'jd-backup-files':
        return redirect('jobsfilesadvanced', name)
    if jd == 'jd-admin':
        return redirect('jobsadminadvanced', name)
    if jd == 'jd-backup-catalog':
        return redirect('jobscatalogadvanced', name)
    return redirect('jobsinfo', name)


def makeinitialdatafiles(name, job):
    (backupsch, backuprepeat) = job['Scheduleparam'].split(':')
    (inclist, exclist, optionlist) = getDIRFSparams(name='fs-' + name)
    include = ''
    for i in inclist:
        if len(include):
            include += '\r\n'           # TODO required for textarea handling, but it is a platform specyfic
        include += i['value']
    exclude = ''
    for e in exclist:
        if len(exclude):
            exclude += '\r\n'           # TODO required for textarea handling, but it is a platform specyfic
        exclude += e['value']
    data = {
        'name': name,
        'descr': job['Descr'],
        'retention': getretentionform(job['Pool']),
        'storage': job['Storage'],
        'client': job['Client'],
        'include': include,
        'exclude': exclude,
        'backupsch': backupsch,
        'starttime': datetime.strptime(job['Scheduletime'], '%H:%M').time(),
        'backuprepeat': backuprepeat,
        'backuplevel': level2form(job['Level']),
        'scheduleweek': job['Scheduleweek'],
        'schedulemonth': job['Schedulemonth'],
    }
    return data


def editfiles(request, name):
    jobres = getDIRJobinfo(name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    st = getDIRStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames()
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        # print backurl
        data = makeinitialdatafiles(name, job)
        form = JobFilesForm(storages=storages, clients=clients, initial=data)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Edit Files Job', 'apppath': ['Jobs', 'Edit', 'Files Backup'], 'form': form,
                   'jobstatusdisplay': 1, 'Job': job}
        updateMenuNumbers(context)
        return render(request, 'jobs/editfiles.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            data = makeinitialdatafiles(name, job)
            form = JobFilesForm(storages=storages, clients=clients, data=post, initial=data)
            if form.is_valid() and form.has_changed():
                # print "form valid and changed ... ", form.changed_data
                if 'descr' in form.changed_data:
                    # update description
                    # print "Update description"
                    with transaction.atomic():
                        updateDIRJobDescr(name=name, descr=form.cleaned_data['descr'])
                if 'storage' in form.changed_data:
                    # update description
                    # print "Update storage"
                    with transaction.atomic():
                        updateJobStorage(name=name, storage=form.cleaned_data['storage'])
                if 'client' in form.changed_data:
                    # update description
                    # print "Update client"
                    with transaction.atomic():
                        updateJobClient(name=name, client=form.cleaned_data['client'])
                if 'include' in form.changed_data:
                    # update include
                    # print "Update include"
                    fsname = 'fs-' + name
                    with transaction.atomic():
                        updateFSIncludeFile(fsname=fsname, include=form.cleaned_data['include'])
                if 'exclude' in form.changed_data:
                    # update include
                    # print "Update exclude"
                    fsname = 'fs-' + name
                    with transaction.atomic():
                        updateFSExclude(fsname=fsname, exclude=form.cleaned_data['exclude'],
                                        client=form.cleaned_data['client'])
                if 'backupsch' in form.changed_data or 'starttime' in form.changed_data or \
                   'scheduleweek' in form.changed_data or 'schedulemonth' in form.changed_data or \
                   'backuprepeat' in form.changed_data or 'backuplevel' in form.changed_data:
                    # update Schedule
                    # print "Update schedule"
                    with transaction.atomic():
                        updateSchedule(jobname=name, data=form.cleaned_data)
                if 'retention' in form.changed_data:
                    # update retention
                    # print "update retention"
                    with transaction.atomic():
                        updateRetention(name=name, retention=form.cleaned_data['retention'])
                directorreload()
            return redirect('jobsinfo', name)
    return redirect('jobsdefined')


def makefilesadvanceddata(name, job):
    data = {
        'name': name,
        'enabled': job['Enabled'] == 'Yes',
        'runbefore': job.get('ClientRunBeforeJob', ''),
        'runafter': job.get('ClientRunAfterJob', ''),
        'dedup': job.get('Dedup'),
    }
    return data


def makeadminadvanceddata(name, job):
    data = {
        'name': name,
        'enabled': job['Enabled'] == 'Yes',
        'starttime': datetime.strptime(job['Scheduletime'], '%H:%M').time(),
    }
    return data


def filesadvanced(request, name):
    jobres = getDIRJobinfo(name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    storagededup = getStorageisDedup(job.get('Storage'))
    fsname = 'fs-' + name
    fsoptions = getDIRFSoptions(name=fsname)
    dedup = False
    for param in fsoptions:
        if param['name'] == 'Dedup':
            dedup = True
    job['Dedup'] = dedup
    if request.method == 'GET':
        data = makefilesadvanceddata(name, job)
        form = JobFilesAdvancedForm(initial=data)
        # form.fields['enabled'].disabled = True
        context = {'contentheader': 'Advanced properities', 'apppath': ['Jobs', 'Advanced', name], 'form': form,
                   'jobstatusdisplay': 1, 'Job': job, 'Storagededup': storagededup}
        updateMenuNumbers(context)
        return render(request, 'jobs/filesadvanced.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            data = makefilesadvanceddata(name, job)
            form = JobFilesAdvancedForm(initial=data, data=request.POST)
            if form.is_valid() and form.has_changed():
                if 'enabled' in form.changed_data:
                    # update job enabled
                    with transaction.atomic():
                        updateJobEnabled(name=name, enabled=form.cleaned_data['enabled'])
                if 'runbefore' in form.changed_data:
                    # update runbefore parameter
                    with transaction.atomic():
                        updateJobRunBefore(name=name, runbefore=form.cleaned_data['runbefore'])
                if 'runafter' in form.changed_data:
                    # update runafter parameter
                    with transaction.atomic():
                        updateJobRunAfter(name=name, runafter=form.cleaned_data['runafter'])
                if 'dedup' in form.changed_data:
                    # update job enabled
                    with transaction.atomic():
                        updateFSOptionsDedup(fsname=fsname, dedup=form.cleaned_data['dedup'])
                directorreload()
    return redirect('jobsinfo', name)


def adminadvanced(request, name):
    jobres = getDIRJobinfo(name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    if request.method == 'GET':
        data = makeadminadvanceddata(name, job)
        form = JobAdminAdvancedForm(initial=data)
        # form.fields['enabled'].disabled = True
        context = {'contentheader': 'Advanced properities', 'apppath': ['Jobs', 'Advanced', name], 'form': form,
                   'jobstatusdisplay': 1, 'Job': name}
        updateMenuNumbers(context)
        return render(request, 'jobs/adminadvanced.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            data = makeadminadvanceddata(name, job)
            form = JobAdminAdvancedForm(initial=data, data=request.POST)
            if form.is_valid() and form.has_changed():
                if 'enabled' in form.changed_data:
                    # update job enabled
                    with transaction.atomic():
                        updateJobEnabled(name=name, enabled=form.cleaned_data['enabled'])
                if 'starttime' in form.changed_data:
                    # update job time parameter
                    with transaction.atomic():
                        updateScheduletime(name='sch-admin', jobname=name, starttime=form.cleaned_data['starttime'])
                directorreload()
    return redirect('jobsinfo', name)


def catalogdvanced(request, name):
    jobres = getDIRJobinfo(name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    if request.method == 'GET':
        data = makeadminadvanceddata(name, job)
        form = JobCatalogAdvancedForm(initial=data)
        # form.fields['enabled'].disabled = True
        context = {'contentheader': 'Advanced properities', 'apppath': ['Jobs', 'Advanced', name], 'form': form,
                   'jobstatusdisplay': 1, 'Job': name}
        updateMenuNumbers(context)
        return render(request, 'jobs/catalogadvanced.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            data = makeadminadvanceddata(name, job)
            form = JobCatalogAdvancedForm(initial=data, data=request.POST)
            if form.is_valid() and form.has_changed():
                if 'enabled' in form.changed_data:
                    # update job enabled
                    with transaction.atomic():
                        updateJobEnabled(name=name, enabled=form.cleaned_data['enabled'])
                if 'starttime' in form.changed_data:
                    # update job time parameter
                    with transaction.atomic():
                        updateScheduletime(name='sch-backup-catalog', jobname=name, starttime=form.cleaned_data['starttime'])
                directorreload()
    return redirect('jobsinfo', name)

