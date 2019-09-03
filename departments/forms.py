# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from libs.widgets import *
from libs.forms import LABELCOLORS


class DepartmentForm(forms.Form):
    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Department name', 'icon': 'fa fa-bank', 'placeholder': 'Marketing'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    shortname = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Short name', 'icon': 'fa fa-flash', 'placeholder': 'shortmx8'}))
    color = forms.ChoiceField(label='Label color', choices=LABELCOLORS, required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))


class DepartmentAddmemberForm(forms.Form):
    def __init__(self, users=(), *args, **kwargs):
        super(DepartmentAddmemberForm, self).__init__(*args, **kwargs)
        self.fields['user'].choices = users

    user = forms.ChoiceField(label='User', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
