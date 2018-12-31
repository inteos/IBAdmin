from __future__ import unicode_literals
from django.db import models


# Create your models here.
class Widgets(models.Model):
    name = models.TextField(unique=True)
    icon = models.CharField(max_length=32)
    widgetid = models.CharField(unique=True, blank=False, max_length=32)
    template = models.TextField(blank=False)
    templatejs = models.TextField(blank=False)
    height = models.IntegerField(null=True, default=189)

    class Meta:
        ordering = ('id',)
