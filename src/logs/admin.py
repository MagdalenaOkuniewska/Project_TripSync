from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "action",
        "content_type",
        "object_id",
        "performed_by",
        "affected_user",
        "timestamp",
    )
    list_filter = ("action",)
    readonly_fields = (
        "content_type",
        "object_id",
        "content_object",
        "action",
        "performed_by",
        "affected_user",
        "timestamp",
        "extra_data",
    )
