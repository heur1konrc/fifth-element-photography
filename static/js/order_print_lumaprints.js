/**
 * Lumaprints Order Interface JavaScript
 * Based on official Lumaprints API documentation
 */

class LumaprintsOrderInterface {
    constructor() {
        this.currentCategory = null;
        this.currentProduct = null;
        this.currentSize = null;
        this.cart = [];
        this.currentView = 'products';
        
        // Dynamic product data from Lumaprints API
        this.categories = [];
        this.subcategories = {};
        this.options = {};
        this.isDataLoaded = false;
        
        this.init();
    }
    
    async init() {
        // Show loading state immediately
        this.showLoadingState();
        
        this.setupEventListeners();
        this.createMobileDropdowns(); // Create mobile dropdowns if on mobile
        
        // Load API data in background
        try {
            await this.loadProductDataFromAPI();
            this.hideLoadingState();
            
            // Populate desktop categories and load first category
            this.populateDesktopCategories();
            if (this.categories.length > 0) {
                this.loadCategoryFromAPI(this.categories[0].id);
            }
        } catch (error) {
            console.error('Failed to load product data:', error);
            this.showError('Failed to load product data. Please refresh the page.');
        }
    }
    
    showLoadingState() {
        const grid = document.getElementById('productsGrid');
        if (grid) {
            grid.innerHTML = '<div class="loading-message">Loading products...</div>';
        }
        
        const mobileContainer = document.querySelector('.mobile-dropdowns-container');
        if (mobileContainer) {
            mobileContainer.innerHTML = '<div class="loading-message">Loading products...</div>';
        }
    }
    
    hideLoadingState() {
        // Loading states will be replaced by actual content
    }
    
    async loadProductDataFromAPI() {
        console.log('Loading product data from Lumaprints API...');
        
        // Step 1: Get all categories
        const categoriesResponse = await fetch('/api/lumaprints/categories');
        this.categories = await categoriesResponse.json();
        console.log('Categories loaded:', this.categories.length);
        
        // Step 2: Get subcategories for each category
        for (const category of this.categories) {
            const subcategoriesResponse = await fetch(`/api/lumaprints/subcategories/${category.id}`);
            this.subcategories[category.id] = await subcategoriesResponse.json();
            console.log(`Subcategories loaded for ${category.name}:`, this.subcategories[category.id].length);
            
            // Step 3: Get options for each subcategory
            for (const subcategory of this.subcategories[category.id]) {
                const optionsResponse = await fetch(`/api/lumaprints/options/${subcategory.subcategoryId}`);
                this.options[subcategory.subcategoryId] = await optionsResponse.json();
                console.log(`Options loaded for ${subcategory.name}:`, this.options[subcategory.subcategoryId].length);
            }
        }
        
        this.isDataLoaded = true;
        console.log('All product data loaded successfully');
        
        // Populate mobile dropdowns if on mobile
        if (window.innerWidth <= 768) {
            this.populateMobileDropdowns();
        }
    }
    
    populateDesktopCategories() {
        const categoriesContainer = document.querySelector('.categories-list');
        if (!categoriesContainer || !this.isDataLoaded) return;
        
        // Clear existing categories
        categoriesContainer.innerHTML = '';
        
        // Add categories from API data
        this.categories.forEach(category => {
            const categoryItem = document.createElement('div');
            categoryItem.className = 'category-item';
            categoryItem.dataset.categoryId = category.id;
            
            categoryItem.innerHTML = `
                <div class="category-icon"></div>
                <span class="category-name">${category.name}</span>
            `;
            
            categoriesContainer.appendChild(categoryItem);
        });
        
        // Re-setup event listeners for new categories
        this.setupCategoryListeners();
    }
    
    setupCategoryListeners() {
        document.querySelectorAll('.category-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const categoryId = parseInt(e.currentTarget.dataset.categoryId);
                this.selectCategory(categoryId);
            });
        });
    }
    
    loadCategoryFromAPI(categoryId) {
        // Update category title
        const category = this.categories.find(c => c.id === categoryId);
        if (category) {
            const categoryTitle = document.getElementById('categoryTitle');
            if (categoryTitle) {
                categoryTitle.textContent = category.name;
            }
            
            // Load products for this category
            this.loadProductsFromAPI(categoryId);
        }
    }
    
    loadProductsFromAPI(categoryId) {
        const grid = document.getElementById('productsGrid');
        if (!grid || !this.subcategories[categoryId]) return;
        
        grid.innerHTML = '';
        
        // Desktop: Create product cards from API data
        this.subcategories[categoryId].forEach(subcategory => {
            const productCard = this.createProductCardFromAPI(subcategory);
            grid.appendChild(productCard);
        });
    }
    
    createProductCardFromAPI(subcategory) {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.dataset.productId = subcategory.subcategoryId;
        
        card.innerHTML = `
            <div class="product-info">
                <h3 class="product-name">${subcategory.name}</h3>
                <div class="product-specs">
                    <p>Size: ${subcategory.minimumWidth}"×${subcategory.minimumHeight}" to ${subcategory.maximumWidth}"×${subcategory.maximumHeight}"</p>
                    <p>Required DPI: ${subcategory.requiredDPI}</p>
                </div>
            </div>
        `;
        
        // Add click handler
        card.addEventListener('click', () => {
            this.selectProduct(subcategory);
        });
        
        return card;
    }
    
    createMobileDropdowns() {
        // Check if we're on mobile (screen width < 768px)
        if (window.innerWidth <= 768) {
            this.createMobileInterface();
        }
    }
    
    createMobileInterface() {
        // Target the main panel where products should appear on mobile
        const mainPanel = document.querySelector('.main-panel');
        if (!mainPanel) {
            console.error('Main panel not found for mobile interface');
            return;
        }
        
        // Clear any existing mobile dropdowns
        const existingDropdowns = mainPanel.querySelectorAll('.mobile-dropdown');
        existingDropdowns.forEach(dropdown => dropdown.remove());
        
        // Create container for all mobile dropdowns
        const mobileContainer = document.createElement('div');
        mobileContainer.className = 'mobile-dropdowns-container';
        
        // Dropdown 1: Product Type
        const productTypeDropdown = document.createElement('select');
        productTypeDropdown.className = 'mobile-category-dropdown mobile-dropdown';
        productTypeDropdown.id = 'mobileProductType';
        productTypeDropdown.innerHTML = '<option value="">Select Product Type...</option>';
        
        // Dropdown 2: Variant
        const variantDropdown = document.createElement('select');
        variantDropdown.className = 'mobile-products-dropdown mobile-dropdown';
        variantDropdown.id = 'mobileVariant';
        variantDropdown.innerHTML = '<option value="">Select Variant...</option>';
        variantDropdown.style.display = 'none';
        
        // Dropdown 3: Variant #2 (if required)
        const variant2Dropdown = document.createElement('select');
        variant2Dropdown.className = 'mobile-sizes-dropdown mobile-dropdown';
        variant2Dropdown.id = 'mobileVariant2';
        variant2Dropdown.innerHTML = '<option value="">Select Option...</option>';
        variant2Dropdown.style.display = 'none';
        
        // Add dropdowns to container
        mobileContainer.appendChild(productTypeDropdown);
        mobileContainer.appendChild(variantDropdown);
        mobileContainer.appendChild(variant2Dropdown);
        
        // Add container to main panel for mobile
        const productsGrid = mainPanel.querySelector('#productsGrid');
        if (productsGrid) {
            productsGrid.appendChild(mobileContainer);
        } else {
            mainPanel.appendChild(mobileContainer);
        }
        
        // Add event listeners
        this.setupMobileDropdownListeners();
    }
    
    populateMobileDropdowns() {
        const productTypeDropdown = document.getElementById('mobileProductType');
        if (!productTypeDropdown || !this.isDataLoaded) return;
        
        // Clear and populate product type dropdown
        productTypeDropdown.innerHTML = '<option value="">Select Product Type...</option>';
        this.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            productTypeDropdown.appendChild(option);
        });
    }
    
    setupMobileDropdownListeners() {
        const productTypeDropdown = document.getElementById('mobileProductType');
        const variantDropdown = document.getElementById('mobileVariant');
        const variant2Dropdown = document.getElementById('mobileVariant2');
        
        // Product Type selection
        productTypeDropdown.addEventListener('change', (e) => {
            const categoryId = parseInt(e.target.value);
            if (categoryId) {
                this.loadMobileVariants(categoryId);
            } else {
                variantDropdown.style.display = 'none';
                variant2Dropdown.style.display = 'none';
            }
        });
        
        // Variant selection
        variantDropdown.addEventListener('change', (e) => {
            const variantId = parseInt(e.target.value);
            if (variantId) {
                this.handleMobileVariantSelection(variantId);
            } else {
                variant2Dropdown.style.display = 'none';
            }
        });
        
        // Variant #2 selection
        variant2Dropdown.addEventListener('change', (e) => {
            const optionId = parseInt(e.target.value);
            if (optionId) {
                this.handleMobileOption2Selection(optionId);
            }
        });
    }
    
    loadMobileVariants(categoryId) {
        const variantDropdown = document.getElementById('mobileVariant');
        const variant2Dropdown = document.getElementById('mobileVariant2');
        
        if (!this.subcategories[categoryId]) return;
        
        // Clear and populate variant dropdown
        variantDropdown.innerHTML = '<option value="">Select Variant...</option>';
        this.subcategories[categoryId].forEach(subcategory => {
            const option = document.createElement('option');
            option.value = subcategory.subcategoryId;
            option.textContent = subcategory.name;
            variantDropdown.appendChild(option);
        });
        
        variantDropdown.style.display = 'block';
        variant2Dropdown.style.display = 'none';
    }
    
    handleMobileVariantSelection(subcategoryId) {
        const variant2Dropdown = document.getElementById('mobileVariant2');
        
        if (this.options[subcategoryId] && this.options[subcategoryId].length > 0) {
            // Clear and populate options dropdown
            variant2Dropdown.innerHTML = '<option value="">Select Option...</option>';
            this.options[subcategoryId].forEach(optionGroup => {
                optionGroup.optionGroupItems.forEach(option => {
                    const optionElement = document.createElement('option');
                    optionElement.value = option.optionId;
                    optionElement.textContent = option.optionName;
                    variant2Dropdown.appendChild(optionElement);
                });
            });
            variant2Dropdown.style.display = 'block';
        } else {
            variant2Dropdown.style.display = 'none';
        }
    }
    
    handleMobileOption2Selection(optionId) {
        console.log('Selected option:', optionId);
        // Handle final option selection
    }
    
    setupEventListeners() {
        // Category selection
        document.querySelectorAll('.category-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const categoryId = parseInt(e.currentTarget.dataset.categoryId);
                this.selectCategory(categoryId);
            });
        });
        
        // Back buttons
        document.getElementById('backToProducts')?.addEventListener('click', () => {
            this.showView('products');
        });
        
        document.getElementById('backToSizes')?.addEventListener('click', () => {
            this.showView('sizes');
        });
        
        // Size selection
        document.getElementById('widthInput')?.addEventListener('input', () => {
            this.updatePricing();
        });
        
        document.getElementById('heightInput')?.addEventListener('input', () => {
            this.updatePricing();
        });
        
        // Add to cart
        document.getElementById('addToCartBtn')?.addEventListener('click', () => {
            this.addToCart();
        });
        
        // Checkout
        document.getElementById('checkoutBtn')?.addEventListener('click', () => {
            this.proceedToCheckout();
        });
    }
    
    selectCategory(categoryId) {
        // Update UI
        document.querySelectorAll('.category-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-category-id="${categoryId}"]`).classList.add('active');
        
        // Load category products using API data
        this.loadCategoryFromAPI(categoryId);
        this.showView('products');
    }
    
    getCategoryName(categoryId) {
        const category = this.categories.find(c => c.id === categoryId);
        return category ? category.name : 'Unknown Category';
    }
    
    selectProduct(product) {
        this.currentProduct = product;
        
        // Update the main panel to show size selection
        const categoryTitle = document.getElementById('categoryTitle');
        if (categoryTitle) {
            categoryTitle.textContent = product.name;
        }
        
        // Clear the products grid and show size inputs
        const grid = document.getElementById('productsGrid');
        if (grid) {
            grid.innerHTML = `
                <div class="size-selection">
                    <h3>Select Size for ${product.name}</h3>
                    <div class="size-specs">
                        <p><strong>Size Range:</strong> ${product.minimumWidth}"×${product.minimumHeight}" to ${product.maximumWidth}"×${product.maximumHeight}"</p>
                        <p><strong>Required DPI:</strong> ${product.requiredDPI}</p>
                    </div>
                    <div class="size-inputs">
                        <div class="input-group">
                            <label for="widthInput">Width (inches):</label>
                            <input type="number" id="widthInput" min="${product.minimumWidth}" max="${product.maximumWidth}" step="0.1" placeholder="Width">
                        </div>
                        <div class="input-group">
                            <label for="heightInput">Height (inches):</label>
                            <input type="number" id="heightInput" min="${product.minimumHeight}" max="${product.maximumHeight}" step="0.1" placeholder="Height">
                        </div>
                    </div>
                    <div class="pricing-section">
                        <div class="price-display">
                            <span class="unit-price">Unit Price: $<span id="unitPrice">0.00</span></span>
                        </div>
                        <div class="quantity-section">
                            <label for="quantityInput">Quantity:</label>
                            <input type="number" id="quantityInput" min="1" value="1">
                        </div>
                        <div class="total-price">
                            <span class="total">Total: $<span id="totalPrice">0.00</span></span>
                        </div>
                        <button id="addToCartBtn" class="add-to-cart-btn" disabled>Add to Cart</button>
                    </div>
                    <button id="backToProductsBtn" class="back-btn">← Back to Products</button>
                </div>
            `;
            
            // Add event listeners for the new elements
            this.setupSizeInputListeners();
        }
    }
    
    setupSizeInputListeners() {
        const widthInput = document.getElementById('widthInput');
        const heightInput = document.getElementById('heightInput');
        const quantityInput = document.getElementById('quantityInput');
        const backBtn = document.getElementById('backToProductsBtn');
        const addToCartBtn = document.getElementById('addToCartBtn');
        
        // Size input listeners
        [widthInput, heightInput, quantityInput].forEach(input => {
            if (input) {
                input.addEventListener('input', () => this.updatePricing());
            }
        });
        
        // Back button
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.loadCategoryFromAPI(this.currentCategory);
            });
        }
        
        // Add to cart button
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', () => this.addToCart());
        }
    }
    
    showView(viewName) {
        this.currentView = viewName;
        
        // Hide all views
        document.querySelectorAll('.view-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        // Show selected view
        const viewMap = {
            'products': 'productsView',
            'sizes': 'sizesView',
            'quantity': 'quantityView'
        };
        
        document.getElementById(viewMap[viewName]).classList.add('active');
    }
    
    updatePricing() {
        // Implementation for pricing updates
        console.log('Updating pricing...');
    }
    
    addToCart() {
        // Implementation for adding to cart
        console.log('Adding to cart...');
    }
    
    proceedToCheckout() {
        // Implementation for checkout
        console.log('Proceeding to checkout...');
    }
    
    showError(message) {
        const grid = document.getElementById('productsGrid');
        if (grid) {
            grid.innerHTML = `<div class="error-message">${message}</div>`;
        }
    }
    
    updatePricing() {
        const widthInput = document.getElementById('widthInput');
        const heightInput = document.getElementById('heightInput');
        const quantityInput = document.getElementById('quantityInput');
        const unitPriceSpan = document.getElementById('unitPrice');
        const totalPriceSpan = document.getElementById('totalPrice');
        const addToCartBtn = document.getElementById('addToCartBtn');
        
        if (!widthInput || !heightInput || !quantityInput) return;
        
        const width = parseFloat(widthInput.value);
        const height = parseFloat(heightInput.value);
        const quantity = parseInt(quantityInput.value) || 1;
        
        // Check if dimensions are valid
        if (width && height && width > 0 && height > 0) {
            // No pricing calculation - would need real Lumaprints pricing API
            // For now, just show that dimensions are valid
            if (unitPriceSpan) unitPriceSpan.textContent = 'TBD';
            if (totalPriceSpan) totalPriceSpan.textContent = 'TBD';
            if (addToCartBtn) addToCartBtn.disabled = false;
        } else {
            // Invalid dimensions
            if (unitPriceSpan) unitPriceSpan.textContent = '--';
            if (totalPriceSpan) totalPriceSpan.textContent = '--';
            if (addToCartBtn) addToCartBtn.disabled = true;
        }
    }
    
    addToCart() {
        const widthInput = document.getElementById('widthInput');
        const heightInput = document.getElementById('heightInput');
        const quantityInput = document.getElementById('quantityInput');
        
        if (!widthInput || !heightInput || !quantityInput || !this.currentProduct) return;
        
        const width = parseFloat(widthInput.value);
        const height = parseFloat(heightInput.value);
        const quantity = parseInt(quantityInput.value) || 1;
        
        if (!width || !height || width <= 0 || height <= 0) {
            alert('Please enter valid dimensions');
            return;
        }
        
        // Create cart item
        const cartItem = {
            product: this.currentProduct,
            width: width,
            height: height,
            quantity: quantity,
            unitPrice: parseFloat(document.getElementById('unitPrice').textContent),
            totalPrice: parseFloat(document.getElementById('totalPrice').textContent)
        };
        
        // Add to cart (placeholder - would integrate with actual cart system)
        console.log('Adding to cart:', cartItem);
        alert(`Added ${quantity}x ${this.currentProduct.name} (${width}"×${height}") to cart!`);
        
        // Reset form
        widthInput.value = '';
        heightInput.value = '';
        quantityInput.value = '1';
        this.updatePricing();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.orderInterface = new LumaprintsOrderInterface();
});

// Also initialize immediately if DOM is already ready
if (document.readyState === 'loading') {
    // DOM hasn't finished loading yet
    document.addEventListener('DOMContentLoaded', () => {
        window.orderInterface = new LumaprintsOrderInterface();
    });
} else {
    // DOM is already ready
    window.orderInterface = new LumaprintsOrderInterface();
}
