from django.contrib import admin
from .models import EmailTemplate, Recipient, EmailCampaign, EmailLog, EmailConfiguration


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'is_html', 'created_by', 'created_at']
    list_filter = ['is_html', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'company', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email', 'name', 'company']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'template', 'created_by', 'created_at', 'started_at']
    list_filter = ['status', 'created_at', 'started_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at', 'started_at', 'completed_at']


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'subject', 'status', 'campaign', 'sent_at']
    list_filter = ['status', 'sent_at', 'created_at']
    search_fields = ['recipient_email', 'recipient_name', 'subject']
    readonly_fields = ['created_at', 'sent_at']
    
    def has_add_permission(self, request):
        # Email logs should only be created programmatically
        return False


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'smtp_server', 'smtp_port', 'username', 'use_tls', 'is_active', 'is_default']
    list_filter = ['use_tls', 'use_ssl', 'is_active', 'is_default']
    search_fields = ['name', 'smtp_server', 'username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_active', 'is_default')
        }),
        ('SMTP Configuration', {
            'fields': ('smtp_server', 'smtp_port', 'username', 'password', 'use_tls', 'use_ssl')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
