"""
Admin site customization for Mailer Application
"""
from django.contrib import admin
from django.template.response import TemplateResponse


# Customize the default admin site
admin.site.site_header = "Mailer Application"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "The Mailer"


# Override the admin index view to add custom context
original_index = admin.site.index

def custom_index(request, extra_context=None):
    """
    Display the main admin index page with custom context.
    """
    extra_context = extra_context or {}
    extra_context.update({
        'app_description': '''
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #007cba;">
                <h3 style="margin-top: 0; color: #007cba;">📧 Mailer Application Dashboard</h3>
                <p style="margin-bottom: 10px; font-size: 14px; line-height: 1.6;">
                    This is your central hub for managing all email marketing activities. From here you can:
                </p>
                <ul style="margin-bottom: 0; font-size: 14px; line-height: 1.6;">
                    <li><strong>📄 Email Templates:</strong> Create and manage reusable email templates with dynamic placeholders</li>
                    <li><strong>👥 Recipients:</strong> Manage your contact lists and recipient information</li>
                    <li><strong>📈 Email Campaigns:</strong> Design and launch email marketing campaigns</li>
                    <li><strong>📊 Email Logs:</strong> Track email delivery status and campaign performance</li>
                    <li><strong>⚙️ Configuration:</strong> Set up SMTP settings and email preferences</li>
                    <li><strong>🗓️ Scheduled Campaigns:</strong> Plan and automate your email marketing</li>
                </ul>
            </div>
        '''
    })
    return original_index(request, extra_context)

# Replace the index method
admin.site.index = custom_index
