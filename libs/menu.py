from __future__ import unicode_literals
from .job import updateJobsnr, updateJobsDefinednr
from .client import updateClientsDefinednr
from .storage import updateStorageDefinednr, updateStorageVolumesnr, updateStoragedetectdedup
from .task import updateTasksrunningall
from .plat import IBADVERSION


def updateMenuNumbers(context):
    updateJobsnr(context)
    updateJobsDefinednr(context)
    updateClientsDefinednr(context)
    updateStorageDefinednr(context)
    updateStorageVolumesnr(context)
    updateStoragedetectdedup(context)
    updateTasksrunningall(context)
    context['ibadminver'] = IBADVERSION
