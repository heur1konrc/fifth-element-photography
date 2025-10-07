// Simplified Product Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeProductManagement();
    loadExistingThumbnails();
    updateProgressStats();
});

let selectedFile = null;
let currentProductKey = '';

function initializeProductManagement() {
    // Initialize file upload
    const dropZone = document.getElementById('thumbnailDropZone');
    const fileInput = document.getElementById('thumbnailFileInput');
    
    // Click to browse
    dropZone.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
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
            handleFileSelection(files[0]);
        }
    });
}

function handleFileSelection(file) {
    selectedFile = file;
    
    // Update drop zone to show selected file
    const dropZone = document.getElementById('thumbnailDropZone');
    dropZone.classList.add('file-selected');
    dropZone.innerHTML = `
        <div class="drop-zone-content">
            <i class="fas fa-check-circle"></i>
            <h4>File Selected</h4>
            <p>${file.name}</p>
            <p class="file-info">Ready to upload (150x150)</p>
        </div>
    `;
    
    // Enable upload button
    document.getElementById('uploadThumbnailBtn').disabled = false;
}

function loadProductVariants() {
    const productType = document.getElementById('productType').value;
    const variantSelect = document.getElementById('productVariant');
    
    // Reset variant dropdown
    variantSelect.innerHTML = '<option value="">Select Product Variant</option>';
    
    // Hide sections
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('currentThumbnail').style.display = 'none';
    
    if (productType && PRODUCT_VARIANTS[productType]) {
        const variants = PRODUCT_VARIANTS[productType];
        
        variants.forEach(variant => {
            const option = document.createElement('option');
            option.value = variant;
            option.textContent = variant;
            variantSelect.appendChild(option);
        });
        
        variantSelect.disabled = false;
    } else {
        variantSelect.disabled = true;
    }
}

function showUploadSection() {
    const productType = document.getElementById('productType').value;
    const productVariant = document.getElementById('productVariant').value;
    
    if (productType && productVariant) {
        // Create product key for file naming
        currentProductKey = `${productType}_${productVariant}`.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
        
        // Check if thumbnail already exists
        checkExistingThumbnail(currentProductKey);
        
        // Show upload section
        document.getElementById('uploadSection').style.display = 'block';
        
        // Reset file selection
        resetFileSelection();
    }
}

function checkExistingThumbnail(productKey) {
    fetch(`/api/product-thumbnail-check/${encodeURIComponent(productKey)}`)
        .then(response => response.json())
        .then(data => {
            const currentThumbnailDiv = document.getElementById('currentThumbnail');
            
            if (data.exists) {
                // Show current thumbnail
                document.getElementById('thumbnailPreview').src = data.url;
                document.getElementById('thumbnailName').textContent = data.filename;
                currentThumbnailDiv.style.display = 'block';
            } else {
                currentThumbnailDiv.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error checking thumbnail:', error);
            document.getElementById('currentThumbnail').style.display = 'none';
        });
}

function uploadThumbnail() {
    if (!selectedFile || !currentProductKey) {
        showAlert('Please select a file and product variant', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('productKey', currentProductKey);
    formData.append('productType', document.getElementById('productType').value);
    formData.append('productVariant', document.getElementById('productVariant').value);
    
    // Update button state
    const uploadBtn = document.getElementById('uploadThumbnailBtn');
    const originalText = uploadBtn.innerHTML;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    uploadBtn.disabled = true;
    
    fetch('/api/upload-product-thumbnail-new', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Thumbnail uploaded successfully!', 'success');
            
            // Refresh current thumbnail display
            checkExistingThumbnail(currentProductKey);
            
            // Refresh thumbnails grid and progress
            loadExistingThumbnails();
            updateProgressStats();
            
            // Reset file selection
            resetFileSelection();
        } else {
            showAlert('Error uploading thumbnail: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        showAlert('Error uploading thumbnail: ' + error.message, 'error');
    })
    .finally(() => {
        uploadBtn.innerHTML = originalText;
        uploadBtn.disabled = false;
    });
}

function deleteThumbnail() {
    if (!currentProductKey) {
        showAlert('No thumbnail selected', 'error');
        return;
    }
    
    if (!confirm('Are you sure you want to delete this thumbnail?')) {
        return;
    }
    
    fetch(`/api/delete-product-thumbnail-new/${encodeURIComponent(currentProductKey)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Thumbnail deleted successfully!', 'success');
            
            // Hide current thumbnail display
            document.getElementById('currentThumbnail').style.display = 'none';
            
            // Refresh thumbnails grid and progress
            loadExistingThumbnails();
            updateProgressStats();
        } else {
            showAlert('Error deleting thumbnail: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error deleting thumbnail', 'error');
    });
}

function loadExistingThumbnails() {
    fetch('/api/product-thumbnails-new')
        .then(response => response.json())
        .then(data => {
            const grid = document.getElementById('thumbnailsGrid');
            
            if (data.thumbnails && data.thumbnails.length > 0) {
                grid.innerHTML = data.thumbnails.map(thumbnail => `
                    <div class="thumbnail-card">
                        <img src="${thumbnail.url}" alt="${thumbnail.displayName}">
                        <div class="thumbnail-card-info">
                            <div class="thumbnail-card-title">${thumbnail.displayName}</div>
                            <div class="thumbnail-card-details">${thumbnail.productType} - ${thumbnail.productVariant}</div>
                            <div class="thumbnail-card-actions">
                                <button class="btn btn-danger btn-small" onclick="deleteThumbnailByKey('${thumbnail.productKey}')">
                                    <i class="fas fa-trash"></i>
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('');
            } else {
                grid.innerHTML = `
                    <div class="empty-thumbnails">
                        <i class="fas fa-images"></i>
                        <h4>No Thumbnails Yet</h4>
                        <p>Upload thumbnails using the form above to see them here.</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading thumbnails:', error);
            document.getElementById('thumbnailsGrid').innerHTML = `
                <div class="empty-thumbnails">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h4>Error Loading Thumbnails</h4>
                    <p>Please refresh the page to try again.</p>
                </div>
            `;
        });
}

function deleteThumbnailByKey(productKey) {
    if (!confirm('Are you sure you want to delete this thumbnail?')) {
        return;
    }
    
    fetch(`/api/delete-product-thumbnail-new/${encodeURIComponent(productKey)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Thumbnail deleted successfully!', 'success');
            loadExistingThumbnails();
            updateProgressStats();
            
            // If this was the currently selected thumbnail, hide the display
            if (productKey === currentProductKey) {
                document.getElementById('currentThumbnail').style.display = 'none';
            }
        } else {
            showAlert('Error deleting thumbnail: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error deleting thumbnail', 'error');
    });
}

function updateProgressStats() {
    fetch('/api/product-thumbnails-stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('uploadedCount').textContent = data.uploaded;
            document.getElementById('totalCount').textContent = data.total;
            document.getElementById('progressPercent').textContent = data.percentage + '%';
        })
        .catch(error => {
            console.error('Error loading stats:', error);
        });
}

function resetFileSelection() {
    selectedFile = null;
    
    // Reset drop zone
    const dropZone = document.getElementById('thumbnailDropZone');
    if (dropZone) {
        dropZone.classList.remove('file-selected');
        dropZone.innerHTML = `
            <div class="drop-zone-content">
                <i class="fas fa-cloud-upload-alt"></i>
                <h4>Upload Product Thumbnail</h4>
                <p>Drag & drop your thumbnail here or click to browse</p>
                <p class="file-info">150x150px, AVIF/JPG format</p>
            </div>
        `;
    }
    
    // Reset file input safely
    const fileInput = document.getElementById('thumbnailFileInput');
    if (fileInput) {
        fileInput.value = '';
    }
    
    // Disable upload button safely
    const uploadBtn = document.getElementById('uploadThumbnailBtn');
    if (uploadBtn) {
        uploadBtn.disabled = true;
    }
}

// Alert function for user feedback
function showAlert(message, type = 'info') {
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
