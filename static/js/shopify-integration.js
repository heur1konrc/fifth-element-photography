/**
 * Shopify JS Buy SDK Integration
 * Fifth Element Photography - v3.0.0
 * Using JS Buy SDK directly instead of Buy Button UI
 */

// Initialize Shopify client
let shopifyClient = null;

// Initialize the Shopify SDK when page loads
function initializeShopify() {
    if (typeof ShopifyBuy === 'undefined') {
        console.error('Shopify Buy SDK not loaded');
        return;
    }

    // Create Shopify client using JS Buy SDK
    shopifyClient = ShopifyBuy.buildClient({
        domain: SHOPIFY_CONFIG.domain,
        storefrontAccessToken: SHOPIFY_CONFIG.storefrontAccessToken
    });
    
    console.log('Shopify JS Buy SDK initialized successfully');
}

// Open product modal for a specific image
function openShopifyProductModal(imageUrl, imageTitle) {
    const productHandle = getProductHandleFromUrl(imageUrl);
    
    if (!productHandle) {
        alert('This image is not yet available for purchase. Please check back soon!');
        console.error('No Shopify product mapped for:', imageUrl);
        return;
    }

    if (!shopifyClient) {
        console.error('Shopify client not initialized');
        initializeShopify();
        setTimeout(() => openShopifyProductModal(imageUrl, imageTitle), 500);
        return;
    }

    // Show loading state
    showLoadingModal(imageTitle);

    // Fetch product by handle using JS Buy SDK
    shopifyClient.product.fetchByHandle(productHandle).then(function(product) {
        if (!product) {
            closeShopifyModal();
            alert('Product not found. Please contact support.');
            console.error('Product not found:', productHandle);
            return;
        }

        console.log('Product loaded:', product);
        
        // Create and show product modal
        displayProductModal(product, imageTitle);
        
    }).catch(function(error) {
        closeShopifyModal();
        console.error('Error fetching product:', error);
        alert('Error loading product. Please try again.');
    });
}

// Show loading modal
function showLoadingModal(title) {
    const modalHTML = `
        <div id="shopify-product-modal" class="shopify-modal">
            <div class="shopify-modal-content">
                <div class="shopify-modal-header">
                    <h2>${title}</h2>
                    <button class="shopify-modal-close" onclick="closeShopifyModal()">&times;</button>
                </div>
                <div id="shopify-product-component" class="shopify-loading">
                    <p>Loading product options...</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    document.getElementById('shopify-product-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// Display product modal with variants
function displayProductModal(product, imageTitle) {
    const container = document.getElementById('shopify-product-component');
    if (!container) return;

    // Build product HTML
    let productHTML = `
        <div class="product-details">
            <div class="product-image">
                <img src="${product.images[0]?.src || ''}" alt="${product.title}" />
            </div>
            <div class="product-info">
                <h3>${product.title}</h3>
                <div class="product-description">${product.descriptionHtml || ''}</div>
                <div class="product-price">
                    <span class="price">$${product.variants[0].price.amount}</span>
                </div>
                
                <div class="product-options">
    `;

    // Add variant selectors
    product.options.forEach((option, index) => {
        productHTML += `
            <div class="option-group">
                <label for="option-${index}">${option.name}:</label>
                <select id="option-${index}" class="variant-select" data-option-index="${index}">
        `;
        
        option.values.forEach(value => {
            productHTML += `<option value="${value.value}">${value.value}</option>`;
        });
        
        productHTML += `
                </select>
            </div>
        `;
    });

    productHTML += `
                </div>
                
                <div class="product-actions">
                    <button id="add-to-cart-btn" class="add-to-cart-button">Add to Cart</button>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = productHTML;
    container.classList.remove('shopify-loading');

    // Add event listeners for variant selection
    const selects = container.querySelectorAll('.variant-select');
    selects.forEach(select => {
        select.addEventListener('change', () => updateSelectedVariant(product));
    });

    // Add to cart button handler
    document.getElementById('add-to-cart-btn').addEventListener('click', () => {
        addToCart(product);
    });

    // Initialize with first variant selected
    updateSelectedVariant(product);
}

// Update selected variant based on option selections
function updateSelectedVariant(product) {
    const container = document.getElementById('shopify-product-component');
    if (!container) return;

    const selects = container.querySelectorAll('.variant-select');
    const selectedOptions = Array.from(selects).map(select => select.value);

    // Find matching variant
    const variant = product.variants.find(v => {
        return v.selectedOptions.every((option, index) => {
            return option.value === selectedOptions[index];
        });
    });

    if (variant) {
        // Update price
        const priceEl = container.querySelector('.price');
        if (priceEl) {
            priceEl.textContent = `$${variant.price.amount}`;
        }

        // Store selected variant ID
        container.dataset.selectedVariantId = variant.id;
    }
}

// Add product to cart
function addToCart(product) {
    const container = document.getElementById('shopify-product-component');
    const variantId = container?.dataset.selectedVariantId;

    if (!variantId) {
        alert('Please select product options');
        return;
    }

    const button = document.getElementById('add-to-cart-btn');
    button.disabled = true;
    button.textContent = 'Adding...';

    // Create or fetch checkout
    shopifyClient.checkout.create().then(checkout => {
        const lineItemsToAdd = [{
            variantId: variantId,
            quantity: 1
        }];

        return shopifyClient.checkout.addLineItems(checkout.id, lineItemsToAdd);
    }).then(checkout => {
        console.log('Added to cart, checkout:', checkout);
        
        // Redirect to Shopify checkout
        window.location.href = checkout.webUrl;
        
    }).catch(error => {
        console.error('Error adding to cart:', error);
        alert('Error adding to cart. Please try again.');
        button.disabled = false;
        button.textContent = 'Add to Cart';
    });
}

// Close Shopify product modal
function closeShopifyModal() {
    const modal = document.getElementById('shopify-product-modal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = 'auto';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Load Shopify JS Buy SDK
    const script = document.createElement('script');
    script.src = 'https://sdks.shopifycdn.com/js-buy-sdk/v2/latest/index.umd.min.js';
    script.async = true;
    script.onload = initializeShopify;
    script.onerror = function() {
        console.error('Failed to load Shopify JS Buy SDK');
    };
    document.head.appendChild(script);
});

