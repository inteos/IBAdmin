# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import print_function
import time
import os
import psycopg2
import psycopg2.extras
import lib


PARAMS = {}
PREV = {}
DISKS = []
NAMES = {}


def setparam(cur, param, types, descr, unit, chart, display, color, box):
    parid = lib.getsetparam(cur, param, types, descr, unit, chart, display, color, box)
    PARAMS[param] = parid
    lib.setstat(cur, parid)


SYSDIR = "/sys/class/block"


def diskstat(device, fg=0):
    try:
        stat = open(SYSDIR + '/' + device + '/stat')
    except IOError:
        return 0
    ready = 1
    iops = 0
    readps = 0
    writeps = 0
    for line in stat:
        disk = line.split()
        if fg > 1:
            print (device, disk)
        # rioreq + wioreq
        ioreq = int(disk[0]) + int(disk[4])
        # reads bytes
        reads = int(disk[2]) * 512
        # writes bytes
        writes = int(disk[6]) * 512
        # time
        curtime = time.time()
        if PREV.get(device).get('time'):
            diff_time = curtime - PREV.get(device).get('time', 0)
            if diff_time == 0:
                return 0
            diff_ioreq = ioreq - PREV.get(device).get('ioreq', 0)
            diff_reads = reads - PREV.get(device).get('reads', 0)
            diff_writes = writes - PREV.get(device).get('writes', 0)
            if fg > 1:
                print (diff_time, diff_ioreq, diff_reads, diff_writes)
            iops = diff_ioreq * 1.0 / diff_time
            readps = diff_reads * 1.0 / diff_time
            writeps = diff_writes * 1.0 / diff_time
        else:
            ready = 0
        PREV[device]['time'] = curtime
        PREV[device]['ioreq'] = ioreq
        PREV[device]['reads'] = reads
        PREV[device]['writes'] = writes
        if fg > 1:
            print(PREV)
        break
    stat.close()
    return ready, iops, readps, writeps


def init(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    for device in os.listdir(SYSDIR):
        # ignore files beginning with a period
        if device.startswith('.'):
            continue
        # no cdrom/dvd devices
        if device.startswith('sr'):
            continue
        # no loop devices
        if device.startswith('loop'):
            continue
        # no disk partitions devices
        if os.path.exists(SYSDIR + '/' + device + '/partition'):
            continue
        name = device
        if device.startswith('dm-'):
            try:
                fname = open(SYSDIR + '/' + device + '/dm/name')
            except IOError:
                continue
            name = fname.readline().rstrip()
        # chart: 1 - lines, 2 - bars, 3 - area
        # display:
        # 1 - autoscale, integer, min zero
        # 2 - percent display
        # 3 - autoscale, integer
        # 4 - autoscale, decimal point
        # 5 - autoscale, decimal point, min zero
        # 6 - binary status display [online/offline]
        #                                                                               unit, chart, display, color, box
        setparam(cur, 'system.disk.'+name+'.iops', 'F', 'Disk '+device+' number of I/O requests per second', 'Req/s', 1, 1, '#3c8dbc', 'box-primary')
        setparam(cur, 'system.disk.'+name+'.readps', 'F', 'Disk '+device+' number of reads per second', 'Bytes/s', 1, 1, '#3c8dbc', 'box-primary')
        setparam(cur, 'system.disk.'+name+'.writeps', 'F', 'Disk '+device+' number of writes per second', 'Bytes/s', 1, 1, '#3c8dbc', 'box-primary')
        PREV[device] = {}
        DISKS.append(device)
        NAMES[device] = name
    if fg > 1:
        print (PARAMS)
        print (DISKS)
        print (NAMES)
    cur.close()


def collect(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    for dev in DISKS:
        (ready, iops, readps, writeps) = diskstat(dev, fg)
        if fg > 1:
            print(ready, iops, readps, writeps)
        if ready:
            param = PARAMS['system.disk.'+NAMES[dev]+'.iops']
            lib.update_stat_f(cur, param, iops)
            param = PARAMS['system.disk.'+NAMES[dev]+'.readps']
            lib.update_stat_f(cur, param, readps)
            param = PARAMS['system.disk.'+NAMES[dev]+'.writeps']
            lib.update_stat_f(cur, param, writeps)
    cur.close()

