"""
groups/serializers.py
----------------------
Serializers for ChurchGroup and GroupMembership.
"""

from rest_framework import serializers
from .models import ChurchGroup, GroupMembership


class GroupMembershipSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model  = GroupMembership
        fields = ['id', 'group', 'user', 'user_name', 'is_co_leader', 'joined', 'notes']
        read_only_fields = ['id', 'joined']


class ChurchGroupSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(source='members.count', read_only=True)
    leader_name   = serializers.CharField(source='leader.full_name', read_only=True, default='')

    class Meta:
        model  = ChurchGroup
        fields = [
            'id', 'organization', 'church', 'leader', 'leader_name',
            'group_type', 'name', 'description', 'is_active',
            'meeting_day', 'meeting_time', 'meeting_location',
            'meeting_online', 'meeting_url',
            'members_count', 'events',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']
