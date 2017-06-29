from __future__ import unicode_literals

from django.db import models
from jobs.models import Job


class Pool(models.Model):
    poolid = models.AutoField(primary_key=True)
    name = models.TextField()
    numvols = models.IntegerField(blank=True, null=True)
    maxvols = models.IntegerField(blank=True, null=True)
    useonce = models.SmallIntegerField(blank=True, null=True)
    usecatalog = models.SmallIntegerField(blank=True, null=True)
    acceptanyvolume = models.SmallIntegerField(blank=True, null=True)
    volretention = models.BigIntegerField(blank=True, null=True)
    voluseduration = models.BigIntegerField(blank=True, null=True)
    maxvoljobs = models.IntegerField(blank=True, null=True)
    maxvolfiles = models.IntegerField(blank=True, null=True)
    maxvolbytes = models.BigIntegerField(blank=True, null=True)
    autoprune = models.SmallIntegerField(blank=True, null=True)
    recycle = models.SmallIntegerField(blank=True, null=True)
    actiononpurge = models.SmallIntegerField(blank=True, null=True)
    pooltype = models.TextField(blank=True, null=True)
    labeltype = models.IntegerField(blank=True, null=True)
    labelformat = models.TextField()
    enabled = models.SmallIntegerField(blank=True, null=True)
    scratchpoolid = models.IntegerField(blank=True, null=True)
    recyclepoolid = models.IntegerField(blank=True, null=True)
    nextpoolid = models.IntegerField(blank=True, null=True)
    migrationhighbytes = models.BigIntegerField(blank=True, null=True)
    migrationlowbytes = models.BigIntegerField(blank=True, null=True)
    migrationtime = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pool'


class Device(models.Model):
    deviceid = models.AutoField(primary_key=True)
    name = models.TextField()
    mediatypeid = models.IntegerField()
    storageid = models.IntegerField()
    devmounts = models.IntegerField()
    devreadbytes = models.BigIntegerField()
    devwritebytes = models.BigIntegerField()
    devreadbytessincecleaning = models.BigIntegerField()
    devwritebytessincecleaning = models.BigIntegerField()
    devreadtime = models.BigIntegerField()
    devwritetime = models.BigIntegerField()
    devreadtimesincecleaning = models.BigIntegerField()
    devwritetimesincecleaning = models.BigIntegerField()
    cleaningdate = models.DateTimeField(blank=True, null=True)
    cleaningperiod = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'device'


class Storage(models.Model):
    storageid = models.AutoField(primary_key=True)
    name = models.TextField()
    autochanger = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'storage'


class Media(models.Model):
    mediaid = models.AutoField(primary_key=True)
    volumename = models.TextField(unique=True)
    slot = models.IntegerField(blank=True, null=True)
    poolid = models.ForeignKey(Pool, db_column='poolid')
    mediatype = models.TextField()
    mediatypeid = models.IntegerField(blank=True, null=True)
    labeltype = models.IntegerField(blank=True, null=True)
    firstwritten = models.DateTimeField(blank=True, null=True)
    lastwritten = models.DateTimeField(blank=True, null=True)
    labeldate = models.DateTimeField(blank=True, null=True)
    voljobs = models.IntegerField(blank=True, null=True)
    volfiles = models.IntegerField(blank=True, null=True)
    volblocks = models.IntegerField(blank=True, null=True)
    volmounts = models.IntegerField(blank=True, null=True)
    volbytes = models.BigIntegerField(blank=True, null=True)
    volabytes = models.BigIntegerField(blank=True, null=True)
    volapadding = models.BigIntegerField(blank=True, null=True)
    volholebytes = models.BigIntegerField(blank=True, null=True)
    volholes = models.IntegerField(blank=True, null=True)
    volparts = models.IntegerField(blank=True, null=True)
    volerrors = models.IntegerField(blank=True, null=True)
    volwrites = models.BigIntegerField(blank=True, null=True)
    volcapacitybytes = models.BigIntegerField(blank=True, null=True)
    volstatus = models.TextField()
    enabled = models.SmallIntegerField(blank=True, null=True)
    recycle = models.SmallIntegerField(blank=True, null=True)
    actiononpurge = models.SmallIntegerField(blank=True, null=True)
    volretention = models.BigIntegerField(blank=True, null=True)
    voluseduration = models.BigIntegerField(blank=True, null=True)
    maxvoljobs = models.IntegerField(blank=True, null=True)
    maxvolfiles = models.IntegerField(blank=True, null=True)
    maxvolbytes = models.BigIntegerField(blank=True, null=True)
    inchanger = models.SmallIntegerField(blank=True, null=True)
    storageid = models.ForeignKey(Storage, db_column='storageid')
    deviceid = models.IntegerField(blank=True, null=True)
    mediaaddressing = models.SmallIntegerField(blank=True, null=True)
    volreadtime = models.BigIntegerField(blank=True, null=True)
    volwritetime = models.BigIntegerField(blank=True, null=True)
    endfile = models.IntegerField(blank=True, null=True)
    endblock = models.BigIntegerField(blank=True, null=True)
    locationid = models.IntegerField(blank=True, null=True)
    recyclecount = models.IntegerField(blank=True, null=True)
    initialwrite = models.DateTimeField(blank=True, null=True)
    scratchpoolid = models.IntegerField(blank=True, null=True)
    recyclepoolid = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'media'

    def __str__(self):
        return self.volumename + " (" + self.mediatype + ")"


class Jobmedia(models.Model):
    jobmediaid = models.AutoField(primary_key=True)
    jobid = models.ForeignKey(Job, db_column='jobid')
    mediaid = models.ForeignKey(Media, db_column='mediaid')
    firstindex = models.IntegerField(blank=True, null=True)
    lastindex = models.IntegerField(blank=True, null=True)
    startfile = models.IntegerField(blank=True, null=True)
    endfile = models.IntegerField(blank=True, null=True)
    startblock = models.BigIntegerField(blank=True, null=True)
    endblock = models.BigIntegerField(blank=True, null=True)
    volindex = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobmedia'

    def __str__(self):
        return str(self.jobmediaid) + " Media:" + str(self.mediaid) + " Job:" + str(self.jobid)


class Mediatype(models.Model):
    mediatypeid = models.AutoField(primary_key=True)
    mediatype = models.TextField()
    readonly = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mediatype'
