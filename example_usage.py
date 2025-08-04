#!/usr/bin/env python3
"""
Simple usage example for the email sender
"""

from mail import EmailSender, EmailConfig, EmailData
import os

def send_single_email_example():
    """Example of sending a single email with attachment"""
    
    # Configure email settings
    config = EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="your_email@gmail.com",  # Update this
        password="your_app_password",     # Update this
        use_tls=True
    )
    
    sender = EmailSender(config)
    
    # Create email data
    email_data = EmailData(
        to_email="recipient@example.com",
        to_name="John Doe",
        subject="Test Email with Attachment",
        body="Hello! This is a test email sent using Python.",
        attachments=["path/to/your/file.pdf"]  # Optional
    )
    
    # Send email
    success = sender.send_single_email(email_data)
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email")


def send_bulk_emails_example():
    """Example of sending bulk emails from CSV"""
    
    # Configure email settings
    config = EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="your_email@gmail.com",  # Update this
        password="your_app_password",     # Update this
        use_tls=True
    )
    
    sender = EmailSender(config)
    
    # Email templates with placeholders
    subject = "Hello {name} - Newsletter Update"
    body = """
    Dear {name},
    
    Thank you for being part of {company}!
    
    We're excited to share our latest updates with you.
    
    Best regards,
    The Team
    
    ---
    This email was sent to: {email}
    """
    
    # Send bulk emails
    results = sender.send_bulk_emails(
        recipients_csv="recipients.csv",
        subject_template=subject,
        body_template=body,
        attachments=[],  # Add file paths here if needed
        time_interval=5  # 5 seconds between emails
    )
    
    print(f"Emails sent: {results['sent']}")
    print(f"Failed: {results['failed']}")


def secure_email_config_example():
    """Example using environment variables for security"""
    
    # Set environment variables or use a .env file
    config = EmailConfig(
        smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        username=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD"),
        use_tls=True
    )
    
    if not config.username or not config.password:
        print("Please set EMAIL_USERNAME and EMAIL_PASSWORD environment variables")
        return
    
    sender = EmailSender(config)
    # ... rest of your code


if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Send single email")
    print("2. Send bulk emails from CSV")
    print("3. Show secure configuration example")
    
    choice = input("Enter choice (1-3): ")
    
    if choice == "1":
        send_single_email_example()
    elif choice == "2":
        send_bulk_emails_example()
    elif choice == "3":
        secure_email_config_example()
    else:
        print("Invalid choice")
