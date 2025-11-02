/**
 * Shopify Integration Configuration
 * Fifth Element Photography - v2.1.0
 */

const SHOPIFY_CONFIG = {
    domain: 'fifth-element-photography.myshopify.com',
    storefrontAccessToken: '9935a2ea27c8d72d164554a9f855f960',
    apiVersion: '2024-10'
};

// Product mapping: image filename -> Shopify product handle
const PRODUCT_MAPPING = {
    'File_000.png': 'test-print-of-capital-paper-and-canva-combined',
    // Add more mappings as products are created in Shopify
};

// Get Shopify product handle for an image
function getProductHandle(imageFilename) {
    return PRODUCT_MAPPING[imageFilename] || null;
}

// Get product handle from image URL
function getProductHandleFromUrl(imageUrl) {
    const filename = imageUrl.split('/').pop();
    return getProductHandle(filename);
}

