/**
 * Shopify Storefront API Integration
 * Fifth Element Photography - v4.2.0
 * Badge-style variant selectors with dynamic availability checking
 */

// Storefront API endpoint
const STOREFRONT_API_URL = `https://${SHOPIFY_CONFIG.domain}/api/2024-10/graphql.json`;

// Format price to always show 2 decimal places
function formatPrice(amount) {
    return parseFloat(amount).toFixed(2);
}

// Fetch product by handle using Storefront API
async function fetchProductByHandle(handle) {
    const query = `
        query getProduct($handle: String!) {
            product(handle: $handle) {
                id
                title
                description
                descriptionHtml
                images(first: 1) {
                    edges {
                        node {
                            url
                            altText
                        }
                    }
                }
                variants(first: 100) {
                    edges {
                        node {
                            id
                            title
                            price {
                                amount
                                currencyCode
                            }
                            availableForSale
                            selectedOptions {
                                name
                                value
                            }
                        }
                    }
                }
                options {
                    name
                    values
                }
            }
        }
    `;

    const response = await fetch(STOREFRONT_API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Shopify-Storefront-Access-Token': SHOPIFY_CONFIG.storefrontAccessToken
        },
        body: JSON.stringify({
            query: query,
            variables: { handle: handle }
        })
    });

    const data = await response.json();
    
    if (data.errors) {
        console.error('GraphQL errors:', data.errors);
        throw new Error('Failed to fetch product');
    }
    
    return data.data.product;
}

// Create cart with line items using Storefront API
async function createCartWithItem(variantId) {
    const mutation = `
        mutation cartCreate($input: CartInput!) {
            cartCreate(input: $input) {
                cart {
                    id
                    checkoutUrl
                }
                userErrors {
                    field
                    message
                }
            }
        }
    `;

    const response = await fetch(STOREFRONT_API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Shopify-Storefront-Access-Token': SHOPIFY_CONFIG.storefrontAccessToken
        },
        body: JSON.stringify({
            query: mutation,
            variables: {
                input: {
                    lines: [
                        {
                            merchandiseId: variantId,
                            quantity: 1
                        }
                    ]
                }
            }
        })
    });

    const data = await response.json();
    
    if (data.errors) {
        console.error('GraphQL errors:', data.errors);
        throw new Error('Failed to create cart');
    }
    
    if (data.data.cartCreate.userErrors.length > 0) {
        console.error('User errors:', data.data.cartCreate.userErrors);
        throw new Error(data.data.cartCreate.userErrors[0].message);
    }
    
    return data.data.cartCreate.cart;
}

// Open product modal for a specific image
function openShopifyProductModal(imageUrl, imageTitle) {
    const productHandle = getProductHandleFromUrl(imageUrl);
    
    if (!productHandle) {
        alert('This image is not yet available for purchase. Please check back soon!');
        console.error('No Shopify product mapped for:', imageUrl);
        return;
    }

    // Show loading state
    showLoadingModal(imageTitle);

    // Fetch product using Storefront API
    fetchProductByHandle(productHandle)
        .then(product => {
            if (!product) {
                closeShopifyModal();
                alert('Product not found. Please contact support.');
                console.error('Product not found:', productHandle);
                return;
            }

            console.log('Product loaded:', product);
            
            // Create and show product modal
            displayProductModal(product, imageTitle);
        })
        .catch(error => {
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

// Display product modal with badge-style variant selectors
function displayProductModal(product, imageTitle) {
    const container = document.getElementById('shopify-product-component');
    if (!container) return;

    const imageUrl = product.images.edges[0]?.node.url || '';

    // Build product HTML with badge selectors
    let productHTML = `
        <div class="product-details">
            <div class="product-image">
                <img src="${imageUrl}" alt="${product.title}" />
            </div>
            <div class="product-info">
                <h3>${product.title}</h3>
                <div class="product-description">${product.descriptionHtml || ''}</div>
                <div class="product-price">
                    <span class="price" id="variant-price">Select options</span>
                </div>
                
                <div class="product-options">
    `;

    // Add badge-style variant selectors
    product.options.forEach((option, optionIndex) => {
        const isFirstOption = optionIndex === 0;
        const badgeClass = isFirstOption ? 'option-badge-full' : 'option-badge-small';
        
        productHTML += `
            <div class="option-group">
                <label class="option-label">${option.name}:</label>
                <div class="option-badges">
        `;
        
        option.values.forEach(value => {
            productHTML += `
                <button 
                    class="${badgeClass}" 
                    data-option-index="${optionIndex}"
                    data-option-value="${value}"
                    onclick="selectOption(${optionIndex}, '${value}')"
                >
                    ${value}
                </button>
            `;
        });
        
        productHTML += `
                </div>
            </div>
        `;
    });

    productHTML += `
                </div>
                
                <div id="availability-message" class="availability-message"></div>
                
                <div class="product-actions">
                    <button id="add-to-cart-btn" class="add-to-cart-button" disabled>Add to Cart</button>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = productHTML;
    container.classList.remove('shopify-loading');

    // Store product data
    window.currentProduct = product;
    window.selectedOptions = {};
}

// Check which option values are available given current selections
function getAvailableOptions(optionIndex) {
    const product = window.currentProduct;
    const selectedOptions = window.selectedOptions;
    const availableValues = new Set();
    
    // Find all variants that match currently selected options (excluding the option we're checking)
    product.variants.edges.forEach(edge => {
        const variant = edge.node;
        
        // Check if this variant matches all currently selected options (except the one we're checking)
        let matches = true;
        variant.selectedOptions.forEach((opt, idx) => {
            if (idx !== optionIndex && selectedOptions[idx] !== undefined) {
                if (opt.value !== selectedOptions[idx]) {
                    matches = false;
                }
            }
        });
        
        // If it matches and is available, add this option value to available set
        if (matches && variant.availableForSale) {
            const optionValue = variant.selectedOptions[optionIndex].value;
            availableValues.add(optionValue);
        }
    });
    
    return availableValues;
}

// Update availability of option badges based on current selections
function updateOptionAvailability() {
    const product = window.currentProduct;
    
    // For each option after the first selected one, update availability
    product.options.forEach((option, optionIndex) => {
        // Skip if this option is already selected
        if (window.selectedOptions[optionIndex] !== undefined) {
            return;
        }
        
        // Check if any previous options are selected
        let hasPreviousSelections = false;
        for (let i = 0; i < optionIndex; i++) {
            if (window.selectedOptions[i] !== undefined) {
                hasPreviousSelections = true;
                break;
            }
        }
        
        if (hasPreviousSelections) {
            const availableValues = getAvailableOptions(optionIndex);
            const badges = document.querySelectorAll(`[data-option-index="${optionIndex}"]`);
            
            badges.forEach(badge => {
                const value = badge.dataset.optionValue;
                if (availableValues.has(value)) {
                    badge.disabled = false;
                    badge.classList.remove('unavailable');
                } else {
                    badge.disabled = true;
                    badge.classList.add('unavailable');
                }
            });
        }
    });
}

// Select an option value
function selectOption(optionIndex, value) {
    const badge = document.querySelector(`[data-option-index="${optionIndex}"][data-option-value="${value}"]`);
    
    // Don't allow selecting disabled options
    if (badge && badge.disabled) {
        return;
    }
    
    // Update selected options
    window.selectedOptions[optionIndex] = value;
    
    // Clear any selections after this option
    const product = window.currentProduct;
    for (let i = optionIndex + 1; i < product.options.length; i++) {
        delete window.selectedOptions[i];
        
        // Remove selected class from badges in later options
        const laterBadges = document.querySelectorAll(`[data-option-index="${i}"]`);
        laterBadges.forEach(b => {
            b.classList.remove('selected');
            b.disabled = false;
            b.classList.remove('unavailable');
        });
    }
    
    // Update UI - highlight selected badge
    const badges = document.querySelectorAll(`[data-option-index="${optionIndex}"]`);
    badges.forEach(badge => {
        if (badge.dataset.optionValue === value) {
            badge.classList.add('selected');
        } else {
            badge.classList.remove('selected');
        }
    });
    
    // Update availability of subsequent options
    updateOptionAvailability();
    
    // Check if all options are selected
    const allOptionsSelected = Object.keys(window.selectedOptions).length === window.currentProduct.options.length;
    
    if (allOptionsSelected) {
        updateVariantAvailability();
    } else {
        // Reset price and disable button
        document.getElementById('variant-price').textContent = 'Select all options';
        document.getElementById('add-to-cart-btn').disabled = true;
        document.getElementById('availability-message').textContent = '';
    }
}

// Update variant availability and price
function updateVariantAvailability() {
    const product = window.currentProduct;
    const selectedOptions = window.selectedOptions;
    
    // Build selected options array in order
    const selectedValues = product.options.map((opt, idx) => selectedOptions[idx]);
    
    // Find matching variant
    const variant = product.variants.edges.find(edge => {
        return edge.node.selectedOptions.every((option, index) => {
            return option.value === selectedValues[index];
        });
    })?.node;

    const priceEl = document.getElementById('variant-price');
    const availabilityMsg = document.getElementById('availability-message');
    const addButton = document.getElementById('add-to-cart-btn');
    
    if (variant) {
        // Update price
        priceEl.textContent = `$${formatPrice(variant.price.amount)}`;
        
        // Store selected variant
        window.selectedVariantId = variant.id;
        
        // Update availability message and button
        if (!variant.availableForSale) {
            availabilityMsg.textContent = 'This combination is currently unavailable';
            availabilityMsg.style.color = '#ff6b6b';
            addButton.disabled = true;
            addButton.textContent = 'Unavailable';
        } else {
            availabilityMsg.textContent = '';
            addButton.disabled = false;
            addButton.textContent = 'Add to Cart';
        }
    } else {
        priceEl.textContent = 'Combination not available';
        addButton.disabled = true;
    }
}

// Add product to cart
function addToCart() {
    const variantId = window.selectedVariantId;

    if (!variantId) {
        alert('Please select all product options');
        return;
    }

    const button = document.getElementById('add-to-cart-btn');
    button.disabled = true;
    button.textContent = 'Adding...';

    // Create cart with item using Storefront API
    createCartWithItem(variantId)
        .then(cart => {
            console.log('Cart created:', cart);
            
            // Redirect to Shopify checkout
            window.location.href = cart.checkoutUrl;
        })
        .catch(error => {
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
    
    // Clean up global state
    window.currentProduct = null;
    window.selectedOptions = {};
    window.selectedVariantId = null;
}

console.log('Shopify Storefront API integration loaded');

