/**
 * Shopify Integration Configuration
 * Fifth Element Photography - v2.1.0
 */

const SHOPIFY_CONFIG = {
    domain: 'fifth-element-photography.myshopify.com',
    storefrontAccessToken: '1b9515df0dc41eec10a5d1a10cfc956a',
    apiVersion: '2025-10'
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

