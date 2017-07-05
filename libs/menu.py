from __future__ import unicode_literals
from .job import updateJobsnr, updateJobsDefinednr
from .client import updateClientsDefinednr
from .storage import updateStorageDefinednr, updateStorageVolumesnr, updateStoragedetectdedup
from .task import updateTasksrunningall
from ibadmin.settings import STATIC_URL


def addhelpurl(context):
    context.update({'helpstaticurl': STATIC_URL + 'helps/'})


def updateMenuNumbers(context):
    updateJobsnr(context)
    updateJobsDefinednr(context)
    updateClientsDefinednr(context)
    updateStorageDefinednr(context)
    updateStorageVolumesnr(context)
    updateStoragedetectdedup(context)
    updateTasksrunningall(context)
    addhelpurl(context)
