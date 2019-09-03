# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from django.utils.deprecation import MiddlewareMixin
from .confinfo import getDIRcompid
from django.shortcuts import redirect
from django.urls import reverse


class ConfigMiddleware(MiddlewareMixin):
    def process_request(self, request):
        valid = [reverse('initial'), reverse('initialsetup'), reverse('initialsetup2'), reverse('initialarchivedir'),
                 reverse('initiallibdetect'), reverse('initialtaskprogress'), reverse('nodbavailable')]
        dbstatus = getDIRcompid(request)
        if request.path not in valid:
            if dbstatus == -1:
                print ("IBadmin is not configured!!")
                return redirect('initial')
            if dbstatus is None:
                print ("IBAdmin no DB available!!")
                return redirect('nodbavailable')
