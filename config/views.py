from django.shortcuts import render, get_object_or_404
from django.template import loader, Context
from django.http import HttpResponse
from libs.client import *
from libs.conf import getdecpass


# Create your views here.
def clientconfig(request, name):
    client = get_object_or_404(ConfComponent, name=name, type='F')
    dirres = ConfResource.objects.get(compid__name=name, compid__type='F', type__name='Director')
    dirp = ConfParameter.objects.filter(resid=dirres)
    dirparams = {}
    for p in dirp:
        if p.name.startswith('.'):
            continue
        if p.name == 'Password':
            encpass = p.value
            password = getdecpass(name, encpass)
            dirparams['Password'] = password
        else:
            dirparams[p.name] = p.value
    fdres = ConfResource.objects.get(compid__name=name, compid__type='F', type__name='FileDaemon')
    fdp = ConfParameter.objects.filter(resid=fdres)
    fdparams = {}
    for p in fdp:
        if p.name.startswith('.'):
            continue
        else:
            fdparams[p.name] = p.value

    messres = ConfResource.objects.get(compid__name=name, compid__type='F', type__name='Messages')
    messp = ConfParameter.objects.filter(resid=messres)
    messparams = {}
    for p in messp:
        if p.name.startswith('.'):
            continue
        else:
            messparams[p.name] = p.value

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="bacula-fd.conf"'
    temp = loader.get_template('config/bacula-fd.txt')
    context = Context({
        'Dir': dirres,
        'Dirparams': dirparams,
        'FD': fdres,
        'FDparams': fdparams,
        'Mess': messres,
        'Messparams': messparams,
    })
    response.write(temp.render(context))
    return response
