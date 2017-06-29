from django import template
from django.utils.safestring import mark_safe
from libs.conf import getscheduletext, getretentiontext

register = template.Library()


@register.filter
def bytestext(value):
    try:
        val = long(value)
    except:
        return value
    if val < 1024:
        return str(val) + " Bytes"
    val /= 1024.0
    for sx in ['kB', 'MB', 'GB', 'TB', 'PB']:
        if val < 1024:
            return "{:.2f} ".format(val) + sx
        val /= 1024.0
    return str(val)


@register.filter
def jobstatustext(value, arg):
    if value == 'A':
        return 'Canceled'
    if value == 'C' or value == 'F' or value == 'S' or value == 'M' or value == 'm' or value == 's' or value == 'j' \
            or value == 'c' or value == 'd' or value == 't':
        return 'Queued'
    if value == 'E' or value == 'f':
        return 'Error'
    if value == 'I':
        return 'Incomplete'
    if value == 'R':
        return 'Running'
    if value == 'T' and arg < 1:
        return 'Success'
    if (value == 'T' and arg > 0) or value == 'W':
        return 'Warning'
    return 'Unknown'


@register.filter
def statustext(value):
    if type(value) is int:
        if value == 1:
            return 'Online'
        if value == 0:
            return 'Offline'
    return "Unknown"


@register.filter
def jobtypetext(value):
    if value == 'B':
        return "Backup"
    if value == 'R':
        return "Restore"
    if value == 'D':
        return "Admin"
    if value == 'C':
        return "Copied"
    if value == 'c':
        return "CopyJob"
    if value == 'M':
        return "Migrated"
    if value == 'g':
        return "Migration"
    if value == 'V':
        return "Verify"
    if value == 'V':
        return "Verify"
    if value == 'S':
        return "ScanJob"
    return "Unknown"


@register.filter
def jobleveltext(value, arg=None):
    """
    
    :param value: Job->Level
    :param arg: Job->Type
    :return: 
    """
    if arg is not None and (arg == 'R' or arg == 'Restore'):
        return "Restore"
    if arg is not None and (arg == 'D' or arg == '' or arg == 'Admin') or value == ' ' or value == '':
        return "Admin"
    if value == 'F' or value == 'full' or value == 'Full':
        return "Full"
    if value == 'D' or value == 'Differential' or value == 'Diff' or value == 'differential':
        return "Diff"
    if value == 'I' or value == 'Incremental' or value == 'Incr' or value == 'incremental':
        return "Incr"
    if value == 'B':
        return "Base"
    if value == 'f' or value == 'VirtualFull':
        return "VFull"
    if value == 'S':
        return "Since"
    if value == 'C':
        return "Ver2Cat"
    if value == 'O':
        return "Vol2Cat"
    if value == 'd':
        return "Disk2Cat"
    if value == 'A':
        return "VerData"
    return "Unknown"


@register.filter
def mediaicon(value):
    if value.startswith('Dedup'):
        return "fa-cubes"
    if value.startswith('Tape'):
        return "fa-simplybuilt"
    return "fa-database"


@register.filter
def trimfilename(value, arg=32):
    out = value
    l = len(value)
    if l > arg:
        if value.startswith('/'):
            out = "/.../" + value[l - arg + 5:]
        else:
            out = value[0:3] + ".../" + value[l - arg + 7:]
    return out.replace('//', '/')


@register.filter
def OStext(value):
    if value == 'rhel':
        return "RHEL/Centos"
    if value == 'deb':
        return "Debian/Ubuntu"
    if value == 'win32':
        return "Windows 32bit"
    if value == 'win64':
        return "Windows 64bit"
    if value == 'osx':
        return "MacOS X"
    if value == 'solsparc':
        return "Solaris SPARC"
    if value == 'solintel':
        return "Solaris x86"
    if value == 'aix':
        return "AIX"
    if value == 'hpux':
        return "HP-UX"
    return "Unknown"


@register.filter
def OSicon(value):
    if value in ('rhel', 'deb'):
        return "fa-linux"
    if value in ('win32', 'win64'):
        return "fa-windows"
    if value == 'osx':
        return "fa-apple"
    return ""


@register.filter
def OSiconall(value):
    if value in ('rhel', 'deb', 'win32', 'win64', 'osx'):
        return OSicon(value)
    return "fa-server"


@register.filter
def scheduletext(value):
    if value is not None:
        return getscheduletext(value)
    return ''


@register.filter
def retentiontext(value):
    if value is None or value == '':
        return mark_safe('<i>N/A</i>')
    else:
        return mark_safe(getretentiontext(value))


@register.filter
def taskstatustext(value):
    if value == 'N':
        return "New"
    if value == 'E':
        return "Failed"
    if value == 'F':
        return "Success"
    return "Running"


@register.filter
def charticon(value):
    if type(value) is not int:
        value = int(value)
    if value == 1:
        return 'fa-line-chart'
    if value == 2:
        return 'fa-bar-chart'
    if value == 3:
        return 'fa-area-chart'
    if value == 4:
        return 'fa-pie-chart'
    return 'fa-bar-chart'


@register.filter
def charttext(value):
    if type(value) is not int:
        value = int(value)
    if value == 1:
        return 'Line chart'
    if value == 2:
        return 'Bar chart'
    if value == 3:
        return 'Area chart'
    if value == 4:
        return 'Pie chart'
    return 'Bar chart - default'


@register.filter
def jdapptext(value):
    if value is not None:
        if value == 'jd-admin':
            return 'Admin Job'
        if value == 'jd-backup-catalog':
            return 'Catalog Backup'
        if value == 'jd-backup-files':
            return 'Files backup'
    return 'Unknown'
