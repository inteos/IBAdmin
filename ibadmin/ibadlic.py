# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from config.conflib import *
from config.confinfo import *


def saveLicenseKey(key=None):
    if key is None:
        return
    dircompid = getDIRcompid()
    dirname = getDIRname()
    resid = getresourceid(dircompid, dirname, 'Director')
    license = getparameter(resid, '.IBADLicenseKey')
    if license is None:
        if key == '':
            return
        addparameter(resid, '.IBADLicenseKey', key)
    else:
        if key == '':
            deleteparameter(resid, '.IBADLicenseKey')
        updateparameterresid(resid, '.IBADLicenseKey', key)


def getLicenseKey():
    dircompid = getDIRcompid()
    dirname = getDIRname()
    resid = getresourceid(dircompid, dirname, 'Director')
    return getparameter(resid, '.IBADLicenseKey')
