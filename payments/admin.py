from django.contrib import admin

from .models import MangoNaturalUser


@admin.register(MangoNaturalUser)
class AMNU(admin.ModelAdmin):
    list_display = ['mid']
