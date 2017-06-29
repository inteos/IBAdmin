from __future__ import unicode_literals
# -*- coding: UTF-8 -*-
from tasks.models import *


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
