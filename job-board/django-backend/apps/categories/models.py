import uuid
from django.db import models
from django.template.defaultfilters import slugify

class Category(models.Model):
    """
    Represents a job category (e.g., Software Development, Marketing, Design).
    Includes a slug for clean URLs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True, help_text="Name of the job category.")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL-friendly version of the category name.")
    description = models.TextField(blank=True, help_text="Optional description of the category.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date when the category was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when the category was last updated.")

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name'] 

    def __str__(self):
        """String representation of the Category."""
        return self.name

    def save(self, *args, **kwargs):
        """
        Overrides save to automatically generate a slug from the name
        if one isn't provided.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Location(models.Model):
    """
    Represents a geographical location for a job.
    Can be city, state/province, and country, or marked as remote.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=100, blank=True, null=True, help_text="City name for the job location.")
    state_province = models.CharField(max_length=100, blank=True, null=True, help_text="State or province name.")
    country = models.CharField(max_length=100, default='Kenya', help_text="Country name.") # Default to Kenya
    is_remote = models.BooleanField(default=False, help_text="Designates if the job is fully remote.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date when the location entry was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when the location entry was last updated.")

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        # Ensures uniqueness for non-remote locations
        unique_together = ('city', 'state_province', 'country', 'is_remote')
        ordering = ['country', 'state_province', 'city'] 

    def __str__(self):
        """String representation of the Location."""
        if self.is_remote:
            return "Remote"
        parts = [self.city] if self.city else []
        if self.state_province:
            parts.append(self.state_province)
        if self.country and self.country != 'Kenya': # Only add country if not default
            parts.append(self.country)
        return ", ".join(parts) if parts else "Location Not Specified"

