from rest_framework import serializers
from .models import Job, JobApplication
from apps.companies.serializers import CompanySerializer # Assuming CompanySerializer exists
from apps.categories.serializers import CategorySerializer, LocationSerializer # Assuming these exist
from apps.accounts.serializers import CustomUserSerializer # To display posted_by user

class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for the Job model.
    Includes nested serializers for related Company, Category, and Location.
    """
    company = CompanySerializer(read_only=True) # Nested, read-only serializer
    category = CategorySerializer(read_only=True) # Nested, read-only serializer
    location = LocationSerializer(read_only=True) # Nested, read-only serializer
    posted_by = CustomUserSerializer(read_only=True) # Nested, read-only for who posted it

    # Writeable fields for FKs, allowing creation/update via ID
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), 
        write_only=True, 
        source='company',
        help_text="UUID of the company posting the job."
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        write_only=True, 
        allow_null=True, 
        required=False, 
        source='category',
        help_text="UUID of the job category."
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), 
        write_only=True, 
        allow_null=True, 
        required=False, 
        source='location',
        help_text="UUID of the job location."
    )

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'job_type', 'salary_min', 
            'salary_max', 'currency', 'experience_level', 'is_active', 
            'application_deadline', 'external_application_url', 
            'source', 'original_url', 'views_count', 'created_at', 
            'updated_at', 'is_expired',
            'company', 'category', 'location', 'posted_by',
            'company_id', 'category_id', 'location_id' # For writing
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'views_count', 
            'is_expired', 'source', 'original_url', 'posted_by'
        ]

class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the JobApplication model.
    Includes read-only nested job and applicant details.
    """
    job = JobSerializer(read_only=True) # Nested, read-only job details
    applicant = CustomUserSerializer(read_only=True) # Nested, read-only applicant details

    class Meta:
        model = JobApplication
        fields = [
            'id', 'status', 'applied_at', 'updated_at', 
            'resume_file', 'cover_letter_text',
            'job', 'applicant'
        ]
        read_only_fields = ['id', 'applied_at', 'updated_at', 'status', 'job', 'applicant']

class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for creating a new JobApplication.
    The job is linked via its ID in the URL, and applicant is set automatically.
    """
    class Meta:
        model = JobApplication
        fields = ['resume_file', 'cover_letter_text'] # Only these are provided by the applicant
    
    # Custom validation for resume_file if it's not always required but useful
    def validate(self, data):
        if not data.get('resume_file') and not self.context.get('request').user.profile.resume:
            raise serializers.ValidationError(
                {"resume_file": "Resume file is required for application if not present in profile."}
            )
        return data

