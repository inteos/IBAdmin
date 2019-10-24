# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import print_function
import psycopg2
import psycopg2.extras
from subprocess import Popen, PIPE
import lib
from libs.plat import *


PARAMS = {}


def setparam(cur, param, types, descr, unit, chart, display, color, box):
    parid = lib.getsetparam(cur, param, types, descr, unit, chart, display, color, box)
    PARAMS[param] = parid
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
    setparam(cur, "bacula.daemon.bacula-dir.status", 'N', "Status of bacula-dir service", "Status", 1, 6, '#00a65a', 'box-primary')
    setparam(cur, "bacula.daemon.bacula-sd.status", 'N', "Status of bacula-sd service", "Status", 1, 6, '#605ca8', 'box-primary')
    setparam(cur, "bacula.daemon.bacula-fd.status", 'N', "Status of bacula-fd service", "Status", 1, 6, '#3c8dbc', 'box-primary')
    setparam(cur, "ibadmin.daemon.ibadstatd.status", 'N', "Status of IBAdmin ibadstatd service", "Status", 1, 6, '#ff851b', 'box-primary')
    if fg > 1:
        print (PARAMS)
    cur.close()


def collect(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    run = 0
    systemctl = Popen([SYSTEMCTL, 'is-active', 'bacula-dir'], stdout=PIPE)
    status = systemctl.stdout.read().rstrip()
    if 'active' == status:
        run = 1
    if fg > 1:
        print (status, run)
    param = PARAMS["bacula.daemon.bacula-dir.status"]
    lib.update_stat_n(cur, param, run)
    run = 0
    systemctl = Popen([SYSTEMCTL, 'is-active', 'bacula-sd'], stdout=PIPE)
    status = systemctl.stdout.read().rstrip()
    if 'active' == status:
        run = 1
    if fg > 1:
        print (status, run)
    param = PARAMS["bacula.daemon.bacula-sd.status"]
    lib.update_stat_n(cur, param, run)
    run = 0
    systemctl = Popen([SYSTEMCTL, 'is-active', 'bacula-fd'], stdout=PIPE)
    status = systemctl.stdout.read().rstrip()
    if 'active' == status:
        run = 1
    if fg > 1:
        print (status, run)
    param = PARAMS["bacula.daemon.bacula-fd.status"]
    lib.update_stat_n(cur, param, run)
    # record itself :)
    param = PARAMS["ibadmin.daemon.ibadstatd.status"]
    lib.update_stat_n(cur, param, 1)
    cur.close()

