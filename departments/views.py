# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from libs.menu import updateMenuNumbers
from libs.user import *
from jobs.models import Log
from libs.client import removedepartclient, changedepartclient
from libs.vmhosts import removedepartvcenter, changedepartvcenter
from users.models import Profile
from libs.forms import LABELCOLORSDICT
from users.decorators import *
from .models import Departments
from .forms import *


# Create your views here.
@perm_required('departments.view_departments')
def defined(request):
    """ Defined Departments table - list """
    context = {'contentheader': 'Departments', 'contentheadersmall': 'currently defined',
               'apppath': ['Departments', 'Defined']}
    updateMenuNumbers(request, context)
    return render(request, 'departments/defined.html', context)


@perm_required('departments.view_departments')
def defineddata(request):
    """ JSON for departments defined datatable """
    cols = ['name', 'description', 'shortname', '', '', '']
    departs = getUserDepartments(request)
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    orderstr = order_dir + order_col
    total = departs.count()
    if search != '':
        f = Q(name__icontains=search) | Q(description__icontains=search) | Q(shortname__icontains=search)
        filtered = departs.filter(f).count()
        query = departs.filter(f).order_by(orderstr)[offset:offset + limit]
    else:
        filtered = total
        query = departs.order_by(orderstr)[offset:offset + limit]
    data = []
    for d in query:
        admins = Profile.objects.filter(departments=d, user__is_staff=False, user__is_superuser=True).count()
        users = Profile.objects.filter(departments=d, user__is_staff=False, user__is_superuser=False).count()
        data.append([d.name, d.shortname, d.description, [d.color, LABELCOLORSDICT.get(d.color, 'Undefined')], admins,
                     users, [d.name, d.shortname, total > 1 or (request.user.is_superuser and request.user.is_staff)]])
    draw = request.GET['draw']
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('departments.add_departments')
def adddep(request):
    if request.method == 'GET':
        form = DepartmentForm()
        context = {'contentheader': 'Departments', 'apppath': ['Departments', 'Add'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'departments/add.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = DepartmentForm(request.POST)
            if form.is_valid():
                username = request.user.username
                department = form.cleaned_data['name']
                descr = form.cleaned_data['descr']
                short = form.cleaned_data['shortname']
                color = form.cleaned_data['color']
                # create Department
                with transaction.atomic():
                    depart = Departments(name=department, shortname=short, description=descr, color=color)
                    depart.save()
                    user = request.user
                    if not user.is_superuser or not user.is_staff:
                        profile = Profile.objects.get(user=user)
                        profile.departments.add(depart)
                    log = Log(jobid_id=0, logtext='Department "%s" created by %s' % (department, str(username)))
                    log.save()
                return redirect('departsdefined')
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('departsdefined')


@any_perm_required('departments.add_departments', 'departments.change_departments')
def deptname(request):
    """
        JSON for Department name
        when department name already exist then return false
    """
    department = request.GET.get('name', '')
    check = True
    if Departments.objects.filter(name=department).count() == 1:
        check = False
    return JsonResponse(check, safe=False)


@any_perm_required('departments.add_departments', 'departments.change_departments')
def shortname(request):
    """
        JSON for Department short name
        when department short name already exist then return false
    """
    department = request.GET.get('shortname', '')[:8]
    check = True
    if Departments.objects.filter(shortname=department).count() == 1:
        check = False
    return JsonResponse(check, safe=False)


@any_perm_required('departments.add_departments', 'departments.change_departments')
def nameother(request, name):
    """
        JSON for Department name
        when department name already exist then return false
    """
    department = request.GET.get('name', '')
    check = True
    if department != name:
        if Departments.objects.filter(name=department).count() == 1:
            check = False
    return JsonResponse(check, safe=False)


@any_perm_required('departments.add_departments', 'departments.change_departments')
def shortnameother(request, name):
    """
        JSON for Department short name
        when department short name already exist then return false
    """
    department = request.GET.get('shortname', '')[:8]
    check = True
    if department != name:
        if Departments.objects.filter(shortname=department).count() == 1:
            check = False
    return JsonResponse(check, safe=False)


def makeinitialdata(department):
    data = {
        'name': department.name,
        'descr': department.description,
        'shortname': department.shortname,
        'color': department.color,
    }
    return data


@perm_required('departments.change_departments')
def editdep(request, name):
    department = get_object_or_404(Departments, shortname=name)
    if request.method == 'GET':
        data = makeinitialdata(department)
        form = DepartmentForm(initial=data)
        context = {'contentheader': 'Departments', 'apppath': ['Departments', 'Edit', name], 'departmentdisplay': 1,
                   'Department': department, 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'departments/edit.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            # print "Save!"
            data = makeinitialdata(department)
            form = DepartmentForm(data=request.POST, initial=data)
            if form.is_valid() and form.has_changed():
                with transaction.atomic():
                    if 'descr' in form.changed_data:
                        # update description
                        # print "Update description"
                        department.description = form.cleaned_data['descr']
                    if 'name' in form.changed_data:
                        # update name
                        newname = form.cleaned_data['name']
                        department.name = newname
                    if 'shortname' in form.changed_data:
                        # update shortname
                        changedepartclient(department.shortname, form.cleaned_data['shortname'])
                        changedepartvcenter(department.shortname, form.cleaned_data['shortname'])
                        department.shortname = form.cleaned_data['shortname']
                    if 'color' in form.changed_data:
                        # update color label
                        department.color = form.cleaned_data['color']
                    department.save()
                    log = Log(jobid_id=0, logtext='Department "' + name + '" modification by ' + request.user.username)
                    log.save()
                return redirect('departsdefined')
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('departsdefined')


@perm_required('departments.view_departments')
def info(request, name):
    """ Department details info """
    department = get_object_or_404(Departments, shortname=name)
    labelcolor = LABELCOLORSDICT.get(department.color, 'bg-blue')
    members = Profile.objects.filter(departments=department)
    memberlist = []
    for m in members:
        memberlist.append(m.user.username)
    userlist = getUserListfiltered(memberlist)
    form = DepartmentAddmemberForm(users=userlist)
    context = {'contentheader': 'Department', 'contentheadersmall': 'Info', 'apppath': ['Departments', 'Info', name],
               'departmentdisplay': 1, 'Department': department, 'form': form, 'membersnr': members.count(),
               'labelcolor': labelcolor,
               'deldepart': getDepartmentssnr(request) > 1 or (request.user.is_superuser and request.user.is_staff)}
    updateMenuNumbers(request, context)
    return render(request, 'departments/info.html', context)


@perm_required('departments.view_departments')
def infoadmins(request, shortdname):
    department = get_object_or_404(Departments, shortname=shortdname)
    admins = Profile.objects.filter(departments=department, user__is_superuser=True).exclude(user__is_staff=True)
    adminnr = admins.count()
    context = {'Users': admins, 'usernr': adminnr}
    return render(request, 'departments/infousers.html', context)


@perm_required('departments.view_departments')
def infousers(request, shortdname):
    department = get_object_or_404(Departments, shortname=shortdname)
    users = Profile.objects.filter(departments=department, user__is_superuser=False, user__is_staff=False)
    usernr = users.count()
    context = {'Users': users, 'usernr': usernr}
    return render(request, 'departments/infousers.html', context)


@perm_required('departments.add_members')
def addmember(request, shortdname):
    department = get_object_or_404(Departments, shortname=shortdname)
    status = [False, '']
    if request.method == 'POST':
        userlist = getUserList()
        form = DepartmentAddmemberForm(users=userlist, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['user']
            with transaction.atomic():
                status = [True, username]
                profile = Profile.objects.get(user__username=username)
                profile.departments.add(department)
        else:
            messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
            # TODO: add error info to status variable
    return JsonResponse(status, safe=False)


@perm_required('departments.delete_members')
def deletemember(request, shortdname, username):
    if request.user.username == username:
        raise PermissionDenied
    department = get_object_or_404(Departments, shortname=shortdname)
    profile = get_object_or_404(Profile, user__username=username)
    fullname = profile.user.get_full_name() or username
    with transaction.atomic():
        profile.departments.remove(department)
        status = [True, username, fullname]
    # TODO: add error info to status variable
    return JsonResponse(status, safe=False)


@perm_required('departments.delete_departments')
def makedelete(request, name):
    userdeparts = getUserDepartments(request)
    depart = get_object_or_404(Departments, shortname=name, id__in=userdeparts)
    if not (request.user.is_superuser and request.user.is_staff) and len(userdeparts) == 1:
        st = False
    else:
        logi = Log(jobid_id=0, logtext='User deleted Department "%s".' % name)
        logi.save()
        st = True
        with transaction.atomic():
            removedepartclient(name)
            removedepartvcenter(name)
            depart.delete()
    context = {'status': st}
    return JsonResponse(context, safe=False)
