from django.db import models
from django.contrib.auth import get_user_model
from trips.models import Trip

User = get_user_model()


class Note(models.Model):
    NOTE_TYPE_CHOICES = [("private", "Private"), ("shared", "Shared")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="notes")

    title = models.CharField(max_length=200)
    note_type = models.CharField(
        max_length=10, choices=NOTE_TYPE_CHOICES, default="private"
    )
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def is_owner(self, user):
        return self.user == user

    def can_edit(self, user):
        return self.is_owner(user)

    def can_delete(self, user):
        return self.can_edit(user)

    def can_view(self, user):
        if self.note_type == "private":
            return self.is_owner(user)
        else:
            return self.trip.is_owner(user) or self.trip.is_participant(user)

    def __str__(self):
        return f" Note: {self.title} - Trip: {self.trip.title}"
