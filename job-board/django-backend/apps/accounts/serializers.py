from rest_framework import serializers
from .models import CustomUser, Profile

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.
    Handles detailed user profile information.
    """
    # Exclude user field as it's typically set by the backend when creating/updating
    # Or, if user wants to update their own profile, it's implicit.
    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'phone_number', 'bio', 
            'profile_picture', 'user_type', 'resume', 'skills', 
            'experience', 'education', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user_type'] # user_type is often set once or by admin

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    Used for user registration, listing, and detail views.
    Includes nested Profile data.
    """
    profile = ProfileSerializer(read_only=True) # Nested serializer for the related profile
    # Using write_only password for security, won't be returned in responses
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'password', 'is_active', 'is_staff', 
            'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'is_active', 'is_staff', 'date_joined', 'last_login']

    def create(self, validated_data):
        """
        Custom create method to handle password hashing and profile creation.
        """
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create_user(email=validated_data['email'], password=password)
        # Create an associated profile for the new user
        Profile.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        """
        Custom update method to handle password hashing if password is provided.
        """
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for user registration (creating a new user).
    Includes password confirmation.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    user_type = serializers.ChoiceField(
        choices=Profile.USER_TYPE_CHOICES, 
        default='job_seeker', 
        write_only=True,
        help_text="Type of user being registered (job_seeker or recruiter)."
    )
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'password_confirm', 'user_type',
            'first_name', 'last_name'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True}
        }

    def validate(self, data):
        """
        Validates that passwords match.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """
        Creates a new CustomUser and their associated Profile during registration.
        """
        validated_data.pop('password_confirm') # Remove confirmation password
        user_type = validated_data.pop('user_type', 'job_seeker')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        Profile.objects.create(
            user=user, 
            user_type=user_type,
            first_name=first_name,
            last_name=last_name
        )
        return user