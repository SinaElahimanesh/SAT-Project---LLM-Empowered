from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass  # Extend for custom fields if needed later

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.IntegerField()

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]} ({self.session_id})"
