# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render, Http404, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from jobs.models import Log
from libs.menu import updateMenuNumbers
from libs.utils import truncateunicodestr
from .forms import *
from libs.forms import LABELCOLORSDICT
from users.decorators import *
from libs.user import *
from libs.role import *


# Create your views here.
@perm_required('roles.view_roles')
def defined(request):
    """ Defined Roles table - list """
    context = {'contentheader': 'Roles', 'contentheadersmall': 'currently defined', 'apppath': ['Roles', 'Defined']}
    updateMenuNumbers(request, context)
    return render(request, 'roles/defined.html', context)


@perm_required('roles.view_roles')
def defineddata(request):
    """ JSON for roles defined datatable """
    cols = ['group__name', 'description', 'color', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Roles.objects.all().count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(group__name__icontains=search) | Q(descr__icontains=search)
        filtered = Roles.objects.filter(f).count()
        query = Roles.objects.filter(f).order_by(orderstr, 'id')[offset:offset + limit]
    else:
        filtered = total
        query = Roles.objects.all().order_by(orderstr, 'id')[offset:offset + limit]
    data = []
    for r in query:
        # Manage [rolename, can_delete, is_active, can_lock]
        data.append([r.group.name, r.description, [r.color, LABELCOLORSDICT.get(r.color, 'Other')],
                     [r.group.name, r.internal]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('roles.view_roles')
def info(request, rolename):
    role = get_object_or_404(Roles, group__name=rolename)
    labelcolor = LABELCOLORSDICT.get(role.color, 'bg-blue')
    perms = get_system_permissions_filtered(role.group)
    perms.insert(0, (None, ''))
    form = RolesAddpermForm(perms=perms)
    context = {'contentheader': 'Roles', 'apppath': ['Roles', 'Info', rolename], 'Role': role, 'rolestatusdisplay': 1,
               'labelcolor': labelcolor, 'form': form}
    updateMenuNumbers(request, context)
    return render(request, 'roles/info.html', context)


@perm_required('roles.view_roles')
def infoperms(request, rolename):
    group = get_object_or_404(Group, name=rolename)
    gperms = get_role_permissions(group)
    context = {'Perms': gperms}
    return render(request, 'roles/infoperms.html', context)


@perm_required('roles.add_roles')
def addrole(request):
    perms = get_system_permissions()
    if request.method == 'GET':
        form = RolesForm(perms=perms)
        context = {'contentheader': 'Roles', 'apppath': ['Roles', 'Add'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'roles/add.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = RolesForm(data=request.POST, perms=perms)
            if form.is_valid():
                rolename = form.cleaned_data['name']
                # Ugly hack for limiting database varchar(80)
                rolenamelen = len(rolename.encode('UTF-8'))
                if rolenamelen > 80:
                    rolename = rolename[:(80 - rolenamelen)/2]
                descr = form.cleaned_data['descr']
                color = form.cleaned_data['color']
                perms = form.cleaned_data['perms']
                # create Role
                with transaction.atomic():
                    role = Group.objects.create(name=rolename)
                    role.roles.description = descr
                    role.roles.color = color
                    newperms = []
                    for p in perms:
                        if p.startswith('addallperms_'):
                            (n, applabel) = p.split('_')
                            allperms = Permission.objects.filter(content_type__model='permissions',
                                                                 content_type__app_label=applabel)\
                                .exclude(codename__icontains='_permissions')
                            for ap in allperms:
                                newperms.append(ap.codename)
                        else:
                            newperms.append(p)
                    permlist = Permission.objects.filter(codename__in=newperms, content_type__model='permissions')
                    role.permissions.set(permlist)
                    role.save()
                    log = Log(jobid_id=0, logtext='Create role: %s by %s' % (rolename, request.user.username))
                    log.save()
                    messages.success(request, 'Role "%s" defined.' % role.name, extra_tags="Success")
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('rolesdefined')


@any_perm_required('roles.add_roles', 'roles.change_roles')
def rolesname(request):
    """
        JSON for Department name
        when department name already exist then return false
    """
    role = request.GET.get('name', '')
    check = True
    if Group.objects.filter(name=role).count() == 1:
        check = False
    return JsonResponse(check, safe=False)


@any_perm_required('roles.add_roles', 'roles.change_roles')
def rolesnameother(request, rolename):
    """
        JSON for Department name
        when department name already exist then return false
    """
    role = request.GET.get('name', '')
    check = True
    if role != rolename:
        if Group.objects.filter(name=role).count() == 1:
            check = False
    return JsonResponse(check, safe=False)


@perm_required('roles.change_roles')
def editrole(request, rolename):
    group = get_object_or_404(Group, name=rolename)
    if group.roles.internal:
        raise Http404
    data = makeinitailadata(group)
    if request.method == 'GET':
        form = RolesForm(initial=data)
        context = {'contentheader': 'Roles', 'apppath': ['Roles', 'Edit', rolename], 'form': form,
                   'rolestatusdisplay': 1, 'Role': group.roles}
        updateMenuNumbers(request, context)
        return render(request, 'roles/edit.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            form = RolesForm(data=request.POST, initial=data)
            if form.is_valid():
                if form.has_changed():
                    with transaction.atomic():
                        if 'name' in form.changed_data:
                            rname = truncateunicodestr(form.cleaned_data['name'], 80)
                            group.name = rname
                        if 'descr' in form.changed_data:
                            group.roles.description = form.cleaned_data['descr']
                        if 'color' in form.changed_data:
                            group.roles.color = form.cleaned_data['color']
                        group.save()
                        log = Log(jobid_id=0, logtext='Role modified: %s by %s' % (rolename, request.user.username))
                        log.save()
                    messages.success(request, 'Role "%s" updated.' % group.name, extra_tags="Success")
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('rolesdefined')


@perm_required('roles.delete_roles')
def rolesdelete(request, rolename):
    group = get_object_or_404(Group, name=rolename)
    if group.roles.internal:
        raise Http404
    with transaction.atomic():
        group.delete()
    return JsonResponse(True, safe=False)


@perm_required('roles.change_roles')
def addperms(request, rolename):
    group = get_object_or_404(Group, name=rolename)
    status = [False, False, '']
    if request.method == 'POST':
        perms = get_system_permissions_filtered(group)
        form = RolesAddpermForm(perms=perms, data=request.POST)
        if form.is_valid():
            permname = form.cleaned_data['perms']
            if permname.startswith('addallperms'):
                (n, applabel) = permname.split('_')
                status = [True, True, applabel.capitalize()]
                allperms = Permission.objects\
                    .filter(content_type__model='permissions', content_type__app_label=applabel)\
                    .exclude(codename__icontains='_permissions')
                with transaction.atomic():
                    for perm in allperms:
                        group.permissions.add(perm)
                    group.save()
            else:
                with transaction.atomic():
                    status = [True, False, permname]
                    perm = get_object_or_404(Permission, codename=permname, content_type__model='permissions')
                    group.permissions.add(perm)
                    group.save()
        else:
            status = [False, False, "Cannot validate a form: %s" % form.errors]
    return JsonResponse(status, safe=False)


@perm_required('roles.change_roles')
def deleteperms(request, rolename, applabel, perms):
    group = get_object_or_404(Group, name=rolename)
    status = [False, '', '', '']
    with transaction.atomic():
        perm = get_object_or_404(Permission, codename=perms, content_type__model='permissions',
                                 content_type__app_label=applabel)
        status = [True, applabel.capitalize(), perms, perm.name]
        group.permissions.remove(perm)
        group.save()
    return JsonResponse(status, safe=False)
