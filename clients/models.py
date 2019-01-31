# -*- coding: UTF-8 -*-
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


class Permissions(models.Model):
    class Meta:
        managed = False
        permissions = (
            ('view_clients', 'Can view clients'),
            ('add_clients', 'Can add standalone clients'),
            ('add_node_clients', 'Can add cluster node clients'),
            ('add_service_clients', 'Can add cluster service clients'),
            ('add_alias_clients', 'Can add alias clients'),
            ('change_clients', 'Can change clients'),
            ('advanced_clients', 'Can change clients advanced'),
            ('delete_clients', 'Can delete clients'),
            ('status_clients', 'Can status clients'),
            ('restore_clients', 'Can restore clients'),
            ('get_configfile', 'Can download clients config file'),
            ('create_default_job', 'Can create default job for a client'),
        )
