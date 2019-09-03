# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from libs.widgets import *


USERTYPE = (
    ("std", "Standard"),
    ("admin", "Administrator"),
    ("super", 'Superuser!'),
)


class UserForm(forms.Form):
    def __init__(self, departments=(), roles=(), usertypes=(), *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['departments'].choices = departments
        self.fields['roles'].choices = roles
        self.fields['usertype'].choices = usertypes

    username = forms.CharField(required=True, max_length=150, widget=ibadInputWidget(attrs={'label': 'User name', 'icon': 'fa fa-user', 'placeholder': 'user1'}))
    firstname = forms.CharField(required=False, max_length=30, widget=ibadInputWidget(attrs={'label': 'First name', 'icon': 'fa fa-paw', 'placeholder': 'Jan'}))
    lastname = forms.CharField(required=False, max_length=30, widget=ibadInputWidget(attrs={'label': 'Last name', 'icon': 'fa fa-paw', 'placeholder': 'Kowalski'}))
    email = forms.EmailField(required=True, widget=ibadInputWidget(attrs={'label': 'Email', 'icon': 'glyphicon glyphicon-envelope', 'placeholder': 'email: user1@example.com'}))
    password = forms.CharField(required=False, widget=ibadPasswordInputWidget(attrs={'placeholder': '.....', 'rplaceholder': '.....'}))
    usertype = forms.ChoiceField(label='User type', required=True, choices=USERTYPE, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    departments = forms.MultipleChoiceField(label='Departments', required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}))
    roles = forms.MultipleChoiceField(label='Roles', required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}))
    backurl = forms.CharField(required=False, widget=forms.HiddenInput())


class UserAdddepartmentForm(forms.Form):
    def __init__(self, departments=(), *args, **kwargs):
        super(UserAdddepartmentForm, self).__init__(*args, **kwargs)
        self.fields['departments'].choices = departments

    departments = forms.ChoiceField(label='Departments', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))


class UserAddroleForm(forms.Form):
    def __init__(self, roles=(), *args, **kwargs):
        super(UserAddroleForm, self).__init__(*args, **kwargs)
        self.fields['roles'].choices = roles

    roles = forms.ChoiceField(label='Roles', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))


def getusertypeslist(request):
    if request.user.is_superuser:
        if request.user.is_staff:
            return USERTYPE
        else:
            return USERTYPE[:2]
    return USERTYPE[:1]
