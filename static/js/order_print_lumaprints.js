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
        
        // Lumaprints API product data based on official documentation
        this.productData = {
            // Canvas Category (ID: 101)
            101: {
                name: 'Canvas',
                subcategories: [
                    { id: 101001, name: '0.75in Stretched Canvas', minWidth: 5, maxWidth: 120, minHeight: 5, maxHeight: 52, dpi: 200 },
                    { id: 101002, name: '1.25in Stretched Canvas', minWidth: 5, maxWidth: 120, minHeight: 5, maxHeight: 52, dpi: 200 },
                    { id: 101003, name: '1.50in Stretched Canvas', minWidth: 5, maxWidth: 120, minHeight: 5, maxHeight: 52, dpi: 200 },
                    { id: 101005, name: 'Rolled Canvas', minWidth: 5, maxWidth: 120, minHeight: 5, maxHeight: 52, dpi: 200 }
                ]
            },
            // Framed Canvas Category (ID: 102)
            102: {
                name: 'Framed Canvas',
                subcategories: [
                    // Frame depth options - user selects depth first
                    { 
                        id: 102001, 
                        name: '0.75" Framed Canvas', 
                        minWidth: 5, maxWidth: 120, minHeight: 5, maxHeight: 52, dpi: 200,
                        frameColors: [
                            { name: 'Black Floating Frame', optionId: 12 },
                            { name: 'White Floating Frame', optionId: 13 },
                            { name: 'Silver Floating Frame', optionId: 14 },
                            { name: 'Gold Floating Frame', optionId: 15 }
                        ]
                    },
                    { 
                        id: 102002, 
                        name: '1.25" Framed Canvas', 
                        minWidth: 5, maxWidth: 120, minHeight: 5, maxHeight: 52, dpi: 200,
                        frameColors: [
                            { name: 'Black Floating Frame', optionId: 27 },
                            { name: 'Oak Floating Frame', optionId: 91 },
                            { name: 'Walnut Floating Frame', optionId: 120 }
                        ]
                    },
                    { 
                        id: 102003, 
                        name: '1.50" Framed Canvas', 
                        minWidth: 5, maxWidth: 120, minHeight: 5, maxHeight: 52, dpi: 200,
                        frameColors: [
                            { name: 'Black Floating Frame', optionId: 23 },
                            { name: 'White Floating Frame', optionId: 24 },
                            { name: 'Silver Floating Frame', optionId: 25 },
                            { name: 'Gold Floating Frame', optionId: 26 },
                            { name: 'Oak Floating Frame', optionId: 92 }
                        ]
                    }
                ]
            },
            // Fine Art Paper Category (ID: 103)
            103: {
                name: 'Fine Art Paper',
                subcategories: [
                    { id: 103001, name: 'Archival Matte Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 103002, name: 'Hot Press Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 103003, name: 'Cold Press Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 103005, name: 'Semi-Glossy Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 103006, name: 'Metallic Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 103007, name: 'Glossy Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 103008, name: 'Semi-Matte Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 103009, name: 'Somerset Velvet Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 }
                ]
            },
            // Foam-mounted Print Category (ID: 104) - Based on Fine Art Paper products
            104: {
                name: 'Foam-mounted Print',
                subcategories: [
                    { id: 104001, name: 'Foam-mounted Archival Matte Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 104002, name: 'Foam-mounted Hot Press Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 104003, name: 'Foam-mounted Cold Press Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 104005, name: 'Foam-mounted Semi-Glossy Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 104006, name: 'Foam-mounted Metallic Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 104007, name: 'Foam-mounted Glossy Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 104009, name: 'Foam-mounted Somerset Velvet Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 },
                    { id: 104010, name: 'Foam-mounted Canvas', minWidth: 5, maxWidth: 44, minHeight: 5, maxHeight: 60, dpi: 300 }
                ]
            },
            // Framed Fine Art Paper Category (ID: 105)
            105: {
                name: 'Framed Fine Art Paper',
                subcategories: [
                    { id: 105001, name: '0.875in Black Frame', minWidth: 5, maxWidth: 36, minHeight: 5, maxHeight: 48, dpi: 300 },
                    { id: 105002, name: '0.875in White Frame', minWidth: 5, maxWidth: 36, minHeight: 5, maxHeight: 48, dpi: 300 },
                    { id: 105003, name: '0.875in Oak Frame', minWidth: 5, maxWidth: 36, minHeight: 5, maxHeight: 48, dpi: 300 },
                    { id: 105005, name: '1.25in Black Frame', minWidth: 5, maxWidth: 36, minHeight: 5, maxHeight: 48, dpi: 300 },
                    { id: 105006, name: '1.25in White Frame', minWidth: 5, maxWidth: 36, minHeight: 5, maxHeight: 48, dpi: 300 },
                    { id: 105007, name: '1.25in Oak Frame', minWidth: 5, maxWidth: 36, minHeight: 5, maxHeight: 48, dpi: 300 }
                ]
            },
            // Metal Category (ID: 106)
            106: {
                name: 'Metal',
                subcategories: [
                    { id: 106001, name: 'Glossy White Metal Print', minWidth: 5, maxWidth: 48, minHeight: 5, maxHeight: 96, dpi: 300 },
                    { id: 106001, name: 'Glossy Silver Metal Print', minWidth: 5, maxWidth: 48, minHeight: 5, maxHeight: 96, dpi: 300 }
                ]
            },
            // Peel and Stick Category (ID: 107)
            107: {
                name: 'Peel and Stick',
                subcategories: [
                    { id: 107001, name: 'Peel and Stick Vinyl', minWidth: 5, maxWidth: 48, minHeight: 5, maxHeight: 96, dpi: 300 },
                    { id: 107002, name: 'Peel and Stick Fabric', minWidth: 5, maxWidth: 48, minHeight: 5, maxHeight: 96, dpi: 300 }
                ]
            }
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadCategory(101); // Start with Canvas category
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
        
        // Quantity controls
        document.getElementById('qtyMinus')?.addEventListener('click', () => {
            this.adjustQuantity(-1);
        });
        
        document.getElementById('qtyPlus')?.addEventListener('click', () => {
            this.adjustQuantity(1);
        });
        
        document.getElementById('quantity')?.addEventListener('change', (e) => {
            this.updateItemTotal();
        });
        
        // Action buttons
        document.getElementById('addToCartBtn')?.addEventListener('click', () => {
            this.addToCart();
        });
        
        document.getElementById('continueShoppingBtn')?.addEventListener('click', () => {
            this.continueShopping();
        });
        
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
        
        // Load category products
        this.loadCategory(categoryId);
        this.showView('products');
    }
    
    loadCategory(categoryId) {
        this.currentCategory = categoryId;
        const categoryData = this.productData[categoryId];
        
        if (!categoryData) return;
        
        // Update category title
        document.getElementById('categoryTitle').textContent = categoryData.name;
        
        // Load products
        this.loadProducts(categoryData.subcategories);
    }
    
    loadProducts(subcategories) {
        const grid = document.getElementById('productsGrid');
        grid.innerHTML = '';
        
        subcategories.forEach(product => {
            const productCard = this.createProductCard(product);
            grid.appendChild(productCard);
        });
    }
    
    createProductCard(product) {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.dataset.productId = product.id;
        
        card.innerHTML = `
            <div class="product-thumbnail">
                <span>Product Preview</span>
            </div>
            <div class="product-name">${product.name}</div>
            <div class="product-description">
                Size range: ${product.minWidth}"×${product.minHeight}" to ${product.maxWidth}"×${product.maxHeight}"<br>
                Required DPI: ${product.dpi}
            </div>
        `;
        
        card.addEventListener('click', () => {
            this.selectProduct(product);
        });
        
        return card;
    }
    
    selectProduct(product) {
        this.currentProduct = product;
        
        // Update UI
        document.querySelectorAll('.product-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-product-id="${product.id}"]`).classList.add('selected');
        
        // Update product title
        document.getElementById('productTitle').textContent = product.name;
        
        // Check if this product has frame color options (for Framed Canvas)
        if (product.frameColors && product.frameColors.length > 0) {
            this.showFrameColorSelection(product);
        } else {
            // Load sizes directly for products without color options
            this.loadSizes(product);
            this.showView('sizes');
        }
    }

    showFrameColorSelection(product) {
        // Update the products grid to show frame color options
        const grid = document.getElementById('productsGrid');
        grid.innerHTML = '';
        
        // Update category title to show we're selecting frame colors
        document.getElementById('categoryTitle').textContent = product.name + ' - Choose Frame Color';
        
        product.frameColors.forEach(color => {
            const colorCard = document.createElement('div');
            colorCard.className = 'product-card';
            colorCard.dataset.colorId = color.optionId;
            
            colorCard.innerHTML = `
                <div class="product-thumbnail">
                    <span>Product Preview</span>
                </div>
                <div class="product-name">${color.name}</div>
                <div class="product-description">
                    Size range: ${product.minWidth}"×${product.minHeight}" to ${product.maxWidth}"×${product.maxHeight}"<br>
                    Required DPI: ${product.dpi}
                </div>
            `;
            
            colorCard.addEventListener('click', () => {
                this.selectFrameColor(product, color);
            });
            
            grid.appendChild(colorCard);
        });
    }

    selectFrameColor(product, color) {
        // Create a new product object with the selected color
        this.currentProduct = {
            ...product,
            name: product.name + ' - ' + color.name,
            optionId: color.optionId,
            selectedColor: color
        };
        
        // Update UI
        document.querySelectorAll('.product-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-color-id="${color.optionId}"]`).classList.add('selected');
        
        // Update product title
        document.getElementById('productTitle').textContent = this.currentProduct.name;
        
        // Load sizes
        this.loadSizes(this.currentProduct);
        this.showView('sizes');
    }
    
    loadSizes(product) {
        const grid = document.getElementById('sizesGrid');
        grid.innerHTML = '';
        
        // Generate common sizes within the product's constraints
        const sizes = this.generateSizes(product.minWidth, product.maxWidth, product.minHeight, product.maxHeight);
        
        sizes.forEach(size => {
            const sizeCard = this.createSizeCard(size);
            grid.appendChild(sizeCard);
        });
    }
    
    generateSizes(minW, maxW, minH, maxH) {
        // Common print sizes that fit within constraints
        const commonSizes = [
            { width: 8, height: 10, price: 29.99 },
            { width: 11, height: 14, price: 39.99 },
            { width: 16, height: 20, price: 59.99 },
            { width: 18, height: 24, price: 79.99 },
            { width: 24, height: 30, price: 119.99 },
            { width: 30, height: 40, price: 179.99 },
            { width: 36, height: 48, price: 249.99 }
        ];
        
        return commonSizes.filter(size => 
            size.width >= minW && size.width <= maxW && 
            size.height >= minH && size.height <= maxH
        );
    }
    
    createSizeCard(size) {
        const card = document.createElement('div');
        card.className = 'size-card';
        card.dataset.width = size.width;
        card.dataset.height = size.height;
        card.dataset.price = size.price;
        
        card.innerHTML = `
            <div class="size-dimensions">${size.width}" × ${size.height}"</div>
            <div class="size-price">$${size.price.toFixed(2)}</div>
        `;
        
        card.addEventListener('click', () => {
            this.selectSize(size);
        });
        
        return card;
    }
    
    selectSize(size) {
        this.currentSize = size;
        
        // Update UI
        document.querySelectorAll('.size-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-width="${size.width}"][data-height="${size.height}"]`).classList.add('selected');
        
        // Update quantity view
        this.updateQuantityView();
        this.showView('quantity');
    }
    
    updateQuantityView() {
        const preview = document.getElementById('selectedItemPreview');
        preview.innerHTML = `
            <h3>${this.currentProduct.name}</h3>
            <p>Size: ${this.currentSize.width}" × ${this.currentSize.height}"</p>
            <p>Unit Price: $${this.currentSize.price.toFixed(2)}</p>
        `;
        
        document.getElementById('unitPrice').textContent = `$${this.currentSize.price.toFixed(2)}`;
        this.updateItemTotal();
    }
    
    adjustQuantity(delta) {
        const qtyInput = document.getElementById('quantity');
        const currentQty = parseInt(qtyInput.value);
        const newQty = Math.max(1, Math.min(99, currentQty + delta));
        qtyInput.value = newQty;
        this.updateItemTotal();
    }
    
    updateItemTotal() {
        const quantity = parseInt(document.getElementById('quantity').value);
        const total = this.currentSize.price * quantity;
        document.getElementById('itemTotal').textContent = `$${total.toFixed(2)}`;
    }
    
    addToCart() {
        const quantity = parseInt(document.getElementById('quantity').value);
        
        const cartItem = {
            id: Date.now(), // Simple ID generation
            categoryName: this.productData[this.currentCategory].name,
            productName: this.currentProduct.name,
            subcategoryId: this.currentProduct.id,
            width: this.currentSize.width,
            height: this.currentSize.height,
            quantity: quantity,
            unitPrice: this.currentSize.price,
            totalPrice: this.currentSize.price * quantity
        };
        
        this.cart.push(cartItem);
        this.updateCartDisplay();
        
        // Show success message or animation
        alert(`Added ${quantity}x ${this.currentProduct.name} (${this.currentSize.width}"×${this.currentSize.height}") to your order!`);
    }
    
    updateCartDisplay() {
        const cartItems = document.getElementById('cartItems');
        const cartTotal = document.getElementById('cartTotal');
        const checkoutBtn = document.getElementById('checkoutBtn');
        
        if (this.cart.length === 0) {
            cartItems.innerHTML = '<p class="cart-empty">No items added yet</p>';
            cartTotal.style.display = 'none';
            checkoutBtn.style.display = 'none';
            return;
        }
        
        // Show cart items
        cartItems.innerHTML = this.cart.map(item => `
            <div class="cart-item">
                <div class="cart-item-name">${item.productName}</div>
                <div class="cart-item-details">
                    ${item.width}"×${item.height}" × ${item.quantity} = $${item.totalPrice.toFixed(2)}
                </div>
            </div>
        `).join('');
        
        // Calculate and show total
        const subtotal = this.cart.reduce((sum, item) => sum + item.totalPrice, 0);
        document.getElementById('subtotalAmount').textContent = `$${subtotal.toFixed(2)}`;
        
        cartTotal.style.display = 'block';
        checkoutBtn.style.display = 'block';
    }
    
    continueShopping() {
        // Reset quantity to 1
        document.getElementById('quantity').value = 1;
        
        // Go back to products view
        this.showView('products');
    }
    
    proceedToCheckout() {
        // Here you would integrate with Lumaprints API to submit the order
        // For now, show the order summary
        const orderSummary = {
            items: this.cart,
            subtotal: this.cart.reduce((sum, item) => sum + item.totalPrice, 0),
            imageUrl: window.orderData.imageUrl,
            imageTitle: window.orderData.imageTitle
        };
        
        console.log('Order Summary:', orderSummary);
        alert(`Order ready for checkout!\n\nItems: ${this.cart.length}\nSubtotal: $${orderSummary.subtotal.toFixed(2)}\n\nThis would integrate with Lumaprints API for actual checkout.`);
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
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LumaprintsOrderInterface();
});
