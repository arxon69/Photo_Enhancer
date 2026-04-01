"""
Test Script for Photo Enhancer Authentication System
Run this script to verify authentication is working with the database
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_enhancer.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.contrib.auth import authenticate

print("="*70)
print("Photo Enhancer - Authentication Test")
print("="*70)

# Test 1: Create a test user
print("\n1. Creating test user...")
try:
    test_user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='TestPassword123',
        first_name='Test'
    )
    print(f"   ✓ User created: {test_user.username}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    test_user = User.objects.get(username='testuser')

# Test 2: Verify user profile was created
print("\n2. Checking user profile...")
try:
    profile = test_user.profile
    print(f"   ✓ Profile found")
    print(f"     - is_verified: {profile.is_verified}")
    print(f"     - created_at: {profile.created_at}")
except Exception as e:
    print(f"   ✗ Profile not found: {e}")

# Test 3: Test authentication
print("\n3. Testing authentication...")
authenticated_user = authenticate(username='testuser', password='TestPassword123')
if authenticated_user is not None:
    print(f"   ✓ Authentication successful!")
    print(f"     - Username: {authenticated_user.username}")
    print(f"     - Email: {authenticated_user.email}")
    print(f"     - First Name: {authenticated_user.first_name}")
else:
    print(f"   ✗ Authentication failed!")

# Test 4: Test wrong password
print("\n4. Testing wrong password...")
wrong_auth = authenticate(username='testuser', password='WrongPassword')
if wrong_auth is None:
    print(f"   ✓ Correctly rejected wrong password")
else:
    print(f"   ✗ Should have rejected wrong password!")

# Test 5: List all users in database
print("\n5. All users in database:")
users = User.objects.all()
for i, user in enumerate(users, 1):
    try:
        profile = user.profile
        profile_status = f"✓ (verified:{profile.is_verified})"
    except:
        profile_status = "✗ No profile"
    
    print(f"   {i}. {user.username} ({user.email}) - Profile: {profile_status}")

print("\n" + "="*70)
print("All tests completed!")
print("="*70)
