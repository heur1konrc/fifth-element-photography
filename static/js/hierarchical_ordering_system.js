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
        this.maxSteps = 4; // Default, will be updated based on product type selection
        
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
        
        // Add event listeners for wizard navigation
        this.setupWizardNavigation();
    }

    setupWizardNavigation() {
        // Add event listeners for wizard navigation buttons
        const prevBtn = document.querySelector('.wizard-prev');
        const nextBtn = document.querySelector('.wizard-next');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prevStep());
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextStep());
        }
    }

    renderWizardStep() {
        // Dynamic step routing based on product type option levels
        if (this.currentStep === 1) {
            return this.renderProductTypeStep();
        }
        
        if (!this.currentSelections.productType) {
            return '<div class="alert alert-warning">Please select a product type first</div>';
        }
        
        const optionLevels = this.currentSelections.productType.max_sub_option_levels;
        
        // For products with 0 option levels (Metal, Rolled Canvas)
        if (optionLevels === 0 && this.currentStep === 2) {
            return this.renderSizeSelectionStep();
        }
        
        // For products with 1 option level (Canvas, Fine Art Paper)
        if (optionLevels === 1) {
            if (this.currentStep === 2) return this.renderSubOption1Step();
            if (this.currentStep === 3) return this.renderSizeSelectionStep();
        }
        
        // For products with 2 option levels (Framed Canvas, Framed Fine Art Paper)
        if (optionLevels === 2) {
            if (this.currentStep === 2) return this.renderSubOption1Step();
            if (this.currentStep === 3) return this.renderSubOption2Step();
            if (this.currentStep === 4) return this.renderSizeSelectionStep();
        }
        
        return '<div class="alert alert-danger">Invalid step configuration</div>';
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
                            <h5>Select Size</h5>
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
                            <h5>Select Size</h5>
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
        console.log('renderSizeSelectionStep called');
        console.log('canShowSizes:', this.canShowSizes());
        console.log('currentSelections:', this.currentSelections);
        
        // Force load sizes immediately when step 4 renders
        if (this.canShowSizes()) {
            setTimeout(() => this.loadAvailableSizes(), 100);
        }
        
        // Always show the step, but content depends on canShowSizes
        return `
            <h4>Select Size</h4>
            <div id="size-selection-mobile-content">
                ${this.canShowSizes() ? 
                    '<select class="form-select" id="size-dropdown" onchange="orderingSystem.selectProductFromDropdown(this.value)"><option value="">Loading sizes...</option></select>' : 
                    '<div class="alert alert-warning">Please complete your selections first</div>'
                }
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
            console.log('DEBUG: Loading sizes from URL:', url);
            
            const response = await fetch(url);
            const data = await response.json();
            console.log('DEBUG: API Response:', data);
            
            if (data.success) {
                console.log('DEBUG: Calling renderSizeSelectionContent with', data.products.length, 'products');
                this.renderSizeSelectionContent(data.products);
            } else {
                console.log('DEBUG: API returned success=false:', data);
            }
        } catch (error) {
            console.error('Error loading available sizes:', error);
        }
    }

    renderSubOption1Content(subOptions) {
        const containers = ['sub-option-1-content', 'sub-option-1-mobile-content'];
        const optionType = subOptions[0]?.option_type;
        
        let html = '';
        
        if (optionType === 'frame_color' || optionType === 'paper_type' || optionType === 'frame_size') {
            // Render as visual cards for colors, paper types, and frame sizes
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
                container.style.display = 'block';
                // Hide the loading message
                const loadingElement = document.getElementById(containerId.replace('-content', '-loading'));
                if (loadingElement) {
                    loadingElement.style.display = 'none';
                }
            }
        });
    }

    renderSubOption2Content(subOptions) {
        const containers = ['sub-option-2-content', 'sub-option-2-mobile-content'];
        const optionType = subOptions[0]?.option_type;
        
        let html = '';
        
        if (optionType === 'frame_color' || optionType === 'frame_size') {
            // Render as visual cards for frame colors and frame sizes
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
                container.style.display = 'block';
                // Hide the loading message
                const loadingElement = document.getElementById(containerId.replace('-content', '-loading'));
                if (loadingElement) {
                    loadingElement.style.display = 'none';
                }
            }
        });
    }

    renderSizeSelectionContent(products) {
        console.log('DEBUG: renderSizeSelectionContent called with', products.length, 'products');
        const dropdown = document.getElementById('size-dropdown');
        console.log('DEBUG: Found dropdown element:', dropdown);
        
        if (dropdown) {
            const options = `
                <option value="">Select Size & Pricing</option>
                ${products.map(product => `
                    <option value="${product.id}">${product.size} - $${product.customer_price} (${product.category_name})</option>
                `).join('')}
            `;
            console.log('DEBUG: Setting dropdown innerHTML to:', options);
            dropdown.innerHTML = options;
            console.log('DEBUG: Dropdown updated successfully');
        } else {
            console.error('DEBUG: size-dropdown element not found!');
        }
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
                
                // Always advance to next step when sub-option 1 is selected
                this.currentStep = 3;
                
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
                
                // Always advance to step 4 when sub-option 2 is selected
                this.currentStep = 4;
                
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
                // Don't call renderInterface() to avoid infinite loop
                // Just update the Add to Cart button visibility
                this.updateAddToCartButton();
            }
        } catch (error) {
            console.error('Error selecting product:', error);
        }
    }

    updateAddToCartButton() {
        // Find existing Add to Cart button and update its visibility
        const existingButton = document.querySelector('button[onclick="addToCart()"]');
        const buttonContainer = document.querySelector('.wizard-navigation') || document.querySelector('.text-center');
        
        if (this.currentSelections.selectedProduct && buttonContainer) {
            if (!existingButton) {
                // Create Add to Cart button if it doesn't exist
                const addToCartBtn = document.createElement('button');
                addToCartBtn.className = 'btn btn-success ms-2';
                addToCartBtn.onclick = () => addToCart();
                addToCartBtn.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
                buttonContainer.appendChild(addToCartBtn);
            } else {
                existingButton.style.display = 'inline-block';
            }
        } else if (existingButton) {
            existingButton.style.display = 'none';
        }
    }

    selectProductFromDropdown(productId) {
        if (!productId) {
            this.currentSelections.selectedProduct = null;
            return;
        }
        
        // Use the existing selectProduct function
        this.selectProduct(productId);
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

// Global function for adding to cart with Lumaprints integration
function addToCart() {
    if (orderingSystem.currentSelections.selectedProduct) {
        const product = orderingSystem.currentSelections.selectedProduct;
        const selections = orderingSystem.currentSelections;
        
        // Prepare order data with Lumaprints codes for OrderDesk
        const orderData = {
            // Product information
            product_id: product.id,
            product_name: product.name,
            size: product.size,
            price: product.customer_price,
            cost_price: product.cost_price,
            
            // Selection details
            product_type: selections.productType?.name || '',
            sub_option_1: selections.subOption1?.value || '',
            sub_option_2: selections.subOption2?.value || '',
            
            // LUMAPRINTS INTEGRATION - Critical for OrderDesk
            lumaprints_subcategory_id: product.lumaprints_subcategory_id,
            lumaprints_options: product.lumaprints_options || [],
            lumaprints_frame_option: product.lumaprints_frame_option,
            
            // Image information (from URL parameter)
            image_filename: new URLSearchParams(window.location.search).get('image') || ''
        };
        
        console.log('🛒 Adding to cart with Lumaprints codes:', orderData);
        
        // Try to call existing cart system first
        if (typeof window.addProductToCart === 'function') {
            window.addProductToCart(orderData);
        } else if (typeof window.addToCart === 'function') {
            window.addToCart(orderData);
        } else {
            // Fallback: Add to local cart or show success message
            addToLocalCart(orderData);
        }
    } else {
        alert('Please complete your selection first.');
    }
}

// Fallback cart function for when main cart system isn't available
function addToLocalCart(orderData) {
    // Get existing cart from localStorage
    let cart = JSON.parse(localStorage.getItem('hierarchical_cart') || '[]');
    
    // Add new item to cart
    const cartItem = {
        id: Date.now(), // Unique ID for cart item
        ...orderData,
        quantity: 1,
        added_at: new Date().toISOString()
    };
    
    cart.push(cartItem);
    localStorage.setItem('hierarchical_cart', JSON.stringify(cart));
    
    // Show success message
    const message = `✅ Added to cart: ${orderData.product_name} (${orderData.size}) - $${orderData.price}`;
    if (orderData.lumaprints_subcategory_id) {
        console.log(`🏷️ Lumaprints Code: ${orderData.lumaprints_subcategory_id}`);
    }
    
    alert(message);
    
    // Optional: Update cart display if function exists
    if (typeof updateCartDisplay === 'function') {
        updateCartDisplay();
    }
}
