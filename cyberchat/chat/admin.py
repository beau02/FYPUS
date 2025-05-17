from django.contrib import admin
from .models import UserProfile, ChatHistory, Threat

admin.site.register(UserProfile)
admin.site.register(ChatHistory)
admin.site.register(Threat)
