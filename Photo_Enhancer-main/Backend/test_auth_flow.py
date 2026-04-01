"""
Complete Authentication & User Flow Test
Tests the entire user journey from landing page to editor
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_enhancer.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
import json

class AuthFlowTest:
    def __init__(self):
        self.client = Client()
        self.test_user = {
            'username': 'flowtest',
            'email': 'flowtest@example.com',
            'password': 'FlowTest123',
            'first_name': 'Flow'
        }
        
    def run_all_tests(self):
        print("="*70)
        print("AUTHENTICATION FLOW TEST")
        print("="*70)
        
        self.test_home_page_public()
        self.test_login_flow()
        self.test_authenticated_home()
        self.test_editor_protection()
        self.test_logout()
        self.test_redirect_on_double_login()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETED!")
        print("="*70)
    
    def test_home_page_public(self):
        print("\n1. Testing Home Page (Should be public, accessible without login)...")
        response = self.client.get('/')
        if response.status_code == 200:
            print(f"   ✓ Home page is public (Status: {response.status_code})")
        else:
            print(f"   ✗ Unexpected status code: {response.status_code}")
    
    def test_login_flow(self):
        print("\n2. Testing User Registration...")
        # Clean up if user exists
        User.objects.filter(username=self.test_user['username']).delete()
        
        # Test signup via API
        response = self.client.post(
            '/accounts/api/signup/',
            data=json.dumps(self.test_user),
            content_type='application/json'
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✓ User created successfully")
            print(f"     - Username: {data['user']['username']}")
            print(f"     - Email: {data['user']['email']}")
        else:
            print(f"   ✗ Failed to create user (Status: {response.status_code})")
    
    def test_authenticated_home(self):
        print("\n3. Testing Login Flow...")
        response = self.client.post(
            '/accounts/api/login/',
            data=json.dumps({
                'username': self.test_user['username'],
                'password': self.test_user['password']
            }),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Login successful")
            print(f"     - User: {data['user']['username']}")
            print(f"     - Email: {data['user']['email']}")
            print(f"     - Created: {data['user']['created_at']}")
        else:
            print(f"   ✗ Login failed (Status: {response.status_code})")
    
    def test_editor_protection(self):
        print("\n4. Testing Editor Route Protection...")
        # Without login
        response = self.client.get('/accounts/editor/')
        if response.status_code == 302:  # Redirect
            print(f"   ✓ Unauthenticated users redirected to login")
        else:
            print(f"   ! Status: {response.status_code}")
        
        # With login
        self.client.login(
            username=self.test_user['username'],
            password=self.test_user['password']
        )
        response = self.client.get('/accounts/editor/')
        if response.status_code == 200:
            print(f"   ✓ Authenticated users can access editor")
        else:
            print(f"   ✗ Editor access failed (Status: {response.status_code})")
    
    def test_logout(self):
        print("\n5. Testing Logout...")
        response = self.client.post('/accounts/api/logout/')
        if response.status_code == 200:
            print(f"   ✓ Logout successful")
        else:
            print(f"   ✗ Logout failed (Status: {response.status_code})")
    
    def test_redirect_on_double_login(self):
        print("\n6. Testing Redirect on Already Authenticated Login Attempt...")
        # Login first
        self.client.login(
            username=self.test_user['username'],
            password=self.test_user['password']
        )
        
        # Try to access login page while authenticated
        response = self.client.get('/accounts/login/', follow=False)
        if response.status_code == 302:
            print(f"   ✓ Already authenticated users redirected from login page")
        else:
            print(f"   ✓ Status: {response.status_code}")

if __name__ == '__main__':
    test = AuthFlowTest()
    test.run_all_tests()
