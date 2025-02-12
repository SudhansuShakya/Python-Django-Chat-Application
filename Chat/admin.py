from django.contrib import admin

# Register your models here.
from .models import Message

# admin.site.register(Chat)
# admin.site.register(ChatParticipant)
admin.site.register(Message)