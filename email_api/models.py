from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.storage import default_storage
from django_ckeditor_5.fields import CKEditor5Field
import json
import os


class EmailTemplate(models.Model):
    """Model for storing email templates with rich formatting"""
    name = models.CharField(max_length=200, unique=True)
    subject = models.CharField(max_length=500)
    body = CKEditor5Field(
        config_name='email_template',
        help_text="Use the rich text editor to format your email content with bold, italic, lists, links, etc."
    )
    is_html = models.BooleanField(default=True, help_text="Automatically set to True when using rich text editor")
    
    # Rich text formatting options
    FORMATTING_HELP = """
    HTML Formatting Guide:
    - Bold: <b>text</b> or <strong>text</strong>
    - Italic: <i>text</i> or <em>text</em>
    - Underline: <u>text</u>
    - Line break: <br>
    - Paragraph: <p>text</p>
    - Headers: <h1>Large</h1>, <h2>Medium</h2>, <h3>Small</h3>
    - Lists: <ul><li>Item 1</li><li>Item 2</li></ul>
    - Numbered: <ol><li>Item 1</li><li>Item 2</li></ol>
    - Links: <a href="url">link text</a>
    - Colors: <span style="color: red;">red text</span>
    """
    
    # Template variables help
    VARIABLES_HELP = """
    Available Variables:
    - $name - Recipient display name
    - $first_name - Recipient first name
    - $last_name - Recipient last name
    - $email - Recipient email
    - $company - Recipient company
    - Custom variables can be added in API calls
    """
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class EmailAttachment(models.Model):
    """Model for storing email attachments"""
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='email_attachments/%Y/%m/%d/')
    content_type = models.CharField(max_length=100, blank=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.name = self.name or self.file.name
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.get_file_size_display()})"
    
    def get_file_size_display(self):
        """Human readable file size"""
        if not self.file_size:
            return "Unknown size"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"
    
    def get_absolute_path(self):
        """Get absolute file path for email attachment"""
        if self.file and default_storage.exists(self.file.name):
            return default_storage.path(self.file.name)
        return None
    
    class Meta:
        ordering = ['-created_at']


class TemplateAttachment(models.Model):
    """Many-to-many relationship between templates and attachments"""
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, related_name='attachments')
    attachment = models.ForeignKey(EmailAttachment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('template', 'attachment')


class Recipient(models.Model):
    """Model for storing recipient information"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True, help_text="Display name")
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=200, blank=True)
    additional_data = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-generate display name if not provided
        if not self.name and (self.first_name or self.last_name):
            name_parts = [self.first_name, self.last_name]
            self.name = ' '.join(filter(None, name_parts))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} <{self.email}>" if self.name else self.email
    
    class Meta:
        ordering = ['name', 'email']


class EmailCampaign(models.Model):
    """Model for email campaigns"""
    name = models.CharField(max_length=200)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=500)
    body = models.TextField()
    is_html = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('paused', 'Paused'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class EmailLog(models.Model):
    """Model for logging email sending activities"""
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, null=True, blank=True)
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=200, blank=True)
    subject = models.CharField(max_length=500)
    body = models.TextField()
    is_html = models.BooleanField(default=False)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Email metadata
    attachments = models.JSONField(default=list, blank=True)
    email_metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Email to {self.recipient_email} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']


class SequentialEmailCampaign(models.Model):
    """Model for sequential email campaigns with time intervals between recipients"""
    name = models.CharField(max_length=200)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient, through='SequentialEmailRecipient')
    
    # Interval settings
    interval_minutes = models.IntegerField(
        default=10,
        help_text="Time interval in minutes between each email"
    )
    
    # Start time - split into separate date and time fields to avoid Django datetime widget issues
    start_date = models.DateField(help_text="Date to start sending emails", null=True, blank=True)
    start_time = models.TimeField(help_text="Time to start sending the first email", null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_recipients = models.IntegerField(default=0)
    emails_sent = models.IntegerField(default=0)
    emails_failed = models.IntegerField(default=0)
    current_recipient_index = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} (Sequential - {self.interval_minutes}min intervals)"
    
    @property
    def start_datetime(self):
        """Combine date and time fields into a timezone-aware datetime object"""
        if self.start_date and self.start_time:
            from datetime import datetime
            from django.utils import timezone
            # Create naive datetime first
            naive_dt = datetime.combine(self.start_date, self.start_time)
            # Make it timezone-aware using the default timezone
            return timezone.make_aware(naive_dt, timezone.get_current_timezone())
        return None
    
    def get_next_send_time(self):
        """Calculate when the next email should be sent"""
        if self.current_recipient_index == 0:
            return self.start_datetime
        
        from datetime import timedelta
        return self.start_datetime + timedelta(
            minutes=self.interval_minutes * self.current_recipient_index
        )
    
    def get_recipient_schedule(self):
        """Get the complete schedule for all recipients"""
        recipients = self.sequential_recipients.all().order_by('send_order')
        schedule = []
        
        for i, seq_recipient in enumerate(recipients):
            from datetime import timedelta
            send_time = self.start_datetime + timedelta(minutes=self.interval_minutes * i)
            schedule.append({
                'recipient': seq_recipient.recipient,
                'send_order': seq_recipient.send_order,
                'scheduled_time': send_time,
                'status': seq_recipient.status
            })
        
        return schedule
    
    class Meta:
        ordering = ['-created_at']


class SequentialEmailRecipient(models.Model):
    """Through model for sequential email campaigns with send order"""
    campaign = models.ForeignKey(
        SequentialEmailCampaign, 
        on_delete=models.CASCADE,
        related_name='sequential_recipients'
    )
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    send_order = models.IntegerField(help_text="Order in which to send emails (0-based)")
    
    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timing
    scheduled_time = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.campaign.name} → {self.recipient.email} (Order: {self.send_order})"
    
    class Meta:
        ordering = ['send_order']
        unique_together = ('campaign', 'recipient')


class ScheduledEmailCampaign(models.Model):
    """Model for scheduled email campaigns with intervals"""
    name = models.CharField(max_length=200)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient, blank=True)
    
    # Scheduling options
    INTERVAL_CHOICES = [
        ('once', 'Send Once'),
        ('hourly', 'Every Hour'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES, default='once')
    
    # Date/time settings
    scheduled_datetime = models.DateTimeField(help_text="When to start sending emails")
    end_datetime = models.DateTimeField(null=True, blank=True, help_text="When to stop recurring emails (optional)")
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    next_send_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_sent = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} ({self.get_interval_display()})"
    
    def save(self, *args, **kwargs):
        # Calculate next_send_at based on interval
        if self.scheduled_datetime and self.status in ['scheduled', 'active']:
            if self.interval == 'once':
                self.next_send_at = self.scheduled_datetime
            elif not self.next_send_at:
                self.next_send_at = self.scheduled_datetime
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']


class EmailConfiguration(models.Model):
    """Model for storing email server configurations"""
    name = models.CharField(max_length=200, unique=True)
    smtp_server = models.CharField(max_length=200)
    smtp_port = models.IntegerField(default=587)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=500)  # Should be encrypted in production
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default configuration
            EmailConfiguration.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.smtp_server})"
    
    class Meta:
        ordering = ['-is_default', 'name']
