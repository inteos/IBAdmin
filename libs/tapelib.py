# -*- coding: UTF-8 -*-
from __future__ import print_function
from .system import *
import time
import os.path
import re


def detectlibs():
    tapeliblist = []
    out = Popen(LSSCSICMD, shell=True, stdout=PIPE).stdout.read()
    lines = out.splitlines()
    pattern = re.compile(r'^(\[\d+:\d+:\d+:\d+\])\s+(\S+)\s+(\S+)\s+(.{16})\s(.{5})\s(\S+)\s+(\S+)')
    for data in lines:
        m = pattern.search(data)
        saddr = m.group(1)
        stype = m.group(2)
        vendor = m.group(3)
        model = m.group(4)
        generic = m.group(7)
        if stype == 'mediumx':
            libname = vendor + ' ' + model
            tapeliblist.append({
                'name': libname,
                'dev': generic,
                'id': saddr,
            })
    return tapeliblist


def mt_status(dev=None):
    time.sleep(1)
    lines = []
    status = {
        'status': None,
        'lines': lines,
        'log': 'Unexecuted',
    }
    if dev is None:
        return status
    if os.path.exists(dev):
        if os.access(dev, os.W_OK):
            out = Popen(MTCMD + ' -f ' + dev + ' status', shell=True, stdout=PIPE).stdout.read()
            lines = out.splitlines()
            for data in lines:
                if 'ONLINE' in data:
                    status['status'] = True
                    status['lines'] = lines
                    status['log'] = ''
                    return status
            status['status'] = False
            status['log'] = ''
        else:
            status['log'] = "Permission denied: %s\n" % str(dev)
    else:
        status['log'] = "Dev %s not exist\n" % str(dev)
    return status


def mtx_statusinfo(dev=None):
    time.sleep(1)
    if dev is None:
        return None
    libraryinfo = {
        'Info': {},
        'Drives': [],
        'Slots': [],
        'ImportExport': [],
    }
    if os.path.exists(dev):
        out = Popen(MTXCMD + ' -f ' + dev + ' status', shell=True, stdout=PIPE).stdout.read()
        lines = out.splitlines()
        pattern1 = re.compile(r'Storage Changer \S+:(\d+) Drives, (\d+) Slots \( (\d+) Import/Export \)')
        pattern2 = re.compile(r'Data Transfer Element (\d+)')
        pattern3 = re.compile(r'Storage Element (\d+)')
        for data in lines:
            m = pattern1.search(data)
            if m is not None:
                drvs = int(m.group(1))
                impexp = int(m.group(3))
                slots = int(m.group(2)) - impexp
                libraryinfo['Info'] = {
                    'Drives': drvs,
                    'Slots': slots,
                    'ImportExport': impexp,
                }
                continue
            if 'Data Transfer Element' in data:
                d = data.split(':')
                m = pattern2.search(d[0])
                drvindx = int(m.group(1))
                loaded = None
                if 'Full' in d[1]:
                    loaded = {
                        'Volume': d[2].replace(' ', '').replace('VolumeTag=', ''),
                        'Slot': int(d[1].split()[3]),
                    }
                libraryinfo['Drives'].append({
                    'DriveIndex': drvindx,
                    'Loaded': loaded,
                })
                continue
            if 'IMPORT/EXPORT' in data:
                x = data.split('IMPORT/EXPORT:')
                m = pattern3.search(x[0])
                indx = int(m.group(1))
                loaded = None
                if 'Full' in x[1]:
                    loaded = x[1].replace(' ', '').replace('Full:VolumeTag=', '')
                libraryinfo['ImportExport'].append({
                    'Index': indx,
                    'Loaded': loaded,
                })
                continue
            if 'Storage Element' in data:
                s = data.split(':')
                m = pattern3.search(s[0])
                slot = int(m.group(1))
                loaded = None
                if 'Full' in s[1]:
                    loaded = s[2].replace(' ', '').replace('VolumeTag=', '')
                libraryinfo['Slots'].append({
                    'Slot': slot,
                    'Loaded': loaded,
                })
                continue
    return libraryinfo


def mtx_load(dev=None, drive=None, slot=0, volume=None):
    time.sleep(1)
    if dev is not None and drive is not None and (slot != 0 or volume is not None):
        if os.path.exists(dev):
            if volume is not None:
                lib = mtx_statusinfo(dev)
                for s in lib['Slots']:
                    vol = s['Loaded']
                    if vol is not None and vol == volume:
                        slot = s['Slot']
                        break
            # print (dev, slot, drive)
            out = Popen(MTXCMD + ' -f ' + dev + ' load ' + str(slot) + ' ' + str(drive), shell=True,
                        stdout=PIPE).stdout.read()
            lines = out.splitlines()
            for data in lines:
                if 'done' in data:
                    return True
    return False


def mtx_unload(dev=None, drive=None):
    time.sleep(1)
    if dev is not None and drive is not None:
        if os.path.exists(dev):
            lib = mtx_statusinfo(dev)
            slot = 0
            for drv in lib['Drives']:
                if drv['DriveIndex'] == drive:
                    vol = drv['Loaded']
                    if vol is not None:
                        slot = vol['Slot']
                        break
            if slot != 0:
                out = Popen(MTXCMD + ' -f ' + dev + ' unload ' + str(slot) + ' ' + str(drive), shell=True,
                            stdout=PIPE).stdout.read()
                lines = out.splitlines()
                for data in lines:
                    if 'done' in data:
                        return True
    return False


def mtx_unloadall(dev=None):
    if dev is None:
        return None
    if os.path.exists(dev):
        lib = mtx_statusinfo(dev)
        for drv in lib['Drives']:
            if drv['Loaded'] is not None:
                drvindx = drv['DriveIndex']
                mtx_unload(dev=dev, drive=drvindx)
