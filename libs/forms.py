# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import copy
from django import forms
from django.forms import fields


INTERVALS = (
    ('seconds', 'Seconds'),
    ('minutes', 'Minutes'),
    ('hours', 'Hours'),
    ('days', 'Days'),
    ('weeks', 'Weeks'),
    ('months', 'Months'),
    ('quarters', 'Quarters'),
    ('years', 'Years'),
)

LABELCOLORS = (
    ('bg-blue', 'Blue label'),
    ('bg-red', 'Red label'),
    ('bg-green', 'Green label'),
    ('bg-orange', 'Orange label'),
    ('bg-navy', 'Navy label'),
    ('bg-yellow', 'Yellow label'),
    ('bg-teal', 'Teal label'),
    ('bg-olive', 'Olive label'),
    ('bg-maroon', 'Maroon label'),
    ('bg-aqua', 'Aqua label'),
    ('bg-purple', 'Purple label'),
    ('bg-fuchsia', 'Fuchsia label'),
    ('bg-lime', 'Lime label'),
    ('bg-black', 'Black label'),
)

LABELCOLORSDICT = {
    'bg-blue': 'Blue label',
    'bg-red': 'Red label',
    'bg-green': 'Green label',
    'bg-orange': 'Orange label',
    'bg-navy': 'Navy label',
    'bg-yellow': 'Yellow label',
    'bg-teal': 'Teal label',
    'bg-olive': 'Olive label',
    'bg-maroon': 'Maroon label',
    'bg-aqua': 'Aqua label',
    'bg-purple': 'Purple label',
    'bg-fuchsia': 'Fuchsia label',
    'bg-lime': 'Lime label',
    'bg-black': 'Black label',
}


def leveltuple(off=False, disableincr=False, disablediff=False):
    lvl = ()
    if off:
        lvl += ('off', 'Off'),
    lvl += ('full', 'Full'),
    if not disableincr:
        lvl += ('incr', 'Incremental'),
    if not disablediff:
        lvl += ('diff', 'Differential'),
    return lvl


def mergeleveltuple(off=False, levels=None):
    lvl = {}
    if levels is not None:
        lvl = levels
    di = lvl.get('disableincr', False)
    dd = lvl.get('disablediff', False)
    return leveltuple(off, di, dd)


def level2form(level='Full'):
    if level.lower().startswith('f'):
        return 'full'
    if level.lower().startswith('i'):
        return 'incr'
    if level.lower().startswith('d'):
        return 'diff'


class RetentionField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(),
            forms.ChoiceField(choices=INTERVALS),
        )
        super(RetentionField, self).__init__(fields=fields, require_all_fields=True, *args, **kwargs)
        self.widget.choices = INTERVALS

    def compress(self, data_list):
        if data_list:
            return data_list[0] + " " + data_list[1]
        return None


class ScheduleWeekField(forms.MultiValueField):
    length = 0

    def __init__(self, choices=(), label=None, *args, **kwargs):
        fields = ()
        # Potrzebujemy 7 pozycji na dni tygodnia i 1 dla 'Everyday'
        for item in range(0, 8):
            fields += (forms.ChoiceField(choices=choices),)
        super(ScheduleWeekField, self).__init__(fields=fields, require_all_fields=True, *args, **kwargs)
        self.length = len(fields)
        self.choices = choices
        self.widget.label = label

    def __deepcopy__(self, memo):
        result = super(ScheduleWeekField, self).__deepcopy__(memo)
        result._choices = copy.deepcopy(self._choices, memo)
        return result

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        # Setting choices also sets the choices on the widget.
        # choices can be any iterable, but we call list() on it because
        # it will be consumed more than once.
        if callable(value):
            value = fields.CallableChoiceIterator(value)
        else:
            value = list(value)

        self._choices = self.widget.choices = value

    choices = property(_get_choices, _set_choices)

    def compress(self, data_list):
        if data_list is not None:
            return ":".join(data_list)
        return ":".join(("off",) * self.length)


class ScheduleMonthField(forms.MultiValueField):
    length = 0

    def __init__(self, choices=(), label=None, *args, **kwargs):
        fields = ()
        # Potrzebujemy 31 pozycji na dni miesiąca i 1 dla 'Everyday'
        for item in range(0, 32):
            fields += (forms.ChoiceField(choices=choices),)
        super(ScheduleMonthField, self).__init__(fields=fields, require_all_fields=True, *args, **kwargs)
        self.length = len(fields)
        self.choices = choices
        self.widget.label = label

    def __deepcopy__(self, memo):
        result = super(ScheduleMonthField, self).__deepcopy__(memo)
        result._choices = copy.deepcopy(self._choices, memo)
        return result

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        # Setting choices also sets the choices on the widget.
        # choices can be any iterable, but we call list() on it because
        # it will be consumed more than once.
        if callable(value):
            value = fields.CallableChoiceIterator(value)
        else:
            value = list(value)

        self._choices = self.widget.choices = value

    choices = property(_get_choices, _set_choices)

    def compress(self, data_list):
        if data_list is not None:
            return ":".join(data_list)
        return ":".join(("off",) * self.length)
