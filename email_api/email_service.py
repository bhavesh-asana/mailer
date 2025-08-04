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
    """Email data structure"""
    to_email: str
    to_name: str = ""
    subject: str = ""
    body: str = ""
    is_html: bool = False
    attachments: List[str] = None

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []


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
    
    def _attach_files(self, msg: MIMEMultipart, file_paths: List[str]) -> None:
        """Attach files to email message"""
        if not file_paths:
            return
            
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
                logger.info(f"Attached file: {file_path.name}")
                
            except Exception as e:
                logger.error(f"Failed to attach file {file_path}: {e}")
    
    def _create_message(self, email_data: EmailData) -> MIMEMultipart:
        """Create email message with attachments"""
        msg = MIMEMultipart()
        
        msg['From'] = self.config.username
        msg['To'] = email_data.to_email
        msg['Subject'] = email_data.subject
        
        # Add body
        if email_data.is_html:
            msg.attach(MIMEText(email_data.body, 'html'))
        else:
            msg.attach(MIMEText(email_data.body, 'plain'))
        
        # Add attachments
        self._attach_files(msg, email_data.attachments)
        
        return msg
    
    def send_single_email(self, email_data: EmailData, campaign_id: int = None) -> bool:
        """Send a single email and log to database"""
        email_log = EmailLog.objects.create(
            campaign_id=campaign_id,
            recipient_email=email_data.to_email,
            recipient_name=email_data.to_name,
            subject=email_data.subject,
            body=email_data.body,
            is_html=email_data.is_html,
            attachments=email_data.attachments,
            status='pending'
        )
        
        try:
            msg = self._create_message(email_data)
            
            with self._create_smtp_connection() as server:
                text = msg.as_string()
                server.sendmail(self.config.username, email_data.to_email, text)
            
            # Update log on success
            email_log.status = 'sent'
            email_log.sent_at = timezone.now()
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
