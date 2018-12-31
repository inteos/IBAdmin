# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from .conflib import *
from .confinfo import *


def createDIRJobDefs(dircompid=None, name='jd-default', descr='', btype='Backup', fileset=None, level=None, pool=None,
                     schedule=None, storage=None, client=None, priority=10, dirjob=None, beforejob=None, afterjob=None,
                     allowduplicatejob='No', writebootstrap='/opt/bacula/bsr/%c-%n.bsr', accurate=True):
    if dircompid is None:
        dircompid = getDIRcompid()
    # create new JobDefs {} resource
    resid = createDIRresJobDefs(dircompid, name, descr)
    # add parameters
    addparameter(resid, 'Type', btype)
    if btype == 'Backup' and accurate:
        addparameter(resid, 'Accurate', 'Yes')
    addparameter(resid, 'AllowDuplicateJobs', allowduplicatejob)
    addparameter(resid, 'CancelQueuedDuplicates', 'Yes')
    addparameter(resid, 'SpoolAttributes', 'Yes')     # TODO trzeba zastanowić się jak rozwiązać problem Tape=SpoolData
    addparameter(resid, 'Priority', priority)
    addparameterstr(resid, 'Messages', 'Standard')
    addparameterstr(resid, 'WriteBootstrap', writebootstrap)
    if level is not None:
        addparameter(resid, 'Level', level)
    if pool is not None:
        addparameterstr(resid, 'Pool', pool)
    if fileset is not None:
        addparameterstr(resid, 'Fileset', fileset)
    if schedule is not None:
        addparameterstr(resid, 'Schedule', schedule)
    if storage is not None:
        addparameterstr(resid, 'Storage',  storage)
    if client is not None:
        addparameterstr(resid, 'Client', client)
    if beforejob is not None:
        addparameterstr(resid, 'ClientRunBeforeJob', beforejob)
    if dirjob is not None:
        addparameterstr(resid, 'RunBeforeJob', dirjob)
    if afterjob is not None:
        addparameterstr(resid, 'ClientRunAfterJob', afterjob)


def createDIRJobDefsCatalog(dircompid=None, storage='ibadmin'):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-catalog', descr='Catalog Backup Defs', priority=20,
                     fileset='fs-catalog-backup', schedule='sch-backup-catalog', storage=storage,
                     beforejob='/opt/bacula/scripts/make_catalog_backup_ibadmin.pl Catalog',
                     afterjob='/opt/bacula/scripts/delete_catalog_backup_ibadmin',
                     writebootstrap='/opt/bacula/bsr/SYS-Backup-Catalog.bsr')


def createDIRJobDefsRestore(dircompid=None, client='ibadmin', storage='ibadmin'):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-restore', btype='Restore', descr='Required Restore Job',
                     fileset='fs-default', level='Full', pool='Default', storage=storage, client=client)


def createDIRJobDefsAdmin(dircompid=None, client='ibadmin', storage='ibadmin'):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-admin', btype='Admin', descr='AdminJob Defs',
                     fileset='fs-default', level='Full', pool='Default', storage=storage, client=client,
                     dirjob='/opt/bacula/scripts/SYS-Admin.sh', schedule='sch-admin')


def createDIRJobDefsFiles(dircompid=None):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-files', descr='Backup Files Defs', level='Incremental')


def createDIRJobDefsProxmox(dircompid=None):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-proxmox', descr='Backup Proxmox Defs', level='Full',
                     accurate=False)


def createDIRJobDefsESX(dircompid=None):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-esx', descr='Backup VMware ESX Defs', level='Incremental')


def createDIRJobDefsXEN(dircompid=None):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-xen', descr='Backup XenServer Defs', level='Full',
                     accurate=False)


def createDIRJobDefsKVM(dircompid=None):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-kvm', descr='Backup KVM Defs', level='Incremental',
                     accurate=False)


def createDIRJobDefsPGSQL(dircompid=None):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-pgsql', descr='Backup PostgreSQL Defs', level='Incremental')


def createDIRJobDefsMySQL(dircompid=None):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-mysql', descr='Backup MySQL Defs', level='Incremental')


def createDIRJobDefsOracle(dircompid=None):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-oracle', descr='Backup Oracle Defs', level='Incremental')


def createDIRJobDefsMSSQL(dircompid=None):
    # create JobDefs
    createDIRJobDefs(dircompid=dircompid, name='jd-backup-mssql', descr='Backup MSSQL VDI Defs', level='Incremental')


def createDIRAllJobDefs(dircompid=None):
    createDIRJobDefsFiles(dircompid)
    createDIRJobDefsProxmox(dircompid)
    createDIRJobDefsXEN(dircompid)
    createDIRJobDefsESX(dircompid)
    createDIRJobDefsKVM(dircompid)
    createDIRJobDefsPGSQL(dircompid)
    createDIRJobDefsMySQL(dircompid)
    createDIRJobDefsOracle(dircompid)
    createDIRJobDefsMSSQL(dircompid)


def checkDIRProxmoxJobDef(dircompid=None):
    if getDIRJobDefs(dircompid, 'jd-backup-proxmox') is None:
        createDIRJobDefsProxmox(dircompid)


def checkDIRVMwareJobDef(dircompid=None):
    if getDIRJobDefs(dircompid, 'jd-backup-esx') is None:
        createDIRJobDefsESX(dircompid)


def checkDIRXenServerJobDef(dircompid=None):
    if getDIRJobDefs(dircompid, 'jd-backup-xen') is None:
        createDIRJobDefsXEN(dircompid)


def checkDIRKVMJobDef(dircompid=None):
    if getDIRJobDefs(dircompid, 'jd-backup-kvm') is None:
        createDIRJobDefsKVM(dircompid)

