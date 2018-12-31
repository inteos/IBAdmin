# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models


class ConfComponent(models.Model):
    compid = models.AutoField(primary_key=True)
    type = models.CharField(max_length=1)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = (('type', 'name'),)

    def __str__(self):
        return self.name + " (ID:" + str(self.compid) + " Type:" + self.type + ")"


class ConfRtype(models.Model):
    typeid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    equ = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ConfResource(models.Model):
    resid = models.AutoField(primary_key=True)
    compid = models.ForeignKey(ConfComponent, db_column='compid')
    type = models.ForeignKey(ConfRtype, db_column='type')
    sub = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.type) + " " + str(self.name) + "(ID:" + str(self.resid) + ") >> "


class ConfParameter(models.Model):
    parid = models.AutoField(primary_key=True)
    resid = models.ForeignKey(ConfResource, db_column='resid')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=1000)
    str = models.BooleanField(default=False)
    enc = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) + "=" + str(self.value) + " (ID:" + str(self.parid) + ")"


class Version(models.Model):
    versionid = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'version'
