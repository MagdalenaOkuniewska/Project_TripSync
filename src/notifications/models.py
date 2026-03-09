from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from trips.models import Trip

User = get_user_model()


class Notification(models.Model):

    NOTIFICATION_TYPE_CHOICES = [
        ("trip_invite", "Trip Invite"),
        ("invite_accepted", "Invite Accepted"),
        ("invite_declined", "Invite Declined"),
        ("member_left", "Member Left the Trip"),
        ("member_removed", "Member Removed from the Trip"),
        ("trip_reminder", "Trip Reminder"),
    ]

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
    )
    notification_type = models.CharField(
        max_length=50, choices=NOTIFICATION_TYPE_CHOICES
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="trip_notifications",
    )

    message = models.TextField(blank=True, default="")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])

    def mark_as_unread(self):
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=["is_read", "read_at"])

    def __str__(self):
        return f"{self.notification_type} - {self.recipient.username}"
