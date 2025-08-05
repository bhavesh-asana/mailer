#!/usr/bin/env python3
"""
Test script to verify timezone handling in the email dashboard
"""

import os
import django
from datetime import datetime, timezone as dt_timezone
import pytz

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailer.settings')
django.setup()

from django.utils import timezone
from email_api.models import ScheduledEmailCampaign, EmailTemplate, Recipient

def test_timezone_handling():
    """Test timezone conversion and handling"""
    
    print("🕐 Testing Timezone Handling")
    print("=" * 50)
    
    # Current time in different formats
    now_utc = timezone.now()
    now_local = now_utc.astimezone(timezone.get_current_timezone())
    
    print(f"Current UTC time: {now_utc}")
    print(f"Current local time: {now_local}")
    print(f"Local timezone: {timezone.get_current_timezone()}")
    
    # Test timezone conversion
    user_timezones = [
        'America/New_York',
        'Europe/London', 
        'Asia/Tokyo',
        'Australia/Sydney',
        'America/Los_Angeles'
    ]
    
    print("\n🌍 Time in different user timezones:")
    for tz_name in user_timezones:
        tz = pytz.timezone(tz_name)
        local_time = now_utc.astimezone(tz)
        print(f"  {tz_name}: {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Test creating a scheduled campaign with timezone-aware datetime
    print(f"\n📧 Testing Campaign Creation:")
    
    # Create a test datetime (1 hour from now in a specific timezone)
    test_tz = pytz.timezone('America/New_York')
    test_time = now_utc.astimezone(test_tz)
    test_time = test_time.replace(hour=test_time.hour + 1)
    
    print(f"Test scheduled time (Eastern): {test_time}")
    print(f"Test scheduled time (UTC): {test_time.astimezone(pytz.UTC)}")
    
    # Verify JavaScript date format compatibility
    iso_format = test_time.isoformat()
    datetime_local_format = test_time.strftime('%Y-%m-%dT%H:%M')
    
    print(f"\nFormat compatibility:")
    print(f"  ISO format: {iso_format}")
    print(f"  datetime-local format: {datetime_local_format}")
    
    # Test parsing back
    parsed_date = datetime.fromisoformat(iso_format.replace('Z', '+00:00'))
    print(f"  Parsed back: {parsed_date}")
    
    print("\n✅ Timezone handling test completed!")

if __name__ == "__main__":
    test_timezone_handling()
