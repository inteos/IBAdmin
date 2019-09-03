# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from libs.forms import *
from libs.widgets import *

BACKUPSCH = (
    ('c1', 'Cycle during Day'),
    ('c2', 'Cycle during Week'),
    ('c3', 'Cycle during Month'),
    # ('c4', 'Cycle weekly during Month'),
)

BACKUPRPT = (
    ('r1', 'Every 1 hour (24 times a day)'),
    ('r2', 'Every 2 hours (12 times a day)'),
    ('r3', 'Every 3 hours (8 times a day)'),
    ('r4', 'Every 4 hours (6 times a day)'),
    ('r6', 'Every 6 hours (4 times a day)'),
    ('r8', 'Every 8 hours (3 times a day)'),
    ('r12', 'Every 12 hours (2 times a day)'),
    ('r24', 'Once a day (Every 24 hours)'),
)

BACKUPCOMP = (
    ('no', 'None'),
    ('lzo', 'LZO'),
    ('gzip1', 'GZIP1'),
    ('gzip4', 'GZIP4'),
    ('gzip9', 'GZIP9'),
)


class JobFormBase(forms.Form):
    def __init__(self, storages=(), clients=(), levels=None, *args, **kwargs):
        super(JobFormBase, self).__init__(*args, **kwargs)
        self.fields['storage'].choices = storages
        self.fields['client'].choices = clients
        if levels is not None:
            self.fields['scheduleweek'].choices = mergeleveltuple(off=True, levels=levels)
            self.fields['schedulemonth'].choices = mergeleveltuple(off=True, levels=levels)
            self.fields['backuplevel'].choices = mergeleveltuple(levels=levels)

    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Job name', 'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    retention = RetentionField(required=True, widget=ibadRetentionWidget(attrs={'label': 'Backup Retention', 'value': '30 Days'}))
    storage = forms.ChoiceField(label='Backup Storage', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    client = forms.ChoiceField(label='Backup Client', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    backupsch = forms.ChoiceField(label='Backup Schedule', required=True, choices=BACKUPSCH, initial='c1', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    starttime = forms.TimeField(label='Start Backup Time', required=True, widget=forms.TextInput(attrs={'class': 'form-control timepicker'}))
    backuprepeat = forms.ChoiceField(label='Backup Repeat', choices=BACKUPRPT, initial='r1', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    scheduleweek = ScheduleWeekField(label='Days of Week', choices=leveltuple(off=True), widget=ibadScheduleWeekWidget(attrs={'label': 'Days of Week'}))
    schedulemonth = ScheduleMonthField(label='Days of Month', choices=leveltuple(off=True), widget=ibadScheduleMonthWidget(attrs={'label': 'Days of Month'}))
    backuplevel = forms.ChoiceField(label='Backup Level', choices=leveltuple(), initial='full', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    backurl = forms.CharField(required=False, widget=forms.HiddenInput())


class JobFilesForm(JobFormBase):
    def __init__(self, storages=(), clients=(), *args, **kwargs):
        super(JobFilesForm, self).__init__(*args, **kwargs)
        self.fields['storage'].choices = storages
        self.fields['client'].choices = clients

    include = forms.CharField(required=True, widget=ibadTextAreaWidget(attrs={'label': 'Files to Backup', 'icon': 'fa fa-plus-square-o', 'placeholder': '/ or C:/'}))
    exclude = forms.CharField(required=False, widget=ibadTextAreaWidget(attrs={'label': 'Exclude from Backup', 'icon': 'fa fa-minus-square-o', 'placeholder': '/tmp or C:/pagefile.sys'}))


class JobProxmoxForm(JobFormBase):
    def __init__(self, storages=(), clients=(), *args, **kwargs):
        levels = {'disablediff': True, 'disableincr': True}
        super(JobProxmoxForm, self).__init__(levels=levels, *args, **kwargs)
        self.fields['storage'].choices = storages
        self.fields['client'].choices = clients

    allvms = forms.BooleanField(required=False, label='Include All VM in backup')
    include = forms.CharField(required=False, widget=ibadTextAreaWidget(attrs={'label': 'GuestVM to Backup', 'icon': 'fa fa-plus-square-o', 'placeholder': 'Guest1 or vmid=123'}))
    exclude = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Exclude from Backup', 'icon': 'fa fa-minus-square-o', 'placeholder': 'OtherGuests regex'}))


class JobXenServerForm(JobFormBase):
    def __init__(self, storages=(), clients=(), *args, **kwargs):
        levels = {'disablediff': True, 'disableincr': True}
        super(JobXenServerForm, self).__init__(levels=levels, *args, **kwargs)
        self.fields['storage'].choices = storages
        self.fields['client'].choices = clients

    allvms = forms.BooleanField(required=False, label='Include All VM in backup')
    include = forms.CharField(required=False, widget=ibadTextAreaWidget(attrs={'label': 'GuestVM to Backup', 'icon': 'fa fa-plus-square-o', 'placeholder': 'Guest1 or uuid=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'}))
    exclude = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Exclude from Backup', 'icon': 'fa fa-minus-square-o', 'placeholder': 'OtherGuests regex'}))


class JobKVMForm(JobFormBase):
    def __init__(self, storages=(), clients=(), *args, **kwargs):
        super(JobKVMForm, self).__init__(*args, **kwargs)
        self.fields['storage'].choices = storages
        self.fields['client'].choices = clients

    allvms = forms.BooleanField(required=False, label='Include All VM in backup')
    include = forms.CharField(required=False, widget=ibadTextAreaWidget(attrs={'label': 'GuestVM to Backup', 'icon': 'fa fa-plus-square-o', 'placeholder': 'Guest1'}))
    exclude = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Exclude from Backup', 'icon': 'fa fa-minus-square-o', 'placeholder': 'OtherGuests regex'}))


class JobVMwareForm(JobFormBase):
    def __init__(self, *args, **kwargs):
        levels = {'disablediff': True}
        super(JobVMwareForm, self).__init__(levels=levels, *args, **kwargs)

    allvms = forms.BooleanField(required=False, label='Include All VM in backup')
    include = forms.CharField(required=False, widget=ibadTextAreaWidget(attrs={'label': 'GuestVM to Backup', 'icon': 'fa fa-plus-square-o', 'placeholder': 'Guest1 or vm-XXXX'}))
    exclude = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Exclude from Backup', 'icon': 'fa fa-minus-square-o', 'placeholder': 'OtherGuests regex'}))


class JobAdvancedForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.HiddenInput())
    enabled = forms.BooleanField(label='Job enabled', required=False, widget=ibadToggleWidget(attrs={'label': 'Job enabled'}))
    dedup = forms.BooleanField(label='Client deduplication', required=False, widget=ibadToggleWidget(attrs={'label': 'Client deduplication'}))
    compr = forms.ChoiceField(label='Client compresion', required=False, choices=BACKUPCOMP, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))


class JobFilesAdvancedForm(JobAdvancedForm):
    runbefore = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Run Before Job', 'icon': 'fa fa-hourglass-start', 'placeholder': '...'}))
    runafter = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Run After Job', 'icon': 'fa fa-hourglass-end', 'placeholder': '...'}))


class JobProxmoxAdvancedForm(JobAdvancedForm):
    abort = forms.BooleanField(label='Abort job on error', required=False, widget=ibadToggleWidget(attrs={'label': 'Abort job on error'}))


class JobXenServerAdvancedForm(JobAdvancedForm):
    abort = forms.BooleanField(label='Abort job on error', required=False, widget=ibadToggleWidget(attrs={'label': 'Abort job on error'}))


class JobKVMAdvancedForm(JobAdvancedForm):
    abort = forms.BooleanField(label='Abort job on error', required=False, widget=ibadToggleWidget(attrs={'label': 'Abort job on error'}))


class JobVMwareAdvancedForm(JobAdvancedForm):
    abort = forms.BooleanField(label='Abort job on error', required=False, widget=ibadToggleWidget(attrs={'label': 'Abort job on error'}))


class JobAdminAdvancedForm(JobAdvancedForm):
    starttime = forms.TimeField(label='Start Backup Time', required=True, widget=forms.TextInput(attrs={'class': 'form-control timepicker'}))


class JobCatalogAdvancedForm(JobAdvancedForm):
    starttime = forms.TimeField(label='Start Backup Time', required=True, widget=forms.TextInput(attrs={'class': 'form-control timepicker'}))

