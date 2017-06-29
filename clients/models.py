from __future__ import unicode_literals

from django.db import models


class Client(models.Model):
    clientid = models.AutoField(primary_key=True)
    name = models.TextField(unique=True)
    uname = models.TextField()
    autoprune = models.SmallIntegerField(blank=True, null=True)
    fileretention = models.BigIntegerField(blank=True, null=True)
    jobretention = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'client'
