# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from libs.widgets import *


REPLACE = (
    ('Always', 'Always'),
    ('Never', 'Never'),
    ('IfOlder', 'If Older'),
    ('IfNewer', 'If Newer'),
)


class RestoreForm(forms.Form):
    def __init__(self, clients=(), *args, **kwargs):
        super(RestoreForm, self).__init__(*args, **kwargs)
        self.fields['restoreclient'].choices = clients

    where = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Where', 'icon': 'fa fa-map', 'placeholder': 'Original location'}))
    comment = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Job comment', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    restoreclient = forms.ChoiceField(required=True, label='Restore client', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    replace = forms.ChoiceField(label='Replace mode', choices=REPLACE, required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    rselected = forms.CharField(required=True, widget=forms.HiddenInput())
    client = forms.CharField(required=True, widget=forms.HiddenInput())


class RestoreFilesForm(RestoreForm):
    def __init__(self, *args, **kwargs):
        super(RestoreFilesForm, self).__init__(*args, **kwargs)


class RestoreProxmoxForm(RestoreForm):
    def __init__(self, *args, **kwargs):
        super(RestoreProxmoxForm, self).__init__(*args, **kwargs)

    localrestore = forms.BooleanField(required=False, label='Restore to directory')
    proxmoxstorage = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Proxmox storage', 'icon': 'fa fa-database', 'placeholder': 'Original storage'}))
    proxmoxpool = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Proxmox resource pool', 'icon': 'fa fa-tags', 'placeholder': 'No pool'}))


class RestoreVMwareForm(RestoreForm):
    def __init__(self, *args, **kwargs):
        super(RestoreVMwareForm, self).__init__(*args, **kwargs)

    localrestore = forms.BooleanField(required=False, label='Restore to directory')
    datastore = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Restore to Datastore', 'icon': 'fa fa-database', 'placeholder': 'Default'}))
    restoreesx = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Restore to Host', 'icon': 'fa fa-server', 'placeholder': 'Default'}))


class RestoreXenserverForm(RestoreForm):
    def __init__(self, *args, **kwargs):
        super(RestoreXenserverForm, self).__init__(*args, **kwargs)

    localrestore = forms.BooleanField(required=False, label='Restore to directory')
    xenpreserve = forms.BooleanField(required=False, label='Preserve guest configuration')
    xenstorage = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'XenServer storage', 'icon': 'fa fa-database', 'placeholder': 'Original storage'}))
