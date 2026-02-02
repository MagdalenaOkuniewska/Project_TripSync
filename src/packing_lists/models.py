from django.db import models
from django.contrib.auth import get_user_model
from trips.models import Trip

User = get_user_model()


class PackingListTemplate(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="packing_templates"
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PackingItemTemplate(models.Model):
    template = models.ForeignKey(
        PackingListTemplate, on_delete=models.CASCADE, related_name="item_templates"
    )
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name}: x{self.quantity}"


# trip może mieć tylko 1 shared liste, stworzona TYLKO przez owner
# trip może mieć tylko 1 private list per member
class PackingList(models.Model):
    LIST_TYPE_CHOICES = [("private", "Private"), ("shared", "Shared")]

    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name="packing_lists"
    )
    list_type = models.CharField(max_length=20, choices=LIST_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    # for private list
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="private_packing_lists",
    )

    class Meta:
        ordering = ["list_type", "-created_at"]


class PackingItem(models.Model):
    packing_list = models.ForeignKey(
        PackingList, on_delete=models.CASCADE, related_name="items"
    )
    item_name = models.CharField(max_length=100)
    item_quantity = models.IntegerField(default=1)
    is_packed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # for shared list
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="added_items",
    )
    packed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="packed_items",
    )

    class Meta:
        ordering = ["-is_packed", "-created_at"]

    def marked_as_packed(self, user):
        self.is_packed = True

        if self.packing_list.list_type == "shared" and user:
            self.packed_by = user

        self.save()
