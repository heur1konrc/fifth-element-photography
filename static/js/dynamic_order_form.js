/**
 * Dynamic Order Form - Adapts to product complexity
 * Builds 2-10 selection boxes based on product structure
 */

class DynamicOrderForm {
    constructor() {
        this.currentCategory = null;
        this.currentSubcategory = null;
        this.selectedOptions = {};
        this.selectionBoxes = [];
        this.init();
    }
    
    async init() {
        try {
            await this.loadCategories();
        } catch (error) {
            this.showError('Failed to load form: ' + error.message);
        }
    }
    
    async loadCategories() {
        const response = await fetch('/api/order-form/categories');
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        document.getElementById('loading').classList.add('hidden');
        this.createCategoryBox(data.categories);
    }
    
    createCategoryBox(categories) {
        const container = document.getElementById('selection-boxes');
        container.innerHTML = '';
        
        const box = this.createSelectionBox(
            'category',
            '1. Select Product Category',
            categories.map(cat => ({
                value: cat.id,
                label: cat.name
            })),
            (value) => this.onCategoryChange(value)
        );
        
        container.appendChild(box);
    }
    
    async onCategoryChange(categoryId) {
        this.currentCategory = parseInt(categoryId);
        this.clearSelectionsAfter(1);
        
        try {
            // Get complete product structure for this category
            const response = await fetch(`/api/order-form/product-structure/${categoryId}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error);
            }
            
            this.buildFormForCategory(data.structure);
            
        } catch (error) {
            this.showError('Failed to load product options: ' + error.message);
        }
    }
    
    buildFormForCategory(structure) {
        const container = document.getElementById('selection-boxes');
        
        // Determine form complexity based on subcategories
        const hasMultipleSubcategories = structure.subcategories.length > 1;
        const firstSubcat = structure.subcategories[0];
        const hasOptions = firstSubcat && firstSubcat.option_groups.length > 0;
        
        if (hasMultipleSubcategories) {
            // Box 2: Subcategory selection
            this.createSubcategoryBox(structure.subcategories);
        } else if (structure.subcategories.length === 1) {
            // Only one subcategory - auto-select it and show options
            this.currentSubcategory = firstSubcat.id;
            
            if (hasOptions) {
                this.createOptionBoxes(firstSubcat.option_groups);
            }
            
            // Always show size selection
            this.createSizeBox(firstSubcat);
        }
    }
    
    createSubcategoryBox(subcategories) {
        const container = document.getElementById('selection-boxes');
        
        const box = this.createSelectionBox(
            'subcategory',
            '2. Select Product Type',
            subcategories.map(sub => ({
                value: sub.id,
                label: sub.name
            })),
            (value) => this.onSubcategoryChange(value, subcategories)
        );
        
        container.appendChild(box);
    }
    
    onSubcategoryChange(subcategoryId, subcategories) {
        this.currentSubcategory = parseInt(subcategoryId);
        this.clearSelectionsAfter(2);
        
        const subcat = subcategories.find(s => s.id === this.currentSubcategory);
        
        if (subcat) {
            // Create option boxes if any
            if (subcat.option_groups.length > 0) {
                this.createOptionBoxes(subcat.option_groups);
            }
            
            // Create size box
            this.createSizeBox(subcat);
        }
    }
    
    createOptionBoxes(optionGroups) {
        const container = document.getElementById('selection-boxes');
        const startIndex = this.getNextBoxNumber();
        
        optionGroups.forEach((group, index) => {
            const boxNumber = startIndex + index;
            
            const box = this.createSelectionBox(
                `option_${group.id}`,
                `${boxNumber}. ${group.name}`,
                group.options.map(opt => ({
                    value: opt.id,
                    label: opt.name
                })),
                (value) => this.onOptionChange(group.id, value)
            );
            
            container.appendChild(box);
        });
    }
    
    createSizeBox(subcategory) {
        const container = document.getElementById('selection-boxes');
        const boxNumber = this.getNextBoxNumber();
        
        // Generate size options based on min/max dimensions
        const sizes = this.generateSizeOptions(
            subcategory.minimumWidth,
            subcategory.maximumWidth,
            subcategory.minimumHeight,
            subcategory.maximumHeight
        );
        
        const box = this.createSelectionBox(
            'size',
            `${boxNumber}. Select Size`,
            sizes.map(size => ({
                value: size,
                label: size
            })),
            (value) => this.onSizeChange(value)
        );
        
        container.appendChild(box);
    }
    
    generateSizeOptions(minW, maxW, minH, maxH) {
        // Common print sizes
        const commonSizes = [
            '4x6', '5x7', '8x8', '8x10', '8.5x11', '8x12',
            '10x10', '10x20', '11x14', '11x17',
            '12x12', '12x16', '12x18', '12x24',
            '16x16', '16x20', '16x24',
            '18x18', '18x24', '20x20', '20x24', '20x30',
            '24x24', '24x30', '24x36',
            '30x30', '30x40', '36x36', '40x40'
        ];
        
        // Filter based on min/max dimensions
        return commonSizes.filter(size => {
            const [w, h] = size.split('x').map(Number);
            return w >= minW && w <= maxW && h >= minH && h <= maxH;
        });
    }
    
    onOptionChange(groupId, optionId) {
        this.selectedOptions[groupId] = parseInt(optionId);
        this.updatePricing();
    }
    
    onSizeChange(size) {
        this.selectedSize = size;
        this.updatePricing();
        
        // Show price display
        document.getElementById('price-display').classList.remove('hidden');
    }
    
    async updatePricing() {
        if (!this.currentSubcategory || !this.selectedSize) {
            return;
        }
        
        try {
            const [width, height] = this.selectedSize.split('x').map(Number);
            
            // Collect selected option IDs
            const options = Object.values(this.selectedOptions);
            
            // Show loading state
            document.getElementById('price-value').textContent = 'Calculating...';
            
            // Call pricing API
            const response = await fetch('/api/order-form/pricing', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    subcategory_id: this.currentSubcategory,
                    width: width,
                    height: height,
                    options: options,
                    quantity: 1
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const retailPrice = data.pricing.retail_price;
                document.getElementById('price-value').textContent = `$${retailPrice.toFixed(2)}`;
            } else {
                document.getElementById('price-value').textContent = 'Price unavailable';
                console.error('Pricing error:', data.error);
            }
            
        } catch (error) {
            document.getElementById('price-value').textContent = 'Error';
            console.error('Failed to get pricing:', error);
        }
    }
    
    createSelectionBox(id, label, options, onChange) {
        const box = document.createElement('div');
        box.className = 'selection-box active';
        box.id = `box-${id}`;
        
        const labelEl = document.createElement('label');
        labelEl.textContent = label;
        
        const select = document.createElement('select');
        select.id = `select-${id}`;
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- Choose --';
        select.appendChild(defaultOption);
        
        // Add options
        options.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt.value;
            option.textContent = opt.label;
            select.appendChild(option);
        });
        
        select.addEventListener('change', (e) => {
            if (e.target.value) {
                onChange(e.target.value);
            }
        });
        
        box.appendChild(labelEl);
        box.appendChild(select);
        
        return box;
    }
    
    getNextBoxNumber() {
        const boxes = document.querySelectorAll('.selection-box');
        return boxes.length + 1;
    }
    
    clearSelectionsAfter(boxIndex) {
        const container = document.getElementById('selection-boxes');
        const boxes = container.querySelectorAll('.selection-box');
        
        // Remove boxes after the specified index
        for (let i = boxIndex; i < boxes.length; i++) {
            boxes[i].remove();
        }
        
        // Reset state
        this.selectedOptions = {};
        this.selectedSize = null;
        document.getElementById('price-display').classList.add('hidden');
    }
    
    showError(message) {
        const errorEl = document.getElementById('error');
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
        document.getElementById('loading').classList.add('hidden');
    }
}

// Initialize form when page loads
document.addEventListener('DOMContentLoaded', () => {
    new DynamicOrderForm();
});

