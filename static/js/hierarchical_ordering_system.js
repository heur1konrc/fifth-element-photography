class HierarchicalOrderingSystem {
    constructor() {
        this.productTypes = [];
        this.currentSelections = {
            productType: null,
            subOption1: null,
            subOption2: null,
            selectedProduct: null
        };
        this.isMobile = window.innerWidth <= 768;
        this.currentStep = 1;
        this.maxSteps = 4;
        
        this.init();
    }

    init() {
        this.loadProductTypes();
        this.setupEventListeners();
        this.setupMobileDetection();
    }

    setupMobileDetection() {
        // Show mobile optimization message if on mobile
        if (this.isMobile) {
            this.showMobileMessage();
        }
        
        // Update on resize
        window.addEventListener('resize', () => {
            const wasMobile = this.isMobile;
            this.isMobile = window.innerWidth <= 768;
            
            if (wasMobile !== this.isMobile) {
                this.renderInterface();
            }
        });
    }

    showMobileMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'mobile-optimization-message';
        messageDiv.innerHTML = `
            <div class="alert alert-info mb-3">
                <h6><i class="fas fa-info-circle"></i> Mobile Notice</h6>
                <p class="mb-2">This site is optimized for desktop viewing. Due to the many product variations offered, we recommend using a desktop or tablet for the best experience.</p>
                <button class="btn btn-sm btn-primary" onclick="this.parentElement.parentElement.style.display='none'">
                    Continue Anyway
                </button>
            </div>
        `;
        
        const container = document.getElementById('ordering-container');
        container.insertBefore(messageDiv, container.firstChild);
    }

    setupEventListeners() {
        // Mobile wizard navigation
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('wizard-next')) {
                this.nextStep();
            } else if (e.target.classList.contains('wizard-prev')) {
                this.prevStep();
            }
        });
    }

    async loadProductTypes() {
        try {
            const response = await fetch('/api/hierarchical/product-types');
            const data = await response.json();
            
            if (data.success) {
                this.productTypes = data.product_types;
                this.renderInterface();
            } else {
                console.error('Failed to load product types:', data.error);
                this.showError('Failed to load product types. Please refresh the page.');
            }
        } catch (error) {
            console.error('Error loading product types:', error);
            this.showError('Network error. Please check your connection and refresh the page.');
        }
    }

    showError(message) {
        const container = document.getElementById('ordering-container');
        container.innerHTML = `
            <div class="alert alert-danger text-center">
                <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                <h5>Error</h5>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">Refresh Page</button>
            </div>
        `;
    }

    renderInterface() {
        const container = document.getElementById('ordering-container');
        
        // Always use mobile wizard logic for proper step progression
        // Container width is controlled by CSS instead of browser detection
        this.renderMobileWizard(container);
        
        // Load data for current selections
        this.loadCurrentStepData();
    }

    async loadCurrentStepData() {
        if (this.currentSelections.productType && !this.currentSelections.subOption1 && this.currentSelections.productType.max_sub_option_levels > 0) {
            await this.loadSubOption1();
        }
        
        if (this.currentSelections.subOption1 && !this.currentSelections.subOption2 && this.currentSelections.productType.max_sub_option_levels > 1) {
            await this.loadSubOption2();
        }
        
        if (this.canShowSizes()) {
            await this.loadAvailableSizes();
        }
    }

    renderMobileWizard(container) {
        const wizardHTML = `
            <div class="mobile-wizard">
                <div class="wizard-progress mb-4">
                    <div class="progress">
                        <div class="progress-bar" style="width: ${(this.currentStep / this.maxSteps) * 100}%"></div>
                    </div>
                    <small class="text-muted">Step ${this.currentStep} of ${this.maxSteps}</small>
                </div>
                
                <div class="wizard-content">
                    ${this.renderWizardStep()}
                </div>
                
                <div class="wizard-navigation mt-4">
                    ${this.currentStep > 1 ? '<button class="btn btn-secondary wizard-prev">Previous</button>' : ''}
                    ${this.canAdvanceStep() ? '<button class="btn btn-primary wizard-next ms-2">Next</button>' : ''}
                    ${this.currentStep === this.maxSteps && this.currentSelections.selectedProduct ? '<button class="btn btn-success ms-2" onclick="addToCart()">Add to Cart</button>' : ''}
                </div>
            </div>
        `;
        
        container.innerHTML = wizardHTML;
    }

    renderWizardStep() {
        switch (this.currentStep) {
            case 1:
                return this.renderProductTypeStep();
            case 2:
                return this.renderSubOption1Step();
            case 3:
                return this.renderSubOption2Step();
            case 4:
                return this.renderSizeSelectionStep();
            default:
                return '<div>Invalid step</div>';
        }
    }

    renderDesktopHybrid(container) {
        const hybridHTML = `
            <div class="desktop-hybrid">
                <div class="row">
                    <div class="col-md-3">
                        <div class="selection-panel">
                            <h5>Product Type</h5>
                            ${this.renderProductTypeDropdown()}
                        </div>
                    </div>
                    
                    <div class="col-md-3">
                        <div class="selection-panel">
                            <h5>Options</h5>
                            <div id="sub-option-1-container">
                                ${this.currentSelections.productType ? this.renderSubOption1Panel() : '<p class="text-muted">Select a product type first</p>'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-3">
                        <div class="selection-panel">
                            <h5>Additional Options</h5>
                            <div id="sub-option-2-container">
                                ${this.shouldShowSubOption2() ? this.renderSubOption2Panel() : '<p class="text-muted">Additional options will appear here</p>'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-3">
                        <div class="selection-panel">
                            <h5>Size & Pricing</h5>
                            <div id="size-selection-container">
                                ${this.canShowSizes() ? this.renderSizeSelection() : '<p class="text-muted">Complete your selections to see sizes</p>'}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <div id="selection-summary" class="selection-summary">
                            ${this.renderSelectionSummary()}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = hybridHTML;
    }

    renderDesktopWithCards(container) {
        const cardHTML = `
            <div class="desktop-card-interface">
                <div class="row">
                    <div class="col-12">
                        <div class="selection-panel">
                            <h5>Select Product Type</h5>
                            <div class="product-type-grid desktop-cards">
                                ${this.productTypes.map(type => `
                                    <div class="product-type-card ${this.currentSelections.productType?.id === type.id ? 'selected' : ''}" 
                                         onclick="orderingSystem.selectProductType(${type.id})">
                                        <h6>${type.name}</h6>
                                        <small class="text-muted">${type.max_sub_option_levels} option levels</small>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
                
                ${this.currentSelections.productType ? `
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="selection-panel">
                            <h5>Options</h5>
                            <div id="sub-option-1-container">
                                ${this.renderSubOption1Panel()}
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="selection-panel">
                            <h5>Additional Options</h5>
                            <div id="sub-option-2-container">
                                ${this.shouldShowSubOption2() ? this.renderSubOption2Panel() : '<p class="text-muted">Additional options will appear here</p>'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="selection-panel">
                            <h5>Size & Pricing</h5>
                            <div id="size-selection-container">
                                ${this.canShowSizes() ? this.renderSizeSelection() : '<p class="text-muted">Complete your selections to see sizes</p>'}
                            </div>
                        </div>
                    </div>
                </div>
                ` : ''}
                
                ${this.currentSelections.selectedProduct ? `
                <div class="row mt-4">
                    <div class="col-12">
                        <div class="selection-summary">
                            ${this.renderSelectionSummary()}
                            <button class="btn btn-success btn-lg mt-3" onclick="addToCart()">
                                <i class="fas fa-cart-plus"></i> Add to Cart
                            </button>
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        
        container.innerHTML = cardHTML;
    }

    renderProductTypeStep() {
        return `
            <h4>Select Product Type</h4>
            <div class="product-type-grid">
                ${this.productTypes.map(type => `
                    <div class="product-type-card ${this.currentSelections.productType?.id === type.id ? 'selected' : ''}" 
                         onclick="orderingSystem.selectProductType(${type.id})">
                        <h6>${type.name}</h6>
                        <small class="text-muted">${type.max_sub_option_levels} option levels</small>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderSubOption1Step() {
        if (!this.currentSelections.productType) {
            return '<div class="alert alert-warning">Please select a product type first</div>';
        }
        
        return `
            <h4>Select ${this.getSubOption1Label()}</h4>
            <div id="sub-option-1-mobile-content">
                <div class="loading-spinner">Loading options...</div>
            </div>
        `;
    }

    renderSubOption2Step() {
        if (!this.shouldShowSubOption2()) {
            return '<div class="alert alert-warning">Please complete previous selections first</div>';
        }
        
        return `
            <h4>Select ${this.getSubOption2Label()}</h4>
            <div id="sub-option-2-mobile-content">
                <div class="loading-spinner">Loading options...</div>
            </div>
        `;
    }

    renderSizeSelectionStep() {
        if (!this.canShowSizes()) {
            return '<div class="alert alert-warning">Please complete your selections first</div>';
        }
        
        return `
            <h4>Select Size & Pricing</h4>
            <div id="size-selection-mobile-content">
                <div class="loading-spinner">Loading sizes...</div>
            </div>
        `;
    }

    getSubOption1Label() {
        const productType = this.currentSelections.productType;
        if (!productType) return 'Option';
        
        switch (productType.id) {
            case 1: return 'Mounting Size';
            case 2: return 'Frame Size';
            case 3: case 5: return 'Paper Type';
            case 4: return 'Frame Size';
            default: return 'Option';
        }
    }

    getSubOption2Label() {
        const productType = this.currentSelections.productType;
        if (!productType) return 'Option';
        
        switch (productType.id) {
            case 2: return 'Frame Color';
            case 4: return 'Mat Size';
            default: return 'Option';
        }
    }

    renderProductTypeDropdown() {
        return `
            <select class="form-select" id="product-type-select" onchange="orderingSystem.selectProductType(this.value)" style="padding: 8px 35px 8px 12px !important; font-size: 0.85rem !important; background-position: right 10px center !important;">
                <option value="">Select Product Type</option>
                ${this.productTypes.map(type => `
                    <option value="${type.id}" ${this.currentSelections.productType?.id == type.id ? 'selected' : ''}>
                        ${type.name}
                    </option>
                `).join('')}
            </select>
        `;
    }

    async selectProductType(productTypeId) {
        const productType = this.productTypes.find(pt => pt.id == productTypeId);
        this.currentSelections.productType = productType;
        this.currentSelections.subOption1 = null;
        this.currentSelections.subOption2 = null;
        this.currentSelections.selectedProduct = null;
        
        // Always advance to next step when product type is selected
        if (productType) {
            this.currentStep = 2;
            this.maxSteps = 2 + productType.max_sub_option_levels;
        }
        
        this.renderInterface();
    }

    renderSubOption1Panel() {
        if (!this.currentSelections.productType) return '';
        
        const productType = this.currentSelections.productType;
        
        if (productType.max_sub_option_levels === 0) {
            return '<p class="text-muted">No additional options needed</p>';
        }
        
        return `
            <div id="sub-option-1-loading">Loading options...</div>
            <div id="sub-option-1-content" style="display: none;"></div>
        `;
    }

    renderSubOption2Panel() {
        return `
            <div id="sub-option-2-loading">Loading options...</div>
            <div id="sub-option-2-content" style="display: none;"></div>
        `;
    }

    renderSizeSelection() {
        return `
            <div id="size-selection-loading">Loading sizes...</div>
            <div id="size-selection-content" style="display: none;"></div>
        `;
    }

    async loadSubOption1() {
        if (!this.currentSelections.productType) return;
        
        try {
            const response = await fetch(`/api/hierarchical/sub-options/${this.currentSelections.productType.id}/1`);
            const data = await response.json();
            
            if (data.success) {
                this.renderSubOption1Content(data.sub_options);
            }
        } catch (error) {
            console.error('Error loading sub-options:', error);
        }
    }

    async loadSubOption2() {
        if (!this.currentSelections.productType || !this.currentSelections.subOption1) return;
        
        try {
            const response = await fetch(`/api/hierarchical/sub-options/${this.currentSelections.productType.id}/2`);
            const data = await response.json();
            
            if (data.success) {
                this.renderSubOption2Content(data.sub_options);
            }
        } catch (error) {
            console.error('Error loading sub-options level 2:', error);
        }
    }

    async loadAvailableSizes() {
        if (!this.currentSelections.productType) return;
        
        try {
            let url = `/api/hierarchical/available-sizes?product_type_id=${this.currentSelections.productType.id}`;
            
            if (this.currentSelections.subOption1) {
                url += `&sub_option_1_id=${this.currentSelections.subOption1.id}`;
            }
            
            if (this.currentSelections.subOption2) {
                url += `&sub_option_2_id=${this.currentSelections.subOption2.id}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                this.renderSizeSelectionContent(data.products);
            }
        } catch (error) {
            console.error('Error loading available sizes:', error);
        }
    }

    renderSubOption1Content(subOptions) {
        const containers = ['sub-option-1-content', 'sub-option-1-mobile-content'];
        const optionType = subOptions[0]?.option_type;
        
        let html = '';
        
        if (optionType === 'frame_color' || optionType === 'paper_type') {
            // Render as visual cards for colors and paper types
            html = `
                <div class="visual-options-grid">
                    ${subOptions.map(option => `
                        <div class="visual-option-card ${this.currentSelections.subOption1?.id === option.id ? 'selected' : ''}"
                             onclick="orderingSystem.selectSubOption1(${option.id})">
                            ${option.image_path ? `<img src="${option.image_path}" alt="${option.value}" class="option-image">` : ''}
                            <div class="option-label">${option.value}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            // Render as dropdown for technical options
            html = `
                <select class="form-select" onchange="orderingSystem.selectSubOption1(this.value)" style="padding: 8px 35px 8px 12px !important; font-size: 0.85rem !important; background-position: right 10px center !important;">
                    <option value="">Select ${subOptions[0]?.name || 'Option'}</option>
                    ${subOptions.map(option => `
                        <option value="${option.id}" ${this.currentSelections.subOption1?.id == option.id ? 'selected' : ''}>
                            ${option.value}
                        </option>
                    `).join('')}
                </select>
            `;
        }
        
        containers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = html;
            }
        });
        
        // Hide loading, show content
        this.hideLoading('sub-option-1');
    }

    renderSubOption2Content(subOptions) {
        const containers = ['sub-option-2-content', 'sub-option-2-mobile-content'];
        const optionType = subOptions[0]?.option_type;
        
        let html = '';
        
        if (optionType === 'frame_color') {
            // Render as visual cards for frame colors
            html = `
                <div class="visual-options-grid">
                    ${subOptions.map(option => `
                        <div class="visual-option-card ${this.currentSelections.subOption2?.id === option.id ? 'selected' : ''}"
                             onclick="orderingSystem.selectSubOption2(${option.id})">
                            ${option.image_path ? `<img src="${option.image_path}" alt="${option.value}" class="option-image">` : ''}
                            <div class="option-label">${option.value}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            // Render as dropdown for mat sizes and other technical options
            html = `
                <select class="form-select" onchange="orderingSystem.selectSubOption2(this.value)" style="padding: 8px 35px 8px 12px !important; font-size: 0.85rem !important; background-position: right 10px center !important;">
                    <option value="">Select ${subOptions[0]?.name || 'Option'}</option>
                    ${subOptions.map(option => `
                        <option value="${option.id}" ${this.currentSelections.subOption2?.id == option.id ? 'selected' : ''}>
                            ${option.value}
                        </option>
                    `).join('')}
                </select>
            `;
        }
        
        containers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = html;
            }
        });
        
        // Hide loading, show content
        this.hideLoading('sub-option-2');
    }

    renderSizeSelectionContent(products) {
        const containers = ['size-selection-content', 'size-selection-mobile-content'];
        
        const html = `
            <div class="size-selection-grid">
                ${products.map(product => `
                    <div class="size-option-card ${this.currentSelections.selectedProduct?.id === product.id ? 'selected' : ''}"
                         onclick="orderingSystem.selectProduct(${product.id})">
                        <div class="size-label">${product.size}</div>
                        <div class="size-price">$${product.customer_price}</div>
                        <div class="size-category">${product.category_name}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        containers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = html;
            }
        });
        
        // Hide loading, show content
        this.hideLoading('size-selection');
    }

    hideLoading(prefix) {
        const loadingElements = document.querySelectorAll(`[id^="${prefix}-loading"]`);
        const contentElements = document.querySelectorAll(`[id^="${prefix}-content"]`);
        
        loadingElements.forEach(el => el.style.display = 'none');
        contentElements.forEach(el => el.style.display = 'block');
    }

    async selectSubOption1(subOptionId) {
        try {
            const response = await fetch(`/api/hierarchical/sub-options/${this.currentSelections.productType.id}/1`);
            const data = await response.json();
            
            if (data.success) {
                const subOption = data.sub_options.find(opt => opt.id == subOptionId);
                this.currentSelections.subOption1 = subOption;
                this.currentSelections.subOption2 = null;
                this.currentSelections.selectedProduct = null;
                
                if (this.isMobile) {
                    this.currentStep = this.currentSelections.productType.max_sub_option_levels >= 2 ? 3 : 4;
                }
                
                this.renderInterface();
            }
        } catch (error) {
            console.error('Error selecting sub-option 1:', error);
        }
    }

    async selectSubOption2(subOptionId) {
        try {
            const response = await fetch(`/api/hierarchical/sub-options/${this.currentSelections.productType.id}/2`);
            const data = await response.json();
            
            if (data.success) {
                const subOption = data.sub_options.find(opt => opt.id == subOptionId);
                this.currentSelections.subOption2 = subOption;
                this.currentSelections.selectedProduct = null;
                
                if (this.isMobile) {
                    this.currentStep = 4;
                }
                
                this.renderInterface();
            }
        } catch (error) {
            console.error('Error selecting sub-option 2:', error);
        }
    }

    async selectProduct(productId) {
        try {
            const response = await fetch(`/api/hierarchical/product-details/${productId}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentSelections.selectedProduct = data.product;
                this.renderInterface();
            }
        } catch (error) {
            console.error('Error selecting product:', error);
        }
    }

    shouldShowSubOption2() {
        return this.currentSelections.productType?.max_sub_option_levels >= 2 && 
               this.currentSelections.subOption1;
    }

    canShowSizes() {
        const productType = this.currentSelections.productType;
        if (!productType) return false;
        
        if (productType.max_sub_option_levels === 0) return true;
        if (productType.max_sub_option_levels === 1) return !!this.currentSelections.subOption1;
        if (productType.max_sub_option_levels === 2) return !!(this.currentSelections.subOption1 && this.currentSelections.subOption2);
        
        return false;
    }

    canAdvanceStep() {
        switch (this.currentStep) {
            case 1: return !!this.currentSelections.productType;
            case 2: return !!this.currentSelections.subOption1 || this.currentSelections.productType?.max_sub_option_levels === 0;
            case 3: return !!this.currentSelections.subOption2 || this.currentSelections.productType?.max_sub_option_levels < 2;
            case 4: return !!this.currentSelections.selectedProduct;
            default: return false;
        }
    }

    renderSelectionSummary() {
        const selections = [];
        
        if (this.currentSelections.productType) {
            selections.push(`Product: ${this.currentSelections.productType.name}`);
        }
        
        if (this.currentSelections.subOption1) {
            selections.push(`${this.getSubOption1Label()}: ${this.currentSelections.subOption1.value}`);
        }
        
        if (this.currentSelections.subOption2) {
            selections.push(`${this.getSubOption2Label()}: ${this.currentSelections.subOption2.value}`);
        }
        
        if (this.currentSelections.selectedProduct) {
            selections.push(`Size: ${this.currentSelections.selectedProduct.size}`);
            selections.push(`Price: $${this.currentSelections.selectedProduct.customer_price}`);
        }
        
        if (selections.length > 0) {
            return `
                <div class="alert alert-info">
                    <strong>Current Selection:</strong> ${selections.join(' • ')}
                    ${this.currentSelections.selectedProduct ? '<button class="btn btn-success btn-sm ms-3" onclick="addToCart()"><i class="fas fa-cart-plus"></i> Add to Cart</button>' : ''}
                </div>
            `;
        } else {
            return '<div class="alert alert-secondary">Make your selections above</div>';
        }
    }

    nextStep() {
        if (this.currentStep < this.maxSteps && this.canAdvanceStep()) {
            this.currentStep++;
            this.renderInterface();
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.renderInterface();
        }
    }

    resetSelections() {
        this.currentSelections = {
            productType: null,
            subOption1: null,
            subOption2: null,
            selectedProduct: null
        };
        this.currentStep = 1;
        this.renderInterface();
    }
}

// Initialize the ordering system when the page loads
let orderingSystem;
document.addEventListener('DOMContentLoaded', function() {
    orderingSystem = new HierarchicalOrderingSystem();
});

// Global function for adding to cart (to be implemented)
function addToCart() {
    if (orderingSystem.currentSelections.selectedProduct) {
        // Implementation for adding to cart
        console.log('Adding to cart:', orderingSystem.currentSelections);
        
        // Call the cart function from the main page
        if (typeof window.addToCart === 'function') {
            window.addToCart();
        } else {
            alert('Product selected! Cart functionality will be implemented.');
        }
    } else {
        alert('Please complete your selection first.');
    }
}
