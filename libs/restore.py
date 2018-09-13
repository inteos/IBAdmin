# coding=utf-8
from __future__ import unicode_literals
from datetime import *
import stat


FILETYPES = {
    'txt': 'fa fa-file-text-o',
    'log': 'fa fa-file-text-o',
    'pdf': 'fa fa-file-pdf-o',
    'zip': 'fa fa-file-archive-o',
    'gz': 'fa fa-file-archive-o',
    'tgz': 'fa fa-file-archive-o',
    'bz2': 'fa fa-file-archive-o',
    'jpg': 'fa fa-file-image-o',
    'jpeg': 'fa fa-file-image-o',
    'png': 'fa fa-file-image-o',
    'gif': 'fa fa-file-image-o',
    'ico': 'fa fa-file-image-o',
    'svg': 'fa fa-file-image-o',
    'c': 'fa fa-file-code-o',
    'cc': 'fa fa-file-code-o',
    'py': 'fa fa-file-code-o',
    'sh': 'fa fa-file-code-o',
    'exe': 'fa fa-file-code-o',
    'php': 'fa fa-file-code-o',
    'js': 'fa fa-file-code-o',
    'css': 'fa fa-file-code-o',
    'pl': 'fa fa-file-code-o',
    'pm': 'fa fa-file-code-o',
    'xls': 'fa fa-file-excel-o',
    'xlsx': 'fa fa-file-excel-o',
    'doc': 'fa fa-file-word-o',
    'docx': 'fa fa-file-word-o',
    'sxw': 'fa fa-file-word-o',
    'odt': 'fa fa-file-word-o',
    'ppt': 'fa fa-file-powerpoint-o',
    'pptx': 'fa fa-file-powerpoint-o',
    'ods': 'fa fa-file-powerpoint-o',
    'bsr': 'fa fa-map-o',
    'html': 'fa fa-file-text',
    'git': 'fa fa-git-square',
    'forward': 'fa fa-forward',
    'iso': 'fa fa-floppy-o',
    'mp4': 'fa fa-file-video-o',
    'mov': 'fa fa-file-video-o',
    'avi': 'fa fa-file-video-o',
    'mp3': 'fa fa-file-audio-o',
    'wav': 'fa fa-file-audio-o',
    'core': 'fa fa-bomb',
    'patch': 'fa fa-object-ungroup',
    'diff': 'fa fa-object-ungroup',
}


DIRTYPES = {
    'git': 'fa fa-git-square',
    'desktop': 'fa fa-desktop',
    'movies': 'fa fa-film',
    'music': 'fa fa-music',
    'pictures': 'fa fa-picture-o',
    'downloads': 'fa fa-download',
}


def filetypeicon(name=None):
    if name is None:
        return 'fa fa-file-o'
    ext = name.lower().split('.')[-1]
    return FILETYPES.get(ext, 'fa fa-file-o')


def dirtypeicon(name=None):
    if name is None:
        return 'fa fa-folder-o'
    ext = name.lower().split('.')[-1].replace('/','')
    return DIRTYPES.get(ext, 'fa fa-folder-o')


def fromb64(token=''):
    b64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    val = 0
    l = len(token)
    for i, c in enumerate(token):
        val += b64.find(c) * (64 ** (l - i - 1))
    return val


def decodelstat(lstat=None):
    if lstat is None:
        return ()
    llist = lstat.split()
    ltable = []
    for i, s in enumerate(llist):
        fr = fromb64(s)
        ltable.append(fr)
    return ltable


def getltable_mode(ltable=None):
    if ltable is None:
        return None
    return ltable[2]


def getltable_islink(ltable=None):
    if ltable is None:
        return None
    return stat.S_ISLNK(ltable[2])


def getltable_size(ltable=None):
    if ltable is None:
        return None
    return ltable[7]


def getltable_mtime(ltable=None):
    if ltable is None:
        return None
    return datetime.fromtimestamp(ltable[11])


def decodeperm(mode=None):
    perm = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    if mode is not None:
        if stat.S_ISDIR(mode):
            perm[0] = 'd'
        if stat.S_ISCHR(mode):
            perm[0] = 'c'
        if stat.S_ISBLK(mode):
            perm[0] = 'b'
        if stat.S_ISFIFO(mode):
            perm[0] = 'p'
        if stat.S_ISLNK(mode):
            perm[0] = 'l'
        if stat.S_ISSOCK(mode):
            perm[0] = 's'
        imode = stat.S_IMODE(mode)
        for a in range(0, 3):
            pmode = imode & 7
            if pmode & 4:
                perm[6 - a * 3 + 1] = 'r'   # 7
            if pmode & 2:
                perm[6 - a * 3 + 2] = 'w'   # 8
            if pmode & 1:
                perm[6 - a * 3 + 3] = 'x'   # 9
            imode = imode >> 3
        imode = stat.S_IMODE(mode)
        if imode & stat.S_ISUID:
            perm[3] = 's'
        if imode & stat.S_ISGID:
            perm[6] = 's'
        if imode & stat.S_ISVTX:
            perm[9] = 't'
    return ''.join(perm)
