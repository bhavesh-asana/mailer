#!/usr/bin/env python3
"""
Email service with file attachments and database integration.
Supports sending single and bulk emails with logging.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import os
from datetime import datetime
from django.utils import timezone
from .models import EmailLog, EmailConfiguration


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email configuration settings"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False


@dataclass
class EmailData:
    """Email data structure with attachment support"""
    to_email: str
    to_name: str = ""
    subject: str = ""
    body: str = ""
    is_html: bool = False
    attachments: List[str] = None  # File paths
    attachment_ids: List[int] = None  # Database attachment IDs

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        if self.attachment_ids is None:
            self.attachment_ids = []


class EmailSender:
    """Email sender class with database integration"""
    
    def __init__(self, config: EmailConfig = None):
        if config is None:
            # Get default configuration from database
            try:
                default_config = EmailConfiguration.objects.filter(is_default=True, is_active=True).first()
                if default_config:
                    config = EmailConfig(
                        smtp_server=default_config.smtp_server,
                        smtp_port=default_config.smtp_port,
                        username=default_config.username,
                        password=default_config.password,
                        use_tls=default_config.use_tls,
                        use_ssl=default_config.use_ssl
                    )
                else:
                    # Fallback to Django settings
                    from django.conf import settings
                    email_settings = settings.EMAIL_CONFIG
                    config = EmailConfig(
                        smtp_server=email_settings['SMTP_SERVER'],
                        smtp_port=email_settings['SMTP_PORT'],
                        username=email_settings['EMAIL_USERNAME'],
                        password=email_settings['EMAIL_PASSWORD'],
                        use_tls=email_settings['USE_TLS']
                    )
            except Exception as e:
                logger.error(f"Failed to load email configuration: {e}")
                raise
        
        self.config = config
        self.sent_count = 0
        self.failed_count = 0
        
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Create and configure SMTP connection"""
        try:
            if self.config.use_ssl:
                server = smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port)
            else:
                server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
                if self.config.use_tls:
                    server.starttls()
            
            server.login(self.config.username, self.config.password)
            logger.info(f"Connected to SMTP server: {self.config.smtp_server}")
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            raise
    
    def _attach_files(self, msg: MIMEMultipart, file_paths: List[str], attachment_ids: List[int] = None) -> List[str]:
        """Attach files to email message from file paths and/or attachment IDs"""
        attached_files = []
        
        # Handle file paths
        if file_paths:
            for file_path in file_paths:
                file_path = Path(file_path)
                if not file_path.exists():
                    logger.warning(f"Attachment file not found: {file_path}")
                    continue
                    
                try:
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {file_path.name}'
                    )
                    msg.attach(part)
                    attached_files.append(str(file_path))
                    logger.info(f"Attached file: {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to attach file {file_path}: {e}")
        
        # Handle attachment IDs from database
        if attachment_ids:
            from .models import EmailAttachment
            for attachment_id in attachment_ids:
                try:
                    email_attachment = EmailAttachment.objects.get(id=attachment_id)
                    file_path = email_attachment.get_absolute_path()
                    
                    if file_path and Path(file_path).exists():
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {email_attachment.name}'
                        )
                        msg.attach(part)
                        attached_files.append(email_attachment.name)
                        logger.info(f"Attached file from DB: {email_attachment.name}")
                    else:
                        logger.warning(f"Attachment file not found for ID {attachment_id}")
                        
                except Exception as e:
                    logger.error(f"Failed to attach file from DB ID {attachment_id}: {e}")
        
        return attached_files
    
    def _create_message(self, email_data: EmailData) -> tuple[MIMEMultipart, List[str]]:
        """Create email message with attachments"""
        msg = MIMEMultipart()
        
        msg['From'] = self.config.username
        msg['To'] = email_data.to_email
        msg['Subject'] = email_data.subject
        
        # Add body
        if email_data.is_html:
            msg.attach(MIMEText(email_data.body, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(email_data.body, 'plain', 'utf-8'))
        
        # Add attachments and get list of attached files
        attached_files = self._attach_files(msg, email_data.attachments, email_data.attachment_ids)
        
        return msg, attached_files
    
    def send_single_email(self, email_data: EmailData, campaign_id: int = None) -> bool:
        """Send a single email and log to database"""
        email_log = EmailLog.objects.create(
            campaign_id=campaign_id,
            recipient_email=email_data.to_email,
            recipient_name=email_data.to_name,
            subject=email_data.subject,
            body=email_data.body,
            is_html=email_data.is_html,
            attachments=email_data.attachments + [f"ID:{aid}" for aid in email_data.attachment_ids],
            status='pending'
        )
        
        try:
            msg, attached_files = self._create_message(email_data)
            
            with self._create_smtp_connection() as server:
                text = msg.as_string()
                server.sendmail(self.config.username, email_data.to_email, text)
            
            # Update log on success with actual attached files
            email_log.status = 'sent'
            email_log.sent_at = timezone.now()
            email_log.attachments = attached_files
            email_log.save()
            
            self.sent_count += 1
            logger.info(f"Email sent successfully to {email_data.to_email}")
            return True
            
        except Exception as e:
            # Update log on failure
            email_log.status = 'failed'
            email_log.error_message = str(e)
            email_log.save()
            
            self.failed_count += 1
            logger.error(f"Failed to send email to {email_data.to_email}: {e}")
            return False
    
    def send_bulk_emails(self, emails: List[EmailData], campaign_id: int = None, 
                        delay_between_emails: float = 0) -> Dict[str, int]:
        """Send multiple emails with optional delay"""
        results = {"sent": 0, "failed": 0}
        
        for email_data in emails:
            success = self.send_single_email(email_data, campaign_id)
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
            
            # Delay between emails if specified
            if delay_between_emails > 0:
                import time
                time.sleep(delay_between_emails)
        
        return results
    
    def get_stats(self) -> Dict[str, any]:
        """Get email statistics"""
        total = self.sent_count + self.failed_count
        return {
            "sent": self.sent_count,
            "failed": self.failed_count,
            "total_processed": total,
            "success_rate": round(
                (self.sent_count / total * 100) if total > 0 else 0, 2
            )
        }


def get_email_sender(config_name: str = None) -> EmailSender:
    """Factory function to get email sender with specific configuration"""
    if config_name:
        try:
            config_obj = EmailConfiguration.objects.get(name=config_name, is_active=True)
            config = EmailConfig(
                smtp_server=config_obj.smtp_server,
                smtp_port=config_obj.smtp_port,
                username=config_obj.username,
                password=config_obj.password,
                use_tls=config_obj.use_tls,
                use_ssl=config_obj.use_ssl
            )
            return EmailSender(config)
        except EmailConfiguration.DoesNotExist:
            logger.warning(f"Email configuration '{config_name}' not found, using default")
    
    return EmailSender()


def send_single_email(template, recipient_email, recipient_name='', variables=None):
    """
    Send a single email using a template
    
    Args:
        template: EmailTemplate object
        recipient_email: str - recipient email address
        recipient_name: str - recipient name
        variables: dict - variables for template substitution
    
    Returns:
        dict with success status and error message if any
    """
    try:
        from string import Template
        
        # Prepare variables for template substitution
        if variables is None:
            variables = {}
        
        # Add default variables
        default_vars = {
            'name': recipient_name or recipient_email,
            'first_name': variables.get('first_name', ''),
            'last_name': variables.get('last_name', ''),
            'email': recipient_email,
            'company': variables.get('company', ''),
        }
        default_vars.update(variables)
        
        # Render template
        subject_template = Template(template.subject)
        body_template = Template(template.body)
        
        rendered_subject = subject_template.safe_substitute(**default_vars)
        rendered_body = body_template.safe_substitute(**default_vars)
        
        # Get template attachments
        attachment_ids = [ta.attachment.id for ta in template.attachments.all()]
        
        # Create email data
        email_data = EmailData(
            to_email=recipient_email,
            to_name=recipient_name,
            subject=rendered_subject,
            body=rendered_body,
            is_html=template.is_html,
            attachment_ids=attachment_ids
        )
        
        # Send email
        sender = get_email_sender()
        success = sender.send_single_email(email_data)
        
        return {
            'success': success,
            'sent_count': 1 if success else 0,
            'failed_count': 0 if success else 1
        }
        
    except Exception as e:
        logger.error(f"Error sending single email: {e}")
        return {
            'success': False,
            'error': str(e),
            'sent_count': 0,
            'failed_count': 1
        }


def send_scheduled_campaign_emails(scheduled_campaign):
    """
    Send emails for a scheduled campaign
    
    Args:
        scheduled_campaign: ScheduledEmailCampaign object
    
    Returns:
        dict with results
    """
    try:
        from string import Template
        
        template = scheduled_campaign.template
        recipients = scheduled_campaign.recipients.filter(is_active=True)
        
        if not recipients.exists():
            return {
                'success': False,
                'error': 'No active recipients found',
                'sent_count': 0,
                'failed_count': 0
            }
        
        sender = get_email_sender()
        sent_count = 0
        failed_count = 0
        
        # Create EmailCampaign for logging
        from .models import EmailCampaign
        email_campaign = EmailCampaign.objects.create(
            name=f"{scheduled_campaign.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            template=template,
            subject=template.subject,
            body=template.body,
            is_html=template.is_html,
            created_by=scheduled_campaign.created_by,
            status='sending',
            started_at=timezone.now()
        )
        
        # Get template attachments
        attachment_ids = [ta.attachment.id for ta in template.attachments.all()]
        
        for recipient in recipients:
            try:
                # Prepare variables for template substitution
                variables = {
                    'name': recipient.name or recipient.email,
                    'first_name': recipient.first_name,
                    'last_name': recipient.last_name,
                    'email': recipient.email,
                    'company': recipient.company,
                }
                
                # Add custom data if available
                if recipient.additional_data:
                    variables.update(recipient.additional_data)
                
                # Render template
                subject_template = Template(template.subject)
                body_template = Template(template.body)
                
                rendered_subject = subject_template.safe_substitute(**variables)
                rendered_body = body_template.safe_substitute(**variables)
                
                # Create email data
                email_data = EmailData(
                    to_email=recipient.email,
                    to_name=recipient.name,
                    subject=rendered_subject,
                    body=rendered_body,
                    is_html=template.is_html,
                    attachment_ids=attachment_ids
                )
                
                # Send email
                success = sender.send_single_email(email_data, email_campaign.id)
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error sending email to {recipient.email}: {e}")
                failed_count += 1
        
        # Update campaign status
        email_campaign.status = 'completed'
        email_campaign.completed_at = timezone.now()
        email_campaign.save()
        
        # Update scheduled campaign statistics
        scheduled_campaign.total_sent += sent_count
        scheduled_campaign.total_failed += failed_count
        scheduled_campaign.last_sent_at = timezone.now()
        
        # Calculate next send time for recurring campaigns
        if scheduled_campaign.interval != 'once':
            next_send = calculate_next_send_time(
                scheduled_campaign.last_sent_at,
                scheduled_campaign.interval
            )
            
            # Check if we should continue (end_datetime check)
            if (not scheduled_campaign.end_datetime or 
                next_send <= scheduled_campaign.end_datetime):
                scheduled_campaign.next_send_at = next_send
                scheduled_campaign.status = 'active'
            else:
                scheduled_campaign.status = 'completed'
                scheduled_campaign.next_send_at = None
        else:
            scheduled_campaign.status = 'completed'
            scheduled_campaign.next_send_at = None
        
        scheduled_campaign.save()
        
        return {
            'success': True,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_recipients': recipients.count()
        }
        
    except Exception as e:
        logger.error(f"Error sending scheduled campaign emails: {e}")
        return {
            'success': False,
            'error': str(e),
            'sent_count': 0,
            'failed_count': 0
        }


def calculate_next_send_time(last_sent, interval):
    """Calculate the next send time based on interval"""
    from datetime import timedelta
    
    if interval == 'hourly':
        return last_sent + timedelta(hours=1)
    elif interval == 'daily':
        return last_sent + timedelta(days=1)
    elif interval == 'weekly':
        return last_sent + timedelta(weeks=1)
    elif interval == 'monthly':
        # Approximate monthly as 30 days
        return last_sent + timedelta(days=30)
    else:
        return last_sent


def send_sequential_campaign_email(sequential_campaign_id):
    """Send the next email in a sequential campaign"""
    from .models import SequentialEmailCampaign, SequentialEmailRecipient
    from datetime import timedelta
    import threading
    
    try:
        sequential_campaign = SequentialEmailCampaign.objects.get(id=sequential_campaign_id)
        
        # Get the next recipient to send to
        next_recipient = SequentialEmailRecipient.objects.filter(
            campaign=sequential_campaign,
            status='pending'
        ).order_by('send_order').first()
        
        if not next_recipient:
            # No more recipients, mark campaign as completed
            sequential_campaign.status = 'completed'
            sequential_campaign.save()
            logger.info(f"Sequential campaign {sequential_campaign.name} completed")
            return {'success': True, 'message': 'Campaign completed'}
        
        # Check if it's time to send
        now = timezone.now()
        expected_send_time = (sequential_campaign.start_datetime + 
                            timedelta(minutes=next_recipient.send_order * sequential_campaign.interval_minutes))
        
        if now < expected_send_time:
            # Not yet time to send, schedule for later
            delay_seconds = (expected_send_time - now).total_seconds()
            if delay_seconds > 0:
                timer = threading.Timer(delay_seconds, send_sequential_campaign_email, [sequential_campaign_id])
                timer.start()
                logger.info(f"Scheduled next email for {expected_send_time}")
                return {'success': True, 'message': f'Next email scheduled for {expected_send_time}'}
        
        # Time to send the email
        try:
            # Get the template and recipient
            template = sequential_campaign.template
            recipient = next_recipient.recipient
            
            # Prepare variables for template rendering
            variables = {
                'name': recipient.name,
                'first_name': recipient.name.split()[0] if recipient.name else '',
                'last_name': ' '.join(recipient.name.split()[1:]) if len(recipient.name.split()) > 1 else '',
                'email': recipient.email,
                'company': '',  # Add company field if available in recipient model
            }
            
            # Render template with placeholders
            from string import Template
            
            subject_template = Template(template.subject)
            body_template = Template(template.body)
            
            rendered_subject = subject_template.safe_substitute(**variables)
            rendered_body = body_template.safe_substitute(**variables)
            
            # Get template attachments
            attachment_ids = [ta.attachment.id for ta in template.attachments.all()]
            
            # Prepare email data
            email_data = EmailData(
                to_email=recipient.email,
                to_name=recipient.name,
                subject=rendered_subject,
                body=rendered_body,
                is_html=template.is_html,
                attachment_ids=attachment_ids
            )
            
            # Send the email
            sender = get_email_sender()
            success = sender.send_single_email(email_data, campaign_id=sequential_campaign.id)
            
            if success:
                # Update recipient status
                next_recipient.status = 'sent'
                next_recipient.sent_at = timezone.now()
                next_recipient.save()
                
                # Update campaign progress
                sequential_campaign.emails_sent += 1
                
                # Check if this was the last email
                remaining_recipients = SequentialEmailRecipient.objects.filter(
                    campaign=sequential_campaign,
                    status='pending'
                ).count()
                
                if remaining_recipients == 0:
                    sequential_campaign.status = 'completed'
                    logger.info(f"Sequential campaign {sequential_campaign.name} completed")
                else:
                    # Schedule next email
                    next_delay_minutes = sequential_campaign.interval_minutes
                    timer = threading.Timer(
                        next_delay_minutes * 60, 
                        send_sequential_campaign_email, 
                        [sequential_campaign_id]
                    )
                    timer.start()
                    logger.info(f"Next email scheduled in {next_delay_minutes} minutes")
                
                sequential_campaign.save()
                
                return {
                    'success': True,
                    'recipient': recipient.email,
                    'send_order': next_recipient.send_order,
                    'remaining': remaining_recipients
                }
            else:
                # Mark as failed and continue with next
                next_recipient.status = 'failed'
                next_recipient.save()
                
                # Try to send next email after a short delay
                timer = threading.Timer(60, send_sequential_campaign_email, [sequential_campaign_id])  # 1 minute delay
                timer.start()
                
                return {
                    'success': False,
                    'error': f'Failed to send to {recipient.email}',
                    'recipient': recipient.email
                }
                
        except Exception as e:
            logger.error(f"Error sending sequential email: {e}")
            # Mark recipient as failed
            next_recipient.status = 'failed'
            next_recipient.save()
            
            # Try next recipient after delay
            timer = threading.Timer(60, send_sequential_campaign_email, [sequential_campaign_id])
            timer.start()
            
            return {'success': False, 'error': str(e)}
            
    except SequentialEmailCampaign.DoesNotExist:
        logger.error(f"Sequential campaign {sequential_campaign_id} not found")
        return {'success': False, 'error': 'Campaign not found'}
    except Exception as e:
        logger.error(f"Error in sequential campaign processing: {e}")
        return {'success': False, 'error': str(e)}


def start_sequential_campaign(sequential_campaign_id):
    """Start a sequential email campaign"""
    from .models import SequentialEmailCampaign
    
    try:
        sequential_campaign = SequentialEmailCampaign.objects.get(id=sequential_campaign_id)
        
        if sequential_campaign.status != 'draft':
            return {'success': False, 'error': 'Campaign is not in draft status'}
        
        # Update campaign status
        sequential_campaign.status = 'sending'
        sequential_campaign.save()
        
        # Start the sequential sending process
        now = timezone.now()
        if sequential_campaign.start_datetime <= now:
            # Start immediately
            send_sequential_campaign_email(sequential_campaign_id)
        else:
            # Schedule for start time
            delay_seconds = (sequential_campaign.start_datetime - now).total_seconds()
            import threading
            timer = threading.Timer(delay_seconds, send_sequential_campaign_email, [sequential_campaign_id])
            timer.start()
            logger.info(f"Sequential campaign scheduled to start at {sequential_campaign.start_datetime}")
        
        return {
            'success': True,
            'message': 'Sequential campaign started',
            'start_time': sequential_campaign.start_datetime
        }
        
    except SequentialEmailCampaign.DoesNotExist:
        return {'success': False, 'error': 'Campaign not found'}
    except Exception as e:
        logger.error(f"Error starting sequential campaign: {e}")
        return {'success': False, 'error': str(e)}


def pause_sequential_campaign(sequential_campaign_id):
    """Pause a sequential email campaign"""
    from .models import SequentialEmailCampaign
    
    try:
        sequential_campaign = SequentialEmailCampaign.objects.get(id=sequential_campaign_id)
        
        if sequential_campaign.status == 'sending':
            sequential_campaign.status = 'paused'
            sequential_campaign.save()
            return {'success': True, 'message': 'Campaign paused'}
        else:
            return {'success': False, 'error': 'Campaign is not currently sending'}
            
    except SequentialEmailCampaign.DoesNotExist:
        return {'success': False, 'error': 'Campaign not found'}
    except Exception as e:
        logger.error(f"Error pausing sequential campaign: {e}")
        return {'success': False, 'error': str(e)}


def resume_sequential_campaign(sequential_campaign_id):
    """Resume a paused sequential email campaign"""
    from .models import SequentialEmailCampaign
    
    try:
        sequential_campaign = SequentialEmailCampaign.objects.get(id=sequential_campaign_id)
        
        if sequential_campaign.status == 'paused':
            sequential_campaign.status = 'sending'
            sequential_campaign.save()
            
            # Resume sending
            send_sequential_campaign_email(sequential_campaign_id)
            return {'success': True, 'message': 'Campaign resumed'}
        else:
            return {'success': False, 'error': 'Campaign is not paused'}
            
    except SequentialEmailCampaign.DoesNotExist:
        return {'success': False, 'error': 'Campaign not found'}
    except Exception as e:
        logger.error(f"Error resuming sequential campaign: {e}")
        return {'success': False, 'error': str(e)}


def cancel_sequential_campaign(sequential_campaign_id):
    """Cancel a sequential email campaign"""
    from .models import SequentialEmailCampaign
    
    try:
        sequential_campaign = SequentialEmailCampaign.objects.get(id=sequential_campaign_id)
        
        sequential_campaign.status = 'cancelled'
        sequential_campaign.save()
        
        return {'success': True, 'message': 'Campaign cancelled'}
            
    except SequentialEmailCampaign.DoesNotExist:
        return {'success': False, 'error': 'Campaign not found'}
    except Exception as e:
        logger.error(f"Error cancelling sequential campaign: {e}")
        return {'success': False, 'error': str(e)}
