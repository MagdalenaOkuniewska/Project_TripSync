from django.contrib import admin
from .models import Trip, TripMember

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id',)

@admin.register(TripMember)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip', 'user', 'role', 'joined_at')