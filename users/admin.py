from django.contrib import admin
from django.contrib.auth import get_user_model

user = get_user_model()


@admin.register(user)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'first_name', 'last_name']
