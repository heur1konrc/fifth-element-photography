// Shopify Tab - Load pages within iframe
function loadShopifyPage(url) {
    const iframe = document.getElementById('shopify-content-frame');
    if (iframe) {
        iframe.src = url;
    }
}

// Auto-load Shopify Product Mapping when Shopify tab is opened
document.addEventListener('DOMContentLoaded', function() {
    // Listen for tab changes
    const shopifyTab = document.querySelector('[data-tab="shopify"]');
    if (shopifyTab) {
        shopifyTab.addEventListener('click', function() {
            // Load default page when Shopify tab is clicked
            setTimeout(() => {
                const iframe = document.getElementById('shopify-content-frame');
                if (iframe && !iframe.src) {
                    loadShopifyPage('/admin/shopify-mapping');
                }
            }, 100);
        });
    }
});
