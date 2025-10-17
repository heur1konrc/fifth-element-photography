// Desktop Modal Script - Complete Version
let allImages = [];

document.addEventListener('DOMContentLoaded', function() {
    document.body.style.overflow = 'auto';
    loadImages();
    
    async function loadImages() {
        try {
            const response = await fetch('/api/images');
            allImages = await response.json();
            
            if (allImages.length > 0) {
                setHeroImage();
                displayImages(allImages);
            }
        } catch (error) {
            console.error('Error loading images:', error);
        }
    }
    
    async function setHeroImage() {
        const heroImage = document.getElementById('heroImage');
        if (!heroImage) return;
        
        try {
            const heroResponse = await fetch('/api/hero_image');
            const heroData = await heroResponse.json();
            
            if (heroData.filename) {
                heroImage.style.backgroundImage = `url('/images/${heroData.filename}')`;
            } else if (allImages.length > 0) {
                const randomImage = allImages[Math.floor(Math.random() * allImages.length)];
                heroImage.style.backgroundImage = `url('${randomImage.url}')`;
            }
        } catch (error) {
            if (allImages.length > 0) {
                const randomImage = allImages[Math.floor(Math.random() * allImages.length)];
                heroImage.style.backgroundImage = `url('${randomImage.url}')`;
            }
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
        
        // Hide pagination container
        const paginationContainer = document.getElementById('paginationContainer');
        if (paginationContainer) {
            paginationContainer.style.display = 'none';
        // Hide loading text
        const loadingDiv = document.querySelector(".loading");
        if (loadingDiv) {
            loadingDiv.style.display = "none";
        }
        
        // Update image count
        const imageCount = document.getElementById("imageCount");
        if (imageCount) {
            imageCount.textContent = `${images.length} image${images.length !== 1 ? "s" : ""}`;
        }
        }
    }
    
    window.openImageModal = function(imageUrl, title) {
        console.log('Opening modal for:', title);
        const modal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        const modalTitle = document.getElementById('modalTitle');
        const modalCategory = document.getElementById('modalCategory');
        
        console.log('Modal elements:', modal, modalImage, modalTitle, modalCategory);
        
        if (modal && modalImage && modalTitle && modalCategory) {
            modalImage.src = imageUrl;
            modalTitle.textContent = title;
            modalCategory.innerHTML = '<span class="brand-main">FIFTH ELEMENT</span><br><span class="brand-sub">PHOTOGRAPHY</span>';
            modal.style.display = 'flex';
            modal.classList.add('show');
        }
    };
    
    window.closeImageModal = function() {
        const modal = document.getElementById('imageModal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('show');
            document.body.style.overflow = 'auto';
        }
    };
    
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
