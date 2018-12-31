# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import transaction
from config.conf import *
from jobs.models import *
from storages.models import *
from config.confinfo import *
from libs.forms import *
import re
from datetime import *


JOBRUNNINGSTATUS = ['R', 'B', 'a', 'i']
JOBQUEUEDSTATUS = ['C', 'F', 'S', 'd', 't', 'p']
JOBTERMINATESTATUS = ['T', 'I']
JOBERRORSTATUS = ['E', 'f', 'A']
JOBDONESTATUS = JOBTERMINATESTATUS + JOBERRORSTATUS
JOBSEXECSTATUS = JOBRUNNINGSTATUS + JOBQUEUEDSTATUS
JOBALLSTATUS = JOBDONESTATUS + JOBSEXECSTATUS


def getJobsrunningnr(request):
    if not hasattr(request, "ibadminjobsrunningnr"):
        userjobs = getUserJobsnames(request)
        val = Job.objects.filter(jobstatus__in=JOBRUNNINGSTATUS, name__in=userjobs)
        request.ibadminjobsrunningnr = val.count()
    return request.ibadminjobsrunningnr


def updateJobsrunningnr(request, context):
    val = getJobsrunningnr(request)
    context.update({'jobsrunning': val})


def getJobsqueuednr(request):
    if not hasattr(request, "ibadminjobsqueuednr"):
        userjobs = getUserJobsnames(request)
        val = Job.objects.filter(jobstatus__in=JOBQUEUEDSTATUS, name__in=userjobs)
        request.ibadminjobsqueuednr = val.count()
    return request.ibadminjobsqueuednr


def updateJobsqueuednr(request, context):
    val = getJobsqueuednr(request)
    context.update({'jobsqueued': val})


def getJobssuccessnr(request):
    if not hasattr(request, "ibadminjobssuccessnr"):
        userjobs = getUserJobsnames(request)
        val = Job.objects.filter(jobstatus__in=JOBTERMINATESTATUS, joberrors=0, name__in=userjobs)
        request.ibadminjobssuccessnr = val.count()
    return request.ibadminjobssuccessnr


def updateJobssuccessnr(request, context):
    val = getJobssuccessnr(request)
    context.update({'jobssuccess': val})


def getJobserrornr(request):
    if not hasattr(request, "ibadminjobserrornr"):
        userjobs = getUserJobsnames(request)
        val = Job.objects.filter(jobstatus__in=JOBERRORSTATUS, name__in=userjobs)
        request.ibadminjobserrornr = val.count()
    return request.ibadminjobserrornr


def updateJobserrornr(request, context):
    val = getJobserrornr(request)
    context.update({'jobserror': val})


def getJobswarningnr(request):
    if not hasattr(request, "ibadminjobswarningnr"):
        userjobs = getUserJobsnames(request)
        val = Job.objects.filter(jobstatus__in=JOBTERMINATESTATUS, name__in=userjobs).exclude(joberrors=0)
        request.ibadminjobswarningnr = val.count()
    return request.ibadminjobswarningnr


def updateJobswarningnr(request, context):
    val = getJobswarningnr(request)
    context.update({'jobswarning': val})


def getJobsDefinednr(request, dircompid=None):
    """
    Gives a number of defined Jobs in config database verifing if the job is available (not disabled during delete
    operation).
    :return: a number of defined jobs
    """
    if not hasattr(request, "ibadminjobsdefinednr"):
        request.ibadminjobsdefinednr = getUserJobs(request, dircompid=dircompid).count()
    return request.ibadminjobsdefinednr


def updateJobsDefinednr(request, context):
    val = getJobsDefinednr(request)
    context.update({'jobsdefinednr': val})


def updateJobsnr(request, context):
    updateJobsrunningnr(request, context)
    updateJobsqueuednr(request, context)
    updateJobssuccessnr(request, context)
    updateJobserrornr(request, context)
    updateJobswarningnr(request, context)


# TODO: trzeba zastanowić się nad podejściem, czy wybierać konkretne pola tak jak poniżej, czy dawać wszystko jak leci
def getJobInfo(job=None):
    if job is None:
        return None
    jobinfo = {
        'JobId': job.jobid,
        'Name': job.name,
        'Client': job.clientid.name,
        'Start': job.starttime,
        'Planned': job.schedtime,
        'End': job.endtime,
        'Level': job.level,
        'Files': job.jobfiles,
        'Bytes': job.jobbytes,
        'Errors': job.joberrors,
        'Status': job.jobstatus,
        'Type': job.type,
        'Comment': job.comment
    }
    return jobinfo


def getJobidinfo(request, jobid):
    userjobs = getUserJobsnames(request)
    try:
        j = Job.objects.select_related('clientid').get(jobid=jobid, name__in=userjobs)
    except ObjectDoesNotExist:
        return None
    return getJobInfo(j)


def updateJobidinfo(request, context, jobid):
    val = getJobidinfo(request, jobid)
    context.update({'Job': val})


def getJobidLogtext(jobid):
    data = Log.objects.filter(jobid=jobid).order_by('logid').all()
    log = []
    jobhl = 0
    pattern = re.compile(r'(\S+ JobId \d+: )([-rwxdsl]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+'
                         r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.*)')
    for l in data:
        m = pattern.match(l.logtext)
        if m is None:
            text = l.logtext.replace('\n', '<br>')
            if ' ERR=' in text or ' Fatal error: ' in text or ' Error: ' in text or 'ABORTING due to ERROR' in text:
                hl = 1
                jobhl = 1
            else:
                hl = 0
            log.append({'Text': text, 'Time': l.time, 'HL': hl})
    return log, jobhl


def updateJobidLogtext(context, jobid):
    (log, jobhl) = getJobidLogtext(jobid)
    context.update({'Log': log, 'LogHL': jobhl})


def getJobidVolumedata(jobid):
    data = Jobmedia.objects.select_related('mediaid').filter(jobid=jobid).distinct('mediaid').all()
    vol = []
    for d in data:
        v = {
            'Name': d.mediaid.volumename,
            'MediaType': d.mediaid.mediatype,
            'Status': d.mediaid.volstatus,
            'Bytes': d.mediaid.volbytes,
        }
        vol.append(v)
    return vol


def updateJobidVolumes(context, jobid):
    vol = getJobidVolumedata(jobid)
    context.update({'Volumelist': vol})


def extractjobparams(jobres):
    jobparams = {'Name': jobres['Name'], 'Descr': jobres['Descr'], 'Type': jobres['Type']}
    for param in jobres['Params']:
        jobparams[param['name'].replace('.', '')] = param['value']
    # print jobparams
    return jobparams


def getJobInternal(name):
    """
    Verifies if a supplied jobname id internal job or not.
    :param name: jobname to verify
    :return: 1 when a job is internal or 0 when it is not
    """
    return ConfParameter.objects.filter(name='.InternalJob', resid__name=name, resid__type__name='Job').count()


def getJobDisabledfordelete(name):
    """
    Verifies if a supplied jobname id internal job or not.
    :param name: jobname to verify
    :return: 1 when a job is internal or 0 when it is not
    """
    return ConfParameter.objects.filter(name='.Disabledfordelete', resid__name=name, resid__type__name='Job').count()


def getJobmaxfiles(name):
    return Job.objects.filter(name=name).aggregate(Max('jobfiles'))['jobfiles__max']


def getJobmaxbytes(name):
    return Job.objects.filter(name=name).aggregate(Max('jobbytes'))['jobbytes__max']


def checkJobisrunning(name=None):
    if name is None:
        return False
    jobs = Job.objects.filter(name=name, jobstatus__in=JOBSEXECSTATUS).all().count()
    return jobs > 0


def checkClientJobisrunning(name=None):
    if name is None:
        return False
    jobs = Job.objects.filter(clientid__name=name, jobstatus__in=JOBSEXECSTATUS).all().count()
    if jobs > 0:
        return 1
    return 0


def getleveltext(level=None, jtype=None):
    if jtype is not None:
        if jtype == 'R' or jtype == 'Restore':
            return "Restore"
        if jtype == 'D' or jtype == '' or jtype == 'Admin' or level == ' ' or level == '':
            return "Admin"
    if level == 'F' or level == 'full':
        return "Full"
    if level == 'D' or level == 'diff':
        return "Differential"
    if level == 'I' or level == 'incr':
        return "Incremental"
    return level


def jobparamsclientkey(jobparams):
    return getparamskey(jobparams, 'Client')


def jobparamsnamekey(jobparams):
    return jobparams['Name']


def jobparamsdescrkey(jobparams):
    return jobparams['Descr']


def jobparamspoolkey(jobparams):
    val = getparamskey(jobparams, 'Pool')
    if val == 'Default':
        val = 'Pool-2-weeks'
    return val


def jobparamsstoragekey(jobparams):
    return getparamskey(jobparams, 'Storage')


def jobparamslevelkey(jobparams):
    val = getparamskey(jobparams, 'Level')
    if val == '':
        val = jobparams['Type']
    return val


def getDIRJobsListfiltered(request, dircompid=None, cols=(), client=None):
    if dircompid is None:
        dircompid = getDIRcompid(request)
    # List of the all jobs resources available
    search = request.GET['search[value]']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    userjobs = getUserJobs(request, dircompid)
    if client is not None:
        userjobs = userjobs.filter(confparameter__name='Client', confparameter__value=client)
    total = userjobs.count()
    if search != '':
        f = Q(name__icontains=search) | Q(description__icontains=search)
        filtered = userjobs.filter(f).count()
        jobsres = userjobs.filter(f).order_by('name')
    else:
        filtered = total
        jobsres = userjobs.order_by('name')
    jobslist = []
    for jr in jobsres:
        jobparams = getDIRJobparams(request, dircompid=dircompid, jobres=jr)
        jobslist.append(jobparams)
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = True if 'desc' == request.GET['order[0][dir]'] else False
    sjobslist = sorted(jobslist, key=order_col, reverse=order_dir)[offset:offset + limit]
    return sjobslist, total, filtered


def getJobsfiltered(request, dircompid=None, jobstatus=(), joberrors=None, cols=(), totalquery=None):
    # TODO: add exclude filter
    # List of the all jobs in job table
    if dircompid is None:
        dircompid = getDIRcompid(request)
    userjobs = getUserJobsnames(request, dircompid)
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    search = request.GET['search[value]']
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    if totalquery is None:
        totalquery = Job.objects.filter(jobstatus__in=jobstatus, name__in=userjobs)
    if joberrors is not None:
        if joberrors:
            totalquery = totalquery.exclude(joberrors=0)
        else:
            totalquery = totalquery.filter(joberrors=0)
    total = totalquery.count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        query = totalquery.select_related('clientid').filter(f)
        filtered = query.count()
    else:
        filtered = total
        query = totalquery.select_related('clientid')
    query = query.order_by(orderstr, '-jobid')[offset:offset + limit]
    jobslist = []
    for j in query:
        jobinfo = getJobInfo(j)
        jobslist.append(jobinfo)
    return jobslist, total, filtered


def updatejobparamsfs(dircompid=None, name=None, jobparams=(), fsname=None):
    if name is None:
        return
    if dircompid is None:
        dircompid = getDIRcompid()
    if fsname is None:
        fsname = 'fs-' + name
    fsoptions = getDIRFSoptions(dircompid=dircompid, name=fsname)
    dedup = False
    compression = None
    for param in fsoptions:
        if param['name'] == 'Dedup':
            dedup = True
        if param['name'] == 'Compression':
            compression = param['value'].lower()
    jobparams['Dedup'] = dedup
    jobparams['Compression'] = compression


def makefilesadvanceddata(name, job):
    data = {
        'name': name,
        'enabled': job['Enabled'] == 'Yes',
        'runbefore': job.get('ClientRunBeforeJob', ''),
        'runafter': job.get('ClientRunAfterJob', ''),
        'dedup': job.get('Dedup'),
        'compr': job.get('Compression') or 'no',
    }
    return data


def makevmsadvanceddata(name, job):
    data = {
        'name': name,
        'enabled': job['Enabled'] == 'Yes',
        'dedup': job.get('Dedup'),
        'compr': job.get('Compression') or 'no',
        'abort': job.get('AbortOnError') == 'True',
    }
    return data


def makeadminadvanceddata(name, job):
    data = {
        'name': name,
        'enabled': job['Enabled'] == 'Yes',
        'starttime': datetime.strptime(job['Scheduletime'], '%H:%M').time(),
    }
    return data


def makecatalogadvanceddata(name, job):
    data = {
        'name': name,
        'enabled': job['Enabled'] == 'Yes',
        'starttime': datetime.strptime(job['Scheduletime'], '%H:%M').time(),
        'compr': job.get('Compression') or 'no',
    }
    return data


def makeinitialdatafiles(name, job, backurl):
    (backupsch, backuprepeat) = job['Scheduleparam'].split(':')
    (inclist, exclist, optionlist) = getDIRFSparams(name='fs-' + name)
    include = ''
    for i in inclist:
        if len(include):
            include += '\r\n'           # TODO required for textarea handling, but it is a platform specific
        include += i['value']
    exclude = ''
    for e in exclist:
        if len(exclude):
            exclude += '\r\n'           # TODO required for textarea handling, but it is a platform specific
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
        'backurl': backurl,
    }
    return data


def makeinitialdatavms(name, job, backurl):
    (backupsch, backuprepeat) = job['Scheduleparam'].split(':')
    inclist = job['Objsinclude'].split(':')
    include = ''
    for i in inclist:
        if len(include):
            include += '\r\n'           # TODO required for textarea handling, but it is a platform specific
        include += i
    exclude = job['Objsexclude']
    if job['Allobjs'] == 'True':
        allvms = True
    else:
        allvms = False
    data = {
        'name': name,
        'descr': job['Descr'],
        'retention': getretentionform(job['Pool']),
        'storage': job['Storage'],
        'client': job['Client'],
        'allvms': allvms,
        'include': include,
        'exclude': exclude,
        'backupsch': backupsch,
        'starttime': datetime.strptime(job['Scheduletime'], '%H:%M').time(),
        'backuprepeat': backuprepeat,
        'backuplevel': level2form(job['Level']),
        'scheduleweek': job['Scheduleweek'],
        'schedulemonth': job['Schedulemonth'],
        'backurl': backurl,
    }
    return data


def updatejobparams(name=None, form=None, forcelevel=None):
    if form is None or name is None:
        return
    if 'descr' in form.changed_data:
        # print "Update description"
        with transaction.atomic():
            updateDIRJobDescr(name=name, descr=form.cleaned_data['descr'])
    if 'storage' in form.changed_data:
        # print "Update storage"
        with transaction.atomic():
            updateJobStorage(name=name, storage=form.cleaned_data['storage'])
    if 'client' in form.changed_data:
        # print "Update client"
        with transaction.atomic():
            updateJobClient(name=name, client=form.cleaned_data['client'])
    if 'backupsch' in form.changed_data or 'starttime' in form.changed_data or \
       'scheduleweek' in form.changed_data or 'schedulemonth' in form.changed_data or \
       'backuprepeat' in form.changed_data or 'backuplevel' in form.changed_data:
        # update Schedule
        with transaction.atomic():
            updateJobSchedule(jobname=name, data=form.cleaned_data, forcelevel=forcelevel)
    if 'retention' in form.changed_data:
        # update retention
        with transaction.atomic():
            updateJobRetention(name=name, retention=form.cleaned_data['retention'])
