from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from email_api.models import Recipient
from email_api.forms import BulkImportRecipientsForm
import os


class Command(BaseCommand):
    help = 'Bulk import recipients from a CSV or Excel file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV or Excel file to import'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing recipients instead of skipping them'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview import without making changes'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        update_existing = options['update_existing']
        dry_run = options['dry_run']

        # Check if file exists
        if not os.path.exists(file_path):
            raise CommandError(f'File does not exist: {file_path}')

        # Create a mock file upload object
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            from django.core.files.uploadedfile import SimpleUploadedFile
            uploaded_file = SimpleUploadedFile(
                name=os.path.basename(file_path),
                content=file_content,
                content_type='application/octet-stream'
            )

            # Create form and validate
            form_data = {'update_existing': update_existing}
            form = BulkImportRecipientsForm(form_data, {'file': uploaded_file})

            if not form.is_valid():
                for field, errors in form.errors.items():
                    for error in errors:
                        self.stdout.write(
                            self.style.ERROR(f'Error in {field}: {error}')
                        )
                raise CommandError('Form validation failed')

            # Process the file
            recipients_data = form.process_file()
            
            if not recipients_data:
                self.stdout.write(
                    self.style.WARNING('No valid recipient data found in file')
                )
                return

            created_count = 0
            updated_count = 0
            skipped_count = 0
            errors = []

            self.stdout.write(f'Processing {len(recipients_data)} recipients...')
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('DRY RUN MODE - No changes will be made')
                )

            for data in recipients_data:
                try:
                    # Handle email generation
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

                    # Check for existing recipient
                    existing_recipient = None
                    try:
                        existing_recipient = Recipient.objects.get(email=email)
                    except Recipient.DoesNotExist:
                        pass

                    if existing_recipient:
                        if update_existing:
                            if not dry_run:
                                existing_recipient.name = data.get('name') or existing_recipient.name
                                existing_recipient.first_name = data.get('first_name') or existing_recipient.first_name
                                existing_recipient.last_name = data.get('last_name') or existing_recipient.last_name
                                existing_recipient.save()
                            updated_count += 1
                            self.stdout.write(f'  Updated: {email}')
                        else:
                            skipped_count += 1
                            self.stdout.write(f'  Skipped: {email} (already exists)')
                    else:
                        if not dry_run:
                            Recipient.objects.create(
                                email=email,
                                name=data.get('name', ''),
                                first_name=data.get('first_name', ''),
                                last_name=data.get('last_name', ''),
                            )
                        created_count += 1
                        self.stdout.write(f'  Created: {email}')

                except Exception as e:
                    error_msg = f"Row {data.get('row_number', 'unknown')}: {str(e)}"
                    errors.append(error_msg)
                    self.stdout.write(self.style.ERROR(f'  Error: {error_msg}'))

            # Print summary
            self.stdout.write('\n' + '='*50)
            self.stdout.write('IMPORT SUMMARY')
            self.stdout.write('='*50)
            
            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN - No actual changes made'))
            
            if created_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Recipients to be created: {created_count}')
                )
            if updated_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Recipients to be updated: {updated_count}')
                )
            if skipped_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'Recipients skipped: {skipped_count}')
                )
            if errors:
                self.stdout.write(
                    self.style.ERROR(f'Errors encountered: {len(errors)}')
                )
                for error in errors[:5]:  # Show first 5 errors
                    self.stdout.write(f'  - {error}')
                if len(errors) > 5:
                    self.stdout.write(f'  ... and {len(errors) - 5} more errors')

            if not dry_run and (created_count > 0 or updated_count > 0):
                self.stdout.write(
                    self.style.SUCCESS(f'\nImport completed successfully!')
                )
            elif dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'\nDry run completed. Use --no-dry-run to execute.')
                )

        except Exception as e:
            raise CommandError(f'Error processing file: {str(e)}')
