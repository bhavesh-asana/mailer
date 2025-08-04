#!/usr/bin/env python3
"""
Email sender with file attachments and CSV recipient management.
Supports sending multiple emails with configurable time intervals.
"""

import csv
import time
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


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_sender.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email configuration settings"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True


@dataclass
class EmailData:
    """Email data structure"""
    to_email: str
    to_name: str = ""
    subject: str = ""
    body: str = ""
    attachments: List[str] = None


class EmailSender:
    """Email sender class with support for attachments and bulk sending"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.sent_count = 0
        self.failed_count = 0
        
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Create and configure SMTP connection"""
        try:
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
    
    def send_single_email(self, email_data: EmailData) -> bool:
        """Send a single email with attachments"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.username
            msg['To'] = email_data.to_email
            msg['Subject'] = email_data.subject
            
            # Add body
            msg.attach(MIMEText(email_data.body, 'plain'))
            
            # Add attachments
            if email_data.attachments:
                self._attach_files(msg, email_data.attachments)
            
            # Send email
            server = self._create_smtp_connection()
            text = msg.as_string()
            server.sendmail(self.config.username, email_data.to_email, text)
            server.quit()
            
            self.sent_count += 1
            logger.info(f"Email sent successfully to: {email_data.to_email}")
            return True
            
        except Exception as e:
            self.failed_count += 1
            logger.error(f"Failed to send email to {email_data.to_email}: {e}")
            return False
    
    def send_bulk_emails(self, 
                        recipients_csv: str, 
                        subject_template: str,
                        body_template: str,
                        attachments: List[str] = None,
                        time_interval: int = 5) -> Dict[str, int]:
        """
        Send bulk emails with time intervals between sends
        
        Args:
            recipients_csv: Path to CSV file with recipient data
            subject_template: Email subject (can include placeholders like {name})
            body_template: Email body (can include placeholders like {name}, {email})
            attachments: List of file paths to attach
            time_interval: Seconds to wait between emails
            
        Returns:
            Dictionary with sent and failed counts
        """
        recipients = self.load_recipients_from_csv(recipients_csv)
        
        if not recipients:
            logger.error("No recipients found in CSV file")
            return {"sent": 0, "failed": 0}
        
        logger.info(f"Starting bulk email send to {len(recipients)} recipients")
        logger.info(f"Time interval between emails: {time_interval} seconds")
        
        for i, recipient in enumerate(recipients):
            try:
                # Format subject and body with recipient data
                subject = subject_template.format(**recipient)
                body = body_template.format(**recipient)
                
                email_data = EmailData(
                    to_email=recipient['email'],
                    to_name=recipient.get('name', ''),
                    subject=subject,
                    body=body,
                    attachments=attachments
                )
                
                # Send email
                success = self.send_single_email(email_data)
                
                if success:
                    logger.info(f"Progress: {i + 1}/{len(recipients)} emails sent")
                
                # Wait before sending next email (except for the last one)
                if i < len(recipients) - 1:
                    logger.info(f"Waiting {time_interval} seconds before next email...")
                    time.sleep(time_interval)
                    
            except Exception as e:
                logger.error(f"Error processing recipient {recipient}: {e}")
                self.failed_count += 1
        
        result = {"sent": self.sent_count, "failed": self.failed_count}
        logger.info(f"Bulk email send completed. Sent: {result['sent']}, Failed: {result['failed']}")
        return result
    
    @staticmethod
    def load_recipients_from_csv(csv_file_path: str) -> List[Dict[str, str]]:
        """
        Load recipient data from CSV file
        Expected CSV format: email, name (optional), other_fields...
        """
        recipients = []
        csv_path = Path(csv_file_path)
        
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_file_path}")
            return recipients
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if 'email' in row and row['email']:
                        recipients.append(dict(row))
                    else:
                        logger.warning(f"Skipping row without email: {row}")
            
            logger.info(f"Loaded {len(recipients)} recipients from CSV")
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
        
        return recipients
    
    @staticmethod
    def create_sample_csv(file_path: str = "recipients.csv"):
        """Create a sample CSV file for testing"""
        sample_data = [
            {"email": "user1@example.com", "name": "John Doe", "company": "Tech Corp"},
            {"email": "user2@example.com", "name": "Jane Smith", "company": "Design Ltd"},
            {"email": "user3@example.com", "name": "Bob Johnson", "company": "Marketing Inc"}
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ["email", "name", "company"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)
        
        logger.info(f"Sample CSV file created: {file_path}")


def main():
    """Example usage of the EmailSender class"""
    
    # Email configuration (update with your SMTP settings)
    config = EmailConfig(
        smtp_server="smtp.gmail.com",  # Gmail SMTP server
        smtp_port=587,
        username="your_email@gmail.com",  # Replace with your email
        password="your_app_password",     # Use app password for Gmail
        use_tls=True
    )
    
    # You can also use environment variables for security
    # config = EmailConfig(
    #     smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    #     smtp_port=int(os.getenv("SMTP_PORT", "587")),
    #     username=os.getenv("EMAIL_USERNAME"),
    #     password=os.getenv("EMAIL_PASSWORD"),
    #     use_tls=True
    # )
    
    # Create email sender instance
    sender = EmailSender(config)
    
    # Create sample CSV file for testing
    sender.create_sample_csv("recipients.csv")
    
    # Email templates
    subject_template = "Hello {name} - Important Update"
    body_template = """
    Dear {name},
    
    I hope this email finds you well. We wanted to reach out to you from {company}.
    
    This is a test email sent using our automated email system.
    
    Your email address on file is: {email}
    
    Best regards,
    The Email Team
    """
    
    # List of files to attach (update with actual file paths)
    attachments = [
        # "path/to/document.pdf",
        # "path/to/image.jpg"
    ]
    
    # Send bulk emails with 10-second intervals
    try:
        results = sender.send_bulk_emails(
            recipients_csv="recipients.csv",
            subject_template=subject_template,
            body_template=body_template,
            attachments=attachments,
            time_interval=10  # 10 seconds between emails
        )
        
        print(f"\nEmail sending completed!")
        print(f"Successfully sent: {results['sent']}")
        print(f"Failed to send: {results['failed']}")
        
    except KeyboardInterrupt:
        logger.info("Email sending interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
