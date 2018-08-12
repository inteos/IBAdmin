from django import template

register = template.Library()


@register.filter
def jobrunningbgcolor(value):
    if type(value) is int:
        if value > 0:
            return "bg-aqua"
    return "bg-gray"


@register.filter
def jobqueuedbgcolor(value):
    if type(value) is int:
        if value > 0:
            return "bg-orange"
    return "bg-gray"


@register.filter
def joberrorbgcolor(value):
    if type(value) is int:
        if value > 0:
            return "bg-red"
    return "bg-gray"


@register.filter
def jobwarningbgcolor(value):
    if type(value) is int:
        if value > 0:
            return "bg-yellow"
    return "bg-gray"


@register.filter
def jobsuccessbgcolor(value):
    if type(value) is int:
        if value > 0:
            return "bg-green"
    return "bg-gray"


@register.filter
def OSfgcolor(value):
    # Linux
    if value == 'rhel' or value == 'xen':
        return "#dd4b39"
    if value == 'deb' or value == 'proxmox':
        return "#ff851b"
    # Windows
    if value == 'win32' or value == 'win64':
        return "#39cccc"
    # OSX
    if value == 'osx':
        return "#d2d6de"
    # Solaris
    if value == 'solsparc' or value == 'solintel':
        return "#00c0ef"
    # AIX
    if value == 'aix':
        return "#00a65a"
    # HP-UX
    if value == 'hpux':
        return "#ff851b"
    return "#3c8dbc"


@register.filter
def OSbgcolor(value):
    # Linux
    if value == 'rhel' or value == 'xen':
        return "bg-red"
    if value == 'deb' or value == 'proxmox':
        return "bg-orange"
    # Windows
    if value == 'win32' or value == 'win64':
        return "bg-teal"
    # OSX
    if value == 'osx':
        return "bg-gray"
    # Solaris
    if value == 'solsparc' or value == 'solintel':
        return "bg-aqua"
    # AIX
    if value == 'aix':
        return "bg-green"
    # HP-UX
    if value == 'hpux':
        return "bg-orange"
    return "bg-primary"


@register.filter
def jobstatusbgcolor(value, arg):
    if value == 'A':                            # Canceled job
        return 'bg-fuchsia'
    if value == 'C' or value == 'F' or value == 'S' or value == 'M' or value == 'm' or value == 's' or value == 'j' \
            or value == 'c' or value == 'd' or value == 't':                            # Created job - queued
        return 'bg-orange'
    if value == 'E' or value == 'f':            # Error/Failed jobs
        return 'bg-red'
    if value == 'I':                            # Incomplete job
        return 'bg-teal'
    if value == 'R':                            # Running job
        return 'bg-aqua'
    if value == 'T' and arg < 1:                # Job finished successfuly
        return 'bg-green'
    if (value == 'T' and arg > 0) or value == 'W':  # Job finished with warnings
        return 'bg-yellow'
    return "bg-gray"                            # other status unknown


@register.filter
def jobstatusboxcolor(value, arg):
    if value == 'A':                            # Canceled job
        return 'box-danger'
    if value == 'C':                            # Created job - queued
        return 'box-orange'
    if value == 'E' or value == 'f':            # Error/Failed jobs
        return 'box-danger'
    if value == 'I':                            # Incomplete job
        return 'box-info'
    if value == 'R':                            # Running job
        return 'box-info'
    if value == 'T' and arg < 1:                # Job finished successfuly
        return 'box-success'
    if (value == 'T' and arg > 0) or value == 'W':  # Job finished with warnings
        return 'box-warning'
    return "box-solid"                          # other status unknown


@register.filter
def statusbgcolor(value):
    if type(value) is int:
        if value == 1:
            return 'bg-green'
        if value == 0:
            return 'bg-red'
    return "bg-gray"


@register.filter
def jobtypebgcolor(value):
    if value == 'B' or value == 'Backup':       # Backup
        return "bg-aqua"
    if value == 'R' or value == 'Restore':      # Restore
        return "bg-purple"
    if value == 'D' or value == 'Admin':        # Admin
        return "bg-maroon"
    if value == 'C':                            #
        return "bg-teal"
    if value == 'c':
        return "bg-aqua"
    if value == 'M':
        return "bg-aqua"
    if value == 'g':
        return "bg-aqua"
    if value == 'V':
        return "bg-aqua"
    if value == 'V':
        return "bg-aqua"
    if value == 'S':
        return "bg-aqua"
    return "bg-gray"


@register.filter
def joblevelbgcolor(value, arg):
    """
    
    :param value: Job->Level
    :param arg: Job.Type
    :return: 
    """
    if arg is not None and (arg == 'R' or arg == 'Restore'):
        return "bg-purple"
    if arg is not None and (arg == 'D' or arg == '' or arg == 'Admin') or value == ' ' or value == '':
        return "bg-maroon"
    if value == 'F' or value == 'full' or value == 'Full' or value == 'f' or value == 'VirtualFull':
        return "label-primary"
    if value == 'D' or value == 'Differential' or value == 'Diff' or value == 'differential':
        return "label-success"
    if value == 'I' or value == 'Incremental' or value == 'Incr' or value == 'incremental':
        return "label-info"
    if value in 'BSCOdA':
        # Base Since Ver2Cat Vol2Cat Disk2Cat VerData
        return "label-primary"
    return "bg-gray"


@register.filter
def volstatusbgcolor(value):
    if value == 'Append':
        return "bg-green"
    if value == 'Used':
        return "bg-aqua"
    if value == 'Error':
        return "bg-red"
    if value == 'Full':
        return "bg-blue"
    if value == 'Purged' or value == 'Recycle':
        return "bg-yellow"
    if value == 'Cleaning':
        return "bg-purple-gradient"
    return "bg-gray"


@register.filter
def jobstatus_running_bgcolor(value):
    if type(value) is int:
        if value > 0:
            return 'bg-aqua'
    return 'bg-gray'


@register.filter
def jobstatus_cancel_bgcolor(value):
    if type(value) is int:
        if value > 0:
            return 'bg-fuchsia'
    return 'bg-gray'


@register.filter
def jobstatus_queued_bgcolor(value):
    if type(value) is int:
        if value > 0:
            return 'bg-orange'
    return 'bg-gray'


@register.filter
def jobstatus_finished_bgcolor(value):
    if type(value) is int:
        if value > 0:
            return 'bg-green'
    return 'bg-gray'


@register.filter
def jobstatus_error_bgcolor(value):
    if type(value) is int:
        if int(value) > 0:
            return 'bg-red'
    return 'bg-gray'


@register.filter
def jobstatus_warning_bgcolor(value):
    if type(value) is int:
        if value > 0:
            return 'bg-yellow'
    return 'bg-gray'


@register.filter
def mediacolor(value):
    if value.startswith('Dedup'):
        return "bg-maroon"
    if value.startswith('Tape'):
        return "bg-aqua"
    return "bg-green"


@register.filter
def tasksbgcolor(value):
    if value == 'N':
        return "bg-maroon"
    if value == 'E':
        return "bg-red"
    if value == 'F':
        return "bg-green"
    if value == 'C':
        return "bg-orange"
    return "bg-aqua"


@register.filter
def tasksprogresscolor(value):
    if value == 'N':
        return "progress-bar-info"
    if value == 'E':
        return "progress-bar-danger"
    if value == 'F':
        return "progress-bar-success"
    if value == 'C':
        return "progress-bar-yellow"
    return "progress-bar-aqua"


@register.filter
def jdappcolor(value):
    if value is not None:
        if value == 'jd-backup-files':
            return 'label-primary'
        if value == 'jd-backup-proxmox':
            return 'bg-orange'
        if value == 'jd-admin':
            return 'bg-maroon'
        if value == 'jd-backup-catalog':
            return 'bg-navy'
    return 'label-default'


@register.filter
def devstatuscolor(value):
    if value is not None:
        if value == 'Running':
            return 'label-info'
        if value == 'Disabled' or value == 'Blocked':
            return 'label-danger'
        if value == 'Mounted':
            return 'bg-navy'
    return 'label-primary'
