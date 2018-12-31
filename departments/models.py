from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Departments(models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField()
    shortname = models.CharField(max_length=8, unique=True)
    color = models.CharField(max_length=20, default='bg-blue')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Permissions(models.Model):
    class Meta:
        managed = False
        permissions = (
            ('view_departments', 'Can view departments'),
            ('add_departments', 'Can add departments'),
            ('change_departments', 'Can change departments'),
            ('delete_departments', 'Can delete departments'),
            ('add_members', 'Can add memebers'),
            ('delete_members', 'Can delete members'),
        )
