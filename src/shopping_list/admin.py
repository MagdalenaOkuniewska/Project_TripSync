from django.contrib import admin
from .models import ShoppingItem, ShoppingList


@admin.register(ShoppingList)
class PackingListAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "created_at")


@admin.register(ShoppingItem)
class PackingItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "item_name",
        "item_quantity",
        "is_purchased",
        "added_by",
        "purchased_by",
    )
