/**
 * Dynamic Lumaprints Ordering System
 * Fetches products and pricing from database instead of hardcoded data
 */

class DynamicOrderingSystem {
    constructor() {
        this.currentImage = null;
        this.currentImageName = null;
        this.selectedProductId = null;
        this.selectedProduct = null;
        this.selectedVariant = null;
        this.quantity = 1;
        this.allProducts = [];
        this.orderDetails = {
            totalPrice: 0,
            shipping: 0,
            tax: 0
        };
        this.init();
    }

    async init() {
        await this.loadProductData();
        this.populateProductDropdown();
        this.setupEventListeners();
        this.checkForImageParameter();
    }

    async loadProductData() {
        try {
            console.log('Loading products from database...');
            const response = await fetch('/api/products');
            const data = await response.json();
            
            if (data.success) {
                this.allProducts = data.products;
                console.log('Loaded', this.allProducts.length, 'products from database');
            } else {
                console.error('Failed to load products:', data.message);
                this.allProducts = [];
            }
        } catch (error) {
            console.error('Error loading product data:', error);
            this.allProducts = [];
        }
    }

    checkForImageParameter() {
        const urlParams = new URLSearchParams(window.location.search);
        const imageUrl = urlParams.get('image');
        const imageName = urlParams.get('name');
        
        console.log('Checking for image parameter:', imageUrl);
        
        if (imageUrl) {
            console.log('Setting current image:', imageUrl);
            this.setCurrentImage(imageUrl, imageName);
        } else {
            console.log('No image parameter found in URL');
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

        // Variant selection
        document.addEventListener('change', (e) => {
            if (e.target.id === 'variantSelect') {
                this.selectVariant(e.target.value);
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
    }

    populateProductDropdown() {
        const productSelect = document.getElementById('productSelect');
        if (!productSelect) {
            console.error('Product select element not found');
            return;
        }
        
        if (!this.allProducts || this.allProducts.length === 0) {
            console.error('No products available to populate dropdown');
            productSelect.innerHTML = '<option value="">No products available</option>';
            return;
        }

        console.log('Populating dropdown with', this.allProducts.length, 'products');

        // Clear existing options
        productSelect.innerHTML = '<option value="">Select a product...</option>';

        // Group products by category for better organization
        const groupedProducts = this.groupProductsByCategory();

        Object.keys(groupedProducts).forEach(category => {
            const optgroup = document.createElement('optgroup');
            optgroup.label = category;

            groupedProducts[category].forEach(product => {
                const option = document.createElement('option');
                option.value = product.id;
                // Don't duplicate size if it's already in the product name
                const displayName = product.name.includes(product.size) ? 
                    product.name : `${product.name} ${product.size}`;
                option.textContent = `${displayName} - $${product.customer_price.toFixed(2)}`;
                optgroup.appendChild(option);
            });

            productSelect.appendChild(optgroup);
        });
    }

    groupProductsByCategory() {
        const grouped = {};
        this.allProducts.forEach(product => {
            const category = product.category_name;
            if (!grouped[category]) {
                grouped[category] = [];
            }
            grouped[category].push(product);
        });
        return grouped;
    }

    selectProduct(productId) {
        if (!productId) {
            this.selectedProductId = null;
            this.selectedProduct = null;
            this.selectedVariant = null;
            this.hideVariantSelection();
            this.updateOrderSummary();
            return;
        }

        this.selectedProductId = productId;
        this.selectedProduct = this.allProducts.find(p => p.id === productId);
        this.selectedVariant = null;
        
        if (this.selectedProduct) {
            this.displayProductDetails();
            this.handleVariantSelection();
            this.updateOrderSummary();
        }
    }

    handleVariantSelection() {
        if (this.selectedProduct && this.selectedProduct.has_variants) {
            this.showVariantSelection();
        } else {
            this.hideVariantSelection();
        }
    }

    showVariantSelection() {
        console.log('showVariantSelection called for product:', this.selectedProduct.name);
        console.log('Product has variants:', this.selectedProduct.has_variants);
        console.log('Variants array:', this.selectedProduct.variants);
        
        // Remove existing variant container first
        this.hideVariantSelection();
        
        const productDetails = document.getElementById('productDetails');
        if (!productDetails) {
            console.error('productDetails container not found');
            return;
        }
        
        if (!this.selectedProduct.variants || this.selectedProduct.variants.length === 0) {
            console.log('No variants available for this product');
            return;
        }

        // Create variant selection container
        const variantContainer = document.createElement('div');
        variantContainer.id = 'variantSelection';
        variantContainer.className = 'form-group';
        variantContainer.style.marginTop = '15px';
        variantContainer.style.padding = '15px';
        variantContainer.style.backgroundColor = '#f8f9fa';
        variantContainer.style.borderRadius = '8px';
        variantContainer.style.border = '1px solid #dee2e6';
        
        variantContainer.innerHTML = `
            <label for="variantSelect" style="font-weight: bold; margin-bottom: 8px; display: block;">Frame Type:</label>
            <select id="variantSelect" required style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ccc;">
                <option value="">Select frame type...</option>
                ${this.selectedProduct.variants.map(variant => 
                    `<option value="${variant.id}" ${variant.is_default ? 'selected' : ''}>
                        ${variant.description}
                    </option>`
                ).join('')}
            </select>
        `;
        
        productDetails.appendChild(variantContainer);
        console.log('Variant container added to productDetails');

        // Add event listener for variant selection
        const variantSelect = document.getElementById('variantSelect');
        if (variantSelect) {
            variantSelect.addEventListener('change', (e) => {
                this.selectVariant(e.target.value);
            });
        }

        // Auto-select default variant
        const defaultVariant = this.selectedProduct.variants.find(v => v.is_default);
        if (defaultVariant) {
            console.log('Auto-selecting default variant:', defaultVariant.description);
            this.selectVariant(defaultVariant.id);
        }
    }
    }

    hideVariantSelection() {
        const variantContainer = document.getElementById('variantSelection');
        if (variantContainer) {
            variantContainer.remove();
        }
    }

    selectVariant(variantId) {
        if (this.selectedProduct && this.selectedProduct.variants) {
            this.selectedVariant = this.selectedProduct.variants.find(v => v.id == variantId);
            this.displayProductDetails();
            this.updateOrderSummary();
        }
    }

    displayProductDetails() {
        const detailsContainer = document.getElementById('productDetails');
        if (!detailsContainer || !this.selectedProduct) return;

        let frameInfo = '';
        if (this.selectedVariant) {
            frameInfo = `<p><strong>Frame:</strong> ${this.selectedVariant.description}</p>`;
        } else if (this.selectedProduct.has_variants) {
            frameInfo = '<p><strong>Frame:</strong> Please select frame type above</p>';
        }

        detailsContainer.innerHTML = `
            <div class="product-details-card">
                <h4>${this.selectedProduct.name} ${this.selectedProduct.size}</h4>
                <div class="product-specs">
                    <p><strong>Category:</strong> ${this.selectedProduct.category_name}</p>
                    <p><strong>Size:</strong> ${this.selectedProduct.size}</p>
                    ${frameInfo}
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
            this.updateSubmitButton(false);
            return;
        }

        // Check if variants are required but not selected
        if (this.selectedProduct.has_variants && !this.selectedVariant) {
            summaryContainer.innerHTML = '<p>Please select a frame type to see order summary.</p>';
            this.updateSubmitButton(false);
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

        let productDisplayName = `${this.selectedProduct.name} ${this.selectedProduct.size}`;
        if (this.selectedVariant) {
            productDisplayName += ` - ${this.selectedVariant.description}`;
        }

        summaryContainer.innerHTML = `
            <div class="order-summary-card">
                <h4>Order Summary</h4>
                <div class="summary-line">
                    <span>${productDisplayName}</span>
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

        this.updateSubmitButton(true, total);
    }

    updateSubmitButton(enabled, total = 0) {
        const submitBtn = document.getElementById('submitOrderBtn');
        if (submitBtn) {
            if (enabled) {
                submitBtn.textContent = `Submit Order - $${total.toFixed(2)}`;
                submitBtn.disabled = false;
            } else {
                submitBtn.textContent = 'Select Product to Continue';
                submitBtn.disabled = true;
            }
        }
    }

    async processPayment() {
        // TODO: Implement payment processing
        console.log('Processing payment for order:', {
            product: this.selectedProduct,
            variant: this.selectedVariant,
            quantity: this.quantity,
            total: this.orderDetails.totalPrice
        });
        
        alert('Payment processing not yet implemented. This is a test order form.');
    }
}

// Initialize the system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Dynamic Ordering System');
    window.orderingSystem = new DynamicOrderingSystem();
});
