# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from roles.models import *
from django.template.defaultfilters import truncatechars


def getRolesnr(request):
    return Roles.objects.all().count()


def updateRolesnr(request, context):
    val = getRolesnr(request)
    context.update({'rolesnr': val})


def getRolesList():
    roles = Roles.objects.all()
    data = ()
    for d in roles:
        data += ((d.group.name, truncatechars(d.group.name, 40)),)
    return data


def getRolesListfilter(exquery):
    roles = Roles.objects.exclude(id__in=exquery)
    data = []
    for d in roles:
        data += ((d.group.name, truncatechars(d.group.name, 40)),)
    return data


def makeinitailadata(group):
    data = {
        'name': group.name,
        'descr': group.roles.description,
        'color': group.roles.color,
    }
    return data
