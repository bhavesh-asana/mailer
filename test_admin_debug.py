#!/usr/bin/env python

# Simple script to test if our admin is working
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, '/Users/Bhavesh/Developer/mailer')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailer.settings')
django.setup()

from django.contrib import admin
from email_api.models import SequentialEmailCampaign

print("=== Testing Admin Registration ===")

# Check if our model is registered
if SequentialEmailCampaign in admin.site._registry:
    admin_class = admin.site._registry[SequentialEmailCampaign]
    print(f"✓ SequentialEmailCampaign is registered with admin class: {admin_class.__class__.__name__}")
    print(f"✓ Form class: {admin_class.form.__name__ if hasattr(admin_class, 'form') and admin_class.form else 'Default ModelForm'}")
    print(f"✓ Has get_form method: {hasattr(admin_class, 'get_form')}")
    print(f"✓ Has save_model method: {hasattr(admin_class, 'save_model')}")
    
    # Test form instantiation
    try:
        from email_api.admin import SequentialEmailCampaignAdminForm
        form = SequentialEmailCampaignAdminForm()
        print(f"✓ Form instantiated successfully")
        print(f"✓ Form fields: {list(form.fields.keys())}")
        print(f"✓ Has selected_recipients field: {'selected_recipients' in form.fields}")
    except Exception as e:
        print(f"✗ Error instantiating form: {e}")
        
else:
    print("✗ SequentialEmailCampaign is NOT registered with admin")
    print("Available registered models:")
    for model, admin_class in admin.site._registry.items():
        print(f"  - {model.__name__}: {admin_class.__class__.__name__}")
