from django.db import models
from apps.accounts.models import CustomUser 
import uuid

class Company(models.Model):
    """
    Represents a company that posts jobs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, db_index=True, help_text="Full name of the company.")
    description = models.TextField(blank=True, help_text="Detailed description of the company.")
    website = models.URLField(max_length=2000, blank=True, null=True, help_text="Official company website URL.")
    logo = models.ImageField(
        upload_to='company_logos/', 
        blank=True, 
        null=True,
        help_text="Company logo. (e.g., stored in S3/Cloud Storage)"
    )
    industry = models.CharField(max_length=100, blank=True, help_text="Industry the company operates in.")
    size = models.CharField(max_length=50, blank=True, help_text="Company size (e.g., '1-10', '11-50', '51-200', '201-500', '501-1000', '1000+').")
    headquarters = models.CharField(max_length=255, blank=True, help_text="Main office location of the company.")
    founded_year = models.PositiveSmallIntegerField(blank=True, null=True, help_text="Year the company was founded.")
    is_verified = models.BooleanField(default=False, help_text="Indicates if the company profile has been verified.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date when the company profile was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when the company profile was last updated.")

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name'] 

    def __str__(self):
        """String representation of the Company."""
        return self.name

class CompanyMember(models.Model):
    """
    Associates a CustomUser with a Company, defining their role within that company.
    This handles multiple recruiters per company or users associated with multiple companies.
    """
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('hiring_manager', 'Hiring Manager'),
        ('recruiter', 'Recruiter'),
    )

    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='company_memberships',
        help_text="The user associated with the company."
    )
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='members',
        help_text="The company this user is a member of."
    )
    role = models.CharField(
        max_length=50, 
        choices=ROLE_CHOICES, 
        default='recruiter',
        help_text="Role of the user within the company."
    )
    is_active = models.BooleanField(default=True, help_text="Indicates if the membership is currently active.")
    joined_at = models.DateTimeField(auto_now_add=True, help_text="Date when the user joined the company.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when the membership was last updated.")

    class Meta:
        verbose_name = 'Company Member'
        verbose_name_plural = 'Company Members'
        unique_together = ('user', 'company') # A user can only have one role per company
        ordering = ['company__name', 'user__email'] 

    def __str__(self):
        """String representation of the CompanyMember."""
        return f"{self.user.email} - {self.role} at {self.company.name}"


class Review(models.Model):
    """
    Allows users to leave reviews and ratings for companies.
    """
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        help_text="The company being reviewed."
    )
    reviewer = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, # If user is deleted, review remains but reviewer is null
        null=True, blank=True,
        related_name='company_reviews',
        help_text="The user who left the review."
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        help_text="Rating given to the company (1-5 stars)."
    )
    comment = models.TextField(blank=True, help_text="Optional text comment for the review.")
    is_approved = models.BooleanField(default=False, help_text="Indicates if the review has been approved by an admin.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date when the review was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when the review was last updated.")

    class Meta:
        verbose_name = 'Company Review'
        verbose_name_plural = 'Company Reviews'
        unique_together = ('company', 'reviewer') 
        ordering = ['-created_at'] 

    def __str__(self):
        """String representation of the Review."""
        reviewer_email = self.reviewer.email if self.reviewer else "Anonymous"
        return f"Review for {self.company.name} by {reviewer_email} - {self.rating} stars"

