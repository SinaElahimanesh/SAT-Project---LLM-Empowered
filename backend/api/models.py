from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum

class Stage(str, Enum):
    BEGINNING = "Beginning"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class User(AbstractUser):
    stage = models.CharField(
        max_length=20,
        choices=Stage.choices(),
        default=Stage.BEGINNING
    )

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.IntegerField()
    is_user = models.BooleanField(default=True)  # True if message is from user, False if from LLM

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]} ({self.session_id})"

class UserMemoryState(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="memory_state")
    current_memory = models.TextField(default="")  # Stores the LLM-generated memory
    last_processed_message = models.ForeignKey(
        Message, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="last_processed"
    )

    def __str__(self):
        return f"Memory state for {self.user.username}"
