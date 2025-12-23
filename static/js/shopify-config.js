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

// Get Shopify product handle for an image
function getProductHandle(imageFilename) {
    return PRODUCT_MAPPING[imageFilename] || null;
}

// Get product handle from image URL
function getProductHandleFromUrl(imageUrl) {
    const filename = imageUrl.split('/').pop();
    return getProductHandle(filename);
}


// Get all product handles for an image (supports multiple categories)
function getAllProductHandlesFromUrl(imageUrl) {
    const filename = imageUrl.split('/').pop();
    const mapping = PRODUCT_MAPPING[filename];
    
    if (!mapping) return [];
    
    // If mapping is a string (old format), return single handle
    if (typeof mapping === 'string') {
        return [{ handle: mapping, category: 'Canvas' }];
    }
    
    // If mapping is an object with categories
    if (typeof mapping === 'object') {
        return Object.entries(mapping).map(([category, handle]) => ({
            category,
            handle
        }));
    }
    
    return [];
}
