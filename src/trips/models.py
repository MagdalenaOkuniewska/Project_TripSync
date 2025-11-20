from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Trip(models.Model):
    title = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE) # TODO logika przy zapisie, że ustawia zalogowane użytkowniak jako owern'a.