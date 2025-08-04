from django import forms
from django.core.exceptions import ValidationError
import pandas as pd
import os


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
