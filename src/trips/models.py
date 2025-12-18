from random import choice
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Trip(models.Model):
    title = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_trips')

    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('Start date must be before end date')

    def save(self, *args, **kwargs):
        self.validate_dates()
        super().save(*args, **kwargs)

    def is_owner(self, user):
        return self.owner == user

    def is_participant(self, user):
        return self.members.filter(user=user).exists()

    def __str__(self):
        return f'{self.title} - {self.destination}'

class TripMember(models.Model):
    ROLE_CHOICES = [('owner', 'Owner'),
                    ('member', 'Member')]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='members') # trip.members.all()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_memberships')
    role = models.CharField(max_length=50, choices= ROLE_CHOICES, default='member', null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-joined_at']
        unique_together = [('trip', 'user')]

    def save(self, *args, **kwargs):
        if self.user == self.trip.owner:
            self.role = 'owner'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} - {self.trip.title}'


class TripInvite(models.Model):
    STATUS_CHOICES = [('accepted', 'Accepted'),
                      ('pending', 'Pending'),
                      ('declined', 'Declined'),
                      ('expired', 'Expired')
                      ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='invites')

    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='send_trip_invites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_invites')
    status =  models.CharField(max_length=30, choices= STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [('trip', 'user')]

    def is_expired(self):
        if self.status == 'pending' and self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def accept(self):
        if self.status != 'pending':
            raise ValidationError('Trip must be in pending state to accept.')

        if self.is_expired():
            self.status = 'expired'
            self.save()
            raise ValidationError('This invitation has expired.')

        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()

        TripMember.objects.get_or_create(
            trip=self.trip,
            user=self.user,
            defaults={'role': 'member'}
        )

    def decline(self):
        if self.status != 'pending':
            raise ValidationError('Trip must be in pending state to decline.')

        self.status = 'declined'
        self.responded_at = timezone.now()
        self.save()

    def mark_expired(self) -> bool:
        if self.is_expired():
            self.status = 'expired'
            self.save(update_fields=['status'])
            return True #marked as expired
        return False #invie is not expired - done nothing

    def cancel(self) -> None:
        if self.status != 'pending':
            raise ValidationError(f'Cannot cancel invitation that is in {self.status} state')
        self.delete()

    def __str__(self) -> str:
        return f'{self.user.username} invited to {self.trip.title} - {self.status}'