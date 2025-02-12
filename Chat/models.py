from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Chats can be private (1-on-1) or group chats. You can differentiate by checking the number of participants in the chat.
class Group(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)  # Group chat name, null for private chats
    is_group = models.BooleanField(default=False)  # Indicates if this is a group chat
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    admin = models.ForeignKey(User, related_name='admin_chats', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name if self.is_group else f"Private Chat {self.id}"

    def get_last_message(self):
        return self.messages.order_by('-created_at').first()

    def get_unread_count(self, user):
        return self.messages.filter(is_read=False, users=user).count()

    def get_other_participants(self, user):
        """Get all participants except the given user"""
        return self.users.exclude(id=user.id)

# To manage users in a chat, you'll need a many-to-many relationship between User and Chat.
class GroupParticipant(models.Model):
    group = models.ForeignKey(Group, related_name="participants", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="chat_participants", on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(default=timezone.now)
    left_at = models.DateTimeField(null=True, blank=True)
    # class Meta:
        # unique_together = ('user', 'chat')
    def __str__(self):
        return f"{self.user.username} in {self.chat.name}"
    def leave_chat(self):
        self.left_at = timezone.now()
        self.save()

class GroupMessage(models.Model):
    sender = models.ForeignKey(User, related_name='group_sent_messages', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    message_type = models.CharField(max_length=20, choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video')])

    def __str__(self):
        return f"GroupMessage from {self.sender.username} in {self.chat_room.name}"

# Model to represent a message sent in a chat
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)  # Text content of the message
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    media = models.ForeignKey('MediaFile', null=True, blank=True, on_delete=models.SET_NULL)  # Reference to media file if any
    read_at = models.DateTimeField(blank=True, null=True)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE, null=True, blank=True)
    message_type = models.CharField(max_length=20, choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video'), ('document', 'Document')], default='text')

    def __str__(self):
        return f"{self.id} - Message by  {self.sender.username} to {self.recipient.username} at {self.timestamp}"
    def mark_as_read(self):
        self.is_read = True
        self.save()
    # def save(self):
    #     channel_layer = get_channel_layer()
    #     user_id=self.recipient.id
    #     message=self.content
    #     channel_layer.group_send(
    #         f'notifications_{user_id}',
    #         {
    #             'type':'receive',
    #             'message':message
    #         }
    #     )

# Model to represent files (images, videos, documents, etc.)
class MediaFile(models.Model):
    file = models.FileField(upload_to='chat_media/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'gif', 'mp4', 'pdf', 'docx'])])
    file_type = models.CharField(max_length=20, choices=[('image', 'Image'), ('video', 'Video'), ('document', 'Document')])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} in message {self.message.id}"

# Optional: Model to store user's online status
class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=[('online', 'Online'), ('offline', 'Offline'), ('away', 'Away')], default='offline')
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} is {self.status}"

# Model to store notifications for users (like new messages)
class Notification(models.Model):
    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name="notifications", on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)
    notified_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Notification for {self.user.username} regarding message {self.message.id}"

    def mark_as_read(self):
        self.read_at = timezone.now()
        self.save()


class TypingIndicator(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    is_typing = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} typing in {self.chat.name}"