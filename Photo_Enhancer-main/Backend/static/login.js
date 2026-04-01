// Initialize generic Lucide icons
lucide.createIcons();

// Theme Management
const themeToggleBtn = document.getElementById('theme-toggle');
let theme = localStorage.getItem('theme') || 'light';

function initTheme() {
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (!localStorage.getItem('theme')) {
        theme = prefersDark ? 'dark' : 'light';
        localStorage.setItem('theme', theme);
    }
    applyTheme();
    themeToggleBtn.addEventListener('click', toggleTheme);
}

function toggleTheme() {
    theme = theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    applyTheme();
}

function applyTheme() {
    document.documentElement.setAttribute('data-theme', theme);
    const iconName = theme === 'light' ? 'moon' : 'sun';
    themeToggleBtn.innerHTML = `<i data-lucide="${iconName}"></i>`;
    lucide.createIcons();
}

initTheme();

// View Switcher Logic
const signinView = document.getElementById('signin-view');
const signupView = document.getElementById('signup-view');
const showSignupBtn = document.getElementById('show-signup');
const showSigninBtn = document.getElementById('show-signin');

// Check URL for initial view
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('signup') === 'true') {
    signinView?.classList.add('hidden');
    signupView?.classList.remove('hidden');
}

if (showSignupBtn) {
    showSignupBtn.addEventListener('click', (e) => {
        e.preventDefault();
        signinView?.classList.add('hidden');
        signupView?.classList.remove('hidden');
        // Update URL without reloading
        window.history.pushState({}, '', '?signup=true');
    });
}

if (showSigninBtn) {
    showSigninBtn.addEventListener('click', (e) => {
        e.preventDefault();
        signupView?.classList.add('hidden');
        signinView?.classList.remove('hidden');
        // Update URL without reloading
        window.history.pushState({}, '', '?');
    });
}

// Helper to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Notification System
function showNotification(title, message, type = 'primary', duration = 4000) {
    const container = document.getElementById('notification-container');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const iconName = type === 'success' ? 'check-circle' : 'info';
    
    notification.innerHTML = `
        <div class="notification-icon">
            <i data-lucide="${iconName}"></i>
        </div>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close">
            <i data-lucide="x"></i>
        </button>
    `;

    container.appendChild(notification);
    lucide.createIcons();

    // Show with delay to trigger animation
    setTimeout(() => notification.classList.add('show'), 10);

    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 400);
    });

    // Auto-remove
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 400);
        }
    }, duration);
}

// Sign-in form
const loginForm = document.getElementById('login-form');
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = loginForm.querySelector('button[type="submit"]');
    const originalText = btn.innerText;
    btn.innerText = 'Signing in...';
    btn.disabled = true;

    const email = document.getElementById('signin-email').value;
    const password = document.getElementById('signin-password').value;

    try {
        const response = await fetch('/accounts/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ username: email, password }),
        });

        const data = await response.json();
        if (response.ok) {
            showNotification('Welcome back!', 'Login successful. Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showNotification('Login failed', data.error || 'Invalid credentials', 'primary');
            btn.innerText = originalText;
            btn.disabled = false;
        }
    } catch (error) {
        showNotification('Error', 'Connection failed: ' + error.message, 'primary');
        btn.innerText = originalText;
        btn.disabled = false;
    }
});

// Sign-up form
const signupForm = document.getElementById('signup-form');
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = signupForm.querySelector('button[type="submit"]');
    const originalText = btn.innerText;
    btn.innerText = 'Creating account...';
    btn.disabled = true;

    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;

    try {
        const response = await fetch('/accounts/api/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ 
                username: email, // Use email as username
                email: email, 
                password: password,
                first_name: name 
            }),
        });

        const data = await response.json();
        if (response.ok) {
            showNotification('Success!', 'Account created successfully. Please sign in.', 'success');
            setTimeout(() => {
                // Switch to sign-in view
                signupView?.classList.add('hidden');
                signinView?.classList.remove('hidden');
                window.history.pushState({}, '', '?');
                // Fill in the email to make it easier for the user
                document.getElementById('signin-email').value = email;
                btn.innerText = originalText;
                btn.disabled = false;
            }, 2000);
        } else {
            showNotification('Account Creation Failed', data.error || 'Please try again', 'primary');
            btn.innerText = originalText;
            btn.disabled = false;
        }
    } catch (error) {
        showNotification('Error', 'Connection failed: ' + error.message, 'primary');
        btn.innerText = originalText;
        btn.disabled = false;
    }
});

// Profile upload/crop code can be imported from app.js if needed:
const profilePicTrigger = document.getElementById('profile-pic-trigger');
const profileUpload = document.getElementById('profile-upload');
const profilePreview = document.getElementById('profile-preview');
const profilePicOverlay = document.getElementById('profile-pic-overlay');
const cropModal = document.getElementById('crop-modal');
const closeModalBtn = document.getElementById('close-modal');
const btnCancelCrop = document.getElementById('btn-cancel-crop');
const btnSaveCrop = document.getElementById('btn-save-crop');
const imageToCrop = document.getElementById('image-to-crop');
let cropper = null;

profilePicTrigger?.addEventListener('click', () => profileUpload?.click());
profileUpload?.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
        const file = files[0];
        if (!file.type.startsWith('image/')) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            imageToCrop.src = event.target.result;
            cropModal.classList.remove('hidden');
            setTimeout(() => {
                if (cropper) cropper.destroy();
                cropper = new Cropper(imageToCrop, {
                    aspectRatio: 1,
                    viewMode: 1,
                    dragMode: 'move',
                    autoCropArea: 0.8,
                    restore: false,
                    guides: false,
                    minContainerWidth: 320,
                    minContainerHeight: 320,
                });
            }, 100);
        };
        reader.readAsDataURL(file);
    }
    e.target.value = '';
});

closeModalBtn?.addEventListener('click', () => cropModal?.classList.add('hidden'));
btnCancelCrop?.addEventListener('click', () => cropModal?.classList.add('hidden'));
btnSaveCrop?.addEventListener('click', () => {
    if (!cropper) return;
    const canvas = cropper.getCroppedCanvas({ width: 200, height: 200 });
    profilePreview.src = canvas.toDataURL('image/png');
    profilePreview.style.opacity = 1;
    profilePicOverlay.style.opacity = 0;
    cropModal.classList.add('hidden');
});