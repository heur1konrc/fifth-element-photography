/**
 * Enhanced Lumaprints Ordering System - Phase 1
 * Integrates with Phase 1 product data and handles image URL from modal
 */

class EnhancedOrderingSystem {
    constructor() {
        this.currentImage = null;
        this.currentImageName = null;
        this.selectedProductId = null;
        this.selectedProduct = null;
        this.quantity = 1;
        this.orderDetails = {
            totalPrice: 0,
            shipping: 0,
            tax: 0
        };
        this.init();
    }

    init() {
        this.loadProductData();
        this.populateProductDropdown();
        this.setupEventListeners();
        this.checkForImageParameter();
    }

    loadProductData() {
        // Load Phase 1 product data
        if (typeof getAllProducts === 'function') {
            this.allProducts = getAllProducts();
            console.log('Product data loaded:', this.allProducts.length, 'products');
        } else {
            console.error('Product data not loaded. Make sure product_data_phase1.js is included.');
            this.allProducts = [];
            // Try again after a short delay
            setTimeout(() => {
                if (typeof getAllProducts === 'function') {
                    this.allProducts = getAllProducts();
                    this.populateProductDropdown();
                    console.log('Product data loaded on retry:', this.allProducts.length, 'products');
                }
            }, 100);
        }
    }

    checkForImageParameter() {
        // Check if image URL was passed from modal
        const urlParams = new URLSearchParams(window.location.search);
        const imageUrl = urlParams.get('image');
        const imageName = urlParams.get('name');
        
        console.log('Checking for image parameter:', imageUrl);
        
        if (imageUrl) {
            console.log('Setting current image:', imageUrl);
            this.setCurrentImage(imageUrl, imageName);
        } else {
            console.log('No image parameter found in URL');
            // Show a message that no image was selected
            const previewContainer = document.getElementById('imagePreview');
            if (previewContainer) {
                previewContainer.innerHTML = '<p>No image selected. Please select an image first.</p>';
            }
        }
    }

    setCurrentImage(imageUrl, imageName = null) {
        this.currentImage = imageUrl;
        this.currentImageName = imageName || this.extractImageNameFromUrl(imageUrl);
        this.displayImagePreview();
    }

    extractImageNameFromUrl(url) {
        return url.split('/').pop().split('?')[0];
    }

    displayImagePreview() {
        console.log('Displaying image preview for:', this.currentImage);
        const previewContainer = document.getElementById('imagePreview');
        console.log('Preview container found:', !!previewContainer);
        
        if (previewContainer && this.currentImage) {
            previewContainer.innerHTML = `
                <div class="image-preview-card">
                    <img src="${this.currentImage}" alt="Selected Image" style="max-width: 200px; max-height: 200px; border-radius: 8px;">
                    <div class="image-info">
                        <h4>Selected Image</h4>
                        <p><strong>File:</strong> ${this.currentImageName}</p>
                        <p class="image-specs" id="imageSpecs">Loading image specifications...</p>
                    </div>
                </div>
            `;
            this.loadImageSpecs();
        }
    }

    loadImageSpecs() {
        if (!this.currentImage) return;
        
        const img = new Image();
        img.onload = () => {
            const specsElement = document.getElementById('imageSpecs');
            if (specsElement) {
                specsElement.innerHTML = `
                    <strong>Size:</strong> ${img.width} × ${img.height} pixels<br>
                    <strong>Aspect Ratio:</strong> ${this.calculateAspectRatio(img.width, img.height)}
                `;
            }
        };
        img.src = this.currentImage;
    }

    calculateAspectRatio(width, height) {
        const gcd = (a, b) => b === 0 ? a : gcd(b, a % b);
        const divisor = gcd(width, height);
        return `${width / divisor}:${height / divisor}`;
    }

    setupEventListeners() {
        // Product selection
        document.addEventListener('change', (e) => {
            if (e.target.id === 'productSelect') {
                this.selectProduct(e.target.value);
            }
        });

        // Quantity change
        document.addEventListener('change', (e) => {
            if (e.target.id === 'quantityInput') {
                this.quantity = parseInt(e.target.value) || 1;
                this.updateOrderSummary();
            }
        });

        // Form submission
        const orderForm = document.getElementById('orderForm');
        if (orderForm) {
            orderForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.processPayment();
            });
        }

        // Order Print button (from modal)
        const orderPrintBtn = document.getElementById('orderPrintBtn');
        if (orderPrintBtn) {
            orderPrintBtn.addEventListener('click', () => this.showOrderForm());
        }
    }

    populateProductDropdown() {
        const productSelect = document.getElementById('productSelect');
        if (!productSelect) {
            console.error('Product select element not found');
            return;
        }
        
        if (!this.allProducts || this.allProducts.length === 0) {
            console.error('No products available to populate dropdown');
            return;
        }

        console.log('Populating dropdown with', this.allProducts.length, 'products');

        // Clear existing options
        productSelect.innerHTML = '<option value="">Select a product...</option>';

        // Group products by type for better organization
        const groupedProducts = this.groupProductsByType();

        Object.keys(groupedProducts).forEach(type => {
            const optgroup = document.createElement('optgroup');
            optgroup.label = this.formatProductType(type);

            groupedProducts[type].forEach(product => {
                const option = document.createElement('option');
                option.value = product.id;
                option.textContent = `${product.title} - $${product.customer_price.toFixed(2)}`;
                optgroup.appendChild(option);
            });

            productSelect.appendChild(optgroup);
        });
    }

    groupProductsByType() {
        const grouped = {};
        this.allProducts.forEach(product => {
            const type = product.type;
            if (!grouped[type]) {
                grouped[type] = [];
            }
            grouped[type].push(product);
        });
        return grouped;
    }

    formatProductType(type) {
        return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    selectProduct(productId) {
        if (!productId) {
            this.selectedProductId = null;
            this.selectedProduct = null;
            this.updateOrderSummary();
            return;
        }

        this.selectedProductId = productId;
        this.selectedProduct = getProductById(productId);
        
        if (this.selectedProduct) {
            this.displayProductDetails();
            this.updateOrderSummary();
        }
    }

    displayProductDetails() {
        const detailsContainer = document.getElementById('productDetails');
        if (!detailsContainer || !this.selectedProduct) return;

        detailsContainer.innerHTML = `
            <div class="product-details-card">
                <h4>${this.selectedProduct.title}</h4>
                <div class="product-specs">
                    <p><strong>Type:</strong> ${this.formatProductType(this.selectedProduct.type)}</p>
                    <p><strong>Thickness:</strong> ${this.selectedProduct.thickness}</p>
                    <p><strong>Size:</strong> ${this.selectedProduct.width}\" × ${this.selectedProduct.height}\"</p>
                    ${this.selectedProduct.frame_style ? `<p><strong>Frame:</strong> ${this.selectedProduct.frame_style}</p>` : ''}
                    <p><strong>Price:</strong> $${this.selectedProduct.customer_price.toFixed(2)}</p>
                </div>
            </div>
        `;
    }

    updateOrderSummary() {
        const summaryContainer = document.getElementById('orderSummary');
        if (!summaryContainer) return;

        if (!this.selectedProduct) {
            summaryContainer.innerHTML = '<p>Please select a product to see order summary.</p>';
            return;
        }

        const subtotal = this.selectedProduct.customer_price * this.quantity;
        const shipping = 0; // Free shipping for now
        const tax = 0; // No tax calculation for now
        const total = subtotal + shipping + tax;

        this.orderDetails = {
            totalPrice: total,
            shipping: shipping,
            tax: tax
        };

        summaryContainer.innerHTML = `
            <div class="order-summary-card">
                <h4>Order Summary</h4>
                <div class="summary-line">
                    <span>${this.selectedProduct.title}</span>
                    <span>$${this.selectedProduct.customer_price.toFixed(2)}</span>
                </div>
                <div class="summary-line">
                    <span>Quantity: ${this.quantity}</span>
                    <span></span>
                </div>
                <div class="summary-line subtotal">
                    <span>Subtotal:</span>
                    <span>$${subtotal.toFixed(2)}</span>
                </div>
                <div class="summary-line">
                    <span>Shipping:</span>
                    <span>$${shipping.toFixed(2)}</span>
                </div>
                <div class="summary-line">
                    <span>Tax:</span>
                    <span>$${tax.toFixed(2)}</span>
                </div>
                <div class="summary-line total">
                    <span><strong>Total:</strong></span>
                    <span><strong>$${total.toFixed(2)}</strong></span>
                </div>
            </div>
        `;

        // Update submit button
        const submitBtn = document.getElementById('submitOrderBtn');
        if (submitBtn) {
            submitBtn.textContent = `Submit Order - $${total.toFixed(2)}`;
            submitBtn.disabled = false;
        }
    }

    showOrderForm() {
        // Hide modal image view, show order form
        const modal = document.getElementById('imageModal');
        const imageView = document.querySelector('.modal-image-view');
        const orderView = document.querySelector('.modal-order-view');

        if (imageView) imageView.style.display = 'none';
        if (orderView) {
            orderView.style.display = 'block';
            this.populateProductDropdown();
        }
    }

    showMainView() {
        // Show modal image view, hide order form
        const imageView = document.querySelector('.modal-image-view');
        const orderView = document.querySelector('.modal-order-view');

        if (orderView) orderView.style.display = 'none';
        if (imageView) imageView.style.display = 'block';
    }

    async processPayment() {
        const form = document.getElementById('orderForm');
        if (!form || !form.checkValidity()) {
            if (form) form.reportValidity();
            return;
        }

        if (!this.selectedProduct || !this.currentImage) {
            alert('Please select a product and ensure an image is selected.');
            return;
        }

        const formData = new FormData(form);
        const submitBtn = document.getElementById('submitOrderBtn');
        
        if (submitBtn) {
            submitBtn.textContent = 'Submitting...';
            submitBtn.disabled = true;
        }

        try {
            // Create FormData to send to the OrderDesk endpoint
            const orderDeskFormData = new FormData();

            // Append customer and shipping info from the form
            orderDeskFormData.append('email', formData.get('email'));
            orderDeskFormData.append('first_name', formData.get('firstName'));
            orderDeskFormData.append('last_name', formData.get('lastName'));
            orderDeskFormData.append('address1', formData.get('address'));
            orderDeskFormData.append('city', formData.get('city'));
            orderDeskFormData.append('state', formData.get('state'));
            orderDeskFormData.append('postal_code', formData.get('zipCode'));
            orderDeskFormData.append('country', 'US');
            orderDeskFormData.append('phone', formData.get('phone'));

            // Append product info using Phase 1 data structure
            orderDeskFormData.append('product_sku', this.selectedProduct.subcategoryId);
            orderDeskFormData.append('lumaprints_options', this.selectedProduct.lumaprints_options);
            orderDeskFormData.append('product_price', this.selectedProduct.customer_price);
            orderDeskFormData.append('print_url', this.currentImage);
            orderDeskFormData.append('print_width', this.selectedProduct.width);
            orderDeskFormData.append('print_height', this.selectedProduct.height);
            orderDeskFormData.append('product_type', this.selectedProduct.title);

            // Submit order to the working OrderDesk endpoint
            const response = await fetch('/test_order_submit', {
                method: 'POST',
                body: orderDeskFormData
            });

            const result = await response.json();

            if (result.success || result.status === 'success') {
                alert(`Order submitted successfully to OrderDesk! Order ID: ${result.order_id || result.orderdesk_order_id}`);
                
                // Close modal and reset
                const modal = document.getElementById('imageModal');
                if (modal) modal.style.display = 'none';
                this.resetForm();
            } else {
                alert(`Error submitting order: ${result.message || result.error || 'Unknown error'}`);
            }

        } catch (error) {
            console.error('Order submission error:', error);
            alert('An error occurred while submitting the order. Please try again.');
        } finally {
            // Re-enable button
            if (submitBtn) {
                submitBtn.textContent = `Submit Order - $${this.orderDetails.totalPrice.toFixed(2)}`;
                submitBtn.disabled = false;
            }
        }
    }

    resetForm() {
        this.selectedProductId = null;
        this.selectedProduct = null;
        this.quantity = 1;
        this.orderDetails = { totalPrice: 0, shipping: 0, tax: 0 };
        
        const form = document.getElementById('orderForm');
        if (form) form.reset();
        
        const productSelect = document.getElementById('productSelect');
        if (productSelect) productSelect.value = '';
        
        this.updateOrderSummary();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedOrdering = new EnhancedOrderingSystem();
});
