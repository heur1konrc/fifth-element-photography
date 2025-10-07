// Admin Thumbnails Management JavaScript

let currentThumbnail = null;

document.addEventListener('DOMContentLoaded', function() {
    loadThumbnails();
    setupFileUpload();
});

function setupFileUpload() {
    const uploadSection = document.getElementById('uploadSection');
    const fileInput = document.getElementById('fileInput');
    
    // Drag and drop functionality
    uploadSection.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadSection.classList.add('dragover');
    });
    
    uploadSection.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadSection.classList.remove('dragover');
    });
    
    uploadSection.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadSection.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        handleFileUpload(files);
    });
    
    // File input change
    fileInput.addEventListener('change', function(e) {
        handleFileUpload(e.target.files);
    });
    
    // Click to upload
    uploadSection.addEventListener('click', function() {
        fileInput.click();
    });
}

function handleFileUpload(files) {
    if (files.length === 0) return;
    
    const formData = new FormData();
    
    for (let i = 0; i < files.length; i++) {
        formData.append('thumbnails', files[i]);
    }
    
    // Show loading state
    showAlert('Uploading thumbnails...', 'info');
    
    fetch('/admin/upload-product-thumbnails', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(`Successfully uploaded ${data.uploaded} thumbnail(s)`, 'success');
            loadThumbnails(); // Reload the grid
        } else {
            showAlert(`Error: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error uploading thumbnails', 'error');
    });
}

function loadThumbnails() {
    fetch('/api/product-thumbnails')
        .then(response => response.json())
        .then(data => {
            displayThumbnails(data.thumbnails || []);
        })
        .catch(error => {
            console.error('Error loading thumbnails:', error);
            showAlert('Error loading thumbnails', 'error');
        });
}

function displayThumbnails(thumbnails) {
    const grid = document.getElementById('thumbnailGrid');
    
    if (thumbnails.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: #666; padding: 40px;">
                <i class="fas fa-images" style="font-size: 3rem; margin-bottom: 20px;"></i>
                <h3>No thumbnails uploaded yet</h3>
                <p>Upload some product thumbnails to get started</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = thumbnails.map(thumbnail => `
        <div class="thumbnail-item">
            <div class="thumbnail-preview">
                <img src="${thumbnail.url}" alt="${thumbnail.name}" loading="lazy">
            </div>
            <div class="thumbnail-info">
                <div class="thumbnail-name">${thumbnail.name}</div>
                <div class="thumbnail-assignment">
                    ${thumbnail.assignment || 'Not assigned'}
                </div>
            </div>
            <div class="thumbnail-actions">
                <button class="btn btn-small btn-primary" onclick="editThumbnail('${thumbnail.id}', '${thumbnail.name}', '${thumbnail.assignment || ''}')">
                    <i class="fas fa-edit"></i>
                    Edit
                </button>
                <button class="btn btn-small btn-danger" onclick="deleteThumbnail('${thumbnail.id}', '${thumbnail.name}')">
                    <i class="fas fa-trash"></i>
                    Delete
                </button>
            </div>
        </div>
    `).join('');
}

function editThumbnail(thumbnailId, thumbnailName, currentAssignment) {
    currentThumbnail = {
        id: thumbnailId,
        name: thumbnailName,
        assignment: currentAssignment
    };
    
    // Set current assignment in dropdown
    const productSelect = document.getElementById('productSelect');
    productSelect.value = currentAssignment || '';
    
    // Update modal title
    document.querySelector('#editModal .modal-header h3').textContent = `Assign: ${thumbnailName}`;
    
    // Show modal
    document.getElementById('editModal').style.display = 'block';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    currentThumbnail = null;
}

function saveAssignment() {
    if (!currentThumbnail) return;
    
    const productSelect = document.getElementById('productSelect');
    const selectedProduct = productSelect.value;
    
    if (!selectedProduct) {
        showAlert('Please select a product', 'warning');
        return;
    }
    
    // Save assignment
    fetch(`/admin/assign-thumbnail`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            thumbnail_id: currentThumbnail.id,
            product_id: selectedProduct
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Assignment saved successfully', 'success');
            closeEditModal();
            loadThumbnails(); // Reload to show updated assignment
        } else {
            showAlert(`Error: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error saving assignment', 'error');
    });
}

function deleteThumbnail(thumbnailId, thumbnailName) {
    if (!confirm(`Are you sure you want to delete "${thumbnailName}"? This action cannot be undone.`)) {
        return;
    }
    
    fetch(`/admin/delete-product-thumbnail/${thumbnailId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Thumbnail deleted successfully', 'success');
            loadThumbnails(); // Reload the grid
        } else {
            showAlert(`Error: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error deleting thumbnail', 'error');
    });
}

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

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('editModal');
    if (event.target === modal) {
        closeEditModal();
    }
});
