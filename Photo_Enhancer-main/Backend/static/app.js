console.log('Starting app.js initialization...');

// Ensure DOM is ready
function initializeEditor() {
    try {
        console.log('Initializing editor...');
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

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
            if (themeToggleBtn) {
                themeToggleBtn.addEventListener('click', toggleTheme);
            }
        }

        function toggleTheme() {
            theme = theme === 'light' ? 'dark' : 'light';
            localStorage.setItem('theme', theme);
            applyTheme();
        }

        function applyTheme() {
            document.documentElement.setAttribute('data-theme', theme);
            const iconName = theme === 'light' ? 'moon' : 'sun';
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = `<i data-lucide="${iconName}"></i>`;
            }
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }

        initTheme();

        // Photo Editor Elements
        const uploadBtn = document.getElementById('upload-btn');
        const photoInput = document.getElementById('photo-input');
        const uploadArea = document.getElementById('upload-area');

        const uploadSection = document.getElementById('upload-section');
        const processingSection = document.getElementById('processing-section');
        const resultSection = document.getElementById('result-section');
        const progressFill = document.getElementById('progress-fill');

        const originalImg = document.getElementById('original-img');
        const enhancedImg = document.getElementById('enhanced-img');
        const editBtn = document.getElementById('edit-btn');
        const downloadBtn = document.getElementById('download-btn');

        console.log('Element references:', {
            uploadBtn: !!uploadBtn,
            photoInput: !!photoInput,
            uploadArea: !!uploadArea,
            uploadSection: !!uploadSection,
            processingSection: !!processingSection,
            resultSection: !!resultSection,
            originalImg: !!originalImg,
            enhancedImg: !!enhancedImg,
            editBtn: !!editBtn,
            downloadBtn: !!downloadBtn
        });

        // State
        let currentImageFile = null;
        let isAuthenticated = false;

        // Check auth status
        async function checkAuthStatus() {
            isAuthenticated = await Auth.checkAuth();
            console.log('Auth status:', isAuthenticated);
        }
        checkAuthStatus();

        // Upload Button Click - This is what the user asked for
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => {
                console.log('Upload button clicked');
                if (!isAuthenticated) {
                    window.location.href = '/accounts/login/';
                    return;
                }
                if (photoInput) {
                    photoInput.click();
                }
            });
            console.log('✓ Upload button listener attached');
        }

        // File Input Change
        if (photoInput) {
            photoInput.addEventListener('change', (e) => {
                if (!isAuthenticated) {
                    window.location.href = '/accounts/login/';
                    return;
                }
                const file = e.target.files[0];
                console.log('File selected:', file?.name);
                if (file && file.type.startsWith('image/')) {
                    currentImageFile = file;
                    processImage(file);
                } else {
                    alert('Please select a valid image file');
                }
            });
            console.log('✓ Photo input listener attached');
        }

        // Drag and Drop Support
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                if (isAuthenticated) {
                    uploadArea.style.borderColor = 'var(--primary)';
                    uploadArea.style.backgroundColor = 'rgba(59, 130, 246, 0.05)';
                }
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.borderColor = 'var(--border)';
                uploadArea.style.backgroundColor = 'transparent';
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = 'var(--border)';
                uploadArea.style.backgroundColor = 'transparent';
                
                if (!isAuthenticated) {
                    window.location.href = '/accounts/login/';
                    return;
                }

                const files = e.dataTransfer.files;
                console.log('Files dropped:', files.length);
                if (files.length > 0 && files[0].type.startsWith('image/')) {
                    currentImageFile = files[0];
                    photoInput.files = files;
                    processImage(files[0]);
                }
            });
            console.log('✓ Drag and drop listener attached');
        }

        // Process Image
        function processImage(file) {
            // Show processing section
            if (uploadSection && processingSection && progressFill && resultSection) {
                uploadSection.classList.add('hidden');
                processingSection.classList.remove('hidden');
                progressFill.style.width = '0%';
                
                // Simulate processing with progress
                let progress = 0;
                const progressInterval = setInterval(() => {
                    progress += Math.random() * 40;
                    if (progress > 100) progress = 100;
                    progressFill.style.width = progress + '%';
                    
                    if (progress >= 100) {
                        clearInterval(progressInterval);
                        
                        // Read and display image
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            const imageData = e.target.result;
                            if (originalImg) originalImg.src = imageData;
                            if (enhancedImg) enhancedImg.src = imageData;
                            
                            // Show results
                            processingSection.classList.add('hidden');
                            resultSection.classList.remove('hidden');
                        };
                        reader.readAsDataURL(file);
                    }
                }, 150);
            }
        }

        // Edit Button - Go Back
        if (editBtn) {
            editBtn.addEventListener('click', () => {
                if (resultSection && uploadSection && photoInput) {
                    resultSection.classList.add('hidden');
                    uploadSection.classList.remove('hidden');
                    photoInput.value = '';
                    currentImageFile = null;
                }
            });
            console.log('✓ Edit button listener attached');
        }

        // Download Button
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                if (enhancedImg && enhancedImg.src) {
                    const link = document.createElement('a');
                    link.href = enhancedImg.src;
                    link.download = `photo-enhanced-${Date.now()}.png`;
                    link.click();
                } else {
                    alert('No image to download');
                }
            });
            console.log('✓ Download button listener attached');
        }

        console.log('✓ Photo Editor Loaded and Ready');
    } catch (error) {
        console.error('Error initializing editor:', error);
    }
}

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEditor);
} else {
    initializeEditor();
}
