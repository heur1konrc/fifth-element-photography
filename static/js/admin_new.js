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
function editImage(filename) {
    // Load edit form in modal
    fetch(`/edit_image/${filename}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('editModalContent').innerHTML = html;
            openEditModal();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading edit form. Please try again.');
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
function saveImageChanges(filename) {
    const form = document.querySelector('.edit-form');
    if (!form) {
        alert('Form not found');
        return;
    }
    
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
    document.getElementById('aboutUploadModal').style.display = 'block';
    initializeAboutUpload();
}

function closeAboutUploadModal() {
    document.getElementById('aboutUploadModal').style.display = 'none';
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
    
    fileInput.value = '';
    bioText.value = '';
    aboutForm.style.display = 'none';
    
    dropZone.innerHTML = `
        <div class="drop-zone-content">
            <i class="fas fa-user"></i>
            <h4>Upload About Page Image</h4>
            <p>Drag & drop your about page image here or click to browse</p>
            <p class="file-info">Supports: JPG, PNG, GIF</p>
        </div>
    `;
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

// Update the DOMContentLoaded event listener to include text formatting initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeModals();
    updateSelectionCount();
    initializeTextFormatting(); // Add this line
});

