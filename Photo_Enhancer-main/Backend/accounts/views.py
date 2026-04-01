from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, FileResponse, Http404
from django.urls import reverse_lazy
from django.conf import settings
from django.middleware.csrf import get_token
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
import logging
import json
import os

from .models import UserProfile, Photo, UserSubscription
from .tasks import process_photo

logger = logging.getLogger('accounts')


class LoginRateThrottle(AnonRateThrottle):
    rate = '10/minute'


class SignupRateThrottle(AnonRateThrottle):
    rate = '5/hour'


# =============================================================================
# PAGE VIEWS
# =============================================================================

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


def home(request):
    """Public home page - accessible to all users"""
    return render(request, 'accounts/home.html')


def app_editor(request):
    """Protected photo editor view - requires authentication"""
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/home.html')


# =============================================================================
# AUTHENTICATION APIs
# =============================================================================

class SignupAPI(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SignupRateThrottle]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')

        if not username or not email or not password:
            return Response({'error': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8:
            return Response({'error': 'Password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'A user with that username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'A user with that email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Create user with secure password hashing
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name
                )
                
                # UserProfile is automatically created via signal
                # Create subscription for user
                UserSubscription.objects.create(user=user)

            logger.info(f"New user registered: {username} ({email})")
            
            return Response({
                'message': 'Account created successfully. Please log in.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'is_verified': user.profile.is_verified,
                    'created_at': user.date_joined.isoformat()
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            return Response({'error': f'Error creating account: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                return Response({'error': 'Account is disabled.'}, status=status.HTTP_403_FORBIDDEN)
            
            login(request, user)
            logger.info(f"User logged in: {username}")
            
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'is_verified': user.profile.is_verified,
                    'tier': user.subscription.tier if hasattr(user, 'subscription') else 'free',
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'created_at': user.date_joined.isoformat()
                },
                'redirect': '/'
            }, status=status.HTTP_200_OK)
        
        logger.warning(f"Failed login attempt: {username}")
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class CheckAuthAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            subscription_info = {}
            try:
                sub = request.user.subscription
                subscription_info = {
                    'tier': sub.tier,
                    'photos_remaining': sub.get_photos_remaining() if sub.can_process_photo() else 0,
                    'is_active': sub.is_active
                }
            except UserSubscription.DoesNotExist:
                subscription_info = {'tier': 'free', 'photos_remaining': 5, 'is_active': True}
            
            return Response({
                'authenticated': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'is_verified': request.user.profile.is_verified,
                    'subscription': subscription_info,
                    'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
                    'created_at': request.user.date_joined.isoformat()
                }
            }, status=status.HTTP_200_OK)
        return Response({'authenticated': False}, status=status.HTTP_200_OK)


# =============================================================================
# PHOTO APIs
# =============================================================================

class PhotoUploadAPI(APIView):
    """Upload a new photo for enhancement"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Check if user can upload
        if hasattr(request.user, 'subscription'):
            if not request.user.subscription.can_process_photo():
                return Response({
                    'error': 'Monthly photo limit reached. Please upgrade your plan.'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        if 'photo' not in request.FILES:
            return Response({'error': 'No photo provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['photo']
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024
        if uploaded_file.size > max_size:
            return Response({'error': 'File size exceeds 10MB limit.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
        if uploaded_file.content_type not in allowed_types:
            return Response({'error': 'Invalid file type. Only JPG, PNG, and WebP are allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get enhancement settings
            settings = request.data.get('settings', '{}')
            if isinstance(settings, str):
                settings = json.loads(settings)
            
            # Create photo record
            photo = Photo.objects.create(
                user=request.user,
                original=uploaded_file,
                enhancement_settings=settings
            )
            
            logger.info(f"Photo uploaded: {photo.uuid} by {request.user.username}")
            
            # Queue for processing
            task = process_photo.delay(photo.id)
            
            return Response({
                'message': 'Photo uploaded successfully. Processing started.',
                'photo': {
                    'id': str(photo.uuid),
                    'status': photo.status,
                    'original_url': request.build_absolute_uri(photo.original.url) if photo.original else None,
                    'created_at': photo.created_at.isoformat(),
                    'task_id': task.id
                }
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Error uploading photo: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PhotoListAPI(APIView):
    """List user's photos with pagination"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get query parameters
        status_filter = request.query_params.get('status')
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 20)), 50)
        
        # Build queryset
        photos = Photo.objects.filter(
            user=request.user,
            is_deleted=False
        ).exclude(status=Photo.Status.PENDING)
        
        if status_filter:
            photos = photos.filter(status=status_filter)
        
        # Manual pagination
        total = photos.count()
        start = (page - 1) * page_size
        end = start + page_size
        photos = photos[start:end]
        
        data = []
        for photo in photos:
            data.append({
                'id': str(photo.uuid),
                'status': photo.status,
                'original': {
                    'url': request.build_absolute_uri(photo.original.url) if photo.original else None,
                    'width': photo.original_width,
                    'height': photo.original_height,
                    'size': photo.original_file_size
                },
                'enhanced': {
                    'url': request.build_absolute_uri(photo.enhanced.url) if photo.enhanced else None,
                    'width': photo.enhanced_width,
                    'height': photo.enhanced_height,
                    'size': photo.enhanced_file_size
                } if photo.status == Photo.Status.COMPLETED else None,
                'error': photo.error_message if photo.status == Photo.Status.FAILED else None,
                'processing_duration': photo.processing_duration.total_seconds() if photo.processing_duration else None,
                'created_at': photo.created_at.isoformat(),
                'updated_at': photo.updated_at.isoformat()
            })
        
        return Response({
            'photos': data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        })


class PhotoDetailAPI(APIView):
    """Get details of a specific photo"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, photo_uuid):
        try:
            photo = Photo.objects.get(uuid=photo_uuid, user=request.user, is_deleted=False)
        except Photo.DoesNotExist:
            raise Http404()
        
        return Response({
            'id': str(photo.uuid),
            'status': photo.status,
            'original': {
                'url': request.build_absolute_uri(photo.original.url) if photo.original else None,
                'width': photo.original_width,
                'height': photo.original_height,
                'size': photo.original_file_size
            },
            'enhanced': {
                'url': request.build_absolute_uri(photo.enhanced.url) if photo.enhanced else None,
                'width': photo.enhanced_width,
                'height': photo.enhanced_height,
                'size': photo.enhanced_file_size
            } if photo.status == Photo.Status.COMPLETED else None,
            'enhancement_settings': photo.enhancement_settings,
            'error': photo.error_message,
            'processing_duration': photo.processing_duration.total_seconds() if photo.processing_duration else None,
            'created_at': photo.created_at.isoformat(),
            'updated_at': photo.updated_at.isoformat()
        })
    
    def delete(self, request, photo_uuid):
        try:
            photo = Photo.objects.get(uuid=photo_uuid, user=request.user, is_deleted=False)
        except Photo.DoesNotExist:
            raise Http404()
        
        photo.delete(soft=True)
        return Response({'message': 'Photo deleted successfully'}, status=status.HTTP_200_OK)


class PhotoDownloadAPI(APIView):
    """Download enhanced photo"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, photo_uuid):
        try:
            photo = Photo.objects.get(
                uuid=photo_uuid,
                user=request.user,
                status=Photo.Status.COMPLETED,
                is_deleted=False
            )
        except Photo.DoesNotExist:
            raise Http404()
        
        if not photo.enhanced:
            return Response({'error': 'Enhanced photo not available.'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            return FileResponse(
                photo.enhanced.open(),
                as_attachment=True,
                filename=f"enhanced_{photo.uuid}.{photo.enhanced.name.split('.')[-1]}"
            )
        except Exception as e:
            logger.error(f"Error downloading photo: {str(e)}")
            return Response({'error': 'Failed to download photo.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# SUBSCRIPTION APIs
# =============================================================================

class SubscriptionAPI(APIView):
    """Get user's subscription details"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            subscription = request.user.subscription
            return Response({
                'tier': subscription.tier,
                'is_active': subscription.is_active,
                'features': UserSubscription.TIER_LIMITS[subscription.tier]['features'],
                'limits': {
                    'photos_per_month': UserSubscription.TIER_LIMITS[subscription.tier]['photos_per_month'],
                    'max_resolution': UserSubscription.TIER_LIMITS[subscription.tier]['max_resolution']
                },
                'usage': {
                    'used_this_month': subscription.photos_used_this_month,
                    'remaining': subscription.get_photos_remaining(),
                    'reset_at': subscription.photos_reset_at.isoformat()
                },
                'current_period': {
                    'start': subscription.current_period_start.isoformat() if subscription.current_period_start else None,
                    'end': subscription.current_period_end.isoformat() if subscription.current_period_end else None
                }
            })
        except UserSubscription.DoesNotExist:
            return Response({
                'tier': 'free',
                'is_active': True,
                'features': UserSubscription.TIER_LIMITS['free']['features'],
                'limits': UserSubscription.TIER_LIMITS['free'],
                'usage': {'used_this_month': 0, 'remaining': 5, 'reset_at': timezone.now().isoformat()}
            })


# =============================================================================
# HEALTH CHECK
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring"""
    from django.db import connection
    from django.core.cache import cache
    
    checks = {
        'database': 'ok',
        'cache': 'ok',
        'storage': 'ok'
    }
    status_code = 200
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
        status_code = 503
    
    # Check cache
    try:
        cache.set('health_check', 'ok', timeout=1)
        if cache.get('health_check') != 'ok':
            checks['cache'] = 'error'
            status_code = 503
    except Exception as e:
        checks['cache'] = f'error: {str(e)}'
        status_code = 503
    
    # Check storage
    try:
        if hasattr(settings, 'AWS_ACCESS_KEY_ID') and settings.AWS_ACCESS_KEY_ID:
            # S3 check logic here
            pass
    except Exception as e:
        checks['storage'] = f'error: {str(e)}'
        status_code = 503
    
    return Response({
        'status': 'healthy' if status_code == 200 else 'unhealthy',
        'timestamp': timezone.now().isoformat(),
        'checks': checks
    }, status=status_code)


@require_http_methods(["GET"])
def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})


# =============================================================================
# ADMIN STATS API
# =============================================================================

from django.contrib.admin.views.decorators import staff_member_required

@api_view(['GET'])
@staff_member_required
def admin_stats(request):
    """Admin statistics endpoint"""
    stats = {
        'users': {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
            'today': User.objects.filter(date_joined__date=timezone.now().date()).count()
        },
        'photos': {
            'total': Photo.objects.filter(is_deleted=False).count(),
            'completed': Photo.objects.filter(status=Photo.Status.COMPLETED, is_deleted=False).count(),
            'processing': Photo.objects.filter(status=Photo.Status.PROCESSING).count(),
            'failed': Photo.objects.filter(status=Photo.Status.FAILED).count(),
            'today': Photo.objects.filter(created_at__date=timezone.now().date()).count()
        },
        'subscriptions': {
            'free': UserSubscription.objects.filter(tier='free').count(),
            'pro': UserSubscription.objects.filter(tier='pro').count(),
            'enterprise': UserSubscription.objects.filter(tier='enterprise').count()
        }
    }
    return Response(stats)
