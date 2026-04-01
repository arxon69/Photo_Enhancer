from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('editor/', views.app_editor, name='editor'),
    path('api/login/', views.LoginAPI.as_view(), name='api_login'),
    path('api/signup/', views.SignupAPI.as_view(), name='api_signup'),
    path('api/logout/', views.LogoutAPI.as_view(), name='api_logout'),
    path('api/check-auth/', views.CheckAuthAPI.as_view(), name='api_check_auth'),
    path('api/csrf-token/', views.get_csrf_token, name='api_csrf_token'),
]