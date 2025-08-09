from rest_framework import serializers
from .models import Category, Location

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at'] # Slug is auto-generated

class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Location model.
    """
    class Meta:
        model = Location
        fields = ['id', 'city', 'state_province', 'country', 'is_remote', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']