from django.contrib import admin

from .models import Trip, TripInvite, TripMember


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "destination", "start_date", "owner", "invite_token")


@admin.register(TripMember)
class TripMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "user", "role", "joined_at")


@admin.register(TripInvite)
class TripInviteAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "status", "created_at", "responded_at")
