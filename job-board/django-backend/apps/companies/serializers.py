from rest_framework import serializers
from .models import Company, CompanyMember, Review
from apps.accounts.serializers import CustomUserSerializer # For reviewer/user details
from apps.accounts.models import CustomUser # For creating CompanyMember

class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for the Company model.
    Includes average rating for display.
    """
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True, default=0.0)
    # Count of reviews
    review_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'website', 'logo', 'industry', 
            'size', 'headquarters', 'founded_year', 'is_verified', 
            'created_at', 'updated_at', 'average_rating', 'review_count'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at', 'average_rating', 'review_count']

class CompanyMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for the CompanyMember model.
    Includes nested user details.
    """
    user = CustomUserSerializer(read_only=True) # Nested, read-only user details
    company = CompanySerializer(read_only=True) # Nested, read-only company details

    # Writeable fields for FKs, allowing creation/update via ID
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), 
        write_only=True, 
        source='user',
        help_text="UUID of the user being added/modified."
    )
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), 
        write_only=True, 
        source='company',
        help_text="UUID of the company the user is associated with."
    )

    class Meta:
        model = CompanyMember
        fields = [
            'id', 'role', 'is_active', 'joined_at', 'updated_at', 
            'user', 'company', 'user_id', 'company_id' # For writing
        ]
        read_only_fields = ['id', 'joined_at', 'updated_at']

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    Includes nested reviewer and company details (read-only).
    """
    reviewer = CustomUserSerializer(read_only=True) # Nested, read-only reviewer details
    company = CompanySerializer(read_only=True) # Nested, read-only company details

    # Writeable field for company FK
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), 
        write_only=True, 
        source='company',
        help_text="UUID of the company being reviewed."
    )

    class Meta:
        model = Review
        fields = [
            'id', 'rating', 'comment', 'is_approved', 'created_at', 
            'updated_at', 'reviewer', 'company', 'company_id' # For writing
        ]
        read_only_fields = ['id', 'is_approved', 'created_at', 'updated_at', 'reviewer']

