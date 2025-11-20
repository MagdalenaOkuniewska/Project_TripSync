from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    avatar = models.ImageField(default='', upload_to='profile_pics')


# Create your models here.
