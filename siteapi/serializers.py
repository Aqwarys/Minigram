from users.models import Community
from rest_framework import serializers

from users.models import Profile

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