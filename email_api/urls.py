from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'templates', views.EmailTemplateViewSet)
router.register(r'recipients', views.RecipientViewSet)
router.register(r'campaigns', views.EmailCampaignViewSet)
router.register(r'logs', views.EmailLogViewSet)
router.register(r'configurations', views.EmailConfigurationViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/send-email/', views.SendSingleEmailView.as_view(), name='send-single-email'),
    path('api/send-bulk-email/', views.SendBulkEmailView.as_view(), name='send-bulk-email'),
    path('api/stats/', views.EmailStatsView.as_view(), name='email-stats'),
    path('api/health/', views.health_check, name='health-check'),
]
