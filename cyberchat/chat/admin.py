from django.contrib import admin
from .models import UserProfile, ChatHistory, ThreatDetection

admin.site.register(UserProfile)
admin.site.register(ChatHistory)
admin.site.register(ThreatDetection)
