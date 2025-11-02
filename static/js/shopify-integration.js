/**
 * Shopify Buy Button SDK Integration
 * Fifth Element Photography - v2.1.0
 */

// Initialize Shopify Buy Button SDK
let shopifyClient = null;
let shopifyUI = null;

// Initialize the Shopify SDK when page loads
function initializeShopify() {
    if (typeof ShopifyBuy === 'undefined') {
        console.error('Shopify Buy SDK not loaded');
        return;
    }

    // Create Shopify client
    shopifyClient = ShopifyBuy.buildClient({
        domain: SHOPIFY_CONFIG.domain,
        storefrontAccessToken: SHOPIFY_CONFIG.storefrontAccessToken,
        apiVersion: SHOPIFY_CONFIG.apiVersion
    });

    // Create UI instance
    shopifyUI = ShopifyBuy.UI.init(shopifyClient);
    
    console.log('Shopify SDK initialized successfully');
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
        return;
    }

    // Fetch product by handle
    shopifyClient.product.fetchByHandle(productHandle).then(function(product) {
        if (!product) {
            alert('Product not found. Please contact support.');
            return;
        }

        // Create modal container
        const modalHTML = `
            <div id="shopify-product-modal" class="shopify-modal">
                <div class="shopify-modal-content">
                    <div class="shopify-modal-header">
                        <h2>${imageTitle}</h2>
                        <button class="shopify-modal-close" onclick="closeShopifyModal()">&times;</button>
                    </div>
                    <div id="shopify-product-component"></div>
                </div>
            </div>
        `;

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Render product component
        shopifyUI.createComponent('product', {
            id: product.id,
            node: document.getElementById('shopify-product-component'),
            options: {
                product: {
                    iframe: false,
                    contents: {
                        img: true,
                        title: false, // We show title in modal header
                        price: true,
                        description: true,
                        buttonWithQuantity: true,
                        quantity: false
                    },
                    styles: {
                        product: {
                            '@media (min-width: 601px)': {
                                'max-width': '100%',
                                'margin-left': '0',
                                'margin-bottom': '0'
                            }
                        },
                        button: {
                            'background-color': '#4a90e2',
                            ':hover': {
                                'background-color': '#357abd'
                            },
                            ':focus': {
                                'background-color': '#357abd'
                            },
                            'border-radius': '4px',
                            'padding': '12px 24px',
                            'font-size': '16px'
                        },
                        price: {
                            'font-size': '24px',
                            'color': '#ffffff'
                        },
                        compareAt: {
                            'font-size': '18px',
                            'color': '#999999'
                        },
                        option: {
                            'background-color': '#2a2a2a',
                            'color': '#ffffff',
                            'border': '1px solid #444',
                            'border-radius': '4px',
                            'padding': '10px'
                        }
                    },
                    text: {
                        button: 'Add to Cart'
                    }
                },
                cart: {
                    iframe: true,
                    startOpen: false,
                    styles: {
                        button: {
                            'background-color': '#4a90e2',
                            ':hover': {
                                'background-color': '#357abd'
                            }
                        }
                    }
                },
                toggle: {
                    iframe: false,
                    styles: {
                        toggle: {
                            'background-color': '#4a90e2',
                            ':hover': {
                                'background-color': '#357abd'
                            }
                        }
                    }
                }
            }
        });

        // Show modal
        document.getElementById('shopify-product-modal').style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
    }).catch(function(error) {
        console.error('Error fetching product:', error);
        alert('Error loading product. Please try again.');
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
    // Load Shopify Buy Button SDK
    const script = document.createElement('script');
    script.src = 'https://sdks.shopifycdn.com/buy-button/latest/buy-button-storefront.min.js';
    script.async = true;
    script.onload = initializeShopify;
    document.head.appendChild(script);
});

