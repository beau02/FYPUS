from django.contrib.auth.models import User
from django.db import models
from .utils import detect_threat, generate_recommendation

# User Profile model to store additional user information
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

# Threat model to store security threat information
class Threat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    threat_type = models.CharField(max_length=100)
    details = models.TextField()
    detection_time = models.DateTimeField()

    def __str__(self):
        return f"{self.threat_type} detected for {self.user.username}"

# ChatHistory model to store user interactions with the chatbot
class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.user.username} on {self.timestamp}"

    @staticmethod
    def calculate_threat_level(user):
        """Calculate the threat level based on the number of threats."""
        total_threats = Threat.objects.filter(user=user).count()
        if total_threats <= 3:
            return "Low"
        elif 4 <= total_threats <= 7:
            return "Medium"
        else:
            return "High"

    @staticmethod
    def monitor_and_detect(user):
        """Monitor the system, detect threats, and save them."""
        from .utils import monitor_system

        # Monitor system activity
        system_data = monitor_system()

        # Detect threats using AI
        threat_description = detect_threat(system_data)

        # Generate recommendations
        recommendation = generate_recommendation(threat_description)

        # Save the detected threat
        threat = Threat.objects.create(
            user=user,
            threat_type="System Threat",  # Example type, can be dynamic
            details=threat_description,
            detection_time=timezone.now()
        )
        return threat
