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
    // Check for both Images tab (.image-select) and Shopify tab (.image-checkbox) checkboxes
    const selectedCheckboxes = document.querySelectorAll('.image-select:checked, .image-checkbox:checked');
    return Array.from(selectedCheckboxes).map(checkbox => checkbox.value || checkbox.dataset.filename);
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


function openReplaceImageModal(filename) {
    const modal = document.createElement('div');
    modal.id = 'replaceImageModal';
    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 10000;';
    
    modal.innerHTML = `
        <div style="background: #1a1a1a; padding: 30px; border-radius: 8px; max-width: 500px; width: 90%;">
            <h2 style="color: #fff; margin-bottom: 20px; font-size: 24px;">Replace Image</h2>
            <p style="color: #ccc; margin-bottom: 20px;">
                Select a new image file to replace <strong style="color: #96bf48;">${filename}</strong>.<br>
                The filename will stay the same, preserving all metadata, categories, galleries, and Shopify links.
            </p>
            <input type="file" id="replaceImageInput" accept="image/*" style="display: block; width: 100%; padding: 10px; margin-bottom: 20px; background: #2a2a2a; color: #fff; border: 1px solid #444; border-radius: 4px;">
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button onclick="closeReplaceImageModal()" style="padding: 10px 20px; background: #444; color: #fff; border: none; border-radius: 4px; cursor: pointer;">Cancel</button>
                <button onclick="replaceImageFile('${filename}')" style="padding: 10px 20px; background: #96bf48; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">Replace Image</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeReplaceImageModal();
        }
    });
}

function closeReplaceImageModal() {
    const modal = document.getElementById('replaceImageModal');
    if (modal) {
        modal.remove();
    }
}

function replaceImageFile(originalFilename) {
    const fileInput = document.getElementById('replaceImageInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file to upload.');
        return;
    }
    
    if (!confirm(`Replace ${originalFilename} with ${file.name}?\n\nThe filename will remain ${originalFilename} and all metadata will be preserved.`)) {
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('original_filename', originalFilename);
    
    // Show loading indicator
    const modal = document.getElementById('replaceImageModal');
    modal.innerHTML = `
        <div style="background: #1a1a1a; padding: 30px; border-radius: 8px; text-align: center;">
            <div style="color: #96bf48; font-size: 48px; margin-bottom: 20px;">
                <i class="fas fa-spinner fa-spin"></i>
            </div>
            <p style="color: #fff; font-size: 18px;">Replacing image...</p>
        </div>
    `;
    
    fetch('/api/replace_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeReplaceImageModal();
            alert(`Successfully replaced ${originalFilename}!`);
            location.reload();
        } else {
            closeReplaceImageModal();
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        closeReplaceImageModal();
        alert('Error replacing image. Please try again.');
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
    mappings: [],
    titleToFilenameMap: {}
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
            
            // Load title-to-filename mapping from image library
            await loadTitleToFilenameMap();
            
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
 * Load title-to-filename mapping from image library
 */
async function loadTitleToFilenameMap() {
    try {
        const response = await fetch('/api/images/title-filename-map');
        const data = await response.json();
        
        if (data.success) {
            LumaprintsState.titleToFilenameMap = data.map;
            console.log('Loaded title-to-filename map:', Object.keys(LumaprintsState.titleToFilenameMap).length, 'entries');
        }
    } catch (error) {
        console.error('Error loading title-to-filename map:', error);
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
    
    // Get unique product titles
    const uniqueTitles = getUniqueProductTitles();
    
    // Show product titles with checkboxes for selection
    listElem.innerHTML = `
        <h4>Select Products to Map:</h4>
        <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 4px; background: #f9f9f9;">
            ${uniqueTitles.map(title => {
                const count = LumaprintsState.unmappedProducts.filter(p => {
                    const baseTitle = p.product_name
                        .replace(/ - Canvas$/i, '')
                        .replace(/ - Framed Canvas$/i, '')
                        .replace(/ - Fine Art Paper$/i, '')
                        .replace(/ - Foam-mounted Print$/i, '')
                        .replace(/ - Metal Print$/i, '')
                        .replace(/ - Metal$/i, '')
                        .trim();
                    return baseTitle === title;
                }).length;
                return `
                    <div style="margin-bottom: 15px; padding: 10px; background: white; border: 1px solid #ddd; border-radius: 4px;">
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="checkbox" class="product-title-checkbox" value="${title}" style="margin-right: 10px; width: 18px; height: 18px;">
                            <div>
                                <strong>${title}</strong>
                                <div style="font-size: 0.9em; color: #666; margin-top: 4px;">${count} unmapped variants</div>
                            </div>
                        </label>
                        <div class="mapping-inputs-${title.replace(/[^a-zA-Z0-9]/g, '_')}" style="margin-top: 10px; padding-left: 28px; display: none;">
                            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px;">
                                <div>
                                    <label style="font-size: 0.9em; color: #666;">Image Filename:</label>
                                    <input type="text" class="mapping-filename" placeholder="e.g., image.jpg" style="width: 100%; padding: 8px; margin-top: 4px;">
                                </div>
                                <div>
                                    <label style="font-size: 0.9em; color: #666;">Aspect Ratio:</label>
                                    <select class="mapping-aspect" style="width: 100%; padding: 8px; margin-top: 4px;">
                                        <option value="3:2">3:2 (Landscape)</option>
                                        <option value="2:3">2:3 (Portrait)</option>
                                        <option value="1:1">1:1 (Square)</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    // Add event listeners to checkboxes
    document.querySelectorAll('.product-title-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const title = this.value;
            const safeTitle = title.replace(/[^a-zA-Z0-9]/g, '_');
            const inputsDiv = document.querySelector(`.mapping-inputs-${safeTitle}`);
            if (inputsDiv) {
                inputsDiv.style.display = this.checked ? 'block' : 'none';
            }
            
            // Auto-fill filename if available
            if (this.checked && LumaprintsState.titleToFilenameMap) {
                const filename = LumaprintsState.titleToFilenameMap[title];
                if (filename) {
                    const filenameInput = inputsDiv.querySelector('.mapping-filename');
                    if (filenameInput) filenameInput.value = filename;
                }
            }
        });
    });
}

/**
 * Get unique product titles from unmapped products
 * Extracts base title without product type suffix (e.g., "Oregon Hockey 16" from "Oregon Hockey 16 - Canvas")
 */
function getUniqueProductTitles() {
    console.log('DEBUG: Getting unique titles from', LumaprintsState.unmappedProducts.length, 'unmapped products');
    const titles = new Set();
    LumaprintsState.unmappedProducts.forEach(p => {
        if (p.product_name) {
            // Remove product type suffixes to get base title
            let baseTitle = p.product_name
                .replace(/ - Canvas$/i, '')
                .replace(/ - Framed Canvas$/i, '')
                .replace(/ - Fine Art Paper$/i, '')
                .replace(/ - Foam-mounted Print$/i, '')
                .replace(/ - Metal Print$/i, '')
                .replace(/ - Metal$/i, '')
                .trim();
            titles.add(baseTitle);
            console.log('DEBUG: Added title:', baseTitle);
        }
    });
    const result = Array.from(titles).sort();
    console.log('DEBUG: Unique titles found:', result);
    return result;
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
    
    // Add event listener to autofill filename when title is selected
    const titleSelect = rowDiv.querySelector('.mapping-title-select');
    const filenameInput = rowDiv.querySelector('.mapping-filename-input');
    
    titleSelect.addEventListener('change', function() {
        const selectedTitle = this.value;
        if (selectedTitle && LumaprintsState.titleToFilenameMap) {
            const filename = LumaprintsState.titleToFilenameMap[selectedTitle];
            if (filename) {
                filenameInput.value = filename;
            }
        }
    });
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
    // Collect checked products
    const checkboxes = document.querySelectorAll('.product-title-checkbox:checked');
    
    if (checkboxes.length === 0) {
        showAlert('Please select at least one product to map', 'warning');
        return;
    }
    
    // Validate and collect mappings
    const userMappings = [];
    for (const checkbox of checkboxes) {
        const title = checkbox.value;
        const safeTitle = title.replace(/[^a-zA-Z0-9]/g, '_');
        const inputsDiv = document.querySelector(`.mapping-inputs-${safeTitle}`);
        
        if (!inputsDiv) continue;
        
        const filenameInput = inputsDiv.querySelector('.mapping-filename');
        const aspectSelect = inputsDiv.querySelector('.mapping-aspect');
        
        const filename = filenameInput ? filenameInput.value.trim() : '';
        const aspectRatio = aspectSelect ? aspectSelect.value : '3:2';
        
        if (!filename) {
            showAlert(`Product "${title}": Please enter an image filename`, 'warning');
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
        // Extract base title from product name
        let baseTitle = product.product_name
            .replace(/ - Canvas$/i, '')
            .replace(/ - Framed Canvas$/i, '')
            .replace(/ - Fine Art Paper$/i, '')
            .replace(/ - Foam-mounted Print$/i, '')
            .replace(/ - Metal Print$/i, '')
            .replace(/ - Metal$/i, '')
            .trim();
        
        // Find matching user mapping by base title
        const userMapping = userMappings.find(m => m.title === baseTitle);
        
        if (!userMapping) {
            // Skip products that don't have a mapping
            continue;
        }
        
        // Generate proper mapping data based on product type
        const width = product.width || 0;
        const length = product.length || 0;
        
        console.log(`Product row ${product.row}: width=${width}, length=${length}, option1="${product.option1}"`);
        
        // Strip ALL occurrences of "Printed Product - " prefix (handles doubled prefixes)
        let productType = (product.option1 || '');
        while (productType.startsWith('Printed Product - ')) {
            productType = productType.replace(/^Printed Product - /i, '');
        }
        
        // Skip Rolled Canvas products entirely
        if (productType.includes('Rolled Canvas')) {
            continue;
        }
        
        let subcategory = '';
        let options = [];
        
        // Convert product type to Lumaprints subcategory format
        if (productType.includes('Stretched Canvas')) {
            // "0.75 Stretched Canvas" → "0.75in Stretched Canvas"
            subcategory = productType.replace(/(\d+\.\d+)\s/, '$1in ');
            options = [
                ['Canvas Border', 'Mirror Wrap'],
                ['Canvas Hanging Hardware', 'Sawtooth Hanger installed']
            ];
        } else if (productType.includes('Framed Canvas')) {
            // "1.25 Framed Canvas Oak" → "1.25in Framed Canvas"
            subcategory = productType.replace(/(\d+\.\d+)\s+Framed Canvas.*/, '$1in Framed Canvas');
            // Extract frame style from product type
            let frameStyle = '1.25in Oak Floating Frame'; // default
            if (productType.includes('Black')) frameStyle = '1.25in Black Floating Frame';
            else if (productType.includes('White')) frameStyle = '1.25in White Floating Frame';
            options = [
                ['Canvas Border', 'Mirror Wrap'],
                ['1.25 Inch Frame Styles', frameStyle],
                ['1.25in Framed Canvas Hanging Hardware', 'Hanging Wire installed']
            ];
        } else if (productType.includes('Foam-mounted')) {
            // Skip Foam-mounted products with invalid sizes
            // Min width: 5 inches, Max dimensions: 39.5 × 59.5 inches
            if (width < 5 || length < 5 || width > 39.5 || length > 59.5) {
                console.log(`Skipping Foam-mounted product at row ${product.row}: size ${width}×${length} outside valid range`);
                continue;
            }
            
            // "Foam-mounted Glossy" → "Foam-mounted Glossy Fine Art Paper"
            if (productType.includes('Glossy')) {
                subcategory = 'Foam-mounted Glossy Fine Art Paper';
            } else if (productType.includes('Semi-Glossy') || productType.includes('Semi-glossy')) {
                subcategory = 'Foam-mounted Semi-Glossy Fine Art Paper';
            } else if (productType.includes('Hot Press')) {
                subcategory = 'Foam-mounted Hot Press Fine Art Paper';
            } else if (productType.includes('Cold Press')) {
                subcategory = 'Foam-mounted Cold Press Fine Art Paper';
            } else {
                subcategory = 'Foam-mounted Glossy Fine Art Paper'; // default
            }
            options = [
                ['Bleed Size', '0.25in Bleed (0.25in on each side)']
            ];
        } else if (productType.includes('Metal')) {
            // "Glossy White Metal Print" or "Glossy Silver Metal Print"
            if (productType.includes('Silver')) {
                subcategory = 'Glossy Silver Metal Print';
            } else {
                subcategory = 'Glossy White Metal Print';
            }
            options = [
                ['Metal Hanging Hardware', 'Inset Frame']
            ];
        } else if (productType.includes('Semi-glossy') || productType.includes('Semi-Glossy')) {
            subcategory = 'Semi-Glossy Fine Art Paper';
            options = [
                ['Bleed Size', 'No Bleed (Image goes to edge of paper)']
            ];
        } else if (productType.includes('Glossy')) {
            subcategory = 'Glossy Fine Art Paper';
            options = [
                ['Bleed Size', 'No Bleed (Image goes to edge of paper)']
            ];
        } else if (productType.includes('Hot Press')) {
            subcategory = 'Hot Press Fine Art Paper';
            options = [
                ['Bleed Size', 'No Bleed (Image goes to edge of paper)']
            ];
        } else if (productType.includes('Cold Press')) {
            subcategory = 'Cold Press Fine Art Paper';
            options = [
                ['Bleed Size', 'No Bleed (Image goes to edge of paper)']
            ];
        } else {
            // Default: use as-is
            subcategory = productType;
            options = [];
        }
        
        // Add highres_ prefix to filename for Lumaprints
        let lumaprintsFilename = userMapping.filename;
        if (!lumaprintsFilename.startsWith('highres_')) {
            lumaprintsFilename = 'highres_' + lumaprintsFilename;
        }
        
        const mappingData = {
            image_filename: lumaprintsFilename,
            subcategory: subcategory,
            width: width,
            length: length,
            options: options
        };
        
        console.log(`Mapping data for row ${product.row}:`, mappingData);
        
        mappings.push({
            row: product.row,
            data: mappingData
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


// ============================================================================
// SHOPIFY CSV GENERATOR
// ============================================================================

async function generateShopifyCSVFromSelected() {
    const selectedImages = getSelectedImages();
    
    if (selectedImages.length === 0) {
        showAlert('Please select at least one image using the checkboxes.', 'warning');
        return;
    }
    
    showAlert(`Generating Shopify CSV for ${selectedImages.length} image(s)...`, 'info');
    
    try {
        const response = await fetch('/api/shopify/generate-csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                images: selectedImages.map(filename => ({
                    filename: filename,
                    title: filename.replace(/\.[^/.]+$/, "").replace(/[-_]/g, ' '),
                    description: '',
                    url: `/images/${filename}`
                }))
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `shopify_products_${Date.now()}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('✓ Shopify CSV generated and downloaded successfully!', 'success');
        } else {
            const error = await response.json();
            showAlert(`Error: ${error.error || 'Failed to generate CSV'}`, 'error');
        }
    } catch (error) {
        console.error('Error generating CSV:', error);
        showAlert('Error generating CSV. Please try again.', 'error');
    }
}


// ============================================================================
// SHOPIFY API PRODUCT CREATOR
// ============================================================================

async function createShopifyProductsViaAPI() {
    const selectedImages = getSelectedImages();
    
    console.log('DEBUG: Selected images:', selectedImages);
    console.log('DEBUG: Number of selected images:', selectedImages.length);
    
    if (selectedImages.length === 0) {
        showAlert('Please select at least one image using the checkboxes.', 'warning');
        return;
    }
    
    showAlert(`Creating ${selectedImages.length} Shopify product(s) via API...`, 'info');
    
    try {
        const requestData = { 
            images: selectedImages.map(filename => ({
                filename: filename,
                title: filename.replace(/\.[^/.]+$/, "").replace(/[-_]/g, ' '),
                description: ''
            }))
        };
        
        console.log('DEBUG: Sending request with data:', requestData);
        console.log('DEBUG: Number of images in request:', requestData.images.length);
        
        const response = await fetch('/api/shopify/create-product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        console.log('DEBUG: API response:', result);
        
        if (result.success) {
            let message = `✓ Successfully created ${result.created.length} product(s)!`;
            if (result.errors.length > 0) {
                message += `\n\nErrors:\n${result.errors.join('\n')}`;
                console.error('Product creation errors:', result.errors);
            }
            showAlert(message, result.errors.length > 0 ? 'warning' : 'success');
        } else {
            const errorMsg = `Error: ${result.error || 'Failed to create products'}`;
            console.error('API Error:', result);
            console.error('Error details:', JSON.stringify(result, null, 2));
            if (result.errors && result.errors.length > 0) {
                console.error('Errors array:', result.errors);
                result.errors.forEach((err, i) => console.error(`Error ${i}:`, err));
            }
            showAlert(errorMsg, 'error');
        }
    } catch (error) {
        console.error('Error creating products:', error);
        showAlert('Error creating products. Please try again.', 'error');
    }
}


// ===== SHOPIFY STATUS FILTER =====

let shopifyStatusData = {};
let currentShopifyFilter = 'all';

// Load Shopify status for all images
async function loadShopifyStatus() {
    try {
        const response = await fetch('/api/images/shopify-status');
        const result = await response.json();
        
        if (result.success) {
            // Build lookup map
            shopifyStatusData = {};
            result.images.forEach(img => {
                shopifyStatusData[img.filename] = img.in_shopify;
            });
            
            // Update filter stats
            updateFilterStats(result.images);
            
            // Apply current filter
            applyShopifyFilter();
        }
    } catch (error) {
        console.error('Error loading Shopify status:', error);
    }
}

// Update filter statistics
function updateFilterStats(images) {
    const inShopify = images.filter(img => img.in_shopify).length;
    const notInShopify = images.filter(img => !img.in_shopify).length;
    const total = images.length;
    
    const statsEl = document.getElementById('filterStats');
    if (statsEl) {
        statsEl.textContent = `Total: ${total} | In Shopify: ${inShopify} | Not in Shopify: ${notInShopify}`;
    }
}

// Apply Shopify filter to image grid
function applyShopifyFilter() {
    const filterSelect = document.getElementById('shopifyFilter');
    if (!filterSelect) return;
    
    currentShopifyFilter = filterSelect.value;
    
    // Get all image cards
    const imageCards = document.querySelectorAll('.image-card');
    
    imageCards.forEach(card => {
        const filename = card.dataset.filename;
        if (!filename) return;
        
        const inShopify = shopifyStatusData[filename] || false;
        
        // Apply filter
        if (currentShopifyFilter === 'all') {
            card.style.display = '';
        } else if (currentShopifyFilter === 'in_shopify') {
            card.style.display = inShopify ? '' : 'none';
        } else if (currentShopifyFilter === 'not_in_shopify') {
            card.style.display = !inShopify ? '' : 'none';
        }
    });
}

// Load Shopify status on page load
document.addEventListener('DOMContentLoaded', () => {
    loadShopifyStatus();
});

// Sync existing Shopify products
async function syncShopifyProducts() {
    if (!confirm('This will fetch all products from Shopify and update the database. Continue?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/shopify/sync-products', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`Successfully synced ${result.synced} products from Shopify (${result.total_shopify_products} total products found)`);
            // Reload status
            loadShopifyStatus();
        } else {
            alert('Sync failed: ' + result.error);
        }
    } catch (error) {
        console.error('Sync error:', error);
        alert('Sync failed. Please try again.');
    }
}

// Reload Shopify status after creating products
const originalCreateShopifyProductsViaAPI = window.createShopifyProductsViaAPI;
if (typeof originalCreateShopifyProductsViaAPI === 'function') {
    window.createShopifyProductsViaAPI = async function() {
        await originalCreateShopifyProductsViaAPI();
        // Reload status after creation
        setTimeout(() => loadShopifyStatus(), 1000);
    };
}

// ============================================================================
// SHOPIFY PRICE SYNC
// ============================================================================

async function syncShopifyPrices() {
    if (!confirm('This will update prices for ALL existing Shopify products based on current pricing in the database.\n\nThis process may take 30-60 minutes due to Shopify rate limits (2 requests/second).\n\nContinue?')) {
        return;
    }
    
    try {
        showAlert('Starting price sync... This will take 30-60 minutes. Please keep this tab open.', 'info');
        
        const response = await fetch('/api/shopify/sync-prices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Log all errors to console for debugging
            if (result.errors && result.errors.length > 0) {
                console.log('Price sync errors:', result.errors);
            }
            
            // Create a custom modal for better display
            let modalContent = `
                <div style="max-height: 500px; overflow-y: auto; text-align: left;">
                    <h4>✓ Price sync completed!</h4>
                    <p><strong>Products updated:</strong> ${result.products_updated}</p>
                    <p><strong>Variants updated:</strong> ${result.variants_updated}</p>
                    <p><strong>Duration:</strong> ${Math.round(result.duration_seconds / 60)} minutes</p>
            `;
            
            if (result.errors && result.errors.length > 0) {
                modalContent += `
                    <hr>
                    <h5>Errors (${result.errors.length}):</h5>
                    <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 11px; max-height: 300px; overflow-y: auto; white-space: pre-wrap;">
                `;
                result.errors.forEach(error => {
                    modalContent += `<div style="margin-bottom: 8px; border-bottom: 1px solid #dee2e6; padding-bottom: 5px;">${error}</div>`;
                });
                modalContent += `</div>`;
            }
            
            modalContent += `</div>`;
            
            // Use a simple modal
            const modal = document.createElement('div');
            modal.innerHTML = `
                <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); z-index: 10000; display: flex; align-items: center; justify-content: center;">
                    <div style="background: white; padding: 30px; border-radius: 8px; max-width: 900px; width: 90%;">
                        ${modalContent}
                        <button onclick="this.closest('div').parentElement.remove()" style="margin-top: 20px; padding: 10px 30px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;">Close</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            showAlert('Price sync completed successfully!', 'success');
        } else {
            showAlert(`Price sync failed: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Price sync error:', error);
        showAlert('Price sync failed. Please check console for details.', 'danger');
    }
}

// Generate gallery images
async function generateGalleryImages() {
    if (!confirm('This will pre-generate optimized versions of all images for fast gallery loading. This may take a few minutes. Continue?')) {
        return;
    }
    
    try {
        showAlert('Generating gallery images... This may take a few minutes.', 'info');
        
        const response = await fetch('/api/generate-gallery-images', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            let message = `Gallery images generated!\n\nGenerated: ${result.generated}\nSkipped (already exist): ${result.skipped}\nTotal: ${result.total}`;
            
            if (result.errors && result.errors.length > 0) {
                message += `\n\nErrors: ${result.errors.length}`;
            }
            
            alert(message);
            showAlert('Gallery images generated successfully!', 'success');
        } else {
            showAlert('Error generating gallery images: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error generating gallery images. Please try again.', 'error');
    }
}


// Populate EXIF database
async function populateExifDatabase() {
    if (!confirm('This will extract EXIF data from all images and store it in the database. This may take a few minutes. Continue?')) {
        return;
    }
    
    try {
        showAlert('Extracting EXIF data from all images... This may take a few minutes.', 'info');
        
        const response = await fetch('/api/populate-exif-database', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            let message = `EXIF data populated!\n\nProcessed: ${result.processed}\nSkipped: ${result.skipped}\nTotal: ${result.total}`;
            
            if (result.errors && result.errors.length > 0) {
                message += `\n\nErrors: ${result.errors.length}`;
            }
            
            alert(message);
            showAlert('EXIF database populated successfully! Image modals will now show camera data.', 'success');
        } else {
            showAlert('Error populating EXIF database: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error populating EXIF database. Please try again.', 'error');
    }
}


// Carousel Management Functions
async function addSelectedToCarousel() {
    const selected = getSelectedImages();
    if (selected.length === 0) {
        alert('Please select at least one image');
        return;
    }
    
    try {
        const response = await fetch('/api/carousel/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filenames: selected })
        });
        
        const data = await response.json();
        if (data.success) {
            showAlert(`${data.message}. Total carousel images: ${data.total}`, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        console.error('Error adding to carousel:', error);
        showAlert('Error adding images to carousel', 'error');
    }
}

async function removeSelectedFromCarousel() {
    const selected = getSelectedImages();
    if (selected.length === 0) {
        alert('Please select at least one image');
        return;
    }
    
    try {
        const response = await fetch('/api/carousel/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filenames: selected })
        });
        
        const data = await response.json();
        if (data.success) {
            showAlert(`${data.message}. Total carousel images: ${data.total}`, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        console.error('Error removing from carousel:', error);
        showAlert('Error removing images from carousel', 'error');
    }
}
