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
    renderGallery() {
        const gallery = document.getElementById('image-gallery');
        
        if (AppState.images.length === 0) {
            gallery.innerHTML = '<div class="loading">No images found</div>';
            return;
        }

        // Pagination
        const startIndex = (AppState.currentPage - 1) * AppState.imagesPerPage;
        const endIndex = startIndex + AppState.imagesPerPage;
        const paginatedImages = AppState.images.slice(startIndex, endIndex);

        gallery.innerHTML = paginatedImages.map(image => `
            <div class="image-card" data-filename="${image.filename}">
                <input type="checkbox" class="image-checkbox" data-filename="${image.filename}">
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
 * Handle filter change
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
 * Handle browse files button
 */
document.getElementById('btn-browse').addEventListener('click', () => {
    document.getElementById('file-input').click();
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

    try {
        const result = await API.uploadImages(AppState.selectedFiles);
        
        if (result.errors.length > 0) {
            UI.showNotification(`Uploaded ${result.uploaded.length} files. ${result.errors.length} errors.`, true);
        } else {
            UI.showNotification(`Successfully uploaded ${result.uploaded.length} files`);
        }

        UI.hideModal('upload-modal');
        AppState.selectedFiles = [];
        document.getElementById('upload-preview').innerHTML = '';
        document.getElementById('file-input').value = '';
        await loadImages();
    } catch (error) {
        UI.showNotification('Error uploading files: ' + error.message, true);
    }
});

/**
 * Handle save image
 */
document.getElementById('btn-save-image').addEventListener('click', async () => {
    const filename = document.getElementById('edit-filename').value;
    const title = document.getElementById('edit-title').value;
    const description = document.getElementById('edit-description').value;
    
    const categories = Array.from(document.querySelectorAll('#edit-categories input:checked'))
        .map(input => input.value);

    try {
        await API.updateImage(filename, { title, description, categories });
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
 * Backup button - download full backup
 */
document.getElementById('btn-backup').addEventListener('click', () => {
    if (confirm('Create a backup of all images and data? This may take a moment for large galleries.')) {
        // Open backup URL in new window to trigger download
        window.location.href = '/api/v3/backup/create';
        UI.showNotification('Creating backup... Download will start shortly.');
    }
});

// ==================== INITIALIZATION ====================

/**
 * Initialize the application
 */
async function init() {
    await loadCategories();
    await loadImages();
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

