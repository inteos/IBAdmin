# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from subprocess import Popen, PIPE
import re
import utils


def bconsolecommand(cmd, api=False, timeout=True):
    """
    *gui on
    *.api=1
    """
    if timeout:
        bconsole = Popen(["/opt/bacula/bin/bconsole", "-u", "5"], stdin=PIPE, stdout=PIPE)
    else:
        bconsole = Popen(["/opt/bacula/bin/bconsole"], stdin=PIPE, stdout=PIPE)
    bconsole.stdin.write("gui on\n")
    if api:
        bconsole.stdin.write(".api=1\n")
    bcmd = cmd + '\n'
    bconsole.stdin.write(bcmd.encode('utf-8'))
    bconsole.stdin.close()
    out = bconsole.stdout.read().decode('utf-8')
    bconsole.wait()
    lines = out.splitlines()
    return lines


def getbconsolecommand(cmd, api=False):
    bconsole = bconsolecommand(cmd, api)
    out = []
    for line in bconsole:
        line.replace(',', '')
        newline = ','.join(line.split())
        out.append(newline)
    return out


def getbconsolefilter(cmd, pattern, api=False):
    bconsole = bconsolecommand(cmd, api)
    out = []
    for line in bconsole:
        if pattern in line:
            line.replace(',', '')
            newline = ','.join(line.split())
            out.append(newline)
    return out


def getClientrunningJobid(client):
    """ chwilowo nie używane """
    bconsole = bconsolecommand(".status client=\"" + client + "\" running")[7:]
    jobs = []
    for line in bconsole:
        if line.startswith('JobId='):
            jobid = line.split('=')
            jobs.append(jobid[1])
    return jobs


def getClientrunningJobs(client):
    """
    *.status client=sun running
    Connecting to Client sun at sun.korzeniewski.net:9102

    JobId=47119
    Job=InteosBackup.2016-11-30_11.00.00_16
    VSS=0
    Level=I
    Type=I
    Status=C
    StartTime_epoch=1480500002
    StartTime=2016-11-30 11:00:02
    JobFiles=0
    JobBytes=0
    Bytes/sec=0
    Errors=0
    Bwlimit=0
    ReadBytes=0
    Files Examined=0
    SDReadSeqNo=5
    fd=6
    SDtls=0


    JobId=47120
    Job=SunSystemJob.2016-11-30_11.58.18_19
    VSS=0
    Level=F
    Type=B
    Status=R
    StartTime_epoch=1480503500
    StartTime=2016-11-30 11:58:20
    JobFiles=4793
    JobBytes=948871
    Bytes/sec=33888
    Errors=0
    Bwlimit=0
    ReadBytes=121288127
    Files Examined=4793
    Processing file=/var/lib/dpkg/info/libdrm-radeon1:amd64.shlibs
    SDReadSeqNo=7
    fd=9
    SDtls=0


    DirectorConnected_epoch=1480503528
    DirectorConnected=2016-11-30 11:58:48
    DirTLS=0
    """
    bconsole = bconsolecommand(".status client=\"" + client + "\" running")[7:]
    jobparams = {}
    jobs = []
    next = 1
    for line in bconsole:
        if line.startswith('Dir'):
            continue
        if line != '':
            # line = line.replace(' ', '')
            line = line.replace('Bytes/sec', 'Bytessec')
            (name, value) = line.split('=')
            name = name.replace(' ', '')
            if name == 'Type':
                name = 'JobType'
            jobparams[name] = value
            next = 0
        elif next == 0:
            next = 1
            jobs.append(jobparams)
            jobparams = {}
    return jobs


def getClientStatus(client='ibadmin'):
    """
    *.status client=test header
    Connecting to Client test at 192.168.2.33:9102
    header:
    name=ibadmin
    version=8.4.14 (20 June 2016)
    uname=x86_64-redhat-linux-gnu-bacula-enterprise redhat Enterprise release
    started_epoch=1482864314
    started=2016-12-27 19:45:14
    jobs_run=26
    jobs_running=0
    winver=
    debug=0
    trace=0
    bwlimit=0
    plugins=bpipe-fd.so
    """
    bconsole = bconsolecommand(".status client=\"" + client + "\" header")[7:]
    if len(bconsole) > 0:
        out = {}
        for data in bconsole:
            if data == '':
                continue
            (name, value) = data.split('=')
            out[name] = value
        return out
    else:
        return None


def disableDevice(storage='ibadmin', device='File0'):
    """
    *disable storage=devel1-File1 device=File1Dev1 drive=0
    3002 Device ""File1Dev1" (/home/backup)" disabled.
    """
    out = getbconsolefilter("disable storage=\"" + storage + "\" device=\"" + device + "\" drive=0", 'disabled')
    return out


def enableDevice(storage='ibadmin', device='File0'):
    """
    *disable storage=devel1-File1 device=File1Dev1 drive=0
    3002 Device ""File1Dev1" (/home/backup)" disabled.
    """
    out = getbconsolefilter("enable storage=\"" + storage + "\" device=\"" + device + "\" drive=0", 'enabled')
    return out


def getStorageStatus(storage='ibadmin'):
    """
    *.status storage=ibadmin-File1 header
    header:
    name=ibadmin
    version=8.6.12 (09 January 2017)
    uname=x86_64-redhat-linux-gnu-bacula-enterprise redhat Enterprise release
    started_epoch=1490205739
    started=2017-03-22 19:02:19
    jobs_run=27
    jobs_running=0
    ndevices=10
    nautochgr=1
    plugins=dedup-sd.so
    """
    bconsole = bconsolecommand(".status storage=\"" + storage + "\" header", api=True)[7:]
    if len(bconsole) > 0:
        out = {}
        for data in bconsole:
            if data == '':
                continue
            (name, value) = data.split('=')
            out[name] = value
        return out
    else:
        return None


def getStorageStatusDevice(storage='ibadmin', device='File0'):
    """
    *.status storage=sun-dedup-sd devices device=DedupStorageDrv3
    
    Device dedup data is "DedupStorageDrv3" (/backup/dedupvolumes) mounted with:
        Volume:      Vol7726
        Pool:        WindowsUserIncrPool
        Media type:  DedupVolume
        Drive 3 is not loaded.
        Total Bytes=36,896,559 Blocks=563 Bytes/block=65,535
        Positioned at File=0 Block=36,896,558
        Available Space=1.963 TB

    Device file is "File1Dev0" (/home/backup) mounted with:
        Volume:      DiskVol0003
        Pool:        Default
        Media type:  File1
        Drive 0 is not loaded.
        Total Bytes=2,185,246,756 Blocks=33,876 Bytes/block=64,507
        Positioned at File=0 Block=2,185,246,755
        Available Space=41.67 GB

    Device file: "File1Dev1" (/home/backup) is not open.
        Drive 1 is not loaded.
        Available Space=41.67 GB

    Device File: "File1Dev7" (/home/backup) is not open.
       Device is disabled. User command.
       Drive 7 is not loaded.
       Available Space=472.5 GB
    """
    bconsole = bconsolecommand(".status storage=\"" + storage + "\" devices device=\"" + device + "\"")[7:]
    out = {'Status': 'Running'}
    if len(bconsole) > 0:
        for line in bconsole:
            if line == '':
                continue
            if 'is not open' in line:
                out['Status'] = 'Idle'
            if 'Device is disabled' in line:
                out['Status'] = 'Disabled'
            if 'Available Space' in line:
                out['AvailableSpace'] = line.split('=')[1]
            if 'Volume:' in line:
                out['Volume'] = line.split(':')[1].lstrip()
            if 'Pool:' in line:
                out['Pool'] = line.split(':')[1].lstrip()
            if 'Media type:' in line:
                out['MediaType'] = line.split(':')[1].lstrip()
            if 'Total Bytes=' in line:
                out['Size'] = line.split()[1].split('=')[1].replace(',', '')
    return out


def getStorageStatusDedup(storage='ibadmin'):
    """
    *.status storage=sun-dedup-autochanger dedupengine
    Connecting to Storage daemon sun-dedup-autochanger at 192.168.0.31:9103
    Dedupengine status:
     DDE: hash_count=60042 ref_count=1451510 ref_size=45.74 GB
        ref_ratio=24.17 size_ratio=37.01 dde_errors=0
     Config: bnum=33554393 bmin=33554393 bmax=0 mlock_strategy=1 mlocked=255MB mlock_max=0MB
     HolePunching: hole_size=4096 KB
     Containers: chunk_allocated=60042 chunk_used=60042
        disk_space_allocated=1.235 GB disk_space_used=1.235 GB containers_errors=0
     Vacuum: last_run="28-Jun-17 05:00" duration=2s ref_count=1367698 ref_size=43.15 GB
        vacuum_errors=0 orphan_addr=0 bad_ref=0 bad_addr=0
     Stats: read_chunk=0 query_hash=969614 new_hash=1300 calc_hash=956145
     [1]   1k filesize=9.216 KB/9.216 KB usage=5/5/524288 100% ****************************************
     [2]   2k filesize=15.62 MB/15.62 MB usage=7627/7627/524288 100% ****************************************
     [3]   3k filesize=16.99 MB/16.99 MB usage=5532/5532/524288 100% ****************************************
     [4]   4k filesize=16.66 MB/16.66 MB usage=4068/4068/524288 100% ****************************************
     [5]   5k filesize=14.30 MB/14.30 MB usage=2794/2794/524288 100% ****************************************
     [6]   6k filesize=14.96 MB/14.96 MB usage=2435/2435/524288 100% ****************************************
     [7]   7k filesize=16.57 MB/16.57 MB usage=2312/2312/524288 100% ****************************************
     [8]   8k filesize=16.20 MB/16.20 MB usage=1978/1978/524288 100% ****************************************
     [9]   9k filesize=14.13 MB/14.13 MB usage=1533/1533/524288 100% ****************************************
     [10] 10k filesize=13.70 MB/13.70 MB usage=1338/1338/524288 100% ****************************************
     [11] 11k filesize=13.26 MB/13.26 MB usage=1177/1177/524288 100% ****************************************
     [12] 12k filesize=12.43 MB/12.43 MB usage=1012/1012/524288 100% ****************************************
     [13] 13k filesize=12.58 MB/12.58 MB usage=945/945/524288 100% ****************************************
     [14] 14k filesize=13.04 MB/13.04 MB usage=910/910/524288 100% ****************************************
     [15] 15k filesize=10.94 MB/10.94 MB usage=712/712/524288 100% ****************************************
     [16] 16k filesize=12.22 MB/12.22 MB usage=746/746/524288 100% ****************************************
     [17] 17k filesize=19.60 MB/19.60 MB usage=1126/1126/524288 100% ****************************************
     [18] 18k filesize=12.20 MB/12.20 MB usage=662/662/524288 100% ****************************************
     [19] 19k filesize=12.59 MB/12.59 MB usage=647/647/524288 100% ****************************************
     [20] 20k filesize=12.86 MB/12.86 MB usage=628/628/524288 100% ****************************************
     [21] 21k filesize=17.59 MB/17.59 MB usage=818/818/524288 100% ****************************************
     [22] 22k filesize=13.52 MB/13.52 MB usage=600/600/524288 100% ****************************************
     [23] 23k filesize=14.51 MB/14.51 MB usage=616/616/524288 100% ****************************************
     [24] 24k filesize=17.55 MB/17.55 MB usage=714/714/524288 100% ****************************************
     [25] 25k filesize=15.67 MB/15.67 MB usage=612/612/524288 100% ****************************************
     [26] 26k filesize=16.21 MB/16.21 MB usage=609/609/524288 100% ****************************************
     [27] 27k filesize=16.37 MB/16.37 MB usage=592/592/524288 100% ****************************************
     [28] 28k filesize=17.46 MB/17.46 MB usage=609/609/524288 100% ****************************************
     [29] 29k filesize=15.97 MB/15.97 MB usage=538/538/524288 100% ****************************************
     [30] 30k filesize=18.95 MB/18.95 MB usage=617/617/524288 100% ****************************************
     [31] 31k filesize=16.70 MB/16.70 MB usage=526/526/524288 100% ****************************************
     [32] 32k filesize=15.27 MB/15.27 MB usage=466/466/524288 100% ****************************************
     [33] 33k filesize=19.56 MB/19.56 MB usage=579/579/524288 100% ****************************************
     [34] 34k filesize=19.95 MB/19.95 MB usage=573/573/524288 100% ****************************************
     [35] 35k filesize=17.09 MB/17.09 MB usage=477/477/524288 100% ****************************************
     [36] 36k filesize=16.51 MB/16.51 MB usage=448/448/524288 100% ****************************************
     [37] 37k filesize=21.82 MB/21.82 MB usage=576/576/524288 100% ****************************************
     [38] 38k filesize=18.21 MB/18.21 MB usage=468/468/524288 100% ****************************************
     [39] 39k filesize=17.77 MB/17.77 MB usage=445/445/524288 100% ****************************************
     [40] 40k filesize=17.12 MB/17.12 MB usage=418/418/524288 100% ****************************************
     [41] 41k filesize=19.06 MB/19.06 MB usage=454/454/524288 100% ****************************************
     [42] 42k filesize=16.64 MB/16.64 MB usage=387/387/524288 100% ****************************************
     [43] 43k filesize=17.88 MB/17.88 MB usage=406/406/524288 100% ****************************************
     [44] 44k filesize=17.43 MB/17.43 MB usage=387/387/524288 100% ****************************************
     [45] 45k filesize=18.98 MB/18.98 MB usage=412/412/524288 100% ****************************************
     [46] 46k filesize=14.46 MB/14.46 MB usage=307/307/524288 100% ****************************************
     [47] 47k filesize=14.00 MB/14.00 MB usage=291/291/524288 100% ****************************************
     [48] 48k filesize=12.78 MB/12.78 MB usage=260/260/524288 100% ****************************************
     [49] 49k filesize=11.54 MB/11.54 MB usage=230/230/524288 100% ****************************************
     [50] 50k filesize=9.475 MB/9.475 MB usage=185/185/524288 100% ****************************************
     [51] 51k filesize=8.255 MB/8.255 MB usage=158/158/524288 100% ****************************************
     [52] 52k filesize=6.126 MB/6.126 MB usage=115/115/524288 100% ****************************************
     [53] 53k filesize=4.888 MB/4.888 MB usage=90/90/524288 100% ****************************************
     [54] 54k filesize=5.533 MB/5.533 MB usage=100/100/524288 100% ****************************************
     [55] 55k filesize=8.451 MB/8.451 MB usage=150/150/524288 100% ****************************************
     [56] 56k filesize=6.196 MB/6.196 MB usage=108/108/524288 100% ****************************************
     [57] 57k filesize=10.97 MB/10.97 MB usage=188/188/524288 100% ****************************************
     [58] 58k filesize=9.090 MB/9.090 MB usage=153/153/524288 100% ****************************************
     [59] 59k filesize=4.776 MB/4.776 MB usage=79/79/524288 100% ****************************************
     [60] 60k filesize=3.198 MB/3.198 MB usage=52/52/524288 100% ****************************************
     [61] 61k filesize=3.689 MB/3.689 MB usage=59/59/524288 100% ****************************************
     [62] 62k filesize=4.765 MB/4.765 MB usage=75/75/524288 100% ****************************************
     [63] 63k filesize=6.196 MB/6.196 MB usage=96/96/524288 100% ****************************************
     [64] 64k filesize=21.49 MB/21.49 MB usage=328/328/524288 100% ****************************************
     [65] 65k filesize=365.0 MB/365.0 MB usage=5484/5484/524288 100% ****************************************
    ====
    # 40 chars=100% container file
    """
    bconsole = bconsolecommand(".status storage=\"" + storage + "\" dedupengine", timeout=False)[7:-2]
    outengine = bconsole[:9]
    outcontainers = bconsole[10:]
    print (outcontainers)
    dedupengine = {}
    for dep in outengine:
        scan_data = re.search(r'disk_space_allocated=(.*) (..) disk_space_used=(.*) (..) containers_errors=(.*)', dep)
        if scan_data is not None:
            dedupengine['disk_space_allocated'] = scan_data.group(1) + ' ' + scan_data.group(2)
            dedupengine['disk_space_used'] = scan_data.group(3) + ' ' + scan_data.group(4)
            dedupengine['containers_errors'] = scan_data.group(5)
            continue
        scan_data = re.search(r'DDE: hash_count=\d+ ref_count=(\d+) ref_size=(.*) (.*)', dep)
        if scan_data is not None:
            dedupengine['ref_count'] = scan_data.group(1)
            dedupengine['ref_size'] = scan_data.group(2) + ' ' + scan_data.group(3)
            continue
        scan_data = re.search(r'size_ratio=(.*) dde_errors=(\d+)', dep)
        if scan_data is not None:
            dedupengine['size_ratio'] = scan_data.group(1)
            dedupengine['dde_errors'] = scan_data.group(2)
            continue
        scan_data = re.search(r'chunk_allocated=(\d+) chunk_used=(\d+)', dep)
        if scan_data is not None:
            dedupengine['chunk_allocated'] = scan_data.group(1)
            dedupengine['chunk_used'] = scan_data.group(2)
            continue
        scan_data = re.search(r'Vacuum: last_run="(.*)" ', dep)
        if scan_data is not None:
            dedupengine['vacuum_last_run'] = scan_data.group(1)
            continue
    dedupcontainers = []
    pattern = re.compile(r' \[\d+\]\s+(\d+k) filesize=(.*)/(.*) usage=\d+/\d+/\d+ (.*) (........................................)')
    for con in outcontainers:
        scan_data = pattern.match(con)
        dedupcontainers.append({
            'block_size': scan_data.group(1),
            'used_size': scan_data.group(2),
            'allocated_size': scan_data.group(3),
            'used_percent': scan_data.group(4).replace('%', ''),
            'fsm': scan_data.group(5),
        })
    return dedupengine, dedupcontainers


def getClientJobiddata(client, jobid):
    bconsole = bconsolecommand(".status client=\"" + client + "\" running")[7:]
    jobparams = {}
    jobs = []
    nextjob = 1
    for line in bconsole:
        if line != '':
            # print ":"+line+":"
            line = line.replace(' ', '')
            line = line.replace('Bytes/sec', 'Bytessec')
            # print ":" + line + ":"
            (name, value) = line.split('=')
            jobparams[name] = value
            nextjob = 0
        elif nextjob == 0:
            nextjob = 1
            if 'JobId' in jobparams and int(jobparams['JobId']) == int(jobid):
                jobs.append(jobparams)
                break
            jobparams = {}
    return jobs


def getrunningjobs():
    """ chwilowo nie używane """
    jobs = getbconsolefilter('.status dir running', 'is running')
    # jobs = ['46850,Back,Full,20,32.18,M,SaturnJobISOImages,is,running', '46851,Back,Full,6,9.234,M,SaturnJobVMImages,is,running', '46852,Back,Full,0,0,SaturnSystemJob,is,running']
    out = []
    for job in jobs:
        jobparam = job.split(',')
        if jobparam[4] == '0':
            jobparam.insert(5, 'B')
        del jobparam[7:]
        out.append({
            'JobId': jobparam[0],
            'Type': jobparam[1],
            'Level': jobparam[2],
            'Files': jobparam[3],
            'Bytes': countbytes(jobparam[4], jobparam[5]),
            'Name': jobparam[6]
        })
    return out


def doUpdateVolumeUsed(name):
    out = getbconsolefilter("update volume=\"" + name + "\" volstatus=Used", 'New Volume status is:')
    return out


def doUpdateVolumeAppend(name):
    out = getbconsolefilter("update volume=\"" + name + "\" volstatus=Append", 'New Volume status is:')
    return out


def doPurgeVolume(name):
    out = getbconsolefilter("purge volume=\"" + name + "\"", 'Marking it purged.')
    out2 = getbconsolefilter("truncate volume=\"" + name + "\" allpools", 'has been truncated')
    return out + out2


def doDeleteVolume(name):
    out = getbconsolefilter("delete volume=\"" + name + "\" yes", 'This command will delete volume')
    return out


def doDeleteJobid(jobid):
    """
    
    :param jobid: jobid to delete by Director
    :return: string from bconsole output
    """
    out = getbconsolefilter("delete jobid=" + str(jobid) + " yes", 'records deleted from the catalog.')
    return out


def doJobrun(name):
    """
    Run a job by Director.
    :param name: name of the Job to run
    :return: string from queued a job to run, including jobid [u'Job,queued.,JobId=327']
    """
    out = getbconsolefilter('run job=\"' + name + '\" yes', 'Job queued.')
    return out


def doRestartJobid(jobid):
    """
    *restart failed jobid=1
    Job queued. JobId=3
    
    :param jobid: 
    :return: 
    """
    out = getbconsolefilter("restart failed jobid=" + str(jobid), 'Job queued.')
    return out


def doCancelJobid(jobid):
    """
    *cancel jobid=90 yes
    2001 Job "systemowy.2017-04-30_17.00.37_55" marked to be canceled.
    3000 JobId=90 Job="systemowy.2017-04-30_17.00.37_55" marked to be canceled.

    :param jobid: 
    :return: 
    """
    out = getbconsolefilter("cancel jobid=" + str(jobid) + " yes", 'marked to be canceled.')
    return out


def doStopJobid(jobid):
    """
    *stop jobid=104
    2001 Job "systemowy.2017-05-01_21.22.47_48" marked to be stopped.
    3000 JobId=104 Job="systemowy.2017-05-01_21.22.47_48" marked to be stopped.

    :param jobid: 
    :return: 
    """
    out = getbconsolefilter("stop jobid=" + str(jobid), 'marked to be stopped.')
    return out


def directorreload():
    """
    Make Director configuration reload
    :return: None when reload completed without problem, errors string otherwise
    """
    out = bconsolecommand("reload")[4:]
    if len(out) > 0:
        return out
    return None


def bvfs_get_jobids(jobid):
    jobidslist = bconsolecommand(".bvfs_get_jobids jobid=" + str(jobid), timeout=False)[-1]
    if len(jobidslist) > 0:
        return jobidslist
    else:
        return None


def bvfs_update(jobids):
    out = bconsolecommand(".bvfs_update jobid=" + str(jobids), timeout=False)[5:]
    if len(out) > 0:
        return out
    return None


def bvfs_lsdirs_path(path, jobids):
    out = bconsolecommand('.bvfs_lsdirs path="' + str(path) + '" jobid=' + str(jobids), timeout=False)[6:]
    if len(out) > 0:
        return out
    return None


def bvfs_lsfiles_path(path, jobids):
    out = bconsolecommand('.bvfs_lsfiles path="' + str(path) + '" jobid=' + str(jobids), timeout=False)[6:]
    if len(out) > 0:
        return out
    return None


def bvfs_lsdirs_pathid(pathid, jobids):
    out = bconsolecommand('.bvfs_lsdirs pathid="' + str(pathid) + '" jobid=' + str(jobids), timeout=False)[6:]
    if len(out) > 0:
        return out
    return None


def bvfs_lsfiles_pathid(pathid, jobids):
    out = bconsolecommand('.bvfs_lsfiles pathid="' + str(pathid) + '" jobid=' + str(jobids), timeout=False)[6:]
    if len(out) > 0:
        return out
    return None


def bvfs_lsdirs_root(jobids):
    return bvfs_lsdirs_path('""', jobids)


def bvfs_restore_prepare(pathids, fileids, jobids, pathtable):      # OK
    pathidstr = ''
    if pathids is not None and pathids != '':
        pathidstr = ' dirid=' + str(pathids)
    fileidstr = ''
    if fileids is not None and fileids != '':
        fileidstr = ' fileid=' + str(fileids)
    out = bconsolecommand('.bvfs_restore' + fileidstr + pathidstr + ' jobid=' + str(jobids) + ' path=' + str(pathtable), timeout=False)[-1]
    if out != 'OK':
        return out
    return True


def bvfs_restore_cleanup(pathtable='b2111'):
    out = bconsolecommand('.bvfs_cleanup path=' + str(pathtable))[6:]
    if len(out) > 0:
        return out
    return True


def doRestore(client, restoreclient, where=None, replace='always', comment=None, pathtable='b2111'):
    wherestr = ''
    if where is not None and where != '':
        wherestr = ' where="' + where + '"'
    commentstr = ''
    if comment is not None and comment != '':
        commentstr = ' comment="' + comment + '"'
    cmd = 'restore client=' + str(client) + ' restoreclient=' + str(restoreclient) + ' file=?' + str(pathtable) + \
          ' replace=' + replace + wherestr + commentstr + ' yes'
    out = bconsolecommand(cmd, timeout=False)
    return out


def getBackupVersion():
    return getbconsolefilter('version', 'bacula-enterprise')
