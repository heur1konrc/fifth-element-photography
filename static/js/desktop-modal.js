// Desktop Modal Script - Simple and Clean
document.addEventListener('DOMContentLoaded', function() {
    
    // Add click handlers to all gallery images
    function setupImageClicks() {
        const imageItems = document.querySelectorAll('.image-item');
        imageItems.forEach(item => {
            item.addEventListener('click', function() {
                const img = this.querySelector('img');
                const titleDiv = this.querySelector('.image-title');
                
                if (img && titleDiv) {
                    const imageUrl = img.src;
                    const imageTitle = titleDiv.textContent;
                    openImageModal(imageUrl, imageTitle);
                }
            });
        });
    }
    
    // Open modal with image
    function openImageModal(imageUrl, title) {
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
    }
    
    // Close modal
    function closeModal() {
        const modal = document.getElementById('imageModal');
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = 'auto';
        }
    }
    
    // ORDER PRINTS functionality (same as mobile)
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
        closeBtn.addEventListener('click', closeModal);
    }
    
    if (modal) {
        window.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    // Initialize
    setupImageClicks();
    
    // Re-setup clicks when new images load (for pagination/filtering)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                setupImageClicks();
            }
        });
    });
    
    const imageGrid = document.getElementById('imageGrid');
    if (imageGrid) {
        observer.observe(imageGrid, { childList: true });
    }
});
