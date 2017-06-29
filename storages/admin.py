from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Pool)
admin.site.register(Device)
admin.site.register(Media)
admin.site.register(Jobmedia)
