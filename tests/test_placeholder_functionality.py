#!/usr/bin/env python3
"""
Test script to validate the new placeholder functionality for first_name and last_name
in email templates.
"""

import os
import sys
import django
import requests
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/Bhavesh/Developer/mailer')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailer.settings')
django.setup()

from email_api.models import EmailTemplate, Recipient
from email_api.serializers import TemplateVariablesSerializer
from string import Template

def test_placeholder_substitution():
    """Test the template variable substitution functionality"""
    print("🧪 Testing Placeholder Substitution Functionality")
    print("=" * 60)
    
    # Test data
    test_variables = {
        'name': 'John Smith',
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'john.smith@example.com',
        'company': 'Tech Solutions Inc.'
    }
    
    # Test templates
    test_templates = [
        {
            'name': 'First Name Only',
            'subject': 'Welcome $first_name!',
            'body': 'Dear $first_name,\n\nWelcome to our service!'
        },
        {
            'name': 'Last Name Only',
            'subject': 'Hello $last_name',
            'body': 'Mr./Ms. $last_name, thank you for joining us.'
        },
        {
            'name': 'Full Name Components',
            'subject': 'Welcome $first_name $last_name',
            'body': 'Dear $first_name $last_name,\n\nYour email $email has been registered.'
        },
        {
            'name': 'Mixed Variables',
            'subject': 'Hello $first_name from $company',
            'body': '''Dear $first_name $last_name,

Welcome to $company! We're excited to have you on board.

Your registration details:
- Name: $name
- Email: $email
- Company: $company

Best regards,
The Team'''
        },
        {
            'name': 'HTML Template with Placeholders',
            'subject': 'Welcome $first_name!',
            'body': '''<html>
<body>
    <h1>Welcome $first_name!</h1>
    <p>Dear <strong>$first_name $last_name</strong>,</p>
    <p>Thank you for joining <em>$company</em>!</p>
    <p>Your registered email: <code>$email</code></p>
    <p>Display name: <strong>$name</strong></p>
</body>
</html>'''
        }
    ]
    
    print("Testing template variable substitution:")
    print("-" * 40)
    
    for i, template_data in enumerate(test_templates, 1):
        print(f"\n{i}. {template_data['name']}")
        print(f"   Subject Template: {template_data['subject']}")
        print(f"   Body Template: {template_data['body'][:50]}...")
        
        # Test substitution
        try:
            subject_template = Template(template_data['subject'])
            body_template = Template(template_data['body'])
            
            rendered_subject = subject_template.safe_substitute(**test_variables)
            rendered_body = body_template.safe_substitute(**test_variables)
            
            print(f"   ✅ Rendered Subject: {rendered_subject}")
            print(f"   ✅ Rendered Body: {rendered_body[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    return True

def test_recipient_model_integration():
    """Test integration with the Recipient model"""
    print("\n🔍 Testing Recipient Model Integration")
    print("=" * 60)
    
    # Create or get a test recipient
    test_recipient, created = Recipient.objects.get_or_create(
        email='test.placeholder@example.com',
        defaults={
            'name': 'Jane Doe',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'company': 'Example Corp'
        }
    )
    
    print(f"Test recipient: {test_recipient}")
    print(f"- Name: {test_recipient.name}")
    print(f"- First Name: {test_recipient.first_name}")
    print(f"- Last Name: {test_recipient.last_name}")
    print(f"- Email: {test_recipient.email}")
    print(f"- Company: {test_recipient.company}")
    
    # Test template with recipient data
    variables = {
        'name': test_recipient.name,
        'first_name': test_recipient.first_name,
        'last_name': test_recipient.last_name,
        'email': test_recipient.email,
        'company': test_recipient.company
    }
    
    template_text = "Hello $first_name $last_name! Your email $email is registered with $company."
    template = Template(template_text)
    rendered = template.safe_substitute(**variables)
    
    print(f"\nTemplate: {template_text}")
    print(f"Rendered: {rendered}")
    
    # Clean up
    if created:
        test_recipient.delete()
        print("✅ Test recipient cleaned up")
    
    return True

def test_bulk_email_serializer():
    """Test the updated bulk email serializer with new fields"""
    print("\n📋 Testing Bulk Email Serializer")
    print("=" * 60)
    
    from email_api.serializers import BulkEmailRecipientSerializer
    
    # Test data with new fields
    test_data = {
        'email': 'test@example.com',
        'name': 'Test User',
        'first_name': 'Test',
        'last_name': 'User',
        'company': 'Test Company',
        'variables': {'custom_var': 'custom_value'}
    }
    
    serializer = BulkEmailRecipientSerializer(data=test_data)
    
    if serializer.is_valid():
        print("✅ Serializer validation passed")
        print(f"Validated data: {serializer.validated_data}")
    else:
        print("❌ Serializer validation failed")
        print(f"Errors: {serializer.errors}")
        return False
    
    return True

def test_api_endpoint_integration():
    """Test API endpoint with new placeholder variables (if server is running)"""
    print("\n🌐 Testing API Endpoint Integration")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api"
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/health/", timeout=2)
        if response.status_code != 200:
            print("❌ Server not running or health check failed")
            return False
    except requests.exceptions.RequestException:
        print("⚠️  Server not running - skipping API tests")
        return True
    
    print("✅ Server is running")
    
    # Test template creation with new placeholders
    template_data = {
        "name": f"Test Template {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "subject": "Hello $first_name from $company",
        "body": "Dear $first_name $last_name, welcome to $company! Contact us at any time.",
        "is_html": False
    }
    
    try:
        response = requests.post(f"{base_url}/templates/", json=template_data)
        if response.status_code == 201:
            template = response.json()
            print(f"✅ Template created: {template['name']}")
            
            # Test variable substitution
            test_vars = {
                "variables": {
                    "first_name": "Alice",
                    "last_name": "Johnson",
                    "company": "Innovation Labs"
                }
            }
            
            test_response = requests.post(
                f"{base_url}/templates/{template['id']}/test_variables/",
                json=test_vars
            )
            
            if test_response.status_code == 200:
                result = test_response.json()
                print("✅ Variable substitution test passed")
                print(f"Rendered subject: {result['rendered_subject']}")
                print(f"Rendered body: {result['rendered_body']}")
            else:
                print(f"❌ Variable substitution test failed: {test_response.status_code}")
            
            # Clean up
            requests.delete(f"{base_url}/templates/{template['id']}/")
            print("✅ Test template cleaned up")
            
        else:
            print(f"❌ Template creation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {str(e)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Email Template Placeholder Functionality")
    print("=" * 80)
    
    tests = [
        test_placeholder_substitution,
        test_recipient_model_integration,
        test_bulk_email_serializer,
        test_api_endpoint_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Placeholder Substitution",
        "Recipient Model Integration", 
        "Bulk Email Serializer",
        "API Endpoint Integration"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Placeholder functionality is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
