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
SQL = {}


def setparam(cur, param, types, descr, unit, sql, chart, display, color, box):
    SQL[param] = sql or ''
    parid = lib.getsetparam(cur, param, types, descr, unit, chart, display, color, box)
    PARAMS[param] = parid
    lib.setstat(cur, parid)


# TODO:
"""
*.status storage=sun-dedup-sd running
Connecting to Storage daemon sun-dedup-sd at 192.168.0.31:9103

Running Jobs:
Writing: Full Backup job SunSystemJob JobId=47978 Volume="Vol9754"
    pool="LinuxSystemFullPool" device="DedupStorageDrv6" (/backup/dedupvolumes)
    spooling=0 despooling=0 despool_wait=0
    Files=1,265,801 Bytes=1,057,544,224 AveBytes/sec=27,745 LastBytes/sec=20,821
    FDReadSeqNo=7 in_msg=7 out_msg=32227958 fd=93
Writing: Incremental Backup job InteosBackup JobId=47986 Volume="Vol9761"
    pool="InteosPool" device="DedupStorageDrv1" (/backup/dedupvolumes)
    spooling=0 despooling=0 despool_wait=0
    Files=0 Bytes=0 AveBytes/sec=0 LastBytes/sec=0
    FDReadSeqNo=6 in_msg=5 out_msg=5 fd=81
====

*.status storage=sun-dedup-autochanger dedupengine
Connecting to Storage daemon sun-dedup-autochanger at 192.168.0.31:9103
Dedupengine status:
 DDE: hash_count=93021707 ref_count=859027623 ref_size=54.50 TB
    ref_ratio=9.18 size_ratio=11.29 dde_errors=0
 Config: bnum=125829103 bmin=33554393 bmax=0 mlock_strategy=1 mlocked=0MB mlock_max=0MB
 HolePunching: hole_size=4096 KB
 Containers: chunk_allocated=107958042 chunk_used=93533748
    disk_space_allocated=5.165 TB disk_space_used=4.828 TB containers_errors=0
 Vacuum: last_run="07-kwi-17 16:21" duration=751s ref_count=823879513 ref_size=52.25 TB
    vacuum_errors=0 orphan_addr=47029 bad_ref=0 bad_addr=0
 Stats: read_chunk=0 query_hash=185118025 new_hash=7854688 calc_hash=43689534
 [1]  filesize=460.5 MB/539.0 MB usage=449707/526437/1048576  85% *****************************6****4...00
 [2]  filesize=1.881 GB/2.411 GB usage=918631/1177557/1572864  78% ******************9988532021002645****99
 [3]  filesize=2.032 GB/2.352 GB usage=661520/765628/1048576  86% *****************9872879996434236**9**9*
 [4]  filesize=2.949 GB/4.298 GB usage=720113/1049505/1572864  68% ***8***********49896322141299**9*5.....1
 [5]  filesize=3.898 GB/4.857 GB usage=761410/948649/1048576  80% **899*********9*9*8***6361201135469999**
 [6]  filesize=3.086 GB/4.347 GB usage=502296/707604/1048576  70% **7*9******9*8*8***2221001012352399999**
 [7]  filesize=4.572 GB/12.05 GB usage=637837/1681239/2097152  37% *77*88889874620000000001000000111233318*
 [8]  filesize=4.398 GB/8.337 GB usage=536959/1017816/1048576  52% *867788*5358348*57211111220001254667559*
 [9]  filesize=4.158 GB/6.707 GB usage=451275/727792/1048576  62% **8888**66682879682113131201034767759***
 [10] filesize=4.428 GB/6.471 GB usage=432439/632001/1048576  68% **98*939966692679969431422210367676*9***
 [11] filesize=4.721 GB/6.622 GB usage=419181/587905/1048576  71% ***9987977496396*97845335232035777599***
 [12] filesize=5.024 GB/6.754 GB usage=408896/549707/1048576  74% *99996399866945*7897664542553378787*9***
 [13] filesize=5.794 GB/7.642 GB usage=435277/574090/1048576  75% *9999159986977*69979452573422498879*9***
 [14] filesize=6.073 GB/7.537 GB usage=423625/525796/1048576  80% *****984999899899*5**996844556554328999*
 [15] filesize=6.576 GB/7.804 GB usage=428140/508101/524288  84% ******89******99*5*9786534633379876*9***
 [16] filesize=19.96 GB/19.96 GB usage=1218581/1218581/1572864 100% ****************************************
 [17] filesize=10.27 GB/10.27 GB usage=816858/816858/1048576 100% *98687697876*7*977764566479*999999597987
 [18] filesize=9.672 GB/20.59 GB usage=524774/1117379/1572864  46% 934446165797798***97320.000....01313079*
 [19] filesize=8.471 GB/12.46 GB usage=435435/640535/1048576  67% *836777*89889*7**88321112133696522489***
 [20] filesize=11.03 GB/20.76 GB usage=538991/1013737/1048576  53% *8779999*8*897589877810000241..214.14330
 [21] filesize=11.97 GB/15.25 GB usage=556738/709414/1048576  78% **586978999975*79*5694487355697994669***
 [22] filesize=23.61 GB/50.65 GB usage=1048415/2248378/2621440  46% 732257386272323324000012000144999999876*
 [23] filesize=29.30 GB/62.68 GB usage=1244116/2661397/3145728  46% 822676814334321220001000013469899989665*
 [24] filesize=53.91 GB/110.5 GB usage=2193987/4496644/4718592  48% 77873120000000011000013557*98***98987759
 [25] filesize=26.56 GB/40.51 GB usage=1037838/1582797/2097152  65% *********88*20247634453483*9382036017***
 [26] filesize=29.48 GB/43.47 GB usage=1107499/1633060/2097152  67% **************94636342445382600270057***
 [27] filesize=29.25 GB/42.25 GB usage=1057947/1528272/1572864  69% *****************33244337291600360067***
 [28] filesize=27.55 GB/35.85 GB usage=961028/1250691/1572864  76% *****************853635876*7420260187***
 [29] filesize=20.04 GB/26.14 GB usage=674913/880344/1048576  76% *****878698688**797963957676*48033098***
 [30] filesize=15.93 GB/19.59 GB usage=518578/637901/1048576  81% **844696**6**9*7989**78886366769254*9***
 [31] filesize=15.30 GB/18.08 GB usage=482083/569645/1048576  84% **7584999*88*9996998**9874387879447*9***
 [32] filesize=15.17 GB/17.65 GB usage=463018/538645/1048576  85% *8877798**999*9965*799*588569888956*9***
 [33] filesize=16.35 GB/18.69 GB usage=483952/553107/1048576  87% *89869799*98*99954*87**8996896799599****
 [34] filesize=16.03 GB/18.45 GB usage=460663/530005/1048576  86% *98879789*6*999738*69*6885798499988*9***
 [35] filesize=16.55 GB/18.88 GB usage=461836/527056/1048576  87% *9887989**7*999748*6**89756948*9988*9***
 [36] filesize=17.55 GB/19.97 GB usage=476296/541723/1048576  87% *9878989**7998*97*6**97855865999958*9***
 [37] filesize=19.04 GB/22.29 GB usage=502561/588539/1048576  85% *96677*9*99*9987978*989445666998966*9***
 [38] filesize=19.92 GB/23.18 GB usage=512177/595801/1048576  85% *97687*9**89*8*65*6**696447658*9999*9***
 [39] filesize=20.90 GB/24.43 GB usage=523352/611820/1048576  85% *95587***8999997*6**9954686359*9988*9***
 [40] filesize=21.04 GB/24.03 GB usage=513706/586707/1048576  87% *9666*8**89**9998*5*9995467559*9999*9***
 [41] filesize=21.47 GB/24.45 GB usage=511456/582510/1048576  87% 986496***8**9997*6**8993687369999*9*9***
 [42] filesize=21.47 GB/24.20 GB usage=499227/562902/1048576  88% 9875789**8*99997969*999856747**9999*****
 [43] filesize=21.15 GB/23.42 GB usage=480496/532072/1048576  90% 98766979*98**9997*6**999846799***99*****
 [44] filesize=20.41 GB/22.14 GB usage=453099/491591/524288  92% 88877777**9*999988*5**9998999****9******
 [45] filesize=19.89 GB/21.22 GB usage=431769/460637/524288  93% *88787779*9**89989*5***9*9**************
 [46] filesize=19.21 GB/20.56 GB usage=407946/436585/524288  93% *9976795**9**9997**5**999**9************
 [47] filesize=18.40 GB/19.68 GB usage=382510/409085/524288  93% ****5969**8**9978*5**9996789************
 [48] filesize=18.00 GB/19.12 GB usage=366215/389179/524288  94% *****998**99**96986*99989785************
 [49] filesize=17.21 GB/18.05 GB usage=343164/359911/524288  95% ***************9987*99869965************
 [50] filesize=16.12 GB/17.30 GB usage=314860/337931/524288  93% ***************59*6*998879727***********
 [51] filesize=16.43 GB/17.08 GB usage=314794/327114/524288  96% **********************998835************
 [52] filesize=17.56 GB/17.79 GB usage=329854/334134/524288  98% *************************9978***********
 [53] filesize=17.06 GB/17.44 GB usage=314426/321418/524288  97% **************************829***********
 [54] filesize=16.09 GB/16.58 GB usage=291005/299863/524288  97% *************************953************
 [55] filesize=16.92 GB/17.09 GB usage=300433/303463/524288  99% ***************************78***********
 [56] filesize=25.11 GB/29.02 GB usage=437935/506128/524288  86% *****************9*******889445546385132
 [57] filesize=20.52 GB/33.31 GB usage=351657/570714/1048576  61% ****************74****1.............2***
 [58] filesize=30.81 GB/35.78 GB usage=518786/602504/1048576  86% ************************6444655124******
 [59] filesize=30.35 GB/35.69 GB usage=502404/590885/1048576  85% ************988893374621475******99*****
 [60] filesize=41.54 GB/63.72 GB usage=676255/1037152/1048576  65% *****************9389*****2.00....00..12
 [61] filesize=62.68 GB/65.88 GB usage=1003594/1054756/1572864  95% ************************9036*******9****
 [62] filesize=90.70 GB/96.37 GB usage=1428631/1518061/1572864  94% ************************5008*******9****
 [63] filesize=161.9 GB/161.9 GB usage=2510155/2510155/2621440 100% ****************************************
 [64] filesize=1.874 TB/1.874 TB usage=28597358/28597358/28835840 100% ****************************************
 [65] filesize=1.648 TB/1.648 TB usage=24763071/24763071/25165824 100% ****************************************
====
# 40 chars=100% container file
"""


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
    setparam(cur, "bacula.jobs.all", 'N', "Number of all jobs", "Job", "select count(1) as data from job;", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.size.jobs.files", 'N', "Number of all jobs files", "File", "select count(1) as data from file;", 3, 3, '#001F3F', 'box-primary')
    setparam(cur, "bacula.size.jobs.bytes", 'N', "Sum size of all jobs", "Bytes", "select coalesce(sum(jobbytes),0) as data from job;", 3, 5, '#00c0ef', 'box-primary')
    setparam(cur, "bacula.jobs.running", 'N', "Number of running jobs", "Job", "select count(1) as data from job where jobstatus='R';", 2, 1, '#00c0ef', 'box-info')
    setparam(cur, "bacula.jobs.queued", 'N', "Number of queued jobs", "Job", "select count(1) as data from job where jobstatus='C';", 2, 1, '#ff851b', 'box-warning')
    setparam(cur, "bacula.jobs.success", 'N', "Number of success jobs", "Job", "select count(1) as data from job where jobstatus in ('T', 'I') and joberrors=0;", 1, 1, '#3c8dbc', 'box-success')
    setparam(cur, "bacula.jobs.errors", 'N', "Number of error jobs", "Job", "select count(1) as data from job where jobstatus in ('E','f','A');", 1, 1, '#3c8dbc', 'box-danger')
    setparam(cur, "bacula.jobs.warning", 'N', "Number of warning jobs", "Job", "select count(1) as data from job where jobstatus='T' and joberrors > 0;", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.tapes.available", 'N', "Number of available tapes", "Tape", "select count(1) as data from media where volstatus in ('Append','Recycled','Purged') and mediatype ilike 'tape%';", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.tapes.all", 'N', "Number of all defined tapes", "Tape", "select count(1) as data from media where mediatype ilike 'tape%';", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.size.tapes.bytes", 'N', "Sum size of all tapes written", "Bytes", "select coalesce(sum(volbytes),0) as data from media where mediatype ilike 'tape%';", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.tapes.error", 'N', "Number of Error tapes", "Tape", "select count(1) as data from media where volstatus='Error' and mediatype ilike 'tape%';", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.tapes.full", 'N', "Number of Full tapes", "Tape", "select count(1) as data from media where volstatus='Full' and mediatype ilike 'tape%';", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.tapes.used", 'N', "Number of Used tapes", "Tape", "select count(1) as data from media where volstatus='Used' and mediatype ilike 'tape%';", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.volumes.available", 'N', "Number of all available volumes", "Volume", "select count(1) as data from media where volstatus in ('Append','Recycled','Purged');", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.volumes.all", 'N', "Number of all defined volumes", "Volume", "select count(1) as data from media;", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.size.volumes.bytes", 'N', "Sum size of all volumes written", "Bytes", "select coalesce(sum(volbytes),0) as data from media;", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.volumes.error", 'N', "Number of Error volumes", "Volume", "select count(1) as data from media where volstatus='Error';", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.volumes.full", 'N', "Number of Full volumes", "Volume", "select count(1) as data from media where volstatus='Full';", 1, 1, '#3c8dbc', 'box-primary')
    setparam(cur, "bacula.volumes.used", 'N', "Number of Used volumes", "Volume", "select count(1) as data from media where volstatus='Used';", 1, 1, '#3c8dbc', 'box-primary')
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

