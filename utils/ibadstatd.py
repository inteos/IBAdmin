#!/opt/ibadengine/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import sys
import time
import signal
import psycopg2
import psycopg2.extras


def printhelp():
    print("Possible parameters are:")
    print(" start       starts the daemon.")
    print(" stop        stops the daemon.")
    print(" restart     restarts the daemon.")
    print(" -f          Don't go into background, run in foreground. Useful for debugging.")
    print(" -h          Print this help.")
    print()


sys.path.append('/opt/ibadmin')
from libs.daemon import Daemon
from ibadmin.settings import DATABASES
from Collect import Catalog
from Collect import Bacula
from Collect import CPU
from Collect import Mem
from Collect import Disk
from Collect import FS
from Collect import Dmon
from Collect import Net
from Collect import Client


# load config
dbname = DATABASES['default']['NAME']
dbuser = DATABASES['default']['USER']
dbpass = DATABASES['default']['PASSWORD']
dbhost = DATABASES['default']['HOST']
dbport = DATABASES['default']['PORT']
cont = 1


def handler(signal, frame):
    global cont
    cont = 0


def maininit(fg=0):
    cont = 10
    conn = None
    while cont:
        try:
            conn = psycopg2.connect("dbname=" + dbname + " user=" + dbuser + " password=" + dbpass + " host=" + dbhost + " port=" + dbport)
        except:
            cont -= 1
            if not cont:
                sys.exit(10)
            time.sleep(10)
            continue
        break
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("select count(1) from stats_statparams;")
    except:
        print("No stat tables found or DB error")
        sys.exit(3)
    # all colectors init goes here
    Catalog.init(conn, 0)
    Bacula.init(conn, 0)
    CPU.init(conn, 0)
    Mem.init(conn, 0)
    Disk.init(conn, 0)
    FS.init(conn, 0)
    Dmon.init(conn, 0)
    Net.init(conn, 0)
    Client.init(conn, 0)

    conn.commit()
    cur.close()
    conn.close()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


def mainloop(fg=0):
    conn = psycopg2.connect("dbname=" + dbname + " user=" + dbuser + " password=" + dbpass + " host=" + dbhost + " port=" + dbport)
    while cont:
        if fg:
            print(time.asctime() + " : Collecting ...")
        try:
            conn.isolation_level
        except psycopg2.OperationalError:
            conn = psycopg2.connect("dbname=" + dbname + " user=" + dbuser + " password=" + dbpass + " host=" + dbhost + " port=" + dbport)
        # colled the data
        Catalog.collect(conn, fg)
        Bacula.collect(conn, fg)
        CPU.collect(conn, fg)
        Mem.collect(conn, fg)
        Disk.collect(conn, fg)
        FS.collect(conn, fg)
        Dmon.collect(conn, fg)
        Net.collect(conn, fg)
        # it should be the last collector
        Client.collect(conn, fg)

        if fg:
            print(time.asctime() + " : Done")
        conn.commit()
        time.sleep(60)

    if fg:
        print(time.asctime() + " : Finish")
    conn.close()
    sys.exit(0)


class IBStatd(Daemon):
    def run(self):
        mainloop()


if __name__ == "__main__":
    print("IBAdmin stats collector daemon (c) 2016 Inteos Sp. z o.o.")
    daemon = IBStatd('/tmp/ibadstatd.pid')
    if len(sys.argv) == 2:
        if '-h' == sys.argv[1]:
            printhelp()
            sys.exit(0)
        elif 'start' == sys.argv[1]:
            maininit()
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            printhelp()
            sys.exit(2)
    elif len(sys.argv) == 3:
        if '-f' == sys.argv[1] and 'start' == sys.argv[2]:
            maininit(fg=1)
            mainloop(fg=1)
            sys.exit(0)
        else:
            printhelp()
            sys.exit(2)
    else:
        printhelp()
        sys.exit(2)
    sys.exit(0)
