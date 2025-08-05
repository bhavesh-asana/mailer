from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path, reverse
from django.utils.html import format_html
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from .models import (
    EmailTemplate, Recipient, EmailCampaign, EmailLog, EmailConfiguration, 
    EmailAttachment, TemplateAttachment, ScheduledEmailCampaign, 
    SequentialEmailCampaign, SequentialEmailRecipient
)
from .forms import BulkImportRecipientsForm, ScheduledEmailForm, SequentialEmailForm


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
    list_display = ['name', 'subject', 'is_html', 'created_at', 'updated_at']
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
    search_fields = ['name']
    readonly_fields = ['created_at', 'file_size_display', 'content_type']
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = 'File Size'


@admin.register(ScheduledEmailCampaign)
class ScheduledEmailCampaignAdmin(admin.ModelAdmin):
    form = ScheduledEmailForm
    list_display = [
        'name', 'template', 'status', 'interval', 'scheduled_datetime', 
        'next_send_at', 'recipient_count', 'total_sent', 'total_failed', 'created_by'
    ]
    list_filter = ['status', 'interval', 'created_at', 'scheduled_datetime']
    search_fields = ['name', 'template__name']
    readonly_fields = [
        'created_at', 'updated_at', 'last_sent_at', 'next_send_at', 
        'total_sent', 'total_failed'
    ]
    actions = ['send_now', 'pause_campaign', 'resume_campaign', 'cancel_campaign']
    
    fieldsets = (
        ('Campaign Information', {
            'fields': ('name', 'template', 'recipients'),
            'description': 'Basic campaign settings and recipient selection.'
        }),
        ('Scheduling', {
            'fields': ('interval', 'scheduled_datetime', 'end_datetime', 'status'),
            'description': 'Configure when and how often to send emails.'
        }),
        ('Statistics', {
            'fields': ('total_sent', 'total_failed', 'last_sent_at', 'next_send_at'),
            'classes': ('collapse',),
            'description': 'Campaign performance metrics.'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def changelist_view(self, request, extra_context=None):
        """Add dashboard link to changelist view"""
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = reverse('admin:email_api_send_email_dashboard')
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'send-email-dashboard/', 
                self.admin_site.admin_view(self.send_email_dashboard), 
                name='email_api_send_email_dashboard'
            ),
            path(
                'preview-template/<int:template_id>/', 
                self.admin_site.admin_view(self.preview_template), 
                name='email_api_preview_template'
            ),
            path(
                'send-test-email/', 
                self.admin_site.admin_view(self.send_test_email), 
                name='email_api_send_test_email'
            ),
        ]
        return custom_urls + urls
    
    def recipient_count(self, obj):
        return obj.recipients.count()
    recipient_count.short_description = 'Recipients'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def send_now(self, request, queryset):
        """Send selected campaigns immediately"""
        from .email_service import send_scheduled_campaign_emails
        
        sent_count = 0
        for campaign in queryset.filter(status__in=['draft', 'scheduled', 'active']):
            try:
                result = send_scheduled_campaign_emails(campaign)
                if result.get('success'):
                    sent_count += 1
                    campaign.status = 'active'
                    campaign.last_sent_at = timezone.now()
                    campaign.save()
            except Exception as e:
                messages.error(request, f"Failed to send campaign '{campaign.name}': {str(e)}")
        
        if sent_count > 0:
            messages.success(request, f"Successfully sent {sent_count} campaign(s).")
    
    send_now.short_description = "Send selected campaigns now"
    
    def pause_campaign(self, request, queryset):
        """Pause selected campaigns"""
        updated = queryset.filter(status='active').update(status='paused')
        if updated:
            messages.success(request, f"Paused {updated} campaign(s).")
    
    pause_campaign.short_description = "Pause selected campaigns"
    
    def resume_campaign(self, request, queryset):
        """Resume selected campaigns"""
        updated = queryset.filter(status='paused').update(status='active')
        if updated:
            messages.success(request, f"Resumed {updated} campaign(s).")
    
    resume_campaign.short_description = "Resume selected campaigns"
    
    def cancel_campaign(self, request, queryset):
        """Cancel selected campaigns"""
        updated = queryset.exclude(status='completed').update(status='cancelled')
        if updated:
            messages.success(request, f"Cancelled {updated} campaign(s).")
    
    cancel_campaign.short_description = "Cancel selected campaigns"
    
    def send_email_dashboard(self, request):
        """Custom dashboard for sending emails"""
        if request.method == 'POST':
            form = ScheduledEmailForm(request.POST)
            if form.is_valid():
                campaign = form.save(commit=False)
                campaign.created_by = request.user
                campaign.status = 'scheduled'
                campaign.save()
                form.save_m2m()  # Save many-to-many relationships
                
                # If it's a "send once" and scheduled for now or past, send immediately
                if (campaign.interval == 'once' and 
                    campaign.scheduled_datetime <= timezone.now()):
                    try:
                        from .email_service import send_scheduled_campaign_emails
                        result = send_scheduled_campaign_emails(campaign)
                        if result.get('success'):
                            campaign.status = 'completed'
                            campaign.last_sent_at = timezone.now()
                            campaign.save()
                            messages.success(
                                request, 
                                f"Email campaign '{campaign.name}' sent successfully to {result.get('sent_count', 0)} recipients."
                            )
                        else:
                            messages.error(request, f"Failed to send campaign: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        messages.error(request, f"Error sending emails: {str(e)}")
                else:
                    # Convert scheduled time to user's timezone for display message
                    from django.utils import timezone as django_timezone
                    user_tz = django_timezone.get_current_timezone()
                    local_time = campaign.scheduled_datetime.astimezone(user_tz)
                    
                    messages.success(
                        request, 
                        f"Email campaign '{campaign.name}' scheduled successfully for {local_time.strftime('%Y-%m-%d %H:%M %Z')}."
                    )
                
                return redirect('admin:email_api_scheduledemailcampaign_changelist')
        else:
            form = ScheduledEmailForm()
        
        # Get data for the dashboard
        templates = EmailTemplate.objects.all()
        recipients = Recipient.objects.filter(is_active=True)
        recent_campaigns = ScheduledEmailCampaign.objects.select_related('template', 'created_by').order_by('-created_at')[:10]
        
        context = {
            'title': 'Send Email Dashboard',
            'form': form,
            'templates': templates,
            'recipients': recipients,
            'recent_campaigns': recent_campaigns,
            'opts': self.model._meta,
            'has_view_permission': True,
            'has_add_permission': True,
        }
        
        return render(request, 'admin/email_api/send_email_dashboard.html', context)
    
    def preview_template(self, request, template_id):
        """Preview email template with sample data"""
        try:
            template = EmailTemplate.objects.get(id=template_id)
            
            # Sample data for preview
            sample_data = {
                'name': 'John Doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'company': 'Example Company'
            }
            
            from string import Template
            subject_template = Template(template.subject)
            body_template = Template(template.body)
            
            rendered_subject = subject_template.safe_substitute(**sample_data)
            rendered_body = body_template.safe_substitute(**sample_data)
            
            # Get attachments
            attachments = template.attachments.all()
            
            return JsonResponse({
                'success': True,
                'subject': rendered_subject,
                'body': rendered_body,
                'is_html': template.is_html,
                'attachments': [
                    {
                        'name': att.attachment.name,
                        'size': att.attachment.get_file_size_display()
                    } for att in attachments
                ]
            })
        except EmailTemplate.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Template not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    def send_test_email(self, request):
        """Send a test email"""
        if request.method == 'POST':
            template_id = request.POST.get('template_id')
            test_email = request.POST.get('test_email')
            
            try:
                template = EmailTemplate.objects.get(id=template_id)
                
                # Create a test recipient
                from .email_service import send_single_email
                
                sample_data = {
                    'name': 'Test User',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'email': test_email,
                    'company': 'Test Company'
                }
                
                result = send_single_email(
                    template=template,
                    recipient_email=test_email,
                    recipient_name='Test User',
                    variables=sample_data
                )
                
                if result.get('success'):
                    return JsonResponse({
                        'success': True,
                        'message': f'Test email sent successfully to {test_email}'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    })
            
            except EmailTemplate.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Template not found'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method'
        })


class SequentialEmailRecipientInline(admin.TabularInline):
    model = SequentialEmailRecipient
    extra = 0
    readonly_fields = ['scheduled_time', 'sent_at', 'status', 'error_message']
    fields = ['send_order', 'recipient', 'scheduled_time', 'status', 'sent_at']
    
    def has_add_permission(self, request, obj=None):
        return False  # Recipients are managed through the campaign form


class SequentialEmailCampaignAdminForm(forms.ModelForm):
    """Admin form for sequential email campaigns"""
    
    selected_recipients = forms.ModelMultipleChoiceField(
        queryset=Recipient.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,  # Simple checkbox widget instead
        required=False,
        help_text="Select recipients in the order you want emails to be sent"
    )
    
    class Meta:
        model = SequentialEmailCampaign
        fields = ['name', 'template', 'interval_minutes', 'start_date', 'start_time', 'selected_recipients']
        widgets = {
            'start_date': admin.widgets.AdminDateWidget(),
            'start_time': admin.widgets.AdminTimeWidget(),
        }
    
    class Media:
        """Include necessary JavaScript and CSS for FilteredSelectMultiple"""
        js = [
            'admin/js/core.js',
            'admin/js/SelectBox.js',
            'admin/js/SelectFilter2.js',
        ]
    
    def __init__(self, *args, **kwargs):
        import datetime
        debug_file = open('/tmp/django_debug.log', 'a')
        debug_file.write(f"\n=== ADMIN FORM INIT DEBUG {datetime.datetime.now()} ===\n")
        
        super().__init__(*args, **kwargs)
        
        # Set help texts
        self.fields['interval_minutes'].help_text = "Time interval in minutes between each email (1-1440 minutes)"
        self.fields['start_date'].help_text = "Date to start sending emails"
        self.fields['start_time'].help_text = "Time to start sending the first email"
        
        debug_file.write(f"Form fields: {list(self.fields.keys())}\n")
        debug_file.write(f"Selected recipients field: {'selected_recipients' in self.fields}\n")
        debug_file.write(f"Selected recipients widget: {type(self.fields['selected_recipients'].widget)}\n")
        
        # If editing existing campaign, populate selected recipients
        if self.instance and self.instance.pk:
            selected_recipients = self.instance.sequential_recipients.all().order_by('send_order')
            recipient_list = [sr.recipient for sr in selected_recipients]
            self.fields['selected_recipients'].initial = recipient_list
            debug_file.write(f"Loading existing recipients for campaign {self.instance.pk}: {[r.email for r in recipient_list]}\n")
        
        debug_file.write("=== END ADMIN FORM INIT DEBUG ===\n")
        debug_file.close()
    
    def clean(self):
        import datetime
        debug_file = open('/tmp/django_debug.log', 'a')
        debug_file.write(f"\n=== ADMIN FORM CLEAN DEBUG {datetime.datetime.now()} ===\n")
        
        cleaned_data = super().clean()
        
        debug_file.write(f"Cleaned data keys: {list(cleaned_data.keys())}\n")
        selected_recipients = cleaned_data.get('selected_recipients', [])
        debug_file.write(f"Selected recipients count: {len(selected_recipients)}\n")
        for i, recipient in enumerate(selected_recipients):
            debug_file.write(f"  Recipient {i}: {recipient.email}\n")
        debug_file.write("=== END ADMIN FORM CLEAN DEBUG ===\n")
        debug_file.close()
        return cleaned_data
    
    def save(self, commit=True):
        print("=== ADMIN FORM SAVE DEBUG ===")
        print("Form data:", self.data)
        print("Cleaned data:", getattr(self, 'cleaned_data', 'Not available'))
        
        campaign = super().save(commit=commit)
        print(f"Campaign saved: {campaign.id} - {campaign.name}")
        
        if commit and 'selected_recipients' in self.cleaned_data:
            selected_recipients = self.cleaned_data.get('selected_recipients', [])
            print(f"Selected recipients: {list(selected_recipients)}")
            print(f"Number of recipients: {len(selected_recipients)}")
            
            # Clear existing recipients
            existing_count = campaign.sequential_recipients.count()
            print(f"Clearing {existing_count} existing recipients")
            campaign.sequential_recipients.all().delete()
            
            # Add selected recipients in order
            campaign.total_recipients = len(selected_recipients)
            campaign.save()
            print(f"Updated total_recipients to: {campaign.total_recipients}")
            
            # Create sequential recipient entries
            from .models import SequentialEmailRecipient
            from datetime import timedelta
            
            for i, recipient in enumerate(selected_recipients):
                print(f"Creating recipient {i}: {recipient.email}")
                if campaign.start_datetime:
                    scheduled_time = campaign.start_datetime + timedelta(
                        minutes=campaign.interval_minutes * i
                    )
                else:
                    scheduled_time = None
                
                seq_recipient = SequentialEmailRecipient.objects.create(
                    campaign=campaign,
                    recipient=recipient,
                    send_order=i,
                    scheduled_time=scheduled_time,
                    status='scheduled'
                )
                print(f"Created SequentialEmailRecipient: {seq_recipient.id}")
        else:
            print("No selected_recipients in cleaned_data or not committing")
            print("Available keys:", list(self.cleaned_data.keys()) if hasattr(self, 'cleaned_data') else 'No cleaned_data')
        
        print("=== END ADMIN FORM SAVE DEBUG ===")
        return campaign


@admin.register(SequentialEmailCampaign)
class SequentialEmailCampaignAdmin(admin.ModelAdmin):
    form = SequentialEmailCampaignAdminForm
    list_display = [
        'name', 'template', 'status', 'interval_minutes', 'start_date', 'start_time',
        'total_recipients', 'emails_sent', 'emails_failed', 'progress_display', 'created_by'
    ]
    list_filter = ['status', 'interval_minutes', 'created_at', 'start_date']
    search_fields = ['name', 'template__name']
    readonly_fields = [
        'created_at', 'updated_at', 'started_at', 'completed_at',
        'total_recipients', 'emails_sent', 'emails_failed', 'current_recipient_index'
    ]
    actions = ['start_campaign', 'pause_campaign', 'resume_campaign', 'cancel_campaign']
    # inlines = [SequentialEmailRecipientInline]  # Temporarily disabled
    
    def get_form(self, request, obj=None, **kwargs):
        """Force use of our custom form"""
        import datetime
        debug_file = open('/tmp/django_debug.log', 'a')
        debug_file.write(f"\n=== GET_FORM DEBUG {datetime.datetime.now()}: using {SequentialEmailCampaignAdminForm.__name__} ===\n")
        debug_file.close()
        
        kwargs['form'] = SequentialEmailCampaignAdminForm
        return super().get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        # Force an exception to see if this method is called
        import datetime
        debug_file = open('/tmp/django_debug.log', 'a')
        debug_file.write(f"\n=== ADMIN SAVE_MODEL CALLED {datetime.datetime.now()} ===\n")
        debug_file.write(f"Object: {obj}\n")
        debug_file.write(f"Form type: {type(form)}\n")
        debug_file.write(f"Change: {change}\n")
        debug_file.close()
        
        # Save the main object first
        super().save_model(request, obj, form, change)
        
        # Look for selected recipients in the POST data directly
        selected_recipient_ids = request.POST.getlist('selected_recipients')
        
        if selected_recipient_ids:
            debug_file = open('/tmp/django_debug.log', 'a')
            debug_file.write(f"Found {len(selected_recipient_ids)} recipient IDs: {selected_recipient_ids}\n")
            debug_file.close()
            
            from .models import SequentialEmailRecipient
            from datetime import timedelta
            
            # Clear existing recipients
            obj.sequential_recipients.all().delete()
            
            # Add selected recipients in order
            obj.total_recipients = len(selected_recipient_ids)
            obj.save()
            
            # Create sequential recipient entries
            for i, recipient_id in enumerate(selected_recipient_ids):
                try:
                    recipient = Recipient.objects.get(id=recipient_id)
                    
                    if obj.start_datetime:
                        scheduled_time = obj.start_datetime + timedelta(
                            minutes=obj.interval_minutes * i
                        )
                    else:
                        scheduled_time = None
                    
                    SequentialEmailRecipient.objects.create(
                        campaign=obj,
                        recipient=recipient,
                        send_order=i,
                        scheduled_time=scheduled_time,
                        status='scheduled'
                    )
                except Recipient.DoesNotExist:
                    pass
    
    fieldsets = (
        ('Campaign Information', {
            'fields': ('name', 'template'),
            'description': 'Basic campaign settings.'
        }),
        ('Sequential Settings', {
            'fields': ('selected_recipients', 'interval_minutes', 'start_date', 'start_time'),
            'description': 'Configure recipient order and timing intervals.'
        }),
        ('Progress Tracking', {
            'fields': ('total_recipients', 'emails_sent', 'emails_failed', 'current_recipient_index'),
            'classes': ('collapse',),
            'description': 'Campaign progress and statistics.'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'sequential-email-dashboard/', 
                self.admin_site.admin_view(self.sequential_email_dashboard), 
                name='email_api_sequential_email_dashboard'
            ),
            path(
                'get-schedule/<int:campaign_id>/', 
                self.admin_site.admin_view(self.get_campaign_schedule), 
                name='email_api_get_campaign_schedule'
            ),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """Add dashboard link to changelist view"""
        extra_context = extra_context or {}
        extra_context['sequential_dashboard_url'] = reverse('admin:email_api_sequential_email_dashboard')
        return super().changelist_view(request, extra_context)
    
    def progress_display(self, obj):
        if obj.total_recipients == 0:
            return "No recipients"
        
        progress_percentage = (obj.emails_sent / obj.total_recipients) * 100
        return format_html(
            '<div style="width: 100px; background: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background: #28a745; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{}%</div></div>',
            progress_percentage,
            int(progress_percentage)
        )
    progress_display.short_description = 'Progress'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def start_campaign(self, request, queryset):
        """Start selected sequential campaigns"""
        started_count = 0
        for campaign in queryset.filter(status__in=['draft', 'scheduled']):
            try:
                campaign.status = 'sending'
                campaign.started_at = timezone.now()
                campaign.save()
                started_count += 1
            except Exception as e:
                messages.error(request, f"Failed to start campaign '{campaign.name}': {str(e)}")
        
        if started_count > 0:
            messages.success(request, f"Started {started_count} sequential campaign(s).")
    
    start_campaign.short_description = "Start selected campaigns"
    
    def pause_campaign(self, request, queryset):
        """Pause selected campaigns"""
        updated = queryset.filter(status='sending').update(status='paused')
        if updated:
            messages.success(request, f"Paused {updated} campaign(s).")
    
    pause_campaign.short_description = "Pause selected campaigns"
    
    def resume_campaign(self, request, queryset):
        """Resume selected campaigns"""
        updated = queryset.filter(status='paused').update(status='sending')
        if updated:
            messages.success(request, f"Resumed {updated} campaign(s).")
    
    resume_campaign.short_description = "Resume selected campaigns"
    
    def cancel_campaign(self, request, queryset):
        """Cancel selected campaigns"""
        updated = queryset.exclude(status='completed').update(status='cancelled')
        if updated:
            messages.success(request, f"Cancelled {updated} campaign(s).")
    
    cancel_campaign.short_description = "Cancel selected campaigns"
    
    def sequential_email_dashboard(self, request):
        """Custom dashboard for sequential email campaigns"""
        if request.method == 'POST':
            form = SequentialEmailForm(request.POST)
            if form.is_valid():
                campaign = form.save(commit=False)
                campaign.created_by = request.user
                campaign.status = 'scheduled'
                campaign.save()
                
                # Save the recipients (handled by form.save())
                form.save()
                
                # Check if we should start immediately
                from django.utils import timezone as django_timezone
                if campaign.start_datetime <= django_timezone.now():
                    campaign.status = 'sending'
                    campaign.started_at = django_timezone.now()
                    campaign.save()
                    
                    messages.success(
                        request, 
                        f"Sequential campaign '{campaign.name}' created and started! "
                        f"Emails will be sent to {campaign.total_recipients} recipients "
                        f"with {campaign.interval_minutes}-minute intervals."
                    )
                else:
                    # Convert scheduled time to user's timezone for display message
                    user_tz = django_timezone.get_current_timezone()
                    local_time = campaign.start_datetime.astimezone(user_tz)
                    
                    messages.success(
                        request, 
                        f"Sequential campaign '{campaign.name}' scheduled! "
                        f"First email will be sent at {local_time.strftime('%Y-%m-%d %H:%M %Z')} "
                        f"to {campaign.total_recipients} recipients with {campaign.interval_minutes}-minute intervals."
                    )
                
                return redirect('admin:email_api_sequentialemailcampaign_changelist')
        else:
            form = SequentialEmailForm()
        
        # Get data for the dashboard
        templates = EmailTemplate.objects.all()
        recipients = Recipient.objects.filter(is_active=True)
        recent_campaigns = SequentialEmailCampaign.objects.select_related('template', 'created_by').order_by('-created_at')[:10]
        
        context = {
            'title': 'Sequential Email Dashboard',
            'form': form,
            'templates': templates,
            'recipients': recipients,
            'recent_campaigns': recent_campaigns,
            'opts': self.model._meta,
            'has_view_permission': True,
            'has_add_permission': True,
        }
        
        return render(request, 'admin/email_api/sequential_email_dashboard.html', context)
    
    def get_campaign_schedule(self, request, campaign_id):
        """Get the email schedule for a campaign"""
        try:
            campaign = SequentialEmailCampaign.objects.get(id=campaign_id)
            schedule = campaign.get_recipient_schedule()
            
            schedule_data = []
            for item in schedule:
                schedule_data.append({
                    'recipient_name': item['recipient'].name or item['recipient'].email,
                    'recipient_email': item['recipient'].email,
                    'send_order': item['send_order'],
                    'scheduled_time': item['scheduled_time'].isoformat(),
                    'status': item['status']
                })
            
            return JsonResponse({
                'success': True,
                'schedule': schedule_data,
                'campaign_name': campaign.name,
                'interval_minutes': campaign.interval_minutes
            })
        except SequentialEmailCampaign.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Campaign not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
