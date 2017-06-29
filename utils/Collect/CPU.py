# -*- coding: UTF-8 -*-
from __future__ import print_function
import psycopg2
import psycopg2.extras
import lib


PARAMS = {}
PREV = {}


def setparam(cur, param, types, descr, unit, chart, display, color, box):
    parid = lib.getsetparam(cur, param, types, descr, unit, chart, display, color, box)
    PARAMS[param] = parid
    lib.setstat(cur, parid)


def cpustat():
    try:
        stat = open('/proc/stat')
    except IOError:
        return 0
    ready = 1
    util = 0
    user = 0
    system = 0
    iowait = 0
    for line in stat:
        if not line.startswith('cpu'):
            continue
        # print line
        cpu = line.split()
        # user + nice
        curuser = int(cpu[1]) + int(cpu[2])
        # system
        cursystem = int(cpu[3])
        # idle
        curidle = int(cpu[4])
        # iowait (since 2.5.41)
        curiowait = int(cpu[5])
        # all ticks
        total = curuser + cursystem + curidle + curiowait + int(cpu[6]) + int(cpu[7]) + int(cpu[8]) + int(cpu[9]) + int(cpu[10])
        if PREV.get('total'):
            diff_total = total - PREV.get('total', 0)
            diff_idle = curidle - PREV.get('idle', 0)
            diff_user = curuser - PREV.get('user', 0)
            diff_system = cursystem - PREV.get('system', 0)
            diff_iowait = curiowait - PREV.get('iowait', 0)

            util = 100.0 * (diff_total - diff_idle) / diff_total
            user = 100.0 * diff_user / diff_total
            system = 100.0 * diff_system / diff_total
            iowait = 100.0 * diff_iowait / diff_total
        else:
            ready = 0
        PREV['user'] = curuser
        PREV['system'] = cursystem
        PREV['iowait'] = curiowait
        PREV['idle'] = curidle
        PREV['total'] = total
        break
    stat.close()
    return ready, util, user, system, iowait


def loadavgstat():
    try:
        stat = open('/proc/loadavg')
    except IOError:
        return 0
    l1 = 0
    l5 = 0
    l15 = 0
    for line in stat:
        cpu = line.split()
        l1 = float(cpu[0])
        l5 = float(cpu[1])
        l15 = float(cpu[2])
        break
    return 1, l1, l5, l15


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
    setparam(cur, 'system.cpu.util', 'F', 'CPU overall utilization', 'CPU%', 3, 2, '#3c8dbc', 'box-primary')
    setparam(cur, 'system.cpu.util.user', 'F', 'CPU utilization in User mode', 'CPU%', 3, 2, '#3c8dbc', 'box-primary')
    setparam(cur, 'system.cpu.util.system', 'F', 'CPU utilization in System mode', 'CPU%', 3, 2, '#3c8dbc', 'box-primary')
    setparam(cur, 'system.cpu.util.iowait', 'F', 'CPU utilization in I/O Wait', 'CPU%', 3, 2, '#3c8dbc', 'box-primary')
    setparam(cur, 'system.cpu.loadavg.1m', 'F', 'CPU load average in 1 min', 'Proc', 3, 4, '#3c8dbc', 'box-primary')
    setparam(cur, 'system.cpu.loadavg.5m', 'F', 'CPU load average in 5 min', 'Proc', 3, 4, '#3c8dbc', 'box-primary')
    setparam(cur, 'system.cpu.loadavg.15m', 'F', 'CPU load average in 15 min', 'Proc', 3, 4, '#3c8dbc', 'box-primary')
    if fg:
        print (PARAMS)
    cur.close()


def collect(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    (ready, util, user, system, iowait) = cpustat()
    if fg:
        print(ready, util, user, system, iowait)
    if ready:
        param = PARAMS['system.cpu.util']
        lib.update_stat_f(cur, param, util)
        param = PARAMS['system.cpu.util.user']
        lib.update_stat_f(cur, param, user)
        param = PARAMS['system.cpu.util.system']
        lib.update_stat_f(cur, param, system)
        param = PARAMS['system.cpu.util.iowait']
        lib.update_stat_f(cur, param, iowait)

    (ready, l1, l5, l15) = loadavgstat()
    if fg:
        print(ready, l1, l5, l15)
    if ready:
        param = PARAMS['system.cpu.loadavg.1m']
        lib.update_stat_f(cur, param, l1)
        param = PARAMS['system.cpu.loadavg.5m']
        lib.update_stat_f(cur, param, l5)
        param = PARAMS['system.cpu.loadavg.15m']
        lib.update_stat_f(cur, param, l15)

    cur.close()

