# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from config.confinfo import getDIRFSparams


CATALOGFS = {
    'catsql': {'icon': 'fa fa-database', 'text': 'Catalog database export'},
    'bsr': {'icon': 'fa fa-map-signs', 'text': 'Bootstrap Files'},
    'scripts': {'icon': 'fa fa-tags', 'text': 'Scripts'},
}

PROXMOXFS = {
    'qemu': {'icon': 'fa fa-desktop', 'text': 'QEMU VM Guests'},
    'lxc': {'icon': 'fa fa-cube', 'text': 'Container Guests'},
    'all': {'icon': 'fa fa-cubes', 'text': 'All Guest VMs'},
}


def catalogfs_get(comp=None):
    if comp is None:
        return {}
    data = CATALOGFS.get(comp, None)
    return data


def catalogfs_get_icon(comp=None):
    if comp is None:
        return ''
    data = CATALOGFS.get(comp, None)
    return data['icon']


def catalogfs_get_text(comp=None):
    if comp is None:
        return ''
    data = CATALOGFS.get(comp, None)
    return data['text']


def catalogfs_getall():
    comps = CATALOGFS.keys()
    data = []
    for c in comps:
        data.append(catalogfs_get(c))
    return data


def catalog_fsdata():
    (inclist, exclist, optionlist) = getDIRFSparams(name='fs-catalog-backup')
    return {
        'FS': catalogfs_getall(),
        'Options': optionlist,
    }


def proxmoxfs_get_icon(comp=None):
    if comp is None:
        return ''
    data = PROXMOXFS.get(comp, None)
    return data['icon']


def proxmoxfs_get_text(comp=None):
    if comp is None:
        return ''
    data = PROXMOXFS.get(comp, None)
    return data['text']


def proxmox_fsdata(jobparams=None):
    if jobparams is not None:
        fsname = jobparams.get('FileSet', None)
        optionlist = None
        if fsname is not None:
            (inclist, exclist, optionlist) = getDIRFSparams(name=fsname)
        vmsexclude = jobparams['Objsexclude']
        if len(vmsexclude) > 0:
            vmsexclude = ({'value': vmsexclude},)
        else:
            vmsexclude = None
        if jobparams['Allobjs'] == 'True':
            vmslist = ['All Guest VMs']
            vmsicon = 'fa-cubes'
        else:
            vmsicon = 'fa-cube'
            vmsinclude = jobparams['Objsinclude']
            if len(vmsinclude) > 0:
                vmsinclude = vmsinclude.split(":")
            else:
                vmsinclude = []
            vmslist = []
            for vm in vmsinclude:
                vmslist.append(vm)
        return {
            'VMSicon': vmsicon,
            'VMS': vmslist,
            'Exclude': vmsexclude,
            'Options': optionlist,
        }
    else:
        return None


def xenserver_fsdata(jobparams=None):
    if jobparams is not None:
        fsname = jobparams.get('FileSet', None)
        optionlist = None
        if fsname is not None:
            (inclist, exclist, optionlist) = getDIRFSparams(name=fsname)
        vmsexclude = jobparams['Objsexclude']
        if len(vmsexclude) > 0:
            vmsexclude = ({'value': vmsexclude},)
        else:
            vmsexclude = None
        if jobparams['Allobjs'] == 'True':
            vmslist = ['All Guest VMs']
            vmsicon = 'fa-cubes'
        else:
            vmsicon = 'fa-cube'
            vmsinclude = jobparams['Objsinclude']
            if len(vmsinclude) > 0:
                vmsinclude = vmsinclude.split(":")
            else:
                vmsinclude = []
            vmslist = []
            for vm in vmsinclude:
                vmslist.append(vm)
        return {
            'VMSicon': vmsicon,
            'VMS': vmslist,
            'Exclude': vmsexclude,
            'Options': optionlist,
        }
    else:
        return None


def kvmhost_fsdata(jobparams=None):
    if jobparams is not None:
        fsname = jobparams.get('FileSet', None)
        optionlist = None
        if fsname is not None:
            (inclist, exclist, optionlist) = getDIRFSparams(name=fsname)
        vmsexclude = jobparams['Objsexclude']
        if len(vmsexclude) > 0:
            vmsexclude = ({'value': vmsexclude},)
        else:
            vmsexclude = None
        if jobparams['Allobjs'] == 'True':
            vmslist = ['All Guest VMs']
            vmsicon = 'fa-cubes'
        else:
            vmsicon = 'fa-cube'
            vmsinclude = jobparams['Objsinclude']
            if len(vmsinclude) > 0:
                vmsinclude = vmsinclude.split(":")
            else:
                vmsinclude = []
            vmslist = []
            for vm in vmsinclude:
                vmslist.append(vm)
        return {
            'VMSicon': vmsicon,
            'VMS': vmslist,
            'Exclude': vmsexclude,
            'Options': optionlist,
        }
    else:
        return None


def vmware_fsdata(jobparams=None):
    if jobparams is not None:
        fsname = jobparams.get('FileSet', None)
        optionlist = None
        if fsname is not None:
            (inclist, exclist, optionlist) = getDIRFSparams(name=fsname)
        vmsexclude = jobparams['Objsexclude']
        if len(vmsexclude) > 0:
            vmsexclude = ({'value': vmsexclude},)
        else:
            vmsexclude = None
        if jobparams['Allobjs'] == 'True':
            vmslist = ['All Guest VMs']
            vmsicon = 'fa-cubes'
        else:
            vmsicon = 'fa-cube'
            vmsinclude = jobparams['Objsinclude']
            if len(vmsinclude) > 0:
                vmsinclude = vmsinclude.split(":")
            else:
                vmsinclude = []
            vmslist = []
            for vm in vmsinclude:
                vmslist.append(vm)
        return {
            'VMSicon': vmsicon,
            'VMS': vmslist,
            'Exclude': vmsexclude,
            'Options': optionlist,
        }
    else:
        return None


def files_fsdata(jobparams=None):
    if jobparams is not None:
        fsname = jobparams.get('FileSet', None)
        if fsname is not None:
            (inclist, exclist, optionlist) = getDIRFSparams(name=fsname)
            return {
                'Include': inclist,
                'Exclude': exclist,
                'Options': optionlist,
            }
    else:
        return None
