/**
 * Order Print Page Controller - Exact Lumaprints Interface Replica
 * Handles category switching, product selection, size selection, and order flow
 */

class OrderPrintController {
    constructor() {
        this.selectedCategory = 'canvas';
        this.selectedProduct = null;
        this.selectedSize = null;
        this.quantity = 1;
        this.currentStep = 1;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showCategory('canvas');
        this.updateStepDisplay();
    }

    setupEventListeners() {
        // Category selection
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

        // Step navigation
        document.addEventListener('click', (e) => {
            if (e.target.closest('.step')) {
                const step = e.target.closest('.step');
                const stepNumber = parseInt(step.dataset.step);
                if (this.canNavigateToStep(stepNumber)) {
                    this.goToStep(stepNumber);
                }
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

        // Continue button
        const continueBtn = document.getElementById('continueOrderBtn');
        if (continueBtn) {
            continueBtn.addEventListener('click', () => this.handleContinue());
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
        
        // Reset selections when changing category
        this.resetSelections();
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

        // Move to size selection step
        this.goToStep(2);
        this.populateSizes(productId);
        this.updateContinueButton();
    }

    populateSizes(productId) {
        const sizesGrid = document.getElementById('sizesGrid');
        if (!sizesGrid) return;

        // Get sizes for this product
        const sizes = this.getSizesForProduct(productId);
        
        // Clear existing sizes
        sizesGrid.innerHTML = '';

        // Add size options
        sizes.forEach(size => {
            const sizeElement = document.createElement('div');
            sizeElement.className = 'size-option';
            sizeElement.dataset.width = size.width;
            sizeElement.dataset.height = size.height;
            sizeElement.dataset.price = size.price;
            sizeElement.innerHTML = `
                <div class="size-display">${size.name}</div>
                <div class="size-price">$${size.price.toFixed(2)}</div>
            `;
            sizesGrid.appendChild(sizeElement);
        });
    }

    selectSize(sizeElement) {
        // Update size selection visual state
        document.querySelectorAll('.size-option').forEach(option => {
            option.classList.remove('selected');
        });
        sizeElement.classList.add('selected');

        // Get size data
        this.selectedSize = {
            width: parseInt(sizeElement.dataset.width),
            height: parseInt(sizeElement.dataset.height),
            price: parseFloat(sizeElement.dataset.price),
            name: sizeElement.querySelector('.size-display').textContent
        };

        // Move to options step
        this.goToStep(3);
        this.updatePricing();
        this.updateContinueButton();
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
            const unitPrice = this.selectedSize.price;
            const total = unitPrice * this.quantity;
            
            priceDisplay.innerHTML = `
                <div class="price-info">
                    <div class="price-breakdown">
                        <div>Unit Price: $${unitPrice.toFixed(2)}</div>
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

    goToStep(stepNumber) {
        this.currentStep = stepNumber;
        this.updateStepDisplay();
        this.updateStepNavigation();
    }

    updateStepDisplay() {
        // Hide all step content panels
        document.querySelectorAll('.step-content-panel').forEach(panel => {
            panel.classList.remove('active');
        });

        // Show current step panel
        const currentPanel = document.querySelector(`[data-step="${this.currentStep}"]`);
        if (currentPanel) {
            currentPanel.classList.add('active');
        }
    }

    updateStepNavigation() {
        // Update step navigation visual state
        document.querySelectorAll('.step').forEach(step => {
            const stepNumber = parseInt(step.dataset.step);
            step.classList.remove('active', 'completed');
            
            if (stepNumber === this.currentStep) {
                step.classList.add('active');
            } else if (stepNumber < this.currentStep) {
                step.classList.add('completed');
            }
        });
    }

    canNavigateToStep(stepNumber) {
        switch (stepNumber) {
            case 1:
                return true;
            case 2:
                return this.selectedProduct !== null;
            case 3:
                return this.selectedProduct !== null && this.selectedSize !== null;
            case 4:
                return this.selectedProduct !== null && this.selectedSize !== null;
            default:
                return false;
        }
    }

    updateContinueButton() {
        const continueBtn = document.getElementById('continueOrderBtn');
        if (!continueBtn) return;

        const canProceed = this.selectedProduct && this.selectedSize;
        continueBtn.disabled = !canProceed;
        
        if (canProceed) {
            if (this.currentStep < 4) {
                continueBtn.textContent = 'Continue';
            } else {
                continueBtn.textContent = 'Proceed to Checkout';
            }
        } else {
            continueBtn.textContent = 'Select Product & Size';
        }
    }

    handleContinue() {
        if (!this.selectedProduct || !this.selectedSize) {
            alert('Please select a product and size first.');
            return;
        }

        if (this.currentStep < 4) {
            this.goToStep(this.currentStep + 1);
            if (this.currentStep === 4) {
                this.updateOrderSummary();
            }
        } else {
            // Proceed to checkout
            this.proceedToCheckout();
        }
        
        this.updateContinueButton();
    }

    updateOrderSummary() {
        const orderSummary = document.getElementById('orderSummary');
        if (!orderSummary) return;

        const productName = this.getProductName(this.selectedProduct);
        const unitPrice = this.selectedSize.price;
        const total = unitPrice * this.quantity;

        orderSummary.innerHTML = `
            <h4>Order Summary</h4>
            <div class="summary-details">
                <p><strong>Product:</strong> <span>${productName}</span></p>
                <p><strong>Size:</strong> <span>${this.selectedSize.name}</span></p>
                <p><strong>Quantity:</strong> <span>${this.quantity}</span></p>
                <p><strong>Unit Price:</strong> <span>$${unitPrice.toFixed(2)}</span></p>
                <p class="total-price"><strong>Total:</strong> <span><strong>$${total.toFixed(2)}</strong></span></p>
            </div>
        `;
    }

    proceedToCheckout() {
        // Prepare order data
        const orderData = {
            product: this.selectedProduct,
            productName: this.getProductName(this.selectedProduct),
            size: this.selectedSize,
            quantity: this.quantity,
            unitPrice: this.selectedSize.price,
            total: this.selectedSize.price * this.quantity
        };

        // For now, show an alert (later this would integrate with payment system)
        alert(`Order prepared!\n\nProduct: ${orderData.productName}\nSize: ${orderData.size.name}\nQuantity: ${orderData.quantity}\nTotal: $${orderData.total.toFixed(2)}\n\nThis would proceed to payment processing.`);
    }

    resetSelections() {
        this.selectedProduct = null;
        this.selectedSize = null;
        this.quantity = 1;
        this.currentStep = 1;
        
        // Reset visual states
        document.querySelectorAll('.product-option, .size-option').forEach(el => {
            el.classList.remove('selected');
        });
        
        const quantityInput = document.getElementById('quantity');
        if (quantityInput) {
            quantityInput.value = 1;
        }
        
        this.updateStepDisplay();
        this.updateStepNavigation();
        this.updatePricing();
        this.updateContinueButton();
    }

    getSizesForProduct(productId) {
        // Default sizes for all products - this would normally come from API
        return [
            { width: 8, height: 10, name: '8" × 10"', price: 29.99 },
            { width: 11, height: 14, name: '11" × 14"', price: 39.99 },
            { width: 16, height: 20, name: '16" × 20"', price: 59.99 },
            { width: 18, height: 24, name: '18" × 24"', price: 79.99 },
            { width: 20, height: 30, name: '20" × 30"', price: 99.99 },
            { width: 24, height: 36, name: '24" × 36"', price: 129.99 }
        ];
    }

    getProductName(productId) {
        const productNames = {
            // Canvas Products
            'canvas-075': '0.75in Stretched Canvas',
            'canvas-125': '1.25in Stretched Canvas',
            'canvas-150': '1.50in Stretched Canvas',
            'canvas-rolled': 'Rolled Canvas',
            
            // Framed Canvas Products - 1.50"
            'frame-maple': '1.50in Maple Wood Floating Frame',
            'frame-espresso': '1.50in Espresso Floating Frame',
            'frame-natural': '1.50in Natural Wood Floating Frame',
            'frame-oak': '1.50in Oak Floating Frame',
            'frame-gold': '1.50in Gold Floating Frame',
            'frame-silver': '1.50in Silver Floating Frame',
            'frame-white': '1.50in White Floating Frame',
            'frame-black': '1.50in Black Floating Frame',
            
            // Framed Canvas Products - 1.25"
            'frame-125-maple': '1.25in Maple Wood Floating Frame',
            'frame-125-espresso': '1.25in Espresso Floating Frame',
            'frame-125-natural': '1.25in Natural Wood Floating Frame',
            'frame-125-black': '1.25in Black Floating Frame',
            
            // Fine Art Paper Products
            'paper-archival-matte': 'Archival Matte Fine Art Paper',
            'paper-hot-press': 'Hot Press Fine Art Paper',
            'paper-cold-press': 'Cold Press Fine Art Paper',
            'paper-semi-glossy': 'Semi-Glossy Fine Art Paper',
            'paper-metallic': 'Metallic Fine Art Paper',
            'paper-glossy': 'Glossy Fine Art Paper',
            'paper-somerset-velvet': 'Somerset Velvet Fine Art Paper',
            
            // Foam Mounted Print
            'foam-mounted-print': 'Foam Mounted Print',
            
            // Framed Fine Art Paper
            'framed-fine-art-black': 'Black Framed Fine Art Paper',
            'framed-fine-art-white': 'White Framed Fine Art Paper',
            'framed-fine-art-natural': 'Natural Wood Framed Fine Art Paper',
            
            // Metal Products
            'metal-glossy': 'Metal Print - Glossy',
            'metal-matte': 'Metal Print - Matte',
            
            // Peel and Stick
            'peel-and-stick': 'Peel and Stick'
        };
        return productNames[productId] || 'Unknown Product';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.orderPrintController = new OrderPrintController();
});
