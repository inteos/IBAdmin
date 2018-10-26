# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-24 07:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='confrtype',
            name='equ',
            field=models.BooleanField(default=False),
        ),
        migrations.RunSQL("INSERT INTO config_confrtype (typeid, name, equ) VALUES (17, 'SDAddresses', true);"),
        migrations.RunSQL("INSERT INTO config_confrtype (typeid, name, equ) VALUES (18, 'IP', true);"),
    ]