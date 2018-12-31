# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class Roles(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField()
    color = models.CharField(max_length=20, default='bg-blue')
    internal = models.BooleanField(default=False)


@receiver(post_save, sender=Group)
def create_group_roles(sender, instance, created, **kwargs):
    if created:
        Roles.objects.create(group=instance)


@receiver(post_save, sender=Group)
def save_group_roles(sender, instance, **kwargs):
    instance.roles.save()


class Permissions(models.Model):
    class Meta:
        managed = False
        permissions = (
            ('view_roles', 'Can view roles'),
            ('add_roles', 'Can add roles'),
            ('change_roles', 'Can change roles'),
            ('delete_roles', 'Can delete roles'),
        )
