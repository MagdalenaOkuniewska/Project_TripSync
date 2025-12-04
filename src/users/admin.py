from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser


admin.site.register(CustomUser, CustomUserAdmin)

