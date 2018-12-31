from django.conf.urls import url

from . import views
from users.views import login, logout

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^lastjobswidget/$', views.lastjobswidget, name='lastjobswidget'),
    url(r'^cpuutilwidget/$', views.cpuutilwidget, name='cpuutilwidget'),
    url(r'^backupsizewidget/$', views.backupsizewidget, name='backupsizewidget'),
    url(r'^runningjobswidget/$', views.runningjobswidget, name='runningjobswidget'),
    url(r'^alljobswidget/$', views.alljobswidget, name='alljobswidget'),
    url(r'^goeswrong/$', views.goeswrong, name='goeswrong'),
    url(r'^nodb/$', views.nodbavailable, name='nodbavailable'),
    url(r'^helppage/(?P<page>.*)/$', views.helppage, name='helppage'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^changewidgets/$', views.changewidgets, name='changewidgets_rel'),
    url(r'^changewidgets/(?P<sectionid>col1|col2)/$', views.changewidgets, name='changewidgets'),
]
