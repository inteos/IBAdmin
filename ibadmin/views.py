# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from __future__ import unicode_literals
from django.shortcuts import render
from django.http import JsonResponse
from libs.menu import updateMenuNumbers
from libs.system import *


def handler404(request):
    context = {}
    updateMenuNumbers(request, context)
    updateservicestatus(context)
    return render(request, '404.html', context)


def handler500(request):
    context = {}
    updateMenuNumbers(request, context)
    updateservicestatus(context)
    return render(request, '500.html', context)


def ibadmin_css(request):
    return render(request, 'ibadmin.css', {})


def ibadmin_js(request):
    return render(request, 'ibadmin.js', {})


def address(request):
    """ JSON for host address """
    addr = request.GET.get('address', '')
    return JsonResponse(checkAddress(addr), safe=False)
