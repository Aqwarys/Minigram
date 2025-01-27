from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property

from django.core.validators import MaxLengthValidator
from django.utils.text import slugify

# Create your models here.



class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    id_verified = models.BooleanField(default=False)


    @property
    def posts_count(self):
        return self.posts.count()

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()


    def __str__(self) -> str:
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default='default_avatars/default_pfp.png')
    phone_number = models.CharField(blank=True, null=True, max_length=15)
    date_of_birth = models.DateField(blank=True, null=True)
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True, null=True)

class Followers(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('follower', 'following')

class Community(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True, validators=[MaxLengthValidator(500)])
    avatar = models.ImageField(upload_to='community_avatars/', blank=True, null=True, default='default_avatars/community.png')
    banner = models.ImageField(upload_to='community_banners/', blank=True, null=True, default='default_avatars/community_banner.png')
    link = models.URLField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def following_count(self):
        return self.community.count()


class Community_Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community')
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'community')  # Один пользователь может подписаться только один раз.

    def __str__(self):
        return f"{self.user.username} follows {self.community.name}"

class Posts(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts'
    )
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name='posts', null=True, blank=True
    )
    image = models.ImageField(upload_to='post_images/')
    likes = models.ManyToManyField(User, through='Likes', related_name='liked_posts')
    bookmarks = models.ManyToManyField(User, through='Bookmark', related_name='bookmarked_posts')
    description = models.TextField(max_length=600, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.user.username} - {self.id}"


class Comments(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on Post {self.post.id}"


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='post_likes')

    class Meta:
        unique_together = ('user', 'post')


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self) -> str:
        return f"{self.user.username} bookmarked {self.post.title}"
