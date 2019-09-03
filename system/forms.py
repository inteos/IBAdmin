# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from libs.forms import *
from libs.widgets import *


class SystemConfigForm(forms.Form):
    def __init__(self, storageip=(), clientip=(), storages=(), *args, **kwargs):
        super(SystemConfigForm, self).__init__(*args, **kwargs)
        self.fields['storageip'].choices = storageip
        self.fields['clientip'].choices = clientip
        self.fields['defstorage'].choices = storages

    name = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'System name', 'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    email = forms.EmailField(required=True, widget=ibadInputWidget(attrs={'label': 'Admin email', 'icon': 'glyphicon glyphicon-envelope', 'placeholder': 'email: root@localhost'}))
    retention = RetentionField(required=False, widget=ibadRetentionWidget(attrs={'label': 'Default Retention', 'value': '2 weeks'}))
    storageip = forms.ChoiceField(label='Storage IP', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    clientip = forms.ChoiceField(label='Client IP', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    defstorage = forms.ChoiceField(label='Default Storage', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    license = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'License Key', 'icon': 'fa fa-key', 'placeholder': 'xxxx-xxxx'}))
