# -*- coding: UTF-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.db import transaction
from libs.task import *
from libs.menu import updateMenuNumbers


# Create your views here.
def index(request):
    context = {'contentheader': 'Tasks', 'contentheadersmall': 'All'}
    updateMenuNumbers(context)
    return render(request, 'tasks/index.html', context)


def historydata(request):
    """ JSON for tasks history datatable """
    cols = ['taskid', 'name', 'starttime', 'endtime', '', '', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Tasks.objects.all().count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(taskid__contains=search) | Q(name__icontains=search)
        filtered = Tasks.objects.filter(f).count()
        query = Tasks.objects.filter(f).order_by(orderstr, '-taskid')[offset:offset + limit]
    else:
        filtered = total
        query = Tasks.objects.all().order_by(
            orderstr, '-taskid')[offset:offset + limit]
    data = []
    for t in query:
        if t.starttime is None:
            sstr = '-'
        else:
            sstr = t.starttime.strftime('%Y-%m-%d %H:%M:%S')
        if t.endtime is None:
            estr = '-'
        else:
            estr = t.endtime.strftime('%Y-%m-%d %H:%M:%S')
        data.append([t.taskid, t.name, sstr, estr, t.progress, t.status, [t.status, t.taskid]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@transaction.atomic
def clearall(request):
    query = Tasks.objects.filter(status__in=['F', 'E']).all()
    query.delete()
    return JsonResponse(True, safe=False)


@transaction.atomic
def delete(request, taskid):
    task = get_object_or_404(Tasks, taskid=taskid)
    task.delete()
    return JsonResponse(True, safe=False)


def progress(request, taskid):
    task = get_object_or_404(Tasks, taskid=taskid)
    context = [task.progress, str(task.progress) + '%', task.status]
    return JsonResponse(context, safe=False)


def statusnr(request):
    """ JSON for Jobsnr """
    context = {}
    updateTasksrunningnr(context)
    return JsonResponse(context)


def statuswidget(request):
    """ Tasks status widget/menu """
    context = {}
    updateTasksrunningall(context)
    return render(request, 'widgets/taskswidget.html', context)


def status(request, taskid):
    task = get_object_or_404(Tasks, taskid=taskid)
    PROCEDURE = {
        1: 'Deleting Job from configuration with job history',
        2: 'Deleting Client from configuration with job configuration and history',
        3: 'Detecting tape library and drives',
        4: 'Initializing tape library volumes for Bacula',
        5: 'Lorem ipsum...',
    }
    procedure = PROCEDURE[task.proc]
    if task.log is None:
        log = ''
    else:
        log = task.log.replace('\n', '<br>')
    if task.endtime is None:
        estr = '-'
    else:
        estr = task.endtime.strftime('%Y-%m-%d %H:%M:%S')
    context = {'contentheader': 'Tasks', 'contentheadersmall': 'All', 'Task': task, 'Procedure': procedure, 'Log': log,
               'EndTime': estr}
    updateMenuNumbers(context)
    return render(request, 'tasks/status.html', context)


def statusdata(request, taskid):
    task = get_object_or_404(Tasks, taskid=taskid)
    if task.log is None:
        log = ''
    else:
        log = task.log.replace('\n', '<br>')
    if task.endtime is None:
        estr = '-'
    else:
        estr = task.endtime.strftime('%Y-%m-%d %H:%M:%S')
    context = [task.progress, str(task.progress) + '%', estr, log, task.status]
    return JsonResponse(context, safe=False)
