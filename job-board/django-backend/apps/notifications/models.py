from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import CustomUser 
from django.utils import timezone
import uuid

class Notification(models.Model):
    """
    Represents a notification for a user.
    Uses GenericForeignKey to link to any specific object (e.g., Job, JobApplication).
    """
    NOTIFICATION_TYPE_CHOICES = (
        ('job_applied', 'Job Applied'),
        ('application_status_update', 'Application Status Update'),
        ('new_job_posting', 'New Job Posting'),
        ('company_review', 'Company Review'),
        ('message_received', 'Message Received'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('system_alert', 'System Alert'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        help_text="The user who receives the notification."
    )
    actor = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='initiated_notifications',
        help_text="The user who initiated the action (optional)."
    )
    type = models.CharField(
        max_length=50, 
        choices=NOTIFICATION_TYPE_CHOICES, 
        default='system_alert',
        help_text="Type of notification."
    )
    
    # Generic foreign key to link to any object (e.g., Job, JobApplication, Conversation)
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        help_text="The content type of the object this notification refers to."
    )
    object_id = models.UUIDField(help_text="The UUID of the object this notification refers to.")
    target = GenericForeignKey('content_type', 'object_id')

    message = models.TextField(help_text="The content of the notification message.")
    read = models.BooleanField(default=False, help_text="Indicates if the notification has been read by the recipient.")
    emailed = models.BooleanField(default=False, help_text="Indicates if an email notification has been sent.")
    in_app = models.BooleanField(default=True, help_text="Indicates if the notification is visible in-app.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the notification was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when the notification was last updated.")

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at'] 

    def __str__(self):
        """String representation of the Notification."""
        return f"Notification for {self.recipient.email}: {self.message[:50]}..."

