# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.template.defaultfilters import truncatechars
from users.models import *


def getUserDepartments(request):
    if not hasattr(request, "ibadminuserdepartments"):
        if request.user.is_superuser and request.user.is_staff:
            request.ibadminuserdepartments = Departments.objects.all()
        else:
            request.ibadminuserdepartments = Departments.objects.filter(profile__user=request.user)
    return request.ibadminuserdepartments


def getUserDepartmentsval(request):
    return getUserDepartments(request).values('shortname')


def getDepartmentssnr(request):
    return getUserDepartments(request).count()


def updateDepartmentsnr(request, context):
    val = getDepartmentssnr(request)
    context.update({'departmentsnr': val})


def makedepartmentslist(departs, default=False):
    if default:
        data = (('#', '- No departments - default -'),)
    else:
        data = ()
    for d in departs:
        data += ((d.shortname, truncatechars(d.name, 40)),)
    return data


def getDepartmentsList(default=False):
    departs = Departments.objects.all()
    return makedepartmentslist(departs, default=default)


def getDepartmentsListfilter(request, exquery, default=False):
    userdeparts = getUserDepartments(request)
    departs = userdeparts.exclude(id__in=exquery)
    return makedepartmentslist(departs, default=default)


def getUserDepartmentsList(request, default=True):
    user = request.user
    if user.is_superuser and user.is_staff:
        return getDepartmentsList(default=(True and default))
    departs = Departments.objects.filter(profile__user=user)
    return makedepartmentslist(departs, default=((len(departs) == 0) and default))


def getDepartment(shortname=None):
    if shortname is None:
        return None
    depart = Departments.objects.filter(shortname=shortname)
    if depart.count() > 0:
        return depart[0]
    return None


def getdepartmentlabel(shortname=None):
    dname = '-'
    dcolor = None
    if shortname is not None:
        d = getDepartment(shortname)
        if d is not None:
            dname = d.name
            dcolor = d.color
    return dname, dcolor
