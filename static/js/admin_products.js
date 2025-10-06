// Product Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeProductManagement();
    loadExistingThumbnails();
});

let selectedFile = null;
let currentProductPath = '';

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
            <p class="file-info">Ready to upload</p>
        </div>
    `;
    
    // Enable upload button
    document.getElementById('uploadThumbnailBtn').disabled = false;
}

function loadProductSizes() {
    const productType = document.getElementById('productType').value;
    const sizeSelect = document.getElementById('productSize');
    const optionSelect = document.getElementById('productOption');
    
    // Reset dependent dropdowns
    sizeSelect.innerHTML = '<option value="">Select Size</option>';
    optionSelect.innerHTML = '<option value="">Select Option</option>';
    optionSelect.disabled = true;
    
    // Hide upload section
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('currentThumbnail').style.display = 'none';
    
    if (productType && PRODUCT_DATA[productType]) {
        const sizes = Object.keys(PRODUCT_DATA[productType].sizes);
        
        sizes.forEach(size => {
            const option = document.createElement('option');
            option.value = size;
            option.textContent = size;
            sizeSelect.appendChild(option);
        });
        
        sizeSelect.disabled = false;
    } else {
        sizeSelect.disabled = true;
    }
}

function loadProductOptions() {
    const productType = document.getElementById('productType').value;
    const productSize = document.getElementById('productSize').value;
    const optionSelect = document.getElementById('productOption');
    
    // Reset option dropdown
    optionSelect.innerHTML = '<option value="">Select Option</option>';
    
    // Hide upload section
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('currentThumbnail').style.display = 'none';
    
    if (productType && productSize && PRODUCT_DATA[productType] && PRODUCT_DATA[productType].sizes[productSize]) {
        const options = PRODUCT_DATA[productType].sizes[productSize];
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.toLowerCase().replace(/[^a-z0-9]/g, '-');
            optionElement.textContent = option;
            optionSelect.appendChild(optionElement);
        });
        
        optionSelect.disabled = false;
    } else {
        optionSelect.disabled = true;
    }
}

function showThumbnailUpload() {
    const productType = document.getElementById('productType').value;
    const productSize = document.getElementById('productSize').value;
    const productOption = document.getElementById('productOption').value;
    
    if (productType && productSize && productOption) {
        // Create product path
        currentProductPath = `${productType}/${productSize}/${productOption}`;
        
        // Check if thumbnail already exists
        checkExistingThumbnail(currentProductPath);
        
        // Show upload section
        document.getElementById('uploadSection').style.display = 'block';
        
        // Reset file selection
        resetFileSelection();
    }
}

function checkExistingThumbnail(productPath) {
    fetch(`/api/product-thumbnail/${encodeURIComponent(productPath)}`)
        .then(response => response.json())
        .then(data => {
            const currentThumbnailDiv = document.getElementById('currentThumbnail');
            
            if (data.exists) {
                // Show current thumbnail
                document.getElementById('thumbnailPreview').src = data.url;
                document.getElementById('thumbnailPath').textContent = data.path;
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
    console.log('uploadThumbnail called');
    console.log('selectedFile:', selectedFile);
    console.log('currentProductPath:', currentProductPath);
    
    if (!selectedFile || !currentProductPath) {
        showAlert('Please select a file and product configuration', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('productPath', currentProductPath);
    
    console.log('FormData created with file:', selectedFile.name, 'and path:', currentProductPath);
    
    // Update button state
    const uploadBtn = document.getElementById('uploadThumbnailBtn');
    const originalText = uploadBtn.innerHTML;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    uploadBtn.disabled = true;
    
    fetch('/api/upload-product-thumbnail', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            showAlert('Thumbnail uploaded successfully!', 'success');
            
            // Refresh current thumbnail display
            checkExistingThumbnail(currentProductPath);
            
            // Refresh thumbnails grid
            loadExistingThumbnails();
            
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
    if (!currentProductPath) {
        showAlert('No thumbnail selected', 'error');
        return;
    }
    
    if (!confirm('Are you sure you want to delete this thumbnail?')) {
        return;
    }
    
    fetch(`/api/delete-product-thumbnail/${encodeURIComponent(currentProductPath)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Thumbnail deleted successfully!', 'success');
            
            // Hide current thumbnail display
            document.getElementById('currentThumbnail').style.display = 'none';
            
            // Refresh thumbnails grid
            loadExistingThumbnails();
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
    fetch('/api/product-thumbnails')
        .then(response => response.json())
        .then(data => {
            const grid = document.getElementById('thumbnailsGrid');
            
            if (data.thumbnails && data.thumbnails.length > 0) {
                grid.innerHTML = data.thumbnails.map(thumbnail => `
                    <div class="thumbnail-card">
                        <img src="${thumbnail.url}" alt="${thumbnail.name}">
                        <div class="thumbnail-card-info">
                            <div class="thumbnail-card-title">${thumbnail.displayName}</div>
                            <div class="thumbnail-card-details">${thumbnail.path}</div>
                            <div class="thumbnail-card-actions">
                                <button class="btn btn-danger btn-small" onclick="deleteThumbnailByPath('${thumbnail.path}')">
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

function deleteThumbnailByPath(path) {
    if (!confirm('Are you sure you want to delete this thumbnail?')) {
        return;
    }
    
    fetch(`/api/delete-product-thumbnail/${encodeURIComponent(path)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Thumbnail deleted successfully!', 'success');
            loadExistingThumbnails();
            
            // If this was the currently selected thumbnail, hide the display
            if (path === currentProductPath) {
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

function resetFileSelection() {
    selectedFile = null;
    
    // Reset drop zone
    const dropZone = document.getElementById('thumbnailDropZone');
    dropZone.classList.remove('file-selected');
    dropZone.innerHTML = `
        <div class="drop-zone-content">
            <i class="fas fa-cloud-upload-alt"></i>
            <h4>Upload Product Thumbnail</h4>
            <p>Drag & drop your thumbnail image here or click to browse</p>
            <p class="file-info">Recommended: 300x300px, JPG/PNG format</p>
        </div>
    `;
    
    // Reset file input
    document.getElementById('thumbnailFileInput').value = '';
    
    // Disable upload button
    document.getElementById('uploadThumbnailBtn').disabled = true;
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
