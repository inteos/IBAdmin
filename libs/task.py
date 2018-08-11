from __future__ import unicode_literals
# -*- coding: UTF-8 -*-
from tasks.models import *
import os

TASKSSTATUS = (
        ('N', 'New task'),
        ('R', 'Running task'),
        ('F', 'Finished succesfully task'),
        ('E', 'Finished with errors task'),
    )

TASKSPROCS = (
        (1, 'Delete jobids for Job'),
        (2, 'Delete jobs and jobids for Client'),
        (3, 'Detect drives for Library'),
        (4, 'Labeling tape volumes'),
        (5, 'Rescanning drives for Library'),
    )

TASKSPROCSDESCR = {
        1: 'Deleting Job from configuration with job history',
        2: 'Deleting Client from configuration with job configuration and history',
        3: 'Detecting tape library and drives',
        4: 'Initializing tape library volumes for Bacula',
        5: 'Rescanning tape library for hardware changes',
    }


def getTasksInfo():
    tasks = Tasks.objects.filter(status__in=['R', 'N', 'E']).order_by('-taskid').all().values()
    return tasks


def getTasksrunningnr():
    return Tasks.objects.filter(status__in=['R', 'N', 'E']).count()


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
