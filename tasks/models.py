from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Tasks(models.Model):
    STATUS = (
        ('N', 'New task'),
        ('R', 'Running task'),
        ('F', 'Finished succesfully task'),
        ('E', 'Finished with errors task'),
    )
    PROCS = (
        (1, 'Delete jobids for Job'),
        (2, 'Delete jobs and jobids for Client'),
        (3, 'Detect drives for Library'),
    )
    taskid = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=False)
    proc = models.IntegerField(null=False, choices=PROCS)
    status = models.CharField(max_length=1, choices=STATUS, default='N')
    starttime = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    endtime = models.DateTimeField(blank=True, null=True)
    progress = models.IntegerField(null=False, default=0)
    params = models.TextField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    log = models.TextField(blank=True, null=True)

