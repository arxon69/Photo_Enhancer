# User Credential Storage & Authentication Setup Guide

## Overview
The Photo Enhancer application now has a complete user authentication system with secure credential storage in SQLite database.

## Database Structure

### 1. User Model (Django Built-in)
Stores core user information:
- `id` - Unique user identifier
- `username` - Unique username
- `email` - User email address
- `password` - Securely hashed password (PBKDF2 algorithm)
- `first_name` - User's first name
- `last_name` - User's last name (optional)
- `is_active` - Account activation status
- `is_staff` - Staff permission flag
- `is_superuser` - Admin permission flag
- `date_joined` - Account creation timestamp
- `last_login` - Last login timestamp

### 2. UserProfile Model (Custom)
Extended profile for additional user information:
- `user` - OneToOne relationship with User model
- `profile_picture` - Optional profile image
- `bio` - User biography (up to 500 characters)
- `is_verified` - Email verification status
- `created_at` - Profile creation timestamp
- `updated_at` - Profile last update timestamp

## Security Features

### Password Storage
✅ Passwords are **automatically hashed** using PBKDF2 algorithm
✅ Never stored in plain text
✅ Cannot be retrieved, only verified during login
✅ Django's `authenticate()` function handles hashing comparison

### Session Management
✅ Django sessions stored securely
✅ Session cookies with CSRF protection
✅ Automatic logout on browser close or timeout

### Email Validation
✅ Unique email checking during signup
✅ Unique username checking
✅ Email format validation

## Setup Instructions

### Step 1: Navigate to Backend Directory
```bash
cd Backend
```

### Step 2: Create Database Migrations
```bash
python manage.py makemigrations accounts
```
This creates migration files that define the database schema.

### Step 3: Apply Migrations to Database
```bash
python manage.py migrate
```
This creates the actual database tables in db.sqlite3.

### Step 4: Verify Database Setup
```bash
python manage.py check_users
```
This command checks if database is properly set up and lists all stored users.

### Step 5: Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

### Step 6: Run Development Server
```bash
python manage.py runserver
```

### Step 7: Access Admin Panel
Visit: `http://127.0.0.1:8000/admin/`
Login with superuser credentials to manage users.

## API Endpoints

### Signup
**POST** `/accounts/api/signup/`
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "first_name": "John"
}
```

Response:
```json
{
  "message": "Account created successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "is_verified": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Login
**POST** `/accounts/api/login/`
```json
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

Response:
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "is_verified": false,
    "last_login": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Check Authentication Status
**GET** `/accounts/api/check-auth/`

Response (if authenticated):
```json
{
  "authenticated": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "is_verified": false,
    "last_login": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Logout
**POST** `/accounts/api/logout/`
Response:
```json
{
  "message": "Logout successful"
}
```

## Management Commands

### Check All Users
```bash
python manage.py check_users
```
Displays all stored users with their credentials and profile information.

### Check Specific User
```bash
python manage.py check_users --username john_doe
```
Displays details for a specific user.

## Database File Location
The SQLite database is stored at:
```
Backend/db.sqlite3
```

This file contains all user credentials, profiles, and application data.

## File Structure
```
Backend/
├── db.sqlite3                  # Database file (created after migration)
├── manage.py                   # Django management script
├── setup_db.ps1               # Windows setup script
├── setup_db.sh                # Linux/Mac setup script
├── photo_enhancer/
│   ├── settings.py            # Database configuration
│   └── urls.py
├── accounts/
│   ├── models.py              # User and UserProfile models
│   ├── views.py               # Authentication APIs
│   ├── urls.py                # URL routing
│   ├── admin.py               # Django admin configuration
│   ├── management/
│   │   └── commands/
│   │       └── check_users.py # User checking command
│   └── migrations/            # Database migrations (auto-generated)
└── static/                    # CSS, JS files
```

## Troubleshooting

### Database not found
```bash
python manage.py migrate
```

### User not found in database
```bash
python manage.py check_users
```

### Migration errors
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

### Reset Database (Danger - loses all data)
```bash
# Delete the db.sqlite3 file
rm db.sqlite3

# Recreate it
python manage.py migrate
```

## Testing Authentication

### Test Signup
```bash
curl -X POST http://127.0.0.1:8000/accounts/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"pass123","first_name":"Test"}'
```

### Test Login
```bash
curl -X POST http://127.0.0.1:8000/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"pass123"}' \
  -c cookies.txt
```

### Test Check Auth
```bash
curl -X GET http://127.0.0.1:8000/accounts/api/check-auth/ \
  -b cookies.txt
```

## Summary
✅ User credentials securely stored in db.sqlite3
✅ Passwords automatically hashed with PBKDF2
✅ User profiles with extended information
✅ Complete API for signup, login, logout
✅ Authentication status checking
✅ Management commands for verification
✅ Django admin panel for user management
✅ Session-based authentication with CSRF protection
