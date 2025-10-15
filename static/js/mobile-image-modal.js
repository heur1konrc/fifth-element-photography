/**
 * Mobile Image Modal & Ordering Interface
 * Fifth Element Photography
 * Version: 2.0 Mobile-First
 * Focus: Mobile Ordering Excellence
 */

class MobileImageModal {
    constructor() {
        this.isOpen = false;
        this.currentImageIndex = 0;
        this.images = window.imagesData || [];
        this.filteredImages = [...this.images];
        this.selectedProduct = null;
        this.modal = null;
        
        this.init();
    }
    
    init() {
        this.createModal();
        this.setupEventListeners();
        this.setupTouchEvents();
    }
    
    createModal() {
        // Create modal HTML structure
        const modalHTML = `
            <div class="mobile-image-modal" id="mobileImageModal">
                <div class="mobile-modal-header">
                    <button class="mobile-modal-close" id="mobileModalClose">
                        <i data-lucide="x" class="mobile-modal-close-icon"></i>
                    </button>
                    <h2 class="mobile-modal-title" id="mobileModalTitle">Image Title</h2>
                    <div style="width: 44px;"></div> <!-- Spacer for centering -->
                </div>
                
                <div class="mobile-modal-content" id="mobileModalContent">
                    <div class="mobile-modal-loading" id="mobileModalLoading">
                        <div class="mobile-modal-spinner"></div>
                        <p class="mobile-modal-loading-text">Loading image...</p>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('mobileImageModal');
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    setupEventListeners() {
        // Close modal
        const closeBtn = document.getElementById('mobileModalClose');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }
        
        // Close on overlay click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
        
        // Arrow keys for navigation
        document.addEventListener('keydown', (e) => {
            if (!this.isOpen) return;
            
            if (e.key === 'ArrowLeft') {
                this.previousImage();
            } else if (e.key === 'ArrowRight') {
                this.nextImage();
            }
        });
    }
    
    setupTouchEvents() {
        let startX = 0;
        let startY = 0;
        let isSwipe = false;
        
        this.modal.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isSwipe = false;
        });
        
        this.modal.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;
            
            const currentX = e.touches[0].clientX;
            const currentY = e.touches[0].clientY;
            
            const diffX = Math.abs(currentX - startX);
            const diffY = Math.abs(currentY - startY);
            
            // Horizontal swipe
            if (diffX > diffY && diffX > 50) {
                isSwipe = true;
                e.preventDefault(); // Prevent scrolling
            }
        });
        
        this.modal.addEventListener('touchend', (e) => {
            if (!isSwipe || !startX) return;
            
            const endX = e.changedTouches[0].clientX;
            const diffX = startX - endX;
            
            if (Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // Swipe left - next image
                    this.nextImage();
                } else {
                    // Swipe right - previous image
                    this.previousImage();
                }
            }
            
            startX = 0;
            startY = 0;
            isSwipe = false;
        });
    }
    
    open(imageId, filteredImages = null) {
        // Set filtered images if provided
        if (filteredImages) {
            this.filteredImages = filteredImages;
        }
        
        // Find image index
        this.currentImageIndex = this.filteredImages.findIndex(img => img.id == imageId);
        if (this.currentImageIndex === -1) {
            console.error('Image not found:', imageId);
            return;
        }
        
        // Show modal
        this.modal.classList.add('active');
        this.isOpen = true;
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Load image content
        this.loadImageContent();
        
        // Add entering animation
        this.modal.classList.add('entering');
        setTimeout(() => {
            this.modal.classList.remove('entering');
        }, 300);
    }
    
    close() {
        if (!this.isOpen) return;
        
        // Add leaving animation
        this.modal.classList.add('leaving');
        
        setTimeout(() => {
            this.modal.classList.remove('active', 'leaving');
            this.isOpen = false;
            
            // Restore body scroll
            document.body.style.overflow = '';
            
            // Clear content
            this.clearContent();
        }, 300);
    }
    
    loadImageContent() {
        const image = this.filteredImages[this.currentImageIndex];
        if (!image) return;
        
        // Update title
        document.getElementById('mobileModalTitle').textContent = image.title;
        
        // Show loading
        this.showLoading();
        
        // Create content
        setTimeout(() => {
            this.createImageContent(image);
        }, 100);
    }
    
    showLoading() {
        const content = document.getElementById('mobileModalContent');
        content.innerHTML = `
            <div class="mobile-modal-loading">
                <div class="mobile-modal-spinner"></div>
                <p class="mobile-modal-loading-text">Loading image...</p>
            </div>
        `;
    }
    
    createImageContent(image) {
        const content = document.getElementById('mobileModalContent');
        
        const imageHTML = `
            <div class="mobile-modal-image-container">
                <img src="${image.url}" alt="${image.title}" class="mobile-modal-image" onload="this.style.opacity='1'">
                
                ${this.filteredImages.length > 1 ? `
                    <button class="mobile-image-nav prev" onclick="window.mobileImageModal.previousImage()">
                        <i data-lucide="chevron-left" class="mobile-image-nav-icon"></i>
                    </button>
                    <button class="mobile-image-nav next" onclick="window.mobileImageModal.nextImage()">
                        <i data-lucide="chevron-right" class="mobile-image-nav-icon"></i>
                    </button>
                ` : ''}
                
                <div class="mobile-swipe-indicator">
                    <i data-lucide="move" class="mobile-swipe-icon"></i>
                    Swipe to navigate
                </div>
            </div>
            
            <div class="mobile-image-info">
                <div class="mobile-image-info-header">
                    <div class="mobile-image-details">
                        <h3 class="mobile-image-info-title">${image.title}</h3>
                        <p class="mobile-image-info-category">${image.category}</p>
                        ${image.description ? `<p class="mobile-image-info-description">${image.description}</p>` : ''}
                    </div>
                </div>
                
                ${this.createImageMetadata(image)}
                
                <div class="mobile-order-section">
                    <div class="mobile-order-header">
                        <h3 class="mobile-order-title">Order This Print</h3>
                        <p class="mobile-order-subtitle">Choose your preferred print type and size</p>
                    </div>
                    
                    ${this.createProductSelection(image)}
                    ${this.createOrderSummary()}
                    ${this.createOrderActions(image)}
                </div>
            </div>
        `;
        
        content.innerHTML = imageHTML;
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Setup product selection
        this.setupProductSelection();
    }
    
    createImageMetadata(image) {
        // This would be populated with actual EXIF data
        return `
            <div class="mobile-image-metadata">
                <div class="mobile-metadata-item">
                    <span class="mobile-metadata-label">Dimensions</span>
                    <span class="mobile-metadata-value">${image.width || 'N/A'} × ${image.height || 'N/A'}</span>
                </div>
                <div class="mobile-metadata-item">
                    <span class="mobile-metadata-label">Category</span>
                    <span class="mobile-metadata-value">${image.category}</span>
                </div>
                <div class="mobile-metadata-item">
                    <span class="mobile-metadata-label">Format</span>
                    <span class="mobile-metadata-value">High Resolution</span>
                </div>
                <div class="mobile-metadata-item">
                    <span class="mobile-metadata-label">Quality</span>
                    <span class="mobile-metadata-value">Professional</span>
                </div>
            </div>
        `;
    }
    
    createProductSelection(image) {
        const products = [
            {
                id: 'canvas-12x12',
                name: 'Canvas Print',
                size: '12" × 12"',
                details: '0.75" Gallery Wrap',
                price: 36.62
            },
            {
                id: 'metal-12x12',
                name: 'Metal Print',
                size: '12" × 12"',
                details: 'Aluminum with Glossy Finish',
                price: 37.98
            },
            {
                id: 'paper-12x12',
                name: 'Fine Art Paper',
                size: '12" × 12"',
                details: 'Premium Matte Finish',
                price: 25.98
            },
            {
                id: 'canvas-16x20',
                name: 'Canvas Print',
                size: '16" × 20"',
                details: '1.25" Gallery Wrap',
                price: 45.12
            }
        ];
        
        return `
            <div class="mobile-product-selection">
                <div class="mobile-product-grid" id="mobileProductGrid">
                    ${products.map(product => `
                        <div class="mobile-product-card" data-product-id="${product.id}" data-price="${product.price}">
                            <div class="mobile-product-header">
                                <span class="mobile-product-name">${product.name}</span>
                                <span class="mobile-product-price">$${product.price.toFixed(2)}</span>
                            </div>
                            <div class="mobile-product-details">
                                <span class="mobile-product-size">${product.size}</span><br>
                                ${product.details}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    createOrderSummary() {
        return `
            <div class="mobile-order-summary" id="mobileOrderSummary" style="display: none;">
                <h4 class="mobile-summary-title">Order Summary</h4>
                <div class="mobile-summary-item">
                    <span class="mobile-summary-label">Product:</span>
                    <span class="mobile-summary-value" id="summaryProduct">-</span>
                </div>
                <div class="mobile-summary-item">
                    <span class="mobile-summary-label">Size:</span>
                    <span class="mobile-summary-value" id="summarySize">-</span>
                </div>
                <div class="mobile-summary-item">
                    <span class="mobile-summary-label">Subtotal:</span>
                    <span class="mobile-summary-value" id="summarySubtotal">$0.00</span>
                </div>
                <div class="mobile-summary-item">
                    <span class="mobile-summary-label">Total:</span>
                    <span class="mobile-summary-total" id="summaryTotal">$0.00</span>
                </div>
            </div>
        `;
    }
    
    createOrderActions(image) {
        return `
            <div class="mobile-order-actions">
                <button class="mobile-order-btn" id="mobileOrderNowBtn" disabled>
                    <i data-lucide="shopping-cart" class="mobile-order-btn-icon"></i>
                    Order Now
                </button>
                <button class="mobile-order-btn mobile-order-btn-secondary" onclick="window.mobileImageModal.shareImage('${image.id}')">
                    <i data-lucide="share-2" class="mobile-order-btn-icon"></i>
                    Share
                </button>
            </div>
        `;
    }
    
    setupProductSelection() {
        const productCards = document.querySelectorAll('.mobile-product-card');
        const orderSummary = document.getElementById('mobileOrderSummary');
        const orderBtn = document.getElementById('mobileOrderNowBtn');
        
        productCards.forEach(card => {
            card.addEventListener('click', () => {
                // Remove previous selection
                productCards.forEach(c => c.classList.remove('selected'));
                
                // Select current card
                card.classList.add('selected');
                
                // Get product data
                const productId = card.dataset.productId;
                const price = parseFloat(card.dataset.price);
                const productName = card.querySelector('.mobile-product-name').textContent;
                const productSize = card.querySelector('.mobile-product-size').textContent;
                
                // Update selected product
                this.selectedProduct = {
                    id: productId,
                    name: productName,
                    size: productSize,
                    price: price
                };
                
                // Update summary
                this.updateOrderSummary();
                
                // Show summary and enable order button
                orderSummary.style.display = 'block';
                orderBtn.disabled = false;
                
                // Setup order button
                orderBtn.onclick = () => this.proceedToOrder();
            });
        });
    }
    
    updateOrderSummary() {
        if (!this.selectedProduct) return;
        
        document.getElementById('summaryProduct').textContent = this.selectedProduct.name;
        document.getElementById('summarySize').textContent = this.selectedProduct.size;
        document.getElementById('summarySubtotal').textContent = `$${this.selectedProduct.price.toFixed(2)}`;
        document.getElementById('summaryTotal').textContent = `$${this.selectedProduct.price.toFixed(2)}`;
    }
    
    proceedToOrder() {
        if (!this.selectedProduct) return;
        
        const image = this.filteredImages[this.currentImageIndex];
        
        // Create order URL with parameters
        const orderParams = new URLSearchParams({
            image: image.filename,
            title: image.title,
            product: this.selectedProduct.id,
            price: this.selectedProduct.price
        });
        
        const orderUrl = `/test_order_form?${orderParams.toString()}`;
        
        // Close modal and redirect
        this.close();
        
        // Open order form
        window.open(orderUrl, '_blank');
    }
    
    nextImage() {
        if (this.currentImageIndex < this.filteredImages.length - 1) {
            this.currentImageIndex++;
            this.loadImageContent();
        }
    }
    
    previousImage() {
        if (this.currentImageIndex > 0) {
            this.currentImageIndex--;
            this.loadImageContent();
        }
    }
    
    shareImage(imageId) {
        const image = this.filteredImages.find(img => img.id == imageId);
        if (!image) return;
        
        if (navigator.share) {
            // Use native sharing if available
            navigator.share({
                title: `${image.title} - Fifth Element Photography`,
                text: `Check out this amazing photograph: ${image.title}`,
                url: window.location.href
            }).catch(console.error);
        } else {
            // Fallback to copying URL
            const url = `${window.location.origin}${window.location.pathname}#image-${image.id}`;
            
            if (navigator.clipboard) {
                navigator.clipboard.writeText(url).then(() => {
                    this.showToast('Link copied to clipboard!');
                });
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = url;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                this.showToast('Link copied to clipboard!');
            }
        }
    }
    
    showToast(message) {
        // Create and show a toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 0.9rem;
            z-index: 3000;
            backdrop-filter: blur(4px);
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
    
    clearContent() {
        const content = document.getElementById('mobileModalContent');
        if (content) {
            content.innerHTML = '';
        }
        this.selectedProduct = null;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mobileImageModal = new MobileImageModal();
    
    // Update the existing mobile gallery to use the new modal
    if (window.mobileGallery) {
        window.mobileGallery.openImageModal = (imageId) => {
            window.mobileImageModal.open(imageId, window.mobileGallery.filteredImages);
        };
    }
});

// Export for global access
window.MobileImageModal = MobileImageModal;
