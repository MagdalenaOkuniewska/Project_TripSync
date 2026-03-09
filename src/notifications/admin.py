from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipient",
        "sender",
        "notification_type",
        "trip",
        "is_read",
        "created_at",
    )
