# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import print_function
import psycopg2
import psycopg2.extras
import lib


PARAMS = {}
KEY_MAPPING = [
    'MemTotal',
    'MemFree',
    'Buffers',
    'Cached',
    'Active',
    'Dirty',
    'Inactive',
    'Shmem',
    'SwapTotal',
    'SwapFree',
    'SwapCached',
]
SYNTH = {}


def setparam(cur, key, param, types, descr, unit, chart, display, color, box):
    parid = lib.getsetparam(cur, param, types, descr, unit, chart, display, color, box)
    PARAMS[key] = parid
    lib.setstat(cur, parid)


def init(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # chart: 1 - lines, 2 - bars, 3 - area
    # display:
    # 1 - autoscale, integer, min zero
    # 2 - percent display
    # 3 - autoscale, integer
    # 4 - autoscale, decimal point
    # 5 - autoscale, decimal point, min zero
    # 6 - binary status display [online/offline]
    #                                                                               unit, chart, display, color, box
    setparam(cur, 'MemTotal', 'system.mem.total', 'N', 'Total amount of physical RAM', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, 'MemFree', 'system.mem.free', 'N', 'The amount of physical RAM left unused by the system', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, 'Buffers', 'system.mem.buffers', 'N', 'The amount of physical RAM used for file buffers', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, 'Cached', 'system.mem.cached', 'N', 'The amount of physical RAM used as cache memory', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, 'Active', 'system.mem.active', 'N', 'The total amount of buffer or page cache memory that is in active use', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, 'Dirty', 'system.mem.dirty', 'N', 'The total amount of memory waiting to be written back to the disk', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, 'Inactive', 'system.mem.inactive', 'N', 'The total amount of buffer or page cache memory that are free', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, 'Shmem', 'system.mem.shmem', 'N', 'The amount of physical RAM shared in processes', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, 'SwapTotal', 'system.swap.total', 'N', 'The total amount of swap available', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, 'SwapFree', 'system.swap.free', 'N', 'The total amount of swap free', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, 'SwapCached', 'system.swap.cached', 'N', 'The amount of swap, in kilobytes, used as cache memory', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
# Below are useless parameters
#    setparam(cur, 'VmallocTotal', 'system.mem.vm.total', 'N', 'The total amount of memory of total allocated virtual address space', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
#    setparam(cur, 'VmallocUsed', 'system.mem.vm.used', 'N', 'The total amount of memory of used virtual address space', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, '_Memory_Used', 'system.mem.used', 'N', 'The total amount of memory used', 'Bytes', 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, '_Memory_Util', 'system.mem.util', 'F', 'The total memory utilisation', 'MEM%', 1, 1, '#3c8dbc', 'box-primary')
    if fg > 1:
        print (PARAMS)
    cur.close()


def collect(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        stat = open('/proc/meminfo')
    except IOError:
        return 0
    # read all memory info into buffer
    data = stat.read()
    stat.close()
    for line in data.splitlines():
        try:
            name, value, units = line.split()
            name = name.rstrip(':')
            value = int(value)
            if name not in KEY_MAPPING:
                continue
        except ValueError:
            continue
        if 'kB' == units:
            value *= 1024
        elif 'MB' == units:
            value *= 1049586
        elif 'GB' == units:
            value *= 1024 * 1048576
        if fg > 1:
            print (name, value)
        param = PARAMS[name]
        lib.update_stat_n(cur, param, value)
        if name in ('MemTotal', 'MemFree'):
            SYNTH[name] = value
    if SYNTH.get('MemTotal', 0):
        used = SYNTH['MemTotal'] - SYNTH['MemFree']
        util = used * 100.0 / SYNTH['MemTotal']
        if fg > 1:
            print (used, util)
        param = PARAMS['_Memory_Used']
        lib.update_stat_n(cur, param, used)
        param = PARAMS['_Memory_Util']
        lib.update_stat_f(cur, param, util)
    cur.close()
