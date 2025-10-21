// SIMPLIFIED FIX - Direct DOM manipulation
class HierarchicalOrderingSystemFixed {
    constructor() {
        this.currentSelections = {
            productType: null,
            subOption1: null,
            subOption2: null,
            selectedProduct: null
        };
        this.currentStep = 1;
        this.maxSteps = 4;
        this.init();
    }

    init() {
        this.loadProductTypes();
    }

    async loadProductTypes() {
        try {
            const response = await fetch('/api/hierarchical/product-types');
            const data = await response.json();
            if (data.success) {
                this.productTypes = data.product_types;
                this.renderInterface();
            }
        } catch (error) {
            console.error('Error loading product types:', error);
        }
    }

    renderInterface() {
        const container = document.getElementById('ordering-container');
        const wizardHTML = `
            <div class="wizard-progress mb-4">
                <div class="progress">
                    <div class="progress-bar" style="width: ${(this.currentStep / this.maxSteps) * 100}%"></div>
                </div>
                <small class="text-muted">Step ${this.currentStep} of ${this.maxSteps}</small>
            </div>
            
            <div class="wizard-content">
                ${this.renderCurrentStep()}
            </div>
            
            <div class="wizard-navigation mt-4">
                ${this.currentStep > 1 ? '<button class="btn btn-secondary" onclick="orderingSystem.prevStep()">Previous</button>' : ''}
            </div>
        `;
        container.innerHTML = wizardHTML;
    }

    renderCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return this.renderStep1();
            case 2:
                return this.renderStep2();
            case 3:
                return this.renderStep3();
            case 4:
                return this.renderStep4();
            default:
                return '<div>Invalid step</div>';
        }
    }

    renderStep1() {
        return `
            <h4>Select Product Type</h4>
            <div class="product-types">
                ${this.productTypes.map(type => `
                    <div class="product-card ${this.currentSelections.productType?.id === type.id ? 'selected' : ''}"
                         onclick="orderingSystem.selectProductType(${type.id})">
                        <h5>${type.name}</h5>
                        <small>${type.max_sub_option_levels} option levels</small>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderStep2() {
        if (!this.currentSelections.productType) return '<div>Please select a product type first</div>';
        
        return `
            <h4>Select Frame Size</h4>
            <div id="step2-content">
                <select class="form-select" onchange="orderingSystem.selectSubOption1(this.value)">
                    <option value="">Select Frame Size</option>
                    <option value="4">0.75" Frame</option>
                    <option value="5">1.25" Frame</option>
                </select>
            </div>
        `;
    }

    renderStep3() {
        if (!this.currentSelections.subOption1) return '<div>Please select frame size first</div>';
        
        return `
            <h4>Select Frame Color</h4>
            <div class="frame-colors">
                <div class="color-option" onclick="orderingSystem.selectSubOption2(11)">
                    <div class="color-preview" style="background: white; border: 1px solid #ccc;"></div>
                    <span>White</span>
                </div>
                <div class="color-option" onclick="orderingSystem.selectSubOption2(12)">
                    <div class="color-preview" style="background: black;"></div>
                    <span>Black</span>
                </div>
            </div>
        `;
    }

    renderStep4() {
        if (!this.currentSelections.subOption2) return '<div>Please select frame color first</div>';
        
        return `
            <h4>Select Size</h4>
            <div id="step4-content">
                <div class="loading-message">Loading sizes...</div>
            </div>
        `;
    }

    selectProductType(typeId) {
        this.currentSelections.productType = this.productTypes.find(t => t.id == typeId);
        this.currentStep = 2;
        this.renderInterface();
    }

    selectSubOption1(optionId) {
        if (!optionId) return;
        this.currentSelections.subOption1 = { id: optionId };
        this.currentStep = 3;
        this.renderInterface();
    }

    selectSubOption2(optionId) {
        this.currentSelections.subOption2 = { id: optionId };
        this.currentStep = 4;
        this.renderInterface();
        // IMMEDIATELY load sizes after rendering step 4
        setTimeout(() => this.loadSizesDirectly(), 100);
    }

    async loadSizesDirectly() {
        const contentDiv = document.getElementById('step4-content');
        if (!contentDiv) return;

        try {
            const url = `/api/hierarchical/available-sizes?product_type_id=2&sub_option_1_id=${this.currentSelections.subOption1.id}&sub_option_2_id=${this.currentSelections.subOption2.id}`;
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success && data.products.length > 0) {
                const sizesHTML = `
                    <div class="sizes-grid">
                        ${data.products.map(product => `
                            <div class="size-card" onclick="orderingSystem.selectProduct(${product.id})">
                                <h5>${product.size}</h5>
                                <div class="price">$${product.customer_price}</div>
                                <small>${product.category_name}</small>
                            </div>
                        `).join('')}
                    </div>
                `;
                contentDiv.innerHTML = sizesHTML;
            } else {
                contentDiv.innerHTML = '<div class="alert alert-warning">No sizes available for this combination</div>';
            }
        } catch (error) {
            console.error('Error loading sizes:', error);
            contentDiv.innerHTML = '<div class="alert alert-danger">Error loading sizes</div>';
        }
    }

    selectProduct(productId) {
        // Handle product selection
        console.log('Product selected:', productId);
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.renderInterface();
        }
    }
}

// Initialize the system
let orderingSystem;
document.addEventListener('DOMContentLoaded', function() {
    orderingSystem = new HierarchicalOrderingSystemFixed();
});
