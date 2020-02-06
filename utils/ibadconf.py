#!/opt/ibadengine/bin/python
# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import print_function
import sys
import psycopg2
import psycopg2.extras
import time


def get_parameters(conn, resid, level, component):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select name, value, str, enc from config_confparameter where resid=%s order by parid", (resid,))
    while 1:
        row = cur.fetchone()
        if row is None:
            break
        cyt = 0
        name = row['name']
        if not name.startswith('.'):
            indent = ''
            if level:
                indent += "  " * level
            if row['enc']:
                # print (indent + "# C:"+component)
                out = getdecpass(component, row['value'])
                cyt = 1
            else:
                out = row['value']
            if row['str']:
                cyt = 1
            if cyt or len(out) == 0:
                print(indent + name + " = \"" + out + "\"")
            else:
                print(indent + name + " = " + out)


def printhelp():
    print(" Possible parameters are:")
    print(" -d [name]       Director configuration.")
    print(" -c [name]       Bacula console configuration.")
    print(" -f <name>       File Daemon configuration.")
    print(" -s <name>       Storage Daemon configuration.")
    print(" <ctype> -l      Lists available component names.")
    print(" -r <restype>    Lists <restype> names in Director.")
    print(" -h              Print this help.")
    print()


def sanitize_conf_string(confstr):
    confstr = confstr.replace('\\', "\\\\") # \ -> \\
    confstr = confstr.replace('\"', "\\\"") # " -> \"
    return confstr


if __name__ == "__main__":
    # check input data
    if len(sys.argv) < 2:
        print("No component type to generate configuration!")
        printhelp()
        sys.exit(1)

    if sys.argv[1] == "-h":
        print("IBAdmin - Inteos Bacula Administration App - (c) 2015-2018 Inteos sp. z o.o.")
        printhelp()
        sys.exit(0)

    res = None
    listing = False
    comptype = None
    name = None
    strunc = False
    sdedup = False
    if sys.argv[1] == '-r':
        if len(sys.argv) < 3:
            print("No resource name to list!")
            sys.exit(2)
        res = sys.argv[2]
    elif sys.argv[1] == '-strunc':
        strunc = True
    elif sys.argv[1] == '-sdedup':
        sdedup = True
    else:
        comptype = sys.argv[1]
        if comptype == '-d':
            comptype = 'D'
            if len(sys.argv) > 2:
                name = sys.argv[2]
            else:
                name = ''
        elif comptype == '-f':
            comptype = 'F'
            if len(sys.argv) > 2:
                name = sys.argv[2]
            else:
                print("No FileDaemon component name to generate configuration!")
                sys.exit(1)
        elif comptype == '-s':
            comptype = 'S'
            if len(sys.argv) > 2:
                name = sys.argv[2]
            else:
                print("No StorageDaemon component name to generate configuration!")
                sys.exit(1)
        elif comptype == '-c':
            comptype = 'C'
            if len(sys.argv) > 2:
                name = sys.argv[2]
            else:
                name = ''
        else:
            print("Unknown component type.")
            printhelp()
            sys.exit(1)
        if name == '-l':
            listing = True
            name = ''

    # load config
    sys.path.append('/opt/ibadmin')
    from ibadmin.settings import DATABASES
    from libs.conf import getdecpass

    # log = open('/tmp/ibadconfd_'+str(os.getpid())+'.log', 'w')
    log = None
    dbname = DATABASES['default']['NAME']
    dbuser = DATABASES['default']['USER']
    dbpass = DATABASES['default']['PASSWORD']
    dbhost = DATABASES['default']['HOST']
    dbport = DATABASES['default']['PORT']

    connectionok = 5
    conn = None
    while connectionok:
        try:
            conn = psycopg2.connect("dbname=" + dbname + " user=" + dbuser + " password=" + dbpass + " host=" + dbhost
                                    + " port=" + dbport)
        except:
            if log is not None:
                log.write('Problem connecting to database! retrying ...\n')
            connectionok -= 1
            time.sleep(5)
            if connectionok == 0:
                log.write('Giving up!\n')
                log.close()
                sys.exit(6)
        else:
            connectionok = 0

    if log is not None:
        log.write('Connection to database ok.\n')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if res is not None:
        cur.execute("select R.name from config_confcomponent C, config_confresource R, config_confrtype T where "
                    "C.compid=R.compid and R.type=T.typeid and T.name=%s and C.type='D';", (res,))
        while 1:
            row = cur.fetchone()
            if row is None:
                conn.close()
                sys.exit(0)
            print(str(row['name']))

    if strunc:
        cur.execute("select R.name from config_confcomponent C, config_confresource R, config_confparameter P where "
                    "C.type='D' and C.compid=R.compid and R.resid=P.resid and P.name='MediaType' and (value like "
                    "'File%' or value like 'Dedup%');")
        while 1:
            row = cur.fetchone()
            if row is None:
                conn.close()
                sys.exit(0)
            print(str(row['name']))

    if sdedup:
        cur.execute("select R.name from config_confcomponent C, config_confresource R, config_confparameter P where "
                    "C.type='D' and C.compid=R.compid and R.resid=P.resid and P.name='MediaType' and value like "
                    "'Dedup%' and not R.resid in (select resid from config_confparameter where name='.Alias');")
        while 1:
            row = cur.fetchone()
            if row is None:
                conn.close()
                sys.exit(0)
            print(str(row['name']))

    if listing:
        print ("Listing component type: " + comptype)
        cur.execute("select name from config_confcomponent where type=%s;", (comptype, ))
        while 1:
            row = cur.fetchone()
            if row is None:
                conn.close()
                sys.exit(0)
            print (" " + str(row['name']))

    cur2 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur3 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if len(name) == 0 and comptype in ('D', 'C'):
        cur.execute("select name from config_confcomponent where type='D';")
        row = cur.fetchone()
        if row is None:
            if log is not None:
                log.write("System not configured.\n")
            print("System not configured.")
            if log is not None:
                log.close()
            sys.exit(2)
        else:
            name = row['name']

    cur.execute("select * from config_confcomponent where type=%s and name=%s;", (comptype, name))
    row = cur.fetchone()
    if row is None:
        print("Cannot find component '" + name + "' of type " + comptype + " in configuration.")
        if log is not None:
            log.write("Cannot find component " + name + " of type " + comptype + " in configuration.\n")
            log.close()
        sys.exit(1)

    compid = row['compid']
    component = row['name']
    comptype = row['type']

    print ("#\n# Bacula Configuration file for Bacula Enterprise 8")
    print ("# Configuration generated by ibadconf script")
    print ("#\n#  (c) 2017 by Inteos Sp. z o.o.\n#")
    print ("# .component: " + str(compid) + " : " + component + " : " + comptype + "\n")

    cur.execute("select R.resid, T.name as resource, R.name, R.description \
                    from config_confrtype T,config_confresource R \
                    where typeid=type and sub is null and compid=%s \
                    order by R.type", (compid,))

    while 1:
        row = cur.fetchone()
        if row is None:
            break
        resid = row['resid']
        print ("# resid: " + str(resid))
        print (row['resource'] + " {")
        print ("  Name = \"" + row['name'] + "\"")
        if row['description'] is not None and len(row['description']) > 0:
            print ("  Description = \"" + sanitize_conf_string(row['description']) + "\"")
        get_parameters(conn, resid, 1, component)
        # Now find any subresource
        cur2.execute(
            "select R.resid, T.name as resource, T.equ from config_confrtype T, config_confresource R where "
            "T.typeid=R.type and sub=%s order by R.type",
            (resid,))
        while 1:
            row2 = cur2.fetchone()
            if row2 is None:
                break
            resid1 = row2['resid']
            equ = " {"
            if row2['equ']:
                equ = " = {"
            print ("  " + row2['resource'] + equ)
            # now any subsequent subresource - we support 2 nested subresources only
            cur3.execute(
                "select R.resid, T.name as resource, T.equ from config_confrtype T,config_confresource R where "
                "T.typeid=R.type and sub=%s order by R.resid",
                (resid1,))
            while 1:
                row3 = cur3.fetchone()
                if row3 is None:
                    break
                resid2 = row3['resid']
                equ = " {"
                if row3['equ']:
                    equ = " = {"
                print ("    " + row3['resource'] + equ)
                get_parameters(conn, resid2, 3, component)
                print ("    }")
            get_parameters(conn, resid1, 2, component)
            print ("  }")
        print ("}\n")
    if log is not None:
        log.write('Configuration generated successfully.\n')
    print ("# .end config: " + str(compid) + " : " + component + " : " + comptype)

    cur.close()
    cur2.close()
    cur3.close()
    conn.close()
    if log is not None:
        log.close()
