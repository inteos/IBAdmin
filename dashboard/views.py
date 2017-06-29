from __future__ import unicode_literals
# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponseServerError, JsonResponse
from libs.menu import updateMenuNumbers
from libs.statistic import *
from libs.system import *
from jobs.models import Job
from config.models import *
from stats.models import *
from datetime import *
# import pytz


def index(request):
    context = {'contentheader': 'Dashboard', 'contentheadersmall': 'Control Panel'}
    updateMenuNumbers(context)
    updateservicestatus(context)
    return render(request, 'pages/index.html', context)


def goeswrong(request):
    return HttpResponseServerError()


def lastjobswidget(request):
    """ Last Jobs widget """
    jdis = [a['name'] for a in ConfResource.objects.filter(compid__type='D', type__name='Job',
                                                           confparameter__name='.Disabledfordelete').values('name')]
    lastjobs = Job.objects.filter(jobstatus__in=['T', 'E', 'f', 'A', 'I']).exclude(name__in=jdis)\
                          .order_by('-jobid').values()[:4]
    elines = ''
    if len(lastjobs) < 4:
        # add missing empty lines
        elines = '0' * (4-len(lastjobs))
    context = {'LastJobs': lastjobs, 'ELines': elines}
    return render(request, 'widgets/lastjobswidget.html', context)


def cpuutilwidget(request):
    hours = 24
    npoints = 200
    data = generate_series_stats(parname='system.cpu.util', npoints=npoints, hours=hours, field='fvalue')
    context = {'color': '#00c0ef', 'label': 'CPU Util%', 'data': data}
    return JsonResponse(context)


def backupsizewidget(request):
    hours = 12
    npoints = 50
    data = generate_series_stats(parname='bacula.size.jobs.bytes', npoints=npoints, hours=hours, div=1073741824.0)   # , allownull=False
    barwidth = (hours * 2000000) / npoints
    context = {'color': '#39cccc', 'label': 'GBytes', 'barWidth': barwidth, 'data': data}
    return JsonResponse(context)


def runningjobswidget(request):
    hours = 1
    past = datetime.today() - timedelta(hours=hours)
    query = StatData.objects.filter(parid__name='bacula.jobs.bytes', time__gt=past).order_by('time')[0:hours * 60]
    data = []
    barwidth = timedelta(hours=hours).total_seconds() * 500 / query.count()
    for d in query:
        timestamp = int((d.time - datetime(1970, 1, 1)).total_seconds() * 1000)
        data.append([timestamp, d.nvalue / 1073741824.0])
    context = {'color': '#39cccc', 'label': 'GBytes', 'barWidth': barwidth, 'data': data}
    return JsonResponse(context)


def alljobswidget(request):
    hours = 1
    past = datetime.today() - timedelta(hours=hours)
    query = StatData.objects.filter(parid__name='bacula.jobs.bytes', time__gt=past).order_by('time')[0:hours * 60]
    data = []
    barwidth = timedelta(hours=hours).total_seconds() * 500 / query.count()
    for d in query:
        timestamp = int((d.time - datetime(1970, 1, 1)).total_seconds() * 1000)
        data.append([timestamp, d.nvalue / 1073741824.0])
    context = {'color': '#39cccc', 'label': 'GBytes', 'barWidth': barwidth, 'data': data}
    return JsonResponse(context)


def allfileswidget(request):
    hours = 1
    past = datetime.today() - timedelta(hours=hours)
    query = StatData.objects.filter(parid__name='bacula.jobs.bytes', time__gt=past).order_by('time')[0:hours * 60]
    data = []
    barwidth = timedelta(hours=hours).total_seconds() * 500 / query.count()
    for d in query:
        timestamp = int((d.time - datetime(1970, 1, 1)).total_seconds() * 1000)
        data.append([timestamp, d.nvalue / 1073741824.0])
    context = {'color': '#39cccc', 'label': 'GBytes', 'barWidth': barwidth, 'data': data}
    return JsonResponse(context)
