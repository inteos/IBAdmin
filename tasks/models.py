from __future__ import unicode_literals

from django.db import models


TASKSSTATUS = (
        ('N', 'New task'),
        ('R', 'Running task'),
        ('F', 'Finished succesfully task'),
        ('E', 'Finished with errors task'),
        ('C', 'Task canceled'),
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
