/**
 * Lumaprints Print Ordering System
 * Handles instant pricing and order placement
 */

class LumaprintsPrintOrdering {
    constructor() {
        this.currentImage = null;
        this.currentPricing = null;
        this.categories = [];
        this.init();
    }

    async init() {
        try {
            // Load categories
            const response = await fetch('/api/lumaprints/categories');
            const data = await response.json();
            if (data.success) {
                this.categories = data.categories;
            }
        } catch (error) {
            console.error('Failed to load categories:', error);
        }
    }

    // Show print ordering modal for an image
    showPrintModal(imagePath) {
        this.currentImage = imagePath;
        
        // Create modal HTML
        const modalHTML = `
            <div id="printOrderModal" class="modal-overlay" onclick="this.closePrintModal(event)">
                <div class="modal-content print-modal" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h2>Order Print</h2>
                        <button class="close-btn" onclick="lumaprintsPrintOrdering.closePrintModal()">&times;</button>
                    </div>
                    
                    <div class="modal-body">
                        <div class="print-preview">
                            <img src="${imagePath}" alt="Print Preview" class="preview-image">
                        </div>
                        
                        <div class="print-options">
                            <div class="option-group">
                                <label>Product Type:</label>
                                <select id="productType" onchange="lumaprintsPrintOrdering.updatePricing()">
                                    <option value="">Select Product Type</option>
                                    <option value="101001">Canvas Print (0.75")</option>
                                    <option value="101002">Canvas Print (1.25")</option>
                                    <option value="102001">Framed Canvas</option>
                                    <option value="103001">Fine Art Paper</option>
                                    <option value="106001">Metal Print</option>
                                </select>
                            </div>
                            
                            <div class="option-group">
                                <label>Size:</label>
                                <select id="printSize" onchange="lumaprintsPrintOrdering.updatePricing()">
                                    <option value="">Select Size</option>
                                    <option value="8,10">8" × 10"</option>
                                    <option value="11,14">11" × 14"</option>
                                    <option value="12,16">12" × 16"</option>
                                    <option value="16,20">16" × 20"</option>
                                    <option value="18,24">18" × 24"</option>
                                    <option value="20,30">20" × 30"</option>
                                </select>
                            </div>
                            
                            <div class="option-group">
                                <label>Quantity:</label>
                                <select id="quantity" onchange="lumaprintsPrintOrdering.updatePricing()">
                                    <option value="1">1</option>
                                    <option value="2">2</option>
                                    <option value="3">3</option>
                                    <option value="4">4</option>
                                    <option value="5">5</option>
                                </select>
                            </div>
                            
                            <div class="pricing-display">
                                <div id="pricingInfo" class="pricing-info">
                                    Select product and size to see pricing
                                </div>
                            </div>
                            
                            <div class="order-actions">
                                <button id="addToCartBtn" class="btn btn-primary" onclick="lumaprintsPrintOrdering.proceedToOrder()" disabled>
                                    Proceed to Order
                                </button>
                                <button class="btn btn-secondary" onclick="lumaprintsPrintOrdering.closePrintModal()">
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Show modal
        document.getElementById('printOrderModal').style.display = 'flex';
    }

    // Close print modal
    closePrintModal(event) {
        if (event && event.target !== event.currentTarget) return;
        
        const modal = document.getElementById('printOrderModal');
        if (modal) {
            modal.remove();
        }
        this.currentImage = null;
        this.currentPricing = null;
    }

    // Update pricing based on current selections
    async updatePricing() {
        const productType = document.getElementById('productType').value;
        const printSize = document.getElementById('printSize').value;
        const quantity = document.getElementById('quantity').value;
        
        const pricingInfo = document.getElementById('pricingInfo');
        const addToCartBtn = document.getElementById('addToCartBtn');
        
        if (!productType || !printSize) {
            pricingInfo.innerHTML = 'Select product and size to see pricing';
            addToCartBtn.disabled = true;
            return;
        }
        
        // Parse size
        const [width, height] = printSize.split(',').map(Number);
        
        try {
            pricingInfo.innerHTML = 'Calculating pricing...';
            
            const response = await fetch('/api/lumaprints/pricing', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    subcategoryId: parseInt(productType),
                    width: width,
                    height: height,
                    quantity: parseInt(quantity)
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentPricing = data.pricing;
                
                pricingInfo.innerHTML = `
                    <div class="price-breakdown">
                        <div class="price-line">
                            <span>Price per item:</span>
                            <span class="price">${data.pricing.formatted_price}</span>
                        </div>
                        ${parseInt(quantity) > 1 ? `
                        <div class="price-line">
                            <span>Quantity:</span>
                            <span>${quantity}</span>
                        </div>
                        <div class="price-line total">
                            <span>Total:</span>
                            <span class="price">$${(data.pricing.retail_price * parseInt(quantity)).toFixed(2)}</span>
                        </div>
                        ` : ''}
                    </div>
                `;
                
                addToCartBtn.disabled = false;
            } else {
                pricingInfo.innerHTML = `Error: ${data.error}`;
                addToCartBtn.disabled = true;
            }
            
        } catch (error) {
            console.error('Pricing error:', error);
            pricingInfo.innerHTML = 'Error calculating pricing';
            addToCartBtn.disabled = true;
        }
    }

    // Proceed to order form
    proceedToOrder() {
        if (!this.currentPricing) return;
        
        const productType = document.getElementById('productType');
        const printSize = document.getElementById('printSize').value;
        const quantity = document.getElementById('quantity').value;
        
        // Get product name
        const productName = productType.options[productType.selectedIndex].text;
        const [width, height] = printSize.split(',').map(Number);
        const sizeName = `${width}" × ${height}"`;
        
        // Close current modal
        this.closePrintModal();
        
        // Show order form
        this.showOrderForm({
            image: this.currentImage,
            productName: productName,
            sizeName: sizeName,
            quantity: parseInt(quantity),
            pricing: this.currentPricing
        });
    }

    // Show order form
    showOrderForm(orderDetails) {
        console.log('showOrderForm called with:', orderDetails);
        const totalPrice = orderDetails.pricing.retail_price * orderDetails.quantity;
        console.log('Total price calculated:', totalPrice);
        
        const orderFormHTML = `
            <div id="orderFormModal" class="modal-overlay" onclick="lumaprintsPrintOrdering.closeOrderForm(event)">
                <div class="modal-content order-modal" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h2>Complete Your Order</h2>
                        <button class="close-btn" onclick="lumaprintsPrintOrdering.closeOrderForm()">&times;</button>
                    </div>
                    
                    <div class="modal-body">
                        <div class="order-summary">
                            <h3>Order Summary</h3>
                            <div class="summary-item">
                                <img src="${orderDetails.image}" alt="Print Preview" class="summary-image">
                                <div class="summary-details">
                                    <div><strong>${orderDetails.productName}</strong></div>
                                    <div>Size: ${orderDetails.sizeName}</div>
                                    <div>Quantity: ${orderDetails.quantity}</div>
                                    <div class="price"><strong>Total: $${totalPrice.toFixed(2)}</strong></div>
                                </div>
                            </div>
                        </div>
                        
                        <form id="orderForm" class="order-form">
                            <h3>Shipping Information</h3>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="firstName">First Name *</label>
                                    <input type="text" id="firstName" name="firstName" required>
                                </div>
                                <div class="form-group">
                                    <label for="lastName">Last Name *</label>
                                    <input type="text" id="lastName" name="lastName" required>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label for="email">Email *</label>
                                <input type="email" id="email" name="email" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="phone">Phone</label>
                                <input type="tel" id="phone" name="phone">
                            </div>
                            
                            <div class="form-group">
                                <label for="address">Address *</label>
                                <input type="text" id="address" name="address" required>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="city">City *</label>
                                    <input type="text" id="city" name="city" required>
                                </div>
                                <div class="form-group">
                                    <label for="state">State *</label>
                                    <input type="text" id="state" name="state" required>
                                </div>
                                <div class="form-group">
                                    <label for="zipCode">ZIP Code *</label>
                                    <input type="text" id="zipCode" name="zipCode" required>
                                </div>
                            </div>
                            
                            <div class="payment-section">
                                <h3>Payment</h3>
                                <div class="payment-total">
                                    <strong>Total: $${totalPrice.toFixed(2)}</strong>
                                </div>
                                
                                <div class="payment-options">
                                    <button type="button" class="btn btn-primary paypal-btn" onclick="lumaprintsPrintOrdering.processPayPalPayment()">
                                        Pay with PayPal - $${totalPrice.toFixed(2)}
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        console.log('Adding order form HTML to body...');
        document.body.insertAdjacentHTML('beforeend', orderFormHTML);
        
        const modal = document.getElementById('orderFormModal');
        console.log('Order form modal element:', modal);
        
        if (modal) {
            modal.style.display = 'flex';
            console.log('Modal display set to flex');
        } else {
            console.error('Order form modal not found after creation!');
        }
        
        // Store order details for payment processing
        this.currentOrderDetails = orderDetails;
        console.log('Order form should now be visible');
    }

    // Close order form
    closeOrderForm(event) {
        if (event && event.target !== event.currentTarget) return;
        
        const modal = document.getElementById('orderFormModal');
        if (modal) {
            modal.remove();
        }
        this.currentOrderDetails = null;
    }

    // Process PayPal payment
    processPayPalPayment() {
        const form = document.getElementById('orderForm');
        const formData = new FormData(form);
        
        // Validate form
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // For now, show a simple confirmation
        // In production, this would integrate with PayPal
        const totalPrice = this.currentOrderDetails.pricing.retail_price * this.currentOrderDetails.quantity;
        
        if (confirm(`Proceed with PayPal payment of $${totalPrice.toFixed(2)}?`)) {
            this.submitOrder(formData);
        }
    }

    // Submit order
    async submitOrder(formData) {
        try {
            // Show loading
            const paypalBtn = document.querySelector('.paypal-btn');
            paypalBtn.innerHTML = 'Processing...';
            paypalBtn.disabled = true;
            
            // Prepare order data
            const orderData = {
                customer_info: {
                    first_name: formData.get('firstName'),
                    last_name: formData.get('lastName'),
                    email: formData.get('email'),
                    phone: formData.get('phone'),
                    address: formData.get('address'),
                    city: formData.get('city'),
                    state: formData.get('state'),
                    zip_code: formData.get('zipCode')
                },
                product_info: {
                    image_url: this.currentOrderDetails.image,
                    subcategory_id: this.currentOrderDetails.pricing.subcategoryId,
                    width: this.currentOrderDetails.pricing.width,
                    height: this.currentOrderDetails.pricing.height,
                    quantity: this.currentOrderDetails.quantity
                },
                pricing: this.currentOrderDetails.pricing
            };
            
            // For now, just show success message
            // In production, this would submit to your backend
            alert('Order submitted successfully! You will receive a confirmation email shortly.');
            
            this.closeOrderForm();
            
        } catch (error) {
            console.error('Order submission error:', error);
            alert('Error submitting order. Please try again.');
            
            // Re-enable button
            const paypalBtn = document.querySelector('.paypal-btn');
            paypalBtn.innerHTML = `Pay with PayPal - $${(this.currentOrderDetails.pricing.retail_price * this.currentOrderDetails.quantity).toFixed(2)}`;
            paypalBtn.disabled = false;
        }
    }
}

// Initialize the print ordering system
const lumaprintsPrintOrdering = new LumaprintsPrintOrdering();

// Add print buttons to existing gallery modals
document.addEventListener('DOMContentLoaded', function() {
    // Add CSS for print ordering
    const printCSS = `
        <style>
        .print-modal { max-width: 600px; width: 90%; }
        .order-modal { max-width: 800px; width: 95%; }
        
        .print-preview { text-align: center; margin-bottom: 20px; }
        .preview-image { max-width: 200px; max-height: 200px; object-fit: cover; border-radius: 8px; }
        
        .print-options { display: flex; flex-direction: column; gap: 15px; }
        .option-group { display: flex; flex-direction: column; gap: 5px; }
        .option-group label { font-weight: bold; }
        .option-group select { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        
        .pricing-display { background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .pricing-info { font-size: 16px; }
        .price-breakdown { display: flex; flex-direction: column; gap: 8px; }
        .price-line { display: flex; justify-content: space-between; }
        .price-line.total { border-top: 1px solid #ddd; padding-top: 8px; font-weight: bold; }
        .price { color: #2c5aa0; font-weight: bold; }
        
        .order-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
        
        .order-summary { background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .summary-item { display: flex; gap: 15px; align-items: center; }
        .summary-image { width: 80px; height: 80px; object-fit: cover; border-radius: 4px; }
        .summary-details { flex: 1; }
        
        .order-form { display: flex; flex-direction: column; gap: 15px; }
        .form-row { display: flex; gap: 15px; }
        .form-group { flex: 1; display: flex; flex-direction: column; gap: 5px; }
        .form-group label { font-weight: bold; }
        .form-group input { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        
        .payment-section { border-top: 1px solid #ddd; padding-top: 20px; margin-top: 20px; }
        .payment-total { font-size: 18px; margin-bottom: 15px; text-align: center; }
        .paypal-btn { background: #0070ba; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; width: 100%; }
        .paypal-btn:hover { background: #005ea6; }
        .paypal-btn:disabled { background: #ccc; cursor: not-allowed; }
        
        @media (max-width: 768px) {
            .form-row { flex-direction: column; }
            .print-modal, .order-modal { width: 95%; margin: 10px; }
        }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', printCSS);
});
