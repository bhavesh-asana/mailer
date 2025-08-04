#!/usr/bin/env python3
"""
Test runner for the email sender application
Run this to test the email functionality safely
"""

from mail import EmailSender, EmailConfig, EmailData
import os

def test_email_functionality():
    """Test the email functionality with user input"""
    
    print("=== Email Sender Test ===")
    print("This will test the email sending functionality.")
    print("\nIMPORTANT: For Gmail, you need to:")
    print("1. Enable 2-Factor Authentication")
    print("2. Generate an App Password (not your regular password)")
    print("3. Use the App Password instead of your regular password")
    print()
    
    # Get email configuration from user
    smtp_server = input("Enter SMTP server (default: smtp.gmail.com): ").strip()
    if not smtp_server:
        smtp_server = "smtp.gmail.com"
    
    smtp_port = input("Enter SMTP port (default: 587): ").strip()
    if not smtp_port:
        smtp_port = 587
    else:
        smtp_port = int(smtp_port)
    
    username = input("Enter your email address: ").strip()
    password = input("Enter your email password (App Password for Gmail): ").strip()
    
    if not username or not password:
        print("Email and password are required!")
        return
    
    # Create configuration
    config = EmailConfig(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        username=username,
        password=password,
        use_tls=True
    )
    
    # Create email sender
    sender = EmailSender(config)
    
    print("\n=== Testing SMTP Connection ===")
    try:
        # Test connection
        server = sender._create_smtp_connection()
        server.quit()
        print("✅ SMTP connection successful!")
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("- For Gmail: Use App Password, not regular password")
        print("- Check if 2FA is enabled (required for Gmail)")
        print("- Verify SMTP server and port settings")
        return
    
    print("\n=== Choose Test Type ===")
    print("1. Send a single test email")
    print("2. Send bulk emails from CSV (dry run)")
    print("3. Send bulk emails from CSV (actual send)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        test_single_email(sender)
    elif choice == "2":
        test_bulk_emails_dry_run(sender)
    elif choice == "3":
        test_bulk_emails_actual(sender)
    else:
        print("Invalid choice")

def test_single_email(sender):
    """Test sending a single email"""
    print("\n=== Single Email Test ===")
    
    to_email = input("Enter recipient email: ").strip()
    if not to_email:
        print("Recipient email is required!")
        return
    
    subject = input("Enter email subject (default: Test Email): ").strip()
    if not subject:
        subject = "Test Email from Python Mailer"
    
    body = input("Enter email body (or press Enter for default): ").strip()
    if not body:
        body = """Hello!

This is a test email sent using the Python Email Sender.

If you received this email, the application is working correctly!

Best regards,
Python Email Sender"""
    
    # Ask about attachments
    attachment_path = input("Enter attachment file path (optional, press Enter to skip): ").strip()
    attachments = [attachment_path] if attachment_path else []
    
    email_data = EmailData(
        to_email=to_email,
        subject=subject,
        body=body,
        attachments=attachments
    )
    
    print(f"\nSending email to: {to_email}")
    success = sender.send_single_email(email_data)
    
    if success:
        print("✅ Email sent successfully!")
    else:
        print("❌ Failed to send email. Check the logs for details.")

def test_bulk_emails_dry_run(sender):
    """Test bulk email functionality without actually sending"""
    print("\n=== Bulk Email Test (Dry Run) ===")
    
    # Load recipients from CSV
    recipients = sender.load_recipients_from_csv("recipients.csv")
    
    if not recipients:
        print("❌ No recipients found in recipients.csv")
        print("Make sure the recipients.csv file exists and has proper format.")
        return
    
    print(f"✅ Found {len(recipients)} recipients in CSV:")
    for i, recipient in enumerate(recipients[:5], 1):  # Show first 5
        print(f"  {i}. {recipient.get('name', 'N/A')} <{recipient.get('email', 'N/A')}>")
    
    if len(recipients) > 5:
        print(f"  ... and {len(recipients) - 5} more")
    
    # Show template preview
    subject_template = "Hello {name} - Test Email"
    body_template = """Dear {name},

This would be a test email for {company}.

Your email: {email}

Best regards,
Test Team"""
    
    print(f"\n📧 Email Preview (using first recipient):")
    first_recipient = recipients[0]
    try:
        preview_subject = subject_template.format(**first_recipient)
        preview_body = body_template.format(**first_recipient)
        print(f"Subject: {preview_subject}")
        print(f"Body:\n{preview_body}")
    except KeyError as e:
        print(f"❌ Template error: Missing field {e} in CSV")
        return
    
    print(f"\n⏱️  With 5-second intervals, this would take approximately {len(recipients) * 5 / 60:.1f} minutes")
    print("✅ Dry run completed. Everything looks good!")

def test_bulk_emails_actual(sender):
    """Actually send bulk emails"""
    print("\n=== Bulk Email Test (Actual Send) ===")
    print("⚠️  WARNING: This will actually send emails!")
    
    confirm = input("Are you sure you want to send emails? (type 'YES' to confirm): ").strip()
    if confirm != "YES":
        print("Cancelled.")
        return
    
    # Time interval
    time_interval = input("Enter time interval between emails in seconds (default: 5): ").strip()
    if not time_interval:
        time_interval = 5
    else:
        time_interval = int(time_interval)
    
    subject_template = "Hello {name} - Test Email from Python Mailer"
    body_template = """Dear {name},

This is a test email sent using our Python Email Sender application.

Company: {company}
Your email: {email}

If you received this email, our application is working correctly!

Best regards,
The Email Team"""
    
    print(f"\nSending bulk emails with {time_interval}-second intervals...")
    
    results = sender.send_bulk_emails(
        recipients_csv="recipients.csv",
        subject_template=subject_template,
        body_template=body_template,
        attachments=[],  # No attachments for test
        time_interval=time_interval
    )
    
    print(f"\n📊 Results:")
    print(f"✅ Successfully sent: {results['sent']}")
    print(f"❌ Failed to send: {results['failed']}")
    print(f"📝 Check 'email_sender.log' for detailed logs")

if __name__ == "__main__":
    test_email_functionality()
