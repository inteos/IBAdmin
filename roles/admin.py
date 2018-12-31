from django.contrib import admin

# Register your models here.
from .models import Roles


@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('group', 'description', 'color', 'internal')
