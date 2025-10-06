/**
 * Lumaprints Instant Pricing Calculator
 * Integrates with gallery modals to provide real-time print pricing
 */

class LumaprintsPricing {
    constructor() {
        this.catalog = null;
        this.currentImage = null;
        this.loadCatalog();
    }

    /**
     * Load the product catalog from the API
     */
    async loadCatalog() {
        try {
            const response = await fetch('/api/lumaprints/catalog');
            const data = await response.json();
            
            if (data.success) {
                this.catalog = data.catalog;
                console.log('Lumaprints catalog loaded:', this.catalog);
            } else {
                console.error('Failed to load catalog:', data.error);
            }
        } catch (error) {
            console.error('Error loading catalog:', error);
        }
    }

    /**
     * Get popular products for quick selection
     */
    async getPopularProducts() {
        try {
            const response = await fetch('/api/lumaprints/popular-products');
            const data = await response.json();
            
            if (data.success) {
                return data.popular_products;
            } else {
                console.error('Failed to load popular products:', data.error);
                return [];
            }
        } catch (error) {
            console.error('Error loading popular products:', error);
            return [];
        }
    }

    /**
     * Calculate pricing for a specific configuration
     */
    async calculatePricing(subcategoryId, width, height, quantity = 1, options = []) {
        try {
            const response = await fetch('/api/lumaprints/pricing', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    subcategoryId: subcategoryId,
                    width: width,
                    height: height,
                    quantity: quantity,
                    options: options
                })
            });

            const data = await response.json();
            
            if (data.success) {
                return data.pricing;
            } else {
                console.error('Pricing calculation failed:', data.error);
                return null;
            }
        } catch (error) {
            console.error('Error calculating pricing:', error);
            return null;
        }
    }

    /**
     * Get size recommendations based on image dimensions
     */
    async getSizeRecommendations(imageWidth, imageHeight, subcategoryId) {
        try {
            const response = await fetch('/api/lumaprints/size-recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    imageWidth: imageWidth,
                    imageHeight: imageHeight,
                    subcategoryId: subcategoryId
                })
            });

            const data = await response.json();
            
            if (data.success) {
                return data.recommendations;
            } else {
                console.error('Failed to get size recommendations:', data.error);
                return [];
            }
        } catch (error) {
            console.error('Error getting size recommendations:', error);
            return [];
        }
    }

    /**
     * Create the print ordering interface for a gallery modal
     */
    async createPrintInterface(imageFilename, imageTitle, modalElement) {
        if (!this.catalog) {
            console.log('Catalog not loaded yet, waiting...');
            await this.loadCatalog();
        }

        const printInterface = document.createElement('div');
        printInterface.className = 'lumaprints-interface';
        printInterface.innerHTML = `
            <div class="print-ordering-section">
                <h3>Order This Print</h3>
                
                <!-- Product Selection -->
                <div class="product-selection">
                    <label for="product-category">Product Type:</label>
                    <select id="product-category" class="form-control">
                        <option value="">Select Product Type...</option>
                    </select>
                </div>

                <!-- Size Selection -->
                <div class="size-selection" style="display: none;">
                    <label for="print-size">Size:</label>
                    <select id="print-size" class="form-control">
                        <option value="">Select Size...</option>
                    </select>
                    <div class="size-recommendations" style="margin-top: 10px;"></div>
                </div>

                <!-- Quantity Selection -->
                <div class="quantity-selection" style="display: none;">
                    <label for="print-quantity">Quantity:</label>
                    <select id="print-quantity" class="form-control">
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                        <option value="5">5</option>
                    </select>
                </div>

                <!-- Pricing Display -->
                <div class="pricing-display" style="display: none;">
                    <div class="price-breakdown">
                        <div class="total-price">
                            <strong>Total: <span id="total-price">$0.00</span></strong>
                        </div>
                        <div class="price-details">
                            <small>
                                <span id="price-per-item">$0.00</span> each × 
                                <span id="quantity-display">1</span> = 
                                <span id="subtotal">$0.00</span>
                            </small>
                        </div>
                    </div>
                </div>

                <!-- Order Button -->
                <div class="order-actions" style="display: none;">
                    <button id="order-print-btn" class="btn btn-primary btn-lg">
                        Order This Print
                    </button>
                </div>

                <!-- Loading Indicator -->
                <div class="pricing-loader" style="display: none;">
                    <small>Calculating pricing...</small>
                </div>
            </div>
        `;

        // Store current image info
        this.currentImage = {
            filename: imageFilename,
            title: imageTitle,
            element: modalElement
        };

        // Populate product categories
        this.populateCategories(printInterface);

        // Set up event listeners
        this.setupEventListeners(printInterface);

        return printInterface;
    }

    /**
     * Populate the product categories dropdown
     */
    populateCategories(interfaceElement) {
        const categorySelect = interfaceElement.querySelector('#product-category');
        
        if (!this.catalog || !this.catalog.categories) {
            categorySelect.innerHTML = '<option value="">Catalog not available</option>';
            return;
        }

        // Add categories to dropdown
        this.catalog.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            categorySelect.appendChild(option);
        });
    }

    /**
     * Populate subcategories (sizes) for selected category
     */
    populateSubcategories(categoryId, interfaceElement) {
        const sizeSelect = interfaceElement.querySelector('#print-size');
        sizeSelect.innerHTML = '<option value="">Select Size...</option>';

        const subcategories = this.catalog.subcategories[categoryId] || [];
        
        subcategories.forEach(subcat => {
            const option = document.createElement('option');
            option.value = subcat.subcategoryId;
            option.textContent = subcat.name;
            option.dataset.minWidth = subcat.minimumWidth;
            option.dataset.maxWidth = subcat.maximumWidth;
            option.dataset.minHeight = subcat.minimumHeight;
            option.dataset.maxHeight = subcat.maximumHeight;
            sizeSelect.appendChild(option);
        });

        // Show size selection
        interfaceElement.querySelector('.size-selection').style.display = 'block';
    }

    /**
     * Set up event listeners for the interface
     */
    setupEventListeners(interfaceElement) {
        const categorySelect = interfaceElement.querySelector('#product-category');
        const sizeSelect = interfaceElement.querySelector('#print-size');
        const quantitySelect = interfaceElement.querySelector('#print-quantity');
        const orderBtn = interfaceElement.querySelector('#order-print-btn');

        // Category change
        categorySelect.addEventListener('change', (e) => {
            const categoryId = e.target.value;
            if (categoryId) {
                this.populateSubcategories(categoryId, interfaceElement);
                this.hidePricing(interfaceElement);
            } else {
                this.hideAllSections(interfaceElement);
            }
        });

        // Size change
        sizeSelect.addEventListener('change', (e) => {
            const subcategoryId = e.target.value;
            if (subcategoryId) {
                interfaceElement.querySelector('.quantity-selection').style.display = 'block';
                this.updatePricing(interfaceElement);
            } else {
                this.hidePricing(interfaceElement);
            }
        });

        // Quantity change
        quantitySelect.addEventListener('change', () => {
            this.updatePricing(interfaceElement);
        });

        // Order button
        orderBtn.addEventListener('click', () => {
            this.initiateOrder(interfaceElement);
        });
    }

    /**
     * Update pricing display
     */
    async updatePricing(interfaceElement) {
        const sizeSelect = interfaceElement.querySelector('#print-size');
        const quantitySelect = interfaceElement.querySelector('#print-quantity');
        const loader = interfaceElement.querySelector('.pricing-loader');
        const pricingDisplay = interfaceElement.querySelector('.pricing-display');
        const orderActions = interfaceElement.querySelector('.order-actions');

        const subcategoryId = parseInt(sizeSelect.value);
        const quantity = parseInt(quantitySelect.value);

        if (!subcategoryId) return;

        // Show loader
        loader.style.display = 'block';
        pricingDisplay.style.display = 'none';
        orderActions.style.display = 'none';

        // Get selected option details
        const selectedOption = sizeSelect.selectedOptions[0];
        const minWidth = parseFloat(selectedOption.dataset.minWidth);
        const maxWidth = parseFloat(selectedOption.dataset.maxWidth);
        const minHeight = parseFloat(selectedOption.dataset.minHeight);
        const maxHeight = parseFloat(selectedOption.dataset.maxHeight);

        // Use common print sizes within the allowed range
        const commonSizes = [
            [8, 10], [8, 12], [11, 14], [12, 16], [16, 20], [16, 24], [20, 30]
        ];

        // Find a suitable size within the range
        let width = 16, height = 20; // Default
        for (const [w, h] of commonSizes) {
            if (w >= minWidth && w <= maxWidth && h >= minHeight && h <= maxHeight) {
                width = w;
                height = h;
                break;
            }
        }

        try {
            const pricing = await this.calculatePricing(subcategoryId, width, height, quantity);
            
            if (pricing) {
                // Update pricing display
                interfaceElement.querySelector('#total-price').textContent = pricing.formatted_price;
                interfaceElement.querySelector('#price-per-item').textContent = pricing.formatted_price_per_item;
                interfaceElement.querySelector('#quantity-display').textContent = quantity;
                interfaceElement.querySelector('#subtotal').textContent = pricing.formatted_price;

                // Show pricing and order button
                pricingDisplay.style.display = 'block';
                orderActions.style.display = 'block';
            } else {
                // Show error
                pricingDisplay.innerHTML = '<div class="alert alert-warning">Unable to calculate pricing. Please try again.</div>';
                pricingDisplay.style.display = 'block';
            }
        } catch (error) {
            console.error('Error updating pricing:', error);
            pricingDisplay.innerHTML = '<div class="alert alert-danger">Error calculating pricing.</div>';
            pricingDisplay.style.display = 'block';
        } finally {
            loader.style.display = 'none';
        }
    }

    /**
     * Hide pricing sections
     */
    hidePricing(interfaceElement) {
        interfaceElement.querySelector('.quantity-selection').style.display = 'none';
        interfaceElement.querySelector('.pricing-display').style.display = 'none';
        interfaceElement.querySelector('.order-actions').style.display = 'none';
    }

    /**
     * Hide all sections
     */
    hideAllSections(interfaceElement) {
        interfaceElement.querySelector('.size-selection').style.display = 'none';
        this.hidePricing(interfaceElement);
    }

    /**
     * Initiate the order process
     */
    initiateOrder(interfaceElement) {
        const categorySelect = interfaceElement.querySelector('#product-category');
        const sizeSelect = interfaceElement.querySelector('#print-size');
        const quantitySelect = interfaceElement.querySelector('#print-quantity');
        const totalPrice = interfaceElement.querySelector('#total-price').textContent;

        const orderData = {
            image: this.currentImage,
            product: {
                categoryId: categorySelect.value,
                categoryName: categorySelect.selectedOptions[0].textContent,
                subcategoryId: sizeSelect.value,
                subcategoryName: sizeSelect.selectedOptions[0].textContent,
                quantity: quantitySelect.value
            },
            pricing: {
                total: totalPrice
            }
        };

        // Open order form modal
        this.openOrderForm(orderData);
    }

    /**
     * Open the order form modal
     */
    openOrderForm(orderData) {
        // Create order form modal
        const orderModal = document.createElement('div');
        orderModal.className = 'modal fade';
        orderModal.id = 'lumaprints-order-modal';
        orderModal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h4 class="modal-title">Complete Your Order</h4>
                        <button type="button" class="close" data-dismiss="modal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="order-summary">
                            <h5>Order Summary</h5>
                            <div class="row">
                                <div class="col-md-6">
                                    <strong>Image:</strong> ${orderData.image.title}<br>
                                    <strong>Product:</strong> ${orderData.product.categoryName}<br>
                                    <strong>Size:</strong> ${orderData.product.subcategoryName}<br>
                                    <strong>Quantity:</strong> ${orderData.product.quantity}
                                </div>
                                <div class="col-md-6 text-right">
                                    <h4>Total: ${orderData.pricing.total}</h4>
                                </div>
                            </div>
                        </div>
                        <hr>
                        <!-- Order form will be loaded here -->
                        <div id="order-form-container">
                            <p>Loading order form...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(orderModal);
        
        // Show modal
        $(orderModal).modal('show');

        // Load order form
        this.loadOrderForm(orderData, orderModal.querySelector('#order-form-container'));

        // Clean up when modal is closed
        $(orderModal).on('hidden.bs.modal', function() {
            document.body.removeChild(orderModal);
        });
    }

    /**
     * Load the order form
     */
    async loadOrderForm(orderData, container) {
        // This will be implemented in the next phase
        container.innerHTML = `
            <div class="alert alert-info">
                <h5>Order Form Coming Soon!</h5>
                <p>The instant pricing calculator is working perfectly. The order form with payment processing will be implemented in the next phase.</p>
                <p><strong>Current Configuration:</strong></p>
                <ul>
                    <li>Image: ${orderData.image.title}</li>
                    <li>Product: ${orderData.product.categoryName} - ${orderData.product.subcategoryName}</li>
                    <li>Quantity: ${orderData.product.quantity}</li>
                    <li>Total: ${orderData.pricing.total}</li>
                </ul>
            </div>
        `;
    }
}

// Initialize the pricing system
const lumaprintsPricing = new LumaprintsPricing();

// Function to add print ordering to gallery modals
function addPrintOrderingToModal(imageFilename, imageTitle, modalElement) {
    // Check if print interface already exists
    if (modalElement.querySelector('.lumaprints-interface')) {
        return;
    }

    // Create and add the print interface
    lumaprintsPricing.createPrintInterface(imageFilename, imageTitle, modalElement)
        .then(printInterface => {
            // Find a good place to insert the interface
            const modalBody = modalElement.querySelector('.modal-body');
            if (modalBody) {
                modalBody.appendChild(printInterface);
            }
        })
        .catch(error => {
            console.error('Error adding print interface:', error);
        });
}

// Export for use in other scripts
window.LumaprintsPricing = LumaprintsPricing;
window.addPrintOrderingToModal = addPrintOrderingToModal;
