#!/usr/bin/env python3
"""
Quick test script to verify the placeholder functionality works in the admin.
This script creates a test template and shows usage examples.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/Bhavesh/Developer/mailer')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailer.settings')
django.setup()

from email_api.models import EmailTemplate
from datetime import datetime

def create_test_template():
    """Create a test template to demonstrate placeholder functionality"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    template = EmailTemplate.objects.create(
        name=f"Placeholder Test Template {timestamp}",
        subject="Welcome $first_name $last_name!",
        body="""<html>
<body>
    <h1>Welcome to Our Service!</h1>
    <p>Dear <strong>$first_name $last_name</strong>,</p>
    
    <p>We're excited to have you join us! Here are your details:</p>
    <ul>
        <li>Display Name: <strong>$name</strong></li>
        <li>Email: <code>$email</code></li>
        <li>Company: <em>$company</em></li>
    </ul>
    
    <p>Thank you for choosing our service!</p>
    
    <p>Best regards,<br>
    The Team</p>
</body>
</html>""",
        is_html=True
    )
    
    return template

def main():
    """Main function"""
    print("🧪 Creating Test Template for Placeholder Functionality")
    print("=" * 60)
    
    try:
        template = create_test_template()
        print(f"✅ Test template created successfully!")
        print(f"📋 Template ID: {template.id}")
        print(f"📝 Template Name: {template.name}")
        print(f"📧 Subject: {template.subject}")
        print(f"🌐 Body (first 100 chars): {template.body[:100]}...")
        
        print("\n🎯 To test the placeholder functionality:")
        print(f"1. Open: http://127.0.0.1:8002/admin/email_api/emailtemplate/{template.id}/change/")
        print("2. Look for the 'Insert Placeholders' panel below the email body field")
        print("3. Click inside the email body editor")
        print("4. Click any placeholder button to test insertion")
        print("5. Observe the console in browser dev tools for debug messages")
        
        print("\n🔍 Available placeholders to test:")
        placeholders = [
            "$name - Display name",
            "$first_name - First name", 
            "$last_name - Last name",
            "$email - Email address",
            "$company - Company name"
        ]
        
        for placeholder in placeholders:
            print(f"   • {placeholder}")
            
        print("\n💡 Expected behavior:")
        print("   • Clicking a button should insert the placeholder at cursor position")
        print("   • Button should briefly show '✅ Inserted!' confirmation")
        print("   • Console should show debug messages about the insertion process")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test template: {str(e)}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
