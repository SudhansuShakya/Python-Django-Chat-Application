from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15,null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    def __str__(self):
        return f"Profile of {self.user.username}"
