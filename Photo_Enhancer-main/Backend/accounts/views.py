from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.middleware.csrf import get_token

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

class SignupAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')

        if not username or not email or not password:
            return Response({'error': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 6:
            return Response({'error': 'Password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'A user with that username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'A user with that email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user with secure password hashing (automatic via Django)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name
            )
            
            # UserProfile is automatically created via signal
            user.refresh_from_db()

            return Response({
                'message': 'Account created successfully. Please log in.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'created_at': user.date_joined.isoformat()
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Error creating account: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'is_verified': user.profile.is_verified,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'created_at': user.date_joined.isoformat()
                }
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutAPI(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

class CheckAuthAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'is_verified': request.user.profile.is_verified,
                    'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
                    'created_at': request.user.date_joined.isoformat()
                }
            }, status=status.HTTP_200_OK)
        return Response({'authenticated': False}, status=status.HTTP_200_OK)

@require_http_methods(["GET"])
def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})
