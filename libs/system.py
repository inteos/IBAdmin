# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import print_function
from subprocess import Popen, PIPE
from socket import gethostbyname
from .plat import *
import os.path
import re
import glob


def checkservice(name=None):
    if name is None:
        return 0
    run = 0
    systemctl = Popen([SYSTEMCTL, 'is-active', name], stdout=PIPE)
    status = systemctl.stdout.read().rstrip()
    if 'active' == status:
        run = 1
    return run


def checkAddress(value):
    try:
        host = gethostbyname(value)
    except:
        return False
    return True


def detectip():
    # exec ip command to get valuable data
    out = Popen(NETIPCMD + " addr show", shell=True, stdout=PIPE).stdout.read()
    lines = out.splitlines()
    insection = False
    for data in lines:
        if re.match(r'^.*: ', data):
            # we are in section, check if it is not lo:
            if ' lo: ' not in data:
                insection = True
                continue
        if insection and 'inet ' in data:
            [inet, a] = data.split('/', 1)
            inet = inet.lstrip()
            return inet.replace('inet ', '', 1)


def detectipall():
    # exec ip command to get valuable data
    out = Popen(NETIPCMD + " addr show", shell=True, stdout=PIPE).stdout.read()
    lines = out.splitlines()
    insection = False
    ipall = []
    for data in lines:
        if re.match(r'^.*: ', data):
            # we are in section, check if it is not lo:
            if ' lo: ' not in data:
                insection = True
                continue
        if insection and 'inet ' in data:
            [inet, a] = data.split('/', 1)
            inet = inet.lstrip()
            ipall.append(inet.replace('inet ', '', 1))
            insection = False
    return ipall


def detectdedup():
    ded = os.path.isfile('/opt/bacula/plugins/dedup-sd.so')
    if ded is True:
        return True
    plugs = glob.glob('/opt/bacula/plugins/bacula-sd-dedup-driver-*.*.*.so')
    if len(plugs) > 0:
        return True
    else:
        return False


def detectvsphere():
    ded = os.path.isfile('/opt/bacula/plugins/vsphere-fd.so')
    if ded is True:
        return True
    else:
        return False


def checkarchivedir(archivedir):
    return os.path.isdir(archivedir)


def checkbaculadocsdir():
    return os.path.isdir("/opt/bacula/docs/html/")


def updateservicestatus(context):
    dirstatus = checkservice(name='bacula-dir')
    sdstatus = checkservice(name='bacula-sd')
    fdstatus = checkservice(name='bacula-fd')
    ibadstatus = checkservice(name='ibadstatd')
    context.update({
        'DIRStatus': dirstatus,
        'SDStatus': sdstatus,
        'FDStatus': fdstatus,
        'IBADStatus': ibadstatus,
    })


def getsystemdlog(name=None):
    if name is None:
        return ''
    out = Popen(JOURNALCTL + name, shell=True, stdout=PIPE).stdout.read()
    lines = out.splitlines()
    return lines


def gettapedrvlist():
    tapedrvlist = []
    out = Popen(LSSCSICMD, shell=True, stdout=PIPE).stdout.read()
    lines = out.splitlines()
    pattern = re.compile(r'^(\[\d+:\d+:\d+:\d+\])\s+(\S+)\s+(\S+)\s+(.{16})\s(.{5})\s(\S+)\s+(\S+)')
    for data in lines:
        m = pattern.search(data)
        saddr = m.group(1)
        stype = m.group(2)
        vendor = m.group(3)
        model = m.group(4)
        dev = m.group(6).replace('st', 'nst')
        if stype == 'tape':
            tapename = vendor + ' ' + model + ' ' + saddr
            tapedrvlist.append({
                'name': tapename,
                'dev': dev,
                'id': saddr,
            })
    return tapedrvlist


def getdevsymlink(name=None):
    if name is None:
        return None
    if os.path.exists(name):
        # udevadm info --query=symlink --name=/dev/nst0
        out = Popen(UDEVADMCMD + ' info --query=symlink --name=' + name, shell=True, stdout=PIPE).stdout.read()
        lines = out.splitlines()
        if len(lines) > 0:
            return '/dev/' + lines[0]
    return None
