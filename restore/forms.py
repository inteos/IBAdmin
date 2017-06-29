from __future__ import unicode_literals
from libs.widgets import *


REPLACE = (
    ('Always', 'Always'),
    ('Never', 'Never'),
    ('IfOlder', 'If Older'),
    ('IfNewer', 'If Newer'),
)


class RestoreForm(forms.Form):
    def __init__(self, clients=(), *args, **kwargs):
        super(RestoreForm, self).__init__(*args, **kwargs)
        self.fields['restoreclient'].choices = clients

    where = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Where', 'icon': 'fa fa-map', 'placeholder': 'Original location'}))
    comment = forms.CharField(required=False, widget=ibadInputWidget(attrs={'label': 'Job comment', 'icon': 'fa fa-commenting-o', 'placeholder': '...'}))
    restoreclient = forms.ChoiceField(required=True, label='Restore client', widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    replace = forms.ChoiceField(label='Replace mode', choices=REPLACE, required=True, widget=forms.Select(attrs={'class': 'select2 form-control', 'style': 'width: 100%;'}))
    rselected = forms.CharField(required=True, widget=forms.HiddenInput())
    client = forms.CharField(required=True, widget=forms.HiddenInput())
