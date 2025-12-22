// Inline Editing Functions for Admin

// Save inline edits (title or filename)
async function saveInlineEdit(element, field) {
    const filename = element.dataset.filename;
    const newValue = element.value.trim();
    
    if (!newValue) {
        showNotification('Value cannot be empty', 'error');
        // Reload to restore original value
        location.reload();
        return;
    }
    
    // Validate filename extension if editing filename
    if (field === 'filename') {
        const ext = filename.split('.').pop();
        if (!newValue.endsWith('.' + ext)) {
            showNotification('Filename must keep the original extension', 'error');
            location.reload();
            return;
        }
    }
    
    try {
        const response = await fetch('/admin/update-image-field', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: filename,
                field: field,
                value: newValue
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${field.charAt(0).toUpperCase() + field.slice(1)} updated successfully`, 'success');
            
            // If filename changed, update all data-filename attributes
            if (field === 'filename' && data.new_filename) {
                const panel = element.closest('.image-panel-horizontal');
                panel.dataset.filename = data.new_filename;
                panel.querySelectorAll('[data-filename]').forEach(el => {
                    el.dataset.filename = data.new_filename;
                });
            }
        } else {
            showNotification(data.error || 'Failed to update', 'error');
            location.reload();
        }
    } catch (error) {
        console.error('Error saving inline edit:', error);
        showNotification('Error updating field', 'error');
        location.reload();
    }
}

// Toggle Featured status
async function toggleFeatured(filename) {
    try {
        const response = await fetch('/admin/toggle-featured', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: filename })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const icon = document.querySelector(`.image-panel-horizontal[data-filename="${filename}"] .fa-star`);
            if (data.is_featured) {
                icon.classList.add('active');
                icon.title = 'Remove from Featured';
                showNotification('Added to Featured', 'success');
            } else {
                icon.classList.remove('active');
                icon.title = 'Set as Featured';
                showNotification('Removed from Featured', 'success');
            }
        } else {
            showNotification(data.error || 'Failed to toggle featured', 'error');
        }
    } catch (error) {
        console.error('Error toggling featured:', error);
        showNotification('Error toggling featured status', 'error');
    }
}

// Toggle Carousel status
async function toggleCarousel(filename) {
    try {
        const response = await fetch('/admin/toggle-carousel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: filename })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const icon = document.querySelector(`.image-panel-horizontal[data-filename="${filename}"] .fa-images`);
            if (data.in_carousel) {
                icon.classList.add('active');
                icon.title = 'Remove from Carousel';
                showNotification('Added to Carousel', 'success');
            } else {
                icon.classList.remove('active');
                icon.title = 'Add to Carousel';
                showNotification('Removed from Carousel', 'success');
            }
        } else {
            showNotification(data.error || 'Failed to toggle carousel', 'error');
        }
    } catch (error) {
        console.error('Error toggling carousel:', error);
        showNotification('Error toggling carousel status', 'error');
    }
}

// Open category selector modal
function openCategorySelector(filename) {
    // TODO: Implement category selector modal
    showNotification('Category selector coming soon', 'info');
}

// Open gallery selector modal
function openGallerySelector(filename) {
    // TODO: Implement gallery selector modal
    showNotification('Gallery selector coming soon', 'info');
}

// Download hi-res image
function downloadHighres(filename) {
    window.location.href = `/admin/download-highres/${filename}`;
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.inline-notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `inline-notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
