from django.utils.deprecation import MiddlewareMixin
from .confinfo import isConfigured
from django.shortcuts import redirect
from django.urls import reverse


class ConfigMiddleware(MiddlewareMixin):
    def process_request(self, request):
        valid = [reverse('initial'), reverse('initialsetup'), reverse('initialarchivedir')]
        if request.path not in valid and not isConfigured():
            print "IBadmin is not configured!!"
            return redirect('initial')
