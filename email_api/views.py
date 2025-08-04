from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
import re
from string import Template

from .models import EmailTemplate, Recipient, EmailCampaign, EmailLog, EmailConfiguration, EmailAttachment
from .serializers import (
    EmailTemplateSerializer, RecipientSerializer, EmailCampaignSerializer,
    EmailLogSerializer, EmailConfigurationSerializer, SingleEmailSerializer,
    BulkEmailSerializer, EmailStatsSerializer, TemplateVariablesSerializer,
    EmailAttachmentSerializer
)
from .email_service import EmailSender, EmailData, get_email_sender


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing email templates"""
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def test_variables(self, request, pk=None):
        """Test template variable replacement"""
        template = self.get_object()
        serializer = TemplateVariablesSerializer(data=request.data)
        if serializer.is_valid():
            variables = serializer.validated_data['variables']
            try:
                subject_template = Template(template.subject)
                body_template = Template(template.body)
                
                rendered_subject = subject_template.safe_substitute(**variables)
                rendered_body = body_template.safe_substitute(**variables)
                
                return Response({
                    'rendered_subject': rendered_subject,
                    'rendered_body': rendered_body,
                    'original_subject': template.subject,
                    'original_body': template.body
                })
            except Exception as e:
                return Response(
                    {'error': f'Template rendering error: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipientViewSet(viewsets.ModelViewSet):
    """ViewSet for managing recipients"""
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Recipient.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create recipients from list"""
        recipients_data = request.data.get('recipients', [])
        created_count = 0
        errors = []
        
        for recipient_data in recipients_data:
            serializer = RecipientSerializer(data=recipient_data)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({
                    'data': recipient_data,
                    'errors': serializer.errors
                })
        
        return Response({
            'created_count': created_count,
            'total_count': len(recipients_data),
            'errors': errors
        })


class EmailCampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for managing email campaigns"""
    queryset = EmailCampaign.objects.all()
    serializer_class = EmailCampaignSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def start_campaign(self, request, pk=None):
        """Start an email campaign"""
        campaign = self.get_object()
        if campaign.status != 'draft':
            return Response(
                {'error': 'Only draft campaigns can be started'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.status = 'sending'
        campaign.started_at = timezone.now()
        campaign.save()
        
        # Here you could trigger background task for sending emails
        return Response({'message': 'Campaign started successfully'})


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing email logs"""
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = EmailLog.objects.all()
        campaign_id = self.request.query_params.get('campaign', None)
        status_filter = self.request.query_params.get('status', None)
        
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset


class EmailConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing email configurations"""
    queryset = EmailConfiguration.objects.all()
    serializer_class = EmailConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test email configuration connection"""
        config = self.get_object()
        try:
            from .email_service import EmailConfig, EmailSender
            email_config = EmailConfig(
                smtp_server=config.smtp_server,
                smtp_port=config.smtp_port,
                username=config.username,
                password=config.password,
                use_tls=config.use_tls,
                use_ssl=config.use_ssl
            )
            
            sender = EmailSender(email_config)
            # Test connection
            with sender._create_smtp_connection():
                pass
            
            return Response({'message': 'Connection successful'})
        except Exception as e:
            return Response(
                {'error': f'Connection failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class EmailAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing email attachments"""
    queryset = EmailAttachment.objects.all()
    serializer_class = EmailAttachmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        queryset = EmailAttachment.objects.all()
        template_id = self.request.query_params.get('template', None)
        if template_id:
            queryset = queryset.filter(templates__id=template_id)
        return queryset


class SendSingleEmailView(APIView):
    """API view for sending a single email"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=SingleEmailSerializer,
        responses={
            200: openapi.Response('Email sent successfully'),
            400: 'Bad Request',
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        """Send a single email"""
        serializer = SingleEmailSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Get template if specified
            template = None
            if data.get('template_id'):
                try:
                    template = EmailTemplate.objects.get(id=data['template_id'])
                    # Use template data if not overridden
                    if not data.get('subject') and template.subject:
                        data['subject'] = template.subject
                    if not data.get('body') and template.body:
                        data['body'] = template.body
                        data['is_html'] = template.is_html
                except EmailTemplate.DoesNotExist:
                    return Response(
                        {'error': 'Template not found'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            try:
                email_data = EmailData(
                    to_email=data['to_email'],
                    to_name=data.get('to_name', ''),
                    subject=data['subject'],
                    body=data['body'],
                    is_html=data.get('is_html', False),
                    attachments=data.get('attachments', []),
                    attachment_ids=data.get('attachment_ids', [])
                )
                
                sender = get_email_sender()
                success = sender.send_single_email(email_data)
                
                if success:
                    return Response({
                        'message': 'Email sent successfully',
                        'recipient': data['to_email'],
                        'status': 'sent'
                    })
                else:
                    return Response(
                        {'error': 'Failed to send email'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except Exception as e:
                return Response(
                    {'error': f'Error sending email: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendBulkEmailView(APIView):
    """API view for sending bulk emails"""
    permission_classes = [AllowAny]  # Open for development
    
    @swagger_auto_schema(
        request_body=BulkEmailSerializer,
        responses={
            200: openapi.Response('Bulk emails processed'),
            400: 'Bad Request',
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        """Send bulk emails"""
        serializer = BulkEmailSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Create campaign if name provided
            campaign = None
            if data.get('campaign_name'):
                campaign = EmailCampaign.objects.create(
                    name=data['campaign_name'],
                    subject=data['subject_template'],
                    body=data['body_template'],
                    is_html=data.get('is_html', False),
                    status='sending',
                    started_at=timezone.now(),
                    created_by=request.user if request.user.is_authenticated else None
                )
            
            try:
                sender = get_email_sender()
                emails_to_send = []
                
                for recipient in data['recipients']:
                    # Process template variables
                    variables = recipient.get('variables', {})
                    variables.update({
                        'name': recipient.get('name', ''),
                        'first_name': recipient.get('first_name', ''),
                        'last_name': recipient.get('last_name', ''),
                        'email': recipient['email'],
                        'company': recipient.get('company', '')
                    })
                    
                    subject_template = Template(data['subject_template'])
                    body_template = Template(data['body_template'])
                    
                    rendered_subject = subject_template.safe_substitute(**variables)
                    rendered_body = body_template.safe_substitute(**variables)
                    
                    email_data = EmailData(
                        to_email=recipient['email'],
                        to_name=recipient.get('name', ''),
                        subject=rendered_subject,
                        body=rendered_body,
                        is_html=data.get('is_html', False),
                        attachment_ids=data.get('attachment_ids', [])
                    )
                    emails_to_send.append(email_data)
                
                results = sender.send_bulk_emails(
                    emails_to_send, 
                    campaign.id if campaign else None,
                    data.get('delay_between_emails', 0)
                )
                
                # Update campaign status
                if campaign:
                    campaign.status = 'completed'
                    campaign.completed_at = timezone.now()
                    campaign.save()
                
                return Response({
                    'message': 'Bulk emails processed',
                    'results': results,
                    'campaign_id': campaign.id if campaign else None
                })
                
            except Exception as e:
                if campaign:
                    campaign.status = 'failed'
                    campaign.save()
                return Response(
                    {'error': f'Error sending bulk emails: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailStatsView(APIView):
    """API view for email statistics"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        responses={200: EmailStatsSerializer}
    )
    def get(self, request):
        """Get email statistics"""
        # Get overall statistics
        total_sent = EmailLog.objects.filter(status='sent').count()
        total_failed = EmailLog.objects.filter(status='failed').count()
        total_pending = EmailLog.objects.filter(status='pending').count()
        
        total = total_sent + total_failed
        success_rate = round((total_sent / total * 100) if total > 0 else 0, 2)
        
        # Recent campaigns (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_campaigns = EmailCampaign.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        stats = {
            'total_sent': total_sent,
            'total_failed': total_failed,
            'total_pending': total_pending,
            'success_rate': success_rate,
            'recent_campaigns': recent_campaigns
        }
        
        return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'service': 'Email API'
    })
