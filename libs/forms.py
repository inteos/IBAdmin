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


def leveltuple(off=False, disableincr=False, disablediff=False):
    l = ()
    if off:
        l += ('off', 'Off'),
    l += ('full', 'Full'),
    if not disableincr:
        l += ('incr', 'Incremental'),
    if not disablediff:
        l += ('diff', 'Differential'),
    return l


def level2form(level='Full'):
    if level.lower().startswith('f'):
        return 'full'
    if level.lower().startswith('i'):
        return 'incr'
    if level.lower().startswith('d'):
        return 'diff'


class ibadCharField(forms.CharField):
    def __init__(self, max_length=None, min_length=None, strip=True, label=None, *args, **kwargs):
        super(ibadCharField, self).__init__(max_length=max_length, min_length=min_length, strip=strip, *args, **kwargs)
        self.widget.label = label


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
