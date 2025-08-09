from django.db import models
from apps.accounts.models import CustomUser
from django.utils import timezone
import uuid

class Conversation(models.Model):
    """
    Represents a private conversation between two or more users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(
        CustomUser, 
        related_name='conversations',
        help_text="Users involved in this conversation."
    )
    last_message_at = models.DateTimeField(
        null=True, 
        blank=True, 
        db_index=True,
        help_text="Timestamp of the last message in the conversation for ordering."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date when the conversation was initiated.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when the conversation was last updated.")

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-last_message_at', '-created_at'] 

    def __str__(self):
        """String representation of the Conversation."""
        # Display participants' emails for easy identification
        participants_emails = ", ".join([p.email for p in self.participants.all()])
        return f"Conversation with: {participants_emails}"

class Message(models.Model):
    """
    Represents an individual message within a conversation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages',
        help_text="The conversation this message belongs to."
    )
    sender = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        help_text="The user who sent this message."
    )
    content = models.TextField(help_text="The text content of the message.")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, help_text="Date and time when the message was sent.")
    is_read = models.BooleanField(default=False, help_text="Indicates if the message has been read by all recipients.")

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['timestamp'] # Order messages chronologically within a conversation

    def __str__(self):
        """String representation of the Message."""
        return f"Message from {self.sender.email} in {self.conversation.id}: {self.content[:50]}..."

    def save(self, *args, **kwargs):
        """
        Overrides save to update the last_message_at timestamp on the related conversation.
        """
        super().save(*args, **kwargs)
        self.conversation.last_message_at = self.timestamp
        self.conversation.save(update_fields=['last_message_at'])

