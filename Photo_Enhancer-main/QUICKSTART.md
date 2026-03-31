# Photo Enhancer - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Start the Server
```bash
cd Backend
python manage.py runserver
```

### Step 2: Open in Browser
```
Visit: http://127.0.0.1:8000/
```

### Step 3: Sign Up
1. Click "Sign Up" button on landing page
2. Enter your details:
   - Full Name
   - Email
   - Password
3. Create account → Automatically logged in → Redirected to editor

### Step 4: Start Editing
1. Click "Choose Photo" or drag & drop
2. Follow the 4-step process:
   - Upload
   - Process
   - Customize
   - Download

### Step 5: Logout
- Click "Logout" button
- Returned to landing page

---

## 📊 User Access Matrix

| User Type | Landing Page | Login Page | Editor | Database |
|-----------|:------------:|:----------:|:------:|:--------:|
| **Guest** | ✅ Visible | ✅ Access | ❌ Blocked | - |
| **Signed Up** | ✅ Visible | ✅ Redirect | ✅ Full Access | ✅ Stored |
| **Logged In** | ✅ Visible | ✅ Redirect Home | ✅ Full Access | ✅ Accessed |

---

## 🔐 Authentication Rules

### Public Routes
- `/` - Landing/Editor page
- `/accounts/login/` - Login/Signup
- `/accounts/api/signup/` - Create account

### Protected Routes
- `/accounts/editor/` - Photo editor (requires login)
- `/accounts/api/logout/` - Requires session

### Redirects
- **Not logged in + Try editor** → Redirect to login
- **Already logged in + Try login** → Redirect to home
- **After login** → Redirect to home/editor
- **After logout** → Redirect to landing page

---

## 💾 Data Storage

All user data stored in `Backend/db.sqlite3`:

**User Table**
```
✅ username (email)
✅ password (hashed)
✅ email
✅ name
✅ account status
✅ login history
```

**User Profile**
```
✅ profile picture
✅ bio
✅ verification status
✅ timestamps
```

---

## 🧪 Testing the System

### Test Signup
```bash
# Create new account
Visit: http://127.0.0.1:8000/accounts/login/
Click: "Sign up"
Fill form
Click: "Create Account"

Expected: Auto-login and redirect to editor ✅
```

### Test Login
```bash
# Login with existing account
Visit: http://127.0.0.1:8000/accounts/login/
Fill login form
Click: "Sign In"

Expected: Redirect to editor ✅
```

### Test Protection
```bash
# Try to access editor without login
Visit: http://127.0.0.1:8000/accounts/editor/
(While not logged in)

Expected: Redirect to login ✅
```

### Test Logout
```bash
# Logout from editor
Click: "Logout" button

Expected: Redirect to landing page ✅
```

### Check Users in Database
```bash
python manage.py check_users
```

Shows all stored users and profiles ✅

---

## 🎯 User Journey Examples

### Example 1: New User
```
1. Visit website → See landing page
2. Click "Sign Up"
3. Create account (username, email, password)
4. Auto-login → Redirect to editor
5. Upload photo → Edit → Download
6. Click "Logout" → Back to landing page
```

### Example 2: Returning User
```
1. Visit website → See landing page
2. Click "Sign In"
3. Enter username & password
4. Redirect to editor (because logged in)
5. Upload photo → Edit → Download
6. Click "Logout" → Back to landing page
```

### Example 3: Return Visit
```
1. Logout in previous session
2. Next day, visit website → See landing page (not logged in)
3. Click "Sign In"
4. Enter credentials
5. Redirect to editor
6. Continue editing
```

---

## ⚙️ Settings Overview

### Location: `Backend/photo_enhancer/settings.py`

**Database**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Allowed Hosts** (for development)
```python
ALLOWED_HOSTS = ['*']
```

**Login/Logout Redirect**
```python
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

---

## 🛠️ Management Commands

### Check All Users
```bash
python manage.py check_users
```

### Check Specific User
```bash
python manage.py check_users --username admin
```

### Create Admin Account
```bash
python manage.py createsuperuser
```

### Test Complete Flow
```bash
python test_auth_flow.py
```

### Test Authentication
```bash
python test_auth.py
```

---

## 📝 File Structure

```
Photo_Enhancer-main/
├── Backend/
│   ├── db.sqlite3                 # User data stored here
│   ├── manage.py
│   ├── test_auth.py              # Authentication test
│   ├── test_auth_flow.py          # Complete flow test
│   ├── photo_enhancer/
│   │   ├── settings.py            # App configuration
│   │   └── urls.py                # URL routing
│   ├── accounts/
│   │   ├── models.py              # User & Profile models
│   │   ├── views.py               # Authentication logic
│   │   ├── urls.py                # Account routes
│   │   ├── admin.py               # Django admin
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── check_users.py
│   │   │       └── create_missing_profiles.py
│   │   └── templates/accounts/
│   │       ├── home.html          # Dynamic home page
│   │       └── login.html         # Login/signup page
│   └── static/
│       ├── auth.js                # Auth module
│       ├── app.js                 # Editor logic
│       └── style.css              # Styling
├── Frontend/
│   ├── auth.js                    # Frontend auth
│   ├── login.js                   # Login logic
│   └── index.html                 # Static home page (not used)
└── USER_FLOW.md                   # Detailed documentation
```

---

## ✅ Verification Checklist

- [ ] Server running on port 8000
- [ ] Can visit home page (landing page visible)
- [ ] Can click "Sign Up" and create account
- [ ] After signup, redirected to editor
- [ ] Can upload photos in editor
- [ ] Can logout and return to landing page
- [ ] Can login again with same credentials
- [ ] Already logged in users redirect from login page
- [ ] `python manage.py check_users` shows accounts

---

## 🎨 What's Visible Where

### Landing Page (Unauthenticated)
```
┌─────────────────────────────────────┐
│  Photo Maker                   Logout│  (If authenticated)
├─────────────────────────────────────┤
│                                     │
│     Transform Your Photos           │
│                                     │
│   [Auto Enhancement]                │
│   [Easy Cropping]                   │
│   [Custom Backgrounds]              │
│                                     │
│         [Sign In]  [Sign Up]       │
│                                     │
└─────────────────────────────────────┘
```

### Editor Page (Authenticated)
```
┌─────────────────────────────────────┐
│  Photo Maker     Welcome, User! │Logout│
├─────────────────────────────────────┤
│ 1️⃣ Upload  2️⃣ Process  3️⃣ Customize  4️⃣ Download │
├─────────────────────────────────────┤
│                                     │
│     Upload Your Photo              │
│     [Choose Photo Button]           │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔗 Useful Links

- **Home**: http://127.0.0.1:8000/
- **Login**: http://127.0.0.1:8000/accounts/login/
- **Editor**: http://127.0.0.1:8000/accounts/editor/
- **Admin**: http://127.0.0.1:8000/admin/
- **API Docs**: See USER_FLOW.md

---

## 📞 Support

If something isn't working:

1. Check browser console (F12) for errors
2. Check Django server output
3. Run: `python test_auth_flow.py`
4. Check users: `python manage.py check_users`
5. See detailed docs: Open `USER_FLOW.md`

---

**You're all set! 🎉 Enjoy your Photo Enhancer!**
