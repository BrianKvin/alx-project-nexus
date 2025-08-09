from django.db import models
from apps.accounts.models import CustomUser 
from django.utils import timezone
import uuid

class PremiumPackage(models.Model):
    """
    Defines different premium packages available for purchase.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Name of the premium package (e.g., 'Basic', 'Standard', 'Premium').")
    description = models.TextField(blank=True, help_text="Detailed description of what the package offers.")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the package.")
    currency = models.CharField(max_length=10, default='KSh', help_text="Currency for the package price.")
    duration_days = models.PositiveIntegerField(help_text="Duration of the package in days (e.g., 30 for 1 month).")
    job_post_limit = models.PositiveIntegerField(
        default=0, 
        help_text="Number of job postings allowed with this package. 0 for unlimited."
    )
    featured_job_slots = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of jobs that can be featured with this package."
    )
    analytics_access = models.BooleanField(default=False, help_text="Does this package include access to advanced analytics?")
    is_active = models.BooleanField(default=True, help_text="Indicates if the package is currently available for purchase.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date when the package was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when the package was last updated.")

    class Meta:
        verbose_name = 'Premium Package'
        verbose_name_plural = 'Premium Packages'
        ordering = ['price'] # Order packages by price

    def __str__(self):
        """String representation of the PremiumPackage."""
        return f"{self.name} - {self.price} {self.currency}"

class UserSubscription(models.Model):
    """
    Tracks a user's active or past subscriptions to premium packages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='subscriptions',
        help_text="The user who holds this subscription."
    )
    package = models.ForeignKey(
        PremiumPackage, 
        on_delete=models.SET_NULL, # Keep subscription record if package is deleted
        null=True, blank=True,
        related_name='subscribers',
        help_text="The premium package associated with this subscription."
    )
    start_date = models.DateTimeField(default=timezone.now, help_text="Date when the subscription started.")
    end_date = models.DateTimeField(help_text="Date when the subscription will expire.")
    is_active = models.BooleanField(default=True, help_text="Indicates if the subscription is currently active.")
    auto_renew = models.BooleanField(default=False, help_text="Should the subscription automatically renew?")
    stripe_subscription_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="ID from payment gateway (e.g., Stripe) for this subscription."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date when the subscription record was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when the subscription record was last updated.")

    class Meta:
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'
        ordering = ['-start_date'] 

    def __str__(self):
        """String representation of the UserSubscription."""
        package_name = self.package.name if self.package else "N/A"
        return f"{self.user.email}'s subscription to {package_name}"

    @property
    def is_current(self):
        """Checks if the subscription is currently active and not expired."""
        return self.is_active and timezone.now() < self.end_date

class Payment(models.Model):
    """
    Records individual payment transactions made by users.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('card', 'Credit/Debit Card'),
        ('mpesa', 'M-Pesa'), # Common in Kenya
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, # Allow payment to remain if user is deleted
        related_name='payments',
        help_text="The user who made the payment."
    )
    subscription = models.ForeignKey(
        UserSubscription, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='payments',
        help_text="The subscription this payment is for (if applicable)."
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount of the payment.")
    currency = models.CharField(max_length=10, default='KSh', help_text="Currency of the payment.")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Current status of the payment transaction."
    )
    transaction_id = models.CharField(
        max_length=255, 
        unique=True, 
        blank=True, 
        null=True,
        help_text="Unique transaction ID from the payment gateway."
    )
    payment_method = models.CharField(
        max_length=50, 
        choices=PAYMENT_METHOD_CHOICES,
        help_text="Method used for the payment."
    )
    payment_gateway_response = models.JSONField(
        blank=True, 
        null=True,
        help_text="Raw JSON response from the payment gateway for auditing."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the payment record was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when the payment record was last updated.")

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at'] 

    def __str__(self):
        """String representation of the Payment."""
        user_email = self.user.email if self.user else "Anonymous"
        return f"Payment of {self.amount} {self.currency} by {user_email} ({self.status})"

