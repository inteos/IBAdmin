# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponseServerError, JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse
from libs.menu import updateMenuNumbers
from libs.statistic import *
from libs.system import *
from jobs.models import Job
from libs.user import *
from libs.job import JOBDONESTATUS


def index(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    pcol1 = profile.dashboardcol1
    if pcol1 is not None and pcol1 != '':
        col1 = pcol1.split(',')
    else:
        col1 = []
    pcol2 = profile.dashboardcol2
    if pcol2 is not None and pcol2 != '':
        col2 = pcol2.split(',')
    else:
        col2 = []
    section1 = []
    for w in col1:
        widget = Dashboardwidgets.objects.get(user=user, widget__widgetid=w)
        if widget.enabled:
            section1.append(widget)
    section2 = []
    for w in col2:
        widget = Dashboardwidgets.objects.get(user=user, widget__widgetid=w)
        if widget.enabled:
            section2.append(widget)
    context = {'contentheader': 'Dashboard', 'contentheadersmall': 'Control Panel',
               'Section1': section1, 'Section2': section2}
    updateMenuNumbers(request, context)
    updateservicestatus(context)
    # messages.info(request, 'Three credits <a href="%s">remain</a> in your account.' % reverse('home'),
    #               extra_tags='AAA')
    # messages.error(request, 'It is a standard error.', extra_tags='ERROR')
    # messages.warning(request, 'about something.', extra_tags='Warning')
    return render(request, 'pages/index.html', context)


def goeswrong(request):
    return HttpResponseServerError()


def nodbavailable(request):
    return render(request, "pages/nodbavailable.html")


def lastjobswidget(request):
    """ Last Jobs widget """
    userjobs = getUserJobsNames(request)
    lastjobs = Job.objects.filter(name__in=userjobs, jobstatus__in=JOBDONESTATUS).order_by('-jobid').values()[:4]
    elines = ''
    if len(lastjobs) < 4:
        # add missing empty lines
        elines = '0' * (4-len(lastjobs))
    context = {'LastJobs': lastjobs, 'ELines': elines}
    return render(request, 'pages/lastjobswidget.html', context)


def cpuutilwidget(request):
    npoints = 200
    # data = generate_series_stats(parname='system.cpu.util', npoints=npoints, hours=hours, field='fvalue')
    data = generate_series_fvalue_fast(parname='system.cpu.util', npoints=npoints)
    context = {'color': '#00c0ef', 'label': 'CPU Util%', 'data': data}
    return JsonResponse(context)


def backupsizewidget(request):
    npoints = 60
    # data = generate_series_stats(parname='bacula.size.jobs.bytes', npoints=npoints, hours=hours, div=1073741824.0)
    # , allownull=False
    data, prefix = generate_series_nvalue_fast_auto(parname='bacula.size.jobs.bytes', npoints=npoints)
    barwidth = 10000000 / npoints
    context = {'color': '#39cccc', 'label': prefix + 'Bytes', 'barWidth': barwidth, 'data': data}
    return JsonResponse(context)


def runningjobswidget(request):
    npoints = 30
    data = generate_series_nvalue_fast(parname='bacula.jobs.running', npoints=npoints)
    barwidth = 8000000 / npoints
    context = {'color': '#5f5aad', 'label': 'Jobs', 'barWidth': barwidth, 'data': data}
    return JsonResponse(context)


def alljobswidget(request):
    npoints = 60
    data = generate_series_nvalue_fast(parname='bacula.jobs.all', npoints=npoints)
    context = {'color': '#001d41', 'label': 'Jobs', 'data': data}
    return JsonResponse(context)


def helppage(request, page):
    context = {}
    try:
        return render(request, 'helps/' + page + '.html', context)
    except:
        return HttpResponse('No help available for this topic.')


def changewidgets(request, sectionid):
    widgets = request.GET.getlist('widgetid[]')
    profile = Profile.objects.get(user=request.user)
    widgetstr = ''
    if widgets:
        widgetstr = ','.join(widgets)
    if sectionid == 'col1':
        profile.dashboardcol1 = widgetstr
        profile.save(update_fields=['dashboardcol1'])
    else:
        profile.dashboardcol2 = widgetstr
        profile.save(update_fields=['dashboardcol2'])
    return JsonResponse(True, safe=False)
