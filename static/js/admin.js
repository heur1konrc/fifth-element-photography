// Admin panel functionality
document.addEventListener('DOMContentLoaded', function() {
    // File input enhancement
    const fileInput = document.getElementById('file');
    const fileLabel = document.querySelector('.file-input-label');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function() {
            const fileCount = this.files.length;
            if (fileCount > 0) {
                fileLabel.innerHTML = `
                    <span class="file-icon">📁</span>
                    ${fileCount} file${fileCount > 1 ? 's' : ''} selected
                `;
                fileLabel.style.background = '#4CAF50';
                fileLabel.style.borderColor = '#45a049';
            } else {
                fileLabel.innerHTML = `
                    <span class="file-icon">📁</span>
                    Choose Images (JPG, PNG, GIF)
                `;
                fileLabel.style.background = '#333';
                fileLabel.style.borderColor = '#666';
            }
        });
    }
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
    
    // Rename form validation
    const renameForms = document.querySelectorAll('.rename-form');
    renameForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const input = this.querySelector('input[name="new_name"]');
            const value = input.value.trim();
            
            if (!value) {
                e.preventDefault();
                alert('Please enter a new filename');
                input.focus();
                return;
            }
            
            // Basic filename validation
            const invalidChars = /[<>:"/\\|?*]/g;
            if (invalidChars.test(value)) {
                e.preventDefault();
                alert('Filename contains invalid characters. Please use only letters, numbers, spaces, hyphens, and underscores.');
                input.focus();
                return;
            }
        });
    });
    
    // Image preview on hover
    const imageCards = document.querySelectorAll('.image-card');
    imageCards.forEach(card => {
        const img = card.querySelector('.image-preview img');
        if (img) {
            card.addEventListener('mouseenter', function() {
                img.style.transform = 'scale(1.05)';
            });
            
            card.addEventListener('mouseleave', function() {
                img.style.transform = 'scale(1)';
            });
        }
    });
});

