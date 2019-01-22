# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-22 18:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('clientid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField(unique=True)),
                ('uname', models.TextField()),
                ('autoprune', models.SmallIntegerField(blank=True, null=True)),
                ('fileretention', models.BigIntegerField(blank=True, null=True)),
                ('jobretention', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'client',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Permissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'managed': False,
                'permissions': (('view_clients', 'Can view clients'), ('add_clients', 'Can add standalone clients'), ('add_node_clients', 'Can add cluster node clients'), ('add_service_clients', 'Can add cluster service clients'), ('add_alias_clients', 'Can add alias clients'), ('change_clients', 'Can change clients'), ('delete_clients', 'Can delete clients'), ('status_clients', 'Can status clients'), ('restore_clients', 'Can restore clients'), ('get_configfile', 'Can download clients config file'), ('create_default_job', 'Can create default job for a client')),
            },
        ),
    ]