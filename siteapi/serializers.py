from users.models import Community
from rest_framework import serializers

from users.models import Profile, Posts, User, Comments

class CommunitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['owner', 'name', 'slug', 'created_at']

class ProfileSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id',
            'bio',
            'phone_number',
            'gender',
            'profile_picture',
            'user_id'
        ]

class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = [
            'user',
            'community',
            'image',
            'description',
        ]

class UserSerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'posts_count']

class PostCommentsSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    post = serializers.ReadOnlyField(source="post.id")
    
    class Meta:
        model = Comments
        fields = ['id', 'user', 'post', 'text', 'created_at']

    def create(self, validated_data):
        return Comments.objects.create(**validated_data)