# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
import string
import random
import base64
from Crypto.Cipher import AES


def randomstr(size=64, chars=tuple(string.ascii_letters) + tuple(string.digits)):
    # it was:  + tuple('!@#$%^&*_+-='), but Windows client had problems
    return ''.join(random.choice(chars) for _ in range(size))


def getencpass(comp, password):
    # encrypt password
    comptxt = comp[:32].rjust(32)
    passwordtxt = password.rjust(32)
    cipher = AES.new(comptxt, AES.MODE_ECB)
    encoded = base64.b64encode(cipher.encrypt(passwordtxt))
    return encoded


def getrndencpass(comp):
    # generate and encrypt password
    password = randomstr()
    return getencpass(comp, password)


"""
# p='password123'
# c='ibadmin'
# ep=getencpass(c,p)
# print ep
# dp=getdecpass(c,ep)
# print '"'+dp+'"'
"""


def getdecpass(comp, encpass):
    # decrypt password
    comptxt = comp.rjust(32)
    cipher = AES.new(comptxt, AES.MODE_ECB)
    decoded = cipher.decrypt(base64.b64decode(encpass))
    return decoded.strip()


def getlevelname(level):
    if str(level).lower() == 'full':
        return 'Full'
    if str(level).lower().startswith('incr'):
        return 'Incremental'
    if str(level).lower().startswith('diff'):
        return 'Differential'
    return 'Full'


def number2time(times='0:0', offset=0):
    (hours, minutes) = times.split(':', 1)
    hours = int(hours) + offset
    minutes = int(minutes)
    if hours > 23:
        hours -= 24
    return str(hours).zfill(2) + ':' + str(minutes).zfill(2)


def getscheduletext(data=None):
    if data is None:
        return ''
    (backupsch, backuprepeat) = data.split(':', 1)
    schrepeatdict = {
        'r1': 'Every hour',
        'r2': 'Every 2 hours',
        'r3': 'Every 3 hours',
        'r4': 'Every 4 hours',
        'r6': 'Every 6 hours',
        'r8': 'Every 8 hours',
        'r12': 'Every 12 hours',
        'r24': 'Once a day',
    }
    if backupsch == 'c1':
        return schrepeatdict[backuprepeat]
    schcycledict = {
        'c2': 'Weekly cycle',
        'c3': 'Monthly cycle'
    }
    return schcycledict[backupsch]


def getretentionform(pool):
    if pool is None or pool == '' or pool == 'Default' or pool == 'Scratch':
        return '2 weeks'
    data = pool.split('-')
    try:
        nr = data[1]
        inter = data[2]
    except IndexError:
        nr = '2'
        inter = 'weeks'
    return nr + ' ' + inter


def getretentiontext(pool):
    if pool is None or pool == '':
        return 'N/A'
    if pool == 'Default' or pool == 'Scratch':
        return pool
    return getretentionform(pool)
