# -*- coding: UTF-8 -*-
from __future__ import print_function
import time
import os
import psycopg2
import psycopg2.extras
import lib


PARAMS = {}
PREV = {}
NETIFS = []


def setparam(cur, param, types, descr, unit, chart, display, color, box):
    parid = lib.getsetparam(cur, param, types, descr, unit, chart, display, color, box)
    PARAMS[param] = parid
    lib.setstat(cur, parid)


SYSDIR = "/sys/class/net"


def netifstat(device):
    try:
        rxstat = open(SYSDIR + '/' + device + '/statistics/rx_bytes')
        txstat = open(SYSDIR + '/' + device + '/statistics/tx_bytes')
    except IOError:
        return 0
    ready = 1
    rxbytes = int(rxstat.read().rstrip())
    txbytes = int(txstat.read().rstrip())
    rxstat.close()
    txstat.close()
    # time
    curtime = time.time()
    rxps = 0
    txps = 0
    if PREV.get(device).get('time'):
        diff_time = curtime - PREV.get(device).get('time', 0)
        if diff_time == 0:
            return 0
        diff_rxbytes = rxbytes - PREV.get(device).get('rxbytes', 0)
        diff_txbytes = txbytes - PREV.get(device).get('txbytes', 0)
        rxps = diff_rxbytes / diff_time
        txps = diff_txbytes / diff_time
    else:
        ready = 0
    PREV[device]['time'] = curtime
    PREV[device]['rxbytes'] = rxbytes
    PREV[device]['txbytes'] = txbytes
    return ready, rxps, txps


"""
TODO: powinniśmy wykorzystać więcej statystyk:
    collisions  multicast  rx_bytes  rx_compressed  rx_crc_errors  rx_dropped  rx_errors  rx_fifo_errors
    rx_frame_errors  rx_length_errors  rx_missed_errors  rx_nohandler  rx_over_errors  rx_packets  tx_aborted_errors
    tx_bytes  tx_carrier_errors  tx_compressed  tx_dropped  tx_errors  tx_fifo_errors  tx_heartbeat_errors  tx_packets
    tx_window_errors
"""


def init(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    for device in os.listdir(SYSDIR):
        # ignore files beginning with a period
        if device.startswith('.'):
            continue
        name = device
        # chart: 1 - lines, 2 - bars, 3 - area
        # display:
        # 1 - autoscale, integer, min zero
        # 2 - percent display
        # 3 - autoscale, integer
        # 4 - autoscale, decimal point
        # 5 - autoscale, decimal point, min zero
        # 6 - binary status display [online/offline]
        #                                                                               unit, chart, display, color, box
        setparam(cur, 'system.net.'+name+'.rxps', 'F', 'Network interface '+device+' receive bytes/s', 'Bytes/s', 1, 1, '#3c8dbc', 'box-success')
        setparam(cur, 'system.net.'+name+'.txps', 'F', 'Network interface '+device+' transfer bytes/s', 'Bytes/s', 1, 1, '#3c8dbc', 'box-danger')
        PREV[device] = {}
        NETIFS.append(device)
    if fg:
        print (PARAMS)
        print (NETIFS)
    cur.close()


def collect(conn, fg):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    for dev in NETIFS:
        (ready, rxps, txps) = netifstat(dev)
        if fg:
            print(dev, ready, rxps, txps)
        if ready:
            param = PARAMS['system.net.'+dev+'.rxps']
            lib.update_stat_f(cur, param, rxps)
            param = PARAMS['system.net.'+dev+'.txps']
            lib.update_stat_f(cur, param, txps)
    cur.close()

