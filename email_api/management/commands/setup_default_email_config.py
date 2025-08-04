from django.core.management.base import BaseCommand
from email_api.models import EmailConfiguration


class Command(BaseCommand):
    help = 'Create default email configuration from settings'

    def handle(self, *args, **options):
        # Check if default configuration already exists
        if EmailConfiguration.objects.filter(is_default=True).exists():
            self.stdout.write(
                self.style.WARNING('Default email configuration already exists')
            )
            return

        # Create default configuration
        from django.conf import settings
        email_config = settings.EMAIL_CONFIG

        config = EmailConfiguration.objects.create(
            name='Default Configuration',
            smtp_server=email_config['SMTP_SERVER'],
            smtp_port=email_config['SMTP_PORT'],
            username=email_config['EMAIL_USERNAME'],
            password=email_config['EMAIL_PASSWORD'],
            use_tls=email_config['USE_TLS'],
            is_default=True,
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created default email configuration: {config.name}')
        )
