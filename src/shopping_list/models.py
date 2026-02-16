from django.db import models
from django.contrib.auth import get_user_model
from trips.models import Trip

User = get_user_model()


class ShoppingList(models.Model):
    trip = models.OneToOneField(
        Trip, on_delete=models.CASCADE, related_name="shopping_list"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f" {self.trip.title} Shopping list"


class ShoppingItem(models.Model):
    shopping_list = models.ForeignKey(
        ShoppingList, on_delete=models.CASCADE, related_name="shopping_items"
    )
    item_name = models.CharField(max_length=100)
    item_quantity = models.IntegerField(default=1)
    is_purchased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="added_shopping_items",
    )
    purchased_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="purchased_items",
    )

    class Meta:
        ordering = ["is_purchased", "-created_at"]

    def marked_as_purchased(self, user):
        self.is_purchased = True

        self.purchased_by = user
        self.save()

    def __str__(self):
        return f"{self.item_name} x{self.item_quantity}"
