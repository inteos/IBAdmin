#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import sys
import signal
import psycopg2
import psycopg2.extras


def printhelp():
    print("Required parameter is:")
    print(" <taskid>    starts the tasks daemon for <taskid>.")
    print("Optional parameter is:")
    print(" -h          Print this help.")
    print()


sys.path.append('/opt/ibadmin')
from libs.daemon import Daemon
from libs.bconsole import doDeleteJobid, directorreload
from ibadmin.settings import DATABASES


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


def maininit(taskid=None):
    if taskid is None:
        return None
    conn = psycopg2.connect("dbname=" + dbname + " user=" + dbuser + " password=" + dbpass + " host=" + dbhost + " port=" + dbport)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("select count(1) from tasks_tasks;")
    except:
        print ("No tasks tables found or DB error")
        sys.exit(3)
    cur.execute("select * from tasks_tasks where status='N' and taskid=%s;", (taskid,))
    row = cur.fetchone()
    if row is None:
        return None
    cur.close()
    conn.close()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return row


def update_status(curtask=None, taskid=0, progress=0, log='', status='R'):
    curtask.execute("update tasks_tasks set progress=%s, log=%s, status=%s where taskid=%s",
                    (int(round(progress)), log, status, taskid,))


def update_status_error(curtask=None, taskid=0, log=''):
    curtask.execute("update tasks_tasks set log=%s, status='E', endtime=now() where taskid=%s",
                    (log, taskid,))


def update_status_finish(curtask=None, taskid=0, progress=100, log=''):
    curtask.execute("update tasks_tasks set progress=%s, log=%s, status='F', endtime=now() where taskid=%s",
                    (int(round(progress)), log, taskid,))


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


def mainloop():
    conn = psycopg2.connect("dbname=" + dbname + " user=" + dbuser + " password=" + dbpass + " host=" + dbhost + " port=" + dbport)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curtask = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # we support a following tasks
    if task['proc'] == 1:
        delete_job(conn=conn, cur=cur, curtask=curtask, tasks=task)
    if task['proc'] == 2:
        delete_client(conn=conn, cur=cur, curtask=curtask, tasks=task)
    #if task['proc'] == 3:
    #    delete_job(conn=conn, cur=cur, curtask=curtask, tasks=task)
    directorreload()
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
                daemon = IBTasksd('/tmp/ibadtasksd.pid')
                daemon.start()
    elif len(sys.argv) == 3:
        if '-f' == sys.argv[1]:
            try:
                taskid = int(sys.argv[2])
            except ValueError:
                print ('Invalid task number!')
                sys.exit(2)
            task = maininit(taskid=taskid)
            if task is not None:
                mainloop()
        # elif 'stop' == sys.argv[1]:
        #    daemon.stop()
    else:
        printhelp()
        sys.exit(2)
    sys.exit(0)
