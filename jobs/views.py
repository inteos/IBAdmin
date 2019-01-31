# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.db import DatabaseError
from django.contrib import messages
from libs.job import *
from libs.menu import updateMenuNumbers
from libs.appdata import *
from libs.bconsole import *
from .models import *
from .forms import *
from config.conf import *
from tasks.models import *
from tags.templatetags.ibadtexts import bytestext
from libs.restore import *
from users.decorators import *
from libs.plat import BACULACOMMUNITY
from libs.storage import *
from libs.ibadmin import *
import time
import os
import re


@perm_required('jobs.view_jobs')
def defined(request):
    """ Defined Jobs table - list """
    context = {'contentheader': 'Jobs', 'contentheadersmall': 'currently defined', 'apppath': ['Jobs', 'Defined']}
    updateMenuNumbers(request, context)
    return render(request, 'jobs/defined.html', context)


@perm_required('jobs.view_jobs')
def defineddata(request):
    """ JSON for defined jobs datatable """
    cols = [jobparamsnamekey, jobparamsclientkey, None, jobparamspoolkey, jobparamsstoragekey, jobparamslevelkey,
            jobparamsdescrkey]
    (jobslist, total, filtered) = getDIRJobsListfiltered(request, cols=cols)
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
        data.append([jobparams.get('Name'), jobparams.get('Client'),
                     [jobparams.get('Enabled'), scheduletext], pooltext, jobparams.get('Storage'),
                     ibadmin_render_joblevel(jobparams.get('Level'), jobparams.get('Type')), jobparams.get('Descr'),
                     [jobparams['Name'], jobparams.get('Type'), jobparams.get('InternalJob')],
                     ])
    draw = request.GET['draw']
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('jobs.view_jobs')
def info(request, name):
    """ Job defined information """
    jobres = getDIRJobinfo(request, name=name)
    if jobres is None:
        raise Http404()
    jobparams = extractjobparams(jobres)
    if jobparams.get('Disabledfordelete', None):
        # the job is disabled so redirect to defined jobs
        return redirect('jobsdefined')
    if jobparams['JobDefs'] == 'jd-backup-catalog':
        fsdata = catalog_fsdata()
    elif jobparams['JobDefs'] == 'jd-backup-proxmox':
        fsdata = proxmox_fsdata(jobparams)
    elif jobparams['JobDefs'] == 'jd-backup-xen':
        fsdata = xenserver_fsdata(jobparams)
    elif jobparams['JobDefs'] == 'jd-backup-kvm':
        fsdata = kvmhost_fsdata(jobparams)
    elif jobparams['JobDefs'] == 'jd-backup-esx':
        fsdata = vmware_fsdata(jobparams)
    else:
        fsdata = files_fsdata(jobparams)
    context = {'contentheader': 'Job info', 'apppath': ['Jobs', name, 'Info'], 'Job': jobparams, 'jobstatusdisplay': 1,
               'FSData': fsdata}
    updateMenuNumbers(request, context)
    return render(request, 'jobs/job.html', context)


@perm_required('jobs.view_jobs')
def historydata(request, name):
    """ JSON for jobs history datatable """
    jobres = getDIRJobinfo(request, name=name)
    if jobres is None:
        raise Http404()
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
        sstr = getstdtimetext(j.starttime)
        estr = getstdtimetext(j.endtime)
        dstr = getstdtimetext(j.schedtime)

        data.append([j.jobid, [sstr, dstr], estr,
                     ibadmin_render_joblevel(j.level, j.type), j.jobfiles, j.jobbytes, 
                     ibadmin_render_jobstatus(j.jobstatus, j.joberrors),
                    [j.jobid, j.name, j.type, j.jobstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('jobs.view_jobs')
def statusnr(request):
    """ JSON for Jobsnr """
    context = {}
    updateJobsnr(request, context)
    return JsonResponse(context)


@perm_required('jobs.view_jobs')
def statuswidget(request):
    """ Jobs status widget """
    context = {}
    updateJobsnr(request, context)
    return render(request, 'widgets/jobstatuswidget.html', context)


@perm_required('jobs.view_jobs')
def running(request):
    """ Running Jobs table """
    context = {'contentheader': 'Running Jobs', 'apppath': ['Jobs', 'Running']}
    updateMenuNumbers(request, context)
    return render(request, 'jobs/running.html', context)


@perm_required('jobs.view_jobs')
def runningdata(request):
    """ JSON for jobs running datatable """
    cols = ['jobid', 'name', 'clientid__name', 'starttime', '', 'jobfiles', 'jobbytes', '']
    draw = request.GET['draw']
    (jobslist, total, filtered) = getJobsfiltered(request, jobstatus=JOBRUNNINGSTATUS, cols=cols)
    data = []
    for job in jobslist:
        sstr = getstdtimetext(job.get("Start"))
        jid = job.get('JobId')
        jn = job.get('Name')
        jtype = job.get('Type')
        data.append([jid, jn, job.get('Client'), sstr,
                     ibadmin_render_joblevel(job.get('Level'), jtype),
                     [jid, jn, jtype]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('jobs.view_jobs')
def finished(request):
    """ Finished Jobs table """
    context = {'contentheader': 'Finished Jobs', 'apppath': ['Jobs', 'Finished']}
    updateMenuNumbers(request, context)
    return render(request, 'jobs/finished.html', context)


@perm_required('jobs.view_jobs')
def finisheddata(request):
    """ JSON for finished jobs datatable """
    cols = ['jobid', 'name', 'clientid__name', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', '']
    draw = request.GET['draw']
    (jobslist, total, filtered) = getJobsfiltered(request, jobstatus=JOBTERMINATESTATUS, joberrors=False, cols=cols)
    data = []
    for job in jobslist:
        sstr = getstdtimetext(job.get("Start"))
        estr = getstdtimetext(job.get("End"))
        jid = job.get('JobId')
        jn = job.get('Name')
        jtype = job.get('Type')
        data.append([jid, jn, job.get('Client'), sstr, estr,
                     ibadmin_render_joblevel(job.get('Level'), jtype),
                     job.get('Files'), job.get('Bytes'),
                     [jid, jn, jtype]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('jobs.view_jobs')
def errors(request):
    """ Running Jobs table """
    context = { 'contentheader': 'Jobs finished with errors', 'apppath': ['Jobs', 'Errors']}
    updateMenuNumbers(request, context)
    return render(request, 'jobs/errors.html', context)


@perm_required('jobs.view_jobs')
def errorsdata(request):
    """ JSON for error jobs datatable """
    cols = ['jobid', 'name', 'clientid__name', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', 'joberrors', '']
    draw = request.GET['draw']
    (jobslist, total, filtered) = getJobsfiltered(request, jobstatus=JOBERRORSTATUS, cols=cols)
    data = []
    for job in jobslist:
        sstr = getstdtimetext(job.get("Start"))
        estr = getstdtimetext(job.get("End"))
        jid = job.get('JobId')
        jn = job.get('Name')
        jtype = job.get('Type')
        data.append([jid, jn, job.get('Client'), sstr, estr,
                     ibadmin_render_joblevel(job.get('Level'), jtype),
                     job.get('Files'), job.get('Bytes'),
                     ibadmin_render_joberrors(job.get('Errors'), job.get('Status')),
                     [jid, jn, jtype]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('jobs.view_jobs')
def queued(request):
    """ Queued Jobs table """
    context = {'contentheader': 'Queued Jobs', 'apppath': ['Jobs', 'Queued']}
    updateMenuNumbers(request, context)
    return render(request, 'jobs/queued.html', context)


@perm_required('jobs.view_jobs')
def queueddata(request):
    """ JSON for queued jobs datatable """
    cols = ['jobid', 'name', 'clientid__name', 'level', 'schedtime', 'joberrors', '']
    draw = request.GET['draw']
    (jobslist, total, filtered) = getJobsfiltered(request, jobstatus=JOBQUEUEDSTATUS, cols=cols)
    data = []
    for job in jobslist:
        sstr = getstdtimetext(job.get('Planned'))
        jid = job.get('JobId')
        jn = job.get('Name')
        jtype = job.get('Type')
        data.append([jid, jn, job.get('Client'),
                     ibadmin_render_joblevel(job.get('Level'), jtype),
                     sstr,
                     ibadmin_render_joberrors(job.get('Errors'), job.get('Status')),
                     [jid, jn, jtype]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('jobs.view_jobs')
def warning(request):
    """ Warning Jobs table """
    context = {'contentheader': 'Jobs with Warnings', 'apppath': ['Jobs', 'Warning']}
    updateMenuNumbers(request, context)
    return render(request, 'jobs/warning.html', context)


@perm_required('jobs.view_jobs')
def warningdata(request):
    """ JSON for warning jobs datatable """
    cols = ['jobid', 'name', 'clientid__name', 'starttime', 'endtime', '', 'jobfiles', 'jobbytes', 'joberrors', '']
    draw = request.GET['draw']
    (jobslist, total, filtered) = getJobsfiltered(request, jobstatus=JOBTERMINATESTATUS, joberrors=True, cols=cols)
    data = []
    for job in jobslist:
        sstr = getstdtimetext(job.get("Start"))
        estr = getstdtimetext(job.get("End"))
        jid = job.get('JobId')
        jn = job.get('Name')
        jtype = job.get('Type')
        jstatus = job.get('Status')
        data.append([jid, jn, job.get('Client'),
                     sstr, estr,
                     ibadmin_render_joblevel(job.get('Level'), jtype),
                     job.get('Files'), job.get('Bytes'),
                     ibadmin_render_joberrors(job.get('Errors'), jstatus),
                     [jid, jn, jtype, jstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('jobs.view_jobs')
def jobslast(request):
    """ Finished Jobs table """
    context = {'contentheader': 'Latest Jobs', 'apppath': ['Jobs', 'Last']}
    updateMenuNumbers(request, context)
    return render(request, 'jobs/last.html', context)


@perm_required('jobs.view_jobs')
def jobslastdata(request):
    """ JSON for error jobs datatable """
    cols = ['jobid', 'name', 'clientid__name', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', 'joberrors', '']
    draw = request.GET['draw']
    (jobslist, total, filtered) = getJobsfiltered(request, jobstatus=JOBDONESTATUS, cols=cols)
    data = []
    for job in jobslist:
        sstr = getstdtimetext(job.get("Start"))
        estr = getstdtimetext(job.get("End"))
        jid = job.get('JobId')
        jn = job.get('Name')
        jtype = job.get('Type')
        jstatus = job.get('Status')
        data.append([jid, jn, job.get('Client'),
                     sstr, estr,
                     ibadmin_render_joblevel(job.get('Level'), jtype),
                     job.get('Files'), job.get('Bytes'),
                     ibadmin_render_jobstatus(jstatus, job.get('Errors')),
                     [jid, jn, jtype, jstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('jobs.view_jobs')
def log(request, jobid):
    """ Info about JobID """
    job = getJobidinfo(request, jobid)
    if job is None:
        raise Http404()
    if job.get('Status', 'C') in 'CR':
        return redirect('jobsstatus', jobid)
    jobname = job.get('Name', 'Undefined')
    if getJobDisabledfordelete(name=jobname):
        return redirect('jobsdefined')
    job['InternalJob'] = getJobInternal(name=jobname)
    hascopies = Job.objects.filter(priorjobid=jobid)
    job['hascopies'] = hascopies
    priorjobid = job.get('priorjobid', 0)
    iscopyof = Job.objects.filter(jobid=priorjobid).count()
    job['iscopyof'] = iscopyof
    context = {'contentheader': 'Job log', 'apppath': ['Jobs', jobname, 'Log', job['JobId']],
               'jobstatusdisplay': 1, 'Job': job}
    updateJobidLogtext(context, jobid)
    updateJobidVolumes(context, jobid)
    updateMenuNumbers(request, context)
    return render(request, 'jobs/log.html', context)


@perm_required('jobs.status_jobs')
def status(request, jobid):
    """ Jobs Log + Media/Volumes + Files """
    job = getJobidinfo(request, jobid)
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
    updateMenuNumbers(request, context)
    return render(request, 'jobs/status.html', context)


@perm_required('jobs.view_jobs')
def restorefilesdata(request, jobid):
    """ JSON for restorefiles datatable """
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    search = request.GET['search[value]']
    total = Log.objects.filter(
        jobid=jobid,
        logtext__regex=r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)')\
        .count()
    if search != '':
        filtered = Log.objects.filter(
            jobid=jobid,
            logtext__regex=r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)',
            logtext__icontains=search).count()
        query = Log.objects.filter(
            jobid=jobid,
            logtext__regex=r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)',
            logtext__icontains=search).order_by('logid')[offset:offset + limit]
    else:
        filtered = total
        query = Log.objects.filter(
            jobid=jobid,
            logtext__regex=r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)') \
            .all().order_by('logid')[offset:offset + limit]
    data = []
    pattern = re.compile(r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+'
                         r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.*)')
    for logtt in query:
        m = pattern.match(logtt.logtext)
        if m is None:
            # cannot match query - strange; ignore
            continue
        t = m.groups()[1:]
        data.append((t[0], t[2], t[3], bytestext(t[4]), t[5], t[6],))
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('jobs.view_jobs')
def backupfilesdata(request, jobid):
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    search = request.GET['search[value]']
    total = File.objects.filter(jobid=jobid).count()
    orderstr1 = 'pathid__path'
    orderstr2 = 'filename'
    if BACULACOMMUNITY:
        orderstr2 = 'filenameid__name'
    if request.GET['order[0][dir]'] == 'desc':
        orderstr1 = '-pathid__path'
        orderstr2 = '-filename'
    if search != '':
        if BACULACOMMUNITY:
            f = Q(filenameid__name__icontains=search) | Q(pathid__path__icontains=search)
        else:
            f = Q(filename__icontains=search) | Q(pathid__path__icontains=search)
        filtered = File.objects.filter(Q(jobid=jobid), f).count()
        query = File.objects.filter(Q(jobid=jobid), f).order_by(orderstr1, orderstr2)[offset:offset + limit]
    else:
        filtered = total
        query = File.objects.filter(jobid=jobid).all().order_by(orderstr1, orderstr2)[offset:offset + limit]
    data = []
    for file in query:
        if BACULACOMMUNITY:
            filename = file.pathid.path + file.filenameid.name
        else:
            filename = file.pathid.path + file.filename
        lstat = file.lstat
        ltable = decodelstat(lstat)
        size = getltable_size(ltable)
        mtime = getltable_mtime(ltable)
        mode = getltable_mode(ltable)
        data.append([decodeperm(mode), mtime.strftime('%Y-%m-%d %H:%M:%S'), bytestext(size), filename])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('jobs.status_jobs')
def status(request, jobid=None):
    """ Jobs Log + Media/Volumes + Files """
    job = getJobidinfo(request, jobid)
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
    updateMenuNumbers(request, context)
    return render(request, 'jobs/status.html', context)


@perm_required('jobs.status_jobs')
def checkstatusfinished(request, jobid):
    """ JSON if job finished """
    job = getJobidinfo(request, jobid)
    if job is None:
        raise Http404()
    check = False
    if job.get('Status', 'C') not in 'CR':
        check = True
    return JsonResponse(check, safe=False)


@perm_required('jobs.status_jobs')
def statusheader(request, jobid):
    """ Job Status Widget render """
    job = getJobidinfo(request, jobid)
    if job is None:
        raise Http404()
    jobname = job['Name']
    job['InternalJob'] = getJobInternal(jobname)
    jobclient = getClientJobiddata(job['Client'], jobid)
    jobprogress = -1
    if len(jobclient):
        jobclient = jobclient[0]
        # TODO: change progres value as files and bytes
        mf = jobclient.get('ExpectedFiles', None)
        if mf is None:
            maxfiles = getJobmaxfiles(jobname)
        else:
            maxfiles = int(mf)
        if maxfiles > 0:
            filesexamined = int(jobclient['FilesExamined'])
            jobprogress = int(filesexamined * 100 / maxfiles)
            if jobprogress > 100:
                jobprogress = 99
    context = {'Job': job, 'JobClient': jobclient, 'JobProgress': jobprogress}
    return render(request, 'widgets/statusjobwidget.html', context)


@perm_required('jobs.status_jobs')
def statusjoblog(request, jobid):
    job = getJobidinfo(request, jobid)
    if job is None:
        raise Http404()
    context = {}
    updateJobidLogtext(context, jobid)
    return render(request, 'widgets/joblogwidget.html', context)


@perm_required('jobs.view_datalocation')
def statusvolumes(request, jobid):
    job = getJobidinfo(request, jobid)
    if job is None:
        raise Http404()
    context = {}
    updateJobidVolumes(context, jobid)
    return render(request, 'widgets/datalocationwidget.html', context)


@perm_required('jobs.delete_jobs')
def makedelete(request, name):
    """ Delete job definition and job history """
    userjobs = getUserJobsnames(request)
    job = get_object_or_404(ConfResource, name=name, type=RESTYPE['Job'], name__in=userjobs)
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
            task = Tasks(name='Deleting Job: %s' % name, proc=1, params=name)
            task.save()
            taskid = task.taskid
            logi = Log(jobid_id=0, logtext='User deleted Job "%s" with %s history job(s).' % (name, str(nrjobs)))
            logi.save()
            os.system('/opt/ibadmin/utils/ibadtasks.py ' + str(taskid))
            st = 2
        else:
            # no history, so simple delete a job from configuration
            logi = Log(jobid_id=0, logtext='User deleted Job "%s".' % name)
            logi.save()
            with transaction.atomic():
                deleteDIRJob(job=job)
            directorreload()
    else:
        # still running
        st = 1
    context = {'status': st, 'taskid': taskid}
    return JsonResponse(context, safe=False)


@perm_required('jobs.run_jobs')
def makerun(request, name):
    """ Uruchamia zadanie o określonej nazwie """
    userjobs = getUserJobsnames(request)
    job = get_object_or_404(ConfResource, name=name, type__name='Job', name__in=userjobs)
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


@perm_required('jobs.restart_jobs')
def makerestartid(request, jobid):
    """ Restartuje zadanie o danym jobid """
    userjobs = getUserJobsnames(request)
    job = get_object_or_404(Job, jobid=jobid, name__in=userjobs)
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


@perm_required('jobs.delete_jobid')
def makedeleteid(request, jobid):
    """ Kasuje pojedyncze zadanie backuowe po JobId """
    userjobs = getUserJobsnames(request)
    job = get_object_or_404(Job, jobid=jobid, name__in=userjobs)
    out = doDeleteJobid(jobid)
    if len(out) == 0:
        st = False
    else:
        st = True
        logi = Log(jobid_id=0, logtext='User deleted JobId: ' + jobid + ' manually.')
        logi.save()
    context = {'status': st}
    return JsonResponse(context, safe=False)


@perm_required('jobs.cancel_jobs')
def makecancelid(request, jobid):
    """ Anuluje pojedyncze zadanie backuowe po JobId """
    userjobs = getUserJobsnames(request)
    job = get_object_or_404(Job, jobid=jobid, name__in=userjobs)
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


@perm_required('jobs.stop_jobs')
def makestopid(request, jobid):
    """ Stopuje pojedyncze zadanie backuowe po JobId """
    userjobs = getUserJobsnames(request)
    job = get_object_or_404(Job, jobid=jobid, name__in=userjobs)
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


@perm_required('jobs.add_jobs')
def jname(request):
    """
        JSON for Job name
        when Job name already exist then return false
    """
    n = request.GET.get('name', '').encode('ascii', 'ignore')
    check = True
    if ConfResource.objects.filter(compid__type='D', type__name='Job', name=n).count() == 1:
        check = False
    return JsonResponse(check, safe=False)


@perm_required('jobs.comment_jobs')
def commentid(request, jobid):
    userjobs = getUserJobsnames(request)
    job = get_object_or_404(Job, jobid=jobid, name__in=userjobs)
    if request.method == 'GET':
        # get comment text
        context = {'comment': job.comment or ''}
        return JsonResponse(context)
    else:
        # save comment
        job.comment = request.POST['commenttext']
        with transaction.atomic():
            job.save(update_fields=["comment"])
        return JsonResponse(True, safe=False)


@perm_required('jobs.add_jobs')
def addfiles(request):
    st = getDIRStorageNames(request)
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames(request)
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        initialclient = request.GET.get('c', None)
        backurl = request.GET.get('b', None)
        initial = {'backurl': backurl}
        if initialclient is not None:
            initial['client'] = initialclient
            initial['name'] = initialclient + '-Job'
        form = JobFilesForm(storages=storages, clients=clients, initial=initial)
        context = {'contentheader': 'Add Files Job', 'apppath': ['Jobs', 'Add', 'Files Backup'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/addfiles.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        name = None
        if not cancel:
            form = JobFilesForm(storages=storages, clients=clients, data=request.POST)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                # print "cleaned data", form.cleaned_data
                try:
                    with transaction.atomic():
                        createJobFilesForm(request, data=form.cleaned_data)
                    directorreload()
                except DatabaseError as e:
                    messages.error(request, "Database error: %s" % e, extra_tags='Error')
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    if backurl is not None and backurl != '':
        messages.success(request, 'Job successfully added', extra_tags='Success!')
        return redirect(backurl)
    if name is not None:
        return redirect('jobsinfo', name)
    return redirect('jobsdefined')


@perm_required('jobs.add_jobs_proxmox')
def addproxmox(request):
    checkDIRProxmoxJobDef()
    st = getDIRStorageNames(request)
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames(request, os='proxmox')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        initialclient = request.GET.get('c', None)
        initialvmname = request.GET.get('v', None)
        initialvmid = request.GET.get('i', None)
        backurl = request.GET.get('b', None)
        initial = {'backurl': backurl}
        jbname = ""
        if initialvmname is not None:
            initial['include'] = str(initialvmname)
            jbname = str(initialvmname)
        if initialvmid is not None:
            initial['include'] = 'vmid=' + str(initialvmid)
            jbname = 'vmid' + str(initialvmid)
        if initialclient is not None:
            initial['client'] = initialclient
            if initialvmname is None and initialvmid is None:
                jbname = 'guest'
            jbname = initialclient + '-' + jbname
        if initialclient is not None or initialvmname is not None or initialvmid is not None:
            initial['name'] = jbname
        form = JobProxmoxForm(storages=storages, clients=clients, initial=initial)
        context = {'contentheader': 'Add Proxmox GuestVM Job', 'apppath': ['Jobs', 'Add', 'Proxmox Backup'],
                   'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/addproxmox.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        name = None
        post = request.POST.copy()
        post['backuplevel'] = 'full'
        if not cancel:
            form = JobProxmoxForm(storages=storages, clients=clients, data=post)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                # print "cleaned data", form.cleaned_data
                with transaction.atomic():
                    createJobProxmoxForm(data=form.cleaned_data)
                directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    if backurl is not None and backurl != '':
        return redirect(backurl)
    if name is not None:
        return redirect('jobsinfo', name)
    return redirect('jobsdefined')


@perm_required('jobs.add_jobs_xen')
def addxenserver(request):
    checkDIRXenServerJobDef()
    st = getDIRStorageNames(request)
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames(request, os='xen')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        initialclient = request.GET.get('c', None)
        initialvmname = request.GET.get('v', None)
        initialvmid = request.GET.get('i', None)
        backurl = request.GET.get('b', None)
        initial = {'backurl': backurl}
        jbname = ""
        if initialvmname is not None:
            initial['include'] = str(initialvmname)
            jbname = str(initialvmname)
        if initialvmid is not None:
            initial['include'] = 'uuid=' + str(initialvmid)
            jbname = 'uuid' + str(initialvmid)
        if initialclient is not None:
            initial['client'] = initialclient
            if initialvmname is None and initialvmid is None:
                jbname = 'guest'
            jbname = initialclient + '-' + jbname
        if initialclient is not None or initialvmname is not None or initialvmid is not None:
            initial['name'] = jbname
        form = JobXenServerForm(storages=storages, clients=clients, initial=initial)
        context = {'contentheader': 'Add XenServer GuestVM Job', 'apppath': ['Jobs', 'Add', 'XenServer Backup'],
                   'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/addxenserver.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        name = None
        if not cancel:
            form = JobXenServerForm(storages=storages, clients=clients, data=request.POST)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                # print "cleaned data", form.cleaned_data
                with transaction.atomic():
                    createJobXenServerForm(data=form.cleaned_data)
                directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    if backurl is not None and backurl != '':
        return redirect(backurl)
    if name is not None:
        return redirect('jobsinfo', name)
    return redirect('jobsdefined')


@perm_required('jobs.add_jobs_vmware')
def addvmware(request):
    checkDIRVMwareJobDef()
    st = getDIRStorageNames(request)
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames(request, os='vmware')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        initialclient = request.GET.get('c', None)
        initialvmname = request.GET.get('v', None)
        backurl = request.GET.get('b', None)
        initial = {'backurl': backurl}
        jbname = ""
        if initialvmname is not None:
            initial['include'] = str(initialvmname)
            jbname = str(initialvmname)
        if initialclient is not None:
            initial['client'] = initialclient
            if initialvmname is None:
                jbname = 'guest'
            jbname = initialclient + '-' + jbname
        if initialclient is not None or initialvmname is not None:
            initial['name'] = jbname
        form = JobVMwareForm(storages=storages, clients=clients, initial=initial)
        context = {'contentheader': 'Add VMware GuestVM Job', 'apppath': ['Jobs', 'Add', 'VMware Backup'],
                   'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/addvmware.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        name = None
        if not cancel:
            form = JobVMwareForm(storages=storages, clients=clients, data=request.POST)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                # print "cleaned data", form.cleaned_data
                with transaction.atomic():
                    createJobVMwareServerForm(data=form.cleaned_data)
                directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    if backurl is not None and backurl != '':
        return redirect(backurl)
    if name is not None:
        return redirect('jobsinfo', name)
    return redirect('jobsdefined')


@perm_required('jobs.add_jobs_kvm')
def addkvm(request):
    checkDIRKVMJobDef()
    st = getDIRStorageNames(request)
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames(request, os='kvm')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        initialclient = request.GET.get('c', None)
        initialvmname = request.GET.get('v', None)
        backurl = request.GET.get('b', None)
        initial = {'backurl': backurl}
        jbname = ""
        if initialvmname is not None:
            initial['include'] = str(initialvmname)
            jbname = str(initialvmname)
        if initialclient is not None:
            initial['client'] = initialclient
            if initialvmname is None:
                jbname = 'guest'
            jbname = initialclient + '-' + jbname
        if initialclient is not None or initialvmname is not None:
            initial['name'] = jbname
        form = JobKVMForm(storages=storages, clients=clients, initial=initial)
        context = {'contentheader': 'Add KVM GuestVM Job', 'apppath': ['Jobs', 'Add', 'KVM Backup'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/addkvm.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        name = None
        if not cancel:
            form = JobKVMForm(storages=storages, clients=clients, data=request.POST)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                # print "cleaned data", form.cleaned_data
                with transaction.atomic():
                    createJobKVMForm(data=form.cleaned_data)
                directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    if backurl is not None and backurl != '':
        return redirect(backurl)
    if name is not None:
        return redirect('jobsinfo', name)
    return redirect('jobsdefined')


@any_perm_required('jobs.add_jobs', 'jobs.add_jobs_xen', 'jobs.add_jobs_kvm', 'jobs.add_jobs_proxmox',
                   'jobs.add_jobs_vmware')
def add(request, vmtype):
    backurl = request.GET.get('b', None)
    clientname = request.GET.get('c', None)
    if vmtype == 'proxmox':
        response = redirect('jobsaddproxmox')
    elif vmtype == 'xen':
        response = redirect('jobsaddxen')
    elif vmtype == 'vmware':
        response = redirect('jobsaddvmware')
    elif vmtype == 'kvm':
        response = redirect('jobsaddkvm')
    else:
        response = redirect('jobsaddfiles')
    if clientname is not None:
        response['Location'] += '?c=%s' % clientname
    if backurl is not None:
        if clientname is not None:
            response['Location'] += '&b=%s' % backurl
        else:
            response['Location'] += '?b=%s' % backurl
    return response


@perm_required('jobs.change_jobs')
def edit(request, name):
    backurl = request.GET.get('b', None)
    jobres = getDIRJobinfo(request, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    jd = job['JobDefs']
    if jd == 'jd-backup-files':
        response = redirect('jobseditfiles', name)
    elif jd == 'jd-backup-proxmox':
        response = redirect('jobseditproxmox', name)
    elif jd == 'jd-backup-xen':
        response = redirect('jobseditxenserver', name)
    elif jd == 'jd-backup-kvm':
        response = redirect('jobseditkvm', name)
    elif jd == 'jd-backup-esx':
        response = redirect('jobseditvmware', name)
    else:
        raise Http404()
    if backurl is not None:
        response['Location'] += '?b=' + backurl
    return response


@perm_required('jobs.advanced_jobs')
def advanced(request, name):
    jobres = getDIRJobinfo(request, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    jd = job['JobDefs']
    if jd == 'jd-backup-files':
        return redirect('jobsfilesadvanced', name)
    if jd == 'jd-backup-proxmox':
        return redirect('jobsproxmoxadvanced', name)
    if jd == 'jd-backup-xen':
        return redirect('jobsxenserveradvanced', name)
    if jd == 'jd-backup-kvm':
        return redirect('jobskvmadvanced', name)
    if jd == 'jd-backup-esx':
        return redirect('jobsvmwareadvanced', name)
    if jd == 'jd-admin':
        return redirect('jobsadminadvanced', name)
    if jd == 'jd-backup-catalog':
        return redirect('jobscatalogadvanced', name)
    return redirect('jobsinfo', name)


@perm_required('jobs.change_jobs')
def editfiles(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    st = getDIRStorageNames(request)
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames(request)
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        data = makeinitialdatafiles(name, job, backurl)
        form = JobFilesForm(storages=storages, clients=clients, initial=data)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Edit Files Job', 'apppath': ['Jobs', 'Edit', 'Files Backup'], 'form': form,
                   'jobstatusdisplay': 1, 'Job': job}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/editfiles.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if backurl is None or backurl == '':
            backurl = 'jobsinfo'
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            data = makeinitialdatafiles(name, job, backurl)
            form = JobFilesForm(storages=storages, clients=clients, data=post, initial=data)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... ", form.changed_data
                    updatejobparams(name, form)
                    with transaction.atomic():
                        fsname = 'fs-' + name
                        if 'include' in form.changed_data:
                            # update include
                            updateFSIncludeFile(request, dircompid=dircompid, fsname=fsname,
                                                include=form.cleaned_data['include'])
                        if 'exclude' in form.changed_data:
                            # update include
                            updateFSExclude(request, dircompid=dircompid, fsname=fsname,
                                            exclude=form.cleaned_data['exclude'], client=form.cleaned_data['client'])
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect(backurl, name)


@perm_required('jobs.change_jobs')
def editproxmox(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    st = getDIRStorageNames(request, dircompid=dircompid)
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames(request, dircompid=dircompid, os='proxmox')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    abortonerror = job.get('AbortOnError', None)
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        # print backurl
        data = makeinitialdatavms(name, job, backurl)
        form = JobProxmoxForm(storages=storages, clients=clients, initial=data)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Edit Proxmox GuestVM Job', 'apppath': ['Jobs', 'Edit', 'Proxmox Backup'],
                   'form': form, 'jobstatusdisplay': 1, 'Job': job}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/editproxmox.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if backurl is None or backurl == '':
            backurl = 'jobsinfo'
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            post['backuplevel'] = 'full'
            data = makeinitialdatavms(name, job, backurl)
            form = JobProxmoxForm(storages=storages, clients=clients, data=post, initial=data)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... ", form.changed_data
                    updatejobparams(name, form, forcelevel='full')
                    fsname = 'fs-' + name
                    if 'allvms' in form.changed_data or 'include' in form.changed_data \
                            or 'exclude' in form.changed_data:
                        allvms = form.cleaned_data['allvms']
                        plugin, include, exclude = prepareFSProxmoxPlugin(form.cleaned_data, abortonerror)
                        with transaction.atomic():
                            updateFSIncludePlugin(dircompid=dircompid, fsname=fsname, include=plugin)
                            updateJobAllobjs(dircompid=dircompid, name=name, allobjs=allvms, objsinclude=include,
                                             objsexclude=exclude)
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect(backurl, name)


@perm_required('jobs.change_jobs')
def editxenserver(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    st = getDIRStorageNames(request, dircompid=dircompid)
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames(request, dircompid=dircompid, os='xen')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        # print backurl
        data = makeinitialdatavms(name, job, backurl)
        form = JobXenServerForm(storages=storages, clients=clients, initial=data)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Edit XenServer GuestVM Job', 'apppath': ['Jobs', 'Edit', 'XenServer Backup'],
                   'form': form, 'jobstatusdisplay': 1, 'Job': job}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/editxenserver.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if backurl is None or backurl == '':
            backurl = 'jobsinfo'
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            post['backuplevel'] = 'full'
            data = makeinitialdatavms(name, job, backurl)
            form = JobXenServerForm(storages=storages, clients=clients, data=post, initial=data)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... ", form.changed_data
                    updatejobparams(name, form, forcelevel='full')
                    fsname = 'fs-' + name
                    if 'allvms' in form.changed_data or 'include' in form.changed_data \
                            or 'exclude' in form.changed_data:
                        allvms = form.cleaned_data['allvms']
                        plugin, include, exclude = prepareFSXenServerPlugin(form.cleaned_data)
                        with transaction.atomic():
                            updateFSIncludePlugin(dircompid=dircompid, fsname=fsname, include=plugin)
                            updateJobAllobjs(dircompid=dircompid, name=name, allobjs=allvms, objsinclude=include,
                                             objsexclude=exclude)
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect(backurl, name)


@perm_required('jobs.change_jobs')
def editkvm(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    st = getDIRStorageNames(request, dircompid=dircompid)
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames(request, dircompid=dircompid, os='kvm')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        # print backurl
        data = makeinitialdatavms(name, job, backurl)
        form = JobKVMForm(storages=storages, clients=clients, initial=data)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Edit KVM GuestVM Job', 'apppath': ['Jobs', 'Edit', 'KVM Backup'],
                   'form': form, 'jobstatusdisplay': 1, 'Job': job}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/editkvm.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if backurl is None or backurl == '':
            backurl = 'jobsinfo'
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            data = makeinitialdatavms(name, job, backurl)
            form = JobKVMForm(storages=storages, clients=clients, data=post, initial=data)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... ", form.changed_data
                    updatejobparams(name, form, forcelevel='full')
                    fsname = 'fs-' + name
                    if 'allvms' in form.changed_data or 'include' in form.changed_data \
                            or 'exclude' in form.changed_data:
                        allvms = form.cleaned_data['allvms']
                        plugin, include, exclude = prepareFSKVMPlugin(form.cleaned_data)
                        with transaction.atomic():
                            updateFSIncludePlugin(dircompid=dircompid, fsname=fsname, include=plugin)
                            updateJobAllobjs(dircompid=dircompid, name=name, allobjs=allvms, objsinclude=include,
                                             objsexclude=exclude)
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect(backurl, name)


@perm_required('jobs.change_jobs')
def editvmware(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    st = getDIRStorageNames(request, dircompid=dircompid)
    storages = ()
    for s in st:
        storages += ((s, s),)
    cl = getDIRClientsNames(request, dircompid=dircompid, os='vmware')
    clients = ()
    for c in cl:
        clients += ((c, c),)
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        # print backurl
        data = makeinitialdatavms(name, job, backurl)
        form = JobVMwareForm(storages=storages, clients=clients, initial=data)
        form.fields['name'].disabled = True
        context = {'contentheader': 'Edit VMware GuestVM Job', 'apppath': ['Jobs', 'Edit', 'VMware Backup'],
                   'form': form, 'jobstatusdisplay': 1, 'Job': job}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/editvmware.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if backurl is None or backurl == '':
            backurl = 'jobsinfo'
        if not cancel:
            # print "Save!"
            post = request.POST.copy()
            post['name'] = name
            data = makeinitialdatavms(name, job, backurl)
            form = JobVMwareForm(storages=storages, clients=clients, data=post, initial=data)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... ", form.changed_data
                    updatejobparams(name, form)
                    fsname = 'fs-%s' % name
                    if 'allvms' in form.changed_data or 'include' in form.changed_data \
                            or 'exclude' in form.changed_data:
                        allvms = form.cleaned_data['allvms']
                        plugin, include, exclude = prepareFSVMwarePlugin(form.cleaned_data)
                        with transaction.atomic():
                            updateFSIncludePlugin(dircompid=dircompid, fsname=fsname, include=plugin)
                            updateJobAllobjs(dircompid=dircompid, name=name, allobjs=allvms, objsinclude=include,
                                             objsexclude=exclude)
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect(backurl, name)


@perm_required('jobs.advanced_jobs')
def filesadvanced(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    storagededup = getStorageisDedup(job.get('Storage'))
    updatejobparamsfs(dircompid=dircompid, name=name, jobparams=job)
    if request.method == 'GET':
        data = makefilesadvanceddata(name, job)
        form = JobFilesAdvancedForm(initial=data)
        # form.fields['enabled'].disabled = True
        form.fields['compr'].disabled = data['dedup']
        context = {'contentheader': 'Advanced properities', 'apppath': ['Jobs', 'Advanced', name], 'form': form,
                   'jobstatusdisplay': 1, 'Job': job, 'Storagededup': storagededup}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/filesadvanced.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            data = makefilesadvanceddata(name, job)
            form = JobFilesAdvancedForm(initial=data, data=request.POST)
            if form.is_valid():
                if form.has_changed():
                    with transaction.atomic():
                        if 'enabled' in form.changed_data:
                            # update job enabled
                            updateJobEnabled(dircompid=dircompid, name=name, enabled=form.cleaned_data['enabled'])
                        if 'runbefore' in form.changed_data:
                            # update runbefore parameter
                            updateJobRunBefore(dircompid=dircompid, name=name, runbefore=form.cleaned_data['runbefore'])
                        if 'runafter' in form.changed_data:
                            # update runafter parameter
                            updateJobRunAfter(dircompid=dircompid, name=name, runafter=form.cleaned_data['runafter'])
                        fsname = 'fs-%s' % name
                        if 'dedup' in form.changed_data:
                            # update job deduplication
                            updateFSOptionsDedup(fsname=fsname, dedup=form.cleaned_data['dedup'])
                        if 'compr' in form.changed_data:
                            # update job compression
                            updateFSOptionsCompression(fsname=fsname, compression=form.cleaned_data['compr'])
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('jobsinfo', name)


@perm_required('jobs.advanced_jobs')
def adminadvanced(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    if request.method == 'GET':
        data = makeadminadvanceddata(name, job)
        form = JobAdminAdvancedForm(initial=data)
        # form.fields['enabled'].disabled = True
        jobcontext = {
            'Name': name,
            'InternalJob': 'Yes',
        }
        context = {'contentheader': 'Advanced properities', 'apppath': ['Jobs', 'Advanced', name], 'form': form,
                   'jobstatusdisplay': 1, 'Job': jobcontext}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/adminadvanced.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            data = makeadminadvanceddata(name, job)
            form = JobAdminAdvancedForm(initial=data, data=request.POST)
            if form.is_valid():
                if form.has_changed():
                    with transaction.atomic():
                        if 'enabled' in form.changed_data:
                            # update job enabled
                            updateJobEnabled(dircompid=dircompid, name=name, enabled=form.cleaned_data['enabled'])
                        if 'starttime' in form.changed_data:
                            # update job time parameter
                            updateScheduletime(dircompid=dircompid, name='sch-admin', jobname=name,
                                               starttime=form.cleaned_data['starttime'])
                    messages.success(request, "Admin Job advanced parameters updated!", extra_tags="Success!")
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('jobsinfo', name)


@perm_required('jobs.advanced_jobs')
def catalogdvanced(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    updatejobparamsfs(dircompid=dircompid, name=name, jobparams=job, fsname='fs-catalog-backup')
    storagededup = getStorageisDedup(job.get('Storage'))
    if request.method == 'GET':
        data = makecatalogadvanceddata(name, job)
        form = JobCatalogAdvancedForm(initial=data)
        # form.fields['enabled'].disabled = True
        form.fields['compr'].disabled = storagededup
        jobcontext = {
            'Name': name,
            'InternalJob': 'Yes',
        }
        context = {'contentheader': 'Advanced properities', 'apppath': ['Jobs', 'Advanced', name], 'form': form,
                   'jobstatusdisplay': 1, 'Job': jobcontext}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/catalogadvanced.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            data = makecatalogadvanceddata(name, job)
            form = JobCatalogAdvancedForm(initial=data, data=request.POST)
            if form.is_valid():
                if form.has_changed():
                    with transaction.atomic():
                        if 'enabled' in form.changed_data:
                            # update job enabled
                            updateJobEnabled(dircompid=dircompid, name=name, enabled=form.cleaned_data['enabled'])
                        if 'starttime' in form.changed_data:
                            # update job time parameter
                            updateScheduletime(dircompid=dircompid, name='sch-backup-catalog', jobname=name,
                                               starttime=form.cleaned_data['starttime'])
                        if 'compr' in form.changed_data:
                            # update job compression
                            updateFSOptionsCompression(fsname='fs-catalog-backup',
                                                       compression=form.cleaned_data['compr'])
                    messages.success(request, "Backup Catalog advanced parameters updated!", extra_tags="Success!")
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('jobsinfo', name)


@perm_required('jobs.advanced_jobs')
def proxmoxadvanced(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    storagededup = getStorageisDedup(job.get('Storage'))
    updatejobparamsfs(dircompid=dircompid, name=name, jobparams=job)
    if request.method == 'GET':
        data = makevmsadvanceddata(name, job)
        form = JobProxmoxAdvancedForm(initial=data)
        # form.fields['enabled'].disabled = True
        form.fields['compr'].disabled = data['dedup']
        context = {'contentheader': 'Advanced properities', 'apppath': ['Jobs', 'Advanced', name], 'form': form,
                   'jobstatusdisplay': 1, 'Job': job, 'Storagededup': storagededup}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/proxmoxadvanced.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            data = makevmsadvanceddata(name, job)
            form = JobProxmoxAdvancedForm(initial=data, data=request.POST)
            if form.is_valid():
                if form.has_changed():
                    with transaction.atomic():
                        if 'enabled' in form.changed_data:
                            # update job enabled
                            updateJobEnabled(name=name, enabled=form.cleaned_data['enabled'])
                        fsname = 'fs-' + name
                        if 'dedup' in form.changed_data:
                            # update job deduplication
                            updateFSOptionsDedup(fsname=fsname, dedup=form.cleaned_data['dedup'])
                        if 'compr' in form.changed_data:
                            # update job compression
                            updateFSOptionsCompression(fsname=fsname, compression=form.cleaned_data['compr'])
                        if 'abort' in form.changed_data:
                            # update abort_on_error
                            updateFSProxmoxPlugin(job=job, abortonerror=form.cleaned_data['abort'])
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('jobsinfo', name)


@perm_required('jobs.advanced_jobs')
def xenserveradvanced(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    storagededup = getStorageisDedup(job.get('Storage'))
    updatejobparamsfs(dircompid=dircompid, name=name, jobparams=job)
    if request.method == 'GET':
        data = makevmsadvanceddata(name, job)
        form = JobXenServerAdvancedForm(initial=data)
        # form.fields['enabled'].disabled = True
        form.fields['compr'].disabled = data['dedup']
        context = {'contentheader': 'Advanced properities', 'apppath': ['Jobs', 'Advanced', name], 'form': form,
                   'jobstatusdisplay': 1, 'Job': job, 'Storagededup': storagededup}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/xenserveradvanced.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            data = makevmsadvanceddata(name, job)
            form = JobXenServerAdvancedForm(initial=data, data=request.POST)
            if form.is_valid():
                if form.has_changed():
                    with transaction.atomic():
                        if 'enabled' in form.changed_data:
                            # update job enabled
                            updateJobEnabled(name=name, enabled=form.cleaned_data['enabled'])
                        fsname = 'fs-' + name
                        if 'dedup' in form.changed_data:
                            # update job deduplication
                            updateFSOptionsDedup(fsname=fsname, dedup=form.cleaned_data['dedup'])
                        if 'compr' in form.changed_data:
                            # update job compression
                            updateFSOptionsCompression(fsname=fsname, compression=form.cleaned_data['compr'])
                        if 'abort' in form.changed_data:
                            # update abort_on_error
                            updateFSXenServerPlugin(job=job, abortonerror=form.cleaned_data['abort'])
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('jobsinfo', name)


@perm_required('jobs.advanced_jobs')
def kvmadvanced(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    storagededup = getStorageisDedup(job.get('Storage'))
    updatejobparamsfs(dircompid=dircompid, name=name, jobparams=job)
    if request.method == 'GET':
        data = makevmsadvanceddata(name, job)
        form = JobKVMAdvancedForm(initial=data)
        # form.fields['enabled'].disabled = True
        form.fields['compr'].disabled = data['dedup']
        context = {'contentheader': 'Advanced properities', 'apppath': ['Jobs', 'Advanced', name], 'form': form,
                   'jobstatusdisplay': 1, 'Job': job, 'Storagededup': storagededup}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/kvmadvanced.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            data = makevmsadvanceddata(name, job)
            form = JobKVMAdvancedForm(initial=data, data=request.POST)
            if form.is_valid():
                if form.has_changed():
                    with transaction.atomic():
                        if 'enabled' in form.changed_data:
                            # update job enabled
                            updateJobEnabled(name=name, enabled=form.cleaned_data['enabled'])
                        fsname = 'fs-' + name
                        if 'dedup' in form.changed_data:
                            # update job deduplication
                            updateFSOptionsDedup(fsname=fsname, dedup=form.cleaned_data['dedup'])
                        if 'compr' in form.changed_data:
                            # update job compression
                            updateFSOptionsCompression(fsname=fsname, compression=form.cleaned_data['compr'])
                        if 'abort' in form.changed_data:
                            # update abort_on_error
                            updateFSKVMPlugin(job=job, abortonerror=form.cleaned_data['abort'])
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('jobsinfo', name)


@perm_required('jobs.advanced_jobs')
def vmwareadvanced(request, name):
    dircompid = getDIRcompid(request)
    jobres = getDIRJobinfo(request, dircompid=dircompid, name=name)
    if jobres is None:
        raise Http404()
    job = extractjobparams(jobres)
    storagededup = getStorageisDedup(job.get('Storage'))
    updatejobparamsfs(dircompid=dircompid, name=name, jobparams=job)
    if request.method == 'GET':
        data = makevmsadvanceddata(name, job)
        form = JobVMwareAdvancedForm(initial=data)
        # form.fields['enabled'].disabled = True
        form.fields['compr'].disabled = data['dedup']
        context = {'contentheader': 'Advanced properities', 'apppath': ['Jobs', 'Advanced', name], 'form': form,
                   'jobstatusdisplay': 1, 'Job': job, 'Storagededup': storagededup}
        updateMenuNumbers(request, context)
        return render(request, 'jobs/vmwareadvanced.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            data = makevmsadvanceddata(name, job)
            form = JobVMwareAdvancedForm(initial=data, data=request.POST)
            if form.is_valid():
                if form.has_changed():
                    with transaction.atomic():
                        if 'enabled' in form.changed_data:
                            # update job enabled
                            updateJobEnabled(name=name, enabled=form.cleaned_data['enabled'])
                        fsname = 'fs-' + name
                        if 'dedup' in form.changed_data:
                            # update job deduplication
                            updateFSOptionsDedup(fsname=fsname, dedup=form.cleaned_data['dedup'])
                        if 'compr' in form.changed_data:
                            # update job compression
                            updateFSOptionsCompression(fsname=fsname, compression=form.cleaned_data['compr'])
                        if 'abort' in form.changed_data:
                            # update abort_on_error
                            updateFSVMwarePlugin(job=job, abortonerror=form.cleaned_data['abort'])
                    directorreload()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('jobsinfo', name)
