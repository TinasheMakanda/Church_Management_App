"""
users/serializers.py
---------------------
DRF Serializers for User and UserProfile.
Passwords are write-only and hashed via set_password().
"""

from rest_framework import serializers
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = [
            'id', 'ministry_title', 'ordination_date',
            'assigned_church', 'assigned_province', 'assigned_region',
            'facebook_url', 'instagram_url', 'twitter_url', 'youtube_url',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    profile  = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model  = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'username',
            'role', 'organization',
            'phone_number', 'address', 'date_of_birth',
            'profile_picture', 'bio',
            'is_active', 'password',
            'profile',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']
        extra_kwargs = {
            'organization': {'read_only': True},  # set by the view from request.user
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data['organization'] = self.context['request'].user.organization
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
