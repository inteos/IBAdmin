# -*- coding: UTF-8 -*-
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from config.models import *
from config.conf import initialize
from config.confinfo import getDIRname
from subprocess import call
from django.db import transaction
from libs.system import *
from libs.plat import *


def index(request):
    try:
        versionid = Version.objects.get().versionid
    except Exception as err:
        # redisplay initial
        return render(request, 'initial/index.html', {
            'displayalert': 1, 'subject': 'Error during preinitialize.',
            'message': 'PreInitialize encountered an error: ' + str(err) +
                       '. Try again later or contact <a href="https://inteos.freshservice.com">Inteos support</a>.',
        })
    if versionid not in CATVERSUPPORTED:
        context = {'displayalert': 1,
                   'subject': "Wrong catalog version",
                   'message': """Your catalog version is unsupported by application. You should install a proper 
                   version of the application to use it on your system. You should contact 
                   <a href="https://inteos.freshservice.com/solution/articles/26674">Inteos support</a>
                   <br><b>Catalog: %s vs. supported: %s</b><br>""" % (versionid, CATVERSUPPORTED),
                   'disableall': 1}
    else:
        isconfigured = getDIRname()
        # isconfigured = None
        if isconfigured is None:
            dedup = detectdedup()
            storage = detectlib()
            context = {'enablededup': dedup, 'Storage': storage}
        else:
            context = {'displayalert': 1,
                       'subject': "Your application is already configured",
                       'message': """Your system name is: <b>%s</b>. You've propably go here by a mistake.<br>
                       Please go into the main page <a href="%s">directly</a>. If it is not a mistake and you want to 
                       reinitialize, please recreate your catalog database or contact
                       <a href="https://inteos.freshservice.com/support/solutions/articles/18982">Inteos support</a>"""
                       % (isconfigured, reverse('home')),
                       'disableall': 1}
    return render(request, 'initial/index.html', context)


def initalize(request):
    dirname = request.POST.get('dirname')
    descr = request.POST.get('descr')
    email = request.POST.get('email')
    admpass = request.POST.get('admpass')
    storage = request.POST.get('storage')
    archdir = request.POST.get('archivedir')
    dedupdir = request.POST.get('dedupdir')
    dedupidxdir = request.POST.get('dedupidxdir')
    try:
        # stop all services
        call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-dir'])
        call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-sd'])
        call([SUDOCMD, SYSTEMCTL, 'stop', 'bacula-fd'])
        call([SUDOCMD, SYSTEMCTL, 'stop', 'ibadstatd'])
        # create config files
        with open('/opt/bacula/etc/bacula-dir.conf', 'w') as f:
            f.write('@|"/opt/ibadmin/utils/ibadconf.py -d"\n')
            f.close()
        with open('/opt/bacula/etc/bacula-sd.conf', 'w') as f:
            f.write('@|"/opt/ibadmin/utils/ibadconf.py -s ' + dirname + '"\n')
            f.close()
        with open('/opt/bacula/etc/bacula-fd.conf', 'w') as f:
            f.write('@|"/opt/ibadmin/utils/ibadconf.py -f ' + dirname + '"\n')
            f.close()
        with open('/opt/bacula/etc/bconsole.conf', 'w') as f:
            f.write('@|"/opt/ibadmin/utils/ibadconf.py -c"\n')
            f.close()
        address = detectip()
        with transaction.atomic():
            # create config files
            initialize(name=dirname, descr=descr, email=email, password=admpass, stortype=storage, address=address,
                       archdir=archdir, dedupdir=dedupdir, dedupidxdir=dedupidxdir)
        # start all services
        call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-dir'])
        call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-sd'])
        call([SUDOCMD, SYSTEMCTL, 'start', 'bacula-fd'])
        call([SUDOCMD, SYSTEMCTL, 'start', 'ibadstatd'])
        return redirect('home')
    except Exception as err:
        # redisplay initial
        return render(request, 'initial/index.html', {
            'displayalert': 1, 'subject': 'Error during initialize.',
            'message': 'Initialize encountered an error: ' + str(err) +
                       '. Try again later or contact <a href="https://inteos.freshservice.com">Inteos support</a>.',
        })


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
