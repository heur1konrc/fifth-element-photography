// Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeModals();
    updateSelectionCount();
});

// Alert function for user feedback
function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        max-width: 400px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    
    // Set background color based on type
    switch(type) {
        case 'success':
            alert.style.backgroundColor = '#28a745';
            break;
        case 'error':
            alert.style.backgroundColor = '#dc3545';
            break;
        case 'warning':
            alert.style.backgroundColor = '#ffc107';
            alert.style.color = '#212529';
            break;
        default:
            alert.style.backgroundColor = '#17a2b8';
    }
    
    alert.textContent = message;
    document.body.appendChild(alert);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 3000);
}

// Selection Management
function selectAll() {
    const checkboxes = document.querySelectorAll('.image-select');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
    updateSelectionCount();
}

function selectNone() {
    const checkboxes = document.querySelectorAll('.image-select');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    updateSelectionCount();
}

function updateSelectionCount() {
    const checkboxes = document.querySelectorAll('.image-select');
    const selectedCount = document.querySelectorAll('.image-select:checked').length;
    document.getElementById('selectedCount').textContent = selectedCount;
    
    // Update category buttons state
    const categoryButtons = document.querySelectorAll('.category-btn');
    categoryButtons.forEach(btn => {
        btn.classList.toggle('active', false);
    });
}

function getSelectedImages() {
    const selectedCheckboxes = document.querySelectorAll('.image-select:checked');
    return Array.from(selectedCheckboxes).map(checkbox => checkbox.dataset.filename);
}

// Category Assignment
function assignCategoryToSelected(category) {
    const categoryButtons = document.querySelectorAll('.category-btn');
    categoryButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === category);
    });
}

function updateSelectedCategories() {
    const selectedImages = getSelectedImages();
    const activeCategory = document.querySelector('.category-btn.active');
    
    if (selectedImages.length === 0) {
        alert('Please select at least one image.');
        return;
    }
    
    if (!activeCategory) {
        alert('Please select a category.');
        return;
    }
    
    const category = activeCategory.dataset.category;
    
    // Show loading state
    const updateBtn = event.target;
    const originalText = updateBtn.innerHTML;
    updateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
    updateBtn.disabled = true;
    
    // Update categories for selected images
    Promise.all(selectedImages.map(filename => 
        fetch(`/assign_category/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `category=${encodeURIComponent(category)}`
        })
    )).then(responses => {
        if (responses.every(response => response.ok)) {
            location.reload(); // Refresh to show updated categories
        } else {
            alert('Error updating some images. Please try again.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Error updating categories. Please try again.');
    }).finally(() => {
        updateBtn.innerHTML = originalText;
        updateBtn.disabled = false;
    });
}

// Bulk Actions
function deleteSelected() {
    const selectedImages = getSelectedImages();
    
    if (selectedImages.length === 0) {
        alert('Please select at least one image to delete.');
        return;
    }
    
    if (!confirm(`Are you sure you want to delete ${selectedImages.length} selected image(s)? This action cannot be undone.`)) {
        return;
    }
    
    // Delete selected images
    Promise.all(selectedImages.map(filename => 
        fetch(`/delete_image/${filename}`, {
            method: 'POST'
        })
    )).then(responses => {
        if (responses.every(response => response.ok)) {
            location.reload(); // Refresh to show updated list
        } else {
            alert('Error deleting some images. Please try again.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Error deleting images. Please try again.');
    });
}

function backupSystem() {
    const backupBtn = event.target;
    const originalText = backupBtn.innerHTML;
    backupBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Backup...';
    backupBtn.disabled = true;
    
    // Create backup using new /backup route
    window.location.href = '/backup';
    
    // Reset button after a short delay
    setTimeout(() => {
        backupBtn.innerHTML = originalText;
        backupBtn.disabled = false;
    }, 2000);
}

// Individual Image Actions
// Global Quill instance
let quillEditor = null;

function editImage(filename) {
    // Load edit form in modal
    fetch(`/edit_image/${filename}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('editModalContent').innerHTML = html;
            openEditModal();
            // Initialize Quill editor after modal content is loaded
            initializeQuillEditor();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading edit form. Please try again.');
        });
}

function initializeQuillEditor() {
    const editorContainer = document.getElementById('quill-editor');
    const hiddenTextarea = document.getElementById('description');
    
    if (!editorContainer || !hiddenTextarea) return;
    
    // Initialize Quill
    quillEditor = new Quill('#quill-editor', {
        theme: 'snow',
        modules: {
            toolbar: [
                ['bold', 'italic', 'underline'],
                [{ 'header': [1, 2, 3, false] }],
                [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                ['link'],
                ['clean']
            ]
        },
        placeholder: 'Enter image description...'
    });
    
    // Load existing content
    const existingContent = hiddenTextarea.value;
    if (existingContent) {
        quillEditor.root.innerHTML = existingContent;
    }
    
    // Sync Quill content to hidden textarea on change
    quillEditor.on('text-change', function() {
        hiddenTextarea.value = quillEditor.root.innerHTML;
    });
}

function addToSlideshow(filename) {
    if (!confirm(`Add ${filename} to slideshow?`)) {
        return;
    }
    
    fetch(`/add_to_slideshow/${filename}`, {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            alert('Image added to slideshow successfully!');
        } else {
            alert('Error adding image to slideshow.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Error adding image to slideshow.');
    });
}

function setAsAbout(filename) {
    if (!confirm(`Set ${filename} as about page background?`)) {
        return;
    }
    
    fetch(`/toggle_background/${filename}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'is_background=on'
    }).then(response => {
        if (response.ok) {
            location.reload();
        } else {
            alert('Error setting background image.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Error setting background image.');
    });
}

function deleteImage(filename) {
    if (!confirm(`Are you sure you want to delete ${filename}? This action cannot be undone.`)) {
        return;
    }
    
    fetch(`/delete_image/${filename}`, {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            location.reload();
        } else {
            alert('Error deleting image.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Error deleting image.');
    });
}

function removeFeatured(filename) {
    if (!confirm('Remove featured status from this image?')) {
        return;
    }
    
    fetch(`/set_featured/${filename}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'is_featured='
    }).then(response => {
        if (response.ok) {
            location.reload();
        } else {
            alert('Error removing featured status.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Error removing featured status.');
    });
}

function removeBackground(filename) {
    if (!confirm('Remove background status from this image?')) {
        return;
    }
    
    fetch(`/toggle_background/${filename}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'is_background='
    }).then(response => {
        if (response.ok) {
            location.reload();
        } else {
            alert('Error removing background status.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Error removing background status.');
    });
}

// Modal Management
function openUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
}

function openCategoryModal() {
    document.getElementById('categoryModal').style.display = 'block';
}

function closeCategoryModal() {
    document.getElementById('categoryModal').style.display = 'none';
}

function openEditModal() {
    document.getElementById('editModal').style.display = 'block';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

function initializeModals() {
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            // Don't close if clicking inside modal content or drop zone
            if (event.target === modal && !event.target.closest('.file-drop-zone')) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Close modals with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
        }
    });
}

// Global variable to store selected files
let selectedFiles = null;

// File Upload Enhancement
function initializeFileUpload() {
    const dropZone = document.getElementById('fileDropZone');
    const fileInput = document.getElementById('fileInput');
    
    console.log('Initializing file upload, dropZone:', dropZone, 'fileInput:', fileInput);
    
    if (!dropZone || !fileInput) {
        console.log('Drop zone or file input not found');
        return;
    }
    
    // Click to browse
    dropZone.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent modal from closing
        console.log('Drop zone clicked, triggering file input');
        fileInput.click();
    });
    
    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        console.log('Files dropped:', files.length);
        if (files.length > 0) {
            selectedFiles = files; // Store files globally
            fileInput.files = files;
            updateFileInputDisplay(files);
        }
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        console.log('File input changed, files:', e.target.files.length);
        selectedFiles = e.target.files; // Store files globally
        updateFileInputDisplay(e.target.files);
    });
}

function updateFileInputDisplay(files) {
    const dropZone = document.getElementById('fileDropZone');
    const content = dropZone.querySelector('.drop-zone-content');
    
    if (files.length > 0) {
        content.innerHTML = `
            <i class="fas fa-check-circle" style="color: #22c55e;"></i>
            <h4>${files.length} file(s) selected</h4>
            <p>Click upload to proceed</p>
        `;
    }
}

// Utility Functions
function showLoading(element, text = 'Loading...') {
    const originalContent = element.innerHTML;
    element.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${text}`;
    element.disabled = true;
    return originalContent;
}

function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
    element.disabled = false;
}

// Auto-refresh functionality (optional)
function enableAutoRefresh(interval = 30000) {
    setInterval(() => {
        // Only refresh if no modals are open
        const openModals = document.querySelectorAll('.modal[style*="block"]');
        if (openModals.length === 0) {
            location.reload();
        }
    }, interval);
}

// Initialize auto-refresh (uncomment if needed)
// enableAutoRefresh();

// Upload Images Function
function uploadImages() {
    console.log('Upload function called, selectedFiles:', selectedFiles);
    
    // Try to get files from global variable first, then from file input
    let files = selectedFiles;
    
    if (!files || files.length === 0) {
        const fileInput = document.getElementById('fileInput');
        console.log('No global files, trying fileInput:', fileInput);
        
        if (fileInput && fileInput.files) {
            files = fileInput.files;
        }
    }
    
    console.log('Final files to upload:', files ? files.length : 0);
    
    if (!files || files.length === 0) {
        alert('Please select files to upload.');
        return;
    }
    
    const uploadBtn = document.querySelector('#uploadModal .btn-primary');
    if (!uploadBtn) {
        console.error('Upload button not found!');
        alert('Error: Upload button not found.');
        return;
    }
    
    const originalText = uploadBtn.innerHTML;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    uploadBtn.disabled = true;
    
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
        console.log('Added file:', files[i].name);
    }
    
    console.log('Sending upload request...');
    
    fetch('/upload_images', {
        method: 'POST',
        body: formData
    }).then(response => {
        console.log('Upload response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Upload response data:', data);
        if (data.success) {
            alert(data.message);
            selectedFiles = null; // Clear global files
            closeUploadModal();
            console.log('Reloading page...');
            location.reload(); // Refresh to show new images
        } else {
            alert('Upload failed: ' + data.message);
        }
    }).catch(error => {
        console.error('Upload error:', error);
        alert('Upload failed. Please try again. Error: ' + error.message);
    }).finally(() => {
        uploadBtn.innerHTML = originalText;
        uploadBtn.disabled = false;
    });
}

// Save Image Changes Function
function saveImageChanges(event, filename) {
    event.preventDefault(); // Prevent default form submission
    
    const form = document.querySelector('.edit-form form');
    if (!form) {
        alert('Form not found');
        return;
    }
    
    // Quill editor automatically handles HTML formatting, no conversion needed
    
    const formData = new FormData(form);
    
    const saveBtn = document.querySelector('#editModal .btn-primary');
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    saveBtn.disabled = true;
    
    fetch(`/update_image/${filename}`, {
        method: 'POST',
        body: formData
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            closeEditModal();
            location.reload(); // Refresh to show changes
        } else {
            alert('Save failed: ' + data.message);
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Save failed. Please try again.');
    }).finally(() => {
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
    });
}


// Featured Image Story Functions
function saveFeaturedStory(filename) {
    const story = document.getElementById('featured-story').value;
    
    fetch(`/save_featured_story/${filename}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ story: story })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Featured image story saved successfully!', 'success');
        } else {
            showAlert('Error saving story: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error saving featured story', 'error');
    });
}

// About Image Functions
function openAboutUploadModal() {
    const modal = document.getElementById('aboutUploadModal');
    if (modal) {
        modal.style.display = 'block';
        initializeAboutUpload();
    }
}

function closeAboutUploadModal() {
    const modal = document.getElementById('aboutUploadModal');
    if (modal) {
        modal.style.display = 'none';
    }
    resetAboutUpload();
}

function initializeAboutUpload() {
    const dropZone = document.getElementById('aboutFileDropZone');
    const fileInput = document.getElementById('aboutFileInput');
    const aboutForm = document.getElementById('aboutForm');
    
    // Click to browse
    dropZone.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            selectedAboutFile = file; // Store the file globally
            dropZone.innerHTML = `
                <div class="drop-zone-content">
                    <i class="fas fa-check-circle" style="color: #4CAF50;"></i>
                    <h4>File Selected</h4>
                    <p>${file.name}</p>
                    <p class="file-info">Ready to upload</p>
                </div>
            `;
            aboutForm.style.display = 'block';
        }
    });
    
    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#2196F3';
        dropZone.style.backgroundColor = 'rgba(33, 150, 243, 0.1)';
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'rgba(255, 255, 255, 0.2)';
        dropZone.style.backgroundColor = 'transparent';
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'rgba(255, 255, 255, 0.2)';
        dropZone.style.backgroundColor = 'transparent';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });
}

function resetAboutUpload() {
    const dropZone = document.getElementById('aboutFileDropZone');
    const fileInput = document.getElementById('aboutFileInput');
    const aboutForm = document.getElementById('aboutForm');
    const bioText = document.getElementById('aboutBioText');
    
    // Only reset elements that exist
    if (fileInput) fileInput.value = '';
    if (bioText) bioText.value = '';
    if (aboutForm) aboutForm.style.display = 'none';
    
    if (dropZone) {
        dropZone.innerHTML = `
            <div class="drop-zone-content">
                <i class="fas fa-user"></i>
                <h4>Upload About Page Image</h4>
                <p>Drag & drop your about page image here or click to browse</p>
                <p class="file-info">Supports: JPG, PNG, GIF</p>
            </div>
        `;
    }
}

// Global variable to store selected About file
let selectedAboutFile = null;

function uploadAboutImage() {
    console.log('uploadAboutImage function called');
    
    const bioText = document.getElementById('aboutBioText').value;
    
    console.log('Selected about file:', selectedAboutFile);
    console.log('Bio text:', bioText);
    
    if (!selectedAboutFile) {
        showAlert('Please select an image file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedAboutFile);
    formData.append('bio', bioText);
    
    // Update button state
    const uploadBtn = document.getElementById('uploadAboutBtn');
    const originalText = uploadBtn.innerHTML;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    uploadBtn.disabled = true;
    
    fetch('/upload_about_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('About image uploaded successfully!', 'success');
            closeAboutUploadModal();
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showAlert('Error uploading image: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error uploading about image', 'error');
    })
    .finally(() => {
        uploadBtn.innerHTML = originalText;
        uploadBtn.disabled = false;
    });
}

function saveAboutBio(filename) {
    const bio = document.getElementById('about-bio').value;
    
    fetch(`/save_about_bio/${filename}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ bio: bio })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('About bio saved successfully!', 'success');
        } else {
            showAlert('Error saving bio: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error saving about bio', 'error');
    });
}

function removeAboutImage(filename) {
    if (!confirm('Are you sure you want to remove this about image?')) {
        return;
    }
    
    fetch(`/remove_about_image/${filename}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('About image removed successfully!', 'success');
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showAlert('Error removing image: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error removing about image', 'error');
    });
}

// Close modals when clicking outside
window.addEventListener('click', function(e) {
    const aboutModal = document.getElementById('aboutUploadModal');
    if (e.target === aboutModal) {
        closeAboutUploadModal();
    }
});



// Set as Featured functionality
function setAsFeatured(filename) {
    if (confirm(`Set ${filename} as the featured image?`)) {
        fetch(`/toggle_featured/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message, 'success');
                
                // Update button colors immediately
                document.querySelectorAll('.btn-featured').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Find and activate the button for this image
                const buttons = document.querySelectorAll('.btn-featured');
                buttons.forEach(btn => {
                    if (btn.onclick.toString().includes(filename)) {
                        btn.classList.add('active');
                    }
                });
                
                // Refresh the page to show the updated featured image
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showAlert(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error setting featured image:', error);
            showAlert('Error setting featured image', 'error');
        });
    }
}



// Text Formatting Functions
function initializeTextFormatting() {
    // Initialize formatting for featured story textarea
    const featuredStoryTextarea = document.getElementById('featured-story');
    if (featuredStoryTextarea) {
        addFormattingToolbar(featuredStoryTextarea, 'featured-story-toolbar');
    }
    
    // Initialize formatting for about bio textarea
    const aboutBioTextarea = document.getElementById('about-bio');
    if (aboutBioTextarea) {
        addFormattingToolbar(aboutBioTextarea, 'about-bio-toolbar');
    }
}

function addFormattingToolbar(textarea, toolbarId) {
    // Create toolbar container
    const toolbar = document.createElement('div');
    toolbar.id = toolbarId;
    toolbar.className = 'formatting-toolbar';
    toolbar.innerHTML = `
        <div class="toolbar-buttons">
            <button type="button" class="format-btn" onclick="formatText('${textarea.id}', 'bold')" title="Bold">
                <i class="fas fa-bold"></i>
            </button>
            <button type="button" class="format-btn" onclick="formatText('${textarea.id}', 'italic')" title="Italic">
                <i class="fas fa-italic"></i>
            </button>
            <button type="button" class="format-btn" onclick="formatText('${textarea.id}', 'h1')" title="Heading 1">
                H1
            </button>
            <button type="button" class="format-btn" onclick="formatText('${textarea.id}', 'h2')" title="Heading 2">
                H2
            </button>
            <button type="button" class="format-btn" onclick="formatText('${textarea.id}', 'h3')" title="Heading 3">
                H3
            </button>
        </div>
    `;
    
    // Insert toolbar before textarea
    textarea.parentNode.insertBefore(toolbar, textarea);
}

function formatText(textareaId, format) {
    const textarea = document.getElementById(textareaId);
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    let formattedText = '';
    
    switch (format) {
        case 'bold':
            formattedText = `<strong>${selectedText}</strong>`;
            break;
        case 'italic':
            formattedText = `<em>${selectedText}</em>`;
            break;
        case 'h1':
            formattedText = `<h1>${selectedText}</h1>`;
            break;
        case 'h2':
            formattedText = `<h2>${selectedText}</h2>`;
            break;
        case 'h3':
            formattedText = `<h3>${selectedText}</h3>`;
            break;
        default:
            formattedText = selectedText;
    }
    
    // Replace selected text with formatted text
    textarea.value = textarea.value.substring(0, start) + formattedText + textarea.value.substring(end);
    
    // Set cursor position after formatted text
    const newCursorPos = start + formattedText.length;
    textarea.focus();
    textarea.setSelectionRange(newCursorPos, newCursorPos);
}

// Simple Hero Image Management
async function setAsHero(filename, title) {
    try {
        const response = await fetch('/set_hero_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: filename,
                title: title
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
        } else {
            showAlert(result.error, 'error');
        }
    } catch (error) {
        console.error('Error setting hero image:', error);
        showAlert('Error setting hero image', 'error');
    }
}

// Add event listeners for hero buttons
function initializeHeroButtons() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-action="set-hero"]')) {
            e.preventDefault();
            e.stopPropagation();
            const button = e.target.closest('[data-action="set-hero"]');
            const filename = button.getAttribute('data-filename');
            const title = button.getAttribute('data-title');
            setAsHero(filename, title);
        }
    });
}

// Update the DOMContentLoaded event listener to include text formatting initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeModals();
    updateSelectionCount();
    initializeTextFormatting(); // Add this line
    initializeHeroButtons(); // Add hero button event listeners
});



// About image upload functionality
document.addEventListener('DOMContentLoaded', function() {
    const aboutFileInput = document.getElementById('aboutFileInput');
    const aboutSubmitBtn = document.getElementById('aboutSubmitBtn');
    const aboutBioTextarea = document.getElementById('about-bio');
    const hiddenBioInput = document.getElementById('hiddenBio');
    
    if (aboutFileInput) {
        aboutFileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                // Update hidden bio field with current bio text
                if (aboutBioTextarea && hiddenBioInput) {
                    hiddenBioInput.value = aboutBioTextarea.value;
                }
                
                // Show submit button and auto-submit
                if (aboutSubmitBtn) {
                    aboutSubmitBtn.style.display = 'inline-block';
                    aboutSubmitBtn.click();
                }
            }
        });
    }
});



// Randomize Portfolio Order
function randomizePortfolio() {
    if (!confirm('This will randomly shuffle the order of all portfolio images. Continue?')) {
        return;
    }
    
    const button = document.querySelector('button[onclick="randomizePortfolio()"]');
    const originalText = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Randomizing...';
    button.disabled = true;
    
    fetch('/admin/randomize_portfolio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Portfolio order randomized successfully!', 'success');
            // Reload the page to show the new order
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showAlert('Error randomizing portfolio: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error randomizing portfolio. Please try again.', 'error');
    })
    .finally(() => {
        // Restore button state
        button.innerHTML = originalText;
        button.disabled = false;
    });
}




// Category Management Functions
async function addCategory(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/admin/categories', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            form.reset();
            await refreshCategoryModal();
            refreshCategoryButtons(data.categories);
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        showAlert('Error adding category: ' + error.message, 'error');
    }
}

async function deleteCategory(event, categoryName) {
    event.preventDefault();
    
    if (!confirm(`Are you sure? Images in "${categoryName}" will be moved to Other category.`)) {
        return;
    }
    
    const formData = new FormData();
    formData.append('action', 'delete');
    formData.append('category_to_delete', categoryName);
    
    try {
        const response = await fetch('/admin/categories', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            await refreshCategoryModal();
            refreshCategoryButtons(data.categories);
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        showAlert('Error deleting category: ' + error.message, 'error');
    }
}

async function refreshCategoryModal() {
    try {
        const response = await fetch('/admin/categories');
        const data = await response.json();
        
        // Rebuild category list in modal
        const categoryList = document.querySelector('.category-list');
        if (categoryList && data.categories) {
            categoryList.innerHTML = data.categories.map(category => `
                <div class="category-item">
                    <span class="category-name">${category.charAt(0).toUpperCase() + category.slice(1)}</span>
                    <span class="category-count">- images</span>
                    ${category !== 'other' ? `
                        <button type="button" class="btn btn-small btn-danger" onclick="deleteCategory(event, '${category}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error refreshing category modal:', error);
    }
}

function refreshCategoryButtons(categories) {
    const categoryButtonsContainer = document.querySelector('.category-buttons');
    if (categoryButtonsContainer && categories) {
        categoryButtonsContainer.innerHTML = categories.sort().map(category => `
            <button class="category-btn" data-category="${category}" onclick="assignCategoryToSelected('${category}')">
                ${category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
        `).join('');
    }
}




// Helper functions for modal actions
function setAsFeaturedFromModal(filename, title) {
    if (confirm(`Set "${title}" as the featured image?`)) {
        fetch(`/toggle_featured/${filename}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Featured image updated successfully!', 'success');
                closeEditModal();
                setTimeout(() => location.reload(), 500);
            } else {
                showAlert('Failed to set featured image: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            showAlert('Error: ' + error.message, 'error');
        });
    }
}

function setAsHeroFromModal(filename, title) {
    // Call existing setAsHero function or implement inline
    if (confirm(`Set "${title}" as the hero image?`)) {
        fetch('/set_hero_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: filename, title: title })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Hero image updated successfully!', 'success');
            } else {
                showAlert('Failed to set hero image: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            showAlert('Error: ' + error.message, 'error');
        });
    }
}

function analyzeImageFromModal(filename, title) {
    // Call existing analyzeImage function
    analyzeImage(filename, title);
}




// Removed: Text formatting functions (replaced by Quill WYSIWYG editor)


// ==================== LUMAPRINTS BULK MAPPING ====================

const LumaprintsState = {
    unmappedProducts: [],
    availableImages: [],
    selectedImage: null,
    mappings: []
};

/**
 * Open Lumaprints mapping modal
 */
function openLumaprintsModal() {
    document.getElementById('lumaprints-modal').style.display = 'block';
    // Reset to step 1
    document.getElementById('lumaprints-step-1').style.display = 'block';
    document.getElementById('lumaprints-step-2').style.display = 'none';
    document.getElementById('lumaprints-step-3').style.display = 'none';
}

/**
 * Close Lumaprints mapping modal
 */
function closeLumaprintsModal() {
    document.getElementById('lumaprints-modal').style.display = 'none';
}

/**
 * Upload and process Lumaprints Excel file
 */
async function uploadLumaprintsFile() {
    const fileInput = document.getElementById('lumaprints-file-input');
    const statusDiv = document.getElementById('lumaprints-upload-status');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showAlert('Please select a file', 'warning');
        return;
    }
    
    const file = fileInput.files[0];
    
    if (!file.name.endsWith('.xlsx')) {
        showAlert('File must be .xlsx format', 'error');
        return;
    }
    
    statusDiv.innerHTML = '<p>Uploading and processing...</p>';
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/lumaprints/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            LumaprintsState.unmappedProducts = data.unmapped_products;
            statusDiv.innerHTML = `<p style="color: green;">✓ File processed! Found ${data.unmapped_count} unmapped products.</p>`;
            
            // Load available images
            await loadLumaprintsImages();
            
            // Move to step 2
            setTimeout(() => {
                document.getElementById('lumaprints-step-1').style.display = 'none';
                document.getElementById('lumaprints-step-2').style.display = 'block';
                displayUnmappedProducts();
            }, 1000);
        } else {
            statusDiv.innerHTML = `<p style="color: red;">✗ Error: ${data.error}</p>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<p style="color: red;">✗ Error: ${error.message}</p>`;
    }
}

/**
 * Load available images with aspect ratios
 */
async function loadLumaprintsImages() {
    try {
        const response = await fetch('/api/lumaprints/images');
        const data = await response.json();
        
        LumaprintsState.availableImages = data.images;
    } catch (error) {
        console.error('Error loading images:', error);
    }
}

/**
 * Display unmapped products
 */
function displayUnmappedProducts() {
    const countElem = document.getElementById('lumaprints-unmapped-count');
    const listElem = document.getElementById('lumaprints-products-list');
    
    countElem.textContent = `Found ${LumaprintsState.unmappedProducts.length} unmapped products.`;
    
    if (LumaprintsState.unmappedProducts.length === 0) {
        listElem.innerHTML = '<p>No unmapped products found!</p>';
        return;
    }
    
    // Initialize mapping rows with first row
    initializeMappingRows();
    
    // Show first 10 products as preview
    const preview = LumaprintsState.unmappedProducts.slice(0, 10);
    listElem.innerHTML = `
        <h4>Preview (first 10 products):</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f0f0f0;">
                    <th style="padding: 8px; border: 1px solid #ddd;">Title</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Size</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Product Type</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Existing Filename</th>
                </tr>
            </thead>
            <tbody>
                ${preview.map(p => `
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">${p.product_name || 'N/A'}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">${p.size || 'N/A'}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">${p.option1 || 'N/A'}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">${p.existing_filename || 'None'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        ${LumaprintsState.unmappedProducts.length > 10 ? `<p style="margin-top: 10px; font-style: italic;">... and ${LumaprintsState.unmappedProducts.length - 10} more products</p>` : ''}
    `;
}

/**
 * Get unique product titles from unmapped products
 */
function getUniqueProductTitles() {
    const titles = new Set();
    LumaprintsState.unmappedProducts.forEach(p => {
        if (p.product_name) {
            titles.add(p.product_name);
        }
    });
    return Array.from(titles).sort();
}

/**
 * Initialize mapping rows with first empty row
 */
function initializeMappingRows() {
    const container = document.getElementById('lumaprints-mapping-rows');
    container.innerHTML = '';
    addMappingRow();
}

/**
 * Add a new mapping row
 */
function addMappingRow() {
    const container = document.getElementById('lumaprints-mapping-rows');
    const rowIndex = container.children.length;
    const titles = getUniqueProductTitles();
    
    const rowDiv = document.createElement('div');
    rowDiv.className = 'mapping-row';
    rowDiv.style.cssText = 'margin-bottom: 15px; padding: 15px; border: 1px solid #ddd; border-radius: 4px; background: white;';
    rowDiv.dataset.rowIndex = rowIndex;
    
    rowDiv.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <strong>Mapping #${rowIndex + 1}</strong>
            ${rowIndex > 0 ? `<button class="btn btn-small btn-danger" onclick="removeMappingRow(${rowIndex})">Remove</button>` : ''}
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
            <div>
                <label>Product Title:</label>
                <select class="mapping-title-select" style="width: 100%; padding: 8px; margin-top: 5px;">
                    <option value="">-- Select Title --</option>
                    ${titles.map(t => `<option value="${t}">${t}</option>`).join('')}
                </select>
            </div>
            <div>
                <label>Image Filename:</label>
                <input type="text" class="mapping-filename-input" placeholder="e.g., image.jpg" style="width: 100%; padding: 8px; margin-top: 5px;">
            </div>
            <div>
                <label>Aspect Ratio:</label>
                <select class="mapping-aspect-select" style="width: 100%; padding: 8px; margin-top: 5px;">
                    <option value="3:2">3:2 (Landscape)</option>
                    <option value="2:3">2:3 (Portrait)</option>
                    <option value="1:1">1:1 (Square)</option>
                </select>
            </div>
        </div>
    `;
    
    container.appendChild(rowDiv);
}

/**
 * Remove a mapping row
 */
function removeMappingRow(rowIndex) {
    const container = document.getElementById('lumaprints-mapping-rows');
    const row = container.querySelector(`[data-row-index="${rowIndex}"]`);
    if (row) {
        row.remove();
        // Renumber remaining rows
        renumberMappingRows();
    }
}

/**
 * Renumber mapping rows after removal
 */
function renumberMappingRows() {
    const container = document.getElementById('lumaprints-mapping-rows');
    const rows = container.querySelectorAll('.mapping-row');
    rows.forEach((row, index) => {
        row.dataset.rowIndex = index;
        row.querySelector('strong').textContent = `Mapping #${index + 1}`;
        
        // Update data attributes
        row.querySelectorAll('[data-row-index]').forEach(elem => {
            elem.dataset.rowIndex = index;
        });
    });
}

/**
 * Apply mapping to all unmapped products
 * Applies ALL product types (Canvas + all Art Paper types) at once
 */
async function applyLumaprintsMapping() {
    // Collect all mapping rows
    const container = document.getElementById('lumaprints-mapping-rows');
    const rows = container.querySelectorAll('.mapping-row');
    
    // Validate and collect mappings
    const userMappings = [];
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const titleSelect = row.querySelector('.mapping-title-select');
        const filenameInput = row.querySelector('.mapping-filename-input');
        const aspectSelect = row.querySelector('.mapping-aspect-select');
        
        const title = titleSelect.value;
        const filename = filenameInput.value.trim();
        const aspectRatio = aspectSelect.value;
        
        if (!title) {
            showAlert(`Mapping #${i + 1}: Please select a product title`, 'warning');
            return;
        }
        
        if (!filename) {
            showAlert(`Mapping #${i + 1}: Please enter an image filename`, 'warning');
            return;
        }
        
        userMappings.push({
            title: title,
            filename: filename,
            aspectRatio: aspectRatio
        });
    }
    
    if (userMappings.length === 0) {
        showAlert('Please add at least one mapping', 'warning');
        return;
    }
    
    // Build mappings for products
    const mappings = [];
    
    for (const product of LumaprintsState.unmappedProducts) {
        // Find matching user mapping by title
        const userMapping = userMappings.find(m => m.title === product.product_name);
        
        if (!userMapping) {
            // Skip products that don't have a mapping
            continue;
        }
        
        const filename = userMapping.filename;
        const width = product.width || 12;
        const length = product.length || 18;
        const productType = product.option1 || '';
        
        // Determine product type
        let subcategory = '';
        let options = [];
        
        if (productType.includes('Canvas')) {
            subcategory = '0.75in Stretched Canvas';
            options = [
                ['Canvas Border', 'Mirror Wrap'],
                ['Canvas Hanging Hardware', 'Sawtooth Hanger installed'],
                ['Canvas Finish', 'Semi-Glossy']
            ];
        } else if (productType.includes('Hot Press')) {
            subcategory = 'Hot Press Fine Art Paper';
            options = [['Bleed Size', '0.25in Bleed (0.25in on each side)']];
        } else if (productType.includes('Semi-Glossy')) {
            subcategory = 'Semi-Glossy Fine Art Paper';
            options = [['Bleed Size', '0.25in Bleed (0.25in on each side)']];
        } else if (productType.includes('Glossy')) {
            subcategory = 'Glossy Fine Art Paper';
            options = [['Bleed Size', '0.25in Bleed (0.25in on each side)']];
        } else {
            // Default to canvas
            subcategory = '0.75in Stretched Canvas';
            options = [
                ['Canvas Border', 'Mirror Wrap'],
                ['Canvas Hanging Hardware', 'Sawtooth Hanger installed'],
                ['Canvas Finish', 'Semi-Glossy']
            ];
        }
        
        mappings.push({
            row: product.row,
            data: {
                product_handling: 'Update',
                image_filename: filename,
                subcategory: subcategory,
                width: width,
                length: length,
                options: options
            }
        });
    }
    
    // Send mappings to backend
    try {
        const response = await fetch('/api/lumaprints/apply-mapping', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mappings: mappings })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(`✓ Successfully mapped ${data.mapped_count} products!`, 'success');
            
            // Move to step 3
            document.getElementById('lumaprints-step-2').style.display = 'none';
            document.getElementById('lumaprints-step-3').style.display = 'block';
            document.getElementById('lumaprints-mapped-count').textContent = data.mapped_count;
        } else {
            showAlert('Error applying mapping: ' + data.error, 'error');
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
    }
}

/**
 * Download mapped Excel file
 */
function downloadLumaprintsFile() {
    window.location.href = '/api/lumaprints/download';
}

// Event listeners for Lumaprints buttons
document.addEventListener('DOMContentLoaded', function() {
    const btnUpload = document.getElementById('btn-lumaprints-upload');
    const btnAddRow = document.getElementById('btn-add-mapping-row');
    const btnApply = document.getElementById('btn-lumaprints-apply-all');
    const btnDownload = document.getElementById('btn-lumaprints-download');
    
    if (btnUpload) btnUpload.addEventListener('click', uploadLumaprintsFile);
    if (btnAddRow) btnAddRow.addEventListener('click', addMappingRow);
    if (btnApply) btnApply.addEventListener('click', applyLumaprintsMapping);
    if (btnDownload) btnDownload.addEventListener('click', downloadLumaprintsFile);
});
