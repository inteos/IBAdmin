from __future__ import unicode_literals
from libs.widgets import *


REPLACE = (
    ('Always', 'Always'),
    ('Never', 'Never'),
    ('IfOlder', 'If Older'),
    ('IfNewer', 'If Newer'),
)


class RestoreFilesForm(forms.Form):
    def __init__(self, clients=(), *args, **kwargs):
        super(RestoreFilesForm, self).__init__(*args, **kwargs)
        self.fields['restoreclient'].choices = clients

    where = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Where', 'icon': 'fa fa-map', 'placeholder': 'Original location'}))
    comment = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Job comment', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    restoreclient = forms.ChoiceField(required=True, label='Restore client', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    replace = forms.ChoiceField(label='Replace mode', choices=REPLACE, required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    rselected = forms.CharField(required=True, widget=forms.HiddenInput())
    client = forms.CharField(required=True, widget=forms.HiddenInput())


class RestoreProxmoxForm(forms.Form):
    def __init__(self, clients=(), *args, **kwargs):
        super(RestoreProxmoxForm, self).__init__(*args, **kwargs)
        self.fields['restoreclient'].choices = clients

    localrestore = forms.BooleanField(required=False, label='Restore to directory')
    where = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Where', 'icon': 'fa fa-map', 'placeholder': 'i.e. /tmp/bacula/restores'}))
    comment = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Job comment', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    restoreclient = forms.ChoiceField(required=True, label='Restore host', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    replace = forms.ChoiceField(label='Replace mode', choices=REPLACE, required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    proxmoxstorage = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Proxmox storage', 'icon': 'fa fa-database', 'placeholder': 'Original storage'}))
    proxmoxpool = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Proxmox resource pool', 'icon': 'fa fa-tags', 'placeholder': 'No pool'}))
    rselected = forms.CharField(required=True, widget=forms.HiddenInput())
    client = forms.CharField(required=True, widget=forms.HiddenInput())
