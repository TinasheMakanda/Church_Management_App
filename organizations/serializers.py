"""
organizations/serializers.py
-----------------------------
DRF Serializers for the full hierarchy:
    Organization → Region → Province → Church
"""

from rest_framework import serializers
from .models import Organization, Region, Province, Church


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Organization
        fields = [
            'id', 'name', 'slug', 'logo', 'website', 'description',
            'email', 'phone_number', 'address', 'country',
            'status', 'payment_provider',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        # payment_metadata deliberately omitted — sensitive, served via a
        # dedicated admin-only endpoint.


class RegionSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    leader_name       = serializers.CharField(source='leader.full_name', read_only=True, default='')

    class Meta:
        model  = Region
        fields = [
            'id', 'organization', 'organization_name',
            'leader', 'leader_name',
            'name', 'description', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class ProvinceSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    region_name       = serializers.CharField(source='region.name', read_only=True)
    leader_name       = serializers.CharField(source='leader.full_name', read_only=True, default='')

    class Meta:
        model  = Province
        fields = [
            'id', 'organization', 'organization_name',
            'region', 'region_name',
            'leader', 'leader_name',
            'name', 'description', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class ChurchSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    province_name     = serializers.CharField(source='province.name', read_only=True)
    leader_name       = serializers.CharField(source='leader.full_name', read_only=True, default='')

    class Meta:
        model  = Church
        fields = [
            'id', 'organization', 'organization_name',
            'province', 'province_name',
            'leader', 'leader_name',
            'name', 'description', 'logo', 'website',
            'email', 'phone_number', 'address', 'city', 'country',
            'seating_capacity', 'service_times',
            'is_active', 'payment_provider',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class ChurchListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views — avoids over-fetching."""
    province_name = serializers.CharField(source='province.name', read_only=True)

    class Meta:
        model  = Church
        fields = ['id', 'name', 'province_name', 'city', 'is_active', 'leader']
