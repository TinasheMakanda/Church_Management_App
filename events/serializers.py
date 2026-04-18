"""
events/serializers.py
----------------------
Serializers for Event.
The scope field drives which province/church FKs are required.
"""

from rest_framework import serializers
from .models import Event, EventScope


class EventSerializer(serializers.ModelSerializer):
    created_by_name   = serializers.CharField(source='created_by.full_name', read_only=True, default='')
    organizer_groups  = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    scope_display     = serializers.CharField(source='get_scope_display', read_only=True)
    status_display    = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model  = Event
        fields = [
            'id', 'organization',
            'scope', 'scope_display', 'province', 'church',
            'title', 'description', 'banner', 'status', 'status_display',
            'start_datetime', 'end_datetime',
            'venue_name', 'venue_address', 'is_online', 'stream_url', 'max_attendance',
            'budget',
            'created_by', 'created_by_name',
            'organizer_groups',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']

    def validate(self, data):
        scope   = data.get('scope', EventScope.LOCAL)
        province = data.get('province')
        church   = data.get('church')

        if scope == EventScope.PROVINCIAL and not province:
            raise serializers.ValidationError(
                "A province is required for PROVINCIAL events."
            )
        if scope == EventScope.LOCAL and not church:
            raise serializers.ValidationError(
                "A church is required for LOCAL events."
            )
        if scope == EventScope.INTERNATIONAL:
            data['province'] = None
            data['church']   = None

        start = data.get('start_datetime')
        end   = data.get('end_datetime')
        if start and end and end <= start:
            raise serializers.ValidationError(
                "end_datetime must be after start_datetime."
            )

        return data


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight list view."""
    class Meta:
        model  = Event
        fields = ['id', 'title', 'scope', 'status', 'start_datetime', 'end_datetime', 'is_online']
