# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models
from clients.models import Client
from libs.plat import BACULACOMMUNITY


class Fileset(models.Model):
    filesetid = models.AutoField(primary_key=True)
    fileset = models.TextField()
    md5 = models.TextField()
    createtime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'fileset'


class Status(models.Model):
    jobstatus = models.CharField(primary_key=True, max_length=1)
    jobstatuslong = models.TextField(blank=True, null=True)
    severity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'status'


class Job(models.Model):
    jobid = models.AutoField(primary_key=True)
    job = models.TextField()
    name = models.TextField()
    # make dict table for FK
    type = models.CharField(max_length=1)
    # make dict table for FK
    level = models.CharField(max_length=1)
    clientid = models.ForeignKey(Client, db_column='clientid')
    # make dict table for FK
    jobstatus = models.CharField(max_length=1)
    schedtime = models.DateTimeField(blank=True, null=True)
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    realendtime = models.DateTimeField(blank=True, null=True)
    jobtdate = models.BigIntegerField(blank=True, null=True)
    volsessionid = models.IntegerField(blank=True, null=True)
    volsessiontime = models.IntegerField(blank=True, null=True)
    jobfiles = models.IntegerField(blank=True, null=True)
    jobbytes = models.BigIntegerField(blank=True, null=True)
    readbytes = models.BigIntegerField(blank=True, null=True)
    joberrors = models.IntegerField(blank=True, null=True)
    jobmissingfiles = models.IntegerField(blank=True, null=True)
    # FK to Pool model
    poolid = models.IntegerField(blank=True, null=True)
    filesetid = models.ForeignKey(Fileset, db_column='filesetid')
    priorjobid = models.IntegerField(blank=True, null=True)
    purgedfiles = models.SmallIntegerField(blank=True, null=True)
    hasbase = models.SmallIntegerField(blank=True, null=True)
    hascache = models.SmallIntegerField(blank=True, null=True)
    reviewed = models.SmallIntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    filetable = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job'

    def __str__(self):
        return self.name + " (ID:" + str(self.jobid) + ")" 


class Jobhisto(models.Model):
    jobid = models.IntegerField()
    job = models.TextField()
    name = models.TextField()
    type = models.CharField(max_length=1)
    level = models.CharField(max_length=1)
    clientid = models.ForeignKey(Client, db_column='clientid')
    jobstatus = models.CharField(max_length=1)
    schedtime = models.DateTimeField(blank=True, null=True)
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    realendtime = models.DateTimeField(blank=True, null=True)
    jobtdate = models.BigIntegerField(blank=True, null=True)
    volsessionid = models.IntegerField(blank=True, null=True)
    volsessiontime = models.IntegerField(blank=True, null=True)
    jobfiles = models.IntegerField(blank=True, null=True)
    jobbytes = models.BigIntegerField(blank=True, null=True)
    readbytes = models.BigIntegerField(blank=True, null=True)
    joberrors = models.IntegerField(blank=True, null=True)
    jobmissingfiles = models.IntegerField(blank=True, null=True)
    poolid = models.IntegerField(blank=True, null=True)
    filesetid = models.ForeignKey(Fileset, db_column='filesetid')
    priorjobid = models.IntegerField(blank=True, null=True)
    purgedfiles = models.SmallIntegerField(blank=True, null=True)
    hasbase = models.SmallIntegerField(blank=True, null=True)
    hascache = models.SmallIntegerField(blank=True, null=True)
    reviewed = models.SmallIntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    filetable = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobhisto'


class Log(models.Model):
    logid = models.AutoField(primary_key=True)
    jobid = models.ForeignKey(Job, db_column='jobid')
    time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    logtext = models.TextField()

    class Meta:
        managed = False
        db_table = 'log'


class Path(models.Model):
    pathid = models.AutoField(primary_key=True)
    path = models.TextField(blank=True, null=False)

    class Meta:
        managed = False
        db_table = 'path'


if not BACULACOMMUNITY:
    class File(models.Model):
        fileid = models.BigAutoField(primary_key=True)
        fileindex = models.IntegerField(blank=True, null=True, default=0)
        jobid = models.ForeignKey(Job, db_column='jobid')
        pathid = models.ForeignKey(Path, db_column='pathid')
        filename = models.TextField(blank=True, null=True)
        deltaseq = models.SmallIntegerField(blank=True, null=True)
        markid = models.IntegerField(blank=True, null=True)
        lstat = models.TextField(blank=True, null=True)
        md5 = models.TextField(blank=True, null=True)

        class Meta:
            managed = False
            db_table = 'file'
else:
    class Filename(models.Model):
        filenameid = models.BigAutoField(primary_key=True)
        name = models.TextField(blank=True, null=True)

        class Meta:
            managed = False
            db_table = 'filename'


    class File(models.Model):
        fileid = models.BigAutoField(primary_key=True)
        fileindex = models.IntegerField(blank=True, null=True, default=0)
        jobid = models.ForeignKey(Job, db_column='jobid')
        pathid = models.ForeignKey(Path, db_column='pathid')
        filenameid = models.ForeignKey(Filename, db_column='filenameid')
        deltaseq = models.SmallIntegerField(blank=True, null=True)
        markid = models.IntegerField(blank=True, null=True)
        lstat = models.TextField(blank=True, null=True)
        md5 = models.TextField(blank=True, null=True)

        class Meta:
            managed = False
            db_table = 'file'


class Permissions(models.Model):
    class Meta:
        managed = False
        permissions = (
            ('view_jobs', 'Can view jobs'),
            ('add_jobs', 'Can add files jobs'),
            ('add_jobs_vmware', 'Can add VMware Guest jobs'),
            ('add_jobs_proxmox', 'Can add Proxmox Guest jobs'),
            ('add_jobs_xen', 'Can add XenServer Guest jobs'),
            ('add_jobs_kvm', 'Can add KVM Guest jobs'),
            ('add_jobs_hyperv', 'Can add Hyper-V Guest jobs'),
            ('add_jobs_rhev', 'Can add RHEV Guest jobs'),
            ('add_jobs_docker', 'Can add Docker container jobs'),
            ('change_jobs', 'Can change jobs'),
            ('advanced_jobs', 'Can change jobs advanced'),
            ('delete_jobs', 'Can delete jobs'),
            ('run_jobs', 'Can run jobs'),
            ('restore_jobs', 'Can restore jobs'),
            ('cancel_jobs', 'Can cancel running jobs'),
            ('stop_jobs', 'Can stop running jobs'),
            ('restart_jobs', 'Can restart failed jobs'),
            ('comment_jobs', 'Can comment jobs'),
            ('view_datalocation', 'Can view jobs data location'),
            ('delete_jobid', 'Can delete jobs history'),
            ('status_jobs', 'Can view running job status'),
        )

