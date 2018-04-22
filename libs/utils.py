# -*- coding: UTF-8 -*-
from __future__ import unicode_literals


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
