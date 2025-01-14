from django.contrib.auth.models import User
from django.db import models

# User Profile model to store additional user information
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

# ChatHistory model to store user interactions with the chatbot
class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.user.username} on {self.timestamp}"

# ThreatDetection model to store security threat information
class ThreatDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    detection_time = models.DateTimeField(auto_now_add=True)  # This is your timestamp field
    threat_type = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return f"{self.threat_type} detected for {self.user.username}"

