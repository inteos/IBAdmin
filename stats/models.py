# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.db import models

"""
display - what plot to use [1: line plot, 2: bar plot, 3: area plot, 4:pie chart] - 0: default (bar plot)
minmax - "min:max"
color - plot color - '#RRGGBB'
box - what box color to use ['primary', 'success', 'error', 'info']
ticks - [Null, '[0, "Offline"], [1, "Online"]']
"""


class StatParams(models.Model):
    parid = models.AutoField(primary_key=True)
    types = models.CharField(max_length=1)
    name = models.TextField(unique=True)
    description = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    chart = models.IntegerField(default=0)
    display = models.IntegerField(default=1)
    color = models.TextField(default='#000000')
    box = models.TextField(default='box-primary')


class StatData(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(blank=False, null=False, db_index=True)
    parid = models.ForeignKey(StatParams, db_column='parid')
    nvalue = models.BigIntegerField(blank=True, null=True)
    fvalue = models.FloatField(blank=True, null=True)
    svalue = models.TextField(blank=True, null=True)


class StatDataHours(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    parid = models.ForeignKey(StatParams, db_column='parid')
    nvaluemin = models.BigIntegerField(blank=True, null=True)
    nvaluemax = models.BigIntegerField(blank=True, null=True)
    nvalueavg = models.BigIntegerField(blank=True, null=True)
    fvaluemin = models.FloatField(blank=True, null=True)
    fvaluemax = models.FloatField(blank=True, null=True)
    fvalueavg = models.FloatField(blank=True, null=True)


class StatDataDays(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    parid = models.ForeignKey(StatParams, db_column='parid')
    nvaluemin = models.BigIntegerField(blank=True, null=True)
    nvaluemax = models.BigIntegerField(blank=True, null=True)
    nvalueavg = models.BigIntegerField(blank=True, null=True)
    fvaluemin = models.FloatField(blank=True, null=True)
    fvaluemax = models.FloatField(blank=True, null=True)
    fvalueavg = models.FloatField(blank=True, null=True)


class StatDaterange(models.Model):
    parid = models.OneToOneField(StatParams, primary_key=True, db_column='parid')
    mintime = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    maxtime = models.DateTimeField(blank=False, null=False, auto_now_add=True)


class StatStatus(models.Model):
    parid = models.OneToOneField(StatParams, primary_key=True, db_column='parid')
    time = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    nvalue = models.BigIntegerField(blank=True, null=True)
    fvalue = models.FloatField(blank=True, null=True)
    svalue = models.TextField(blank=True, null=True)


class Permissions(models.Model):
    class Meta:
        managed = False
        permissions = (
            ('view_backup_stats', 'Can view backup statistics'),
            ('view_system_stats', 'Can view system statistics'),
            ('view_daemons_stats', 'Can view daemons statistics'),
            ('view_job_stats', 'Can view job statistics'),
        )
