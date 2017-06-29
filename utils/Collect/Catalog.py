# -*- coding: UTF-8 -*-
from __future__ import print_function
import psycopg2
import psycopg2.extras
import lib


PARAMS = {}
SQL = {}


def setparam(cur, param, types, descr, unit, sql, chart, display, color, box):
    SQL[param] = sql or ''
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
    setparam(cur, "catalog.size.bytes", 'N', "The size of the whole catalog database", "Bytes", "select pg_catalog.pg_database_size('bacula') as data;", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "catalog.size.table.files.bytes", 'N', "The size of the file table in catalog", "Bytes", "select pg_relation_size('file') as data;", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "catalog.size.table.log.bytes", 'N', "The size of the log table in catalog", "Bytes", "select pg_relation_size('log') as data;", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "catalog.size.table.stats.bytes", 'N', "The size of the stats table in catalog", "Bytes", "select pg_relation_size('stats_statdata') as data;", 1, 1, '#3c8dbc', 'box-primary')
    if fg:
        print (PARAMS)
        print (SQL)
    cur.close()


def collect(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    for param in PARAMS:
        cur.execute(SQL[param])
        row = cur.fetchone()
        if row is not None:
            lib.update_stat_n(cur, PARAMS[param], row['data'])
    cur.close()

