# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from django import template
from django.utils.safestring import mark_safe
from libs.conf import getscheduletext, getretentiontext
from libs.ibadmin import *
from django.contrib.messages import constants as message_constants

register = template.Library()


@register.filter
def bytestext(value):
    try:
        val = int(value)
    except ValueError:
        return value
    if val < 1024:
        return str(val) + " Bytes"
    val /= 1024.0
    for sx in ['kB', 'MB', 'GB', 'TB', 'PB']:
        if val < 1024:
            return "{:.2f} ".format(val) + sx
        val /= 1024.0
    return str(val)


@register.filter
def jobstatustext(value, arg):
    return ibadmin_jobstatustext(value, arg)


@register.filter
def statustext(value):
    if value is not None:
        if int(value) == 1:
            return 'Online'
        if int(value) == 0:
            return 'Offline'
    return "Unknown"


@register.filter
def jobtypetext(value):
    return ibadmin_jobtext(value)


@register.filter
def jobleveltext(value, arg=None):
    return ibadmin_jobleveltext(value, arg)


@register.filter
def mediaicon(value):
    return ibadmin_media_icon(value)


@register.filter
def trimfilename(value, arg=32):
    out = value
    length = len(value)
    if length > arg:
        if value.startswith('/'):
            out = "/.../" + value[length - arg + 5:]
        else:
            out = value[0:3] + ".../" + value[length - arg + 7:]
    return out.replace('//', '/')


@register.filter
def OStext(value):
    return ibadmin_ostext(value)


@register.filter
def OSicon(value):
    return ibadmin_osicon(value)


@register.filter
def OSiconall(value):
    return ibadmin_osiconall(value)


@register.filter
def scheduletext(value):
    if value is not None:
        return getscheduletext(value)
    return ''


@register.filter
def retentiontext(value):
    if value is None or value == '':
        return mark_safe('<i>N/A</i>')
    else:
        return mark_safe(getretentiontext(value))


@register.filter
def taskstatustext(value):
    return ibadmin_tasks_text(value)


@register.filter
def charticon(value):
    return ibadmin_charts_icon(value)


@register.filter
def charttext(value):
    return ibadmin_charts_text(value)


@register.filter
def jdapptext(value):
    return ibadmin_jobapptext(value)


@register.filter
def plugintypetext(name):
    return ibadmin_plugin_text(name)


@register.filter
def fullname(firstname, lastname):
    if firstname or lastname:
        return firstname + ' ' + lastname
    else:
        return None


@register.filter
def usertypetext(superuser, staff):
    if superuser:
        if staff:
            return 'Superuser!'
        else:
            return 'Administrator'
    return 'Standard'


@register.filter
def usertypetextfull(superuser, staff):
    if superuser:
        return 'You are the Superuser!'
    if staff:
        return 'Powerfull Administrator'
    return 'Standard User'


@register.filter
def messageico(level):
    if level == message_constants.INFO:
        return 'fa-info-circle'
    if level == message_constants.SUCCESS:
        return 'fa-check'
    if level == message_constants.WARNING:
        return 'fa-warning'
    if level == message_constants.ERROR:
        return 'fa-ban'
    return 'fa-coffee'


@register.filter
def messagealert(message):
    level = 0
    if hasattr(message, 'level'):
        level = message.level
    if level == message_constants.INFO:
        return 'alert-info'
    if level == message_constants.SUCCESS:
        return 'alert-success'
    if level == message_constants.WARNING:
        return 'alert-warning'
    if level == message_constants.ERROR:
        return 'alert-danger'
    return 'alert-warning'


@register.filter
def messagesubject(message):
    subject = 'Info'
    if hasattr(message, 'extra_tags'):
        subject = message.extra_tags
    if subject.startswith('slide:'):
        subject = subject.split('slide:')[1]
    if subject.startswith('noslide:'):
        subject = subject.split('noslide:')[1]
    return subject


@register.filter
def messagesbox(message):
    boxclass = 'messagesbox'
    level = message_constants.INFO
    subject = ''
    if hasattr(message, 'level'):
        level = message.level
    if hasattr(message, 'extra_tags'):
        subject = message.extra_tags
    if subject.startswith('slide:'):
        boxclass = 'messagesbox'
    else:
        if subject.startswith('noslide:'):
            boxclass = ''
        else:
            if level == message_constants.ERROR:
                boxclass = ''
    return boxclass
