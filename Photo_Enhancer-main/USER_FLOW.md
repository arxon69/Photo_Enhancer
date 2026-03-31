# Photo Enhancer - Complete User Flow & Authentication Guide

## Overview
The Photo Enhancer application now has a complete user authentication system with proper redirects and access control.

## User Flow

### 1. **First Visit - Landing Page (Public)**
When a user visits the website for the first time without logging in:
- **URL**: `http://127.0.0.1:8000/`
- **Page**: Landing page with features and call-to-action
- **Content**: 
  - Feature highlights
  - Sign in button
  - Sign up button
- **Navigation**: Shows "Login" and "Sign Up" buttons

### 2. **Signup/Login Page**
- **URL**: `http://127.0.0.1:8000/accounts/login/`
- **Features**:
  - Toggle between Sign In and Sign Up views
  - Email/username and password fields
  - Form validation
- **Logic**:
  - If already logged in → redirects to home
  - On successful signup → auto-login and redirect to home
  - On successful login → redirect to home

### 3. **Authenticated User - Home Page (Photo Editor)**
When a logged-in user visits home:
- **URL**: `http://127.0.0.1:8000/`
- **Page**: Full photo editor interface
- **Content**:
  - Photo upload area
  - Processing steps
  - Customization options
  - Download functionality
- **Navigation**: Shows "Welcome, {Username}!" and "Logout" button

### 4. **Protected Routes**
- **Editor Page**: `http://127.0.0.1:8000/accounts/editor/`
  - Only accessible to authenticated users
  - Redirect to login if not authenticated

### 5. **Logout**
- User clicks "Logout" button
- Session is cleared
- Redirected to home page
- Home page now shows landing page again

## Technical Architecture

### Backend Routes

| Route | Method | Authentication | Purpose |
|-------|--------|----------------|---------|
| `/` | GET | Public | Home page (shows landing or editor) |
| `/accounts/login/` | GET/POST | Public | Login page |
| `/accounts/logout/` | GET | Any | Logout endpoint |
| `/accounts/editor/` | GET | Required | Protected editor view |
| `/accounts/api/login/` | POST | Public | Login API |
| `/accounts/api/signup/` | POST | Public | Signup API |
| `/accounts/api/logout/` | POST | Any | Logout API |
| `/accounts/api/check-auth/` | GET | Public | Check auth status |
| `/accounts/api/csrf-token/` | GET | Public | Get CSRF token |

### Frontend Components

1. **auth.js** - Authentication module
   - `Auth.login()` - Send login request
   - `Auth.signup()` - Create new account
   - `Auth.logout()` - Clear session
   - `Auth.checkAuth()` - Check if authenticated

2. **login.js** - Login page logic
   - Checks if already authenticated → redirects to home
   - Handles form submission
   - Shows signup/signin views
   - Profile photo cropping

3. **home.html** - Dynamic home page
   - Shows landing page for unauthenticated users
   - Shows editor for authenticated users
   - Updates navigation based on auth status

4. **app.js** - Photo editor functionality
   - Handles photo upload
   - Processing and enhancement
   - Customization options
   - Download functionality

## Session Management

### How Sessions Work:
1. **Login Success**: Django creates a session cookie
2. **Each Request**: Cookie is sent with requests (credentials: 'include')
3. **Session Validation**: Django verifies cookie on each request
4. **Logout**: Session is destroyed, cookie cleared

### Session Endpoints:
- Login creates a session
- Logout destroys the session
- Check-auth verifies session validity

## Database Storage

### User Table
```
- username (unique)
- email (unique)
- password (hashed with PBKDF2)
- first_name, last_name
- is_active (account status)
- date_joined, last_login (timestamps)
```

### UserProfile Table
```
- user (OneToOne relationship)
- profile_picture (optional)
- bio (optional)
- is_verified (email verification)
- created_at, updated_at
```

## Testing the Flow

### Test 1: Public Home Page
```bash
curl http://127.0.0.1:8000/
```
Should return home.html landing page (status 200)

### Test 2: Signup
```bash
curl -X POST http://127.0.0.1:8000/accounts/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","email":"new@test.com","password":"pass123","first_name":"New"}'
```

### Test 3: Login
```bash
curl -X POST http://127.0.0.1:8000/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"pass123"}' \
  -c cookies.txt
```

### Test 4: Check Auth
```bash
curl -X GET http://127.0.0.1:8000/accounts/api/check-auth/ \
  -b cookies.txt
```

### Test 5: Access Editor
```bash
curl http://127.0.0.1:8000/accounts/editor/ \
  -b cookies.txt
```

### Test 6: Logout
```bash
curl -X POST http://127.0.0.1:8000/accounts/api/logout/ \
  -b cookies.txt
```

### Run Complete Flow Test
```bash
python test_auth_flow.py
```

## User Experience Flow

```
┌─────────────────────────────────────────┐
│   User Opens Website (First Time)       │
└─────────────────────────────────────────┘
                    ↓
         ┌─────────────────┐
         │  SELECT ACTION  │
         └──────┬──────┬───┘
                │      │
         SIGN UP       LOGIN
           │              │
    ┌──────┴────┐    ┌────┴──────┐
    │ Fill Form  │    │Fill Form   │
    │ (Validate) │    │ (Validate) │
    └──────┬────┘    └────┬──────┘
           │              │
           └──────┬───────┘
                  ↓
         ┌─────────────────┐
         │Create Session   │
         │Auto-login       │
         └────────┬────────┘
                  ↓
         ┌─────────────────┐
         │ REDIRECT HOME   │
         └────────┬────────┘
                  ↓
         ┌─────────────────┐
         │   EDITOR PAGE   │
         │ (Authenticated) │
         └────────┬────────┘
                  ↓
         ┌─────────────────┐
         │Upload & Process │
         │   Your Photos   │
         └────────┬────────┘
                  ↓
         ┌─────────────────┐
         │ Download Result │
         └────────┬────────┘
                  ↓
         ┌─────────────────┐
         │    LOGOUT       │
         │ Clear Session   │
         └────────┬────────┘
                  ↓
         ┌─────────────────┐
         │ LANDING PAGE    │
         │(Back to Start)  │
         └─────────────────┘
```

## Security Features

✅ **Password Security**
- Passwords automatically hashed with PBKDF2
- Never stored in plain text
- Cannot be retrieved, only verified

✅ **Session Security**
- Django session handling
- CSRF protection on forms
- Secure cookies

✅ **Database Security**
- SQLite database (development)
- User credentials encrypted
- Session data isolated

✅ **Route Protection**
- Public routes accessible to all
- Protected routes check authentication
- Automatic redirects for unauthorized access

## Configuration

### ALLOWED_HOSTS
```python
ALLOWED_HOSTS = ['*']  # For development
```

### LOGIN URLs
```python
LOGIN_REDIRECT_URL = '/'      # Redirect after login
LOGOUT_REDIRECT_URL = '/'     # Redirect after logout
```

### API Configuration
```python
API_BASE = 'http://127.0.0.1:8000'  # Frontend API endpoint
```

## Running the Application

### 1. Terminal 1 - Start Django Server
```bash
cd Backend
python manage.py runserver
```

### 2. Browser
```
Visit: http://127.0.0.1:8000/
```

### 3. First Time Users
- See landing page
- Click "Sign In" or "Sign Up"
- Create account or login
- Automatically redirected to editor

### 4. Returning Users
- See landing page
- Click "Sign In"
- Login with credentials
- Automatically redirected to editor

## Files Modified

### Backend
- `/Backend/photo_enhancer/settings.py` - ALLOWED_HOSTS, MEDIA settings
- `/Backend/photo_enhancer/urls.py` - Root URL to home
- `/Backend/accounts/views.py` - Auth views and APIs
- `/Backend/accounts/urls.py` - Auth routes
- `/Backend/accounts/models.py` - User profile model
- `/Backend/accounts/admin.py` - Admin configuration

### Frontend
- `/Backend/accounts/templates/accounts/home.html` - Dynamic home page
- `/Backend/accounts/templates/accounts/login.html` - Login/signup page
- `/Frontend/auth.js` - Authentication module
- `/Frontend/login.js` - Login page logic

## Troubleshooting

### User sees landing page but can't login
- Check that auth.js is loaded before login.js
- Verify API Base URL matches your server URL
- Check browser console for errors

### Redirect not working after login
- Ensure `next_page` is set in LoginView
- Check that Auth.login() returns success
- Verify window.location.href is correct

### Session not persisting
- Ensure `credentials: 'include'` in fetch requests
- Check that cookies are enabled
- Verify CSRF token handling

### Editor page shows landing page when logged in
- Check Auth.checkAuth() returns true
- Verify user profile exists
- Check browser cookies for session

## Summary

✅ **Public landing page** - Anyone can see features
✅ **Authentication required** - Only logged-in users access editor
✅ **Proper redirects** - Users sent to appropriate pages
✅ **Secure sessions** - Django manages user sessions
✅ **Clean UI** - Different content for authenticated users
✅ **Full functionality** - Complete photo editing once logged in
