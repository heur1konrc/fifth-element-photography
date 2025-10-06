/**
 * Lumaprints Inline Print Ordering System
 * Handles ordering within the same modal window
 */

class LumaprintsInlineOrdering {
    constructor() {
        this.currentImage = null;
        this.currentPricing = null;
        this.selectedProduct = null;
        this.selectedSize = null;
        this.quantity = 1;
        this.orderDetails = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSizeOptions();
    }

    setupEventListeners() {
        // Order Print button
        const orderPrintBtn = document.getElementById('orderPrintBtn');
        if (orderPrintBtn) {
            orderPrintBtn.addEventListener('click', () => this.showPrintOrderView());
        }

        // Back buttons
        const backToImageBtn = document.getElementById('backToImageBtn');
        if (backToImageBtn) {
            backToImageBtn.addEventListener('click', () => this.showMainView());
        }

        const backToPrintOrderBtn = document.getElementById('backToPrintOrderBtn');
        if (backToPrintOrderBtn) {
            backToPrintOrderBtn.addEventListener('click', () => this.showPrintOrderView());
        }

        // Product selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.product-category')) {
                this.selectProduct(e.target.closest('.product-category'));
            }
        });

        // Size selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.size-option')) {
                this.selectSize(e.target.closest('.size-option'));
            }
        });

        // Quantity controls
        const qtyMinus = document.getElementById('qtyMinus');
        const qtyPlus = document.getElementById('qtyPlus');
        const quantityInput = document.getElementById('quantity');

        if (qtyMinus) {
            qtyMinus.addEventListener('click', () => this.changeQuantity(-1));
        }
        if (qtyPlus) {
            qtyPlus.addEventListener('click', () => this.changeQuantity(1));
        }
        if (quantityInput) {
            quantityInput.addEventListener('change', (e) => {
                this.quantity = Math.max(1, Math.min(10, parseInt(e.target.value) || 1));
                this.updatePricing();
            });
        }

        // Continue to order
        const continueOrderBtn = document.getElementById('continueOrderBtn');
        if (continueOrderBtn) {
            continueOrderBtn.addEventListener('click', () => this.showOrderFormView());
        }

        // PayPal payment
        const paypalBtn = document.getElementById('paypalBtn');
        if (paypalBtn) {
            paypalBtn.addEventListener('click', () => this.processPayment());
        }
    }

    showPrintOrderView() {
        // Try to get current image from modal first
        const modalImage = document.getElementById('modalImage');
        const modalTitle = document.getElementById('modalTitle');
        
        let imageSource = null;
        let imageTitle = 'Selected Image';
        
        // Check if we're in a modal context with a valid image
        if (modalImage && modalImage.src && modalImage.src !== window.location.href) {
            imageSource = modalImage.src;
            imageTitle = modalTitle ? modalTitle.textContent : 'Selected Image';
        } else {
            // Try to find the featured image or any visible image
            const featuredImg = document.querySelector('.hero-image img, .featured-image img, img[alt*="featured"], img[src*="IMG_5555"]');
            if (featuredImg && featuredImg.src) {
                imageSource = featuredImg.src;
                imageTitle = featuredImg.alt || 'Featured Image';
            } else {
                // Fallback: try to find any image on the page
                const anyImg = document.querySelector('img[src*="/static/"], img[src*="/images/"]');
                if (anyImg && anyImg.src) {
                    imageSource = anyImg.src;
                    imageTitle = anyImg.alt || 'Selected Image';
                }
            }
        }
        
        if (imageSource) {
            this.currentImage = imageSource;
            
            // Update preview image and title
            const orderPreviewImage = document.getElementById('orderPreviewImage');
            const orderImageTitle = document.getElementById('orderImageTitle');
            
            if (orderPreviewImage) orderPreviewImage.src = this.currentImage;
            if (orderImageTitle) orderImageTitle.textContent = imageTitle;
            
            // Ensure modal is visible and show print order view
            const modal = document.getElementById('imageModal');
            if (modal) {
                modal.style.display = 'flex';
            }
            
            // Show print order view
            this.showView('modalPrintOrder');
            
            // Reset selections
            this.resetSelections();
            
            console.log('Print order view shown for image:', this.currentImage);
        } else {
            console.error('No valid image found to order');
            alert('No image available for ordering. Please select an image first.');
        }
    }

    showMainView() {
        this.showView('modalMainView');
    }

    showOrderFormView() {
        if (!this.currentPricing) return;
        
        // Prepare order details
        this.prepareOrderSummary();
        
        // Show order form view
        this.showView('modalOrderForm');
    }

    showView(viewId) {
        // Hide all views
        const views = ['modalMainView', 'modalPrintOrder', 'modalOrderForm'];
        views.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });
        
        // Show selected view
        const targetView = document.getElementById(viewId);
        if (targetView) {
            targetView.style.display = 'block';
        }
    }

    loadSizeOptions() {
        const sizeOptions = document.getElementById('sizeOptions');
        if (!sizeOptions) return;

        const sizes = [
            { width: 8, height: 10, name: '8" × 10"' },
            { width: 11, height: 14, name: '11" × 14"' },
            { width: 12, height: 16, name: '12" × 16"' },
            { width: 16, height: 20, name: '16" × 20"' },
            { width: 18, height: 24, name: '18" × 24"' },
            { width: 20, height: 30, name: '20" × 30"' }
        ];

        sizeOptions.innerHTML = sizes.map(size => `
            <div class="size-option" data-width="${size.width}" data-height="${size.height}">
                <div class="size-name">${size.name}</div>
                <div class="size-dimensions">${size.width}" × ${size.height}"</div>
            </div>
        `).join('');
    }

    selectProduct(productElement) {
        // Remove previous selection
        document.querySelectorAll('.product-category').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Add selection to clicked element
        productElement.classList.add('selected');
        
        // Store selected product
        this.selectedProduct = productElement.dataset.product;
        
        // Update pricing
        this.updatePricing();
    }

    selectSize(sizeElement) {
        // Remove previous selection
        document.querySelectorAll('.size-option').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Add selection to clicked element
        sizeElement.classList.add('selected');
        
        // Store selected size
        this.selectedSize = {
            width: parseInt(sizeElement.dataset.width),
            height: parseInt(sizeElement.dataset.height),
            name: sizeElement.querySelector('.size-name').textContent
        };
        
        // Update pricing
        this.updatePricing();
    }

    changeQuantity(delta) {
        this.quantity = Math.max(1, Math.min(10, this.quantity + delta));
        const quantityInput = document.getElementById('quantity');
        if (quantityInput) {
            quantityInput.value = this.quantity;
        }
        this.updatePricing();
    }

    async updatePricing() {
        const priceDisplay = document.getElementById('priceDisplay');
        const continueBtn = document.getElementById('continueOrderBtn');
        
        if (!this.selectedProduct || !this.selectedSize) {
            if (priceDisplay) {
                priceDisplay.innerHTML = `
                    <div class="price-breakdown">
                        <div class="price-line">
                            <span>Select product and size to see pricing</span>
                        </div>
                    </div>
                `;
            }
            if (continueBtn) continueBtn.disabled = true;
            return;
        }

        try {
            if (priceDisplay) {
                priceDisplay.innerHTML = `
                    <div class="price-breakdown">
                        <div class="price-line">
                            <span>Calculating pricing...</span>
                        </div>
                    </div>
                `;
            }

            const response = await fetch('/api/lumaprints/pricing', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    subcategoryId: parseInt(this.selectedProduct),
                    width: this.selectedSize.width,
                    height: this.selectedSize.height,
                    quantity: this.quantity
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentPricing = data.pricing;
                const totalPrice = data.pricing.retail_price * this.quantity;

                if (priceDisplay) {
                    priceDisplay.innerHTML = `
                        <div class="price-breakdown">
                            <div class="price-line">
                                <span>Price per item:</span>
                                <span class="price">${data.pricing.formatted_price}</span>
                            </div>
                            ${this.quantity > 1 ? `
                            <div class="price-line">
                                <span>Quantity:</span>
                                <span>${this.quantity}</span>
                            </div>
                            <div class="price-line total">
                                <span>Total:</span>
                                <span class="price">$${totalPrice.toFixed(2)}</span>
                            </div>
                            ` : ''}
                        </div>
                    `;
                }

                if (continueBtn) continueBtn.disabled = false;
            } else {
                if (priceDisplay) {
                    priceDisplay.innerHTML = `
                        <div class="price-breakdown">
                            <div class="price-line">
                                <span style="color: #dc3545;">Error: ${data.error}</span>
                            </div>
                        </div>
                    `;
                }
                if (continueBtn) continueBtn.disabled = true;
            }

        } catch (error) {
            console.error('Pricing error:', error);
            if (priceDisplay) {
                priceDisplay.innerHTML = `
                    <div class="price-breakdown">
                        <div class="price-line">
                            <span style="color: #dc3545;">Error calculating pricing</span>
                        </div>
                    </div>
                `;
            }
            if (continueBtn) continueBtn.disabled = true;
        }
    }

    prepareOrderSummary() {
        const orderSummary = document.getElementById('orderSummary');
        const paymentTotal = document.getElementById('paymentTotal');
        
        if (!this.currentPricing || !this.selectedSize) return;

        const totalPrice = this.currentPricing.retail_price * this.quantity;
        const productName = document.querySelector('.product-category.selected h5')?.textContent || 'Selected Product';

        this.orderDetails = {
            image: this.currentImage,
            productName: productName,
            sizeName: this.selectedSize.name,
            quantity: this.quantity,
            pricing: this.currentPricing,
            totalPrice: totalPrice
        };

        if (orderSummary) {
            orderSummary.innerHTML = `
                <h4>Order Summary</h4>
                <div class="summary-item">
                    <img src="${this.currentImage}" alt="Print Preview" class="summary-image">
                    <div class="summary-details">
                        <div><strong>${productName}</strong></div>
                        <div>Size: ${this.selectedSize.name}</div>
                        <div>Quantity: ${this.quantity}</div>
                        <div class="price"><strong>Total: $${totalPrice.toFixed(2)}</strong></div>
                    </div>
                </div>
            `;
        }

        if (paymentTotal) {
            paymentTotal.innerHTML = `<strong>Total: $${totalPrice.toFixed(2)}</strong>`;
        }

        // Update PayPal button
        const paypalBtn = document.getElementById('paypalBtn');
        if (paypalBtn) {
            paypalBtn.textContent = `Pay with PayPal - $${totalPrice.toFixed(2)}`;
        }
    }

    async processPayment() {
        const form = document.getElementById('orderForm');
        if (!form || !form.checkValidity()) {
            if (form) form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const paypalBtn = document.getElementById('paypalBtn');
        
        if (paypalBtn) {
            paypalBtn.textContent = 'Processing...';
            paypalBtn.disabled = true;
        }

        try {
            // Prepare order data to match backend API
            const orderData = {
                subcategoryId: parseInt(this.selectedProduct),
                width: this.selectedSize.width,
                height: this.selectedSize.height,
                quantity: this.quantity,
                imageUrl: this.currentImage,
                price: this.orderDetails.totalPrice,
                shipping: {
                    firstName: formData.get('firstName'),
                    lastName: formData.get('lastName'),
                    addressLine1: formData.get('address'),
                    city: formData.get('city'),
                    state: formData.get('state'),
                    zipCode: formData.get('zipCode'),
                    country: 'US',
                    phone: formData.get('phone')
                },
                payment: {
                    method: 'paypal',
                    email: formData.get('email'),
                    amount: this.orderDetails.totalPrice
                },
                options: []
            };

            // Submit order to backend
            const response = await fetch('/api/lumaprints/submit-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(orderData)
            });

            const result = await response.json();

            if (result.success) {
                alert('Order submitted successfully! You will receive a confirmation email shortly.');
                
                // Close modal
                const modal = document.getElementById('imageModal');
                if (modal) modal.style.display = 'none';
                
                // Reset everything
                this.resetSelections();
                this.showMainView();
            } else {
                alert(`Error submitting order: ${result.error}`);
            }

        } catch (error) {
            console.error('Order submission error:', error);
            alert('Error submitting order. Please try again.');
        } finally {
            // Re-enable button
            if (paypalBtn) {
                paypalBtn.textContent = `Pay with PayPal - $${this.orderDetails.totalPrice.toFixed(2)}`;
                paypalBtn.disabled = false;
            }
        }
    }

    resetSelections() {
        this.selectedProduct = null;
        this.selectedSize = null;
        this.quantity = 1;
        this.currentPricing = null;
        this.orderDetails = null;

        // Reset UI
        document.querySelectorAll('.product-category').forEach(el => {
            el.classList.remove('selected');
        });
        document.querySelectorAll('.size-option').forEach(el => {
            el.classList.remove('selected');
        });

        const quantityInput = document.getElementById('quantity');
        if (quantityInput) quantityInput.value = '1';

        const priceDisplay = document.getElementById('priceDisplay');
        if (priceDisplay) {
            priceDisplay.innerHTML = `
                <div class="price-breakdown">
                    <div class="price-line">
                        <span>Select product and size to see pricing</span>
                    </div>
                </div>
            `;
        }

        const continueBtn = document.getElementById('continueOrderBtn');
        if (continueBtn) continueBtn.disabled = true;

        // Clear form
        const form = document.getElementById('orderForm');
        if (form) form.reset();
    }
}

// Initialize the inline ordering system
const lumaprintsInlineOrdering = new LumaprintsInlineOrdering();

// Export for use in other scripts
window.lumaprintsInlineOrdering = lumaprintsInlineOrdering;
