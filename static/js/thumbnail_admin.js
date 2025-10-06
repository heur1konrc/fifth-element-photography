// Lumaprints Thumbnail Management JavaScript

class ThumbnailManager {
    constructor() {
        this.currentCategory = 'canvas';
        this.selectedFiles = [];
        this.thumbnailData = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadThumbnails();
    }

    setupEventListeners() {
        // Category tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchCategory(e.target.dataset.category);
            });
        });

        // File input handling
        const fileInput = document.getElementById('thumbnailInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e.target.files);
            });
        }

        // Drag and drop
        const dropzone = document.getElementById('thumbnailDropzone');
        if (dropzone) {
            dropzone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropzone.classList.add('dragover');
            });

            dropzone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            });

            dropzone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
                this.handleFileSelection(e.dataTransfer.files);
            });

            dropzone.addEventListener('click', () => {
                fileInput.click();
            });
        }
    }

    switchCategory(category) {
        this.currentCategory = category;
        
        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-category="${category}"]`).classList.add('active');
        
        // Load thumbnails for this category
        this.loadThumbnails();
    }

    handleFileSelection(files) {
        this.selectedFiles = Array.from(files);
        this.displaySelectedFiles();
    }

    displaySelectedFiles() {
        const grid = document.getElementById('thumbnailGrid');
        grid.innerHTML = '';

        if (this.selectedFiles.length === 0) {
            grid.innerHTML = '<div class="thumbnail-empty">No files selected. Choose files to upload.</div>';
            return;
        }

        this.selectedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const thumbnailItem = document.createElement('div');
                thumbnailItem.className = 'thumbnail-item';
                thumbnailItem.innerHTML = `
                    <img src="${e.target.result}" alt="${file.name}">
                    <div class="thumbnail-overlay">
                        <div class="thumbnail-actions">
                            <button class="btn-danger" onclick="thumbnailManager.removeFile(${index})" title="Remove">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
                grid.appendChild(thumbnailItem);
            };
            reader.readAsDataURL(file);
        });
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.displaySelectedFiles();
    }

    async uploadThumbnails() {
        if (this.selectedFiles.length === 0) {
            alert('Please select files to upload first.');
            return;
        }

        const formData = new FormData();
        formData.append('category', this.currentCategory);
        
        this.selectedFiles.forEach((file, index) => {
            formData.append('thumbnails', file);
        });

        try {
            const response = await fetch('/admin/upload-thumbnails', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                alert(`Successfully uploaded ${result.uploaded} thumbnail(s)!`);
                this.selectedFiles = [];
                this.loadThumbnails();
            } else {
                alert('Upload failed: ' + result.error);
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Upload failed. Please try again.');
        }
    }

    async loadThumbnails() {
        try {
            const response = await fetch(`/admin/thumbnails/${this.currentCategory}`);
            const thumbnails = await response.json();
            
            this.displayThumbnails(thumbnails);
        } catch (error) {
            console.error('Error loading thumbnails:', error);
            this.displayThumbnails([]);
        }
    }

    displayThumbnails(thumbnails) {
        const grid = document.getElementById('thumbnailGrid');
        
        if (thumbnails.length === 0) {
            grid.innerHTML = '<div class="thumbnail-empty">No thumbnails uploaded for this category yet.</div>';
            return;
        }

        grid.innerHTML = '';
        thumbnails.forEach(thumbnail => {
            const thumbnailItem = document.createElement('div');
            thumbnailItem.className = 'thumbnail-item';
            thumbnailItem.innerHTML = `
                <img src="${thumbnail.url}" alt="${thumbnail.name}">
                <div class="thumbnail-overlay">
                    <div class="thumbnail-actions">
                        <button class="btn-primary" onclick="thumbnailManager.replaceThumbnail('${thumbnail.id}')" title="Replace">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-danger" onclick="thumbnailManager.deleteThumbnail('${thumbnail.id}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            grid.appendChild(thumbnailItem);
        });
    }

    async deleteThumbnail(thumbnailId) {
        if (!confirm('Are you sure you want to delete this thumbnail?')) {
            return;
        }

        try {
            const response = await fetch(`/admin/thumbnails/${thumbnailId}`, {
                method: 'DELETE'
            });

            const result = await response.json();
            
            if (result.success) {
                this.loadThumbnails();
            } else {
                alert('Delete failed: ' + result.error);
            }
        } catch (error) {
            console.error('Delete error:', error);
            alert('Delete failed. Please try again.');
        }
    }

    replaceThumbnail(thumbnailId) {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('thumbnail', file);

            try {
                const response = await fetch(`/admin/thumbnails/${thumbnailId}/replace`, {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (result.success) {
                    this.loadThumbnails();
                } else {
                    alert('Replace failed: ' + result.error);
                }
            } catch (error) {
                console.error('Replace error:', error);
                alert('Replace failed. Please try again.');
            }
        };
        fileInput.click();
    }
}

// Global functions for onclick handlers
function uploadThumbnails() {
    if (window.thumbnailManager) {
        window.thumbnailManager.uploadThumbnails();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.thumbnailManager = new ThumbnailManager();
});
