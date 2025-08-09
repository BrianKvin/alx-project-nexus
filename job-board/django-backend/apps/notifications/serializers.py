from rest_framework import serializers
from .models import Notification
from apps.accounts.serializers import CustomUserSerializer # For recipient/actor details
from django.contrib.contenttypes.models import ContentType

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    Includes read-only nested recipient and actor details.
    """
    recipient = CustomUserSerializer(read_only=True)
    actor = CustomUserSerializer(read_only=True)

    # To display the type of the target object
    target_type = serializers.SerializerMethodField()
    # To display a basic representation of the target object (e.g., job title)
    target_representation = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'actor', 'type', 'message', 'read', 
            'emailed', 'in_app', 'created_at', 'updated_at',
            'content_type', 'object_id', 'target_type', 'target_representation'
        ]
        read_only_fields = [
            'id', 'recipient', 'actor', 'type', 'message', 
            'emailed', 'in_app', 'created_at', 'updated_at',
            'content_type', 'object_id', 'target_type', 'target_representation'
        ] # Most fields are set by the system

    def get_target_type(self, obj):
        if obj.target:
            return obj.content_type.model
        return None

    def get_target_representation(self, obj):
        if obj.target:
            return str(obj.target) # Returns the __str__ method of the target object
        return None