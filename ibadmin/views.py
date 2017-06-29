from __future__ import unicode_literals
# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponseServerError, JsonResponse
from libs.menu import updateMenuNumbers
from libs.statistic import *
from libs.system import *
from jobs.models import Job
from config.models import *


def handler404(request):
    context = {}
    updateMenuNumbers(context)
    updateservicestatus(context)
    return render(request, '404.html', context)


def handler500(request):
    context = {}
    updateMenuNumbers(context)
    updateservicestatus(context)
    return render(request, '500.html', context)

