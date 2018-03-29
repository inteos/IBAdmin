from __future__ import unicode_literals
# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponseServerError, JsonResponse, HttpResponse
from libs.menu import updateMenuNumbers
from libs.statistic import *
from libs.system import *
from jobs.models import Job
from config.models import *
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
    npoints = 200
    # data = generate_series_stats(parname='system.cpu.util', npoints=npoints, hours=hours, field='fvalue')
    data = generate_series_fvalue_fast(parname='system.cpu.util', npoints=npoints)
    context = {'color': '#00c0ef', 'label': 'CPU Util%', 'data': data}
    return JsonResponse(context)


def backupsizewidget(request):
    npoints = 60
    # data = generate_series_stats(parname='bacula.size.jobs.bytes', npoints=npoints, hours=hours, div=1073741824.0)   # , allownull=False
    data = generate_series_nvalue_fast(parname='bacula.size.jobs.bytes', npoints=npoints, div=1073741824.0)
    barwidth = 10000000 / npoints
    context = {'color': '#39cccc', 'label': 'GBytes', 'barWidth': barwidth, 'data': data}
    return JsonResponse(context)


def runningjobswidget(request):
    npoints = 30
    data = generate_series_nvalue_fast(parname='bacula.jobs.running', npoints=npoints)
    barwidth = 8000000 / npoints
    context = {'color': '#5f5aad', 'label': 'Jobs', 'barWidth': barwidth, 'data': data}
    return JsonResponse(context)


def alljobswidget(request):
    npoints = 30
    data = generate_series_nvalue_fast(parname='bacula.jobs.all', npoints=npoints)
    context = {'color': '#001d41', 'label': 'Jobs', 'data': data}
    return JsonResponse(context)


def helppage(request, page):
    context = {}
    try:
        return render(request, 'helps/' + page + '.html', context)
    except:
        return HttpResponse('No help available for this topic.')
