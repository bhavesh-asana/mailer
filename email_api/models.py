from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class EmailTemplate(models.Model):
    """Model for storing email templates"""
    name = models.CharField(max_length=200, unique=True)
    subject = models.CharField(max_length=500)
    body = models.TextField()
    is_html = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class Recipient(models.Model):
    """Model for storing recipient information"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    additional_data = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
