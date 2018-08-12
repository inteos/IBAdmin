from __future__ import unicode_literals
# -*- coding: UTF-8 -*-
from tasks.models import *
import os


def getTasksInfo():
    tasks = Tasks.objects.exclude(status='F').order_by('-taskid').all().values()
    return tasks


def getTasksrunningnr():
    return Tasks.objects.exclude(status='F').count()


def updateTasksrunningnr(context):
    val = getTasksrunningnr()
    context.update({'tasksrunningnr': val})


def updateTasksrunningall(context):
    val = getTasksInfo()
    context.update({'tasksrunningnr': val.count, 'tasksinfo': val})


def prepareTask(name=None, proc=0, params=None, log=None):
    if name is None or proc == 0 or params is None:
        return None
    # prepare a background task
    task = Tasks(name=name, proc=proc, params=params, log=log)
    task.save()
    taskid = task.taskid
    os.system('/opt/ibadmin/utils/ibadtasks.py ' + str(taskid))
    return taskid
