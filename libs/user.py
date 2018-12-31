# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import Permission, ContentType
from config.confinfo import *
from config.restype import RESTYPE
from .department import *
from virtual.models import *


def getUsersnr(request):
    if not hasattr(request, "ibadminusersnr"):
        users = getUserUsers(request).count()
        request.ibadminusersnr = users
    return request.ibadminusersnr


def updateUsersnr(request, context):
    val = getUsersnr(request)
    context.update({'usersnr': val})


def getUserList():
    users = User.objects.exclude(is_staff=True).all()
    data = []
    for d in users:
        name = d.get_full_name() or d.username
        data.append((d.username, name))
    return data


def getUserListfiltered(exlist=(), full_view=False):
    users = User.objects.exclude(is_staff=True).exclude(username__in=exlist).all()
    data = ()
    for d in users:
        name = d.get_full_name()
        if not full_view:
            name = name or d.username
        else:
            if name != '':
                name += ' (' + d.username + ')'
            else:
                name = d.username
        data += ((d.username, name),)
    return data


def get_system_permissions():
    content_types = ContentType.objects.filter(model='permissions').order_by('app_label')
    ctlist = []
    for ct in content_types:
        ctname = ct.app_label.capitalize()
        perms = Permission.objects.filter(content_type=ct).exclude(codename__icontains='_permissions')
        permlist = [('addallperms_'+ct.app_label, '- Add all permissions in ' + ctname + ' -')]
        for p in perms:
            permlist.append((p.codename, p.name,))
        ctlist.append((ctname, permlist,))
    return ctlist


def get_system_permissions_filtered(group):
    content_types = ContentType.objects.filter(model='permissions').order_by('app_label')
    ctlist = []
    groupperms = group.permissions.all()
    for ct in content_types:
        ctname = ct.app_label.capitalize()
        perms = Permission.objects.filter(content_type=ct).exclude(id__in=groupperms)\
            .exclude(codename__icontains='_permissions')
        if perms.count():
            permlist = [('addallperms_'+ct.app_label, '- Add all permissions in ' + ctname + ' -')]
        else:
            permlist = []
        for p in perms:
            permlist.append((p.codename, p.name,))
        ctlist.append((ctname, permlist,))
    return ctlist


def get_role_permissions(group):
    perms = group.permissions.all()
    datalist = {}
    for p in perms:
        ctname = p.content_type.app_label
        permtab = datalist.get(ctname)
        if permtab is None:
            permtab = []
        permtab.append((p.codename, p.name,))
        datalist[ctname] = permtab
    permlist = []
    content_types = ContentType.objects.filter(model='permissions').order_by('app_label')
    for label in content_types:
        ctname = label.app_label
        permlist.append({
            'name': ctname.capitalize(),
            'applabel': ctname,
            'perms': datalist.get(ctname),
        })
    return permlist


def createadminuser(email='root@localhost', password='password'):
    user = User.objects.create_user(username='admin', email=email, password=password)
    user.first_name = ''
    user.last_name = ''
    user.is_staff = True
    user.is_superuser = True
    user.save()


def getUserClients(request, dircompid=None):
    """
    Return a queryset which represents a list of clients which user should has access to.
    :param request: a Django request class
    :param dircompid: Director CompID
    :return: queryset
    """
    if not hasattr(request, "ibadminclientsqueryuser"):
        if dircompid is None:
            dircompid = getDIRcompid(request)
        if request.user.is_superuser and request.user.is_staff:
            query = ConfResource.objects.filter(compid_id=dircompid, type=RESTYPE['Client'])\
                .exclude(confparameter__name='.Disabledfordelete').order_by('name')
        else:
            departs = getUserDepartmentsval(request)
            if departs.count() > 0:
                query = ConfResource.objects.filter(compid_id=dircompid, type=RESTYPE['Client'],
                                                    confparameter__name='.Department',
                                                    confparameter__value__in=departs)\
                    .exclude(confparameter__name='.Disabledfordelete').order_by('name')
            else:
                query = ConfResource.objects.filter(compid_id=dircompid, type=RESTYPE['Client'])\
                    .exclude(confparameter__name='.Department')\
                    .exclude(confparameter__name='.Disabledfordelete').order_by('name')
        request.ibadminclientsqueryuser = query
    return request.ibadminclientsqueryuser


def getUserClientsnames(request, dircompid=None):
    """
    Return a value queryset for clients which user should has access to.
    :param request: a Django request class
    :param dircompid: Director CompID
    :return: queryset values
    """
    if not hasattr(request, "ibadminclientslistuser"):
        if dircompid is None:
            dircompid = getDIRcompid(request)
        request.ibadminclientslistuser = getUserClients(request, dircompid).values('name')
    return request.ibadminclientslistuser


def getUserStorages(request, dircompid=None):
    """
    Return a queryset which represents a list of storages which user should has access to.
    :param request: a Django request class
    :param dircompid: Director CompID
    :return: queryset
    """
    if not hasattr(request, "ibadminstoragesqueryuser"):
        if dircompid is None:
            dircompid = getDIRcompid(request)
        if request.user.is_superuser and request.user.is_staff:
            query = ConfResource.objects.filter(compid_id=dircompid, type=RESTYPE['Storage'])\
                .exclude(confparameter__name='.Disabledfordelete').distinct().order_by('name')
        else:
            departs = getUserDepartmentsval(request)
            if departs.count() > 0:
                query = ConfResource.objects.filter(compid_id=dircompid, type=RESTYPE['Storage'],
                                                    confparameter__name='.Department',
                                                    confparameter__value__in=departs)\
                    .exclude(confparameter__name='.Disabledfordelete').distinct().order_by('name')
            else:
                query = ConfResource.objects.filter(compid_id=dircompid, type=RESTYPE['Storage'])\
                    .exclude(confparameter__name='.Department')\
                    .exclude(confparameter__name='.Disabledfordelete').order_by('name')
        request.ibadminstoragesqueryuser = query
    return request.ibadminstoragesqueryuser


def getUserStoragesnames(request, dircompid=None):
    """
    Return a value queryset for storages which user should has access to.
    :param request: a Django request class
    :param dircompid: Director CompID
    :return: queryset values
    """
    if not hasattr(request, "ibadminstorageslistuser"):
        if dircompid is None:
            dircompid = getDIRcompid(request)
        request.ibadminstorageslistuser = getUserStorages(request, dircompid).values('name')
    return request.ibadminstorageslistuser


def getUserJobs(request, dircompid=None):
    """
    Return a queryset which represents a list of jobs which user should has access to.
    :param request: a Django request class
    :param dircompid: Director CompID
    :return: queryset
    """
    if not hasattr(request, "ibadminjobsqueryuser"):
        if dircompid is None:
            dircompid = getDIRcompid(request)
        if request.user.is_superuser and request.user.is_staff:
            query = ConfResource.objects.filter(compid_id=dircompid, type=RESTYPE['Job'])\
                .exclude(confparameter__name='.Disabledfordelete')
        else:
            departclients = getUserClientsnames(request, dircompid)
            query = ConfResource.objects.filter(compid_id=dircompid, type=RESTYPE['Job'], confparameter__name='Client',
                                                confparameter__value__in=departclients)\
                .exclude(confparameter__name='.Disabledfordelete')
        request.ibadminjobsqueryuser = query
    return request.ibadminjobsqueryuser


def getUserJobsnames(request, dircompid=None):
    """
    Return a value queryset for jobs which user should has access to.
    :param request: a Django request class
    :param dircompid: Director CompID
    :return: queryset values
    """
    if not hasattr(request, "ibadminjobslistuser"):
        if dircompid is None:
            dircompid = getDIRcompid(request)
        request.ibadminjobslistuser = getUserJobs(request, dircompid).values('name')
    return request.ibadminjobslistuser


def getUservCenters(request):
    """
    Return a queryset which represents a list of vcenters which user should has access to.
    :param request: a Django request class
    :return: queryset
    """
    if not hasattr(request, "ibadminvcentersqueryuser"):
        if request.user.is_superuser and request.user.is_staff:
            query = vCenterHosts.objects.all()
        else:
            departs = getUserDepartmentsval(request)
            if departs.count() > 0:
                query = vCenterHosts.objects.filter(department__in=departs)
            else:
                query = vCenterHosts.objects.filter(department=None)
        request.ibadminvcentersqueryuser = query
    return request.ibadminvcentersqueryuser


def getUserUsers(request):
    """
    Return a queryset which represents a list of Users which user should has access to.
    :param request: a Django request class
    :return: queryset
    """
    if not hasattr(request, "ibadminusersqueryuser"):
        if request.user.is_superuser and request.user.is_staff:
            query = User.objects.all()
        else:
            departs = getUserDepartments(request)
            if departs.count() > 0:
                query = User.objects.filter(profile__departments__in=departs).distinct()
            else:
                query = User.objects.filter(profile__departments=None).distinct()
        request.ibadminusersqueryuser = query
    return request.ibadminusersqueryuser


def getusertypeinitial(user):
    if user.is_superuser:
        if user.is_staff:
            return 'super'
        else:
            return 'admin'
    return 'std'


def userissuperuser(request):
    user = request
    if hasattr(request, "user"):
        user = request.user
    if user.is_superuser and user.is_staff:
        return True
    return False
