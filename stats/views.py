# coding=utf-8
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.urls import reverse
from config.conf import *
from libs.job import extractjobparams, getleveltext
from libs.menu import updateMenuNumbers
from libs.statistic import *
from django.db.models import Q
from users.decorators import *
import datetime


bytesdict = {
    '1': [1, 'Bytes'],
    '2': [1024.0, 'kBytes'],
    '3': [1048576.0, 'MBytes'],
    '4': [1048576.0 * 1024, 'GBytes'],
    '5': [1048576.0 * 1048576, 'TBytes'],
}


timedict = {
    '1': [1, 'Seconds'],
    '2': [60.0, 'Minutes'],
    '3': [3600.0, 'Hours'],
    '4': [86400.0, 'Days'],
}


# Create your views here.
def update_charttype(context=None, chart=1, barwidth=0.75):
    if context is None:
        return
    charttype = int(chart)
    if charttype == 1:  # lines
        context.update({'lines': {'show': True}, 'points': {'show': True}})
    elif charttype == 2:  # bars
        context.update({'bars': {'show': True, 'barWidth': barwidth, 'align': 'center'}})
    elif charttype == 3:  # area
        context.update({'lines': {'show': True, 'fill': True}})
    else:
        context.update({'lines': {'show': True}, 'points': {'show': True}})


@any_perm_required('stats.view_backup_stats', 'stats.view_system_stats', 'stats.view_daemons_stats',
                   'stats.view_job_stats')
def statdata(request, name, starttime, endtime, chart, valdiv):
    param = get_object_or_404(StatParams, name=name)
    stime = datetime.datetime.fromtimestamp(int(starttime))
    etime = datetime.datetime.fromtimestamp(int(endtime))
    npoints = 150
    field = 'nvalue'
    if param.types == 'F':
        field = 'fvalue'
    data = generate_series_stats(parname=name, npoints=npoints, starttime=stime, endtime=etime, field=field,
                                 div=bytesdict[valdiv][0], allownull=False)
    td = etime - stime
    hours = td.total_seconds() / 3600
    barwidth = (hours * 2000000) / npoints
    label = param.unit
    yaxis = param.display
    if param.unit == 'Bytes':
        label = bytesdict[valdiv][1]
    elif param.unit == 'Bytes/s':
        label = bytesdict[valdiv][1] + '/sec'
    if label.startswith('Bytes'):
        yaxis = 1
    label += ' (' + name + ')'
    color = param.color or '#39cccc'
    context = {'color': color, 'label': label, 'yaxis': yaxis, 'data': data}
    if yaxis == 6 and int(chart) == 2:
        # bar chart should have a color distinguish
        context.update({'threshold': [{'below': 0.5, 'color': '#d33724'}, {'below': 2, 'color': '#008d4c'}]})
    update_charttype(context=context, chart=chart, barwidth=barwidth)
    return JsonResponse(context, safe=False)


@perm_required('stats.view_backup_stats')
def backup_jobs(request):
    params = StatDaterange.objects.filter(parid__name__contains='bacula.jobs').order_by('parid')
    context = {'contentheader': 'Backup Statistics', 'contentheadersmall': 'Jobs',
               'apppath': ['Statistics', 'Backup', 'Jobs'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_backup_stats')
def backup_volumes(request):
    params = StatDaterange.objects.filter(parid__name__contains='bacula.volumes').order_by('parid')
    context = {'contentheader': 'Backup Statistics', 'contentheadersmall': 'Volumes',
               'apppath': ['Statistics', 'Backup', 'Volumes'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_backup_stats')
def backup_tapes(request):
    params = StatDaterange.objects.filter(parid__name__contains='bacula.tape').order_by('parid')
    context = {'contentheader': 'Backup Statistics', 'contentheadersmall': 'Tapes',
               'apppath': ['Statistics', 'Backup', 'Tapes'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_backup_stats')
def backup_sizes(request):
    params = StatDaterange.objects.filter(Q(parid__name__contains='bacula.size') |
                                          Q(parid__name__contains='catalog.size')).order_by('parid')
    context = {'contentheader': 'Backup Statistics', 'contentheadersmall': 'Sizes',
               'apppath': ['Statistics', 'Backup', 'Sizes'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_system_stats')
def system_cpu(request):
    params = StatDaterange.objects.filter(parid__name__contains='system.cpu').order_by('parid')
    context = {'contentheader': 'System Statistics', 'contentheadersmall': 'CPU',
               'apppath': ['Statistics', 'System', 'CPU'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_system_stats')
def system_memory(request):
    params = StatDaterange.objects.filter(parid__name__contains='system.mem').order_by('parid')
    context = {'contentheader': 'System Statistics', 'contentheadersmall': 'Memory',
               'apppath': ['Statistics', 'System', 'Memory'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_system_stats')
def system_swap(request):
    params = StatDaterange.objects.filter(parid__name__contains='system.swap').order_by('parid')
    context = {'contentheader': 'System Statistics', 'contentheadersmall': 'Swap',
               'apppath': ['Statistics', 'System', 'Swap'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_system_stats')
def system_disks(request):
    params = StatDaterange.objects.filter(parid__name__contains='system.disk').order_by('parid')
    context = {'contentheader': 'System Statistics', 'contentheadersmall': 'Disk',
               'apppath': ['Statistics', 'System', 'Disks'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_system_stats')
def system_fs(request):
    params = StatDaterange.objects.filter(parid__name__contains='system.fs').order_by('parid')
    context = {'contentheader': 'System Statistics', 'contentheadersmall': 'Filesystems',
               'apppath': ['Statistics', 'System', 'Filesystem'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_system_stats')
def system_net(request):
    params = StatDaterange.objects.filter(parid__name__contains='system.net').order_by('parid')
    context = {'contentheader': 'System Statistics', 'contentheadersmall': 'Network interfaces',
               'apppath': ['Statistics', 'System', 'Network'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_daemons_stats')
def stats_server(request):
    params = StatDaterange.objects.filter(Q(parid__name__contains='bacula.daemon') |
                                          Q(parid__name__contains='ibadmin.daemon')).order_by('parid')
    context = {'contentheader': 'System Statistics', 'contentheadersmall': 'Server Daemons',
               'apppath': ['Statistics', 'Daemons', 'Server'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


@perm_required('stats.view_daemons_stats')
def stats_client(request):
    params = StatDaterange.objects.filter(parid__name__contains='bacula.client').order_by('parid')
    context = {'contentheader': 'System Statistics', 'contentheadersmall': 'Clients',
               'apppath': ['Statistics', 'Daemons', 'Clients'], 'params': params}
    updateMenuNumbers(request, context)
    return render(request, 'stats/default.html', context)


def define_chart_js(params=None, id=1, name=None, level='F', jtype='B'):
    if params is None or name is None:
        return
    descr = 'Level ' + getleveltext(level=level, jtype=jtype) + ' job size'
    url = reverse('statssizedata_rel', args=[name, level])
    params.append({
        'id': id,
        'descr': descr,
        'box': 'box-primary',
        'chart': 1,
        'level': level,
        'url': url,
        'unit': 1,
    })


def define_chart_fn(params=None, id=1, name=None, level='F', jtype='B'):
    if params is None or name is None:
        return
    descr = 'Level ' + getleveltext(level=level, jtype=jtype) + ' job file numbers'
    url = reverse('statsfiledata_rel', args=[name, level])
    params.append({
        'id': id,
        'descr': descr,
        'box': 'box-primary',
        'chart': 1,
        'level': level,
        'url': url,
        'unit': 0,
    })


def define_chart_tr(params=None, id=1, name=None, level='F', jtype='B'):
    if params is None or name is None:
        return
    if level == 'A':
        descr = name + ' job time running'
    else:
        descr = 'Level ' + getleveltext(level=level, jtype=jtype) + ' job time running'
    url = reverse('statstimedata_rel', args=[name, level])
    params.append({
        'id': id,
        'descr': descr,
        'box': 'box-primary',
        'chart': 1,
        'level': level,
        'url': url,
        'unit': 2,
    })


def define_chart_at(params=None, id=1, name=None, level='F', jtype='B'):
    if params is None or name is None:
        return
    descr = 'Level ' + getleveltext(level=level, jtype=jtype) + ' job average throughput'
    url = reverse('statsavgdata_rel', args=[name, level])
    params.append({
        'id': id,
        'descr': descr,
        'box': 'box-primary',
        'chart': 1,
        'level': level,
        'url': url,
        'unit': 3,
    })


@perm_required('stats.view_job_stats')
def stats_job(request, name):
    jobres = getDIRJobinfo(request, name=name)
    if jobres is None:
        raise Http404()
    jobparams = extractjobparams(jobres)
    if jobparams.get('Disabledfordelete', None):
        # the job is disabled so redirect to jobs stats
        return redirect('statsbackupjobs')
    if jobparams['Type'] == 'Admin':
        params = []
        # Job timing
        if Job.objects.filter(name=name, jobstatus='T').count() > 0:
            define_chart_tr(params=params, id=1, name=name, jtype='D')
    elif jobparams['Type'] == 'Restore':
        params = []
        # Job timing
        if Job.objects.filter(name=name, jobstatus='T').count() > 0:
            define_chart_tr(params=params, id=1, name=name, jtype='R')
            define_chart_at(params=params, id=2, name=name, jtype='R')
    else:
        # box, id, chart
        params = []
        if Job.objects.filter(name=name, level='F', jobstatus__in=['T', 'I']).count() > 0:
            define_chart_js(params=params, id=1, name=name)
            define_chart_fn(params=params, id=2, name=name)
            define_chart_tr(params=params, id=3, name=name)
            define_chart_at(params=params, id=4, name=name)
        if Job.objects.filter(name=name, level='I', jobstatus__in=['T', 'I']).count() > 0:
            define_chart_js(params=params, id=5, name=name, level='I')
            define_chart_fn(params=params, id=6, name=name, level='I')
            define_chart_tr(params=params, id=7, name=name, level='I')
            define_chart_at(params=params, id=8, name=name, level='I')
        if Job.objects.filter(name=name, level='D', jobstatus__in=['T', 'I']).count() > 0:
            define_chart_js(params=params, id=9, name=name, level='D')
            define_chart_fn(params=params, id=10, name=name, level='D')
            define_chart_tr(params=params, id=11, name=name, level='D')
            define_chart_at(params=params, id=12, name=name, level='D')

    context = {'contentheader': 'Job Statistics', 'contentheadersmall': name, 'Name': name,
               'apppath': ['Statistics', 'Job', name], 'params': params, 'jobstatsdisplay': 1}
    updateMenuNumbers(request, context)
    return render(request, 'stats/job.html', context)


def getnpoints(last=0):
    ll = int(last)
    if ll == 1:
        # last 10 jobs
        return 10
    if ll == 2:
        # last 20 jobs
        return 20
    if ll == 3:
        # last 50 jobs
        return 50
    if ll == 4:
        # last 100 jobs
        return 100
    # default
    return 10


def statsizedata(request, name, level, last, chart, valdiv):
    if level not in ['F', 'D', 'I']:
        raise Http404()
    npoints = getnpoints(last=last)
    data = generate_series_job(name=name, level=level, npoints=npoints, field='jobbytes', div=bytesdict[valdiv][0])
    label = bytesdict[valdiv][1]
    color = '#39cccc'
    context = {'color': color, 'label': label, 'data': data}
    update_charttype(context=context, chart=chart)
    return JsonResponse(context, safe=False)


def statfiledata(request, name, level, last, chart, valdiv):
    if level not in ['F', 'D', 'I']:
        raise Http404()
    npoints = getnpoints(last=last)
    data = generate_series_job(name=name, level=level, npoints=npoints, field='jobfiles', div=bytesdict[valdiv][0])
    label = 'Files'
    color = '#1919cc'
    context = {'color': color, 'label': label, 'data': data}
    update_charttype(context=context, chart=chart)
    return JsonResponse(context, safe=False)


def stattimedata(request, name, level, last, chart, valdiv):
    if level not in ['F', 'D', 'I', 'R', 'D']:
        raise Http404()
    npoints = getnpoints(last=last)
    data = generate_series_jobtime(name=name, level=level, npoints=npoints, div=timedict[valdiv][0])
    label = timedict[valdiv][1]
    color = '#990011'
    context = {'color': color, 'label': label, 'data': data}
    update_charttype(context=context, chart=chart)
    return JsonResponse(context, safe=False)


def statavgdata(request, name, level, last, chart, valdiv):
    if level not in ['F', 'D', 'I', 'R']:
        raise Http404()
    npoints = getnpoints(last=last)
    data = generate_series_jobavg(name=name, level=level, npoints=npoints, div=bytesdict[valdiv][0])
    label = bytesdict[valdiv][1] + '/s'
    color = '#009911'
    context = {'color': color, 'label': label, 'data': data}
    update_charttype(context=context, chart=chart)
    return JsonResponse(context, safe=False)
