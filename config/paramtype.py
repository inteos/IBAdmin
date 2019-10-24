# -*- coding: UTF-8 -*-
from __future__ import unicode_literals


class ParamType(object):
    Name = 'Name'
    Enabled = 'Enabled'
    Client = 'Client'
    Storage = 'Storage'
    Pool = 'Pool'
    Password = 'Password'
    Address = 'Address'
    Port = 'Port'
    FDAddress = 'FDAddress'
    Address_short = 'Addr'
    Catalog = 'Catalog'
    Run = 'Run'
    Mail = 'Mail'
    Device = 'Device'
    MediaType = 'MediaType'
    ArchiveDevice = 'ArchiveDevice'
    DedupDirectory = 'DedupDirectory'
    DedupIndexDirectory = 'DedupIndexDirectory'
    ibadClusterName = '.ClusterName'
    ibadClusterService = '.ClusterService'
    ibadAlias = '.Alias'
    ibadvCenterName = '.vCenterName'
    ibadSDAddress = '.SDAddress'
    ibadDepartment = '.Department'
    ibadOS = '.OS'
    ibadDisabledfordelete = '.Disabledfordelete'
    ibadLicenseKey = '.IBADLicenseKey'


class ParamValue(object):
    Yes = 'Yes'
    No = 'No'
