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
    console.log('[SHOPIFY MODAL] openShopifyProductModal called with:', imageUrl, imageTitle);
    
    // Store original image URL and title for back button
    window.originalImageUrl = imageUrl;
    window.originalImageTitle = imageTitle;
    
    // Get all product handles for this image (multiple categories)
    const productHandles = getAllProductHandlesFromUrl(imageUrl);
    console.log('[SHOPIFY MODAL] productHandles:', productHandles);
    
    // Store product handles for back button
    window.originalProductHandles = productHandles;
    
    if (!productHandles || productHandles.length === 0) {
        console.error('[SHOPIFY MODAL] No product handles found for:', imageUrl);
        alert('This image is not yet available for purchase. Please check back soon!');
        return;
    }

    // If multiple products exist, show category selector
    if (productHandles.length > 1) {
        console.log('[SHOPIFY MODAL] Multiple products, showing category selector');
        showCategorySelector(imageUrl, imageTitle, productHandles);
        return;
    }
    
    console.log('[SHOPIFY MODAL] Single product, loading directly');

    // Single product - open directly
    const productHandle = productHandles[0].handle;
    
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
                    <button class="shopify-modal-close">&times;</button>
                </div>
                <div id="shopify-product-component" class="shopify-loading">
                    <p>Loading product options...</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = document.getElementById('shopify-product-modal');
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // Attach close handlers immediately
    const closeBtn = document.querySelector('.shopify-modal-close');
    if (closeBtn) {
        closeBtn.onclick = function() {
            window.closeShopifyModal();
            return false;
        };
    }
    
    // Click on backdrop to close
    modal.onclick = function(e) {
        if (e.target === modal) {
            window.closeShopifyModal();
        }
    };
    
    // ESC key to close
    const escHandler = function(e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            window.closeShopifyModal();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

// Display product modal with badge-style variant selectors
function displayProductModal(product, imageTitle) {
    const container = document.getElementById('shopify-product-component');
    if (!container) return;

    const imageUrl = product.images.edges[0]?.node.url || '';

    // Context already stored in openShopifyProductModal
    
    // Build product HTML with badge selectors and description panel
    let productHTML = `
        <div class="product-details">
            <div class="product-image">
                <img src="${imageUrl}" alt="${product.title}" />
                <!-- Substrate Description Panel -->
                <div id="substrate-description-panel" class="substrate-description-panel">
                    <h4 id="substrate-title"></h4>
                    <p id="substrate-description"></p>
                    <ul id="substrate-specs"></ul>
                </div>
            </div>
            <div class="product-info">
                <h3>${product.title}</h3>
                <div class="product-description">${product.descriptionHtml || ''}</div>
                <div class="product-price">
                    <span class="price" id="variant-price">Select a size</span>
                </div>
                
                <!-- Back Button -->
                <button id="back-to-categories-btn" class="back-button" style="display: none;">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" style="margin-right: 8px;">
                        <path d="M8 0L6.59 1.41 12.17 7H0v2h12.17l-5.58 5.59L8 16l8-8z" transform="rotate(180 8 8)"/>
                    </svg>
                    Back to Print Types
                </button>
                
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
    
    // Initialize substrate description hover listeners
    initializeSubstrateHoverListeners();
    
    // Attach Add to Cart button event listener
    const addToCartBtn = document.getElementById('add-to-cart-btn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', addToCart);
    }
    
    // Show back button if there are multiple product categories
    const backBtn = document.getElementById('back-to-categories-btn');
    if (backBtn && window.originalProductHandles && window.originalProductHandles.length > 1) {
        backBtn.style.display = 'inline-flex';
        backBtn.addEventListener('click', function() {
            showCategorySelector(window.originalImageUrl, window.originalImageTitle, window.originalProductHandles);
        });
    }
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
window.selectOption = function(optionIndex, value) {
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
        document.getElementById('variant-price').textContent = 'Select a size';
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
window.closeShopifyModal = function() {
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



// Show category selector modal
function showCategorySelector(imageUrl, imageTitle, productHandles) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('shopify-product-modal');
    
    if (!modal) {
        // Create the modal structure
        const modalHTML = `
            <div id="shopify-product-modal" class="shopify-modal">
                <div class="shopify-modal-content">
                    <div class="shopify-modal-header">
                        <h2>${imageTitle}</h2>
                        <button class="shopify-modal-close">&times;</button>
                    </div>
                    <div id="shopify-product-component"></div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modal = document.getElementById('shopify-product-modal');
        
        // Attach close handlers
        const closeBtn = document.querySelector('.shopify-modal-close');
        if (closeBtn) {
            closeBtn.onclick = function() {
                window.closeShopifyModal();
                return false;
            };
        }
        
        // Click on backdrop to close
        modal.onclick = function(e) {
            if (e.target === modal) {
                window.closeShopifyModal();
            }
        };
        
        // ESC key to close
        const escHandler = function(e) {
            if (e.key === 'Escape' || e.keyCode === 27) {
                window.closeShopifyModal();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }
    
    const container = document.getElementById('shopify-product-component');
    if (!container) return;
    
    // Build category selector HTML
    const escapedTitle = imageTitle.replace(/'/g, "\\'");
    const categoriesHTML = productHandles.map(({category, handle}) => `
        <button class="category-selector-btn" onclick="openProductByHandle('${handle}', '${escapedTitle}')">
            <img src="${getCategoryIcon(category)}" alt="${category}" class="category-image" />
            <div class="category-info">
                <div class="category-title">${category}</div>
                <div class="category-description">${getCategoryDescription(category)}</div>
            </div>
        </button>
    `).join('');
    
    container.innerHTML = `
        <div class="category-selector">
            <h2>Select Print Type</h2>
            <p class="category-subtitle">${imageTitle}</p>
            <div class="category-grid">
                ${categoriesHTML}
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Get icon for category
function getCategoryIcon(category) {
    const images = {
        'Canvas': '/static/images/products/canvas.png',
        'Metal': '/static/images/products/metal.png',
        'Fine Art Paper': '/static/images/products/fine-art-paper.png',
        'Framed Canvas': '/static/images/products/framed-canvas.png',
        'Foam-mounted Print': '/static/images/products/foam-mounted.png'
    };
    return images[category] || '/static/images/products/canvas.png';
}

// Get description for category
function getCategoryDescription(category) {
    const descriptions = {
        'Canvas': 'Get your artwork, designs and photos on canvas with our high-quality stretched or rolled canvas prints. Made with carefully hand-stretched fabric on a wooden frame.',
        'Framed Canvas': 'Give your photos and artwork the professional look of a framed canvas print. Choose from floating, decorative, or traditional gallery frames – a perfect blend of elegance, depth, and versatility.',
        'Fine Art Paper': "It's not just a piece of paper – it's a work of art. Fine art paper creates an elegant, classic aesthetic with vibrant colors that give off a gallery-feel that won't fade easily.",
        'Foam-mounted Print': 'Discover a new way to showcase your art and photos with our foam-mounted fine art paper prints. These lightweight and sturdy prints offer the perfect solution for stunning, professional presentation.',
        'Metal': "Display your photos and artworks in a way that's both beautiful and durable. The infusion of the image to the aluminum's coating offers a level of vibrancy and vividness not seen in other print medium."
    };
    return descriptions[category] || '';
}

// Open product by handle directly
function openProductByHandle(handle, imageTitle) {
    showLoadingModal(imageTitle);
    
    fetchProductByHandle(handle)
        .then(product => {
            if (!product) {
                closeShopifyModal();
                alert('Product not found. Please contact support.');
                return;
            }
            displayProductModal(product, imageTitle);
        })
        .catch(error => {
            closeShopifyModal();
            alert('Error loading product. Please try again.');
            console.error('Error:', error);
        });
}

// Make function globally available
window.openProductByHandle = openProductByHandle;

/**
 * Initialize hover listeners for substrate descriptions
 * Shows detailed information when hovering over product option badges
 */
function initializeSubstrateHoverListeners() {
    console.log('[SUBSTRATE HOVER] Initializing hover listeners');
    
    const descriptionPanel = document.getElementById('substrate-description-panel');
    const titleElement = document.getElementById('substrate-title');
    const descriptionElement = document.getElementById('substrate-description');
    const specsElement = document.getElementById('substrate-specs');
    
    console.log('[SUBSTRATE HOVER] Elements found:', {
        panel: !!descriptionPanel,
        title: !!titleElement,
        description: !!descriptionElement,
        specs: !!specsElement
    });
    
    if (!descriptionPanel || !titleElement || !descriptionElement || !specsElement) {
        console.warn('[SUBSTRATE HOVER] Some elements not found - aborting');
        return;
    }
    
    console.log('[SUBSTRATE HOVER] All elements found, attaching listeners');
    
    // Get all option badges (buttons)
    const optionBadges = document.querySelectorAll('.option-badge-full, .option-badge-small');
    
    console.log('[SUBSTRATE HOVER] Found', optionBadges.length, 'option badges');
    
    optionBadges.forEach(badge => {
        // Mouse enter - show description
        badge.addEventListener('mouseenter', function() {
            const optionValue = this.dataset.optionValue;
            console.log('[SUBSTRATE HOVER] Hovering over:', optionValue);
            
            // Get description from substrate descriptions database
            if (typeof window.getSubstrateDescription === 'function') {
                const substrateInfo = window.getSubstrateDescription(optionValue);
                
                if (substrateInfo) {
                    // Update panel content
                    titleElement.textContent = substrateInfo.title;
                    descriptionElement.textContent = substrateInfo.description;
                    
                    // Build specs list
                    specsElement.innerHTML = '';
                    if (substrateInfo.specs && substrateInfo.specs.length > 0) {
                        substrateInfo.specs.forEach(spec => {
                            const li = document.createElement('li');
                            li.textContent = spec;
                            specsElement.appendChild(li);
                        });
                    }
                    
                    // Show panel with fade-in effect
                    descriptionPanel.classList.add('visible');
                }
            }
        });
        
        // Mouse leave - hide description
        badge.addEventListener('mouseleave', function() {
            descriptionPanel.classList.remove('visible');
        });
    });
}
