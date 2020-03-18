from django.contrib import admin

# Register your models here.

from .models import Package, PkgFile

admin.site.register(Package)
admin.site.register(PkgFile)