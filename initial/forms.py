from __future__ import unicode_literals
from libs.widgets import *


class InitialForm(forms.Form):
    def __init__(self, storages=(), *args, **kwargs):
        super(InitialForm, self).__init__(*args, **kwargs)
        self.fields['storage'].choices = storages

    dirname = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'System Name - required'}))
    descr = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Administrator email - required'}))
    admpass = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Administrator password - required'}))
    admrpass = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Retype password - required'}))
    storage = forms.ChoiceField(required=True, widget=SelectWithDisabled(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    archivedir = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Archive directory - required. Directory must exist.'}))
    dedupidxdir = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Deduplication Index directory - required. Directory must exist.'}))
    dedupdir = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Deduplication Engine directory - required. Directory must exist.'}))


class InitialDetectForm(forms.Form):
    dirname = forms.CharField(required=True, widget=forms.HiddenInput())
    descr = forms.CharField(required=False, widget=forms.HiddenInput())
    email = forms.CharField(required=True, widget=forms.HiddenInput())
    admpass = forms.CharField(required=True, widget=forms.HiddenInput())
    storage = forms.CharField(required=True, widget=forms.HiddenInput())
    taskid = forms.IntegerField(required=True, widget=forms.HiddenInput())
    tapeinit = forms.BooleanField(required=False, label='Initialize all tapes')
