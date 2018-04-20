# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.forms.widgets import Select
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape
# import traceback


class ibadInputWidget(forms.widgets.TextInput):
    def render(self, name, value, attrs=None):
        id_for_label = attrs['id']
        label = self.attrs.get('label', '')
        valuetag = ''
        if value is not None:
            valuetag = 'value="' + value + '"'
        disabled = attrs.get('disabled', None)
        disabletag = ''
        if disabled is not None:
            disabletag = 'disabled'
        required = attrs.get('required', None)
        requiredtag = ''
        if required is not None and required:
            requiredtag = 'required'
        icon = self.attrs.get('icon', 'fa-question-circle')
        placeholder = self.attrs.get('placeholder', '')
        shtml = """<div id="{id_for_label}-group" class="form-group">
  <label for="{id_for_label}" class="col-sm-2 control-label">{label}</label>
  <div class="col-sm-10">
    <div class="input-group">
      <input type="text" class="form-control" id="{id_for_label}" {valuetag} placeholder="{placeholder}" name="{name}" {disabletag} {requiredtag}>
      <span class="input-group-addon"><i class="{icon}"></i></span>
    </div>
  </div>
</div><!-- /.form-group -->"""
        html = shtml.format(id_for_label=id_for_label, label=label, valuetag=valuetag, name=name, disabletag=disabletag,
                            requiredtag=requiredtag, icon=icon, placeholder=placeholder)
        return mark_safe(html)


class ibadToggleWidget(forms.widgets.CheckboxInput):
    def render(self, name, value, attrs=None):
        id_for_label = attrs['id']
        label = self.attrs.get('label', '')
        checkedtag = ''
        if value is not None and value:
            checkedtag = 'checked="checked"'
        disabled = attrs.get('disabled', None)
        disabletag = ''
        if disabled is not None:
            disabletag = 'disabled'
        required = attrs.get('required', None)
        requiredtag = ''
        if required is not None and required:
            requiredtag = 'required'
        shtml = """<div id="{id_for_label}-group" class="form-group">
  <label for="{id_for_label}" class="col-sm-2 control-label vertical-align">{label}</label>
  <div class="col-sm-10">
    <div class="input-group">
      <input id="{id_for_label}" name="{name}" type="checkbox" class="form-control" {checkedtag} {disabletag} {requiredtag} data-toggle="toggle" />
    </div>
  </div>
</div><!-- /.form-group -->"""
        html = shtml.format(id_for_label=id_for_label, label=label, checkedtag=checkedtag, name=name, disabletag=disabletag,
                            requiredtag=requiredtag)
        return mark_safe(html)


class ibadSelect2Widget(forms.widgets.TextInput):
    def render(self, name, value, attrs=None):
        id_for_label = attrs['id']
        label = self.attrs.get('label', '')
        valuetag = ''
        if value is not None:
            valuetag = 'value="' + value + '"'
        disabled = attrs.get('disabled', None)
        disabletag = ''
        if disabled is not None:
            disabletag = 'disabled'
        required = attrs.get('required', None)
        requiredtag = ''
        if required is not None and required:
            requiredtag = 'required'
        icon = self.attrs.get('icon', 'fa-question-circle')
        placeholder = self.attrs.get('placeholder', '')
        shtml = """<div id="{id_for_label}-group" class="form-group">
          <label for="{id_for_label}" class="col-sm-2 control-label">{label}</label>
          <div class="col-sm-10">
            {{ form.storage }}
          </div>
        </div><!-- /.form-group -->
        """
        html = shtml.format(id_for_label=id_for_label, label=label, valuetag=valuetag, name=name, disabletag=disabletag,
                            requiredtag=requiredtag, icon=icon, placeholder=placeholder)
        return mark_safe(html)


class ibadTextAreaWidget(forms.widgets.Textarea):
    def render(self, name, value, attrs=None):
        id_for_label = attrs['id']
        label = self.attrs.get('label', '')
        disabled = attrs.get('disabled', None)
        disabletag = ''
        if disabled is not None:
            disabletag = 'disabled'
        required = attrs.get('required', None)
        requiredtag = ''
        if required is not None and required:
            requiredtag = 'required'
        if value is None:
            value = ''
        icon = self.attrs.get('icon', 'fa-question-circle')
        placeholder = self.attrs.get('placeholder', '')
        shtml = """<div id="{id_for_label}-group" class="form-group"> <!-- has-success has-error -->
  <label for="{id_for_label}" class="col-sm-2 control-label">{label}</label>
  <div class="col-sm-10">
    <div class="input-group">
      <textarea class="form-control" rows=3 id="{id_for_label}" placeholder="{placeholder}" name="{name}" {disabletag} {requiredtag}>{value}</textarea>
      <span class="input-group-addon"><i class="{icon}"></i></span>
    </div>
  </div>
</div><!-- /.form-group -->"""
        html = shtml.format(id_for_label=id_for_label, label=label, value=value, name=name, disabletag=disabletag,
                            requiredtag=requiredtag, icon=icon, placeholder=placeholder)
        return mark_safe(html)


class ibadRetentionWidget(forms.widgets.MultiWidget):
    choices = ()

    def __init__(self, attrs=None):
        widgets = (
            forms.TextInput(attrs=attrs),
            forms.Select(attrs=attrs, choices=self.choices),
        )
        super(ibadRetentionWidget, self).__init__(widgets, attrs)

    def id_for_label(self, id_):
        return id_

    def decompress(self, value):
        if value:
            return value.split()
        return ['30', 'days']

    def render(self, name, value, attrs=None):
        # value is a list of values, each corresponding to a widget
        # in self.widgets, if not decompress it.
        if not isinstance(value, list):
            value = self.decompress(value)
        idforlabel = attrs['id']
        label = self.attrs.get('label', 'Retention')
        valuetag = 'value="30"'
        if value is not None:
            valuetag = 'value="' + value[0] + '"'
        valueinterval = value[1]
        valuebutton = self.choices[3][1]
        for a in self.choices:
            if a[0] == value[1]:
                valuebutton = a[1]
        disabled = attrs.get('disabled', None)
        disabletag = ''
        if disabled is not None:
            disabletag = 'disabled'
        required = attrs.get('required', None)
        requiredtag = ''
        if required is not None and required:
            requiredtag = 'required'
        placeholder = self.attrs.get('placeholder', '')
        shtml = """<div id="{id_for_label}-group" class="form-group">
  <label for="{id_for_label}" class="col-sm-2 control-label">{label}</label>
  <div class="col-sm-10">
    <div class="input-group">
      <input type="text" class="form-control" id="{id_for_label}" {valuetag} placeholder="{placeholder}" name="{name}_0" {disabletag} {requiredtag}>
      <div class="input-group-btn">
        <input class="span2" id="{id_for_label}-interval" value="{valueinterval}" name="{name}_1" type="hidden">
        <button id="{id_for_label}-button" type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">{valuebutton} <span class="caret"></span></button>
        <ul class="dropdown-menu">"""
        for val, text in self.choices:
            shtml += '<li><a href="#" id="' + val + '">' + text + '</a></li>'
        shtml += """</ul>
      </div>
    </div>
  </div>
</div><!-- /.form-group -->"""
        html = shtml.format(id_for_label=idforlabel, label=label, valuetag=valuetag, name=name, disabletag=disabletag,
                            requiredtag=requiredtag, placeholder=placeholder, valueinterval=valueinterval, valuebutton=valuebutton)
        return mark_safe(html)


WEEKITEMS = (
    ('Monday', None),
    ('Tuesday', None),
    ('Wednesday', None),
    ('Thursday', None),
    ('Friday', None),
    ('Saturday', 'warning'),
    ('Sunday', 'danger'),
    ('Everyday', 'default'),
)


class ibadScheduleWeekWidget(forms.widgets.MultiWidget):
    length = 0

    def __init__(self, attrs=None, choices=()):
        widgets = ()
        for i in WEEKITEMS:
            widgets += (forms.Select(attrs=attrs, choices=choices)),
        super(ibadScheduleWeekWidget, self).__init__(widgets, attrs)
        self.length = len(WEEKITEMS)
        self.choices = list(choices)

    def id_for_label(self, id_):
        return id_

    def decompress(self, value):
        if value:
            return value.split(':')
        return ['off'] * self.length

    def render_level(self, value, label, selected=False):
        if selected:
            selected_html = mark_safe(' selected="selected"')
        else:
            selected_html = ""
        return format_html('<option value="{}"{}>{}</option>', value, selected_html, label)

    def render_select(self, name, label, value, col=None, disabled=False):
        if col is None:
            col = 'primary'
        if disabled:
            disabled_html = mark_safe(' disabled="disabled"')
        else:
            disabled_html = ""
        shtml = """ <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6 text-center">
                      <div class="row">
                        <h4><span class="label label-{col}">{label}</span></h4>
                      </div>
                      <div class="row">
                        <select class="select2" id="{name}" name="{name}" style="width: 80%"{disabled}>
                          """
        for v, l in self.choices:
            shtml += self.render_level(v, l, v == value)
        shtml += """
                        </select>
                      </div>
                    </div>"""
        html = shtml.format(col=col, label=label, name=name, disabled=disabled_html)
        return mark_safe(html)

    def render(self, name, value, attrs=None):
        # value is a list of values, each corresponding to a widget
        # in self.widgets, if not decompress it.
        if not isinstance(value, list):
            value = self.decompress(value)
        disabled = (value[self.length - 1] != 'off')
        idforlabel = attrs['id']
        if self.label is None:
            label = self.attrs.get('label', 'Days of week')
        else:
            label = self.label
        shtml = """<div id="{id_for_label}-group" class="form-group">
             <label for="{id_for_label}" class="col-sm-2 control-label">{label}</label>
             <div class="col-sm-10">
               <div class="col-sm-12">
                 <div class="row">
                   """
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = 'off'
            shtml += self.render_select(name + '_%s' % i, WEEKITEMS[i][0], widget_value, WEEKITEMS[i][1],
                                        disabled & (i != (self.length - 1)))
        shtml += """
                </div>
              </div>
            </div>
          </div><!-- /.form-group -->"""
        html = shtml.format(id_for_label=idforlabel, label=label)
        return mark_safe(html)


MONTHHLIGHT = ('1', '28', '30', '31')


class ibadScheduleMonthWidget(forms.widgets.MultiWidget):
    length = 0

    def __init__(self, attrs=None, choices=()):
        widgets = ()
        for item in range(0, 32):
            widgets += (forms.Select(attrs=attrs, choices=choices)),
        super(ibadScheduleMonthWidget, self).__init__(widgets, attrs)
        self.length = len(widgets)
        self.choices = list(choices)

    def id_for_label(self, id_):
        return id_

    def decompress(self, value):
        if value:
            return value.split(':')
        return ['off'] * self.length

    def render_level(self, value, label, selected=False):
        if selected:
            selected_html = mark_safe(' selected="selected"')
        else:
            selected_html = ""
        return format_html('<option value="{}"{}>{}</option>', value, selected_html, label)

    def render_select(self, name, label, value, disabled=False):
        if disabled:
            disabled_html = mark_safe(' disabled="disabled"')
        else:
            disabled_html = ""
        if label in MONTHHLIGHT:
            col = 'success'
        elif label == 'Everyday':
            col = 'default'
        else:
            col = 'primary'
        shtml = """ <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6 text-center">
                      <div class="row">
                        <h4><span class="label label-{col}">{label}</span></h4>
                      </div>
                      <div class="row">
                        <select class="select2" id="{name}" name="{name}" style="width: 80%"{disabled}>"""
        for v, l in self.choices:
            shtml += self.render_level(v, l, v == value)
        shtml += """
                        </select>
                      </div>
                    </div>"""
        html = shtml.format(col=col, label=label, name=name, disabled=disabled_html)
        return mark_safe(html)

    def render(self, name, value, attrs=None):
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        disabled = (value[self.length - 1] != 'off')
        id_for_label = attrs['id']
        if self.label is None:
            label = self.attrs.get('label', 'Days of month')
        else:
            label = self.label
        shtml = """<div id="{id_for_label}-group" class="form-group">
             <label for="{id_for_label}" class="col-sm-2 control-label">{label}</label>
               <div class="col-sm-10">
                 <div class="col-sm-12">
                   <div class="row">
                   """
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = 'off'
            if i == self.length - 1:
                wlabel = 'Everyday'
            else:
                wlabel = str(i + 1)
            shtml += self.render_select(name + '_%s' % i, wlabel, widget_value, disabled & (i != self.length - 1))
        shtml += """   </div>
                     </div>
                   </div>
                 </div><!-- /.form-group -->"""
        html = shtml.format(id_for_label=id_for_label, label=label)
        return mark_safe(html)


class SelectWithDisabled(Select):
    """
    Subclass of Django's select widget that allows disabling options.
    To disable an option, pass a dict instead of a string for its label,
    of the form: {'label': 'option label', 'disabled': True}
    """
    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        disabled_html = ''
        if isinstance(option_label, dict):
            if dict.get(option_label, 'disabled'):
                disabled_html = u' disabled="disabled"'
            option_label = option_label['label']
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, disabled_html,
            conditional_escape(force_unicode(option_label)))
