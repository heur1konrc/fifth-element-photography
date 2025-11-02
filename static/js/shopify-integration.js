/**
 * Shopify Storefront API Integration
 * Fifth Element Photography - v4.0.0
 * Using Storefront API directly with GraphQL (JS Buy SDK is deprecated)
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

// Display product modal with variants
function displayProductModal(product, imageTitle) {
    const container = document.getElementById('shopify-product-component');
    if (!container) return;

    const imageUrl = product.images.edges[0]?.node.url || '';
    const firstVariant = product.variants.edges[0]?.node;

    // Build product HTML
    let productHTML = `
        <div class="product-details">
            <div class="product-image">
                <img src="${imageUrl}" alt="${product.title}" />
            </div>
            <div class="product-info">
                <h3>${product.title}</h3>
                <div class="product-description">${product.descriptionHtml || ''}</div>
                <div class="product-price">
                    <span class="price">$${formatPrice(firstVariant.price.amount)}</span>
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
            productHTML += `<option value="${value}">${value}</option>`;
        });
        
        productHTML += `
                </select>
            </div>
        `;
    });

    productHTML += `
                </div>
                
                <div id="availability-message" class="availability-message"></div>
                
                <div class="product-actions">
                    <button id="add-to-cart-btn" class="add-to-cart-button">Add to Cart</button>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = productHTML;
    container.classList.remove('shopify-loading');

    // Store product data
    container.dataset.productData = JSON.stringify(product);

    // Add event listeners for variant selection
    const selects = container.querySelectorAll('.variant-select');
    selects.forEach(select => {
        select.addEventListener('change', () => updateSelectedVariant());
    });

    // Add to cart button handler
    document.getElementById('add-to-cart-btn').addEventListener('click', () => {
        addToCart();
    });

    // Initialize with first variant selected
    updateSelectedVariant();
}

// Update selected variant based on option selections
function updateSelectedVariant() {
    const container = document.getElementById('shopify-product-component');
    if (!container) return;

    const product = JSON.parse(container.dataset.productData);
    const selects = container.querySelectorAll('.variant-select');
    const selectedOptions = Array.from(selects).map(select => select.value);

    // Find matching variant
    const variant = product.variants.edges.find(edge => {
        return edge.node.selectedOptions.every((option, index) => {
            return option.value === selectedOptions[index];
        });
    })?.node;

    if (variant) {
        // Update price
        const priceEl = container.querySelector('.price');
        if (priceEl) {
            priceEl.textContent = `$${formatPrice(variant.price.amount)}`;
        }

        // Store selected variant
        container.dataset.selectedVariantId = variant.id;
        container.dataset.selectedVariantAvailable = variant.availableForSale;

        // Update availability message and button
        const availabilityMsg = document.getElementById('availability-message');
        const addButton = document.getElementById('add-to-cart-btn');
        
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
    }
}

// Add product to cart
function addToCart() {
    const container = document.getElementById('shopify-product-component');
    const variantId = container?.dataset.selectedVariantId;
    const isAvailable = container?.dataset.selectedVariantAvailable === 'true';

    if (!variantId) {
        alert('Please select product options');
        return;
    }

    if (!isAvailable) {
        alert('This variant is currently unavailable');
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
}

console.log('Shopify Storefront API integration loaded');

