from __future__ import unicode_literals
from libs.widgets import *
from libs.forms import LABELCOLORS


class RolesForm(forms.Form):
    def __init__(self, perms=(), *args, **kwargs):
        super(RolesForm, self).__init__(*args, **kwargs)
        self.fields['perms'].choices = perms

    name = forms.CharField(required=True, max_length=80, widget=ibadInputWidget(attrs={'label': 'Role name', 'icon': 'fa fa-paw', 'placeholder': 'Role ...'}))
    descr = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Description', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    color = forms.ChoiceField(label='Label color', choices=LABELCOLORS, required=True, widget=forms.Select(attrs={'class': 'form-control label-color select2', 'style': 'width: 100%;'}))
    perms = forms.MultipleChoiceField(label='Permissions', required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control perms select2', 'style': 'width: 100%;'}))


class RolesAddpermForm(forms.Form):
    def __init__(self, perms=(), *args, **kwargs):
        super(RolesAddpermForm, self).__init__(*args, **kwargs)
        self.fields['perms'].choices = perms

    perms = forms.ChoiceField(label='Permissions', required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
