from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.defined, name='rolesdefined'),
    url(r'^data/$', views.defineddata, name='rolesdefineddata'),
    url(r'^info/$', views.info, name='rolesinfo_rel'),
    url(r'^info/(?P<rolename>.*)/$', views.info, name='rolesinfo'),
    url(r'^add/$', views.addrole, name='rolesadd'),
    url(r'^edit/$', views.editrole, name='rolesedit_rel'),
    url(r'^edit/(?P<rolename>.*)/$', views.editrole, name='rolesedit'),
    url(r'^rolename/$', views.rolesname, name='rolesname'),
    url(r'^rolenameother/(?P<rolename>.*)/$', views.rolesnameother, name='rolesnameother'),
    url(r'^delete/$', views.rolesdelete, name='rolesdelete_rel'),
    url(r'^delete/(?P<rolename>.*)/$', views.rolesdelete, name='rolesdelete'),
    url(r'^infoperms/(?P<rolename>.*)/$', views.infoperms, name='rolesinfoperms'),
    url(r'^addperms/(?P<rolename>.*)/$', views.addperms, name='rolesaddperms'),
    url(r'^deleteperms/(?P<rolename>.*)/(?P<applabel>.*)/(?P<perms>.*)/$', views.deleteperms, name='rolesdeleteperms'),
    url(r'^deleteperms/(?P<rolename>.*)/$', views.deleteperms, name='rolesdeleteperms_rel'),
]

