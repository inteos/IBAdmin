# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import print_function
from subprocess import Popen, PIPE


def update_stat_n(cur, param, value):
    cur.execute("update stats_statdaterange set maxtime=now() where parid=%s;", (param,))
    cur.execute("insert into stats_statdata(parid,time,nvalue) values (%s,now(),%s);", (param, value,))
    cur.execute("update stats_statstatus set time=now(), nvalue=%s where parid=%s;", (value, param,))


def update_stat_f(cur, param, value):
    cur.execute("update stats_statdaterange set maxtime=now() where parid=%s;", (param,))
    cur.execute("insert into stats_statdata(parid,time,fvalue) values (%s,now(),%s);", (param, value,))
    cur.execute("update stats_statstatus set time=now(), fvalue=%s where parid=%s;", (value, param,))


def setstat(cur, parid):
    cur.execute("select parid from stats_statdaterange where parid=%s;", (parid,))
    row = cur.fetchone()
    if row is None:
        cur.execute("insert into stats_statdaterange(parid, mintime, maxtime) values (%s, now(), now());", (parid,))
    cur.execute("select parid from stats_statstatus where parid=%s;", (parid,))
    row = cur.fetchone()
    if row is None:
        cur.execute("insert into stats_statstatus(parid, time) values (%s, now());", (parid,))


def getsetparam(cur, param, types, descr, unit, chart, display, color, box):
    cur.execute("select parid from stats_statparams where name=%s;", (param,))
    row = cur.fetchone()
    if row is not None:
        return row['parid']
    else:
        cur.execute("insert into stats_statparams(types,name,description,unit,chart,display,color,box) values (%s,%s,%s,%s,%s,%s,%s,%s) returning parid;",
                    (types, param, descr, unit, chart, display, color, box))
        row = cur.fetchone()
        return row['parid']


def bconsolecommand(cmd):
    bconsole = Popen(["/opt/bacula/bin/bconsole", "-u", "5"], stdin=PIPE, stdout=PIPE)
    bconsole.stdin.write("gui on\n")
    bconsole.stdin.write(cmd + "\n")
    bconsole.stdin.close()
    out = bconsole.stdout.read()
    bconsole.wait()
    lines = out.split('\n')
    return lines
