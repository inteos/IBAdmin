# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from config.models import *
from config.conf import initialize
from config.conflib import getDIRname
from libs.init import *
from tasks.models import Tasks
from django.db import transaction
from libs.system import *
from libs.plat import *
from django.contrib.auth import authenticate, login as auth_login
from libs.tapelib import detectlibs
from libs.task import prepareTask
from .forms import *
import ast
import traceback


def index(request):
    storages = preparestorages()
    form = InitialForm(storages=storages)
    displayalert = False
    dall = False
    subject = None
    message = None

    versionid = 0
    try:
        versionid = Version.objects.get().versionid
    except Exception as err:
        # redisplay initial
        disableall(form)
        dall = True
        displayalert = True
        subject = 'Error during preinitialize.'
        message = """PreInitialize procedure encountered an error: %s Try again later or contact 
        <a href="https://inteos.freshservice.com">Inteos support</a>.""" % (str(err))

    if versionid not in CATVERSUPPORTED:
        disableall(form)
        displayalert = True
        dall = True
        subject = "Wrong catalog version"
        message = """Your catalog version is unsupported by application. You should install a proper 
                   version of the application to use it on your system. You should contact 
                   <a href="https://inteos.freshservice.com/solution/articles/26674">Inteos support</a>
                   <br><b>Catalog: %s vs. supported: %s</b><br>""" % (versionid, CATVERSUPPORTED)
    else:
        isconfigured = getDIRname(request)
        # isconfigured = None
        if isconfigured is not None:
            disableall(form)
            displayalert = 1
            dall = True
            subject = "Your application is already configured"
            message = """Your system name is: <b>%s</b>. You've propably go here by a mistake. <br>Please go into the 
            main page <a href="%s">directly</a>. If it is not a mistake and you want to reinitialize, please recreate 
            your catalog database or contact <a href="https://inteos.freshservice.com/support/solutions/articles/18982">
            Inteos support</a>""" % (isconfigured, reverse('home'))

    context = {
        'form': form,
        'displayalert': displayalert,
        'subject': subject,
        'message': message,
        'disableall': dall,
    }
    return render(request, 'initial/index.html', context)


def taskprogress(request):
    taskid = request.POST.get('taskid')
    # print "TaskId", taskid
    task = get_object_or_404(Tasks, taskid=taskid)
    log = task.log.splitlines()
    if len(log) > 0:
        log = log[-1]
    else:
        log = '...'
    context = [task.progress, str(task.progress) + '%', log, task.status]
    return JsonResponse(context, safe=False)


def libdetect(request):
    isconfigured = getDIRname(request)
    if isconfigured is not None:
        return redirect('initial')
    storages = preparestorages()
    forminitial = InitialForm(data=request.POST, storages=storages)
    if forminitial.is_valid():
        st = forminitial.cleaned_data['storage']
        storagename = 'Library'
        for (s, n) in storages:
            if s == st:
                storagename = n
                break
        taskid = prepareTask(name="Detecting tape library: " + storagename, proc=3, params=st, log='Starting...')
        data = {
            'dirname': forminitial.cleaned_data['dirname'].encode('ascii', 'ignore'),
            'descr': forminitial.cleaned_data['descr'],
            'email': forminitial.cleaned_data['email'],
            'admpass': forminitial.cleaned_data['admpass'],
            'storage': st,
            'taskid': taskid,
            'tapeinit': True,
        }
        form = InitialDetectForm(initial=data)
        context = {
            'form': form,
            'storage': storagename,
        }
        return render(request, 'initial/libdetect.html', context)
    else:
        message = """Cannot parse parameters: %s Try again later or contact 
                <a href="https://inteos.freshservice.com">Inteos support</a>.""" % str(forminitial.errors)
    return render(request, 'initial/index.html', {
        'displayalert': True,
        'subject': 'Error during preinitialize.',
        'form': forminitial,
        'message': message,
    })


def initialsetup(request):
    storages = preparestorages()
    form = InitialForm(data=request.POST, storages=storages)
    if form.is_valid():
        dirname = form.cleaned_data['dirname'].encode('ascii', 'ignore')
        descr = form.cleaned_data['descr']
        email = form.cleaned_data['email']
        admpass = form.cleaned_data['admpass']
        storage = form.cleaned_data['storage']
        archdir = form.cleaned_data['archivedir']
        dedupdir = form.cleaned_data['dedupdir']
        dedupidxdir = form.cleaned_data['dedupidxdir']
        try:
            stopallservices()
            createconfigfiles(dirname)
            address = detectip()
            with transaction.atomic():
                # create config files
                initialize(name=dirname, descr=descr, email=email, password=admpass, stortype=storage, address=address,
                           archdir=archdir, dedupdir=dedupdir, dedupidxdir=dedupidxdir)
                postinitial(request)
            startallservices()
            user = authenticate(username='admin', password=admpass)
            auth_login(request, user)
            return redirect('home')
        except Exception as err:
            # redisplay initial
            message = """Initialize encountered an error: %s Try again later or contact 
            <a href="https://inteos.freshservice.com">Inteos support</a>.""" % str(err)
            traceback.print_exc()
    else:
        message = """Cannot parse parameters: %s Try again later or contact 
        <a href="https://inteos.freshservice.com">Inteos support</a>.""" % str(form.errors)
    return render(request, 'initial/index.html', {
        'displayalert': True,
        'subject': 'Error during initialize.',
        'form': form,
        'message': message,
    })


def initialsetup2(request):
    form = InitialDetectForm(data=request.POST)
    if form.is_valid():
        taskid = form.cleaned_data['taskid']
        task = get_object_or_404(Tasks, taskid=taskid)
        if task.status == 'F':
            dirname = form.cleaned_data['dirname'].encode('ascii', 'ignore')
            descr = form.cleaned_data['descr']
            email = form.cleaned_data['email']
            admpass = form.cleaned_data['admpass']
            storage = form.cleaned_data['storage'].replace('tape', '')
            tapeinit = form.cleaned_data['tapeinit']
            libs = detectlibs()
            libdata = None
            for l in libs:
                if l['id'] == storage:
                    libdata = l
            tapelib = {
                'Lib': libdata,
                'Devices': ast.literal_eval(task.output)
            }
            try:
                stopallservices()
                createconfigfiles(dirname)
                address = detectip()
                with transaction.atomic():
                    # create config files
                    initialize(name=dirname, descr=descr, email=email, password=admpass, stortype='tape',
                               address=address, tapelib=tapelib)
                    postinitial(request)
                startallservices()
                if tapeinit:
                    prepareTask(name="Initializing tape library", proc=4, params='tape', log='Starting...')
                user = authenticate(username='admin', password=admpass)
                auth_login(request, user)
                return redirect('home')
            except Exception as err:
                # redisplay initial
                message = """Initialize encountered an error: %s Try again later or contact 
                    <a href="https://inteos.freshservice.com">Inteos support</a>.""" % str(err)
                traceback.print_exc()
        else:
            log = task.log.replace('\n', '<br>')
            message = """Error encountered during library detection:<hr>%s<hr>
            Try again later or contact <a href="https://inteos.freshservice.com">Inteos support</a>.""" % log
    else:
        message = """Cannot parse parameters: %s Try again later or contact 
            <a href="https://inteos.freshservice.com">Inteos support</a>.""" % str(form.errors)
    storages = preparestorages()
    form = InitialForm(storages=storages)
    return render(request, 'initial/index.html', {
        'displayalert': True,
        'subject': 'Error during initialize.',
        'form': form,
        'message': message,
    })


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
