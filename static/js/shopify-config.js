/**
 * Shopify Integration Configuration
 * Fifth Element Photography - v2.1.0
 */

const SHOPIFY_CONFIG = {
    domain: 'fifth-element-photography.myshopify.com',
    storefrontAccessToken: '9935a2ea27c8d72d164554a9f855f960',
    apiVersion: '2024-10'
};

// Product mapping cache (loaded from database)
// Format: { "image.jpg": { "Canvas": "handle-canvas", "Metal": "handle-metal", ... } }
let PRODUCT_MAPPING = {};

// Load product mappings from database
async function loadProductMappings() {
    try {
        const response = await fetch('/admin/api/shopify-mapping/all');
        const data = await response.json();
        if (data.success) {
            PRODUCT_MAPPING = data.mappings;
            console.log('Shopify product mappings loaded:', PRODUCT_MAPPING);
        }
    } catch (error) {
        console.error('Error loading Shopify product mappings:', error);
    }
}

// Initialize mappings on page load
loadProductMappings();

// Get all Shopify product handles for an image (returns object with categories)
function getProductHandles(imageFilename) {
    return PRODUCT_MAPPING[imageFilename] || null;
}

// Get product handles from image URL
function getProductHandlesFromUrl(imageUrl) {
    const filename = imageUrl.split('/').pop();
    return getProductHandles(filename);
}

// Legacy function for backward compatibility - returns first available handle
function getProductHandle(imageFilename) {
    const handles = getProductHandles(imageFilename);
    if (!handles) return null;
    // Return first available handle
    return Object.values(handles)[0] || null;
}

// Legacy function for backward compatibility
function getProductHandleFromUrl(imageUrl) {
    const filename = imageUrl.split('/').pop();
    return getProductHandle(filename);
}

