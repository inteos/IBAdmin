# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
import ssl
import socket
import hashlib
import random
import re


def countbytes(fbyte, bs):
    if bs == 'B':
        return int(float(fbyte))
    if bs == 'K':
        return int(float(fbyte) * 1024)
    if bs == 'M':
        return int(float(fbyte) * 1048576)
    if bs == 'G':
        return int(float(fbyte) * 1024 * 1048576)
    if bs == 'T':
        return int(float(fbyte) * 1048576 * 1048576)
    if bs == 'P':
        return int(float(fbyte) * 1024 * 1048576 * 1048576)
    return int(float(fbyte))


def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)


def getrandomnumber(length=8):
    return ''.join(random.choice("0123456789") for _ in range(length))


def truncateunicodestr(ustr, length):
    mystr = ustr
    while len(mystr.encode('utf-8')) > length:
        mystr = mystr[:-1]
    return mystr


def getstdtimetext(stime=None):
    if stime is None:
        return None
    return stime.strftime('%Y-%m-%d %H:%M:%S')


def urlparse(url):
    if url is None:
        return None, None
    port = 80
    addr = '127.0.0.1'
    s = re.search(r'^https://(.*):(\d+)/.*', url)
    if s is not None:
        addr, port = s.groups()
        return addr, port
    s = re.search(r'^https://(.*)/.*', url)
    if s is not None:
        port = 443
        addr = s.group(1)
        return addr, port
    s = re.search(r'^http://(.*):(\d+)/.*', url)
    if s is not None:
        addr, port = s.groups()
        return addr, port
    s = re.search(r'^http://(.*)/.*', url)
    if s is not None:
        port = 80
        addr = s.group(1)
    return addr, port


def getssltumbprint(addr, port=443):
    if type(addr) != str and type(addr) != unicode:
        return None
    if type(port) != int:
        port = int(port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(20)
    out = None
    wrappedSocket = ssl.wrap_socket(sock)
    try:
        wrappedSocket.connect((addr, port))
    except Exception as e:
        print ("getssltumbprint - %s" % str(e))
    else:
        der_cert_bin = wrappedSocket.getpeercert(True)
        thumb_sha1 = hashlib.sha1(der_cert_bin).hexdigest().upper()
        out = ':'.join([thumb_sha1[i:i+2] for i in range(0, len(thumb_sha1), 2)])
    wrappedSocket.close()
    return out


def sanitize_conf_string(confstr):
    confstr = confstr.replace('\\', "\\\\") # \ -> \\
    confstr = confstr.replace('\"', "\\\"") # " -> \"
