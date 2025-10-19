class ThreeDropdownOrderingSystem {
    constructor() {
        this.allProducts = [];
        this.productTypes = [];
        this.selectedType = null;
        this.selectedModifier = null;
        this.selectedProduct = null;
        this.currentImageUrl = '';
    }

    async init() {
        console.log('Initializing Three Dropdown Ordering System');
        
        // Get image URL from page
        this.currentImageUrl = this.getImageUrlFromPage();
        
        // Load products from database
        await this.loadProducts();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Populate first dropdown
        this.populateProductTypes();
        
        // Setup image preview
        this.setupImagePreview();
        
        console.log('Three Dropdown System initialized successfully');
    }

    getImageUrlFromPage() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('image') || '';
    }

    async loadProducts() {
        try {
            console.log('Loading products from database...');
            const response = await fetch('/api/products');
            const data = await response.json();
            
            if (data.success) {
                this.allProducts = data.products;
                console.log(`Loaded ${this.allProducts.length} products from database`);
                
                // Extract unique product types
                this.extractProductTypes();
            } else {
                console.error('Failed to load products:', data.message);
                this.showError('Failed to load products. Please refresh the page.');
            }
        } catch (error) {
            console.error('Error loading products:', error);
            this.showError('Error loading products. Please check your connection.');
        }
    }

    extractProductTypes() {
        const typeMap = new Map();
        
        console.log('Processing', this.allProducts.length, 'products for type extraction');
        
        this.allProducts.forEach((product, index) => {
            const categoryName = product.category_name;
            console.log(`Product ${index + 1}: ${product.name} - Category: ${categoryName}`);
            
            if (!typeMap.has(categoryName)) {
                typeMap.set(categoryName, {
                    name: categoryName,
                    category_id: product.category_id,
                    hasVariants: false,
                    products: []
                });
            }
            
            const type = typeMap.get(categoryName);
            type.products.push(product);
            
            if (product.has_variants) {
                type.hasVariants = true;
            }
        });
        
        // Convert to array and sort logically
        this.productTypes = Array.from(typeMap.values()).sort((a, b) => {
            // Sort by thickness for canvas products
            const aThickness = this.extractThickness(a.name);
            const bThickness = this.extractThickness(b.name);
            
            if (aThickness && bThickness) {
                return aThickness - bThickness;
            }
            
            // Fallback to alphabetical
            return a.name.localeCompare(b.name);
        });
        
        console.log('Extracted product types:', this.productTypes.map(t => t.name));
    }

    extractThickness(categoryName) {
        const match = categoryName.match(/(\d+\.?\d*)\"/);
        return match ? parseFloat(match[1]) : null;
    }

    setupEventListeners() {
        const typeDropdown = document.getElementById('productTypeSelect');
        const modifierDropdown = document.getElementById('modifierSelect');
        const sizeDropdown = document.getElementById('sizeSelect');
        const quantityInput = document.getElementById('quantityInput');

        if (typeDropdown) {
            typeDropdown.addEventListener('change', () => this.onTypeChange());
        }

        if (modifierDropdown) {
            modifierDropdown.addEventListener('change', () => this.onModifierChange());
        }

        if (sizeDropdown) {
            sizeDropdown.addEventListener('change', () => this.onSizeChange());
        }

        if (quantityInput) {
            quantityInput.addEventListener('change', () => this.updateOrderSummary());
        }
    }

    populateProductTypes() {
        const dropdown = document.getElementById('productTypeSelect');
        if (!dropdown) return;

        // Clear existing options
        dropdown.innerHTML = '<option value="">Select product type...</option>';

        // Add product types
        this.productTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.name;
            option.textContent = type.name;
            dropdown.appendChild(option);
        });

        console.log(`Populated ${this.productTypes.length} product types`);
    }

    onTypeChange() {
        const typeDropdown = document.getElementById('productTypeSelect');
        const modifierDropdown = document.getElementById('modifierSelect');
        const sizeDropdown = document.getElementById('sizeSelect');
        const selectedTypeName = typeDropdown.value;
        
        console.log('Product type changed to:', selectedTypeName);

        if (!selectedTypeName) {
            this.selectedType = null;
            this.clearModifierDropdown();
            this.clearSizeDropdown();
            this.clearProductDetails();
            this.disableDropdown('step2', modifierDropdown);
            this.disableDropdown('step3', sizeDropdown);
            return;
        }

        // Find selected type
        this.selectedType = this.productTypes.find(type => type.name === selectedTypeName);
        
        if (this.selectedType) {
            this.enableDropdown('step2', modifierDropdown);
            this.populateModifierDropdown();
            document.getElementById('step1').classList.add('completed');
        }
    }

    populateModifierDropdown() {
        const dropdown = document.getElementById('modifierSelect');
        if (!dropdown || !this.selectedType) return;

        // Clear existing options
        dropdown.innerHTML = '';

        if (this.selectedType.hasVariants) {
            // Get unique variants from products in this type
            const variantMap = new Map();
            
            this.selectedType.products.forEach(product => {
                if (product.variants && product.variants.length > 0) {
                    product.variants.forEach(variant => {
                        if (!variantMap.has(variant.name)) {
                            variantMap.set(variant.name, variant);
                        }
                    });
                }
            });

            if (variantMap.size > 0) {
                dropdown.innerHTML = '<option value="">Select frame type...</option>';
                
                // Sort variants with default first
                const variants = Array.from(variantMap.values()).sort((a, b) => {
                    if (a.is_default && !b.is_default) return -1;
                    if (!a.is_default && b.is_default) return 1;
                    return a.name.localeCompare(b.name);
                });

                variants.forEach(variant => {
                    const option = document.createElement('option');
                    option.value = variant.name;
                    option.textContent = variant.description || variant.name;
                    dropdown.appendChild(option);
                });

                console.log(`Populated ${variants.length} modifiers for ${this.selectedType.name}`);
            } else {
                dropdown.innerHTML = '<option value="none">No color options apply</option>';
            }
        } else {
            // No variants available
            dropdown.innerHTML = '<option value="none">No color options apply</option>';
            console.log('No modifiers needed for', this.selectedType.name);
        }

        // Auto-trigger modifier change if only one option
        if (dropdown.options.length === 1) {
            dropdown.selectedIndex = 0;
            this.onModifierChange();
        }
    }

    onModifierChange() {
        const modifierDropdown = document.getElementById('modifierSelect');
        const sizeDropdown = document.getElementById('sizeSelect');
        const selectedModifier = modifierDropdown.value;
        
        console.log('Modifier changed to:', selectedModifier);

        if (!selectedModifier) {
            this.selectedModifier = null;
            this.clearSizeDropdown();
            this.clearProductDetails();
            this.disableDropdown('step3', sizeDropdown);
            return;
        }

        this.selectedModifier = selectedModifier;
        this.enableDropdown('step3', sizeDropdown);
        this.populateSizeDropdown();
        document.getElementById('step2').classList.add('completed');
    }

    populateSizeDropdown() {
        const dropdown = document.getElementById('sizeSelect');
        if (!dropdown || !this.selectedType) return;

        // Clear existing options
        dropdown.innerHTML = '<option value="">Select size...</option>';

        // Get products for current type and modifier
        let availableProducts = this.selectedType.products;

        // If modifier is selected and not "none", filter by variant
        if (this.selectedModifier && this.selectedModifier !== 'none' && this.selectedModifier !== '') {
            availableProducts = availableProducts.filter(product => {
                if (!product.has_variants) return false;
                return product.variants && product.variants.some(variant => variant.name === this.selectedModifier);
            });
        }

        // Sort products by size (smallest to largest)
        availableProducts.sort((a, b) => {
            return this.compareSizes(a.size, b.size);
        });

        // Add size options
        availableProducts.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = `${product.size} - $${product.customer_price.toFixed(2)}`;
            option.dataset.productId = product.database_id;
            dropdown.appendChild(option);
        });

        console.log(`Populated ${availableProducts.length} sizes for ${this.selectedType.name}`);
        
        // Clear product details until size is selected
        this.clearProductDetails();
    }

    compareSizes(sizeA, sizeB) {
        // Extract dimensions and calculate area for sorting
        const parseSize = (size) => {
            const match = size.match(/(\d+)×(\d+)/);
            if (match) {
                const width = parseInt(match[1]);
                const height = parseInt(match[2]);
                return width * height;
            }
            return 0;
        };

        return parseSize(sizeA) - parseSize(sizeB);
    }

    onSizeChange() {
        const sizeDropdown = document.getElementById('sizeSelect');
        const selectedProductId = sizeDropdown.value;
        
        console.log('Size changed to product ID:', selectedProductId);

        if (!selectedProductId) {
            this.selectedProduct = null;
            this.clearProductDetails();
            return;
        }

        // Find selected product
        this.selectedProduct = this.allProducts.find(product => product.id === selectedProductId);
        
        if (this.selectedProduct) {
            this.displayProductDetails();
            this.updateOrderSummary();
        }
    }

    displayProductDetails() {
        const detailsContainer = document.getElementById('productDetails');
        if (!detailsContainer || !this.selectedProduct) return;

        const modifierText = (this.selectedModifier && this.selectedModifier !== 'none') 
            ? this.selectedModifier 
            : 'Standard';

        detailsContainer.innerHTML = `
            <div class="product-details-card">
                <h4>${this.selectedType.name}</h4>
                <div class="detail-row">
                    <span class="label">Category:</span>
                    <span class="value">${this.selectedProduct.category_name}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Size:</span>
                    <span class="value">${this.selectedProduct.size}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Option:</span>
                    <span class="value">${modifierText}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Price:</span>
                    <span class="value price">$${this.selectedProduct.customer_price.toFixed(2)}</span>
                </div>
            </div>
        `;

        console.log('Displayed product details for:', this.selectedProduct.name);
    }

    updateOrderSummary() {
        const summaryContainer = document.getElementById('orderSummary');
        const quantityInput = document.getElementById('quantityInput');
        
        if (!summaryContainer || !this.selectedProduct) return;

        const quantity = parseInt(quantityInput?.value || 1);
        const unitPrice = this.selectedProduct.customer_price;
        const totalPrice = unitPrice * quantity;

        const modifierText = (this.selectedModifier && this.selectedModifier !== 'none') 
            ? this.selectedModifier 
            : 'Standard';

        summaryContainer.innerHTML = `
            <div class="order-summary-card">
                <h4>Order Summary</h4>
                <div class="summary-row">
                    <span class="label">Product:</span>
                    <span class="value">${this.selectedType.name}</span>
                </div>
                <div class="summary-row">
                    <span class="label">Size:</span>
                    <span class="value">${this.selectedProduct.size}</span>
                </div>
                <div class="summary-row">
                    <span class="label">Option:</span>
                    <span class="value">${modifierText}</span>
                </div>
                <div class="summary-row">
                    <span class="label">Quantity:</span>
                    <span class="value">${quantity}</span>
                </div>
                <div class="summary-row">
                    <span class="label">Unit Price:</span>
                    <span class="value">$${unitPrice.toFixed(2)}</span>
                </div>
                <div class="summary-row total">
                    <span class="label">Total:</span>
                    <span class="value">$${totalPrice.toFixed(2)}</span>
                </div>
            </div>
        `;

        console.log('Updated order summary:', { quantity, unitPrice, totalPrice });
    }

    setupImagePreview() {
        const imageContainer = document.getElementById('imagePreview');
        if (!imageContainer) return;

        if (this.currentImageUrl) {
            console.log('Setting current image:', this.currentImageUrl);
            imageContainer.innerHTML = `
                <div class="image-preview-card">
                    <h4>Selected Image</h4>
                    <img src="${this.currentImageUrl}" alt="Selected image" class="preview-image">
                    <div class="image-info">
                        <div class="info-row">
                            <span class="label">File:</span>
                            <span class="value">${this.getFilenameFromUrl(this.currentImageUrl)}</span>
                        </div>
                    </div>
                </div>
            `;
        } else {
            imageContainer.innerHTML = '<p>No image selected</p>';
        }
    }

    getFilenameFromUrl(url) {
        return url.split('/').pop() || 'Unknown';
    }

    clearModifierDropdown() {
        const dropdown = document.getElementById('modifierSelect');
        if (dropdown) {
            dropdown.innerHTML = '<option value="">Select modifier...</option>';
        }
    }

    clearSizeDropdown() {
        const dropdown = document.getElementById('sizeSelect');
        if (dropdown) {
            dropdown.innerHTML = '<option value="">Select size...</option>';
        }
    }

    clearProductDetails() {
        const detailsContainer = document.getElementById('productDetails');
        if (detailsContainer) {
            detailsContainer.innerHTML = '<p>Select a product to see details.</p>';
        }
        
        const summaryContainer = document.getElementById('orderSummary');
        if (summaryContainer) {
            summaryContainer.innerHTML = '<p>Complete your selection to see order summary.</p>';
        }
    }

    showError(message) {
        const errorContainer = document.getElementById('errorMessage');
        if (errorContainer) {
            errorContainer.innerHTML = `<div class="error-message">${message}</div>`;
            errorContainer.style.display = 'block';
        } else {
            alert(message);
        }
    }

    enableDropdown(stepId, dropdown) {
        const step = document.getElementById(stepId);
        if (step) {
            step.classList.remove('disabled');
        }
        if (dropdown) {
            dropdown.disabled = false;
        }
        console.log('Enabled dropdown:', stepId);
    }

    disableDropdown(stepId, dropdown) {
        const step = document.getElementById(stepId);
        if (step) {
            step.classList.add('disabled');
            step.classList.remove('completed');
        }
        if (dropdown) {
            dropdown.disabled = true;
        }
        console.log('Disabled dropdown:', stepId);
    }

    // Public method to get current selection for form submission
    getCurrentSelection() {
        if (!this.selectedProduct) return null;

        return {
            productId: this.selectedProduct.database_id,
            productName: this.selectedProduct.name,
            size: this.selectedProduct.size,
            modifier: this.selectedModifier !== 'none' ? this.selectedModifier : null,
            unitPrice: this.selectedProduct.customer_price,
            quantity: parseInt(document.getElementById('quantityInput')?.value || 1),
            totalPrice: this.selectedProduct.customer_price * parseInt(document.getElementById('quantityInput')?.value || 1)
        };
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing Three Dropdown System');
    const orderingSystem = new ThreeDropdownOrderingSystem();
    orderingSystem.init();
    
    // Make globally available for form submission
    window.orderingSystem = orderingSystem;
});
