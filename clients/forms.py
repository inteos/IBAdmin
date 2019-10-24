# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from libs.widgets import *
from libs.ibadmin import ibadmin_oslist


class ClientForm(forms.Form):
    def __init__(self, departments=(), *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.fields['departments'].choices = departments

    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Client name',
                                                                        'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description',
                                                                          'icon': 'fa fa-commenting-o',
                                                                          'placeholder': '...'}))
    departments = forms.ChoiceField(label='Department', required=True,
                                    widget=forms.Select(attrs={'class': 'form-control select2',
                                                               'style': 'width: 100%;'}))
    defjob = forms.BooleanField(label='Create default backup Job', required=False)
    backurl = forms.CharField(required=False, widget=forms.HiddenInput())


class ClientStdForm(ClientForm):
    address = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Address',
                                                                           'icon': 'fa fa-envelope-o',
                                                                           'placeholder': 'Address'}))
    os = forms.ChoiceField(label='Server OS', choices=ibadmin_oslist(), required=True,
                           widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))


class ClientNodeForm(ClientForm):
    def __init__(self, clusters=(), *args, **kwargs):
        super(ClientNodeForm, self).__init__(*args, **kwargs)
        self.fields['clusterlist'].choices = clusters

    cluster = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'New Cluster name',
                                                                            'icon': 'fa fa-cubes',
                                                                            'placeholder': 'Name or ...'}))
    clusterlist = forms.ChoiceField(label='Existing Cluster', required=False,
                                    widget=forms.Select(attrs={'class': 'select2 form-control',
                                                               'style': 'width: 100%;'}))
    address = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Address',
                                                                           'icon': 'fa fa-envelope-o',
                                                                           'placeholder': 'Address'}))
    os = forms.ChoiceField(label='Server OS', choices=ibadmin_oslist(), required=True,
                           widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))


class ClientServiceForm(ClientForm):
    def __init__(self, clusters=(), *args, **kwargs):
        super(ClientServiceForm, self).__init__(*args, **kwargs)
        self.fields['cluster'].choices = clusters

    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Service name', 'icon': 'fa fa-paw',
                                                                        'placeholder': 'Name'}))
    cluster = forms.ChoiceField(label='Cluster name', required=True,
                                widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    address = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Address',
                                                                           'icon': 'fa fa-envelope-o',
                                                                           'placeholder': 'Address'}))


class ClientAliasForm(ClientForm):
    def __init__(self, clients=(), *args, **kwargs):
        super(ClientAliasForm, self).__init__(*args, **kwargs)
        self.fields['client'].choices = clients

    name = forms.CharField(required=True,
                           widget=ibadInputWidget(attrs={'label': 'Alias name', 'icon': 'fa fa-paw',
                                                         'placeholder': 'Name'}))
    client = forms.ChoiceField(label='Alias to', required=True,
                               widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))


class ClientAdvancedForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.HiddenInput())
    enabled = forms.BooleanField(label='Client enabled', required=False,
                                 widget=ibadToggleWidget(attrs={'label': 'Client enabled'}))
    backurl = forms.CharField(required=False, widget=forms.HiddenInput())


class ClientStdAdvancedForm(ClientAdvancedForm):
    genpass = forms.BooleanField(label='Generate new client access key on Save', required=False)
