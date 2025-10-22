/**
 * Hierarchical Ordering System V2
 * Works with simplified Lumaprints database structure
 * No sub_options - direct product queries by category and size
 */

class HierarchicalOrderingSystemV2 {
    constructor() {
        this.productTypes = [];
        this.categories = [];
        this.sizes = [];
        this.currentSelections = {
            productType: null,
            category: null,
            size: null,
            product: null
        };
        this.globalMarkup = 0;
        
        this.init();
    }

    async init() {
        await this.loadProductTypes();
        this.renderInterface();
    }

    async loadProductTypes() {
        try {
            const response = await fetch('/api/hierarchical/v2/product-types');
            const data = await response.json();
            
            if (data.success) {
                this.productTypes = data.product_types;
            } else {
                console.error('Failed to load product types:', data.error);
                this.showError('Failed to load product types. Please refresh the page.');
            }
        } catch (error) {
            console.error('Error loading product types:', error);
            this.showError('Network error. Please check your connection and refresh the page.');
        }
    }

    async loadCategories(productTypeId) {
        try {
            const response = await fetch(`/api/hierarchical/v2/categories?product_type_id=${productTypeId}`);
            const data = await response.json();
            
            if (data.success) {
                this.categories = data.categories;
                this.currentSelections.category = null;
                this.currentSelections.size = null;
                this.currentSelections.product = null;
                this.sizes = [];
                this.renderInterface();
            } else {
                console.error('Failed to load categories:', data.error);
                this.showError('Failed to load categories.');
            }
        } catch (error) {
            console.error('Error loading categories:', error);
            this.showError('Network error loading categories.');
        }
    }

    async loadSizes(categoryId) {
        try {
            const response = await fetch(`/api/hierarchical/v2/sizes?category_id=${categoryId}`);
            const data = await response.json();
            
            if (data.success) {
                this.sizes = data.sizes;
                this.globalMarkup = data.global_markup || 0;
                this.currentSelections.size = null;
                this.currentSelections.product = null;
                this.renderInterface();
            } else {
                console.error('Failed to load sizes:', data.error);
                this.showError('Failed to load sizes.');
            }
        } catch (error) {
            console.error('Error loading sizes:', error);
            this.showError('Network error loading sizes.');
        }
    }

    async loadProduct(categoryId, size) {
        try {
            const response = await fetch(`/api/hierarchical/v2/product?category_id=${categoryId}&size=${size}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentSelections.product = data.product;
                this.globalMarkup = data.global_markup || 0;
                this.renderInterface();
            } else {
                console.error('Failed to load product:', data.error);
                this.showError('Failed to load product details.');
            }
        } catch (error) {
            console.error('Error loading product:', error);
            this.showError('Network error loading product.');
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
        
        let html = `
            <div class="hierarchical-wizard">
                ${this.renderProductTypeSelector()}
                ${this.currentSelections.productType ? this.renderCategorySelector() : ''}
                ${this.currentSelections.category ? this.renderSizeSelector() : ''}
                ${this.currentSelections.product ? this.renderProductSummary() : ''}
            </div>
        `;
        
        container.innerHTML = html;
    }

    renderProductTypeSelector() {
        const selected = this.currentSelections.productType;
        
        let html = `
            <div class="wizard-step ${selected ? 'completed' : 'active'}">
                <div class="step-header">
                    <h4><span class="step-number">1</span> Select Product Type</h4>
                </div>
                <div class="step-content">
                    <div class="option-grid">
        `;
        
        this.productTypes.forEach(type => {
            const isSelected = selected && selected.id === type.id;
            html += `
                <div class="option-card ${isSelected ? 'selected' : ''}" 
                     onclick="orderingSystem.selectProductType(${type.id}, '${type.name}')">
                    <div class="option-name">${type.name}</div>
                    ${isSelected ? '<i class="fas fa-check-circle"></i>' : ''}
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
        
        return html;
    }

    renderCategorySelector() {
        if (this.categories.length === 0) {
            return '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading options...</div>';
        }
        
        const selected = this.currentSelections.category;
        
        let html = `
            <div class="wizard-step ${selected ? 'completed' : 'active'}">
                <div class="step-header">
                    <h4><span class="step-number">2</span> Select Option</h4>
                </div>
                <div class="step-content">
                    <div class="option-grid">
        `;
        
        this.categories.forEach(category => {
            const isSelected = selected && selected.id === category.id;
            html += `
                <div class="option-card ${isSelected ? 'selected' : ''}" 
                     onclick="orderingSystem.selectCategory(${category.id}, '${category.name}')">
                    <div class="option-name">${category.name}</div>
                    ${isSelected ? '<i class="fas fa-check-circle"></i>' : ''}
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
        
        return html;
    }

    renderSizeSelector() {
        if (this.sizes.length === 0) {
            return '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading sizes...</div>';
        }
        
        const selected = this.currentSelections.size;
        
        let html = `
            <div class="wizard-step ${selected ? 'completed' : 'active'}">
                <div class="step-header">
                    <h4><span class="step-number">3</span> Select Size</h4>
                </div>
                <div class="step-content">
                    <div class="size-grid">
        `;
        
        this.sizes.forEach(sizeData => {
            const isSelected = selected === sizeData.size;
            html += `
                <div class="size-card ${isSelected ? 'selected' : ''}" 
                     onclick="orderingSystem.selectSize('${sizeData.size}')">
                    <div class="size-name">${sizeData.size}"</div>
                    <div class="size-price">$${sizeData.retail_price.toFixed(2)}</div>
                    ${isSelected ? '<i class="fas fa-check-circle"></i>' : ''}
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
        
        return html;
    }

    renderProductSummary() {
        const product = this.currentSelections.product;
        
        return `
            <div class="wizard-step active">
                <div class="step-header">
                    <h4><span class="step-number">4</span> Confirm Selection</h4>
                </div>
                <div class="step-content">
                    <div class="product-summary">
                        <h5>${product.name}</h5>
                        <div class="summary-details">
                            <p><strong>Product Type:</strong> ${product.product_type}</p>
                            <p><strong>Option:</strong> ${product.category}</p>
                            <p><strong>Size:</strong> ${product.size}"</p>
                            <p class="price-display"><strong>Price:</strong> $${product.retail_price.toFixed(2)}</p>
                        </div>
                        <div class="action-buttons">
                            <button class="btn btn-primary btn-lg" onclick="orderingSystem.addToCart()">
                                <i class="fas fa-shopping-cart"></i> Add to Cart
                            </button>
                            <button class="btn btn-secondary" onclick="orderingSystem.reset()">
                                <i class="fas fa-redo"></i> Start Over
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    selectProductType(id, name) {
        this.currentSelections.productType = { id, name };
        this.loadCategories(id);
    }

    selectCategory(id, name) {
        this.currentSelections.category = { id, name };
        this.loadSizes(id);
    }

    selectSize(size) {
        this.currentSelections.size = size;
        this.loadProduct(this.currentSelections.category.id, size);
    }

    addToCart() {
        const product = this.currentSelections.product;
        
        // Get image name from URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const imageName = urlParams.get('image');
        
        if (!imageName) {
            alert('Error: No image selected. Please go back and select an image.');
            return;
        }
        
        // Create cart item
        const cartItem = {
            image: imageName,
            product_id: product.id,
            product_name: product.name,
            size: product.size,
            price: product.retail_price,
            quantity: 1
        };
        
        // Add to cart (implement your cart logic here)
        console.log('Adding to cart:', cartItem);
        
        // For now, show success message
        alert(`Added ${product.name} to cart!\n\nPrice: $${product.retail_price.toFixed(2)}`);
        
        // Optionally redirect to cart or reset
        this.reset();
    }

    reset() {
        this.currentSelections = {
            productType: null,
            category: null,
            size: null,
            product: null
        };
        this.categories = [];
        this.sizes = [];
        this.renderInterface();
    }
}

// Initialize when DOM is ready
let orderingSystem;
document.addEventListener('DOMContentLoaded', () => {
    orderingSystem = new HierarchicalOrderingSystemV2();
});

