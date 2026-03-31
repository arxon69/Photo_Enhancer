// Initialize generic Lucide icons
lucide.createIcons();

// Check if already authenticated - redirect to home
(async function checkAndRedirect() {
    try {
        const isAuthenticated = await Auth.checkAuth();
        if (isAuthenticated) {
            window.location.href = '/';
        }
    } catch (error) {
        console.log('Auth check error:', error);
    }
})();

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

showSignupBtn.addEventListener('click', (e) => {
    e.preventDefault();
    signinView.classList.add('hidden');
    signupView.classList.remove('hidden');
});

if (showSigninBtn) {
    showSigninBtn.addEventListener('click', (e) => {
        e.preventDefault();
        signupView.classList.add('hidden');
        signinView.classList.remove('hidden');
    });
}

// Profile Photo Crop Logic (if elements exist)
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

if (profilePicTrigger) {
    profilePicTrigger.addEventListener('click', () => {
        profileUpload.click();
    });

    profileUpload.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            const file = files[0];
            if (!file.type.startsWith('image/')) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                imageToCrop.src = event.target.result;
                openCropModal();
            };
            reader.readAsDataURL(file);
        }
        e.target.value = '';
    });

    function openCropModal() {
        cropModal.classList.remove('hidden');
        setTimeout(() => {
            if (cropper) {
                cropper.destroy();
            }
            cropper = new Cropper(imageToCrop, {
                aspectRatio: 1,
                viewMode: 1,
                dragMode: 'move',
                autoCropArea: 0.8,
                restore: false,
                guides: false,
                center: false,
                highlight: false,
                cropBoxMovable: true,
                cropBoxResizable: true,
                toggleDragModeOnDblclick: false,
            });
        }, 100);
    }

    function closeCropModal() {
        cropModal.classList.add('hidden');
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    }

    closeModalBtn.addEventListener('click', closeCropModal);
    btnCancelCrop.addEventListener('click', closeCropModal);

    btnSaveCrop.addEventListener('click', () => {
        if (!cropper) return;

        const canvas = cropper.getCroppedCanvas({
            width: 300,
            height: 300,
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'high',
        });

        profilePreview.src = canvas.toDataURL('image/jpeg');
        profilePreview.style.opacity = '1';
        profilePicOverlay.style.opacity = '0';
        profilePicOverlay.style.background = 'rgba(0,0,0,0.5)';
        profilePicOverlay.innerHTML = '<i data-lucide="edit-2"></i>';
        lucide.createIcons();

        closeCropModal();
    });
}

// Form Submission
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = loginForm.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = "Signing in...";
        btn.disabled = true;

        const email = document.getElementById('signin-email').value;
        const password = document.getElementById('signin-password').value;

        const result = await Auth.login(email, password);

        if (result.success) {
            // Redirect to home page after successful login
            window.location.href = "/";
        } else {
            alert(result.error || 'Login failed');
            btn.innerText = originalText;
            btn.disabled = false;
        }
    });
}

const signupForm = document.getElementById('signup-form');
if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = signupForm.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = "Creating Account...";
        btn.disabled = true;

        const fullName = document.getElementById('signup-name').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;

        // Use email as username
        const result = await Auth.signup(email, email, password, fullName);

        if (result.success) {
            // Redirect to home page after successful signup
            window.location.href = "/";
        } else {
            alert(result.error || 'Signup failed');
            btn.innerText = originalText;
            btn.disabled = false;
        }
    });
}
