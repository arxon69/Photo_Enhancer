// Initialize generic Lucide icons
lucide.createIcons();

// Elements
const themeToggleBtn = document.getElementById('theme-toggle');
const steps = document.querySelectorAll('.step');
const stepContent = document.querySelectorAll('.step-content');
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const uploadError = document.getElementById('upload-error');
const processingText = document.getElementById('processing-text');
const processingImage = document.getElementById('processing-image');

// Customize Elements
const previewBox = document.getElementById('preview-box');
const originalPreview = document.getElementById('original-preview');
const finalPreview = document.getElementById('final-preview');
const sliderHandle = document.getElementById('slider-handle');
const sizeCards = document.querySelectorAll('.size-card');
const colorBtns = document.querySelectorAll('.color-btn:not(.custom-color-trigger)');
const customColorInput = document.getElementById('custom-color');
const customColorTrigger = document.querySelector('.custom-color-trigger');
const btnNext = document.getElementById('btn-next');

// Download Elements
const downloadPreviewWrapper = document.getElementById('download-preview-wrapper');
const downloadPreview = document.getElementById('download-preview');
const btnStartOver = document.getElementById('btn-start-over');
const btnDownloadSingle = document.getElementById('btn-download-single');
const btnDownloadSheet = document.getElementById('btn-download-sheet');

// State
let state = {
    currentStep: 1,
    originalImageStr: null,
    processedImageStr: null, // "Transparent" background version
    selectedSize: 'passport',
    selectedColor: '#ffffff',
    theme: 'light' // light or dark
};

// ---------------------------
// Theme Management
// ---------------------------
function initTheme() {
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    let savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        state.theme = savedTheme;
    } else {
        state.theme = prefersDark ? 'dark' : 'light';
        localStorage.setItem('theme', state.theme);
    }
    applyTheme();
    themeToggleBtn.addEventListener('click', toggleTheme);
}

function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', state.theme);
    applyTheme();
}

function applyTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
    const iconName = state.theme === 'light' ? 'moon' : 'sun';
    themeToggleBtn.innerHTML = `<i data-lucide="${iconName}"></i>`;
    lucide.createIcons();
}

initTheme();

// ---------------------------
// Step Management
// ---------------------------
function goToStep(stepNumber) {
    if(stepNumber < 1 || stepNumber > 4) return;
    
    // Update top indicator
    steps.forEach((step, index) => {
        const num = index + 1;
        step.classList.remove('active', 'completed');
        if (num < stepNumber) {
            step.classList.add('completed');
        } else if (num === stepNumber) {
            step.classList.add('active');
        }
    });

    // Update lines
    const lines = document.querySelectorAll('.step-line');
    lines.forEach((line, index) => {
        if (index + 1 < stepNumber) {
            line.classList.add('completed');
        } else {
            line.classList.remove('completed');
        }
    });

    // Show content
    stepContent.forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`step-${stepNumber}`).classList.add('active');

    state.currentStep = stepNumber;

    // Trigger specific step logic
    if (stepNumber === 2) {
        startProcessing();
    } else if (stepNumber === 3) {
        setupCustomization();
    } else if (stepNumber === 4) {
        setupDownload();
    }
}

// ---------------------------
// Step 1: Upload Logic
// ---------------------------
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
});

dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
});

fileInput.addEventListener('change', function() {
    handleFiles(this.files);
});

function handleFiles(files) {
    uploadError.classList.add('hidden');
    if (files.length === 0) return;
    
    const file = files[0];
    if (!file.type.startsWith('image/')) {
        uploadError.classList.remove('hidden');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        state.originalImageStr = e.target.result;
        // Proceed to processing
        goToStep(2);
    };
    reader.readAsDataURL(file);
}

// ---------------------------
// Step 2: Processing Logic
// ---------------------------
const processingMessages = [
    "Analyzing image structure...",
    "Removing background...",
    "Enhancing facial features...",
    "Cropping to ideal proportions...",
    "Almost ready..."
];

async function startProcessing() {
    // Set initial image in processing
    processingImage.style.backgroundImage = `url(${state.originalImageStr})`;
    
    let msgIndex = 0;
    
    // Cycle messages
    const messageInterval = setInterval(() => {
        msgIndex = (msgIndex + 1) % processingMessages.length;
        processingText.innerText = processingMessages[msgIndex];
        
        // At mid-point, switch to transparent background simulation
        if (msgIndex === 2) {
             // In a real app we would call removeBackground()
             // Here we simulate it simply by using the same photo, but in Step 3 we'll rely on the background div coloring.
             // We can use a CSS trick using drop shadow filter or just leave it. 
             // We'll rely on the original image with a transparent background API in real life.
             state.processedImageStr = state.originalImageStr; // mock API
        }
    }, 1200);

    // Simulate API delay
    await simulateApiCall(4500);
    clearInterval(messageInterval);
    
    goToStep(3);
}

function simulateApiCall(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ---------------------------
// Step 3: Customization Logic
// ---------------------------
function setupCustomization() {
    originalPreview.src = state.originalImageStr;
    finalPreview.src = state.processedImageStr; // In real life, transparent BG image
    
    // Reset size/color logic
    updatePreviewBox();
    setupSlider();
}

function updatePreviewBox() {
    previewBox.style.backgroundColor = state.selectedColor;
    // Update preview box aspect ratio based on size
    if (state.selectedSize === 'passport') {
        previewBox.style.width = '200px';
        previewBox.style.height = '200px';
    } else if (state.selectedSize === 'visa') {
        previewBox.style.width = '175px';
        previewBox.style.height = '225px';
    } else if (state.selectedSize === 'id') {
        previewBox.style.width = '240px';
        previewBox.style.height = '150px';
    }
}

// Setup Slider
let isDragging = false;
function setupSlider() {
    // Reset slider
    sliderHandle.style.left = '50%';
    originalPreview.style.clipPath = `inset(0 0 0 50%)`;

    const startDrag = (e) => {
        isDragging = true;
    };
    const endDrag = () => {
        isDragging = false;
    };
    
    const drag = (e) => {
        if (!isDragging) return;
        
        // Get touch or mouse position
        let clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
        
        const rect = previewBox.getBoundingClientRect();
        let x = clientX - rect.left;
        
        // Clamp
        if (x < 0) x = 0;
        if (x > rect.width) x = rect.width;
        
        const percent = (x / rect.width) * 100;
        sliderHandle.style.left = `${percent}%`;
        
        // Clip path syntax: inset(top right bottom left)
        // We want the original image (which is on top) to be visible on the RIGHT side of the slider
        originalPreview.style.clipPath = `inset(0 0 0 ${percent}%)`;
    };

    sliderHandle.addEventListener('mousedown', startDrag);
    sliderHandle.addEventListener('touchstart', startDrag, {passive: true});
    
    window.addEventListener('mouseup', endDrag);
    window.addEventListener('touchend', endDrag);
    
    window.addEventListener('mousemove', drag);
    window.addEventListener('touchmove', drag, {passive: true});
}

// Bind size cards
sizeCards.forEach(card => {
    card.addEventListener('click', () => {
        sizeCards.forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        state.selectedSize = card.dataset.size;
        updatePreviewBox();
    });
});

// Bind color buttons
colorBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        colorBtns.forEach(c => c.classList.remove('active'));
        customColorTrigger.classList.remove('active');
        btn.classList.add('active');
        state.selectedColor = btn.dataset.color;
        updatePreviewBox();
    });
});

// Bind custom color
customColorInput.addEventListener('input', (e) => {
    const color = e.target.value;
    colorBtns.forEach(c => c.classList.remove('active'));
    customColorTrigger.classList.add('active');
    customColorTrigger.style.borderColor = color;
    state.selectedColor = color;
    updatePreviewBox();
});

btnNext.addEventListener('click', () => {
    goToStep(4);
});

// App Crop Logic
const cropModal = document.getElementById('crop-modal');
const closeModalBtn = document.getElementById('close-modal');
const btnCancelCrop = document.getElementById('btn-cancel-crop');
const btnSaveCrop = document.getElementById('btn-save-crop');
const imageToCrop = document.getElementById('image-to-crop');
const btnOpenCrop = document.getElementById('btn-open-crop');

let mainCropper = null;

if (btnOpenCrop) {
    btnOpenCrop.addEventListener('click', () => {
        if (!state.originalImageStr) return;
        imageToCrop.src = state.originalImageStr; // use original photo to crop
        cropModal.classList.remove('hidden');
        
        setTimeout(() => {
            if (mainCropper) {
                mainCropper.destroy();
            }
            
            let ratio = NaN;
            if (state.selectedSize === 'passport') {
                ratio = 1;
            } else if (state.selectedSize === 'visa') {
                ratio = 35 / 45;
            } else if (state.selectedSize === 'id') {
                ratio = 240 / 150;
            }

            mainCropper = new Cropper(imageToCrop, {
                aspectRatio: ratio,
                viewMode: 1,
                dragMode: 'move',
                autoCropArea: 0.9,
                restore: false,
                guides: true,
                center: true,
                highlight: false,
                cropBoxMovable: true,
                cropBoxResizable: true,
                toggleDragModeOnDblclick: false,
            });
        }, 100);
    });
}

function closeMainCropModal() {
    cropModal.classList.add('hidden');
    if (mainCropper) {
        mainCropper.destroy();
        mainCropper = null;
    }
}

if (closeModalBtn) closeModalBtn.addEventListener('click', closeMainCropModal);
if (btnCancelCrop) btnCancelCrop.addEventListener('click', closeMainCropModal);

if (btnSaveCrop) {
    btnSaveCrop.addEventListener('click', () => {
        if (!mainCropper) return;
        const canvas = mainCropper.getCroppedCanvas({
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'high',
        });
        const newImageStr = canvas.toDataURL('image/png');
        state.processedImageStr = newImageStr;
        state.originalImageStr = newImageStr; 
        
        // update UI previews
        const finalPreview = document.getElementById('final-preview');
        const originalPreview = document.getElementById('original-preview');
        if (finalPreview) finalPreview.src = state.processedImageStr;
        if (originalPreview) originalPreview.src = state.originalImageStr;
        
        closeMainCropModal();
    });
}

// ---------------------------
// Step 4: Download Logic
// ---------------------------
function setupDownload() {
    downloadPreview.src = state.processedImageStr;
    downloadPreviewWrapper.style.backgroundColor = state.selectedColor;
    
    // Copy the aspect ratio from step 3
    downloadPreviewWrapper.style.width = previewBox.style.width;
    downloadPreviewWrapper.style.height = previewBox.style.height;
}

btnStartOver.addEventListener('click', () => {
    // Reset state
    state.originalImageStr = null;
    state.processedImageStr = null;
    fileInput.value = '';
    goToStep(1);
});

btnDownloadSingle.addEventListener('click', () => {
    triggerDownload("passport-photo.jpg");
});

btnDownloadSheet.addEventListener('click', () => {
    triggerDownload("passport-print-sheet.pdf");
});

function triggerDownload(filename) {
    // Mock download action
    btnDownloadSingle.disabled = true;
    btnDownloadSheet.disabled = true;
    
    const originalText = btnDownloadSingle.innerHTML;
    
    // Show loading
    const activeBtn = event.currentTarget;
    const btnText = activeBtn.querySelector('strong');
    const oldText = btnText.innerText;
    btnText.innerText = "Generating...";
    
    setTimeout(() => {
        alert(`Mock Download complete: ${filename}\n(In a real app, this would download the composited canvas image)`);
        
        btnText.innerText = oldText;
        btnDownloadSingle.disabled = false;
        btnDownloadSheet.disabled = false;
    }, 1500);
}
