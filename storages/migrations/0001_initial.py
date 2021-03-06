# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-12-14 07:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('deviceid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('mediatypeid', models.IntegerField()),
                ('storageid', models.IntegerField()),
                ('devmounts', models.IntegerField()),
                ('devreadbytes', models.BigIntegerField()),
                ('devwritebytes', models.BigIntegerField()),
                ('devreadbytessincecleaning', models.BigIntegerField()),
                ('devwritebytessincecleaning', models.BigIntegerField()),
                ('devreadtime', models.BigIntegerField()),
                ('devwritetime', models.BigIntegerField()),
                ('devreadtimesincecleaning', models.BigIntegerField()),
                ('devwritetimesincecleaning', models.BigIntegerField()),
                ('cleaningdate', models.DateTimeField(blank=True, null=True)),
                ('cleaningperiod', models.BigIntegerField()),
            ],
            options={
                'db_table': 'device',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Jobmedia',
            fields=[
                ('jobmediaid', models.AutoField(primary_key=True, serialize=False)),
                ('firstindex', models.IntegerField(blank=True, null=True)),
                ('lastindex', models.IntegerField(blank=True, null=True)),
                ('startfile', models.IntegerField(blank=True, null=True)),
                ('endfile', models.IntegerField(blank=True, null=True)),
                ('startblock', models.BigIntegerField(blank=True, null=True)),
                ('endblock', models.BigIntegerField(blank=True, null=True)),
                ('volindex', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'jobmedia',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('mediaid', models.AutoField(primary_key=True, serialize=False)),
                ('volumename', models.TextField(unique=True)),
                ('slot', models.IntegerField(blank=True, null=True)),
                ('mediatype', models.TextField()),
                ('mediatypeid', models.IntegerField(blank=True, null=True)),
                ('labeltype', models.IntegerField(blank=True, null=True)),
                ('firstwritten', models.DateTimeField(blank=True, null=True)),
                ('lastwritten', models.DateTimeField(blank=True, null=True)),
                ('labeldate', models.DateTimeField(blank=True, null=True)),
                ('voljobs', models.IntegerField(blank=True, null=True)),
                ('volfiles', models.IntegerField(blank=True, null=True)),
                ('volblocks', models.IntegerField(blank=True, null=True)),
                ('volmounts', models.IntegerField(blank=True, null=True)),
                ('volbytes', models.BigIntegerField(blank=True, null=True)),
                ('volabytes', models.BigIntegerField(blank=True, null=True)),
                ('volapadding', models.BigIntegerField(blank=True, null=True)),
                ('volholebytes', models.BigIntegerField(blank=True, null=True)),
                ('volholes', models.IntegerField(blank=True, null=True)),
                ('volparts', models.IntegerField(blank=True, null=True)),
                ('volerrors', models.IntegerField(blank=True, null=True)),
                ('volwrites', models.BigIntegerField(blank=True, null=True)),
                ('volcapacitybytes', models.BigIntegerField(blank=True, null=True)),
                ('volstatus', models.TextField()),
                ('enabled', models.SmallIntegerField(blank=True, null=True)),
                ('recycle', models.SmallIntegerField(blank=True, null=True)),
                ('actiononpurge', models.SmallIntegerField(blank=True, null=True)),
                ('volretention', models.BigIntegerField(blank=True, null=True)),
                ('voluseduration', models.BigIntegerField(blank=True, null=True)),
                ('maxvoljobs', models.IntegerField(blank=True, null=True)),
                ('maxvolfiles', models.IntegerField(blank=True, null=True)),
                ('maxvolbytes', models.BigIntegerField(blank=True, null=True)),
                ('inchanger', models.SmallIntegerField(blank=True, null=True)),
                ('deviceid', models.IntegerField(blank=True, null=True)),
                ('mediaaddressing', models.SmallIntegerField(blank=True, null=True)),
                ('volreadtime', models.BigIntegerField(blank=True, null=True)),
                ('volwritetime', models.BigIntegerField(blank=True, null=True)),
                ('endfile', models.IntegerField(blank=True, null=True)),
                ('endblock', models.BigIntegerField(blank=True, null=True)),
                ('locationid', models.IntegerField(blank=True, null=True)),
                ('recyclecount', models.IntegerField(blank=True, null=True)),
                ('initialwrite', models.DateTimeField(blank=True, null=True)),
                ('scratchpoolid', models.IntegerField(blank=True, null=True)),
                ('recyclepoolid', models.IntegerField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'media',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Mediatype',
            fields=[
                ('mediatypeid', models.AutoField(primary_key=True, serialize=False)),
                ('mediatype', models.TextField()),
                ('readonly', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'mediatype',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('poolid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('numvols', models.IntegerField(blank=True, null=True)),
                ('maxvols', models.IntegerField(blank=True, null=True)),
                ('useonce', models.SmallIntegerField(blank=True, null=True)),
                ('usecatalog', models.SmallIntegerField(blank=True, null=True)),
                ('acceptanyvolume', models.SmallIntegerField(blank=True, null=True)),
                ('volretention', models.BigIntegerField(blank=True, null=True)),
                ('voluseduration', models.BigIntegerField(blank=True, null=True)),
                ('maxvoljobs', models.IntegerField(blank=True, null=True)),
                ('maxvolfiles', models.IntegerField(blank=True, null=True)),
                ('maxvolbytes', models.BigIntegerField(blank=True, null=True)),
                ('autoprune', models.SmallIntegerField(blank=True, null=True)),
                ('recycle', models.SmallIntegerField(blank=True, null=True)),
                ('actiononpurge', models.SmallIntegerField(blank=True, null=True)),
                ('pooltype', models.TextField(blank=True, null=True)),
                ('labeltype', models.IntegerField(blank=True, null=True)),
                ('labelformat', models.TextField()),
                ('enabled', models.SmallIntegerField(blank=True, null=True)),
                ('scratchpoolid', models.IntegerField(blank=True, null=True)),
                ('recyclepoolid', models.IntegerField(blank=True, null=True)),
                ('nextpoolid', models.IntegerField(blank=True, null=True)),
                ('migrationhighbytes', models.BigIntegerField(blank=True, null=True)),
                ('migrationlowbytes', models.BigIntegerField(blank=True, null=True)),
                ('migrationtime', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'pool',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('storageid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('autochanger', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'storage',
                'managed': False,
            },
        ),
    ]
