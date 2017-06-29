from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(ConfComponent)
class ConfComponentAdmin(admin.ModelAdmin):
    list_display = ('compid', 'name', 'type')


@admin.register(ConfResource)
class ConfResourceAdmin(admin.ModelAdmin):
    list_display = ('resid', 'name', 'description', 'sub')


@admin.register(ConfParameter)
class ConfParameterAdmin(admin.ModelAdmin):
    list_display = ('parid', 'name', 'value', 'str')


@admin.register(ConfRtype)
class ConfRtypeAdmin(admin.ModelAdmin):
    list_display = ('typeid', 'name')


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ('versionid',)


