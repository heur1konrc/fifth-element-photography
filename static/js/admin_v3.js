/**
 * Admin V3 JavaScript - Fifth Element Photography
 * Version: 3.0.0-alpha
 * 
 * Handles all client-side logic for the admin dashboard.
 * Organized into modules for maintainability.
 */

// ==================== STATE MANAGEMENT ====================

const AppState = {
    images: [],
    categories: [],
    currentFilter: 'all',
    currentSort: 'newest',
    searchQuery: '',
    currentPage: 1,
    imagesPerPage: 24,
    selectedFiles: [],
    selectedImages: [] // For bulk operations
};

// ==================== API FUNCTIONS ====================

const API = {
    /**
     * Fetch all images with optional filtering and sorting
     */
    async fetchImages(category = 'all', sort = 'newest') {
        const params = new URLSearchParams({ category, sort });
        const response = await fetch(`/api/v3/images?${params}`);
        if (!response.ok) throw new Error('Failed to fetch images');
        return await response.json();
    },

    /**
     * Fetch a single image's data
     */
    async fetchImage(filename) {
        const response = await fetch(`/api/v3/images/${filename}`);
        if (!response.ok) throw new Error('Failed to fetch image');
        return await response.json();
    },

    /**
     * Update an image's metadata and categories
     */
    async updateImage(filename, data) {
        const response = await fetch(`/api/v3/images/${filename}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Failed to update image');
        return await response.json();
    },

    /**
     * Delete an image
     */
    async deleteImage(filename) {
        const response = await fetch(`/api/v3/images/${filename}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete image');
        return await response.json();
    },

    /**
     * Upload images
     */
    async uploadImages(files) {
        const formData = new FormData();
        files.forEach(file => formData.append('files[]', file));

        const response = await fetch('/api/v3/upload', {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error('Failed to upload images');
        return await response.json();
    },

    /**
     * Fetch all categories
     */
    async fetchCategories() {
        const response = await fetch('/api/v3/categories');
        if (!response.ok) throw new Error('Failed to fetch categories');
        return await response.json();
    },

    /**
     * Create a new category
     */
    async createCategory(name) {
        const response = await fetch('/api/v3/categories', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (!response.ok) throw new Error('Failed to create category');
        return await response.json();
    },

    /**
     * Delete a category
     */
    async deleteCategory(name) {
        const response = await fetch(`/api/v3/categories/${encodeURIComponent(name)}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete category');
        return await response.json();
    },

    /**
     * Bulk assign categories to multiple images
     */
    async bulkAssignCategories(filenames, categories) {
        const response = await fetch('/api/v3/images/bulk/assign-categories', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filenames, categories })
        });
        if (!response.ok) throw new Error('Failed to assign categories');
        return await response.json();
    }
};

// ==================== UI FUNCTIONS ====================

const UI = {
    /**
     * Show notification toast
     */
    showNotification(message, isError = false) {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.classList.toggle('error', isError);
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    },

    /**
     * Show modal
     */
    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    },

    /**
     * Hide modal
     */
    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    },

    /**
     * Render image gallery
     */
    renderGallery(imagesToRender = null) {
        const gallery = document.getElementById('image-gallery');
        
        // Use provided images or default to AppState.images
        const images = imagesToRender || AppState.images;
        
        if (images.length === 0) {
            gallery.innerHTML = '<div class="loading">No images found</div>';
            return;
        }

        // Pagination
        const startIndex = (AppState.currentPage - 1) * AppState.imagesPerPage;
        const endIndex = startIndex + AppState.imagesPerPage;
        const paginatedImages = images.slice(startIndex, endIndex);

        gallery.innerHTML = paginatedImages.map(image => `
            <div class="image-card" data-filename="${image.filename}">
                <input type="checkbox" class="image-checkbox" data-filename="${image.filename}">
                <a href="/data/${image.filename}" download="${image.filename}" class="download-btn" title="Download Hi-Res" onclick="event.stopPropagation()">⬇️</a>
                ${image.featured ? '<div class="featured-badge" title="Featured Image">⭐</div>' : ''}
                <img src="/data/thumbnails/${image.filename}" alt="${image.title}" class="image-card-img">
                <div class="image-card-content">
                    <div class="image-card-title">${image.title}</div>
                    <div class="image-card-categories">
                        ${image.categories.map(cat => `
                            <span class="category-badge">${cat}</span>
                        `).join('')}
                    </div>
                </div>
            </div>
        `).join('');

        // Add click handlers for image cards (not checkboxes)
        document.querySelectorAll('.image-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // Don't open edit modal if clicking checkbox
                if (e.target.classList.contains('image-checkbox')) return;
                const filename = card.dataset.filename;
                UI.openEditModal(filename);
            });
        });

        // Add checkbox change handlers
        document.querySelectorAll('.image-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                e.stopPropagation();
                updateSelectedImages();
            });
        });

        // Render pagination
        UI.renderPagination();
    },

    /**
     * Render pagination controls
     */
    renderPagination() {
        const pagination = document.getElementById('pagination');
        const totalPages = Math.ceil(AppState.images.length / AppState.imagesPerPage);

        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let html = '';
        for (let i = 1; i <= totalPages; i++) {
            html += `<button class="${i === AppState.currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
        }

        pagination.innerHTML = html;

        // Add click handlers
        pagination.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                AppState.currentPage = parseInt(btn.dataset.page);
                UI.renderGallery();
            });
        });
    },

    /**
     * Populate category filter dropdown
     */
    populateCategoryFilter() {
        const select = document.getElementById('filter-category');
        select.innerHTML = '<option value="all">All Categories</option>' +
            AppState.categories.map(cat => `
                <option value="${cat.name}">${cat.name} (${cat.count})</option>
            `).join('');
    },

    /**
     * Open edit modal for an image
     */
    async openEditModal(filename) {
        try {
            const image = await API.fetchImage(filename);
            
            document.getElementById('edit-filename').value = filename;
            document.getElementById('edit-title').value = image.title;
            document.getElementById('edit-description').value = image.description;
            document.getElementById('edit-featured').checked = image.featured || false;
            document.getElementById('edit-image-preview').src = `/data/${filename}`;

            // Populate categories
            const categoriesContainer = document.getElementById('edit-categories');
            categoriesContainer.innerHTML = AppState.categories.map(cat => `
                <label class="category-checkbox">
                    <input type="checkbox" value="${cat.name}" 
                           ${image.categories.includes(cat.name) ? 'checked' : ''}>
                    ${cat.name}
                </label>
            `).join('');
            
            // Load and display EXIF data
            try {
                const exifResponse = await fetch(`/api/v3/images/${filename}/exif`);
                const exifData = await exifResponse.json();
                const exifContainer = document.getElementById('edit-exif');
                
                if (Object.keys(exifData).length === 0) {
                    exifContainer.innerHTML = '<p style="color: #999; font-style: italic;">No EXIF data available</p>';
                } else {
                    const exifLabels = {
                        'camera': 'Camera',
                        'lens': 'Lens',
                        'aperture': 'Aperture',
                        'shutter_speed': 'Shutter Speed',
                        'iso': 'ISO',
                        'focal_length': 'Focal Length',
                        'date_taken': 'Date Taken',
                        'dimensions': 'Dimensions'
                    };
                    
                    exifContainer.innerHTML = Object.entries(exifData)
                        .map(([key, value]) => `
                            <div class="exif-item">
                                <span class="exif-label">${exifLabels[key] || key}:</span>
                                <span class="exif-value">${value}</span>
                            </div>
                        `).join('');
                }
            } catch (error) {
                document.getElementById('edit-exif').innerHTML = '<p style="color: #999;">Could not load EXIF data</p>';
            }

            UI.showModal('edit-modal');
        } catch (error) {
            UI.showNotification('Error loading image: ' + error.message, true);
        }
    },

    /**
     * Populate categories in manage modal
     */
    renderCategoriesModal() {
        const container = document.getElementById('current-categories');
        container.innerHTML = AppState.categories.map(cat => `
            <div class="category-item">
                <div class="category-info">
                    <span class="category-name">${cat.name}</span>
                    <span class="category-count">${cat.count} images</span>
                </div>
                <button class="btn-delete-category" data-category="${cat.name}">Delete</button>
            </div>
        `).join('');

        // Add delete handlers
        container.querySelectorAll('.btn-delete-category').forEach(btn => {
            btn.addEventListener('click', async () => {
                const categoryName = btn.dataset.category;
                if (confirm(`Delete category "${categoryName}"? This will remove it from all images.`)) {
                    try {
                        await API.deleteCategory(categoryName);
                        UI.showNotification('Category deleted successfully');
                        await loadCategories();
                        UI.renderCategoriesModal();
                        UI.populateCategoryFilter();
                    } catch (error) {
                        UI.showNotification('Error deleting category: ' + error.message, true);
                    }
                }
            });
        });
    }
};

// ==================== EVENT HANDLERS ====================

/**
 * Load images from API
 */
async function loadImages() {
    try {
        AppState.images = await API.fetchImages(AppState.currentFilter, AppState.currentSort);
        UI.renderGallery();
    } catch (error) {
        UI.showNotification('Error loading images: ' + error.message, true);
    }
}

/**
 * Load categories from API
 */
async function loadCategories() {
    try {
        AppState.categories = await API.fetchCategories();
        UI.populateCategoryFilter();
    } catch (error) {
        UI.showNotification('Error loading categories: ' + error.message, true);
    }
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    /**
     * Handle category filter change
     */
    document.getElementById('filter-category').addEventListener('change', async (e) => {
        AppState.currentFilter = e.target.value;
        AppState.currentPage = 1;
        await loadImages();
    });

    /**
     * Handle sort change
     */
    document.getElementById('sort-order').addEventListener('change', async (e) => {
        AppState.currentSort = e.target.value;
        AppState.currentPage = 1;
        await loadImages();
    });

    /**
     * Handle search input
     */
    document.getElementById('search-box').addEventListener('input', (e) => {
        AppState.searchQuery = e.target.value.toLowerCase().trim();
        UI.renderGallery(getFilteredAndSortedImages());
    });

    /**
     * Handle upload button
     */
    document.getElementById('btn-upload').addEventListener('click', () => {
        UI.showModal('upload-modal');
    });

    /**
     * Handle manage categories button
     */
    document.getElementById('btn-manage-categories').addEventListener('click', () => {
        UI.renderCategoriesModal();
        UI.showModal('categories-modal');
    });

    /**
     * Handle Lumaprints mapping button
     */
    document.getElementById('btn-lumaprints').addEventListener('click', () => {
        openLumaprintsModal();
    });

    /**
     * Handle Lumaprints upload button
     */
    document.getElementById('btn-lumaprints-upload').addEventListener('click', () => {
        uploadLumaprintsFile();
    });



    /**
     * Handle Lumaprints apply mapping
     */
    document.getElementById('btn-lumaprints-apply-all').addEventListener('click', () => {
        applyLumaprintsMapping();
    });

    /**
     * Handle Lumaprints download
     */
    document.getElementById('btn-lumaprints-download').addEventListener('click', () => {
        downloadLumaprintsFile();
    });

    /**
     * Handle browse files button
     */
    document.getElementById('btn-browse').addEventListener('click', () => {
        document.getElementById('file-input').click();
    });

    /**
     * Handle save image
     */
    document.getElementById('btn-save-image').addEventListener('click', async () => {
        const filename = document.getElementById('edit-filename').value;
        const title = document.getElementById('edit-title').value;
        const description = document.getElementById('edit-description').value;
        const featured = document.getElementById('edit-featured').checked;
        
        const categories = Array.from(document.querySelectorAll('#edit-categories input:checked'))
            .map(input => input.value);

        try {
            await API.updateImage(filename, { title, description, categories, featured });
            UI.showNotification('Image updated successfully');
            UI.hideModal('edit-modal');
            await loadImages();
            await loadCategories();
        } catch (error) {
            UI.showNotification('Error updating image: ' + error.message, true);
        }
    });

    /**
     * Handle delete image
     */
    document.getElementById('btn-delete-image').addEventListener('click', async () => {
        const filename = document.getElementById('edit-filename').value;
        
        if (confirm(`Delete "${filename}"? This action cannot be undone.`)) {
            try {
                await API.deleteImage(filename);
                UI.showNotification('Image deleted successfully');
                UI.hideModal('edit-modal');
                await loadImages();
                await loadCategories();
            } catch (error) {
                UI.showNotification('Error deleting image: ' + error.message, true);
            }
        }
    });

    /**
     * Handle add category
     */
    document.getElementById('btn-add-category').addEventListener('click', async () => {
        const input = document.getElementById('new-category-name');
        const categoryName = input.value.trim();
        
        if (!categoryName) {
            UI.showNotification('Please enter a category name', true);
            return;
        }

        try {
            await API.createCategory(categoryName);
            UI.showNotification('Category created successfully');
            input.value = '';
            await loadCategories();
            UI.renderCategoriesModal();
            UI.populateCategoryFilter();
        } catch (error) {
            UI.showNotification('Error creating category: ' + error.message, true);
        }
    });

    /**
     * Handle modal close buttons
     */
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').classList.remove('active');
        });
    });

    /**
     * Close modal on background click
     */
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });

    /**
     * Handle file selection
     */
    document.getElementById('file-input').addEventListener('change', (e) => {
        AppState.selectedFiles = Array.from(e.target.files);
        
        const preview = document.getElementById('upload-preview');
        preview.innerHTML = AppState.selectedFiles.map(file => `
            <div class="upload-preview-item">
                <img src="${URL.createObjectURL(file)}" class="upload-preview-img">
            </div>
        `).join('');
    });

    /**
     * Handle drag and drop upload
     */
    const uploadArea = document.getElementById('upload-area');

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'));
        AppState.selectedFiles = files;
        
        const preview = document.getElementById('upload-preview');
        preview.innerHTML = files.map(file => `
            <div class="upload-preview-item">
                <img src="${URL.createObjectURL(file)}" class="upload-preview-img">
            </div>
        `).join('');
    });

    /**
     * Handle upload confirm
     */
    document.getElementById('btn-upload-confirm').addEventListener('click', async () => {
        if (AppState.selectedFiles.length === 0) {
            UI.showNotification('Please select files to upload', true);
            return;
        }

        const statusDiv = document.getElementById('upload-status');
        const uploadBtn = document.getElementById('btn-upload-confirm');
        
        try {
            // Show progress
            uploadBtn.disabled = true;
            uploadBtn.textContent = 'Uploading...';
            statusDiv.innerHTML = `<p>Uploading ${AppState.selectedFiles.length} file(s)... Please wait.</p>`;
            
            const result = await API.uploadImages(AppState.selectedFiles);
            
            // Show results
            if (result.errors.length > 0) {
                statusDiv.innerHTML = `<p style="color: orange;">✓ Uploaded ${result.uploaded.length} files. ✗ ${result.errors.length} failed.</p>`;
                UI.showNotification(`Uploaded ${result.uploaded.length} files. ${result.errors.length} errors.`, true);
            } else {
                statusDiv.innerHTML = `<p style="color: green;">✓ Successfully uploaded ${result.uploaded.length} file(s)!</p>`;
                UI.showNotification(`Successfully uploaded ${result.uploaded.length} files`);
            }

            // Wait a moment to show success, then close
            setTimeout(() => {
                UI.hideModal('upload-modal');
                AppState.selectedFiles = [];
                document.getElementById('upload-preview').innerHTML = '';
                document.getElementById('file-input').value = '';
                statusDiv.innerHTML = '';
                uploadBtn.disabled = false;
                uploadBtn.textContent = 'Upload';
            }, 1500);
            
            await loadImages();
        } catch (error) {
            statusDiv.innerHTML = `<p style="color: red;">✗ Error: ${error.message}</p>`;
            UI.showNotification('Error uploading files: ' + error.message, true);
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload';
        }
    });
}

/**
 * Get filtered and sorted images based on current state
 */
function getFilteredAndSortedImages() {
    let filtered = AppState.images;
    
    // Apply category filter
    if (AppState.currentFilter !== 'all') {
        filtered = filtered.filter(img => img.categories.includes(AppState.currentFilter));
    }
    
    // Apply search filter
    if (AppState.searchQuery) {
        filtered = filtered.filter(img => {
            const searchText = `${img.filename} ${img.title} ${img.description}`.toLowerCase();
            return searchText.includes(AppState.searchQuery);
        });
    }
    
    // Apply sorting
    filtered = [...filtered].sort((a, b) => {
        switch (AppState.currentSort) {
            case 'newest':
                return new Date(b.upload_date) - new Date(a.upload_date);
            case 'oldest':
                return new Date(a.upload_date) - new Date(b.upload_date);
            case 'name_asc':
                return a.filename.localeCompare(b.filename);
            case 'name_desc':
                return b.filename.localeCompare(a.filename);
            default:
                return 0;
        }
    });
    
    return filtered;
}







// ==================== BULK ACTIONS ====================

/**
 * Update selected images state and UI
 */
function updateSelectedImages() {
    const checkboxes = document.querySelectorAll('.image-checkbox:checked');
    AppState.selectedImages = Array.from(checkboxes).map(cb => cb.dataset.filename);
    
    const count = AppState.selectedImages.length;
    const bulkBar = document.getElementById('bulk-actions-bar');
    const countSpan = document.getElementById('selected-count');
    
    if (count > 0) {
        bulkBar.style.display = 'flex';
        countSpan.textContent = `${count} image${count > 1 ? 's' : ''} selected`;
    } else {
        bulkBar.style.display = 'none';
    }
}

/**
 * Select all images on current page
 */
document.getElementById('btn-select-all').addEventListener('click', () => {
    document.querySelectorAll('.image-checkbox').forEach(cb => cb.checked = true);
    updateSelectedImages();
});

/**
 * Deselect all images
 */
document.getElementById('btn-deselect-all').addEventListener('click', () => {
    document.querySelectorAll('.image-checkbox').forEach(cb => cb.checked = false);
    updateSelectedImages();
});

/**
 * Open bulk assign categories modal
 */
document.getElementById('btn-bulk-assign-categories').addEventListener('click', () => {
    if (AppState.selectedImages.length === 0) return;
    
    // Update count in modal
    document.getElementById('bulk-assign-count').textContent = AppState.selectedImages.length;
    
    // Populate categories
    const container = document.getElementById('bulk-assign-categories');
    container.innerHTML = AppState.categories.map(cat => `
        <label class="category-checkbox-label">
            <input type="checkbox" value="${cat.name}">
            <span>${cat.name}</span>
        </label>
    `).join('');
    
    // Show modal
    document.getElementById('bulk-assign-modal').classList.add('active');
});

/**
 * Confirm bulk category assignment
 */
document.getElementById('btn-bulk-assign-confirm').addEventListener('click', async () => {
    const checkboxes = document.querySelectorAll('#bulk-assign-categories input:checked');
    const categories = Array.from(checkboxes).map(cb => cb.value);
    
    if (categories.length === 0) {
        UI.showNotification('Please select at least one category', true);
        return;
    }
    
    try {
        const result = await API.bulkAssignCategories(AppState.selectedImages, categories);
        UI.showNotification(result.message);
        document.getElementById('bulk-assign-modal').classList.remove('active');
        
        // Deselect all and reload
        document.querySelectorAll('.image-checkbox').forEach(cb => cb.checked = false);
        updateSelectedImages();
        await loadCategories(); // Reload category counts
        await loadImages(); // Reload gallery
    } catch (error) {
        UI.showNotification('Error assigning categories: ' + error.message, true);
    }
});

/**
 * Bulk delete images
 */
document.getElementById('btn-bulk-delete').addEventListener('click', async () => {
    if (AppState.selectedImages.length === 0) return;
    
    const count = AppState.selectedImages.length;
    if (!confirm(`Delete ${count} selected image${count > 1 ? 's' : ''}? This cannot be undone.`)) {
        return;
    }
    
    try {
        let successCount = 0;
        for (const filename of AppState.selectedImages) {
            try {
                await API.deleteImage(filename);
                successCount++;
            } catch (error) {
                console.error(`Failed to delete ${filename}:`, error);
            }
        }
        
        UI.showNotification(`Deleted ${successCount} of ${count} image(s)`);
        
        // Deselect all and reload
        document.querySelectorAll('.image-checkbox').forEach(cb => cb.checked = false);
        updateSelectedImages();
        await loadCategories(); // Reload category counts
        await loadImages(); // Reload gallery
    } catch (error) {
        UI.showNotification('Error deleting images: ' + error.message, true);
    }
});

/**
 * Backup button - create backup and show download modal
 */
document.getElementById('btn-backup').addEventListener('click', async () => {
    if (confirm('Create a backup of all images and data? This may take a moment for large galleries.')) {
        try {
            UI.showNotification('Creating backup... Please wait.');
            
            const response = await fetch('/api/v3/backup/create');
            const data = await response.json();
            
            if (data.success) {
                // Show modal with download button
                document.getElementById('backup-filename').textContent = data.filename;
                document.getElementById('backup-size').textContent = data.size_mb;
                document.getElementById('btn-download-backup').href = data.download_url;
                document.getElementById('backup-success-modal').classList.add('active');
                
                // Also auto-trigger download
                window.location.href = data.download_url;
                
                UI.showNotification(`✓ Backup created: ${data.filename} (${data.size_mb} MB)`);
            } else {
                UI.showNotification('Backup failed: ' + (data.error || 'Unknown error'), true);
            }
        } catch (error) {
            UI.showNotification('Error creating backup: ' + error.message, true);
        }
    }
});

/**
 * Manage Backups button - open backups management modal
 */
document.getElementById('btn-manage-backups').addEventListener('click', async () => {
    document.getElementById('manage-backups-modal').classList.add('active');
    await loadBackupsList();
});

/**
 * Refresh backups list
 */
document.getElementById('btn-refresh-backups').addEventListener('click', async () => {
    await loadBackupsList();
});

/**
 * Load and display backups list
 */
async function loadBackupsList() {
    try {
        const response = await fetch('/api/v3/backup/list');
        const data = await response.json();
        
        if (data.success) {
            // Update summary
            document.getElementById('backups-count').textContent = data.total_count;
            document.getElementById('backups-total-size').textContent = data.total_size_mb;
            
            // Build backups list HTML
            const listContainer = document.getElementById('backups-list');
            
            if (data.backups.length === 0) {
                listContainer.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">No backups found</p>';
                return;
            }
            
            let html = '<table style="width: 100%; border-collapse: collapse;">';
            html += '<thead><tr style="border-bottom: 2px solid #ddd; text-align: left;">';
            html += '<th style="padding: 10px;">Filename</th>';
            html += '<th style="padding: 10px;">Date</th>';
            html += '<th style="padding: 10px;">Size</th>';
            html += '<th style="padding: 10px;">Actions</th>';
            html += '</tr></thead><tbody>';
            
            data.backups.forEach(backup => {
                html += '<tr style="border-bottom: 1px solid #eee;">';
                html += `<td style="padding: 10px; font-family: monospace; font-size: 12px;">${backup.filename}</td>`;
                html += `<td style="padding: 10px;">${backup.created}</td>`;
                html += `<td style="padding: 10px;">${backup.size_mb} MB</td>`;
                html += '<td style="padding: 10px;">';
                html += `<a href="${backup.download_url}" class="btn btn-sm btn-primary" download style="margin-right: 5px;">Download</a>`;
                html += `<button class="btn btn-sm btn-danger" onclick="deleteBackup('${backup.filename}')">Delete</button>`;
                html += '</td>';
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            listContainer.innerHTML = html;
        } else {
            UI.showNotification('Failed to load backups: ' + (data.error || 'Unknown error'), true);
        }
    } catch (error) {
        UI.showNotification('Error loading backups: ' + error.message, true);
    }
}

/**
 * Delete a backup file
 */
async function deleteBackup(filename) {
    if (!confirm(`Delete backup: ${filename}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/v3/backup/delete/${filename}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            UI.showNotification(`✓ Backup deleted: ${filename}`);
            await loadBackupsList(); // Refresh the list
        } else {
            UI.showNotification('Failed to delete backup: ' + (data.error || 'Unknown error'), true);
        }
    } catch (error) {
        UI.showNotification('Error deleting backup: ' + error.message, true);
    }
}

// ==================== LUMAPRINTS MAPPING ====================

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
    UI.showModal('lumaprints-modal');
    // Reset to step 1
    document.getElementById('lumaprints-step-1').style.display = 'block';
    document.getElementById('lumaprints-step-2').style.display = 'none';
    document.getElementById('lumaprints-step-3').style.display = 'none';
}

/**
 * Upload and process Lumaprints Excel file
 */
async function uploadLumaprintsFile() {
    const fileInput = document.getElementById('lumaprints-file-input');
    const statusDiv = document.getElementById('lumaprints-upload-status');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        UI.showNotification('Please select a file', true);
        return;
    }
    
    const file = fileInput.files[0];
    
    if (!file.name.endsWith('.xlsx')) {
        UI.showNotification('File must be .xlsx format', true);
        return;
    }
    
    statusDiv.innerHTML = '<p>Processing file...</p>';
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/v3/lumaprints/upload', {
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
        const response = await fetch('/api/v3/lumaprints/images');
        const data = await response.json();
        
        LumaprintsState.availableImages = data.images;
        
        // Populate image select dropdown
        const select = document.getElementById('lumaprints-image-select');
        select.innerHTML = '<option value="">-- Select Image --</option>';
        
        data.images.forEach(img => {
            const option = document.createElement('option');
            option.value = img.filename;
            option.textContent = `${img.title || img.filename} (${img.aspect_ratio} - ${img.dimensions})`;
            option.dataset.aspectRatio = img.aspect_ratio;
            option.dataset.dimensions = img.dimensions;
            select.appendChild(option);
        });
    } catch (error) {
        UI.showNotification('Error loading images: ' + error.message, true);
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
    
    // Show first 10 products as preview
    const preview = LumaprintsState.unmappedProducts.slice(0, 10);
    listElem.innerHTML = `
        <h4>Preview (first 10 products):</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f0f0f0;">
                    <th style="padding: 8px; border: 1px solid #ddd;">Product Name</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Size</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Product Type</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Existing Filename</th>
                </tr>
            </thead>
            <tbody>
                ${preview.map(p => `
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">${p.product_name || ''}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">${p.size || 'Unknown'}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">${p.option1 || ''}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">${p.existing_filename || 'None'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        ${LumaprintsState.unmappedProducts.length > 10 ? `<p style="margin-top: 10px; font-style: italic;">... and ${LumaprintsState.unmappedProducts.length - 10} more products</p>` : ''}
    `;
}

/**
 * Handle image selection change
 */
function onLumaprintsImageChange() {
    const select = document.getElementById('lumaprints-image-select');
    const infoDiv = document.getElementById('lumaprints-image-info');
    
    if (!select.value) {
        infoDiv.innerHTML = '';
        return;
    }
    
    const option = select.options[select.selectedIndex];
    const aspectRatio = option.dataset.aspectRatio;
    const dimensions = option.dataset.dimensions;
    
    infoDiv.innerHTML = `
        <strong>Aspect Ratio:</strong> ${aspectRatio} &nbsp;|&nbsp; 
        <strong>Dimensions:</strong> ${dimensions}
    `;
}

/**
 * Apply mapping to all unmapped products
 * Applies ALL product types (Canvas + all Art Paper types) at once
 */
async function applyLumaprintsMapping() {
    const imageSelect = document.getElementById('lumaprints-image-select');
    const aspectRatio = document.getElementById('lumaprints-aspect-ratio').value;
    
    if (!imageSelect.value) {
        UI.showNotification('Please select an image', true);
        return;
    }
    
    const imageFilename = imageSelect.value;
    
    // Build mappings for all unmapped products
    const mappings = [];
    
    for (const product of LumaprintsState.unmappedProducts) {
        const filename = product.existing_filename || imageFilename;
        const width = product.width || 12;
        const length = product.length || 18;
        
        // Determine subcategory and options based on product option1
        let subcategory = '';
        let options = [];
        
        const option1Lower = (product.option1 || '').toLowerCase();
        
        // Match product type from option1
        if (option1Lower.includes('canvas') || option1Lower.includes('stretched')) {
            subcategory = '0.75in Stretched Canvas';
            options = [
                ['Canvas Border', 'Mirror Wrap'],
                ['Canvas Hanging Hardware', 'Sawtooth Hanger installed'],
                ['Canvas Finish', 'Semi-Glossy']
            ];
        } else if (option1Lower.includes('hot') && option1Lower.includes('press')) {
            subcategory = 'Hot Press Fine Art Paper';
            options = [
                ['Bleed Size', '0.25in Bleed (0.25in on each side)']
            ];
        } else if (option1Lower.includes('semi') && option1Lower.includes('gloss')) {
            subcategory = 'Semi-Glossy Fine Art Paper';
            options = [
                ['Bleed Size', '0.25in Bleed (0.25in on each side)']
            ];
        } else if (option1Lower.includes('gloss') && !option1Lower.includes('semi')) {
            subcategory = 'Glossy Fine Art Paper';
            options = [
                ['Bleed Size', '0.25in Bleed (0.25in on each side)']
            ];
        } else {
            // Default to Hot Press if can't determine
            subcategory = 'Hot Press Fine Art Paper';
            options = [
                ['Bleed Size', '0.25in Bleed (0.25in on each side)']
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
        const response = await fetch('/api/v3/lumaprints/apply-mapping', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mappings: mappings })
        });
        
        const data = await response.json();
        
        if (data.success) {
            UI.showNotification(`✓ Successfully mapped ${data.mapped_count} products!`);
            
            // Move to step 3
            document.getElementById('lumaprints-step-2').style.display = 'none';
            document.getElementById('lumaprints-step-3').style.display = 'block';
            document.getElementById('lumaprints-mapped-count').textContent = data.mapped_count;
        } else {
            UI.showNotification('Error applying mapping: ' + data.error, true);
        }
    } catch (error) {
        UI.showNotification('Error: ' + error.message, true);
    }
}

/**
 * Download mapped Excel file
 */
function downloadLumaprintsFile() {
    window.location.href = '/api/v3/lumaprints/download';
}

// ==================== INITIALIZATION ====================

/**
 * Initialize the application
 */
async function init() {
    setupEventListeners();
    await loadCategories();
    await loadImages();
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

