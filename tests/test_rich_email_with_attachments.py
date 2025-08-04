#!/usr/bin/env python3
"""
Test script for rich text email formatting and attachments functionality
"""
import requests
import json
import os
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test@example.com"

# Unique timestamp for test names
TIMESTAMP = int(time.time())

def test_attachment_upload():
    """Test uploading an attachment"""
    print("Testing attachment upload...")
    
    # Create a test file
    test_file_path = "/tmp/test_attachment.txt"
    with open(test_file_path, 'w') as f:
        f.write("This is a test attachment file for email testing.")
    
    # Upload attachment
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        data = {'name': f'Test Attachment {TIMESTAMP}'}
        
        response = requests.post(f"{BASE_URL}/attachments/", files=files, data=data)
        
    if response.status_code == 201:
        attachment_data = response.json()
        print(f"✓ Attachment uploaded successfully: ID {attachment_data['id']}")
        return attachment_data['id']
    else:
        print(f"✗ Failed to upload attachment: {response.status_code}")
        print(response.text)
        return None

def test_rich_text_template():
    """Test creating a template with rich text formatting"""
    print("Testing rich text template creation...")
    
    template_data = {
        "name": f"Rich Text Test Template {TIMESTAMP}",
        "subject": "Welcome to our service, $name!",
        "body": """<html>
<body>
    <h1>Welcome to Our Service!</h1>
    <p>Dear <strong>$name</strong>,</p>
    
    <p>Thank you for joining us! Here are some benefits you'll enjoy:</p>
    
    <ul>
        <li><strong>24/7 Support</strong> - We're always here to help</li>
        <li><em>Premium Features</em> - Access to exclusive tools</li>
        <li><u>Free Training</u> - Learn from our experts</li>
    </ul>
    
    <p>Your company: <strong>$company</strong></p>
    
    <blockquote>
        <p><em>"Success is not final, failure is not fatal: it is the courage to continue that counts."</em></p>
        <p>- Winston Churchill</p>
    </blockquote>
    
    <p>Best regards,<br>
    <strong>The Team</strong></p>
</body>
</html>""",
        "is_html": True
    }
    
    response = requests.post(f"{BASE_URL}/templates/", json=template_data)
    
    if response.status_code == 201:
        template_data = response.json()
        print(f"✓ Rich text template created successfully: ID {template_data['id']}")
        return template_data['id']
    else:
        print(f"✗ Failed to create template: {response.status_code}")
        print(response.text)
        return None

def test_send_email_with_attachment(template_id, attachment_id):
    """Test sending an email with rich text and attachment"""
    print("Testing email sending with attachment...")
    
    email_data = {
        "to_email": TEST_EMAIL,
        "to_name": "John Doe",
        "subject": "Welcome to our service, John Doe!",  # Add explicit subject
        "body": "<h1>Test email</h1><p>This is a test email with <strong>rich</strong> formatting.</p>",  # Add explicit body
        "is_html": True,
        "template_id": template_id,
        "attachment_ids": [attachment_id] if attachment_id else []
    }
    
    response = requests.post(f"{BASE_URL}/send-email/", json=email_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Email sent successfully to {result['recipient']}")
        return True
    else:
        print(f"✗ Failed to send email: {response.status_code}")
        print(response.text)
        return False

def test_template_variables():
    """Test template variable substitution"""
    print("Testing template variable substitution...")
    
    # First create a simple template
    template_data = {
        "name": f"Variable Test Template {TIMESTAMP}",
        "subject": "Hello $name from $company",
        "body": "<p>Dear <strong>$name</strong>,</p><p>Welcome from <em>$company</em>!</p>",
        "is_html": True
    }
    
    response = requests.post(f"{BASE_URL}/templates/", json=template_data)
    
    if response.status_code != 201:
        print(f"✗ Failed to create test template: {response.status_code}")
        return False
    
    template_id = response.json()['id']
    
    # Test variable substitution
    test_variables = {
        "variables": {
            "name": "Alice Smith",
            "company": "Innovation Inc"
        }
    }
    
    response = requests.post(f"{BASE_URL}/templates/{template_id}/test_variables/", json=test_variables)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Variable substitution successful:")
        print(f"  Subject: {result['rendered_subject']}")
        print(f"  Body: {result['rendered_body']}")
        return True
    else:
        print(f"✗ Failed to test variables: {response.status_code}")
        print(response.text)
        return False

def test_bulk_email_with_attachments(attachment_id):
    """Test sending bulk emails with attachments"""
    print("Testing bulk email with attachments...")
    
    bulk_data = {
        "campaign_name": f"Rich Text Campaign Test {TIMESTAMP}",
        "subject_template": "Bulk Email Test for $name",
        "body_template": """<html>
<body>
    <h2>Hello $name!</h2>
    <p>This is a <strong>bulk email test</strong> with <em>rich formatting</em>.</p>
    <p>Your company: <strong>$company</strong></p>
    <ul>
        <li>Feature 1</li>
        <li>Feature 2</li>
        <li>Feature 3</li>
    </ul>
</body>
</html>""",
        "is_html": True,
        "attachment_ids": [attachment_id] if attachment_id else [],
        "recipients": [
            {
                "email": "user1@example.com",
                "name": "User One", 
                "company": "Company A"
            },
            {
                "email": "user2@example.com",
                "name": "User Two",
                "company": "Company B"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/send-bulk-email/", json=bulk_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Bulk emails processed successfully")
        print(f"  Campaign ID: {result.get('campaign_id')}")
        print(f"  Results: {result.get('results')}")
        return True
    else:
        print(f"✗ Failed to send bulk emails: {response.status_code}")
        print(response.text)
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Rich Text Email with Attachments")
    print("=" * 50)
    
    # Test attachment upload
    attachment_id = test_attachment_upload()
    print()
    
    # Test rich text template creation
    template_id = test_rich_text_template()
    print()
    
    # Test template variables
    test_template_variables()
    print()
    
    # Test single email with attachment
    if template_id and attachment_id:
        test_send_email_with_attachment(template_id, attachment_id)
    print()
    
    # Test bulk email with attachments
    if attachment_id:
        test_bulk_email_with_attachments(attachment_id)
    print()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
