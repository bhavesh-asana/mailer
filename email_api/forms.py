from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import ScheduledEmailCampaign, EmailTemplate, Recipient, SequentialEmailCampaign
from .widgets import ChicagoDatePickerInput, ChicagoTimePickerInput
import pandas as pd
import os


class SequentialEmailForm(forms.ModelForm):
    """Form for creating sequential email campaigns"""
    
    selected_recipients = forms.ModelMultipleChoiceField(
        queryset=Recipient.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '10'
        }),
        help_text="Select recipients in the order you want emails to be sent"
    )
    
    class Meta:
        model = SequentialEmailCampaign
        fields = ['name', 'template', 'interval_minutes', 'start_date', 'start_time']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter sequential campaign name'
            }),
            'template': forms.Select(attrs={
                'class': 'form-control'
            }),
            'interval_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '1440',  # Max 24 hours
                'value': '10'
            }),
            'start_date': ChicagoDatePickerInput(),
            'start_time': ChicagoTimePickerInput(),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract user before calling super()
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Make fields required
        self.fields['name'].required = True
        self.fields['template'].required = True
        self.fields['start_date'].required = True
        self.fields['start_time'].required = True
        
        # Filter template queryset by user
        if self.user and self.user.is_authenticated:
            self.fields['template'].queryset = EmailTemplate.objects.filter(created_by=self.user)
        else:
            # For anonymous users or testing, show all templates
            self.fields['template'].queryset = EmailTemplate.objects.all()
        
        # Add selected_recipients field
        if self.user and self.user.is_authenticated:
            # Recipients don't have created_by field, so show all active recipients
            self.fields['selected_recipients'] = forms.ModelMultipleChoiceField(
                queryset=Recipient.objects.filter(is_active=True),
                widget=forms.SelectMultiple(attrs={
                    'class': 'form-control',
                    'size': '8',
                    'multiple': True
                }),
                required=True,
                help_text="Hold Ctrl (or Cmd on Mac) to select multiple recipients in order"
            )
        else:
            # For anonymous users or testing, show all recipients
            self.fields['selected_recipients'] = forms.ModelMultipleChoiceField(
                queryset=Recipient.objects.filter(is_active=True),
                widget=forms.SelectMultiple(attrs={
                    'class': 'form-control',
                    'size': '8',
                    'multiple': True
                }),
                required=True,
                help_text="Hold Ctrl (or Cmd on Mac) to select multiple recipients in order"
            )
        
        # Set help texts
        self.fields['interval_minutes'].help_text = "Time interval in minutes between each email (1-1440 minutes)"
        self.fields['start_date'].help_text = "Date to start sending emails"
        self.fields['start_time'].help_text = "Time to start sending the first email (in Chicago time)"
    
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            from datetime import date
            if start_date < date.today():
                raise ValidationError("Start date cannot be in the past.")
        return start_date
    
    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        # Basic validation - time field handles format automatically
        return start_time
    
    def clean(self):
        """Validate the combined date and time"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        
        if start_date and start_time:
            from datetime import datetime, timedelta
            from django.utils import timezone as django_timezone
            import pytz
            
            # Combine date and time
            naive_dt = datetime.combine(start_date, start_time)
            
            # Get user timezone (default to Chicago)
            user_timezone = getattr(self, '_user_timezone', 'America/Chicago')
            
            try:
                # Convert to user timezone first, then to UTC
                user_tz = pytz.timezone(user_timezone)
                local_dt = user_tz.localize(naive_dt)
                utc_dt = local_dt.astimezone(pytz.UTC)
                
                # Make it Django timezone-aware
                aware_dt = django_timezone.make_aware(utc_dt.replace(tzinfo=None), django_timezone.utc)
                
                # Check if it's in the future (with 2 minute buffer)
                current_time = django_timezone.now()
                buffer_time = current_time - timedelta(minutes=2)
                
                if aware_dt <= buffer_time:
                    current_local = current_time.astimezone(user_tz)
                    error_msg = f"Start time must be in the future. Current time in {user_timezone}: {current_local.strftime('%m/%d/%Y %I:%M %p')}"
                    raise ValidationError(error_msg)
                    
                # Store the combined datetime for saving
                cleaned_data['combined_datetime'] = aware_dt
                
            except pytz.exceptions.UnknownTimeZoneError:
                raise ValidationError(f"Invalid timezone: {user_timezone}")
            except Exception as e:
                raise ValidationError(f"Error processing date/time: {str(e)}")
        
        return cleaned_data
    
    def clean_interval_minutes(self):
        interval = self.cleaned_data.get('interval_minutes')
        if interval is not None:
            if interval < 1:
                raise ValidationError("Interval must be at least 1 minute.")
            if interval > 1440:  # 24 hours
                raise ValidationError("Interval cannot exceed 1440 minutes (24 hours).")
        return interval
    
    def clean_selected_recipients(self):
        recipients = self.cleaned_data.get('selected_recipients')
        if recipients is not None and len(recipients) < 1:
            raise ValidationError("Please select at least one recipient.")
        if recipients is not None and len(recipients) > 100:
            raise ValidationError("Maximum 100 recipients allowed for sequential campaigns.")
        return recipients
    
    def save(self, commit=True):
        campaign = super().save(commit=commit)
        
        if commit:
            # Clear existing recipients
            campaign.sequential_recipients.all().delete()
            
            # Add selected recipients in order
            selected_recipients = self.cleaned_data.get('selected_recipients', [])
            campaign.total_recipients = len(selected_recipients)
            campaign.save()
            
            # Create sequential recipient entries
            from .models import SequentialEmailRecipient
            from datetime import timedelta
            
            for i, recipient in enumerate(selected_recipients):
                scheduled_time = campaign.start_datetime + timedelta(
                    minutes=campaign.interval_minutes * i
                )
                
                SequentialEmailRecipient.objects.create(
                    campaign=campaign,
                    recipient=recipient,
                    send_order=i,
                    scheduled_time=scheduled_time,
                    status='scheduled'
                )
        
        return campaign


class ScheduledEmailForm(forms.ModelForm):
    """Form for creating scheduled email campaigns"""
    
    class Meta:
        model = ScheduledEmailCampaign
        fields = ['name', 'template', 'recipients', 'interval', 'scheduled_datetime', 'end_datetime']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter campaign name'
            }),
            'template': forms.Select(attrs={
                'class': 'form-control'
            }),
            'recipients': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '10'
            }),
            'interval': forms.Select(attrs={
                'class': 'form-control'
            }),
            'scheduled_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'end_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make fields required as needed
        self.fields['name'].required = True
        self.fields['template'].required = True
        self.fields['recipients'].required = True
        self.fields['scheduled_datetime'].required = True
        
        # Set help texts
        self.fields['recipients'].help_text = "Select one or more recipients. Hold Ctrl/Cmd to select multiple."
        self.fields['scheduled_datetime'].help_text = "When to start sending emails"
        self.fields['end_datetime'].help_text = "For recurring emails, when to stop (optional)"
        
        # Set input formats for datetime fields
        self.fields['scheduled_datetime'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_datetime'].input_formats = ['%Y-%m-%dT%H:%M']
    
    def clean_scheduled_datetime(self):
        scheduled_datetime = self.cleaned_data.get('scheduled_datetime')
        if scheduled_datetime:
            # Convert to timezone-aware datetime if it's naive
            if scheduled_datetime.tzinfo is None:
                # Assume the datetime is in the user's local timezone
                # For now, we'll treat it as UTC since datetime-local sends local time
                from django.utils import timezone
                scheduled_datetime = timezone.make_aware(scheduled_datetime, timezone.get_current_timezone())
            
            # Check if the datetime is in the future
            from django.utils import timezone as django_timezone
            if scheduled_datetime <= django_timezone.now():
                raise ValidationError("Scheduled time must be in the future.")
        return scheduled_datetime
    
    def clean(self):
        cleaned_data = super().clean()
        scheduled_datetime = cleaned_data.get('scheduled_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        interval = cleaned_data.get('interval')
        
        # Handle timezone conversion for end_datetime if provided
        if end_datetime:
            if end_datetime.tzinfo is None:
                from django.utils import timezone
                end_datetime = timezone.make_aware(end_datetime, timezone.get_current_timezone())
                cleaned_data['end_datetime'] = end_datetime
            
            # Validate end datetime if provided
            if scheduled_datetime and end_datetime <= scheduled_datetime:
                raise ValidationError({
                    'end_datetime': "End time must be after the scheduled start time."
                })
            
            # End datetime is only relevant for recurring emails
            if interval == 'once':
                cleaned_data['end_datetime'] = None
        
        return cleaned_data


class BulkImportRecipientsForm(forms.Form):
    """Form for bulk importing recipients from CSV/Excel files"""
    
    SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls']
    
    file = forms.FileField(
        label="Import File",
        help_text="Upload a CSV, XLS, or XLSX file with headers: 'Display name', 'First name', 'Last name' (Email is optional)",
        widget=forms.FileInput(attrs={
            'accept': '.csv,.xlsx,.xls',
            'class': 'form-control'
        })
    )
    
    update_existing = forms.BooleanField(
        label="Update existing recipients",
        help_text="If checked, existing recipients (based on email) will be updated. Otherwise, they will be skipped.",
        required=False,
        initial=False
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            return file
        
        # Check file extension
        file_ext = os.path.splitext(file.name)[1].lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValidationError(
                f"Unsupported file format. Please upload a file with one of these extensions: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # Check file size (limit to 10MB)
        if file.size > 10 * 1024 * 1024:  # 10MB
            raise ValidationError("File size should not exceed 10MB.")
        
        return file
    
    def process_file(self):
        """Process the uploaded file and return a list of recipient data"""
        file = self.cleaned_data.get('file')
        if not file:
            return []
        
        file_ext = os.path.splitext(file.name)[1].lower()
        
        try:
            # Read the file based on its extension
            if file_ext == '.csv':
                df = pd.read_csv(file)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file)
            else:
                raise ValidationError("Unsupported file format.")
            
            # Normalize column names (case-insensitive and strip whitespace)
            df.columns = df.columns.str.strip().str.lower()
            
            # Check for required columns
            required_columns = ['display name', 'first name', 'last name']
            optional_columns = ['email']  # Email is optional, will be generated if not provided
            missing_columns = []
            
            for col in required_columns:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                raise ValidationError(
                    f"Missing required columns: {', '.join(missing_columns)}. "
                    f"Expected columns: {', '.join(required_columns)}. "
                    f"Optional columns: {', '.join(optional_columns)}"
                )
            
            # Process the data
            recipients_data = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Get values and handle NaN
                    display_name = str(row['display name']).strip() if pd.notna(row['display name']) else ''
                    first_name = str(row['first name']).strip() if pd.notna(row['first name']) else ''
                    last_name = str(row['last name']).strip() if pd.notna(row['last name']) else ''
                    
                    # Get email if provided
                    email = ''
                    if 'email' in df.columns and pd.notna(row['email']):
                        email = str(row['email']).strip()
                    
                    # Skip empty rows
                    if not any([display_name, first_name, last_name, email]):
                        continue
                    
                    # Validate that we have at least first_name or last_name for email generation
                    if not email and not first_name and not last_name:
                        errors.append(f"Row {index + 2}: Either email must be provided or first/last name for email generation")
                        continue
                    
                    recipients_data.append({
                        'name': display_name,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,  # May be empty, will be generated in admin
                        'row_number': index + 2  # +2 because of 0-indexing and header row
                    })
                
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")
            
            if errors:
                raise ValidationError("Errors found in file:\n" + "\n".join(errors))
            
            return recipients_data
        
        except pd.errors.EmptyDataError:
            raise ValidationError("The uploaded file is empty.")
        except pd.errors.ParserError as e:
            raise ValidationError(f"Error parsing file: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error processing file: {str(e)}")
