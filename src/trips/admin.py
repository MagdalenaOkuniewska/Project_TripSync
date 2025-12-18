from django.contrib import admin
from .models import Trip, TripMember, TripInvite

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id',)

@admin.register(TripMember)
class TripMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip', 'user', 'role', 'joined_at')

@admin.register(TripInvite)
class TripInviteAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip','status', 'created_at', 'responded_at')
