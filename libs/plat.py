# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import platform


# Bacula Enterprise 8.4.x - 1017
# Bacula Enterprise 8.6.x - 1018
# Bacula Enterprise 8.8.x - 1019
# Bacula Enterprise 10.2 - 1020
# Bacula Enterprise 12.0 - 1021
# Bacula Community 7.4.x - 15
# Bacula Community 9.2.x - 16
BEECATVERSUPPORTED = (1017, 1018, 1019, 1020, 1021)
BCCATVERSUPPORTED = (15, 16)
CATVERSUPPORTED = BEECATVERSUPPORTED + BCCATVERSUPPORTED
BACULACOMMUNITY = False
# system commands
SUDOCMD = "/usr/bin/sudo"
SYSTEMCTL = "/usr/bin/systemctl"
JOURNALCTL = "/usr/bin/journalctl --no-pager -u "
NETIPCMD = "/usr/sbin/ip"
LSSCSICMD = "/usr/bin/lsscsi -g"
MTCMD = "/usr/bin/mt"
MTXCMD = "/usr/sbin/mtx"
UDEVADMCMD = "/sbin/udevadm"
# platform specific
ourplatform = platform.linux_distribution(full_distribution_name=0)[0]
if ourplatform in ('Ubuntu', 'debian'):
    SYSTEMCTL = "/bin/systemctl"
    JOURNALCTL = "/bin/journalctl --no-pager -u "
    NETIPCMD = "/sbin/ip"
    MTCMD = "/bin/mt"


def getOSVersion():
    out = platform.linux_distribution()
    if out[2] != '':
        return out[0] + ' ' + out[1] + ' (' + out[2] + ')'
    else:
        return out[0] + ' ' + out[1]


def getOSPlatform():
    return platform.machine()


def getOStype():
    if ourplatform in ('centos', 'redhat'):
        return 'rhel'
    if ourplatform in ('debian', 'Ubuntu'):
        return 'deb'
    return 'rhel'
