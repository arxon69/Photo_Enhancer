from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Auth Views
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('accounts/editor/', views.app_editor, name='editor'),
    
    # Auth APIs
    path('accounts/api/login/', views.LoginAPI.as_view(), name='api_login'),
    path('accounts/api/signup/', views.SignupAPI.as_view(), name='api_signup'),
    path('accounts/api/logout/', views.LogoutAPI.as_view(), name='api_logout'),
    path('accounts/api/check-auth/', views.CheckAuthAPI.as_view(), name='api_check_auth'),
    path('accounts/api/csrf-token/', views.get_csrf_token, name='api_csrf_token'),
    
    # Photo APIs
    path('api/photos/', views.PhotoListAPI.as_view(), name='api_photo_list'),
    path('api/photos/upload/', views.PhotoUploadAPI.as_view(), name='api_photo_upload'),
    path('api/photos/<uuid:photo_uuid>/', views.PhotoDetailAPI.as_view(), name='api_photo_detail'),
    path('api/photos/<uuid:photo_uuid>/download/', views.PhotoDownloadAPI.as_view(), name='api_photo_download'),
    
    # AI Enhancer APIs
    path('api/ai-services/status/', views.ai_service_status, name='api_ai_service_status'),
    path('api/ai-services/options/', views.enhancement_options, name='api_enhancement_options'),
    
    # Subscription API
    path('api/subscription/', views.SubscriptionAPI.as_view(), name='api_subscription'),
    
    # Health Check
    path('health/', views.health_check, name='health_check'),
    
    # Admin Stats
    path('api/admin/stats/', views.admin_stats, name='api_admin_stats'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
