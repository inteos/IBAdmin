#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import print_function
import sys
import signal
import psycopg2
import psycopg2.extras
import ast


def printhelp():
    print("Required parameter is:")
    print(" <taskid>    starts the tasks daemon for <taskid>.")
    print("Optional parameter is:")
    print(" -h          Print this help.")
    print()


sys.path.append('/opt/ibadmin')
from libs.daemon import Daemon
from libs.bconsole import doDeleteJobid, directorreload, doUpdateslots, doLabel, disableDevice, enableDevice, \
    getStorageIdleDevice, umountDevice, getStorageStatusDevice
from ibadmin.settings import DATABASES
from libs.tapelib import *

# load config
dbname = DATABASES['default']['NAME']
dbuser = DATABASES['default']['USER']
dbpass = DATABASES['default']['PASSWORD']
dbhost = DATABASES['default']['HOST']
dbport = DATABASES['default']['PORT']
cont = 1
task = {}


def handler(signal, frame):
    global cont
    cont = 0


def maininit(taskid=None, fg=False):
    if taskid is None:
        if fg:
            print ('Invalid taskid in maininit!')
        sys.exit(3)
    conn = psycopg2.connect("dbname=" + dbname + " user=" + dbuser + " password=" + dbpass + " host=" + dbhost + " port=" + dbport)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("select count(1) from tasks_tasks;")
    except:
        print ('No tasks tables found or DB error!')
        sys.exit(3)
    cur.execute("select * from tasks_tasks where status='N' and taskid=%s;", (taskid,))
    row = cur.fetchone()
    if row is None:
        return None
    cur.close()
    conn.close()
    if fg:
        print (row)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return row


def update_status(curtask=None, taskid=0, progress=0.0, log='', status='R'):
    curtask.execute("update tasks_tasks set progress=%s, log=%s, status=%s where taskid=%s",
                    (int(round(progress)), log, status, taskid,))


def update_status_error(curtask=None, taskid=0, log=''):
    curtask.execute("update tasks_tasks set log=%s, status='E', endtime=now() where taskid=%s",
                    (log, taskid,))


def update_status_finish(curtask=None, taskid=0, progress=100.0, log=''):
    curtask.execute("update tasks_tasks set progress=%s, log=%s, status='F', endtime=now() where taskid=%s",
                    (int(round(progress)), log, taskid,))


def update_status_out(curtask=None, taskid=0, outlog=''):
    curtask.execute("update tasks_tasks set output=%s where taskid=%s",
                    (outlog, taskid,))


def delete_parameters(cur=None, resid=None):
    if cur is None or resid is None:
        return
    cur.execute("delete from config_confparameter where resid=%s;", (resid,))


def delete_parameters_list(cur=None, reslist=None):
    if cur is None or reslist is None:
        return
    cur.execute("delete from config_confparameter where resid=ANY(%s);", (reslist,))


def delete_resource(cur=None, resid=None):
    if cur is None or resid is None:
        return
    cur.execute("delete from config_confresource where resid=%s;", (resid,))


def delete_resource_list(cur=None, reslist=None):
    if cur is None or reslist is None:
        return
    cur.execute("delete from config_confresource where resid=ANY(%s);", (reslist,))


def getresid(cur=None, compid=None, restype=None, resname=None):
    if cur is None or compid is None or restype is None or resname is None:
        return None
    cur.execute("select resid from config_confresource R, config_confrtype T where compid=%s and R.type=T.typeid and T.name=%s "
                "and R.name=%s;",
                (compid, restype, resname,))
    row = cur.fetchone()
    resid = row['resid']
    return resid


def getdircompid(cur=None):
    if cur is None:
        return None
    cur.execute("select compid from config_confcomponent where type='D';")
    row = cur.fetchone()
    dircompid = row['compid']
    return dircompid


def dodeleteJob(conn=None, cur=None, name=None):
    if conn is None or cur is None or name is None:
        return
    # find dircompid
    dircompid = getdircompid(cur)
    # find jobresid
    jobresid = getresid(cur, dircompid, 'Job', name)
    # find Fileset resources
    fsname = 'fs-' + name
    fsresid = getresid(cur, dircompid, 'Fileset', fsname)
    # get Include and Exclude resids
    cur.execute("select resid from config_confresource where compid=%s and sub=%s;", (dircompid, fsresid,))
    row = cur.fetchall()
    fslist = [r[0] for r in row]
    # add fsresid too
    fslist.append(fsresid)
    # get Options resid for Include
    cur.execute("select resid from config_confresource where compid=%s and sub=ANY(%s);", (dircompid, fslist,))
    row = cur.fetchone()
    fslist.append(row['resid'])
    # delete all parameters
    delete_parameters_list(cur, fslist)
    # delete fs resources
    fslist.append(fsresid)
    delete_resource_list(cur, fslist)
    # find sch resource
    schname = 'sch-' + name
    schresid = getresid(cur, dircompid, 'Schedule', schname)
    # delete Schedule parameters
    delete_parameters(cur=cur, resid=schresid)
    # delete Schedule resource
    delete_resource(cur=cur, resid=schresid)
    # delete Job parameters
    delete_parameters(cur=cur, resid=jobresid)
    # delete Job resource
    delete_resource(cur=cur, resid=jobresid)


def dodeleteClient(conn=None, cur=None, name=None):
    if conn is None or cur is None or name is None:
        return
    # find dircompid
    dircompid = getdircompid(cur)
    # find clientresid
    clientresid = getresid(cur, dircompid, 'Client', name)
    # delete Client parameters
    delete_parameters(cur=cur, resid=clientresid)
    # delete Client resource
    delete_resource(cur=cur, resid=clientresid)
    # delete FD component
    cur.execute("select compid from config_confcomponent where type='F' and name=%s;", (name,))
    row = cur.fetchone()
    if row is not None:
        # get fdcompid
        fdcompid = row['compid']
        # delete component parameters
        cur.execute("delete from config_confparameter where resid in (select resid from config_confresource where compid=%s);",
                    (fdcompid,))
        # delete component resources
        cur.execute("delete from config_confresource where compid=%s;", (fdcompid,))
        # delete component
        cur.execute("delete from config_confcomponent where compid=%s;", (fdcompid,))


def enableJob(cur=None, name=None):
    if cur is None or name is None:
        return
    cur.execute("delete from config_confparameter where name='.Disabledfordelete' and resid in (select resid from "
                "config_confresource R, config_confrtype T where R.name=%s and R.type=T.typeid and T.name='Job');", (name,))
    cur.execute("update config_confparameter set value='Yes' where name='Enabled' and resid in (select resid from "
                "config_confresource R, config_confrtype T where R.name=%s and R.type=T.typeid and T.name='Job');", (name,))


def enableClient(cur=None, name=None):
    if cur is None or name is None:
        return
    cur.execute("delete from config_confparameter where name in ('.Disabledfordelete', 'Enabled') and resid in (select "
                "resid from config_confresource R, config_confrtype T where R.name=%s and R.type=T.typeid and T.name='Client');",
                (name,))


def delete_job(conn=None, cur=None, curtask=None, tasks=None):
    global cont
    if conn is None or tasks is None or cur is None or curtask is None:
        return
    # update status
    taskid = tasks['taskid']
    update_status(curtask=curtask, taskid=taskid)
    # prepare required variables
    progress = 0
    log = ''
    name = tasks['params']
    step = 100
    try:
        cur.execute("select jobid from job where name=%s;", (name,))
        jids = cur.fetchall()

        jidslen = len(jids)
        if jidslen:
            # some jobids exists, delete them all
            step = 100 / (jidslen + 1.0)
            for jobid in jids:
                if not cont:
                    log += 'Error: execution stopped.'
                    update_status_error(curtask=curtask, taskid=taskid, log=log)
                    conn.commit()
                    return
                out = doDeleteJobid(jobid[0])
                # out = [u'JobId=173,and,associated,records,deleted,from,the,catalog.']
                log += out[0].replace(',', ' ') + '\n'
                progress += step
                update_status(curtask=curtask, progress=progress, log=log, taskid=taskid)
                # give feedback to application server
                conn.commit()
    except Exception as detail:
        conn.autocommit = True
        enableJob(cur, name)
        log += 'Error: job history deleting problem. Err=' + str(detail) + ' [lineno:' + \
               str(sys.exc_info()[-1].tb_lineno) + ']'
        update_status_error(curtask=curtask, log=log, taskid=taskid)
        return
    try:
        # start a transaction
        conn.autocommit = False
        dodeleteJob(conn=conn, cur=cur, name=name)
    except Exception as detail:
        conn.rollback()
        # back autocommit
        conn.autocommit = True
        enableJob(cur, name)
        log += 'Error: configuration deleting problem. Err=' + str(detail) + ' [lineno:' + \
               str(sys.exc_info()[-1].tb_lineno) + ']'
        update_status_error(curtask=curtask, log=log, taskid=taskid)
        return
    progress += step
    log += 'Delete Job: "' + name + '" from configuration.'
    update_status_finish(curtask=curtask, log=log, taskid=taskid)
    conn.commit()


def delete_client(conn=None, cur=None, curtask=None, tasks=None):
    global cont
    if conn is None or tasks is None or cur is None or curtask is None:
        return
    # update status
    # print ('In procedure: deleting client')
    taskid = tasks['taskid']
    update_status(curtask=curtask, taskid=taskid)
    # prepare required variables
    progress = 0
    log = ''
    name = tasks['params']
    step = 100
    jobs = []
    try:
        # TODO: change from: femove history, remove jobs, remove client into: remove jobs with history, remove client
        cur.execute("select R.name from config_confresource R, config_confparameter P where R.resid=P.resid and P.name='Client' "
                    "and P.value=%s;", (name,))
        jobs = cur.fetchall()
        jobslen = len(jobs)
        if jobslen:
            # a client has defined jobs, so find jobid to delete
            joblist = tuple([j[0] for j in jobs])
            cur.execute("select jobid from job where name in %s;", (joblist,))
            jids = cur.fetchall()

            jidslen = len(jids)
            if jidslen:
                # some jobids exists, delete them all
                step = 100 / (jidslen + jobslen + 1.0)
                for jobid in jids:
                    if not cont:
                        log += 'Error: execution stopped.'
                        update_status_error(curtask=curtask, taskid=taskid, log=log)
                        conn.commit()
                        return
                    # print('deleting jobid:', jobid[0])
                    out = doDeleteJobid(jobid[0])
                    # out = ['JobId='+str(jobid[0])+',and,associated,records,deleted,from,the,catalog.']
                    log += out[0].replace(',', ' ') + '\n'
                    progress += step
                    update_status(curtask=curtask, progress=progress, log=log, taskid=taskid)
                    # give feedback to application server
                    conn.commit()

            # start a transaction TODO: co to kurwa jest, że tutaj mamy problem z transakcją???
            # conn.autocommit = False
            for j in jobs:
                if not cont:
                    log += 'Error: execution stopped.'
                    update_status_error(curtask=curtask, taskid=taskid, log=log)
                    conn.commit()
                    return
                # print ('deleting job:', j[0])
                dodeleteJob(conn=conn, cur=cur, name=j[0])
                progress += step
                log += 'Delete Job: "' + j[0] + '" from configuration.\n'
                update_status(curtask=curtask, progress=progress, log=log, taskid=taskid)
    except Exception as detail:
        conn.autocommit = True
        for j in jobs:
            enableJob(cur, j[0])
        enableClient(cur, name)
        log += 'Error: history and job deleting problem. Err=' + str(detail) + ' [lineno:' + \
               str(sys.exc_info()[-1].tb_lineno) + ']'
        update_status_error(curtask=curtask, log=log, taskid=taskid)
        return
    try:
        dodeleteClient(conn=conn, cur=cur, name=name)
        # print ('deleteing client:', name)
    except Exception as detail:
        conn.rollback()
        # back autocommit
        conn.autocommit = True
        for j in jobs:
            enableJob(cur, j[0])
        enableClient(cur, name)
        log += 'Error: configuration deleting problem. Err=' + str(detail) + ' [lineno:' + \
               str(sys.exc_info()[-1].tb_lineno) + ']'
        update_status_error(curtask=curtask, log=log, taskid=taskid)
        return
    progress += step
    log += 'Delete Client: "' + name + '" from configuration.'
    update_status_finish(curtask=curtask, log=log, taskid=taskid)
    conn.commit()


def detectlib(conn=None, cur=None, tasks=None, fg=False):
    global cont
    conn.autocommit = True
    if conn is None or tasks is None or cur is None:
        return
    # update status
    if fg:
        print('In procedure: detectlib')
    taskid = tasks['taskid']
    tapeid = tasks['params']
    log = 'Starting...\n'
    update_status(curtask=cur, taskid=taskid, log=log)
    log, drvconfig = detectlib_common(conn=conn, cur=cur, tasks=tasks, tapeid=tapeid, log=log, fg=fg)
    if len(drvconfig) > 0:
        log += 'Library detection success!'
        update_status_finish(curtask=cur, log=log, taskid=taskid)
    else:
        log += 'Library detection failed.'
        update_status_error(curtask=cur, log=log, taskid=taskid)


def rescanlib(conn=None, cur=None, tasks=None, fg=False):
    global cont
    conn.autocommit = True
    if conn is None or tasks is None or cur is None:
        return
    # update status
    if fg:
        print('In procedure: rescanlib')
    taskid = tasks['taskid']
    log = 'Starting...\n'
    update_status(curtask=cur, taskid=taskid, log=log)
    # disable all current drives
    params = ast.literal_eval(task['params'])
    tapeid = params['tapeid']
    devices = params['devices']
    storage = params['storage']
    # disable current devices to free up the resources
    for devres in devices:
        dev = devres['name']
        devindx = devres['driveindex']
        log += "Disabling and unmounting " + dev + "\n"
        update_status(curtask=cur, taskid=taskid, progress=2.0, log=log)
        statdevice = getStorageStatusDevice(storage=storage, device=dev)
        out = disableDevice(storage=storage, device=dev)
        if fg:
            print(out)
        if len(out) == 0:
            # error?
            log += out[0]

        slot = statdevice.get('Slot', None)
        if slot is not None:
            # we have to enable device for unmount
            enableDevice(storage=storage, device=dev)
            umountDevice(storage=storage, drive=devindx, slot=slot)
            disableDevice(storage=storage, device=dev)
    update_status(curtask=cur, taskid=taskid, progress=5.0, log=log)
    log, drvconfig = detectlib_common(conn=conn, cur=cur, tasks=tasks, tapeid=tapeid, log=log, fg=fg)
    for devres in devices:
        dev = devres['name']
        log += "Enabling " + dev + "\n"
        update_status(curtask=cur, taskid=taskid, progress=99.0, log=log)
        out = enableDevice(storage=storage, device=dev)
        if fg:
            print (out)
        if len(out) == 0:
            if not out[0].startswith('3002'):
                # error?
                log += out[0]
    if len(drvconfig) > 0:
        log += 'Library rescan success!'
        update_status_finish(curtask=cur, log=log, taskid=taskid)
    else:
        log += 'Library rescan failed.'
        update_status_error(curtask=cur, log=log, taskid=taskid)


def detectlib_common(conn=None, cur=None, tasks=None, progress=0, tapeid=None, log='', fg=False):
    global cont
    if fg:
        print ('In procedure: detectlib_common')
    taskid = tasks['taskid']
    # prepare required variables
    if tapeid is None or not tapeid.startswith('tape['):
        if fg:
            print ('No valid library to detect!')
        log = 'No valid library to detect! All I found: ' + str(tapeid) + "\n"
        update_status_error(curtask=cur, taskid=taskid, log=log)
    else:
        step = 12.5
        libs = detectlibs()
        dev = ''
        for d in libs:
            dt = 'tape' + d['id']
            if dt == tapeid:
                dev = d['dev']
                if fg:
                    print ('Found dev: ' + str(dev))
                log += 'Found dev: ' + str(dev) + "\n"
                break
        if os.path.exists(dev):
            if os.access(dev, os.W_OK):
                # 1
                log += 'Unloading all tapes\n'
                progress += 5.0
                update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                lib = mtx_statusinfo(dev)
                log += 'mtx_statusinfo executed\n'
                progress = step
                update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                # 2
                drvstep = len(lib['Drives'])
                for drv in lib['Drives']:
                    if drv['Loaded'] is not None:
                        drvindx = drv['DriveIndex']
                        if fg:
                            print ('Unloading tape: ' + str(drvindx))
                        log += 'Unloading tape: ' + str(drvindx) + '\n'
                        update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                        mtx_unload(dev=dev, drive=drvindx)
                        log += 'Unloading done.\n'
                        progress += step / drvstep
                    update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                # 3
                log += 'Getting tapedrv list\n'
                progress = step * 2
                update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                tapes = gettapedrvlist()
                tapeslist = []
                if fg:
                    print ('All tapes', tapes)
                # 4
                log += 'Selecting tapes\n'
                progress = step * 3
                update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                for tape in tapes:
                    stat = mt_status(tape['dev'])
                    if fg:
                        print ("mt status: " + str(stat))
                    if stat['status'] is None:
                        log += stat['log']
                        update_status_error(curtask=cur, taskid=taskid, log=log)
                        conn.commit()
                        return log, []
                    if not stat['status']:
                        tapeslist.append(tape)
                if fg:
                    print ("Selected tapes", tapeslist)
                # 5
                log += 'Getting library status\n'
                progress = step * 4
                update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                lib = mtx_statusinfo(dev)
                if fg:
                    print ("LIB status:", lib)
                slot = 0
                # 6
                log += 'Selecting library slot to test\n'
                progress = step * 5
                update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                for sl in lib['Slots']:
                    if sl['Loaded'] is not None:
                        slot = sl['Slot']
                        if fg:
                            print ("selected slot", slot)
                        break
                if slot == 0:
                    # Error
                    if fg:
                        print('No available volumes in library found!')
                    log += 'No available volumes in library found!\n'
                    update_status_error(curtask=cur, taskid=taskid, log=log)
                else:
                    drvconfig = []
                    # 7,8
                    log += 'Mapping tape drives to library index\n'
                    progress = step * 6
                    update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                    for drv in lib['Drives']:
                        drvindx = drv['DriveIndex']
                        if fg:
                            print ("test drvindx", drvindx)
                        mtx_load(dev=dev, drive=drvindx, slot=slot)
                        log += 'Testing tape drive: ' + str(drvindx) + '\n'
                        progress += drvstep
                        update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                        for tape in tapeslist:
                            stat = mt_status(tape['dev'])
                            if fg:
                                print ("load status", str(stat))
                            if stat['status'] is None:
                                log += stat['log']
                                update_status_error(curtask=cur, taskid=taskid, log=log)
                                conn.commit()
                                return log, []
                            if stat:
                                if fg:
                                    print ("Got it!", drv, tape)
                                drvconfig.append({
                                    'DriveIndex': drvindx,
                                    'Tape': tape,
                                })
                                break
                        mtx_unload(dev=dev, drive=drvindx)
                    if fg:
                        print (drvconfig)
                    update_status_out(curtask=cur, outlog=str(drvconfig), taskid=taskid)
                    return log, drvconfig
            else:
                print("Permission denied: " + str(dev))
                log += "Permission denied: " + str(dev) + "\n"
                update_status_error(curtask=cur, taskid=taskid, log=log)
        else:
            print('No valid device for library found!')
            log += 'No valid device for library found! dev=' + str(dev) + "\n"
            update_status_error(curtask=cur, taskid=taskid, log=log)
    conn.commit()
    return log, []


def labeltapes(conn=None, cur=None, tasks=None, fg=False):
    global cont
    conn.autocommit = True
    if conn is None or tasks is None or cur is None:
        return
    # update status
    if fg:
        print ('In procedure: labeltapes')
    taskid = tasks['taskid']
    log = 'Starting...\n'
    update_status(curtask=cur, taskid=taskid)
    # prepare required variables
    storage = tasks['params']
    if storage is None:
        if fg:
            print ('No valid storage to label!')
        log += 'No valid storage to label! All I found: ' + str(storage) + '\n'
        update_status_error(curtask=cur, taskid=taskid, log=log)
    else:
        volumes = doUpdateslots(storage)
        if fg:
            print (volumes)
        volsnr = len(volumes)
        step = 100.0 / (volsnr + 1)
        progress = step
        log += 'Getting slots information from storage\n'
        update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
        if volsnr > 0:
            for vol in volumes:
                volname = vol['name']
                if not volname.startswith('CLN'):
                    volslot = vol['slot']
                    drive = getStorageIdleDevice(storage=storage)
                    log += 'Label volume: ' + str(volname) + ' drive: ' + str(drive) + ' slot: ' + str(volslot) + '\n'
                    update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
                    (status, out) = doLabel(storage=storage, volume=volname, drive=drive, slot=volslot)
                    if fg:
                        print (status, out)
                    if status:
                        log += out + '\n'
                    else:
                        log += 'Label ERROR!\n' + str(out) + '\n'
                        update_status_error(curtask=cur, taskid=taskid, log=log)
                        return
                    umountDevice(storage=storage, drive=drive, slot=volslot)
                else:
                    if fg:
                        print ("cleaning tape...")
                    log += 'Skipping cleaning tape: ' + str(volname) + '\n'
                progress += step
                update_status(curtask=cur, taskid=taskid, progress=progress, log=log)
            log += 'Task finish.\n'
        else:
            if fg:
                print('No volumes to label!')
            log += 'No volumes to label!' + '\n'
        update_status_finish(curtask=cur, taskid=taskid, log=log)
    conn.commit()


def mainloop(fg=False):
    if fg:
        print ('Entering the mainloop...')
    conn = psycopg2.connect("dbname=" + dbname + " user=" + dbuser + " password=" + dbpass + " host=" + dbhost +
                            " port=" + dbport)
    # prepare cursors
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curtask = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # update task tpid
    tpid = os.getpid()
    cur.execute("update tasks_tasks set tpid=%s where taskid=%s", (tpid, task['taskid'],))
    conn.commit()
    # we support a following tasks
    if task['proc'] == 1:
        if fg:
            print (' > Proc delete Job')
        delete_job(conn=conn, cur=cur, curtask=curtask, tasks=task)
        directorreload()
    if task['proc'] == 2:
        if fg:
            print(' > Proc delete Client')
        delete_client(conn=conn, cur=cur, curtask=curtask, tasks=task)
        directorreload()
    if task['proc'] == 3:
        if fg:
            print(' > Proc detect library')
        detectlib(conn=conn, cur=cur, tasks=task, fg=fg)
    if task['proc'] == 4:
        if fg:
            print(' > Proc label tapes')
        labeltapes(conn=conn, cur=cur, tasks=task, fg=fg)
    if task['proc'] == 5:
        if fg:
            print(' > Proc rescan library')
        rescanlib(conn=conn, cur=cur, tasks=task, fg=fg)
    conn.close()
    sys.exit(0)


class IBTasksd(Daemon):
    def run(self):
        mainloop()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if '-h' == sys.argv[1]:
            printhelp()
            sys.exit(0)
        else:
            try:
                taskid = int(sys.argv[1])
            except ValueError:
                print ('Invalid task number!')
                sys.exit(2)
            task = maininit(taskid=taskid)
            if task is not None:
                daemon = IBTasksd('/tmp/ibadtasksd.' + str(taskid) + '.pid')
                daemon.start()
    elif len(sys.argv) == 3:
        if '-f' == sys.argv[1]:
            print ('Foreground mode enabled.')
            try:
                taskid = int(sys.argv[2])
            except ValueError:
                print ('Invalid task number!')
                sys.exit(2)
            task = maininit(taskid=taskid, fg=True)
            if task is not None:
                mainloop(fg=True)
            else:
                print ('taskid finished or not found!')
                sys.exit(4)
        # elif 'stop' == sys.argv[1]:
        #    daemon.stop()
    else:
        printhelp()
        sys.exit(2)
    sys.exit(0)
