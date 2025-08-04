from rest_framework import serializers
from .models import (
    EmailTemplate, Recipient, EmailCampaign, EmailLog, EmailConfiguration,
    EmailAttachment, TemplateAttachment
)


class EmailAttachmentSerializer(serializers.ModelSerializer):
    file_size_display = serializers.CharField(source='get_file_size_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailAttachment
        fields = ['id', 'name', 'file', 'file_url', 'content_type', 'file_size', 
                 'file_size_display', 'created_at']
        read_only_fields = ['id', 'file_size', 'created_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class EmailTemplateSerializer(serializers.ModelSerializer):
    attachments = EmailAttachmentSerializer(many=True, read_only=True)
    attachment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of attachment IDs to associate with this template"
    )
    formatting_help = serializers.CharField(source='FORMATTING_HELP', read_only=True)
    variables_help = serializers.CharField(source='VARIABLES_HELP', read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'subject', 'body', 'is_html', 'attachments', 
                 'attachment_ids', 'formatting_help', 'variables_help', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        attachment_ids = validated_data.pop('attachment_ids', [])
        template = super().create(validated_data)
        
        # Associate attachments
        for attachment_id in attachment_ids:
            try:
                attachment = EmailAttachment.objects.get(id=attachment_id)
                TemplateAttachment.objects.get_or_create(
                    template=template,
                    attachment=attachment
                )
            except EmailAttachment.DoesNotExist:
                pass  # Skip invalid attachment IDs
        
        return template
    
    def update(self, instance, validated_data):
        attachment_ids = validated_data.pop('attachment_ids', None)
        template = super().update(instance, validated_data)
        
        # Update attachments if provided
        if attachment_ids is not None:
            # Remove existing associations
            TemplateAttachment.objects.filter(template=template).delete()
            
            # Add new associations
            for attachment_id in attachment_ids:
                try:
                    attachment = EmailAttachment.objects.get(id=attachment_id)
                    TemplateAttachment.objects.get_or_create(
                        template=template,
                        attachment=attachment
                    )
                except EmailAttachment.DoesNotExist:
                    pass  # Skip invalid attachment IDs
        
        return template


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = ['id', 'email', 'name', 'company', 'additional_data', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmailCampaignSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = EmailCampaign
        fields = ['id', 'name', 'template', 'template_name', 'subject', 'body', 'is_html', 
                 'status', 'created_at', 'started_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'started_at', 'completed_at']


class EmailLogSerializer(serializers.ModelSerializer):
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    
    class Meta:
        model = EmailLog
        fields = ['id', 'campaign', 'campaign_name', 'recipient_email', 'recipient_name', 
                 'subject', 'status', 'error_message', 'sent_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'sent_at']


class EmailConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailConfiguration
        fields = ['id', 'name', 'smtp_server', 'smtp_port', 'username', 'use_tls', 'use_ssl', 
                 'is_active', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}


class SingleEmailSerializer(serializers.Serializer):
    """Serializer for sending a single email with attachments"""
    to_email = serializers.EmailField()
    to_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    subject = serializers.CharField(max_length=500)
    body = serializers.CharField(help_text="Email body. Use HTML tags for formatting if is_html=true")
    is_html = serializers.BooleanField(
        default=False, 
        help_text="Set to true for HTML formatted emails with rich text"
    )
    attachment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False, 
        allow_empty=True,
        help_text="List of attachment IDs to include with the email"
    )
    attachment_files = serializers.ListField(
        child=serializers.CharField(), 
        required=False, 
        allow_empty=True,
        help_text="List of file paths for attachments (alternative to attachment_ids)"
    )
    template_id = serializers.IntegerField(
        required=False, 
        allow_null=True,
        help_text="Use an existing template for the email"
    )


class BulkEmailRecipientSerializer(serializers.Serializer):
    """Serializer for bulk email recipient"""
    email = serializers.EmailField()
    name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    company = serializers.CharField(max_length=200, required=False, allow_blank=True)
    variables = serializers.DictField(required=False, allow_empty=True)


class BulkEmailSerializer(serializers.Serializer):
    """Serializer for sending bulk emails with attachments"""
    recipients = BulkEmailRecipientSerializer(many=True)
    subject_template = serializers.CharField(max_length=500)
    body_template = serializers.CharField(help_text="Email body template. Use HTML tags for formatting if is_html=true")
    is_html = serializers.BooleanField(
        default=False,
        help_text="Set to true for HTML formatted emails with rich text"
    )
    campaign_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    delay_between_emails = serializers.FloatField(default=0, min_value=0)
    template_id = serializers.IntegerField(required=False, allow_null=True)
    attachment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False, 
        allow_empty=True,
        help_text="List of attachment IDs to include with all emails"
    )


class EmailStatsSerializer(serializers.Serializer):
    """Serializer for email statistics"""
    total_sent = serializers.IntegerField()
    total_failed = serializers.IntegerField()
    total_pending = serializers.IntegerField()
    success_rate = serializers.FloatField()
    recent_campaigns = serializers.IntegerField()
    
    
class TemplateVariablesSerializer(serializers.Serializer):
    """Serializer for template variable replacement"""
    variables = serializers.DictField()
