# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from libs.menu import updateMenuNumbers
from libs.job import getJobsrunningnr
from libs.system import *
from libs.plat import *
from libs.bconsole import *
from subprocess import call
from config.conf import *
from .forms import *
from jobs.models import Log


def daemons(request):
    context = {'contentheader': 'Daemons', 'contentheadersmall': 'Manage', 'apppath': ['Backup', 'Daemons']}
    updateMenuNumbers(context)
    updateservicestatus(context)
    return render(request, 'system/daemons.html', context)


def messages(request):
    context = {'contentheader': 'Messages', 'apppath': ['Backup', 'Messages']}
    updateMenuNumbers(context)
    return render(request, 'system/messages.html', context)


def config(request):
    name = getDIRname()
    osver = getOSVersion()
    # TODO: when Director is unavailable then we can't verify backup version
    out = getBackupVersion()
    if len(out) > 0:
        backupver = 'Bacula Enterprise ' + out[0].split(',')[2]
    else:
        backupver = 'Unknown'
    ip = detectipall()
    ipall = [(a, a) for a in ip]
    sip = getSDStorageAddress(sdname=name)
    cip = getFDClientAddress(name=name)
    descr = getDIRdescr()
    email = getDIRadminemail()
    stor = getDIRStorageNames()
    storages = [(a, a) for a in stor]
    defstorage = getDefaultStorage()
    license = getLicenseKey()
    platform = getOSPlatform()
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
    context = {'contentheader': 'System', 'contentheadersmall': 'Config', 'apppath': ['Backup', 'System'], 'form': form,
               'ibadminver': IBADVERSION, 'backupver': backupver, 'osver': osver, 'platform': platform}
    updateMenuNumbers(context)
    updateservicestatus(context)
    return render(request, 'system/config.html', context)


def configsave(request):
    restartinfo = False
    if request.method == 'POST':
        name = getDIRname()
        ip = detectipall()
        ipall = [(a, a) for a in ip]
        sip = getSDStorageAddress(sdname=name)
        cip = getFDClientAddress(name=name)
        descr = getDIRdescr()
        email = getDIRadminemail()
        stor = getDIRStorageNames()
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
        if form.is_valid() and form.has_changed():
            # print "form valid and changed ... ", form.changed_data
            if 'descr' in form.changed_data:
                # print "Update descr!"
                with transaction.atomic():
                    updateDIRDescr(descr=form.cleaned_data['descr'])
            if 'storageip' in form.changed_data:
                # print "Update Storage"
                with transaction.atomic():
                    restartinfo = True
                    updateStorageAddress(sdcomponent=name, address=form.cleaned_data['storageip'])
            if 'clientip' in form.changed_data:
                # print "Update Client"
                with transaction.atomic():
                    restartinfo = True
                    updateClientAddress(name=name, address=form.cleaned_data['clientip'])
            if 'defstorage' in form.changed_data:
                # print "Update defstorage"
                with transaction.atomic():
                    updateDIRdefaultStorage(storname=form.cleaned_data['defstorage'])
            if 'email' in form.changed_data:
                # print "Update email"
                with transaction.atomic():
                    updateDIRadminemail(email=form.cleaned_data['email'])
            directorreload()
        else:
            # TODO zrobic obsługę błędów albo i nie
            print form.is_valid()
            print form.errors.as_data()
    return JsonResponse(restartinfo, safe=False)


def servicestatuswidget(request):
    context = {}
    updateservicestatus(context)
    return JsonResponse(context)


def masterlogdisplay(request):
    logs = getsystemdlog('bacula-dir')
    context = {'Logs': logs, 'daemon': 'Master Daemon logs'}
    return render(request, 'system/daemonlogs.html', context)


def sdlogdisplay(request):
    logs = getsystemdlog('bacula-sd')
    context = {'Logs': logs, 'daemon': 'Storage Daemon logs'}
    return render(request, 'system/daemonlogs.html', context)


def fdlogdisplay(request):
    logs = getsystemdlog('bacula-fd')
    context = {'Logs': logs, 'daemon': 'File Daemon logs'}
    return render(request, 'system/daemonlogs.html', context)


def ibadlogdisplay(request):
    logs = getsystemdlog('ibadstatd')
    context = {'Logs': logs, 'daemon': 'Collector Daemon logs'}
    return render(request, 'system/daemonlogs.html', context)


def masterstop(request):
    confirm = request.GET.get('conf', None)
    if confirm is not None or getJobsrunningnr() == 0:
        status = 1
        call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-dir'])
    else:
        status = 2
    context = {'status': status}
    return JsonResponse(context)


def storagestop(request):
    confirm = request.GET.get('conf', None)
    if confirm is not None or getJobsrunningnr() == 0:
        status = 1
        call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-sd'])
    else:
        status = 2
    context = {'status': status}
    return JsonResponse(context)


def filedaemonstop(request):
    call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-fd'])
    context = {'status': 1}
    return JsonResponse(context)


def ibaddaemonstop(request):
    call([SUDOCMD, SYSTEMCTL, 'stop', 'ibadstatd'])
    context = {'status': 1}
    return JsonResponse(context)


def masterstart(request):
    call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-dir'])
    context = {'status': 1}
    return JsonResponse(context)


def storagestart(request):
    call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-sd'])
    context = {'status': 1}
    return JsonResponse(context)


def filedaemonstart(request):
    call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-fd'])
    context = {'status': 1}
    return JsonResponse(context)


def ibaddaemonstart(request):
    call([SUDOCMD, SYSTEMCTL, 'start', 'ibadstatd'])
    context = {'status': 1}
    return JsonResponse(context)


def masterrestart(request):
    confirm = request.GET.get('conf', None)
    if confirm is not None or getJobsrunningnr() == 0:
        status = 1
        call([SUDOCMD, SYSTEMCTL, 'restart', 'bacula-dir'])
    else:
        status = 2
    context = {'status': status}
    return JsonResponse(context)


def storagerestart(request):
    confirm = request.GET.get('conf', None)
    if confirm is not None or getJobsrunningnr() == 0:
        status = 1
        call([SUDOCMD, SYSTEMCTL, 'restart', 'bacula-sd'])
    else:
        status = 2
    context = {'status': status}
    return JsonResponse(context)


def filedaemonrestart(request):
    call([SUDOCMD, SYSTEMCTL, 'restart', 'bacula-fd'])
    context = {'status': 1}
    return JsonResponse(context)


def ibaddaemonrestart(request):
    call([SUDOCMD, SYSTEMCTL, 'restart', 'ibadstatd'])
    context = {'status': 1}
    return JsonResponse(context)


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


def messagesclear(request):
    query = Log.objects.filter(jobid=0).all()
    query.delete()
    context = {'status': 1}
    return JsonResponse(context)
