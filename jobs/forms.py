# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from libs.forms import *
from libs.widgets import *

BACKUPSCH = (
    ('c1', 'Cycle during Day'),
    ('c2', 'Cycle during Week'),
    ('c3', 'Cycle during Month'),
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


class JobFilesForm(forms.Form):
    def __init__(self, storages=(), clients=(), *args, **kwargs):
        super(JobFilesForm, self).__init__(*args, **kwargs)
        self.fields['storage'].choices = storages
        self.fields['client'].choices = clients

    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Job name', 'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    retention = RetentionField(required=True, widget=ibadRetentionWidget(attrs={'label': 'Backup Retention', 'value': '30 Days'}))
    storage = forms.ChoiceField(label='Backup Storage', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    client = forms.ChoiceField(label='Backup Client', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    include = forms.CharField(required=True, widget=ibadTextAreaWidget(attrs={'label': 'Files to Backup', 'icon': 'fa fa-plus-square-o', 'placeholder': '/ or C:/'}))
    exclude = forms.CharField(required=False, widget=ibadTextAreaWidget(attrs={'label': 'Exclude from Backup', 'icon': 'fa fa-minus-square-o', 'placeholder': '/tmp or C:/pagefile.sys'}))
    backupsch = forms.ChoiceField(label='Backup Schedule', required=True, choices=BACKUPSCH, initial='c1', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    starttime = forms.TimeField(label='Start Backup Time', required=True, widget=forms.TextInput(attrs={'class': 'form-control timepicker'}))
    backuprepeat = forms.ChoiceField(label='Backup Repeat', choices=BACKUPRPT, initial='r1', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    backuplevel = forms.ChoiceField(label='Backup Level', choices=leveltuple(), initial='full', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    scheduleweek = ScheduleWeekField(label='Days of Week', choices=leveltuple(off=True), widget=ibadScheduleWeekWidget(attrs={'label': 'Days of Week'}))
    schedulemonth = ScheduleMonthField(label='Days of Month', choices=leveltuple(off=True), widget=ibadScheduleMonthWidget(attrs={'label': 'Days of Month'}))


class JobProxmoxForm(forms.Form):
    def __init__(self, storages=(), clients=(), *args, **kwargs):
        super(JobProxmoxForm, self).__init__(*args, **kwargs)
        self.fields['storage'].choices = storages
        self.fields['client'].choices = clients

    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Job name', 'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    retention = RetentionField(required=True, widget=ibadRetentionWidget(attrs={'label': 'Backup Retention', 'value': '30 Days'}))
    storage = forms.ChoiceField(label='Backup Storage', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    client = forms.ChoiceField(label='Backup Client', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    allvms = forms.BooleanField(required=False, label='Include All VM in backup')
    include = forms.CharField(required=False, widget=ibadTextAreaWidget(attrs={'label': 'GuestVM to Backup', 'icon': 'fa fa-plus-square-o', 'placeholder': 'Guest1 or vmid=123'}))
    exclude = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Exclude from Backup', 'icon': 'fa fa-minus-square-o', 'placeholder': 'OtherGuests regex'}))
    backupsch = forms.ChoiceField(label='Backup Schedule', required=True, choices=BACKUPSCH, initial='c1', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    starttime = forms.TimeField(label='Start Backup Time', required=True, widget=forms.TextInput(attrs={'class': 'form-control timepicker'}))
    backuprepeat = forms.ChoiceField(label='Backup Repeat', choices=BACKUPRPT, initial='r1', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    scheduleweek = ScheduleWeekField(label='Days of Week', choices=leveltuple(off=True, disableincr=True, disablediff=True), widget=ibadScheduleWeekWidget(attrs={'label': 'Days of Week'}))
    schedulemonth = ScheduleMonthField(label='Days of Month', choices=leveltuple(off=True, disableincr=True, disablediff=True), widget=ibadScheduleMonthWidget(attrs={'label': 'Days of Month'}))


class JobFilesAdvancedForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.HiddenInput())
    enabled = forms.BooleanField(label='Job enabled', required=False, widget=ibadToggleWidget(attrs={'label': 'Job enabled'}))
    runbefore = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Run Before Job', 'icon': 'fa fa-hourglass-start', 'placeholder': '...'}))
    runafter = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Run After Job', 'icon': 'fa fa-hourglass-end', 'placeholder': '...'}))
    dedup = forms.BooleanField(label='Client deduplication', required=False, widget=ibadToggleWidget(attrs={'label': 'Client deduplication'}))
    compr = forms.ChoiceField(label='Client compresion', required=False, choices=BACKUPCOMP, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))


class JobProxmoxAdvancedForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.HiddenInput())
    enabled = forms.BooleanField(label='Job enabled', required=False, widget=ibadToggleWidget(attrs={'label': 'Job enabled'}))
    dedup = forms.BooleanField(label='Client deduplication', required=False, widget=ibadToggleWidget(attrs={'label': 'Client deduplication'}))
    compr = forms.ChoiceField(label='Client compresion', required=False, choices=BACKUPCOMP, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))


class JobAdminAdvancedForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.HiddenInput())
    enabled = forms.BooleanField(label='Job enabled', required=False, widget=ibadToggleWidget(attrs={'label': 'Job enabled'}))
    starttime = forms.TimeField(label='Start Backup Time', required=True, widget=forms.TextInput(attrs={'class': 'form-control timepicker'}))


class JobCatalogAdvancedForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.HiddenInput())
    enabled = forms.BooleanField(label='Job enabled', required=False, widget=ibadToggleWidget(attrs={'label': 'Job enabled'}))
    starttime = forms.TimeField(label='Start Backup Time', required=True, widget=forms.TextInput(attrs={'class': 'form-control timepicker'}))
    compr = forms.ChoiceField(label='Client compresion', required=False, choices=BACKUPCOMP, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
