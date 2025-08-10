from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid
from django.core.validators import RegexValidator
from django.conf import settings

# Custom User Manager to handle user creation
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as the primary identifier.
    Inherits from AbstractBaseUser for core authentication fields
    and PermissionsMixin for Django's permission system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True, help_text="User's unique email address.")
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active. "
                  "Unselect this instead of deleting accounts."
    )
    date_joined = models.DateTimeField(default=timezone.now, help_text="Date when the user account was created.")
    last_login = models.DateTimeField(null=True, blank=True, help_text="Last time the user logged in.")
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # No required fields beyond email for superuser creation

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined'] 

    def __str__(self):
        """String representation of the CustomUser."""
        return self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        (Typically pulled from the related Profile model for non-admin users)
        """
        if hasattr(self, 'profile'):
            return self.profile.full_name
        return self.email 

    def get_short_name(self):
        """
        Returns the short name for the user.
        (Typically pulled from the related Profile model)
        """
        return self.email.split('@')[0]

# User Profile Model

class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True,
        help_text="Profile picture of the user. (e.g., stored in S3/Cloud Storage)"
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='job_seeker',
    )

    # Fields specific to Job Seekers
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)

    # Fields specific to Recruiters
    company_name = models.CharField(max_length=255, blank=True, help_text="Recruiter's company name")
    company_website = models.URLField(blank=True, help_text="Company website")
    company_description = models.TextField(blank=True, help_text="Brief description of the company")
    position = models.CharField(max_length=100, blank=True, help_text="Recruiter's job title or role in company")
    linkedin_profile = models.URLField(blank=True, help_text="Recruiter's LinkedIn URL")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['user__email']

    def __str__(self):
        return f"{self.user.email}'s Profile"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()