# -*- coding: UTF-8 -*-
from stats.models import *
from jobs.models import *
from datetime import *
from django.db.models import Avg, Max, Min


def generate_series_stats(parname=None, starttime=None, endtime=None, hours=1, npoints=0, aggregate='Max',
                          field='nvalue', div=1, allownull=False):
    if parname is None or npoints == 0:
        return None
    agg = Max(field)
    ragg = field + '__max'
    if aggregate == 'Avg':
        agg = Avg(field)
        ragg = field + '__avg'
    if aggregate == 'Min':
        agg = Min(field)
        ragg = field + '__min'
    if div == 0:
        div = 1
    if endtime is None:
        endtime = datetime.today()
    if starttime is None:
        starttime = endtime - timedelta(hours=hours)
    delta = (endtime - starttime) / npoints
    st = starttime
    et = st + delta
    data = []
    for i in range(npoints):
        query = StatData.objects.filter(parid__name=parname, time__range=(st, et)).aggregate(agg)
        st = et
        et += delta
        value = query[ragg]
        if value is None:
            if allownull:
                value = 0
            else:
                continue
        timestamp = int((st - datetime(1970, 1, 1)).total_seconds() * 1000)
        data.append([timestamp, value / div])
    return data


def generate_series_job(name=None, level='F', npoints=0, field=None, div=1):
    if name is None or npoints == 0 or field is None:
        return None
    query = Job.objects.filter(name=name, level=level, jobstatus__in=['T', 'I']).order_by('-jobid').values()[:npoints][::-1]
    data = []
    for i, j in enumerate(query):
        data.append([i, j[field] / div])
    return data


def generate_series_jobtime(name=None, level='F', npoints=0, div=1):
    if name is None or npoints == 0:
        return None
    if level == 'R':
        query = Job.objects.filter(name=name, type='R', jobstatus__in=['T', 'I']).order_by('-jobid').values()[:npoints][::-1]
    else:
        query = Job.objects.filter(name=name, level=level, jobstatus__in=['T', 'I']).order_by('-jobid').values()[:npoints][::-1]
    data = []
    for i, j in enumerate(query):
        td = j['endtime'] - j['starttime']
        data.append([i, td.total_seconds() / div])
    return data


def generate_series_jobavg(name=None, level='F', npoints=0, div=1):
    if name is None or npoints == 0:
        return None
    if level == 'R':
        query = Job.objects.filter(name=name, type='R', jobstatus__in=['T', 'I']).order_by('-jobid').values()[:npoints][::-1]
    else:
        query = Job.objects.filter(name=name, level=level, jobstatus__in=['T', 'I']).order_by('-jobid').values()[:npoints][::-1]
    data = []
    for i, j in enumerate(query):
        td = (j['endtime'] - j['starttime']).total_seconds()
        if td > 0:
            size = j['jobbytes']
            avg = 1.0 * size / td
        else:
            avg = 0
        data.append([i, avg / div])
    return data
