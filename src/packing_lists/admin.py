from django.contrib import admin
from .models import PackingList, PackingListTemplate, PackingItem, PackingItemTemplate


@admin.register(PackingListTemplate)
class PackingListTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "created_at")


@admin.register(PackingItemTemplate)
class PackingTemplateItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "quantity", "template")


@admin.register(PackingList)
class PackingListAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "list_type", "user", "created_at")


@admin.register(PackingItem)
class PackingItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "item_name",
        "item_quantity",
        "is_packed",
        "packing_lists",
        "added_by",
        "packed_by",
    )
