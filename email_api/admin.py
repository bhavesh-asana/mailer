from django.contrib import admin
from django import forms
from .models import EmailTemplate, Recipient, EmailCampaign, EmailLog, EmailConfiguration, EmailAttachment, TemplateAttachment


class EmailTemplateAdminForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_html'].widget = forms.HiddenInput()
        self.fields['is_html'].initial = True


class TemplateAttachmentInline(admin.TabularInline):
    model = TemplateAttachment
    extra = 0


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateAdminForm
    list_display = ['name', 'subject', 'is_html', 'created_by', 'created_at']
    list_filter = ['is_html', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TemplateAttachmentInline]
    
    class Media:
        css = {
            'all': ('admin/css/ckeditor-responsive.css',)
        }
        js = ('admin/js/ckeditor-width-fix.js',)
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'subject')
        }),
        ('Email Content', {
            'fields': ('body', 'is_html'),
            'description': 'Use the rich text editor below to format your email content with bold, italic, lists, links, colors, and more.'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        obj.is_html = True  # Always set to True for rich text
        super().save_model(request, obj, form, change)


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


class TemplateAttachmentInline(admin.TabularInline):
    model = TemplateAttachment
    extra = 0


@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_size_display', 'content_type', 'created_by', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['name', 'original_filename']
    readonly_fields = ['created_at', 'file_size_display', 'content_type']
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = 'File Size'
