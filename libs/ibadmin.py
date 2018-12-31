# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

# App Version
IBADVERSION = 'Community.2019.01'

IBADMINOSINFO = {
    # ostext, fgcolor, bgcolor, icon
    'rhel':     ["RHEL/Centos", "#dd4b39", "bg-red", "fa-linux"],
    'xen':      ["XenServer", "#dd4b39", "bg-red", "fa-cloud"],
    'deb':      ["Debian/Ubuntu", "#ff851b", "bg-orange", "fa-linux"],
    'proxmox':  ["Proxmox", "#ff851b", "bg-orange", "fa-cloud"],
    'win32':    ["Windows 32bit", "#39cccc", "bg-teal", "fa-windows"],
    'win64':    ["Windows 64bit", "#39cccc", "bg-teal", "fa-windows"],
    'osx':      ["MacOS", "#d2d6de", "bg-gray", "fa-apple"],
    'solsparc': ["Solaris SPARC", "#00c0ef", "bg-aqua", None],
    'solintel': ["Solaris x86", "#00c0ef", "bg-aqua", None],
    'aix':      ["AIX", "#00a65a", "bg-green", None],
    'hpux':     ["HP-UX", "#ff851b", "bg-orange", None],
    'vmware':   ["VMware ESXi", "#00a65a", "bg-green", "fa-cloud"],
    'kvm':      ["KVM Hypervisor", "#357ca5", "bg-light-blue", "fa-cloud"],
}

BACULAJOBTYPES = {
    # jobtext, bgcolor
    'B': ["Backup", "bg-aqua"],
    'Backup': ["Backup", "bg-aqua"],
    'R': ["Restore", "bg-purple"],
    'Restore': ["Restore", "bg-purple"],
    'D': ["Admin", "bg-maroon"],
    'Admin': ["Admin", "bg-maroon"],
    'C': ["Copied", "bg-teal"],
    'c': ["CopyJob", "bg-aqua"],
    'M': ["Migrated", "bg-aqua"],
    'g': ["Migration", "bg-aqua"],
    'V': ["Verify", "bg-aqua"],
    'S': ["ScanJob", "bg-aqua"],
}

BACULAJOBLEVELS = {
    # leveltext, bgcolor
    'F': ["Full", "label-primary"],
    'full': ["Full", "label-primary"],
    'Full': ["Full", "label-primary"],
    'D': ["Diff", "label-success"],
    'Differential': ["Diff", "label-success"],
    'Diff': ["Diff", "label-success"],
    'differential': ["Diff", "label-success"],
    'I': ["Incr", "label-info"],
    'Incremental': ["Incr", "label-info"],
    'Incr': ["Incr", "label-info"],
    'incremental': ["Incr", ],
    'B': ["Base", ],
    'f': ["VFull", "label-primary"],
    'VirtualFull': ["VFull", ],
    'S': ["Since", "label-primary"],
    'C': ["Ver2Cat", "label-primary"],
    'O': ["Vol2Cat", "label-primary"],
    'd': ["Disk2Cat", "label-primary"],
    'A': ["VerData", "label-primary"],
}

IBADMINJOBAPPS = {
    # Descr, bgcolor
    'jd-admin': ["Admin Job", "bg-maroon"],
    'jd-restore': ["Restore", "bg-purple"],
    'jd-backup-catalog': ["Catalog Backup", "bg-navy"],
    'jd-backup-files': ["Files Backup", "label-primary"],
    'jd-backup-proxmox': ["Proxmox Guest Backup", "bg-orange"],
    'jd-backup-esx': ["VMware Guest Backup", "bg-green"],
    'jd-backup-xen': ["XenServer Guest Backup", "bg-red"],
    'jd-backup-kvm': ["KVM Guest Backup", "bg-light-blue"],
}

BACULAJOBSTATUS = {
    # text, bgcolor, boxcolor
    'A': ['Canceled', 'bg-fuchsia', 'box-danger'],
    'C': ['Queued', 'bg-orange', 'box-orange'],
    'F': ['Queued', 'bg-orange', 'box-orange'],
    'S': ['Queued', 'bg-orange', 'box-orange'],
    'M': ['Queued', 'bg-orange', 'box-orange'],
    'm': ['Queued', 'bg-orange', 'box-orange'],
    's': ['Queued', 'bg-orange', 'box-orange'],
    'j': ['Queued', 'bg-orange', 'box-orange'],
    'c': ['Queued', 'bg-orange', 'box-orange'],
    'd': ['Queued', 'bg-orange', 'box-orange'],
    't': ['Queued', 'bg-orange', 'box-orange'],
    'E': ['Error', 'bg-red', 'box-danger'],
    'f': ['Error', 'bg-red', 'box-danger'],
    'I': ['Incomplete', 'bg-teal', 'box-info'],
    'R': ['Running', 'bg-aqua', 'box-info'],
    'T': ['Success', 'bg-green', 'box-success'],
    'TW': ['Warning', 'bg-yellow', 'box-warning'],
    'W': ['Warning', 'bg-yellow', 'box-warning'],
}

BACULAVOLUMESTATUS = {
    # bgcolor
    'Append': "bg-green",
    'Used': "bg-aqua",
    'Error': "bg-red",
    'Full': "bg-blue",
    'Purged': "bg-yellow",
    'Recycle': "bg-yellow",
    'Cleaning': "bg-purple-gradient",
}


BACULAPLUGINS = {
    # text, bgcolor
    'bpipe-fd': ["BPipe", "bg-aqua"],
    'proxmox-fd': ["Proxmox", "bg-orange"],
    'xenserver-fd': ["XenServer", "bg-red"],
    'kvm-fd': ["KVM", "bg-light-blue"],
    'vsphere-fd': ["vSphere", "bg-green"],
    'oracle-fd': ["Oracle", "bg-red"],
    'oracle-sbt-fd': ["Oracle SBT", "bg-red"],
    'sybase-sbt-fd': ["Sybase SBT", "bg-green"],
}


IBADMINTASKS = {
    # text, color, progresscolor
    'N': ["New", "bg-maroon", "progress-bar-info"],
    'E': ["Failed", "bg-red", "progress-bar-danger"],
    'F': ["Success", "bg-green", "progress-bar-success"],
    'C': ["Canceled", "bg-orange", "progress-bar-yellow"],
    'R': ["Running", "bg-aqua", "progress-bar-aqua"],
}


IBADMINCHARTS = {
    # text, icon
    1: ["Line chart", "fa-line-chart"],
    2: ["Bar chart", "fa-bar-chart"],
    3: ["Area chart", "fa-area-chart"],
    4: ["Pie chart", "fa-pie-chart"],
}


IBADMINMEDIA = {
    # icon, color
    'Dedu': ["fa-cubes", "bg-maroon"],
    'Tape': ["fa-simplybuilt", "bg-aqua"],
    'File': ["fa-database", "bg-green"],
}


def getdatadefault(key=None, table=None, indx=None, default=None):
    if key is not None and table is not None:
        val = table.get(key, None)
        if val is not None:
            if indx is None:
                retval = val
            else:
                retval = val[indx]
            if retval is None:
                return default
            else:
                return retval
    return default


def ibadmin_ostext(value=None):
    return getdatadefault(value, IBADMINOSINFO, 0, "Unknown")


def ibadmin_osfgcolor(value=None):
    return getdatadefault(value, IBADMINOSINFO, 1, "#3c8dbc")


def ibadmin_osbgcolor(value=None):
    return getdatadefault(value, IBADMINOSINFO, 2, "bg-light-blue")


def ibadmin_osicon(value=None):
    return getdatadefault(value, IBADMINOSINFO, 3, "")


def ibadmin_osiconall(value=None):
    return getdatadefault(value, IBADMINOSINFO, 3, "fa-server")


def ibadmin_oslist():
    oses = []
    for os in IBADMINOSINFO:
        oses.append((os, IBADMINOSINFO[os][0]),)
    return oses


def ibadmin_jobtext(value=None):
    return getdatadefault(value, BACULAJOBTYPES, 0, "Unknown")


def ibadmin_jobbgcolor(value=None):
    return getdatadefault(value, BACULAJOBTYPES, 1, "bg-gray")


def ibadmin_jobleveltext(value=None, arg=None):
    if arg is not None and (arg in ('R', 'Restore')):
        return "Restore"
    if arg is not None and (arg in ('D', '', 'Admin')) or value == ' ' or value == '':
        return "Admin"
    return getdatadefault(value, BACULAJOBLEVELS, 0, "Unknown")


def ibadmin_joblevelbgcolor(value=None, arg=None):
    if arg is not None and (arg == 'R' or arg == 'Restore'):
        return "bg-purple"
    if arg is not None and (arg == 'D' or arg == '' or arg == 'Admin') or value == ' ' or value == '':
        return "bg-maroon"
    return getdatadefault(value, BACULAJOBLEVELS, 1, "bg-gray")


def ibadmin_jobapptext(value):
    return getdatadefault(value, IBADMINJOBAPPS, 0, "Unknown")


def ibadmin_jobappcolor(value):
    return getdatadefault(value, IBADMINJOBAPPS, 1, "Unknown")


def ibadmin_jobstatustext(value, arg):
    if value == 'T' and arg > 0:
        value += 'W'
    return getdatadefault(value, BACULAJOBSTATUS, 0, "Unknown")


def ibadmin_jobstatusbgcolor(value, arg):
    if value == 'T' and arg > 0:
        value += 'W'
    return getdatadefault(value, BACULAJOBSTATUS, 1, "bg-gray")


def ibadmin_jobstatusboxcolor(value, arg):
    if value == 'T' and arg > 0:
        value += 'W'
    return getdatadefault(value, BACULAJOBSTATUS, 2, "box-solid")


def ibadmin_volstatusbgcolor(value):
    return getdatadefault(value, BACULAVOLUMESTATUS, None, "bg-gray")


def ibadmin_jobrunningbgcolor(value):
    if type(value) is int:
        if value > 0:
            return BACULAJOBSTATUS['R'][1]
    return "bg-gray"


def ibadmin_jobqueuedbgcolor(value):
    if type(value) is int:
        if value > 0:
            return BACULAJOBSTATUS['C'][1]
    return "bg-gray"


def ibadmin_joberrorbgcolor(value):
    if type(value) is int:
        if value > 0:
            return BACULAJOBSTATUS['E'][1]
    return "bg-gray"


def ibadmin_jobwarningbgcolor(value):
    if type(value) is int:
        if value > 0:
            return BACULAJOBSTATUS['W'][1]
    return "bg-gray"


def ibadmin_jobsuccessbgcolor(value):
    if type(value) is int:
        if value > 0:
            return BACULAJOBSTATUS['T'][1]
    return "bg-gray"


def ibadmin_jobcancelbgcolor(value):
    if type(value) is int:
        if value > 0:
            return BACULAJOBSTATUS['A'][1]
    return "bg-gray"


def ibadmin_render_os(os):
    return [ibadmin_osbgcolor(os), ibadmin_ostext(os)]


def ibadmin_render_joblevel(jlevel, jtype):
    return [ibadmin_joblevelbgcolor(jlevel, jtype), ibadmin_jobleveltext(jlevel, jtype)]


def ibadmin_render_joberrors(errors, status):
    val = str(errors)
    if status == 'A':
        val = BACULAJOBSTATUS['A'][0]
    return [ibadmin_jobstatusbgcolor(status, errors), val]


def ibadmin_render_jobstatus(status, errors):
    return [ibadmin_jobstatusbgcolor(status, errors), ibadmin_jobstatustext(status, errors)]


def ibadmin_plugin_color(name):
    pname = name
    if name is not None:
        pname = name.split('.')[0]
    return getdatadefault(pname, BACULAPLUGINS, 1, "bg-gray")


def ibadmin_plugin_text(name):
    pname = name
    if name is not None:
        pname = name.split('.')[0]
    return getdatadefault(pname, BACULAPLUGINS, 0, name)


def ibadmin_tasks_color(status):
    return getdatadefault(status, IBADMINTASKS, 1, "bg-gray")


def ibadmin_tasks_text(status):
    return getdatadefault(status, IBADMINTASKS, 0, status)


def ibadmin_tasks_progresscolor(status):
    return getdatadefault(status, IBADMINTASKS, 2, "progress-bar-aqua")


def ibadmin_charts_text(value):
    if type(value) is not int:
        value = int(value)
    return getdatadefault(value, IBADMINCHARTS, 0, 'Bar chart - default')


def ibadmin_charts_icon(value):
    if type(value) is not int:
        value = int(value)
    return getdatadefault(value, IBADMINCHARTS, 1, 'fa-bar-chart')


def ibadmin_media_icon(value):
    pvalue = value
    if value is not None:
        pvalue = value[:4]
    return getdatadefault(pvalue, IBADMINMEDIA, 0, 'fa-database')


def ibadmin_media_color(value):
    pvalue = value
    if value is not None:
        pvalue = value[:4]
    return getdatadefault(pvalue, IBADMINMEDIA, 1, 'bg-gray')

