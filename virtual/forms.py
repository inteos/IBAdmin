from __future__ import unicode_literals
from libs.widgets import *
from clients.forms import ClientForm


class vCenterForm(forms.Form):
    def __init__(self, clients=(), departments=(), *args, **kwargs):
        super(vCenterForm, self).__init__(*args, **kwargs)
        self.fields['client'].choices = clients
        self.fields['departments'].choices = departments

    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Name', 'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    username = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Username', 'icon': 'fa fa-user', 'placeholder': 'Username'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control', 'placeholder': 'Password'}))
    address = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Address', 'icon': 'fa fa-envelope-o', 'placeholder': 'Address'}))
    url = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'URL', 'icon': 'fa fa-external-link', 'placeholder': 'https://.../sdk'}))
    thumbprint = forms.CharField(required=False, widget=ibadInputBtnWidget(attrs={'label': 'Thumbprint', 'icon': 'fa fa-search', 'btn': 'btn-default',
                                                                                  'placeholder': 'xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx'}))
    departments = forms.ChoiceField(label='Department', required=True, widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}))
    client = forms.MultipleChoiceField(label='Client Proxy', required=False, widget=forms.SelectMultiple(attrs={'class': 'select2 form-control', 'style': 'width: 100%;', 'multiple': 'multiple'}))


class VMhostForm(ClientForm):
    address = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Address', 'icon': 'fa fa-envelope-o', 'placeholder': 'Address'}))


class vCenterClientForm(forms.Form):
    def __init__(self, vcenter=(), clients=(), departments=(), *args, **kwargs):
        super(vCenterClientForm, self).__init__(*args, **kwargs)
        self.fields['vcenter'].choices = vcenter
        self.fields['client'].choices = clients
        self.fields['departments'].choices = departments

    vcenter = forms.ChoiceField(label='vCenter', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    client = forms.MultipleChoiceField(label='Client Proxy', required=True, widget=forms.SelectMultiple(attrs={'class': 'select2 form-control', 'style': 'width: 100%;', 'multiple': 'multiple'}))
    departments = forms.ChoiceField(label='Department', required=True, widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}))
