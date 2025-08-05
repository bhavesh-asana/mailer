from django.core.management.base import BaseCommand
from django.utils import timezone
from email_api.models import SequentialEmailCampaign
from email_api.email_service import send_sequential_campaign_email
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send sequential email campaigns that are due'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )
        parser.add_argument(
            '--campaign-id',
            type=int,
            help='Start a specific campaign by ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        campaign_id = options.get('campaign_id')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No emails will be sent')
            )
        
        if campaign_id:
            # Start a specific campaign
            try:
                campaign = SequentialEmailCampaign.objects.get(id=campaign_id)
                if campaign.status != 'draft':
                    self.stdout.write(
                        self.style.ERROR(f'Campaign {campaign.name} is not in draft status. Current status: {campaign.status}')
                    )
                    return
                
                self.stdout.write(f'Starting sequential campaign: {campaign.name}')
                
                if not dry_run:
                    # Update campaign status and start time
                    campaign.status = 'sending'
                    campaign.started_at = timezone.now()
                    campaign.save()
                    
                    # Start the sequential sending process
                    send_sequential_campaign_email(campaign.id)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Sequential campaign "{campaign.name}" started successfully!')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Would start campaign: {campaign.name}')
                    )
                    
            except SequentialEmailCampaign.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Campaign with ID {campaign_id} not found')
                )
            return
        
        # Check for campaigns that should be started automatically
        now = timezone.now()
        
        # Find campaigns that should start now
        due_campaigns = SequentialEmailCampaign.objects.filter(
            status='draft'
        ).select_related('template', 'created_by')
        
        # Filter by start_datetime property (since it's a property, we need to check in Python)
        ready_campaigns = []
        for campaign in due_campaigns:
            if campaign.start_datetime and campaign.start_datetime <= now:
                ready_campaigns.append(campaign)
        
        if not ready_campaigns:
            self.stdout.write(
                self.style.SUCCESS('No sequential campaigns due for sending.')
            )
            return
        
        self.stdout.write(
            f'Found {len(ready_campaigns)} sequential campaign(s) ready to start:'
        )
        
        for campaign in ready_campaigns:
            self.stdout.write(
                f'  - {campaign.name} (Start time: {campaign.start_datetime})'
            )
            
            if not dry_run:
                # Update campaign status
                campaign.status = 'sending'
                campaign.started_at = timezone.now()
                campaign.save()
                
                # Start the sequential sending process
                try:
                    send_sequential_campaign_email(campaign.id)
                    self.stdout.write(
                        self.style.SUCCESS(f'Started campaign: {campaign.name}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to start campaign {campaign.name}: {str(e)}')
                    )
                    logger.error(f'Failed to start sequential campaign {campaign.id}: {str(e)}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN completed - no campaigns were actually started')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Started {len(ready_campaigns)} sequential campaign(s)')
            )
