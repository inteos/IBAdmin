from django import template
from libs.ibadmin import *

register = template.Library()


@register.filter
def jobrunningbgcolor(value):
    return ibadmin_jobrunningbgcolor(value)


@register.filter
def jobqueuedbgcolor(value):
    return ibadmin_jobqueuedbgcolor(value)


@register.filter
def joberrorbgcolor(value):
    return ibadmin_joberrorbgcolor(value)


@register.filter
def jobwarningbgcolor(value):
    return ibadmin_jobwarningbgcolor(value)


@register.filter
def jobsuccessbgcolor(value):
    return ibadmin_jobsuccessbgcolor(value)


@register.filter
def OSfgcolor(value):
    return ibadmin_osfgcolor(value)


@register.filter
def OSbgcolor(value):
    return ibadmin_osbgcolor(value)


@register.filter
def jobstatusbgcolor(value, arg):
    return ibadmin_jobstatusbgcolor(value, arg)


@register.filter
def jobstatusboxcolor(value, arg):
    return ibadmin_jobstatusboxcolor(value, arg)


@register.filter
def statusbgcolor(value):
    if value is not None:
        if int(value) == 1:
            return 'bg-green'
        if int(value) == 0:
            return 'bg-red'
    return "bg-gray"


@register.filter
def jobtypebgcolor(value):
    return ibadmin_jobbgcolor(value)


@register.filter
def joblevelbgcolor(value, arg):
    return ibadmin_joblevelbgcolor(value, arg)


@register.filter
def volstatusbgcolor(value):
    return ibadmin_volstatusbgcolor(value)


@register.filter
def jobstatus_running_bgcolor(value):
    if type(value) is int:
        if value > 0:
            return 'bg-aqua'
    return 'bg-gray'


@register.filter
def jobstatus_cancel_bgcolor(value):
    if type(value) is int:
        if value > 0:
            return 'bg-fuchsia'
    return 'bg-gray'


@register.filter
def jobstatus_queued_bgcolor(value):
    if type(value) is int:
        if value > 0:
            return 'bg-orange'
    return 'bg-gray'


@register.filter
def jobstatus_finished_bgcolor(value):
    if type(value) is int:
        if value > 0:
            return 'bg-green'
    return 'bg-gray'


@register.filter
def jobstatus_error_bgcolor(value):
    if type(value) is int:
        if int(value) > 0:
            return 'bg-red'
    return 'bg-gray'


@register.filter
def jobstatus_warning_bgcolor(value):
    if type(value) is int:
        if value > 0:
            return 'bg-yellow'
    return 'bg-gray'


@register.filter
def mediacolor(value):
    return ibadmin_media_color(value)


@register.filter
def tasksbgcolor(value):
    return ibadmin_tasks_color(value)


@register.filter
def tasksprogresscolor(value):
    return ibadmin_tasks_progresscolor(value)


@register.filter
def jdappcolor(value):
    return ibadmin_jobappcolor(value)


@register.filter
def devstatuscolor(value):
    if value is not None:
        if value == 'Running':
            return 'label-info'
        if value == 'Disabled' or value == 'Blocked':
            return 'label-danger'
        if value == 'Mounted':
            return 'bg-navy'
    return 'label-primary'


@register.filter
def plugintypecolor(name):
    return ibadmin_plugin_color(name)


@register.filter
def usertypecolor(superuser, staff):
    if superuser:
        if staff:
            return 'bg-maroon'
        else:
            return 'bg-orange'
    return 'bg-blue'

