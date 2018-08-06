# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.db.models import Q
from django.db import transaction
from libs.menu import updateMenuNumbers
from libs.storage import *
from libs.system import *
from libs.bconsole import *
from libs.task import prepareTask
from libs.tapelib import detectlibs
from config.conf import *
from config.confinfo import *
from .models import *
from .forms import *
from jobs.models import Job, Log
from tasks.models import Tasks
from datetime import datetime, timedelta
import ast


def defined(request):
    """ Defined Storages table - list """
    storagelist = getDIRStorageList()
    storagedefined = []
    for storage in storagelist:
        storageparams = extractstorageparams(storage)
        storagedefined.append(storageparams)
    context = {'contentheader': 'Storage', 'contentheadersmall': 'currently defined',
               'apppath': ['Storage', 'Defined'], 'StorageDefined': storagedefined}
    updateMenuNumbers(context)
    return render(request, 'storage/defined.html', context)


def info(request, name):
    """ Storage info and status """
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    storagealert = request.GET.get('n')
    storagealertheader = "Restart required!"
    try:
        if int(storagealert) == 1:
            # new storage added
            storagealertheader = "New Storage added!"
        if int(storagealert) == 2:
            # new storage added
            storagealertheader = "Storage hardware configuration changed!"
    except:
        storagealert = None
    context = {'contentheader': 'Storage', 'apppath': ['Storage', 'Info', name], 'Storage': storage,
               'storagealert': storagealert, 'storagealertheader': storagealertheader, 'storagestatusdisplay': 1}
    updateMenuNumbers(context)
    return render(request, 'storage/storage.html', context)


def historydata(request, name):
    """ wywołanie ajax dla datatables podający zadania uruchomione dla danego storage """
    cols = ['jobid', 'name', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', 'jobstatus', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    jobidlist = Jobmedia.objects.filter(mediaid__storageid__name=name).distinct('jobid').values('jobid')
    total = jobidlist.count()
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        filtered = Job.objects.filter(Q(jobid__in=jobidlist), f).count()
        query = Job.objects.filter(Q(jobid__in=jobidlist), f).order_by(orderstr, '-jobid')[offset:offset + limit]
    else:
        filtered = total
        query = Job.objects.filter(jobid__in=jobidlist).all().order_by(
            orderstr, '-jobid')[offset:offset + limit]
    data = []
    for j in query:
        if j.starttime is None:
            sstr = None
        else:
            sstr = j.starttime.strftime('%Y-%m-%d %H:%M:%S')
        if j.endtime is None:
            estr = None
        else:
            estr = j.endtime.strftime('%Y-%m-%d %H:%M:%S')
        data.append([j.jobid, j.name, [sstr, j.schedtime.strftime('%Y-%m-%d %H:%M:%S')], estr,
                    [j.level, j.type], j.jobfiles, j.jobbytes, [j.jobstatus, j.joberrors], [j.jobid, j.name, j.type, j.jobstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


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
    updateMenuNumbers(context)
    return render(request, 'storage/status.html', context)


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
                    print (job, dev)
                    params['Status'] = 'Running'
                    break
            status.append(params)
        context = {'Devices': status}
    return render(request, 'storage/statusdevices.html', context)


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
    updateMenuNumbers(context)
    return render(request, 'storage/dedup.html', context)


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


def volumes(request):
    context = {'contentheader': 'Volumes list', 'apppath': ['Storage', 'Volumes']}
    updateMenuNumbers(context)
    return render(request, 'storage/volumes.html', context)


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
        f = Q(volumename__icontains=search) | Q(mediatype__icontains=search) | Q(poolid__name__icontains=search) | Q(poolid__name__icontains=search.replace(' ','-')) | Q(volstatus__icontains=search)
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


def volinfo(request, name):
    volume = get_object_or_404(Media.objects.select_related('poolid'), volumename=name)
    if volume.lastwritten is None:
        expired = '-'
    else:
        expired = volume.lastwritten + timedelta(seconds=volume.volretention)
    context = {'contentheader': 'Volume Info', 'apppath': ['Storage', 'Volume', 'Info', name], 'Volume': volume,
                'Volexpired': expired, 'volumestatusdisplay': 1}
    updateMenuNumbers(context)
    return render(request, 'storage/volinfo.html', context)


def volhistorydata(request, name):
    jm = Jobmedia.objects.filter(mediaid__volumename=name).distinct('jobid')
    jobmedia = [d.jobid_id for d in list(jm)]
    cols = ['jobid', 'name', 'starttime', 'endtime', 'level', 'jobfiles', 'jobbytes', 'jobstatus', '']
    draw = request.GET['draw']
    offset = int(request.GET['start'])
    limit = int(request.GET['length'])
    order_col = cols[int(request.GET['order[0][column]'])]
    order_dir = '-' if 'desc' == request.GET['order[0][dir]'] else ''
    search = request.GET['search[value]']
    total = len(jobmedia)
    orderstr = order_dir + order_col
    if search != '':
        f = Q(jobid__contains=search) | Q(name__icontains=search) | Q(clientid__name__icontains=search)
        filtered = Job.objects.filter(Q(jobid__in=jobmedia), f).count()
        query = Job.objects.filter(Q(jobid__in=jobmedia), f).order_by(orderstr, '-jobid')[offset:offset + limit]
    else:
        filtered = total
        query = Job.objects.filter(jobid__in=jobmedia).order_by(orderstr, '-jobid')[offset:offset + limit]
    data = []

    for job in query:
        if job.starttime is None:
            sstr = None
        else:
            sstr = job.starttime.strftime('%Y-%m-%d %H:%M:%S')
        if job.endtime is None:
            estr = None
        else:
            estr = job.endtime.strftime('%Y-%m-%d %H:%M:%S')
        data.append([job.jobid, job.name, [sstr, job.schedtime.strftime('%Y-%m-%d %H:%M:%S')], estr,
                     [job.level, job.type], job.jobfiles, job.jobbytes, [job.jobstatus, job.joberrors],
                     [job.jobid, job.name, job.type, job.jobstatus]])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


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
        query = Log.objects.filter(Q(logtext__contains='Volume "' + name + '"'), f).order_by(orderstr, 'logid')[offset:offset + limit]
    else:
        filtered = total
        query = Log.objects.filter(logtext__contains='Volume "' + name + '"').order_by(orderstr, 'logid')[offset:offset + limit]
    data = []
    for log in query:
        timestr = log.time.strftime('%Y-%m-%d %H:%M:%S')
        data.append([timestr, log.jobid_id, log.logtext])
    context = {'draw': draw, 'recordsTotal': total, 'recordsFiltered': filtered, 'data': data}
    return JsonResponse(context)


def makeused(request, name):
    vol = get_object_or_404(Media, volumename=name)
    out = doUpdateVolumeUsed(name)
    if len(out) == 0:
        st = False
    else:
        st = True
        log = Log(jobid_id=0, logtext='User closed Volume "' + name + '" marking it as Used.')
        log.save()
    context = {'status': st}
    return JsonResponse(context, safe=False)


def makeappend(request, name):
    vol = get_object_or_404(Media, volumename=name)
    out = doUpdateVolumeAppend(name)
    if len(out) == 0:
        st = False
    else:
        st = True
        log = Log(jobid_id=0, logtext='User opened Volume "' + name + '" marking it as Append.')
        log.save()
    context = {'status': st}
    return JsonResponse(context, safe=False)


def makepurged(request, name):
    vol = get_object_or_404(Media, volumename=name)
    out = doPurgeVolume(name)
    if len(out) == 0:
        st = False
    else:
        st = True
        log = Log(jobid_id=0, logtext='User recycled Volume "' + name + '" marking it as Purged.')
        log.save()
    context = {'status': st}
    return JsonResponse(context, safe=False)


def makedeletevolume(request, name):
    vol = get_object_or_404(Media, volumename=name)
    out = doDeleteVolume(name)
    if len(out) == 0:
        st = False
    else:
        st = True
        log = Log(jobid_id=0, logtext='User deleted Volume "' + name + '" all data on volume was lost.')
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


def address(request):
    """ JSON for host address """
    addr = request.GET.get('address', '')
    return JsonResponse(checkAddress(addr), safe=False)


def name(request):
    """
        JSON for storage name
        when storage name already exist then return false
    """
    storage = request.GET.get('name', '').encode('ascii', 'ignore')
    check = True
    if ConfResource.objects.filter(compid__type='D', type__name='Storage', name=storage).count() == 1:
        check = False
    return JsonResponse(check, safe=False)


# TODO: Move to libs/storage.py
def archivedir(request):
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


def adddisk(request):
    st = getStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    if request.method == 'GET':
        form = StorageDiskForm(storages=storages)
        form.fields['address'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Add', 'Disk storage'], 'form': form}
        updateMenuNumbers(context)
        return render(request, 'storage/adddisk.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            form = StorageDiskForm(data=request.POST, storages=storages)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                storage = form.cleaned_data['storagelist']
                # address = form.cleaned_data['address']
                archdir = form.cleaned_data['archivedir']
                # create a Storage resource
                #   TODO: and a Storage component and all required resources
                with transaction.atomic():
                    extendStoragefile(storname=name, descr=descr, sdcomponent=storage, archdir=archdir)
                directorreload()
                response = redirect('storageinfo', name)
                response['Location'] += '?n=1'
                return response
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('storagedefined')


def adddedup(request):
    if not storagededupavailable():
        raise Http404()
    st = getStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    if request.method == 'GET':
        form = StorageDedupForm(storages=storages)
        form.fields['address'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Add', 'Dedup storage'], 'form': form}
        updateMenuNumbers(context)
        return render(request, 'storage/adddedup.html', context)
    else:
        # print request.POST
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            form = StorageDedupForm(data=request.POST, storages=storages)
            if form.is_valid():
                name = form.cleaned_data['name'].encode('ascii', 'ignore')
                descr = form.cleaned_data['descr']
                storage = form.cleaned_data['storagelist']
                # address = form.cleaned_data['address']
                dedupidxdir = form.cleaned_data['dedupidxdir']
                dedupdir = form.cleaned_data['dedupdir']
                # create a Storage resource
                #   TODO: and a Storage component and all required resources
                with transaction.atomic():
                    extendStoragededup(storname=name, descr=descr, sdcomponent=storage, dedupidxdir=dedupidxdir,
                                       dedupdir=dedupdir)
                directorreload()
                response = redirect('storageinfo', name)
                response['Location'] += '?n=1'
                return response
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('storagedefined')


def addtape(request):
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
    if request.method == 'GET':
        form = StorageTapeForm(storages=storages, tapelibs=tapelibs)
        form.fields['address'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Add', 'Tape storage'], 'form': form,
                   'tlavl': tlavl}
        updateMenuNumbers(context)
        return render(request, 'storage/addtape.html', context)
    else:
        # print (request.POST)
        cancel = request.POST.get('cancel', 0)
        if not cancel:
            form = StorageTapeForm(data=request.POST, storages=storages, tapelibs=tapelibs)
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
                    #   TODO: and a Storage component and all required resources
                    with transaction.atomic():
                        extendStoragetape(storname=storname, descr=descr, sdcomponent=storage, tapelib=tapelib)
                    directorreload()
                    response = redirect('storageinfo', storname)
                    response['Location'] += '?n=1'
                    return response
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('storagedefined')


def tapedetectlib(request, id):
    libs = detectlibs()
    tape = id
    stname = 'Unknown'
    for l in libs:
        if l['id'] == id:
            tape = 'tape' + str(id)
            stname = l['name']
            break
    taskid = prepareTask(name="Detecting tape library: " + str(stname) + ' ' + str(id), proc=3, params=tape,
                         log='Starting...')
    # TODO: change into {'taskid': taskid}
    context = [taskid]
    return JsonResponse(context, safe=False)


def taperescanlib(request, name, id):
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    devices = getSDDevicesList(component=storage['StorageComponent'], storage=storage['Device'])
    print storage
    print devices
    params = {
        'tapeid': 'tape' + id,
        'storage': storage['Name'],
        'devices': devices,
    }
    taskid = prepareTask(name="Rescan tape library: " + storage['StorageDirDevice'], proc=5, params=params,
                         log='Starting...')
    context = {'taskid': taskid}
    print params
    return JsonResponse(context, safe=False)


def detectprogress(request, taskid):
    task = get_object_or_404(Tasks, taskid=taskid)
    log = task.log.splitlines()
    if len(log) > 0:
        log = log[-1]
    else:
        log = '...'
    context = [task.progress, str(task.progress) + '%', log, task.status]
    return JsonResponse(context, safe=False)


def makeinitialdata(name, storage):
    data = {
        'name': name,
        'descr': storage['Descr'],
        'address': storage['Address'],
        'storagelist': storage['StorageComponent'],
        'archivedir': storage.get('StorageDirDevice', 'unknown'),
        'dedupidxdir': storage.get('StorageDirDedupidx', 'unknown'),
        'dedupdir': storage.get('StorageDirDevice', 'unknown'),
    }
    return data


def edit(request, name):
    backurl = request.GET.get('b', None)
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    #if storage.get('InternalStorage'):
    #    raise Http404()
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


def editdisk(request, name):
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    #if storage.get('InternalStorage'):
    #    return redirect('storagedefined')
    st = getStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    if request.method == 'GET':
        data = makeinitialdata(name, storage)
        form = StorageDiskForm(storages=storages, initial=data)
        form.fields['name'].disabled = True
        form.fields['address'].disabled = True
        form.fields['storagelist'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Edit', 'Disk storage'], 'form': form,
                   'storagestatusdisplay': 1, 'Storage': storage}
        updateMenuNumbers(context)
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
            form = StorageDiskForm(data=post, storages=storages, initial=data)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... "
                    if 'descr' in form.changed_data:
                        # update description
                        with transaction.atomic():
                            updateDIRStorageDescr(name=name, descr=form.cleaned_data['descr'])
                    if 'archivedir' in form.changed_data:
                        # update archivedir
                        with transaction.atomic():
                            updateStorageArchdir(storname=name, archdir=form.cleaned_data['archivedir'])
                    directorreload()
                return redirect('storageinfo', name)
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('storagedefined')


def edittape(request, name):
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    # if storage.get('InternalStorage'):
    #    return redirect('storagedefined')
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
        form = StorageTapeForm(storages=storages, tapelibs=tapelibs, initial=data)
        form.fields['name'].disabled = True
        form.fields['address'].disabled = True
        form.fields['storagelist'].disabled = True
        form.fields['tapelist'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Edit', 'Tape storage'], 'form': form,
                   'Storage': storage, 'tlavl': tlavl, 'StorageId': storageid}
        updateMenuNumbers(context)
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
            form = StorageTapeForm(data=post, storages=storages, initial=data, tapelibs=tapelibs)
            if form.is_valid():
                print form.changed_data
                response = redirect('storageinfo', name)
                if form.has_changed():
                    # print "form valid and changed ... "
                    if 'descr' in form.changed_data:
                        # update description
                        with transaction.atomic():
                            updateDIRStorageDescr(name=name, descr=form.cleaned_data['descr'])
                    if 'taskid' in form.changed_data:
                        # rescan was performed
                        taskid = form.cleaned_data['taskid']
                        task = get_object_or_404(Tasks, taskid=taskid)
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
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('storagedefined')


def editdedup(request, name):
    storageres = getDIRStorageinfo(name=name)
    if storageres is None:
        raise Http404()
    storage = extractstorageparams(storageres)
    #if storage.get('InternalStorage'):
    #    return redirect('storagedefined')
    st = getStorageNames()
    storages = ()
    for s in st:
        storages += ((s, s),)
    if request.method == 'GET':
        data = makeinitialdata(name, storage)
        form = StorageDedupForm(storages=storages, initial=data)
        form.fields['name'].disabled = True
        form.fields['address'].disabled = True
        form.fields['storagelist'].disabled = True
        context = {'contentheader': 'Storages', 'apppath': ['Storage', 'Edit', 'Dedup storage'], 'form': form,
                   'storagestatusdisplay': 1, 'Storage': storage}
        updateMenuNumbers(context)
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
            form = StorageDedupForm(data=post, storages=storages, initial=data)
            if form.is_valid():
                if form.has_changed():
                    # print "form valid and changed ... "
                    if 'descr' in form.changed_data:
                        # update description
                        with transaction.atomic():
                            updateDIRStorageDescr(name=name, descr=form.cleaned_data['descr'])
                    if 'dedupidxdir' in form.changed_data:
                        # update archivedir
                        with transaction.atomic():
                            updateStorageDedupidxdir(storname=name, dedupidxdir=form.cleaned_data['dedupidxdir'])
                    if 'dedupdir' in form.changed_data:
                        # update archivedir
                        with transaction.atomic():
                            updateStorageDedupdir(storname=name, dedupdir=form.cleaned_data['dedupdir'])
                    directorreload()
                return redirect('storageinfo', name)
            else:
                # TODO zrobić obsługę błędów, albo i nie
                print form.is_valid()
                print form.errors.as_data()
    return redirect('storagedefined')


def enabledevice(request, storage, device):
    storageres = getDIRStorageinfo(name=storage)
    if storageres is None:
        raise Http404()
    out = enableDevice(storage=storage, device=device)
    if len(out) > 0 and out[0].startswith('3002'):
        return JsonResponse(True, safe=False)
    return JsonResponse(False, safe=False)


def disabledevice(request, storage, device):
    storageres = getDIRStorageinfo(name=storage)
    if storageres is None:
        raise Http404()
    out = disableDevice(storage=storage, device=device)
    if len(out) > 0 and out[0].startswith('3002'):
        return JsonResponse(True, safe=False)
    return JsonResponse(False, safe=False)


def umountdevice(request, storage, slot, device):
    storageres = getDIRStorageinfo(name=storage)
    if storageres is None:
        raise Http404()
    out = umountDevice(storage=storage, device=device, slot=slot)
    if len(out) > 0 and out[0].startswith('3002'):
        return JsonResponse(True, safe=False)
    return JsonResponse(False, safe=False)


def labeltape(request, storage):
    storageres = getDIRStorageinfo(name=storage)
    if storageres is None:
        raise Http404()
    logi = Log(jobid_id=0, logtext='User labeled tapes in "' + storage + '"')
    logi.save()
    taskid = prepareTask(name="Label tapes", proc=4, params=storage, log="Starting...")
    context = {'taskid': taskid}
    return JsonResponse(context, safe=False)
