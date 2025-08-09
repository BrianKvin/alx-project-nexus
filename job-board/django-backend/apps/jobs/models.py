from django.db import models
from apps.accounts.models import CustomUser
from apps.companies.models import Company
from apps.categories.models import Category, Location
from django.utils import timezone
import uuid

class Job(models.Model):
    """
    Represents a job listing posted on the platform.
    """
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
    )

    EXPERIENCE_LEVEL_CHOICES = (
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('director', 'Director'),
        ('executive', 'Executive'),
    )

    SOURCE_CHOICES = (
        ('manual', 'Manual Entry'),
        ('scraped', 'Web Scraped'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, db_index=True, help_text="Title of the job position.")
    description = models.TextField(help_text="Full description of the job responsibilities and requirements.")
    job_type = models.CharField(
        max_length=20, 
        choices=JOB_TYPE_CHOICES, 
        default='full_time',
        help_text="Type of employment (e.g., full-time, part-time)."
    )
    salary_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Minimum annual salary for the position."
    )
    salary_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Maximum annual salary for the position."
    )
    currency = models.CharField(
        max_length=10, 
        default='KSh', # Default to Kenyan Shillings
        help_text="Currency for the salary (e.g., USD, KSh)."
    )
    experience_level = models.CharField(
        max_length=20, 
        choices=EXPERIENCE_LEVEL_CHOICES, 
        default='mid',
        help_text="Required experience level for the job."
    )
    posted_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, # Allow job to remain if poster is deleted
        related_name='posted_jobs',
        help_text="The user who posted this job listing."
    )
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='jobs',
        help_text="The company offering this job."
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='jobs',
        help_text="The category this job belongs to."
    )
    location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='jobs',
        help_text="The geographical location of the job."
    )
    is_active = models.BooleanField(default=True, help_text="Indicates if the job listing is currently active and visible.")
    application_deadline = models.DateTimeField(blank=True, null=True, help_text="Deadline for submitting applications.")
    external_application_url = models.URLField(
        max_length=2000, 
        blank=True, 
        null=True,
        help_text="URL for external application portal, if applicable."
    )
    source = models.CharField(
        max_length=10, 
        choices=SOURCE_CHOICES, 
        default='manual',
        help_text="Origin of the job listing (manual entry or web scraped)."
    )
    original_url = models.URLField(
        max_length=2000, 
        blank=True, 
        null=True,
        help_text="Original URL of the job if it was web scraped."
    )
    views_count = models.PositiveIntegerField(default=0, help_text="Number of times the job listing has been viewed.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date when the job listing was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when the job listing was last updated.")

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the Job."""
        return f"{self.title} at {self.company.name}"

    @property
    def is_expired(self):
        """Checks if the application deadline has passed."""
        if self.application_deadline:
            return timezone.now() > self.application_deadline
        return False # No deadline means it's not expired by deadline

class JobApplication(models.Model):
    """
    Represents a job application submitted by a job seeker for a specific job.
    """
    APPLICATION_STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('interview', 'Interview Scheduled'),
        ('offer', 'Offer Extended'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(
        Job, 
        on_delete=models.CASCADE, 
        related_name='applications',
        help_text="The job to which this application pertains."
    )
    applicant = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='job_applications',
        help_text="The user who submitted this application."
    )
    # Resume and cover letter can be directly attached or link to Profile fields
    # Here, allowing specific application documents for flexibility
    resume_file = models.FileField(
        upload_to='application_resumes/', 
        blank=True, 
        null=True,
        help_text="Applicant's resume for this specific application. (e.g., stored in S3/Cloud Storage)"
    )
    cover_letter_text = models.TextField(blank=True, help_text="Applicant's cover letter for this specific application.")
    
    status = models.CharField(
        max_length=20, 
        choices=APPLICATION_STATUS_CHOICES, 
        default='pending',
        help_text="Current status of the job application."
    )
    applied_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the application was submitted.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when the application status was last updated.")

    class Meta:
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
        unique_together = ('job', 'applicant') # A user can only apply to a job once
        ordering = ['-applied_at'] # Order applications by most recent

    def __str__(self):
        """String representation of the JobApplication."""
        return f"Application for {self.job.title} by {self.applicant.email} ({self.status})"

