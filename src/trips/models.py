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
    participants = models.ManyToManyField(User, related_name='trips', blank=True)
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
        return self.participants.filter(id=user.id).exists()

    def __str__(self):
        return f'{self.title} - {self.destination}'

