# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from departments.models import Departments
from dashboard.models import Widgets
from libs.dashbrd import getdashboarddefault


class Dashboardwidgets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    widget = models.ForeignKey(Widgets, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Departments)
    dashboardcol1 = models.TextField(blank=True, null=True)
    dashboardcol2 = models.TextField(blank=True, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        pcol1, pcol2 = getdashboarddefault()
        Profile.objects.create(user=instance, dashboardcol1=pcol1, dashboardcol2=pcol2)
        widgets = Widgets.objects.all()
        for w in widgets:
            Dashboardwidgets.objects.create(user=instance, widget=w)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Permissions(models.Model):
    class Meta:
        managed = False
        permissions = (
            ('view_users', 'Can view users'),
            ('add_users', 'Can add users'),
            ('change_users', 'Can change users'),
            ('delete_users', 'Can delete users'),
            ('suspend_users', 'Can suspend users'),
        )
