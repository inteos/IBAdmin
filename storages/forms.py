from __future__ import unicode_literals
from libs.widgets import *


class StorageForm(forms.Form):
    def __init__(self, storages=(), *args, **kwargs):
        super(StorageForm, self).__init__(*args, **kwargs)
        self.fields['storagelist'].choices = storages

    name = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Storage name', 'icon': 'fa fa-paw', 'placeholder': 'Name'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    address = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Remote address', 'icon': 'fa fa-envelope-o', 'placeholder': 'Address'}))
    storagelist = forms.ChoiceField(label='Existing Storage', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))


class StorageDiskForm(StorageForm):
    archivedir = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Archive directory', 'icon': 'glyphicon glyphicon-folder-close', 'placeholder': 'available folder'}))


class StorageTapeForm(StorageForm):
    def __init__(self, tapelibs=(), *args, **kwargs):
        super(StorageTapeForm, self).__init__(*args, **kwargs)
        self.fields['tapelist'].choices = tapelibs

    tapelist = forms.ChoiceField(label='Available Libraries', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    taskid = forms.IntegerField(required=True, widget=forms.HiddenInput())


class StorageDedupForm(StorageForm):
    dedupidxdir = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Dedup index directory', 'icon': 'fa fa-indent', 'placeholder': 'available folder'}))
    dedupdir = forms.CharField(required=True, widget=ibadInputWidget(attrs={'label': 'Dedup engine directory', 'icon': 'fa fa-cubes', 'placeholder': 'available folder'}))


class StorageAlias(StorageForm):
    def __init__(self, storageips=(), *args, **kwargs):
        super(StorageAlias, self).__init__(*args, **kwargs)
        self.fields['storageip'].choices = storageips

    storageip = forms.ChoiceField(label='Storage IP', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
