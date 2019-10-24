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
CLIENTS = []
STAT = {}
NR = 0


def setparam(cur, param, types, descr, unit, chart, display, color, box):
    parid = lib.getsetparam(cur, param, types, descr, unit, chart, display, color, box)
    PARAMS[param] = parid
    lib.setstat(cur, parid)


def clientlist(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curparam = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select R.name as name from config_confcomponent C, config_confrtype T, config_confresource R where C.type='D' and C.compid=R.compid and T.typeid=R.type and T.name='Client';")
    for client in cur:
        name = client['name']
        if name not in CLIENTS:
            CLIENTS.append(name)
        setparam(curparam, "bacula.client."+name+".status", 'N', "Status of bacula-fd agent service at "+name, "Status",
                 1, 6, '#001F3F', 'box-primary')
    global NR
    NR = cur.rowcount
    param = PARAMS["bacula.client.number"]
    lib.update_stat_n(cur, param, NR)
    if fg > 1:
        print(PARAMS)
        print(CLIENTS)
    cur.close()
    curparam.close()


def checkclient(name):
    out = lib.bconsolecommand('.status client=\"'+name+'\" header')
    for line in out:
        if line.startswith('version='):
            STAT[name] = 0
            return 1
    STAT[name] = NR * 2
    return 0


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
    setparam(cur, "bacula.client.number", 'N', "Number of bacula-fd clients", 'Number', 1, 1, '#3c8dbc', 'box-info')
    if fg > 1:
        print (PARAMS)
    cur.close()


def collect(conn, fg):
    clientlist(conn, fg)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    for client in CLIENTS:
        if STAT.get(client, 0) == 0:
            # last check was ok or never checked
            if fg > 1:
                print ("cheking ", client)
            out = checkclient(client)
            param = PARAMS["bacula.client."+client+".status"]
            lib.update_stat_n(cur, param, out)
            if out == 0:
                if fg > 1:
                    print ("Timeout in checking client "+client+" !")
                # TODO zastanowić się jak rozwiązać problem przerywania testu dla działających klientów
                # CLIENTS.append(CLIENTS.pop(CLIENTS.index(client)))
                break
        else:
            STAT[client] -= 1
    if fg > 1:
        print (STAT)
    cur.close()

