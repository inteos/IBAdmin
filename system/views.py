# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from libs.menu import updateMenuNumbers
from libs.job import getJobsrunningnr
from libs.system import *
from libs.storage import getDIRStorageNames
from libs.plat import *
from libs.bconsole import *
from subprocess import call
from config.confinfo import *
from config.client import *
from .forms import *
from jobs.models import Log
from users.decorators import *


@userissuperuser_required()
def daemons(request):
    context = {'contentheader': 'Daemons', 'contentheadersmall': 'Manage', 'apppath': ['Backup', 'Daemons']}
    updateMenuNumbers(request, context)
    updateservicestatus(context)
    return render(request, 'system/daemons.html', context)


@userissuperuser_required()
def messages(request):
    context = {'contentheader': 'Messages', 'apppath': ['Backup', 'Messages']}
    updateMenuNumbers(request, context)
    return render(request, 'system/messages.html', context)


@userissuperuser_required()
def config(request):
    name = getDIRname()
    osver = getOSVersion()
    # TODO: when Director is unavailable then we can't verify backup version
    out = getBackupVersion()
    backupver = "%s %s" % (out['edition'], out['version'])
    ip = detectipall()
    ipall = [(a, a) for a in ip]
    sip = getDIRInternalStorageAddress()
    cip = getFDClientAddress(name=name)
    descr = getDIRdescr()
    email = getDIRadminemail()
    stor = getDIRStorageNames(request)
    storages = [(a, a) for a in stor]
    defstorage = getDefaultStorage()
    license = getLicenseKey()
    platforminfo = getOSPlatform()
    data = {
        'name': name,
        'descr': descr,
        'email': email,
        'storageip': sip,
        'clientip': cip,
        'defstorage': defstorage,
        'license': license,
    }
    form = SystemConfigForm(storageip=ipall, clientip=ipall, storages=storages, initial=data)
    form.fields['name'].disabled = True
    form.fields['license'].disabled = True
    if len(storages) < 2:
        form.fields['defstorage'].disabled = True
    if len(ip) < 2:
        form.fields['storageip'].disabled = True
        form.fields['clientip'].disabled = True
    context = {'contentheader': 'System', 'contentheadersmall': 'Config', 'apppath': ['Backup', 'Config'],
               'form': form, 'backupver': backupver, 'osver': osver, 'platform': platforminfo}
    updateMenuNumbers(request, context)
    updateservicestatus(context)
    return render(request, 'system/config.html', context)


@userissuperuser_required()
def configsave(request):
    restartinfo = False
    if request.method == 'POST':
        name = getDIRname()
        ip = detectipall()
        ipall = [(a, a) for a in ip]
        sip = getDIRInternalStorageAddress()
        cip = getFDClientAddress(name=name)
        descr = getDIRdescr()
        email = getDIRadminemail()
        stor = getDIRStorageNames(request)
        storages = [(a, a) for a in stor]
        defstorage = getDefaultStorage()
        data = {
            'name': name,
            'descr': descr,
            'email': email,
            'storageip': sip,
            'clientip': cip,
            'defstorage': defstorage,
        }
        post = request.POST.copy()
        if post.get('defstorage') is None:
            post['defstorage'] = defstorage
        if post.get('storageip') is None:
            post['storageip'] = sip
        if post.get('clientip') is None:
            post['clientip'] = cip
        form = SystemConfigForm(storageip=ipall, clientip=ipall, storages=storages, initial=data, data=post)
        if form.is_valid():
            if form.has_changed():
                # print "form valid and changed ... ", form.changed_data
                with transaction.atomic():
                    if 'descr' in form.changed_data:
                        # print "Update descr!"
                        updateDIRDescr(request, descr=form.cleaned_data['descr'])
                    if 'defstorage' in form.changed_data:
                        # print "Update defstorage"
                        updateDIRdefaultStorage(storname=form.cleaned_data['defstorage'])
                    if 'storageip' in form.changed_data:
                        # print "Update Storage IP"
                        restartinfo = True
                        updateStorageAddress(sdcomponent=name, address=form.cleaned_data['storageip'])
                    if 'clientip' in form.changed_data:
                        # print "Update Client IP"
                        restartinfo = True
                        updateClientAddress(request, name=name, address=form.cleaned_data['clientip'])
                    if 'email' in form.changed_data:
                        # print "Update email"
                        updateDIRadminemail(email=form.cleaned_data['email'])
                directorreload()
        else:
            messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return JsonResponse(restartinfo, safe=False)


def servicestatuswidget(request):
    context = {}
    updateservicestatus(context)
    return JsonResponse(context)


@userissuperuser_required()
def masterlogdisplay(request):
    logs = getsystemdlog('bacula-dir')
    context = {'Logs': logs, 'daemon': 'Master Daemon logs'}
    return render(request, 'system/daemonlogs.html', context)


@userissuperuser_required()
def sdlogdisplay(request):
    logs = getsystemdlog('bacula-sd')
    context = {'Logs': logs, 'daemon': 'Storage Daemon logs'}
    return render(request, 'system/daemonlogs.html', context)


@userissuperuser_required()
def fdlogdisplay(request):
    logs = getsystemdlog('bacula-fd')
    context = {'Logs': logs, 'daemon': 'File Daemon logs'}
    return render(request, 'system/daemonlogs.html', context)


@userissuperuser_required()
def ibadlogdisplay(request):
    logs = getsystemdlog('ibadstatd')
    context = {'Logs': logs, 'daemon': 'Collector Daemon logs'}
    return render(request, 'system/daemonlogs.html', context)


@userissuperuser_required()
def masterstop(request):
    confirm = request.GET.get('conf', None)
    if confirm is not None or getJobsrunningnr(request) == 0:
        status = 1
        call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-dir'])
    else:
        status = 2
    context = {'status': status}
    return JsonResponse(context)


@userissuperuser_required()
def storagestop(request):
    confirm = request.GET.get('conf', None)
    if confirm is not None or getJobsrunningnr(request) == 0:
        status = 1
        call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-sd'])
    else:
        status = 2
    context = {'status': status}
    return JsonResponse(context)


@userissuperuser_required()
def filedaemonstop(request):
    call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-fd'])
    context = {'status': 1}
    return JsonResponse(context)


@userissuperuser_required()
def ibaddaemonstop(request):
    call([SUDOCMD, SYSTEMCTL, 'stop', 'ibadstatd'])
    context = {'status': 1}
    return JsonResponse(context)


@userissuperuser_required()
def masterstart(request):
    call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-dir'])
    context = {'status': 1}
    return JsonResponse(context)


@userissuperuser_required()
def storagestart(request):
    call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-sd'])
    context = {'status': 1}
    return JsonResponse(context)


@userissuperuser_required()
def filedaemonstart(request):
    call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-fd'])
    context = {'status': 1}
    return JsonResponse(context)


@userissuperuser_required()
def ibaddaemonstart(request):
    call([SUDOCMD, SYSTEMCTL, 'start', 'ibadstatd'])
    context = {'status': 1}
    return JsonResponse(context)


@userissuperuser_required()
def masterrestart(request):
    confirm = request.GET.get('conf', None)
    if confirm is not None or getJobsrunningnr(request) == 0:
        status = 1
        call([SUDOCMD, SYSTEMCTL, 'restart', 'bacula-dir'])
    else:
        status = 2
    context = {'status': status}
    return JsonResponse(context)


@userissuperuser_required()
def storagerestart(request):
    confirm = request.GET.get('conf', None)
    if confirm is not None or getJobsrunningnr(request) == 0:
        status = 1
        call([SUDOCMD, SYSTEMCTL, 'restart', 'bacula-sd'])
    else:
        status = 2
    context = {'status': status}
    return JsonResponse(context)


@userissuperuser_required()
def filedaemonrestart(request):
    call([SUDOCMD, SYSTEMCTL, 'restart', 'bacula-fd'])
    context = {'status': 1}
    return JsonResponse(context)


@userissuperuser_required()
def ibaddaemonrestart(request):
    call([SUDOCMD, SYSTEMCTL, 'restart', 'ibadstatd'])
    context = {'status': 1}
    return JsonResponse(context)


@userissuperuser_required()
def messagesdata(request):
    """ JSON for jobs running datatable """
    cols = ['time', 'logtext']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Log.objects.filter(jobid=0).all().count()
    orderstr = order_dir + order_col
    if search != '':
        filtered = Log.objects.filter(jobid=0, logtext__icontains=search).count()
        query = Log.objects.filter(jobid=0, logtext__icontains=search).order_by(orderstr)[offset:offset + limit]
    else:
        filtered = total
        query = Log.objects.filter(jobid=0).order_by(orderstr)[offset:offset + limit]
    data = []
    for l in query:
        data.append([l.time.strftime('%Y-%m-%d %H:%M:%S'), l.logtext])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@userissuperuser_required()
def messagesclear(request):
    query = Log.objects.filter(jobid=0).all()
    query.delete()
    context = {'status': 1}
    return JsonResponse(context)
