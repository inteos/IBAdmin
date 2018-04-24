from __future__ import unicode_literals
from libs.widgets import *


OSES = (
    ("rhel", "RHEL / Centos"),
    ("deb", "Debian / Ubuntu"),
    ("win32", "Windows 32bit"),
    ("win64", "Windows 64bit"),
    ("osx", "Mac OS X"),
    ("solsparc", "Solaris SPARC"),
    ("solintel", "Solaris x86"),
    ("freebsd", "FreeBSD"),
    ("proxmox", "Proxmox Hypervisor"),
    ("xen", "XenServer Hypervisor"),
    ("aix", "AIX"),
    ("hpux", "HP-UX"),
)


class ClientForm(forms.Form):
    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Client name', 'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    address = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Address', 'icon': 'fa fa-envelope-o', 'placeholder': 'Address'}))
    os = forms.ChoiceField(label='Server OS', choices=OSES, required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    defjob = forms.BooleanField(label='Create default backup Job', required=False)


class ClientNodeForm(forms.Form):
    def __init__(self, clusters=(), *args, **kwargs):
        super(ClientNodeForm, self).__init__(*args, **kwargs)
        self.fields['clusterlist'].choices = clusters

    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Client name', 'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    cluster = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'New Cluster name', 'icon': 'fa fa-cubes', 'placeholder': 'Name or ...'}))
    clusterlist = forms.ChoiceField(label='Existing Cluster', required=False, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    address = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Address', 'icon': 'fa fa-envelope-o', 'placeholder': 'Address'}))
    os = forms.ChoiceField(label='Server OS', choices=OSES, required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    defjob = forms.BooleanField(label='Create default backup Job', required=False)


class ClientServiceForm(forms.Form):
    def __init__(self, clusters=(), *args, **kwargs):
        super(ClientServiceForm, self).__init__(*args, **kwargs)
        self.fields['cluster'].choices = clusters

    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Service name', 'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    cluster = forms.ChoiceField(label='Cluster name', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    address = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Address', 'icon': 'fa fa-envelope-o', 'placeholder': 'Address'}))
    defjob = forms.BooleanField(label='Create default backup Job', required=False)


class ClientAliasForm(forms.Form):
    def __init__(self, clients=(), *args, **kwargs):
        super(ClientAliasForm, self).__init__(*args, **kwargs)
        self.fields['client'].choices = clients

    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Alias name', 'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    client = forms.ChoiceField(label='Alias to', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    defjob = forms.BooleanField(label='Create default backup Job', required=False)
