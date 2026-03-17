from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from notifications.models import Notification
from logs.utils import log_action

User = get_user_model()


class Trip(models.Model):
    title = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_trips"
    )

    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start date must be before end date")

    def save(self, *args, **kwargs):
        self.validate_dates()
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            TripMember.objects.create(trip=self, user=self.owner, role="owner")

    def is_owner(self, user):
        return self.owner == user

    def is_participant(self, user):
        return self.members.filter(user=user).exists()

    def has_shopping_list(self):
        try:
            return self.shopping_list is not None
        except Exception:
            return False

    def __str__(self):
        return f"{self.title} - {self.destination}"


class TripMember(models.Model):
    ROLE_CHOICES = [("owner", "Owner"), ("member", "Member")]

    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name="members"
    )  # trip.members.all()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="trip_memberships"
    )
    role = models.CharField(
        max_length=50, choices=ROLE_CHOICES, default="member", null=True, blank=True
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-joined_at"]
        unique_together = [("trip", "user")]  # to avoid duplicates

    def save(self, *args, **kwargs):
        if self.user == self.trip.owner:
            self.role = "owner"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.trip.title}"

    def leave(self):
        if self.role == "owner":
            raise ValidationError("Owner cannot leave the trip.")

        Notification.objects.create(
            recipient=self.trip.owner,
            sender=self.user,
            notification_type="member_left",
            trip=self.trip,
            message=f'{self.user.username} left your trip "{self.trip.title}".',
        )

        log_action(
            action="member_left",
            content_object=self.trip,
            performed_by=self.user,
            affected_user=self.user,
        )
        self.delete()

    def remove(self, performed_by):
        if self.role == "owner":
            raise ValidationError("Cannot remove the owner from the trip.")

        Notification.objects.create(
            recipient=self.user,
            sender=performed_by,
            notification_type="member_removed",
            trip=self.trip,
            message=f'You have been removed from "{self.trip.title}" by {performed_by.username}.',
        )

        log_action(
            action="member_removed",
            content_object=self.trip,
            performed_by=performed_by,
            affected_user=self.user,
        )

        self.delete()


class TripInvite(models.Model):
    STATUS_CHOICES = [
        ("accepted", "Accepted"),
        ("pending", "Pending"),
        ("declined", "Declined"),
        ("expired", "Expired"),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="invites")

    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="send_trip_invites"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="trip_invites"
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("trip", "user")]

    def is_expired(self):
        if self.status == "pending" and self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def accept(self):
        if self.status != "pending":
            raise ValidationError("Trip must be in pending state to accept.")

        if self.is_expired():
            self.status = "expired"
            self.save()
            raise ValidationError("This invitation has expired.")

        self.status = "accepted"
        self.responded_at = timezone.now()
        self.save()

        TripMember.objects.get_or_create(
            trip=self.trip, user=self.user, defaults={"role": "member"}
        )

        Notification.objects.create(
            recipient=self.trip.owner,
            sender=self.user,
            notification_type="invite_accepted",
            trip=self.trip,
            message=f"{self.user.username} accepted your invitation to {self.trip.title}.",
        )

        log_action(
            action="member_added",
            content_object=self.trip,
            performed_by=self.user,
            affected_user=self.user,
        )

    def decline(self):
        if self.status != "pending":
            raise ValidationError("Trip must be in pending state to decline.")

        self.status = "declined"
        self.responded_at = timezone.now()
        self.save()

        Notification.objects.create(
            recipient=self.trip.owner,
            sender=self.user,
            notification_type="invite_declined",
            trip=self.trip,
            message=f"{self.user.username} declined your invitation to {self.trip.title}.",
        )

    def mark_expired(self) -> bool:
        if self.is_expired():
            self.status = "expired"
            self.save(update_fields=["status"])
            return True  # marked as expired
        return False  # invie is not expired - done nothing

    def cancel(self) -> None:
        if self.status != "pending":
            raise ValidationError(
                f"Cannot cancel invitation that is in {self.status} state"
            )
        self.delete()

    def __str__(self) -> str:
        return f"{self.user.username} invited to {self.trip.title} - {self.status}"
