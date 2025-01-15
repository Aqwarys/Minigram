from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.



class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    id_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(blank=True, null=True, max_length=15)
    date_of_birth = models.DateField(blank=True, null=True)
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True, null=True)

class Statistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    posts_count = models. IntegerField(default=0)
