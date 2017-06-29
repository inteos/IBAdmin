# coding=utf-8
from __future__ import unicode_literals
import platform


# globals
SUDOCMD = "/usr/bin/sudo"
SYSTEMCTL = "/usr/bin/systemctl"
# App Version
IBADVERSION = '2017.01'
# Bacula Enterprise 8.4.x - 1017
# Bacula Enterprise 8.6.x - 1018
# Bacula Enterprise 8.8.x - 1019
CATVERSUPPORTED = (1017, 1018, 1019)
# system commands
JOURNALCTL = "/usr/bin/journalctl --no-pager -u "
NETIPCMD = "/usr/sbin/ip"
LSSCSICMD = "/usr/bin/lsscsi -g"
# platform specyfic
ourplatform = platform.linux_distribution(full_distribution_name=0)[0]
if ourplatform in ('Ubuntu', 'debian'):
    SYSTEMCTL = "/bin/systemctl"
    JOURNALCTL = "/bin/journalctl --no-pager -u "
    NETIPCMD = "/sbin/ip"


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
