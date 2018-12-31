# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import transaction
from django.contrib import messages
from jobs.models import Log
from libs.menu import updateMenuNumbers
from libs.role import *
from .forms import *
from libs.client import *
from libs.init import postupgrade
from roles.models import *
from .decorators import *


# Create your views here.
def login(request):
    if request.method == 'GET':
        nexturl = request.GET.get('next')
        context = {'nexturl': nexturl}
        auth_logout(request)
        return render(request, 'users/login.html', context)
    else:
        user_name = request.POST.get('username')
        password = request.POST.get('password')
        nexturl = request.POST.get('next')
        user = authenticate(username=user_name, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                log = Log(jobid_id=0, logtext='Login successful: %s' % user_name)
                log.save()
                postupgrade(request)
                if nexturl is not None:
                    return HttpResponseRedirect(nexturl)
                else:
                    return redirect('home')
        # authentication failed
        messages.error(request, 'Username or password did not match any of available users. Try again.',
                       extra_tags="slide:Login failure")
        context = {'next': nexturl}
        log = Log(jobid_id=0, logtext='Login failure: %s' % user_name)
        log.save()
        return render(request, 'users/login.html', context)


def logout(request):
    user_name = request.user.get_username()
    auth_logout(request)
    log = Log(jobid_id=0, logtext='Successful logout: ' + user_name)
    log.save()
    messages.success(request, "User successfuly logged out from application.", extra_tags="Success")
    return redirect('login')


# @permission_required('users.view_users', raise_exception=True)
@perm_required('users.view_users')
def defined(request):
    """ Defined Clients table - list """
    context = {'contentheader': 'Users', 'contentheadersmall': 'currently defined', 'apppath': ['Users', 'Defined']}
    updateMenuNumbers(request, context)
    return render(request, 'users/defined.html', context)


@perm_required('users.view_users')
def defineddata(request):
    """ JSON for users defined datatable """
    cols = ['username', 'first_name', 'last_name', 'email', 'last_login', 'is_active', 'is_staff', '']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    userusers = getUserUsers(request)
    total = userusers.count()
    nrsuperusers = User.objects.filter(is_superuser=True, is_staff=True).count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | \
            Q(email__icontains=search)
        filtered = userusers.filter(f).count()
        query = userusers.filter(f).order_by(orderstr, 'id')[offset:offset + limit]
    else:
        filtered = total
        query = userusers.all().order_by(orderstr, 'id')[offset:offset + limit]
    data = []
    for u in query:
        if u.last_login is None:
            llstr = None
        else:
            llstr = u.last_login.strftime('%Y-%m-%d %H:%M:%S')
        # Manage [username, can_delete, is_active, can_lock]
        data.append([u.username, u.first_name, u.last_name, u.email, llstr, u.is_active, [u.is_superuser, u.is_staff],
                     [u.username, not ((u.username == 'admin' and u.is_superuser and u.is_staff)
                                       or u.username == request.user.username),
                      u.is_active,
                      not (u.username == request.user.username or
                           (u.is_superuser and u.is_staff and nrsuperusers < 2))]])
    draw = request.GET['draw']
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('users.view_users')
def info(request, username):
    user = get_object_or_404(User, username=username)
    nrsuperusers = User.objects.filter(is_superuser=True).count()
    profile = Profile.objects.get(user=user)
    canlock = not (user.username == request.user.username or (user.is_superuser and nrsuperusers < 2))
    dl = getDepartmentsListfilter(request, user.profile.departments.all())
    departform = UserAdddepartmentForm(departments=dl)
    rl = getRolesListfilter(user.groups.all())
    rolesform = UserAddroleForm(roles=rl)
    context = {'User': user, 'Profile': profile, 'userstatusdisplay': 1,
               'contentheader': 'Users', 'apppath': ['Users', 'Info', username], 'canlock': canlock,
               'nrsuperusers': nrsuperusers, 'formdepart': departform, 'formrole': rolesform}
    updateMenuNumbers(request, context)
    return render(request, 'users/info.html', context)


def infodeparts(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    departments = profile.departments.all()
    context = {'Departments': departments}
    return render(request, 'users/infodeparts.html', context)


def inforoles(request, username):
    user = get_object_or_404(User, username=username)
    roles = user.groups.all()
    context = {'Roles': roles}
    return render(request, 'users/inforoles.html', context)


@perm_required('departments.add_members')
def adddepart(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    status = [False, '']
    if request.method == 'POST':
        dl = getDepartmentsList()
        form = UserAdddepartmentForm(departments=dl, data=request.POST)
        if form.is_valid():
            shortname = form.cleaned_data['departments']
            with transaction.atomic():
                status = [True, shortname]
                department = Departments.objects.get(shortname=shortname)
                profile.departments.add(department)
        else:
            status = [False, 'Error: Cannot validate %s' % form.errors.as_data()]
    return JsonResponse(status, safe=False)


@perm_required('users.change_users')
def addroles(request, username):
    user = get_object_or_404(User, username=username)
    status = [False, '']
    if request.method == 'POST':
        rl = getRolesList()
        form = UserAddroleForm(roles=rl, data=request.POST)
        if form.is_valid():
            rolename = form.cleaned_data['roles']
            with transaction.atomic():
                status = [True, rolename]
                group = Group.objects.get(name=rolename)
                user.groups.add(group)
        else:
            status = [False, 'Error: Cannot validate %s' % form.errors.as_data()]
    return JsonResponse(status, safe=False)


@perm_required('departments.delete_members')
def departdelete(request, username, name):
    department = get_object_or_404(Departments, name=name)
    profile = get_object_or_404(Profile, user__username=username)
    with transaction.atomic():
        profile.departments.remove(department)
        status = [True, department.shortname, truncatechars(name, 40)]
    return JsonResponse(status, safe=False)


@perm_required('users.change_users')
def rolesdelete(request, username, name):
    group = get_object_or_404(Group, name=name)
    user = get_object_or_404(User, username=username)
    with transaction.atomic():
        user.groups.remove(group)
        status = [True, name, truncatechars(name, 40)]
    return JsonResponse(status, safe=False)


def userprofile(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    departments = profile.departments.all()
    dashboard = Dashboardwidgets.objects.filter(user=user).order_by('widget')
    if not dashboard.count():
        # no widgets in profile populate default
        widgets = Widgets.objects.all()
        for w in widgets:
            dbwidget = Dashboardwidgets(user=user, widget=w)
            dbwidget.enabled = False
            dbwidget.save()
        dashboard = Dashboardwidgets.objects.filter(user=user)
    clientlist = getUserClients(request)
    clients = []
    for clientres in clientlist:
        clientparams = getDIRClientparams(clientres)
        clientparams = extractclientparams(clientparams)
        clients.append({
            'Name': clientparams['Name'],
            'OS': clientparams['OS'],
        })
    context = {'User': user, 'Profile': profile, 'Departments': departments, 'contentheader': 'User Profile',
               'apppath': ['Profile'], 'Clients': clients, 'Dashboard': dashboard}
    updateMenuNumbers(request, context)
    return render(request, 'users/profile.html', context)


def userprofiledash(request, stat, widgetid):
    user = request.user
    widget = get_object_or_404(Dashboardwidgets, user=user, widget__widgetid=widgetid)
    if stat == 'on':
        widget.enabled = True
        profile = Profile.objects.get(user=user)
        pcol1 = profile.dashboardcol1
        if pcol1 is not None and pcol1 != '':
            col1 = pcol1.split(',')
        else:
            profile.dashboardcol1 = ''
            col1 = []
        pcol2 = profile.dashboardcol2
        if pcol2 is not None and pcol2 != '':
            col2 = pcol2.split(',')
        else:
            col2 = []
            profile.dashboardcol2 = ''
        if widgetid not in col1+col2:
            if len(col1) > len(col2):
                if profile.dashboardcol2 != '':
                    profile.dashboardcol2 += ',' + widgetid
                else:
                    profile.dashboardcol2 += widgetid
            else:
                if profile.dashboardcol1 != '':
                    profile.dashboardcol1 += ',' + widgetid
                else:
                    profile.dashboardcol1 += widgetid
            profile.save()
    else:
        widget.enabled = False
    widget.save()
    return JsonResponse(True, safe=False)


@perm_required('users.add_users')
def adduser(request):
    departments = getUserDepartmentsList(request, default=False)
    roles = getRolesList()
    usertypeslist = getusertypeslist(request)
    if request.method == 'GET':
        form = UserForm(departments=departments, roles=roles, usertypes=usertypeslist)
        # When add a User it should have a password
        form.fields['password'].required = True
        # admin should provide departments when in departments
        if not userissuperuser(request) and getDepartmentssnr(request) > 0:
            form.fields['departments'].required = True
        form.fields['password'].required = True
        context = {'contentheader': 'Users', 'apppath': ['Users', 'Add'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'users/add.html', context)
    else:
        # print request.POST
        add = request.POST.get('add', 0)
        cancel = request.POST.get('cancel', 0)
        if add and not cancel:
            form = UserForm(data=request.POST, departments=departments, roles=roles, usertypes=usertypeslist)
            # When add a User it should have a password
            form.fields['password'].required = True
            # admin should provide departments when in departments
            if not userissuperuser(request) and getDepartmentssnr(request) > 0:
                form.fields['departments'].required = True
            if form.is_valid():
                username = form.cleaned_data['username']
                # Ugly hack for limiting database varchar(150)
                usernamelen = len(username.encode('UTF-8'))
                if usernamelen > 150:
                    username = username[:(150 - usernamelen)/2]
                firstname = form.cleaned_data['firstname']
                lastname = form.cleaned_data['lastname']
                # Ugly hack for limiting database varchar(30)
                firstnamelen = len(firstname.encode('UTF-8'))
                if firstnamelen > 30:
                    firstname = firstname[:(30-firstnamelen)/2]
                lastnamelen = len(lastname.encode('UTF-8'))
                if lastnamelen > 30:
                    lastname = lastname[:(30-lastnamelen)/2]
                email = form.cleaned_data['email']
                usertype = form.cleaned_data['usertype']
                depart = form.cleaned_data['departments']
                uroles = form.cleaned_data['roles']
                password = form.cleaned_data['password']
                # [u'adm', u'finacc', u'it']
                # create User
                with transaction.atomic():
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.first_name = firstname
                    user.last_name = lastname
                    if usertype == 'admin':
                        user.is_superuser = True
                        user.is_staff = False
                    elif usertype == 'super':
                        user.is_staff = True
                        user.is_superuser = True
                    user.save()
                    query = Departments.objects.filter(shortname__in=depart)
                    for dep in query:
                        user.profile.departments.add(dep)
                    query = Group.objects.filter(name__in=uroles)
                    for group in query:
                        user.groups.add(group)
                    log = Log(jobid_id=0, logtext='Create user: ' + username + ' by ' + request.user.username)
                    log.save()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('usersdefined')


@any_perm_required('users.add_users', 'users.change_users')
def checkusername(request):
    """
        JSON for Department name
        when department name already exist then return false
    """
    user = request.GET.get('username', '')
    check = True
    if User.objects.filter(username=user).count() == 1:
        check = False
    return JsonResponse(check, safe=False)


def makeinitailadata(user, backurl):
    data = {
        'username': user.username,
        'firstname': user.first_name,
        'lastname': user.last_name,
        'email': user.email,
        'password': '',
        'usertype': getusertypeinitial(user),
        'backurl': backurl,
    }
    return data


@perm_required('users.change_users')
def edit(request, username):
    user = get_object_or_404(User, username=username)
    usertypeslist = getusertypeslist(request)
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        data = makeinitailadata(user, backurl)
        form = UserForm(departments=[], initial=data, usertypes=usertypeslist)
        form.fields['username'].disabled = True
        if user.is_superuser and user.is_staff:
            form.fields['departments'].disabled = True
        context = {'contentheader': 'Users', 'apppath': ['Users', 'Edit', username], 'form': form,
                   'userstatusdisplay': 1, 'User': user}
        updateMenuNumbers(request, context)
        return render(request, 'users/edit.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if backurl is None or backurl == '':
            backurl = reverse('usersdefined')
        if not cancel:
            data = makeinitailadata(user, backurl)
            post = request.POST.copy()
            post['username'] = username
            if user.username == ' admin':
                post['usertype'] = 'super'
            form = UserForm(data=post, departments=[], initial=data, usertypes=usertypeslist)
            if form.is_valid():
                if form.has_changed():
                    with transaction.atomic():
                        if 'firstname' in form.changed_data:
                            firstname = form.cleaned_data['firstname']
                            # Ugly hack for limiting database varchar(30)
                            firstnamelen = len(firstname.encode('UTF-8'))
                            if firstnamelen > 30:
                                firstname = firstname[:(30 - firstnamelen)/2]
                            user.first_name = firstname
                        if 'lastname' in form.changed_data:
                            lastname = form.cleaned_data['lastname']
                            # Ugly hack for limiting database varchar(30)
                            lastnamelen = len(lastname.encode('UTF-8'))
                            if lastnamelen > 30:
                                lastname = lastname[:(30 - lastnamelen)/2]
                            user.last_name = lastname
                        if 'email' in form.changed_data:
                            user.email = form.cleaned_data['email']
                        if 'usertype' in form.changed_data and user.username != 'admin':
                            usertype = form.cleaned_data['usertype']
                            if usertype == 'std':
                                user.is_staff = False
                                user.is_superuser = False
                            elif usertype == 'admin':
                                user.is_staff = False
                                user.is_superuser = True
                            elif usertype == 'super':
                                user.is_staff = True
                                user.is_superuser = True
                                user.profile.departments.clear()
                                user.groups.clear()
                        if 'password' in form.changed_data:
                            user.set_password(form.cleaned_data['password'])
                        user.save()
                        log = Log(jobid_id=0, logtext='User modification: ' + username + ' by ' + request.user.username)
                        log.save()
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect(backurl)


@perm_required('users.suspend_users')
def userlock(request, username):
    user = get_object_or_404(User, username=username)
    context = [False, user.is_active]
    if user.is_superuser:
        # prevent locking last superadmin
        if User.objects.filter(is_superuser=True).count() < 2:
            return JsonResponse(context, safe=False)
    if request.user.username == user.username:
        # prevent locking himself
        return JsonResponse(context, safe=False)
    user.is_active = False
    user.save()
    context = [True, user.is_active]
    return JsonResponse(context, safe=False)


@perm_required('users.suspend_users')
def userunlock(request, username):
    user = get_object_or_404(User, username=username)
    user.is_active = True
    user.save()
    return JsonResponse([True, True], safe=False)


@perm_required('users.delete_users')
def userdelete(request, username):
    user = get_object_or_404(User, username=username)
    if user.username == request.user.username:
        return JsonResponse(False, safe=False)
    user.delete()
    return JsonResponse(True, safe=False)


def userprofileedit(request):
    user = request.user
    if request.method == 'GET':
        backurl = request.GET.get('b', None)
        data = makeinitailadata(user, backurl)
        form = UserForm(departments=[], initial=data, usertypes=USERTYPE)
        form.fields['username'].disabled = True
        context = {'contentheader': 'Profile Edit', 'apppath': ['Profile', 'Edit'], 'form': form,
                   'User': user}
        updateMenuNumbers(request, context)
        return render(request, 'users/editprofile.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        backurl = request.POST.get('backurl')
        if backurl is None or backurl == '':
            backurl = reverse('usersprofile')
        if not cancel:
            data = makeinitailadata(user, backurl)
            post = request.POST.copy()
            post['username'] = user.username
            form = UserForm(data=post, departments=[], initial=data, usertypes=USERTYPE)
            if form.is_valid():
                if form.has_changed():
                    with transaction.atomic():
                        if 'firstname' in form.changed_data:
                            firstname = form.cleaned_data['firstname']
                            # Ugly hack for limiting database varchar(30)
                            firstnamelen = len(firstname.encode('UTF-8'))
                            if firstnamelen > 30:
                                firstname = firstname[:(30 - firstnamelen)/2]
                            user.first_name = firstname
                        if 'lastname' in form.changed_data:
                            lastname = form.cleaned_data['lastname']
                            # Ugly hack for limiting database varchar(30)
                            lastnamelen = len(lastname.encode('UTF-8'))
                            if lastnamelen > 30:
                                lastname = lastname[:(30 - lastnamelen)/2]
                            user.last_name = lastname
                        if 'email' in form.changed_data:
                            user.email = form.cleaned_data['email']
                        if 'password' in form.changed_data:
                            user.set_password(form.cleaned_data['password'])
                            # special case
                            user.save()
                            return redirect('logout')
                        log = Log(jobid_id=0, logtext='User profile modification: ' + user.username)
                        log.save()
                        user.save()
                        messages.success(request, "User profile updated", extra_tags='Success')
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect(backurl)
