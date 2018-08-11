from __future__ import unicode_literals

from django.db import models
from libs.task import TASKSSTATUS, TASKSPROCS


# Create your models here.
class Tasks(models.Model):

    taskid = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=False)
    proc = models.IntegerField(null=False, choices=TASKSPROCS)
    status = models.CharField(max_length=1, choices=TASKSSTATUS, default='N')
    starttime = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    endtime = models.DateTimeField(blank=True, null=True)
    progress = models.IntegerField(null=False, default=0)
    params = models.TextField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    log = models.TextField(blank=True, null=True)
    tpid = models.IntegerField(null=False, default=0)
