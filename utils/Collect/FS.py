# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import print_function
import os
import psycopg2
import psycopg2.extras
import lib


PARAMS = {}
FS = []


def setparam(cur, param, types, descr, unit, chart, display, color, box):
    parid = lib.getsetparam(cur, param, types, descr, unit, chart, display, color, box)
    PARAMS[param] = parid
    lib.setstat(cur, parid)


def update(cur, fg):
    try:
        mounts = open('/proc/mounts')
    except IOError:
        return

    for line in mounts:
        try:
            mount = line.split()
            device = mount[0]
            mountpoint = mount[1]
        except (IndexError, ValueError):
            continue

        # ignore virtual filesystem by device
        if not device.startswith('/dev'):
            continue
        # ignore virtual filesystems by mounted path
        if mountpoint.startswith('/dev') or mountpoint.startswith('/proc') or mountpoint.startswith('/sys'):
            continue

        if mountpoint not in FS:
            FS.append(mountpoint)
            # chart: 1 - lines, 2 - bars, 3 - area
            # display:
            # 1 - autoscale, integer, min zero
            # 2 - percent display
            # 3 - autoscale, integer
            # 4 - autoscale, decimal point
            # 5 - autoscale, decimal point, min zero
            # 6 - binary status display [online/offline]
            #                                                                           unit, chart, display, color, box
            setparam(cur, 'system.fs.'+mountpoint+'.size.total', 'N', 'Filesystem '+mountpoint+ ' on device '+device+' total size', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
            setparam(cur, 'system.fs.'+mountpoint+'.size.free', 'N', 'Filesystem '+mountpoint+ ' on device '+device+' free space', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
            setparam(cur, 'system.fs.'+mountpoint+'.size.available', 'N', 'Filesystem '+mountpoint+' on device '+device+' available space for user', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
            setparam(cur, 'system.fs.'+mountpoint+'.inode.total', 'N', 'Filesystem '+mountpoint+' number of inodes', 'inode', 1, 1, '#3c8dbc', 'box-primary')
            setparam(cur, 'system.fs.'+mountpoint+'.inode.free', 'N', 'Filesystem '+mountpoint+' free inodes', 'inode', 1, 1, '#3c8dbc', 'box-primary')
            setparam(cur, 'system.fs.'+mountpoint+'.inode.available', 'N', 'Filesystem '+mountpoint+' available inodes for user', 'inode', 1, 1, '#3c8dbc', 'box-primary')
            if fg > 1:
                print ("Added:" + mountpoint)
    mounts.close()


def init(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    update(cur, fg)
    cur.close()

    if fg > 1:
        print (PARAMS)
        print (FS)


def collect(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    update(cur, fg)
    for mountpoint in FS:
        try:
            data = os.statvfs(mountpoint)
        except OSError:
            continue
        size_total = data.f_blocks * data.f_frsize
        size_free = data.f_bfree * data.f_frsize
        size_avail = data.f_bavail * data.f_frsize
        inode_total = data.f_files
        inode_free = data.f_ffree
        inode_avail = data.f_favail

        if fg > 1:
            print (mountpoint, size_free, size_avail, inode_total, inode_free, inode_avail)

        param = PARAMS['system.fs.'+mountpoint+'.size.total']
        lib.update_stat_n(cur, param, size_total)
        param = PARAMS['system.fs.'+mountpoint+'.size.free']
        lib.update_stat_n(cur, param, size_free)
        param = PARAMS['system.fs.'+mountpoint+'.size.available']
        lib.update_stat_n(cur, param, size_avail)
        param = PARAMS['system.fs.'+mountpoint+'.inode.total']
        lib.update_stat_n(cur, param, inode_total)
        param = PARAMS['system.fs.'+mountpoint+'.inode.free']
        lib.update_stat_n(cur, param, size_free)
        param = PARAMS['system.fs.'+mountpoint+'.inode.available']
        lib.update_stat_n(cur, param, inode_avail)

    cur.close()
