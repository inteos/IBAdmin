# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-10 22:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Widgets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
                ('icon', models.CharField(max_length=32)),
                ('widgetid', models.CharField(max_length=32, unique=True)),
                ('template', models.TextField()),
                ('templatejs', models.TextField()),
                ('height', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.RunSQL("INSERT INTO dashboard_widgets (name, icon, widgetid, template, templatejs, height) VALUES "
                          "('System Utilization', 'fa fa-area-chart', 'cpuutilwidget', 'pages/plotwidget.html', "
                          "'pages/cpuutilwidget.js', 189);"),
        migrations.RunSQL("INSERT INTO dashboard_widgets (name, icon, widgetid, template, templatejs, height) VALUES "
                          "('Total Backup Size', 'fa fa-bar-chart', 'backupsizewidget', 'pages/plotwidget.html', "
                          "'pages/backupsizewidget.js', 189);"),
        migrations.RunSQL("INSERT INTO dashboard_widgets (name, icon, widgetid, template, templatejs, height) VALUES "
                          "('Service Status', 'fa fa-sellsy', 'servicestatuswidget', 'pages/servicestatus.html', "
                          "'pages/servicestatus.js', 189);"),
        migrations.RunSQL("INSERT INTO dashboard_widgets (name, icon, widgetid, template, templatejs, height) VALUES "
                          "('Last Jobs', 'fa fa-server', 'lastjobswidget', 'pages/lastjobs.html', "
                          "'pages/lastjobswidget.js', 189);"),
        migrations.RunSQL("INSERT INTO dashboard_widgets (name, icon, widgetid, template, templatejs, height) VALUES "
                          "('Running Jobs', 'fa fa-bar-chart', 'runningjobswidget', 'pages/plotwidget.html', "
                          "'pages/runningjobswidget.js', 189);"),
        migrations.RunSQL("INSERT INTO dashboard_widgets (name, icon, widgetid, template, templatejs, height) VALUES "
                          "('All Jobs', 'fa fa-line-chart', 'alljobswidget', 'pages/plotwidget.html', "
                          "'pages/alljobswidget.js', 189);"),
    ]
