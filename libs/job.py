# coding=utf-8
from __future__ import unicode_literals
from django.db.models import Max
from jobs.models import *
from config.models import *
from storages.models import *
import re


def getJobsrunningnr():
    val = Job.objects.filter(jobstatus__in=['R', 'B', 'a', 'i'])
    return val.count()


def updateJobsrunningnr(context):
    val = getJobsrunningnr()
    context.update({'jobsrunning': val})


def getJobsqueuednr():
    val = Job.objects.filter(jobstatus__in=['C', 'F', 'S', 'd', 't', 'p'])
    return val.count()


def updateJobsqueuednr(context):
    val = getJobsqueuednr()
    context.update({'jobsqueued': val})


def getJobssuccessnr():
    val = Job.objects.filter(jobstatus__in=['T', 'I'], joberrors=0)
    return val.count()


def updateJobssuccessnr(context):
    val = getJobssuccessnr()
    context.update({'jobssuccess': val})


def getJobserrornr():
    val = Job.objects.filter(jobstatus__in=['E', 'f', 'A'])
    return val.count()


def updateJobserrornr(context):
    val = getJobserrornr()
    context.update({'jobserror': val})


def getJobswarningnr():
    val = Job.objects.filter(jobstatus__in=['T', 'I']).exclude(joberrors=0)
    return val.count()


def updateJobswarningnr(context):
    val = getJobswarningnr()
    context.update({'jobswarning': val})


def updateJobsnr(context):
    updateJobsrunningnr(context)
    updateJobsqueuednr(context)
    updateJobssuccessnr(context)
    updateJobserrornr(context)
    updateJobswarningnr(context)


# TODO: trzeba zastanowić się nad podejściem, czy wybierać konkretne pola tak jak poniżej, czy dawać wszystko jak leci
def getJobidinfo(jobid=None):
    if jobid is None:
        return None
    try:
        j = Job.objects.select_related('clientid').get(jobid=jobid)
    except:
        return None
    job = {
        'JobId': j.jobid,
        'Name': j.name,
        'Client': j.clientid.name,
        'Start': j.starttime,
        'Planned': j.schedtime,
        'End': j.endtime,
        'Level': j.level,
        'Files': j.jobfiles,
        'Bytes': j.jobbytes,
        'Errors': j.joberrors,
        'Status': j.jobstatus,
        'Type': j.type,
        'Comment': j.comment
    }
    return job


def updateJobidinfo(context, jobid):
    val = getJobidinfo(jobid)
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


def getJobsDefinednr():
    """
    Gives a number of defined Jobs in config database verifing if the job is available (not disabled during delete 
    operation).
    :return: a number of defined jobs
    """
    return ConfResource.objects.filter(compid__type='D', type__name='Job')\
                               .exclude(confparameter__name='.Disabledfordelete').count()


def updateJobsDefinednr(context):
    val = getJobsDefinednr()
    context.update({'jobsdefinednr': val})


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


def checkJobisrunning(name=None):
    if name is None:
        return False
    jobs = Job.objects.filter(name=name, jobstatus__in=['R', 'C']).all().count()
    return jobs > 0


def checkClientJobisrunning(name=None):
    if name is None:
        return False
    jobs = Job.objects.filter(clientid__name=name, jobstatus__in=['R', 'C']).all().count()
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

