# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from libs.menu import updateMenuNumbers
from libs.storage import *
from libs.system import *
from libs.bconsole import *
from libs.task import prepareTask
from libs.tapelib import detectlibs
from libs.job import *
from config.conf import *
from config.confinfo import *
from .models import *
from .forms import *
from jobs.models import Job, Log
from tasks.models import Tasks
from datetime import timedelta
from libs.ibadmin import *
from libs.department import *
from users.decorators import *
import ast


@perm_required('storages.view_storages')
def defined(request):
    """ Defined Storages table - list """
    storagelist = getUserStorages(request)
    userdeparts = getUserDepartments(request)
    storagedefined = []
    for storage in storagelist:
        storageparams = extractstorageparams(getDIRStorageparams(storage))
        departs = storageparams.get('Departments')
        dlist = []
        if departs is not None:
            for d in departs:
                if userdeparts.filter(shortname=d).count() > 0:
                    dlist.append(getDepartment(d))
            if len(dlist) > 3:
                dlist = dlist[:2]
                storageparams['departslice'] = 1
        storageparams.update({'Departments': dlist})
        storagedefined.append(storageparams)
    context = {'contentheader': 'Storage', 'contentheadersmall': 'currently defined',
               'apppath': ['Storage', 'Defined'], 'StorageDefined': storagedefined}
    updateMenuNumbers(request, context)
    return render(request, 'storage/defined.html', context)


@perm_required('storages.view_storages')
def info(request, name):
    """ Storage info and status """
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    departs = storage.get('Departments')
    dlist = []
    if departs is not None:
        for d in departs:
            dlist.append(getDepartment(d))
    storage.update({'Departments': dlist})
    storagealert = request.GET.get('n', 0)
    storagealertheader = "Restart required!"
    try:
        if int(storagealert) == 1:
            # new storage added
            storagealertheader = "New Storage added!"
        if int(storagealert) == 2:
            # new storage added
            storagealertheader = "Storage hardware configuration changed!"
    except (ValueError, TypeError):
        storagealert = None
    context = {'contentheader': 'Storage', 'apppath': ['Storage', 'Info', name], 'Storage': storage,
               'storagealert': storagealert, 'storagealertheader': storagealertheader, 'storagestatusdisplay': 1}
    updateMenuNumbers(request, context)
    return render(request, 'storage/storage.html', context)


@perm_required('jobs.view_jobs')
def historydata(request, name):
    """ wywołanie ajax dla datatables podający zadania uruchomione dla danego storage """
    cols = ['jobid', 'name', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', 'jobstatus', '']
    draw = request.GET['draw']
    userjobs = getUserJobs(request).values('name')
    jobidlist = Jobmedia.objects.filter(mediaid__storageid__name=name, jobid__name__in=userjobs) \
        .distinct('jobid').values('jobid')
    totalquery = Job.objects.filter(jobid__in=jobidlist)

    (jobslist, total, filtered) = getJobsfiltered(request, jobstatus=JOBALLSTATUS, cols=cols, totalquery=totalquery)
    data = []
    for job in jobslist:
        sstr = getstdtimetext(job.get("Start"))
        estr = getstdtimetext(job.get("End"))
        jid = job.get('JobId')
        jn = job.get('Name')
        jtype = job.get('Type')
        jstatus = job.get('Status')
        data.append([jid, jn, sstr, estr,
                     ibadmin_render_joblevel(job.get('Level'), jtype),
                     job.get('Files'), job.get('Bytes'),
                     ibadmin_render_jobstatus(jstatus, job.get('Errors')),
                     [jid, jn, jtype, jstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('storages.status_storages')
def status(request, name):
    """ Storage online status """
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    devname = storage['Device']
    devices = getSDDevicesList(component=storage['StorageComponent'], storage=devname)
    context = {'contentheader': 'Storage', 'apppath': ['Storage', 'Status', name], 'Storage': storage,
               'Devices': devices, 'storagestatusdisplay': 1}
    updateMenuNumbers(request, context)
    return render(request, 'storage/status.html', context)


@perm_required('storages.status_storages')
def statusheader(request, name):
    """ wywołanie ajax dla parametrów storage """
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storparams = extractstorageparams(storageres)
    stat = getStorageStatus(name)
    if stat is None:
        context = {'Storage': {'Status': 0, 'Name': name}}
    else:
        plug = stat.get('plugins')
        if plug is not None and plug != '':
            plug = plug.split(',')
        else:
            plug = []
        driv = stat.get('drivers')
        if driv is not None and driv != '':
            driv = driv.split(',')
        else:
            driv = []
        storage = {
            'Name': name,
            'Agent': stat.get('name'),
            'Status': 1,
            'Version': stat.get('version'),
            'Started': stat.get('started'),
            'RunJobs': int(stat.get('jobs_run')),
            'JobsRunning': int(stat.get('jobs_running')),
            'Plugins': plug,
            'Drivers': driv,
        }
        context = {'Storage': storage, 'Storparams': storparams}
    return render(request, 'storage/statusheader.html', context)


@perm_required('storages.status_storages')
def statusdevices(request, name):
    """ wywołanie ajax dla statusu urządzeń """
    storage = getDIRStorageinfo(name=name)
    if storage is None:
        context = {'Devices': []}
    else:
        storageparams = extractstorageparams(storage)
        devname = storageparams['Device']
        devices = getSDDevicesList(component=storageparams['StorageComponent'], storage=devname)
        runningjobs = getStoragerunningJobs(name)
        status = []
        for dev in devices:
            params = getStorageStatusDevice(storage=name, device=dev)
            params['Name'] = dev
            for job in runningjobs:
                if job['Device'] == dev:
                    params['Status'] = 'Running'
                    break
            status.append(params)
        context = {'Devices': status}
    return render(request, 'storage/statusdevices.html', context)


@perm_required('storages.view_dedup')
def dedup(request, name):
    """ Storage online status """
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    if not storage.get('MediaType', '').startswith('Dedup'):
        raise Http404()
    context = {'contentheader': 'Storage', 'apppath': ['Storage', 'Dedup Engine', name], 'Storage': storage,
               'storagestatusdisplay': 1, 'blk': range(1, 66)}
    updateMenuNumbers(request, context)
    return render(request, 'storage/dedup.html', context)


@perm_required('storages.view_dedup')
def dedupdata(request, name):
    """ Storage online status data """
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    if not storage.get('MediaType', '').startswith('Dedup'):
        raise Http404()
    (dedupengine, dedupcontainers) = getStorageStatusDedup(storage=name)
    context = {'dedupengine': dedupengine, 'dedupcontainers': dedupcontainers}
    return JsonResponse(context)


@perm_required('storages.view_storages')
def storagevolumesnr(request):
    context = {}
    updateStorageVolumesnr(context)
    return JsonResponse(context, safe=False)


@perm_required('storages.view_volumes')
def volumes(request):
    context = {'contentheader': 'Volumes list', 'apppath': ['Storage', 'Volumes']}
    updateMenuNumbers(request, context)
    return render(request, 'storage/volumes.html', context)


@perm_required('storages.view_volumes')
def volumesdata(request):
    cols = ['volumename', 'poolid__name', 'mediatype', 'volbytes', 'volstatus', 'lastwritten', 'volretention', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Media.objects.all().count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(volumename__icontains=search) | Q(mediatype__icontains=search) | Q(poolid__name__icontains=search) | \
            Q(poolid__name__icontains=search.replace(' ','-')) | Q(volstatus__icontains=search)
        filtered = Media.objects.filter(f).count()
        query = Media.objects.select_related('poolid').filter(f).order_by(orderstr)[offset:offset + limit]
    else:
        filtered = total
        query = Media.objects.select_related('poolid').order_by(orderstr)[offset:offset + limit]
    data = []
    for v in query:
        if v.lastwritten is None:
            lastwritten = '-'
            expired = '-'
        else:
            lastwritten = v.lastwritten.strftime('%Y-%m-%d %H:%M:%S')
            expired = (v.lastwritten + timedelta(seconds=v.volretention)).strftime('%Y-%m-%d %H:%M:%S')
        data.append([v.volumename, getretentiontext(v.poolid.name), v.mediatype, v.volbytes, v.volstatus,
                     lastwritten, expired, [v.volumename, v.volstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('storages.view_volumes')
def volinfo(request, name):
    volume = get_object_or_404(Media.objects.select_related('poolid'), volumename=name)
    if volume.lastwritten is None:
        expired = '-'
    else:
        expired = volume.lastwritten + timedelta(seconds=volume.volretention)
    context = {'contentheader': 'Volume Info', 'apppath': ['Storage', 'Volume', 'Info', name], 'Volume': volume,
                'Volexpired': expired, 'volumestatusdisplay': 1}
    updateMenuNumbers(request, context)
    return render(request, 'storage/volinfo.html', context)


@perm_required('jobs.view_jobs')
def volhistorydata(request, name):
    cols = ['jobid', 'name', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', 'jobstatus', '']
    draw = request.GET['draw']
    userjobs = getUserJobsnames(request)
    jobidlist = Jobmedia.objects.filter(mediaid__volumename=name, jobid__name__in=userjobs) \
        .distinct('jobid').values('jobid')
    totalquery = Job.objects.filter(jobid__in=jobidlist)

    (jobslist, total, filtered) = getJobsfiltered(request, jobstatus=JOBALLSTATUS, cols=cols, totalquery=totalquery)
    data = []
    for job in jobslist:
        sstr = getstdtimetext(job.get("Start"))
        estr = getstdtimetext(job.get("End"))
        jid = job.get('JobId')
        jn = job.get('Name')
        jtype = job.get('Type')
        jstatus = job.get('Status')
        data.append([jid, jn, sstr, estr,
                     ibadmin_render_joblevel(job.get('Level'), jtype),
                     job.get('Files'), job.get('Bytes'),
                     ibadmin_render_jobstatus(jstatus, job.get('Errors')),
                     [jid, jn, jtype, jstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('storages.view_volumelogs')
def vollogdata(request, name):
    cols = ['time', 'jobid', 'logtext']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = Log.objects.filter(logtext__contains='Volume "' + name + '"').count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(logtext__icontains=search)
        filtered = Log.objects.filter(Q(logtext__contains='Volume "' + name + '"'), f).count()
        query = Log.objects.filter(Q(logtext__contains='Volume "' + name + '"'), f)\
            .order_by(orderstr, 'logid')[offset:offset + limit]
    else:
        filtered = total
        query = Log.objects.filter(logtext__contains='Volume "' + name + '"')\
            .order_by(orderstr, 'logid')[offset:offset + limit]
    data = []
    for log in query:
        timestr = log.time.strftime('%Y-%m-%d %H:%M:%S')
        data.append([timestr, log.jobid_id, log.logtext])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


@perm_required('storages.change_volumes')
def makeused(request, name):
    vol = get_object_or_404(Media, volumename=name)
    out = doUpdateVolumeUsed(name)
    if len(out) == 0:
        st = False
    else:
        st = True
        username = request.user.username
        log = Log(jobid_id=0, logtext='User %s closed Volume "%s" marking it as Used.' % (username, name))
        log.save()
    context = {'status': st}
    return JsonResponse(context, safe=False)


@perm_required('storages.change_volumes')
def makeappend(request, name):
    vol = get_object_or_404(Media, volumename=name)
    out = doUpdateVolumeAppend(name)
    if len(out) == 0:
        st = False
    else:
        st = True
        username = request.user.username
        log = Log(jobid_id=0, logtext='User %s opened Volume "%s" marking it as Append.' % (username, name))
        log.save()
    context = {'status': st}
    return JsonResponse(context, safe=False)


@perm_required('storages.recycle_volumes')
def makepurged(request, name):
    vol = get_object_or_404(Media, volumename=name)
    out = doPurgeVolume(name)
    if len(out) == 0:
        st = False
    else:
        st = True
        username = request.user.username
        log = Log(jobid_id=0, logtext='User %s recycled Volume "%s" marking it as Purged.' % (username, name))
        log.save()
    context = {'status': st}
    return JsonResponse(context, safe=False)


@perm_required('storages.delete_volumes')
def makedeletevolume(request, name):
    vol = get_object_or_404(Media, volumename=name)
    out = doDeleteVolume(name)
    if len(out) == 0:
        st = False
    else:
        st = True
        username = request.user.username
        log = Log(jobid_id=0, logtext='User %s deleted Volume "%s" all data on volume was lost.' % (username, name))
        log.save()
    context = {'status': st}
    return JsonResponse(context, safe=False)


"""
*.status storage=sun-dedup-autochanger devices device="DedupStorageDrv6"
Connecting to Storage daemon sun-dedup-autochanger at 192.168.0.31:9103

Device status:

Device dedup data: "DedupStorageDrv6" (/backup/dedupvolumes) is not open.
    Drive 6 is not loaded.
    Available Space=2.019 TB
==
====
"""


@perm_required('storages.comment_volumes')
@transaction.atomic
def comment(request, name):
    volume = get_object_or_404(Media, volumename=name)
    # print ("|", volume.comment, "|")
    if request.method == 'GET':
        # get comment text
        context = {'comment': volume.comment or ''}
        return JsonResponse(context)
    else:
        # save comment
        # print request.POST
        volume.comment = request.POST['commenttext']
        volume.save(update_fields=["comment"])
        return JsonResponse(True, safe=False)


@perm_required('storages.view_storages')
def address(request):
    """ JSON for host address """
    # TODO: move to general address resolve service
    addr = request.GET.get('address', '')
    return JsonResponse(checkAddress(addr), safe=False)


@any_perm_required('storages.add_storages', 'storages.change_storages')
def sdname(request):
    """
        JSON for storage name
        when storage name already exist then return false
    """
    storage = request.GET.get('name', '').encode('ascii', 'ignore')
    check = True
    if ConfResource.objects.filter(compid__type='D', type__name='Storage', name=storage).count() == 1:
        check = False
    return JsonResponse(check, safe=False)


@userissuperuser_required()
def archivedir(request):
    # TODO: Move to libs/storage.py
    archdir = request.GET.get('archivedir')
    if archdir is not None:
        return JsonResponse(checkarchivedir(archdir), safe=False)
    dedupdir = request.GET.get('dedupdir')
    if dedupdir is not None:
        return JsonResponse(checkarchivedir(dedupdir), safe=False)
    dedupidxdir = request.GET.get('dedupidxdir')
    if dedupidxdir is not None:
        return JsonResponse(checkarchivedir(dedupidxdir), safe=False)
    return JsonResponse(False, safe=False)


@userissuperuser_required()
def adddisk(request):
    departments = getUserDepartmentsList(request, default=False)
    st = getStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    if request.method == 'GET':
        form = StorageDiskForm(departments=departments, storages=storages)
        form.fields['address'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Add', 'Disk storage'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'storage/adddisk.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            form = StorageDiskForm(data=request.POST, departments=departments, storages=storages)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                storage = form.cleaned_data['storagelist']
                # address = form.cleaned_data['address']
                archdir = form.cleaned_data['archivedir']
                departs = form.cleaned_data['departments']
                # create a Storage resource
                with transaction.atomic():
                    extendStoragefile(storname=name, descr=descr, sdcomponent=storage, archdir=archdir,
                                      departments=departs)
                directorreload()
                messages.info(request, """You have to <a href="%s">restart the Storage service</a> if you want to 
                              use this storage. You could be unable to run successful jobs without it."""
                              % reverse('daemonindex'), extra_tags="noslide:New Storage added!")
                return redirect('storageinfo', name)
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('storagedefined')


@userissuperuser_required()
def adddedup(request):
    if not storagededupavailable():
        raise Http404()
    departments = getUserDepartmentsList(request, default=False)
    st = getStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    if request.method == 'GET':
        form = StorageDedupForm(storages=storages, departments=departments)
        form.fields['address'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Add', 'Dedup storage'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'storage/adddedup.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            form = StorageDedupForm(data=request.POST, storages=storages, departments=departments)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                storage = form.cleaned_data['storagelist']
                # address = form.cleaned_data['address']
                dedupidxdir = form.cleaned_data['dedupidxdir']
                dedupdir = form.cleaned_data['dedupdir']
                departs = form.cleaned_data['departments']
                # create a Storage resource
                with transaction.atomic():
                    extendStoragededup(storname=name, descr=descr, sdcomponent=storage, dedupidxdir=dedupidxdir,
                                       dedupdir=dedupdir, departments=departs)
                directorreload()
                messages.info(request, """You have to <a href="%s">restart the Storage service</a> if you want to 
                                       use this storage. You could be unable to run successful jobs without it."""
                              % reverse('daemonindex'), extra_tags="noslide:New Storage added!")
                return redirect('storageinfo', name)
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('storagedefined')


@perm_required('storages.add_storages')
def addalias(request):
    departments = getUserDepartmentsList(request)
    st = getDIRStorageNamesnAlias(request)
    storages = ()
    for s in st:
        storages += ((s, s),)
    ip = detectipall()
    ipall = [(a, a) for a in ip]
    if request.method == 'GET':
        form = StorageAliasForm(storages=storages, storageips=ipall, departments=departments)
        form.fields['address'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Add', 'Alias'], 'form': form}
        updateMenuNumbers(request, context)
        return render(request, 'storage/addalias.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            form = StorageAliasForm(data=request.POST, storages=storages, storageips=ipall, departments=departments)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                storage = form.cleaned_data['storagelist']
                storageip = form.cleaned_data['storageip']
                depart = form.cleaned_data['departments']
                # create a Storage resource
                with transaction.atomic():
                    createStorageAlias(request, storname=name, descr=descr, storage=storage, address=storageip,
                                       department=depart)
                directorreload()
                # response['Location'] += '?n=1'
                return redirect('storageinfo', name)
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('storagedefined')


@userissuperuser_required()
def addtape(request):
    departments = getUserDepartmentsList(request, default=False)
    st = getStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    libs = detectlibs()
    tapelibs = ()
    tlavl = False
    stortapeids = getDIRStorageTapeids()
    for l in libs:
        if l['id'] not in stortapeids:
            tapelibs += ((l['id'], l['name'] + l['id']),)
            tlavl = True
    if request.method == 'GET':
        form = StorageTapeForm(storages=storages, tapelibs=tapelibs, departments=departments)
        form.fields['address'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Add', 'Tape storage'], 'form': form,
                   'tlavl': tlavl}
        updateMenuNumbers(request, context)
        messages.info(request, """Here <b>IBAdmin</b> will detect a storage you select. It will require to execute 
            tape load/unload operations which will take some time to complete. You should check the operation 
            progress below.<br>
            By default IBAdmin will automatically <u>initialize</u> all tapes found in library for future use.
            If you want to make this initialization later you have to deselect the checkbox below.""",
                      extra_tags="noslide:Info")
        return render(request, 'storage/addtape.html', context)
    else:
        # print (request.POST)
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            form = StorageTapeForm(data=request.POST, storages=storages, tapelibs=tapelibs, departments=departments)
            if form.is_valid():
                taskid = form.cleaned_data['taskid']
                task = get_object_or_404(Tasks, taskid=taskid)
                if task.status == 'F':
                    storname = form.cleaned_data['name'].encode('ascii', 'ignore')
                    descr = form.cleaned_data['descr']
                    storage = form.cleaned_data['storagelist']
                    # address = form.cleaned_data['address']
                    tapelist = form.cleaned_data['tapelist']
                    libdata = None
                    for l in libs:
                        if l['id'] == tapelist:
                            libdata = l
                    tapelib = {
                        'Lib': libdata,
                        'Devices': ast.literal_eval(task.output)
                    }
                    # create a Storage resource
                    with transaction.atomic():
                        extendStoragetape(storname=storname, descr=descr, sdcomponent=storage, tapelib=tapelib)
                    directorreload()
                    response = redirect('storageinfo', storname)
                    response['Location'] += '?n=1'
                    return response
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('storagedefined')


@userissuperuser_required()
def tapedetectlib(request, tapeid):
    libs = detectlibs()
    tape = tapeid
    stname = 'Unknown'
    for l in libs:
        if l['id'] == tapeid:
            tape = 'tape' + str(tapeid)
            stname = l['name']
            break
    taskid = prepareTask(name="Detecting tape library: " + str(stname) + ' ' + str(tapeid), proc=3, params=tape,
                         log='Starting...')
    # TODO: change into {'taskid': taskid}
    context = [taskid]
    return JsonResponse(context, safe=False)


@userissuperuser_required()
def taperescanlib(request, name, tapeid):
        storageres = getDIRStorageinfo(name=name)
        if storageres is None:
            raise Http404()
        storage = extractstorageparams(storageres)
        devices = getSDDevicesListex(component=storage['StorageComponent'], storage=storage['Device'])
        params = {
            'tapeid': 'tape' + tapeid,
            'storage': storage['Name'],
            'devices': devices,
        }
        taskid = prepareTask(name="Rescan tape library: " + storage['StorageDirDevice'], proc=5, params=params,
                             log='Starting...')
        context = {'taskid': taskid}
        return JsonResponse(context, safe=False)


@userissuperuser_required()
def detectprogress(request, taskid):
        task = get_object_or_404(Tasks, taskid=taskid)
        log = task.log.splitlines()
        if len(log) > 0:
            log = log[-1]
        else:
            log = '...'
        context = [task.progress, str(task.progress) + '%', log, task.status]
        return JsonResponse(context, safe=False)


@perm_required('storages.change_storages')
def edit(request, name):
    backurl = request.GET.get('b', None)
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    alias = storage.get('Alias', None)
    if alias is not None:
        response = redirect('storageeditalias', name)
        if backurl is not None:
            response['Location'] += '?b=' + backurl
        return response
    if userissuperuser(request):
        mediatype = storage.get('MediaType')
        if mediatype.startswith('File'):
            response = redirect('storageeditdisk', name)
            if backurl is not None:
                response['Location'] += '?b=' + backurl
            return response
        if mediatype.startswith('Dedup'):
            response = redirect('storageeditdedup', name)
            if backurl is not None:
                response['Location'] += '?b=' + backurl
            return response
        if mediatype.startswith('Tape'):
            response = redirect('storageedittape', name)
            if backurl is not None:
                response['Location'] += '?b=' + backurl
            return response
    raise Http404()


@userissuperuser_required()
def editdisk(request, name):
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    st = getStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    departments = getUserDepartmentsList(request, default=False)
    if request.method == 'GET':
        data = makeinitialdata(name, storage)
        form = StorageDiskForm(storages=storages, departments=departments, initial=data)
        form.fields['name'].disabled = True
        form.fields['address'].disabled = True
        form.fields['storagelist'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Edit', 'Disk storage'], 'form': form,
                   'storagestatusdisplay': 1, 'Storage': storage}
        updateMenuNumbers(request, context)
        return render(request, 'storage/editdisk.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            post = request.POST.copy()
            post['name'] = name
            post['address'] = storage['Address']
            post['storagelist'] = storage['StorageComponent']
            data = makeinitialdata(name, storage)
            form = StorageDiskForm(data=post, storages=storages, departments=departments, initial=data)
            if form.is_valid():
                descr = form.cleaned_data['descr']
                archdir = form.cleaned_data['archivedir']
                departs = form.cleaned_data['departments']
                if form.has_changed():
                    with transaction.atomic():
                        # print "form valid and changed ... "
                        if 'descr' in form.changed_data:
                            # update description
                            updateDIRStorageDescr(request, name=name, descr=descr)
                        if 'archivedir' in form.changed_data:
                            # update archivedir
                            updateStorageArchdir(request, storname=name, archdir=archdir)
                        if 'departments' in form.changed_data:
                            # update departments
                            updateDIRStorageDepartments(request, name=name, departments=departs)
                    directorreload()
                return redirect('storageinfo', name)
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('storagedefined')


@perm_required('storages.change_storages')
def editalias(request, name):
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    departments = getUserDepartmentsList(request)
    storage = extractstorageparams(storageres)
    st = getDIRStorageNamesnAlias(request)
    storages = ()
    for s in st:
        storages += ((s, s),)
    if len(storages) == 0:
        alias = storage.get('Alias', 'Default storage')
        storages = ((alias, alias),)
    ip = detectipall()
    ipall = [(a, a) for a in ip]
    if request.method == 'GET':
        data = makeinitialaliasdata(name, storage)
        form = StorageAliasForm(storages=storages, storageips=ipall, initial=data, departments=departments)
        form.fields['name'].disabled = True
        form.fields['storagelist'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Edit', 'Alias'], 'form': form,
                   'storagestatusdisplay': 1, 'Storage': storage}
        updateMenuNumbers(request, context)
        return render(request, 'storage/editalias.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            post = request.POST.copy()
            post['name'] = name
            post['storagelist'] = storage['Alias']
            data = makeinitialaliasdata(name, storage)
            form = StorageAliasForm(data=post, storages=storages, storageips=ipall, initial=data,
                                    departments=departments)
            if form.is_valid():
                descr = form.cleaned_data['descr']
                departs = [form.cleaned_data['departments'], ]
                if form.has_changed():
                    with transaction.atomic():
                        # print "form valid and changed ... "
                        if 'descr' in form.changed_data:
                            # update description
                            updateDIRStorageDescr(request, name=name, descr=descr)
                        # if 'storageip' in form.changed_data:
                            # update archivedir
                            # updateStorageAliasAddress(storname=name, address=form.cleaned_data['storageip'])
                        if 'departments' in form.changed_data:
                            # update departments
                            print (departs)
                            updateDIRStorageDepartments(request, name=name, departments=departs)
                    directorreload()
                return redirect('storageinfo', name)
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('storagedefined')


@userissuperuser_required()
def edittape(request, name):
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    departments = getUserDepartmentsList(request, default=False)
    storage = extractstorageparams(storageres)
    storageid = storage.get("StorageDirTapeid")
    if storageid is None:
        return redirect('storagedefined')
    st = getStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    libs = detectlibs()
    tapelibs = ()
    tlavl = False
    if len(libs) > 0:
        tlavl = True
    for l in libs:
        tapelibs += ((l['id'], l['name'] + l['id']),)
    data = makeinitialdata(name, storage)
    data['taskid'] = 0
    data['tapelist'] = storageid
    if request.method == 'GET':
        form = StorageTapeForm(storages=storages, departments=departments, tapelibs=tapelibs, initial=data)
        form.fields['name'].disabled = True
        form.fields['address'].disabled = True
        form.fields['storagelist'].disabled = True
        form.fields['tapelist'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Edit', 'Tape storage'], 'form': form,
                   'Storage': storage, 'tlavl': tlavl, 'StorageId': storageid}
        updateMenuNumbers(request, context)
        return render(request, 'storage/edittape.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            post = request.POST.copy()
            post['name'] = name
            post['address'] = storage['Address']
            post['storagelist'] = storage['StorageComponent']
            post['tapelist'] = storageid
            form = StorageTapeForm(data=post, storages=storages, departments=departments, initial=data,
                                   tapelibs=tapelibs)
            if form.is_valid():
                response = redirect('storageinfo', name)
                descr = form.cleaned_data['descr']
                departs = form.cleaned_data['departments']
                if form.has_changed():
                    with transaction.atomic():
                        # print "form valid and changed ... "
                        if 'descr' in form.changed_data:
                            # update description
                            updateDIRStorageDescr(request, name=name, descr=descr)
                        if 'departments' in form.changed_data:
                            # update departments
                            updateDIRStorageDepartments(request, name=name, departments=departs)
                    if 'taskid' in form.changed_data:
                        # rescan was performed
                        taskid = form.cleaned_data['taskid']
                        tasks = Tasks.objects.filter(taskid=taskid)
                        if len(tasks) != 0:
                            task = tasks[0]
                        else:
                            messages.error(request, "Something goes wrong and I cannot find TaskId: %s" % taskid,
                                           extra_tags="Error")
                            return redirect('storagedefined')
                        if task.status == 'F':
                            libdata = None
                            for l in libs:
                                if l['id'] == storageid:
                                    libdata = l
                            tapelib = {
                                'Lib': libdata,
                                'Devices': ast.literal_eval(task.output)
                            }
                            with transaction.atomic():
                                updateStorageTapelib(storname=name, tapelib=tapelib)
                            response['Location'] += '?n=2'
                    directorreload()
                return response
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('storagedefined')


@userissuperuser_required()
def editdedup(request, name):
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    departments = getUserDepartmentsList(request, default=False)
    storage = extractstorageparams(storageres)
    st = getStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    if request.method == 'GET':
        data = makeinitialdata(name, storage)
        form = StorageDedupForm(storages=storages, departments=departments, initial=data)
        form.fields['name'].disabled = True
        form.fields['address'].disabled = True
        form.fields['storagelist'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Edit', 'Dedup storage'], 'form': form,
                   'storagestatusdisplay': 1, 'Storage': storage}
        updateMenuNumbers(request, context)
        return render(request, 'storage/editdedup.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            post = request.POST.copy()
            post['name'] = name
            post['address'] = storage['Address']
            post['storagelist'] = storage['StorageComponent']
            data = makeinitialdata(name, storage)
            form = StorageDedupForm(data=post, storages=storages, departments=departments, initial=data)
            if form.is_valid():
                descr = form.cleaned_data['descr']
                departs = form.cleaned_data['departments']
                dedupidxdir = form.cleaned_data['dedupidxdir']
                dedupdir = form.cleaned_data['dedupdir']
                if form.has_changed():
                    # print "form valid and changed ... "
                    if 'descr' in form.changed_data:
                        # update description
                        with transaction.atomic():
                            updateDIRStorageDescr(request, name=name, descr=descr)
                    if 'dedupidxdir' in form.changed_data:
                        # update archivedir
                        with transaction.atomic():
                            updateStorageDedupidxdir(storname=name, dedupidxdir=dedupidxdir)
                    if 'dedupdir' in form.changed_data:
                        # update archivedir
                        with transaction.atomic():
                            updateStorageDedupdir(storname=name, dedupdir=dedupdir)
                    if 'departments' in form.changed_data:
                        # update departments
                        updateDIRStorageDepartments(request, name=name, departments=departs)
                    directorreload()
                return redirect('storageinfo', name)
            else:
                messages.error(request, "Cannot validate a form: %s" % form.errors, extra_tags='Error')
    return redirect('storagedefined')


@userissuperuser_required()
def enabledevice(request, storage, device):
    storageres = getDIRStorageinfo(name=storage)
    if storageres is None:
        raise Http404()
    out = enableDevice(storage=storage, device=device)
    if len(out) > 0 and out[0].startswith('3002'):
        return JsonResponse(True, safe=False)
    return JsonResponse(False, safe=False)


@userissuperuser_required()
def disabledevice(request, storage, device):
    storageres = getDIRStorageinfo(name=storage)
    if storageres is None:
        raise Http404()
    out = disableDevice(storage=storage, device=device)
    if len(out) > 0 and out[0].startswith('3002'):
        return JsonResponse(True, safe=False)
    return JsonResponse(False, safe=False)


@userissuperuser_required()
def umountdevice(request, storage, slot, device):
    storageres = getDIRStorageinfo(name=storage)
    if storageres is None:
        raise Http404()
    out = umountDevice(storage=storage, device=device, slot=slot)
    if len(out) > 0 and out[0].startswith('3002'):
        return JsonResponse(True, safe=False)
    return JsonResponse(False, safe=False)


@userissuperuser_required()
def labeltape(request, storage):
    storageres = getDIRStorageinfo(name=storage)
    if storageres is None:
        raise Http404()
    logi = Log(jobid_id=0, logtext='User labeled tapes in "%s"' % storage)
    logi.save()
    taskid = prepareTask(name="Label tapes", proc=4, params=storage, log="Starting...")
    context = {'taskid': taskid}
    return JsonResponse(context, safe=False)
