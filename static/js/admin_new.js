// Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeModals();
    updateSelectionCount();
});

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
    
    // Create backup (this would need to be implemented on the backend)
    fetch('/backup_system', {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('Backup failed');
        }
    }).then(blob => {
        // Download backup file
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `portfolio_backup_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }).catch(error => {
        console.error('Error:', error);
        alert('Error creating backup. Please try again.');
    }).finally(() => {
        backupBtn.innerHTML = originalText;
        backupBtn.disabled = false;
    });
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
            if (event.target === modal) {
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

// File Upload Enhancement
function initializeFileUpload() {
    const dropZone = document.getElementById('fileDropZone');
    const fileInput = document.getElementById('fileInput');
    
    if (!dropZone || !fileInput) return;
    
    // Click to browse
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileInputDisplay(files);
        }
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
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
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    
    if (files.length === 0) {
        alert('Please select files to upload.');
        return;
    }
    
    const uploadBtn = document.querySelector('#uploadModal .btn-primary');
    const originalText = uploadBtn.innerHTML;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    uploadBtn.disabled = true;
    
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    
    fetch('/upload_images', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            closeUploadModal();
            location.reload(); // Refresh to show new images
        } else {
            alert('Upload failed: ' + data.message);
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Upload failed. Please try again.');
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

