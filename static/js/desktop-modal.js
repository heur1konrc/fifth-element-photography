// Desktop Modal Script - Fixed Version
let allImages = [];

document.addEventListener('DOMContentLoaded', function() {
    // Reset body overflow in case it's stuck
    document.body.style.overflow = 'auto';
    
    loadImages();
    
    async function loadImages() {
        try {
            const response = await fetch('/api/images');
            allImages = await response.json();
            displayImages(allImages);
        } catch (error) {
            console.error('Error loading images:', error);
            document.getElementById('imageGrid').innerHTML = '<div class="loading">Error loading images</div>';
        }
    }
    
    function displayImages(images) {
        const imageGrid = document.getElementById('imageGrid');
        if (!imageGrid) return;
        
        const imageHTML = images.map(image => {
            return `
                <div class="image-item" onclick="openImageModal('${image.url}', '${image.title}')">
                    <img src="${image.url}" alt="${image.title}" loading="lazy">
                    <div class="image-overlay">
                        <div class="image-title">${image.title}</div>
                        <div class="image-category">${image.category.toUpperCase()}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        imageGrid.innerHTML = imageHTML;
        
        // Hide pagination
        const paginationContainer = document.getElementById('paginationContainer');
        if (paginationContainer) {
            paginationContainer.style.display = 'none';
        }
    }
    
    // Make openImageModal global
    window.openImageModal = function(imageUrl, title) {
        const modal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        const modalTitle = document.getElementById('modalTitle');
        const modalCategory = document.getElementById('modalCategory');
        
        if (modal && modalImage && modalTitle && modalCategory) {
            modalImage.src = imageUrl;
            modalTitle.textContent = title;
            modalCategory.innerHTML = '<span class="brand-main">FIFTH ELEMENT</span><br><span class="brand-sub">PHOTOGRAPHY</span>';
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    };
    
    // Make closeModal global
    window.closeImageModal = function() {
        const modal = document.getElementById('imageModal');
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = 'auto';
        }
    };
    
    // ORDER PRINTS functionality
    window.openDesktopOrderForm = function() {
        const modalTitle = document.getElementById('modalTitle');
        if (modalTitle && modalTitle.textContent) {
            const imageName = encodeURIComponent(modalTitle.textContent.trim());
            const orderFormUrl = '/test_order_form?image=' + imageName;
            window.open(orderFormUrl, '_blank');
        } else {
            window.open('/test_order_form', '_blank');
        }
    };
    
    // Setup close events
    const closeBtn = document.querySelector('.close');
    const modal = document.getElementById('imageModal');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', window.closeImageModal);
    }
    
    if (modal) {
        window.addEventListener('click', function(e) {
            if (e.target === modal) {
                window.closeImageModal();
            }
        });
    }
});
