"""ibadmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles import views
from django.conf.urls import handler404, handler500

urlpatterns = [
    url(r'^', include('dashboard.urls')),
    url(r'^jobs/', include('jobs.urls')),
    url(r'^clients/', include('clients.urls')),
    url(r'^storages/', include('storages.urls')),
    url(r'^initial/', include('initial.urls')),
    url(r'^tasks/', include('tasks.urls')),
    url(r'^stats/', include('stats.urls')),
    url(r'^restore/', include('restore.urls')),
    url(r'^config/', include('config.urls')),
    url(r'^system/', include('system.urls')),
]

handler404 = 'ibadmin.views.handler404'
handler500 = 'ibadmin.views.handler500'

if settings.DEBUG:
    from django.views.generic.base import TemplateView
    urlpatterns += [
        url(r'^admin/', admin.site.urls),
        url(r'^static/(?P<path>.*)$', views.serve),
        url(r'^404/$', TemplateView.as_view(template_name="404.html"), ),
        url(r'^500/$', TemplateView.as_view(template_name="500.html"), ),
    ]
