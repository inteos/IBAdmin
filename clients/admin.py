from __future__ import unicode_literals
from django.contrib import admin

# Register your models here.
from .models import Client


admin.site.register(Client)
