from rest_framework import serializers
from .models import EmailTemplate, Recipient, EmailCampaign, EmailLog, EmailConfiguration


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'subject', 'body', 'is_html', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


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
    """Serializer for sending a single email"""
    to_email = serializers.EmailField()
    to_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    subject = serializers.CharField(max_length=500)
    body = serializers.CharField()
    is_html = serializers.BooleanField(default=False)
    attachments = serializers.ListField(
        child=serializers.CharField(), 
        required=False, 
        allow_empty=True
    )
    template_id = serializers.IntegerField(required=False, allow_null=True)


class BulkEmailRecipientSerializer(serializers.Serializer):
    """Serializer for bulk email recipient"""
    email = serializers.EmailField()
    name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    company = serializers.CharField(max_length=200, required=False, allow_blank=True)
    variables = serializers.DictField(required=False, allow_empty=True)


class BulkEmailSerializer(serializers.Serializer):
    """Serializer for sending bulk emails"""
    recipients = BulkEmailRecipientSerializer(many=True)
    subject_template = serializers.CharField(max_length=500)
    body_template = serializers.CharField()
    is_html = serializers.BooleanField(default=False)
    campaign_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    delay_between_emails = serializers.FloatField(default=0, min_value=0)
    template_id = serializers.IntegerField(required=False, allow_null=True)


class EmailStatsSerializer(serializers.Serializer):
    """Serializer for email statistics"""
    total_sent = serializers.IntegerField()
    total_failed = serializers.IntegerField()
    total_pending = serializers.IntegerField()
    success_rate = serializers.FloatField()
    recent_campaigns = serializers.IntegerField()
    
    
class TemplateVariablesSerializer(serializers.Serializer):
    """Serializer for template variable replacement"""
    template_content = serializers.CharField()
    variables = serializers.DictField()
