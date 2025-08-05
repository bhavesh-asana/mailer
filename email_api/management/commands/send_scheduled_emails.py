from django.core.management.base import BaseCommand
from django.utils import timezone
from email_api.models import ScheduledEmailCampaign
from email_api.email_service import send_scheduled_campaign_emails
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send scheduled email campaigns that are due'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No emails will be sent')
            )
        
        # Get campaigns that are due to be sent
        now = timezone.now()
        due_campaigns = ScheduledEmailCampaign.objects.filter(
            status__in=['scheduled', 'active'],
            next_send_at__lte=now
        ).select_related('template', 'created_by')
        
        if not due_campaigns.exists():
            self.stdout.write(
                self.style.SUCCESS('No campaigns due for sending.')
            )
            return
        
        self.stdout.write(
            f'Found {due_campaigns.count()} campaign(s) due for sending:'
        )
        
        for campaign in due_campaigns:
            self.stdout.write(
                f'  - {campaign.name} (Next send: {campaign.next_send_at})'
            )
        
        if dry_run:
            return
        
        # Send the campaigns
        sent_count = 0
        failed_count = 0
        
        for campaign in due_campaigns:
            try:
                self.stdout.write(f'Sending campaign: {campaign.name}')
                result = send_scheduled_campaign_emails(campaign)
                
                if result.get('success'):
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Campaign "{campaign.name}" sent successfully. '
                            f'Sent: {result.get("sent_count", 0)}, '
                            f'Failed: {result.get("failed_count", 0)}'
                        )
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ Campaign "{campaign.name}" failed: '
                            f'{result.get("error", "Unknown error")}'
                        )
                    )
                    
            except Exception as e:
                failed_count += 1
                logger.error(f'Error sending campaign {campaign.name}: {e}')
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Campaign "{campaign.name}" failed with exception: {str(e)}'
                    )
                )
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'📊 SUMMARY:')
        self.stdout.write(f'   Campaigns processed: {sent_count + failed_count}')
        self.stdout.write(f'   Successfully sent: {sent_count}')
        self.stdout.write(f'   Failed: {failed_count}')
        
        if sent_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ {sent_count} campaign(s) sent successfully!')
            )
        
        if failed_count > 0:
            self.stdout.write(
                self.style.ERROR(f'❌ {failed_count} campaign(s) failed!')
            )
