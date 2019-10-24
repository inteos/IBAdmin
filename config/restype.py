# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals


RESTYPE = {
    'Director': 1,
    'Storage': 2,
    'FileDaemon': 3,
    'Client': 4,
    'Messages': 5,
    'Catalog': 6,
    'Schedule': 7,
    'Job': 8,
    'JobDefs': 9,
    'Fileset': 10,
    'Pool': 11,
    'Device': 12,
    'Autochanger': 13,
    'Include': 14,
    'Exclude': 15,
    'Options': 16,
    'SDAddresses': 17,
    'IP': 18,
    'Console': 19,
}


class ResType(object):
    Director = RESTYPE['Director']
    Storage = RESTYPE['Storage']
    FileDaemon = RESTYPE['FileDaemon']
    Client = RESTYPE['Client']
    Messages = RESTYPE['Messages']
    Catalog = RESTYPE['Catalog']
    Schedule = RESTYPE['Schedule']
    Job = RESTYPE['Job']
    JobDefs = RESTYPE['JobDefs']
    Fileset = RESTYPE['Fileset']
    Pool = RESTYPE['Pool']
    Device = RESTYPE['Device']
    Autochanger = RESTYPE['Autochanger']
    Include = RESTYPE['Include']
    Exclude = RESTYPE['Exclude']
    Options = RESTYPE['Options']
    SDAddresses = RESTYPE['SDAddresses']
    IP = RESTYPE['IP']
    Console = RESTYPE['Console']
