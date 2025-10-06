/**
 * Lumaprints Interface Controller - Exact Match to Official Design
 * Handles left sidebar categories and right panel product selection
 */

class LumaprintsInterface {
    constructor() {
        this.currentImage = null;
        this.selectedCategory = 'canvas';
        this.selectedProduct = null;
        this.selectedSize = null;
        this.quantity = 1;
        this.currentPricing = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showCategory('canvas'); // Default to canvas category
    }

    setupEventListeners() {
        // Category selection in sidebar
        document.addEventListener('click', (e) => {
            if (e.target.closest('.category-item')) {
                this.selectCategory(e.target.closest('.category-item'));
            }
        });

        // Product selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-select-product')) {
                e.preventDefault();
                this.selectProduct(e.target.closest('.product-option'));
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
                this.quantity = Math.max(1, parseInt(e.target.value) || 1);
                this.updatePricing();
            });
        }

        // Proceed to order button
        const proceedBtn = document.getElementById('continueOrderBtn');
        if (proceedBtn) {
            proceedBtn.addEventListener('click', () => this.proceedToOrder());
        }
    }

    selectCategory(categoryElement) {
        // Update sidebar active state
        document.querySelectorAll('.category-item').forEach(item => {
            item.classList.remove('active');
        });
        categoryElement.classList.add('active');

        // Get category from data attribute
        const category = categoryElement.dataset.category;
        this.selectedCategory = category;
        
        // Show corresponding product section
        this.showCategory(category);
    }

    showCategory(category) {
        // Hide all product category sections
        document.querySelectorAll('.product-category-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected category section
        const categorySection = document.querySelector(`[data-category="${category}"]`);
        if (categorySection) {
            categorySection.classList.add('active');
        }

        // Reset selections when changing category
        this.selectedProduct = null;
        this.selectedSize = null;
        this.hideSizeSelection();
        this.updateProceedButton();
    }

    selectProduct(productElement) {
        // Update product selection visual state
        document.querySelectorAll('.product-option').forEach(option => {
            option.classList.remove('selected');
        });
        productElement.classList.add('selected');

        // Get product data
        const productId = productElement.dataset.product;
        this.selectedProduct = productId;

        // Show size selection
        this.showSizeSelection(productId);
        this.updateProceedButton();
    }

    showSizeSelection(productId) {
        const sizeSection = document.getElementById('sizeSelectionSection');
        const sizesGrid = document.getElementById('sizesGrid');
        
        if (!sizeSection || !sizesGrid) return;

        // Get sizes for this product from pricing data
        const sizes = this.getSizesForProduct(productId);
        
        // Clear existing sizes
        sizesGrid.innerHTML = '';

        // Add size options
        sizes.forEach(size => {
            const sizeElement = document.createElement('div');
            sizeElement.className = 'size-option';
            sizeElement.dataset.size = size.id;
            sizeElement.innerHTML = `
                <div class="size-display">${size.name}</div>
                <div class="size-price">$${size.price}</div>
            `;
            sizesGrid.appendChild(sizeElement);
        });

        // Show size selection section
        sizeSection.style.display = 'block';
        
        // Scroll to size selection
        sizeSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    hideSizeSelection() {
        const sizeSection = document.getElementById('sizeSelectionSection');
        if (sizeSection) {
            sizeSection.style.display = 'none';
        }
    }

    selectSize(sizeElement) {
        // Update size selection visual state
        document.querySelectorAll('.size-option').forEach(option => {
            option.classList.remove('selected');
        });
        sizeElement.classList.add('selected');

        // Get size data
        const sizeId = sizeElement.dataset.size;
        this.selectedSize = sizeId;

        // Update pricing
        this.updatePricing();
        this.updateProceedButton();
    }

    changeQuantity(delta) {
        this.quantity = Math.max(1, this.quantity + delta);
        const quantityInput = document.getElementById('quantity');
        if (quantityInput) {
            quantityInput.value = this.quantity;
        }
        this.updatePricing();
    }

    updatePricing() {
        const priceDisplay = document.getElementById('priceDisplay');
        if (!priceDisplay) return;

        if (this.selectedProduct && this.selectedSize) {
            const price = this.getPriceForProductSize(this.selectedProduct, this.selectedSize);
            const total = price * this.quantity;
            
            priceDisplay.innerHTML = `
                <div class="price-info">
                    <div class="price-breakdown">
                        <div>Unit Price: $${price.toFixed(2)}</div>
                        <div>Quantity: ${this.quantity}</div>
                        <div class="total-price"><strong>Total: $${total.toFixed(2)}</strong></div>
                    </div>
                </div>
            `;
        } else {
            priceDisplay.innerHTML = `
                <div class="price-info">
                    <span>Select product and size to see pricing</span>
                </div>
            `;
        }
    }

    updateProceedButton() {
        const proceedBtn = document.getElementById('continueOrderBtn');
        if (!proceedBtn) return;

        const canProceed = this.selectedProduct && this.selectedSize;
        proceedBtn.disabled = !canProceed;
        
        if (canProceed) {
            proceedBtn.textContent = 'Proceed to Order';
        } else {
            proceedBtn.textContent = 'Select Product & Size';
        }
    }

    getSizesForProduct(productId) {
        // Default sizes for all products - this would normally come from API
        return [
            { id: '8x10', name: '8" × 10"', price: 29.99 },
            { id: '11x14', name: '11" × 14"', price: 39.99 },
            { id: '16x20', name: '16" × 20"', price: 59.99 },
            { id: '18x24', name: '18" × 24"', price: 79.99 },
            { id: '20x30', name: '20" × 30"', price: 99.99 },
            { id: '24x36', name: '24" × 36"', price: 129.99 }
        ];
    }

    getPriceForProductSize(productId, sizeId) {
        const sizes = this.getSizesForProduct(productId);
        const size = sizes.find(s => s.id === sizeId);
        return size ? size.price : 0;
    }

    proceedToOrder() {
        if (!this.selectedProduct || !this.selectedSize) {
            alert('Please select a product and size first.');
            return;
        }

        // Prepare order data
        const orderData = {
            image: this.currentImage,
            product: this.selectedProduct,
            size: this.selectedSize,
            quantity: this.quantity,
            price: this.getPriceForProductSize(this.selectedProduct, this.selectedSize),
            total: this.getPriceForProductSize(this.selectedProduct, this.selectedSize) * this.quantity
        };

        // Show order form (existing functionality)
        this.showOrderForm(orderData);
    }

    showOrderForm(orderData) {
        // Hide print order view
        const printOrderModal = document.getElementById('modalPrintOrder');
        const orderFormModal = document.getElementById('modalOrderForm');
        
        if (printOrderModal) printOrderModal.style.display = 'none';
        if (orderFormModal) {
            orderFormModal.style.display = 'block';
            
            // Populate order summary
            const orderSummary = document.getElementById('orderSummary');
            if (orderSummary) {
                orderSummary.innerHTML = `
                    <h4>Order Summary</h4>
                    <div class="summary-details">
                        <p><strong>Image:</strong> ${orderData.image?.title || 'Selected Image'}</p>
                        <p><strong>Product:</strong> ${this.getProductName(orderData.product)}</p>
                        <p><strong>Size:</strong> ${orderData.size}</p>
                        <p><strong>Quantity:</strong> ${orderData.quantity}</p>
                        <p class="total-price"><strong>Total: $${orderData.total.toFixed(2)}</strong></p>
                    </div>
                `;
            }
        }
    }

    getProductName(productId) {
        const productNames = {
            '101001': 'Canvas Print (0.75")',
            '101002': 'Canvas Print (1.25")',
            '101003': 'Canvas Print (1.50")',
            '101004': 'Rolled Canvas',
            '102001': '1.50in Maple Wood Floating Frame',
            '102002': '1.50in Espresso Floating Frame',
            '102003': '1.50in Natural Wood Floating Frame',
            '102008': '1.50in Black Floating Frame',
            '103001': 'Fine Art Paper',
            '106001': 'Metal Print - Glossy',
            '106002': 'Metal Print - Matte'
        };
        return productNames[productId] || 'Unknown Product';
    }

    setCurrentImage(imageData) {
        this.currentImage = imageData;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.lumaprintsInterface = new LumaprintsInterface();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LumaprintsInterface;
}
