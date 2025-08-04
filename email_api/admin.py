from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path, reverse
from django.utils.html import format_html
from django.db import transaction
from .models import EmailTemplate, Recipient, EmailCampaign, EmailLog, EmailConfiguration, EmailAttachment, TemplateAttachment
from .forms import BulkImportRecipientsForm


class EmailTemplateAdminForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_html'].widget = forms.HiddenInput()
        self.fields['is_html'].initial = True
        
        # Add help text for placeholders with inline buttons
        placeholder_help = """
        <div style="margin-top: 10px; padding: 10px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;">
            <strong>Available Placeholders:</strong>
            <div style="margin: 8px 0;">
                <button type="button" onclick="insertPlaceholder('$name')" style="margin: 2px; padding: 4px 8px; background: #007cba; color: white; border: none; border-radius: 3px; font-size: 11px; cursor: pointer;">
                    📋 $name
                </button>
                <button type="button" onclick="insertPlaceholder('$first_name')" style="margin: 2px; padding: 4px 8px; background: #007cba; color: white; border: none; border-radius: 3px; font-size: 11px; cursor: pointer;">
                    👤 $first_name
                </button>
                <button type="button" onclick="insertPlaceholder('$last_name')" style="margin: 2px; padding: 4px 8px; background: #007cba; color: white; border: none; border-radius: 3px; font-size: 11px; cursor: pointer;">
                    👤 $last_name
                </button>
                <button type="button" onclick="insertPlaceholder('$email')" style="margin: 2px; padding: 4px 8px; background: #007cba; color: white; border: none; border-radius: 3px; font-size: 11px; cursor: pointer;">
                    📧 $email
                </button>
                <button type="button" onclick="insertPlaceholder('$company')" style="margin: 2px; padding: 4px 8px; background: #007cba; color: white; border: none; border-radius: 3px; font-size: 11px; cursor: pointer;">
                    🏢 $company
                </button>
            </div>
            <div style="margin-top: 8px; font-size: 12px; color: #666;">
                Click a button to insert at cursor position, or see descriptions below:
            </div>
            <ul style="margin: 5px 0; padding-left: 20px; font-size: 12px;">
                <li><code>$name</code> - Display name (e.g., "John Doe")</li>
                <li><code>$first_name</code> - First name (e.g., "John")</li>
                <li><code>$last_name</code> - Last name (e.g., "Doe")</li>
                <li><code>$email</code> - Email address</li>
                <li><code>$company</code> - Company name</li>
            </ul>
            
            <script>
            function insertPlaceholder(placeholder) {
                console.log('Inserting placeholder:', placeholder);
                
                // Try CKEditor 5 first
                if (window.editor && window.editor.model) {
                    window.editor.model.change(writer => {
                        const insertPosition = window.editor.model.document.selection.getFirstPosition();
                        writer.insertText(placeholder, insertPosition);
                    });
                    return;
                }
                
                // Try to find CKEditor instance
                const ckInstances = window.CKEDITOR?.instances;
                if (ckInstances) {
                    const editorName = Object.keys(ckInstances)[0];
                    if (editorName && ckInstances[editorName]) {
                        ckInstances[editorName].insertText(placeholder);
                        return;
                    }
                }
                
                // Fallback to textarea
                const bodyField = document.querySelector('#id_body, textarea[name="body"]');
                if (bodyField) {
                    const cursorPos = bodyField.selectionStart;
                    const textBefore = bodyField.value.substring(0, cursorPos);
                    const textAfter = bodyField.value.substring(cursorPos);
                    bodyField.value = textBefore + placeholder + textAfter;
                    bodyField.focus();
                    bodyField.setSelectionRange(cursorPos + placeholder.length, cursorPos + placeholder.length);
                }
            }
            </script>
        </div>
        """
        
        self.fields['body'].help_text = (
            self.fields['body'].help_text + placeholder_help
        )


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
            'fields': ('name', 'subject'),
            'description': 'Basic template information. You can use placeholders like $first_name, $last_name in the subject as well.'
        }),
        ('Email Content', {
            'fields': ('body', 'is_html'),
            'description': 'Use the rich text editor below to format your email content. Use the placeholder buttons to insert recipient-specific variables.'
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
    list_display = ['email', 'name', 'first_name', 'last_name', 'company', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email', 'name', 'first_name', 'last_name', 'company']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['bulk_import_recipients']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-import/', self.admin_site.admin_view(self.bulk_import_view), name='email_api_recipient_bulk_import'),
        ]
        return custom_urls + urls
    
    def bulk_import_recipients(self, request, queryset):
        """Custom admin action to redirect to bulk import page"""
        return redirect('admin:email_api_recipient_bulk_import')
    
    bulk_import_recipients.short_description = "Bulk import recipients from file"
    
    def bulk_import_view(self, request):
        """Handle bulk import of recipients"""
        if request.method == 'POST':
            form = BulkImportRecipientsForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    recipients_data = form.process_file()
                    update_existing = form.cleaned_data.get('update_existing', False)
                    
                    created_count = 0
                    updated_count = 0
                    skipped_count = 0
                    errors = []
                    
                    with transaction.atomic():
                        for data in recipients_data:
                            try:
                                # Handle email generation or validation
                                email = data.get('email', '').strip()
                                
                                if not email:
                                    # Generate email from names
                                    first_name = data.get('first_name', '').lower().replace(' ', '')
                                    last_name = data.get('last_name', '').lower().replace(' ', '')
                                    
                                    if first_name and last_name:
                                        email = f"{first_name}.{last_name}@example.com"
                                    elif first_name:
                                        email = f"{first_name}@example.com"
                                    elif last_name:
                                        email = f"{last_name}@example.com"
                                    else:
                                        errors.append(f"Row {data.get('row_number', 'unknown')}: Cannot generate email without first or last name")
                                        continue
                                
                                # Ensure email is valid and unique
                                base_email = email
                                counter = 1
                                while Recipient.objects.filter(email=email).exists():
                                    if update_existing:
                                        break  # We'll update the existing one
                                    # Generate unique email by adding counter
                                    name_part, domain = base_email.split('@')
                                    email = f"{name_part}{counter}@{domain}"
                                    counter += 1
                                
                                # Check if recipient exists
                                existing_recipient = None
                                try:
                                    existing_recipient = Recipient.objects.get(email=email)
                                except Recipient.DoesNotExist:
                                    pass
                                
                                if existing_recipient:
                                    if update_existing:
                                        # Update existing recipient
                                        existing_recipient.name = data.get('name') or existing_recipient.name
                                        existing_recipient.first_name = data.get('first_name') or existing_recipient.first_name
                                        existing_recipient.last_name = data.get('last_name') or existing_recipient.last_name
                                        existing_recipient.save()
                                        updated_count += 1
                                    else:
                                        skipped_count += 1
                                else:
                                    # Create new recipient
                                    Recipient.objects.create(
                                        email=email,
                                        name=data.get('name', ''),
                                        first_name=data.get('first_name', ''),
                                        last_name=data.get('last_name', ''),
                                    )
                                    created_count += 1
                                    
                            except Exception as e:
                                errors.append(f"Row {data.get('row_number', 'unknown')}: {str(e)}")
                    
                    # Prepare success message
                    success_parts = []
                    if created_count > 0:
                        success_parts.append(f"{created_count} recipients created")
                    if updated_count > 0:
                        success_parts.append(f"{updated_count} recipients updated")
                    if skipped_count > 0:
                        success_parts.append(f"{skipped_count} recipients skipped")
                    
                    if success_parts:
                        messages.success(request, "Import completed successfully: " + ", ".join(success_parts))
                    
                    if errors:
                        error_message = "Some errors occurred during import:\n" + "\n".join(errors[:10])  # Limit to first 10 errors
                        if len(errors) > 10:
                            error_message += f"\n... and {len(errors) - 10} more errors"
                        messages.warning(request, error_message)
                    
                    if not errors or (created_count + updated_count) > 0:
                        return redirect('admin:email_api_recipient_changelist')
                        
                except Exception as e:
                    messages.error(request, f"Error processing file: {str(e)}")
        else:
            form = BulkImportRecipientsForm()
        
        context = {
            'form': form,
            'title': 'Bulk Import Recipients',
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        
        return render(request, 'admin/email_api/recipient/bulk_import.html', context)


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
