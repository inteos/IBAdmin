# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'user'), "The Login Required middleware\
         requires authentication middleware to be installed. Edit your\
         MIDDLEWARE_CLASSES setting to insert\
         'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
         work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
         'django.core.context_processors.auth'."
        valid = [reverse('login'), reverse('logout'), reverse('initial'), reverse('initialsetup'),
                 reverse('initialarchivedir'), reverse('initiallibdetect'), reverse('initialtaskprogress'),
                 reverse('initialsetup2')]
        if not request.user.is_authenticated():
            path = request.path
            if path not in valid:
                response = redirect('login')
                response['Location'] += '?' + urlencode({'next': path})
                return response
