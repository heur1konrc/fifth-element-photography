// Shopify Tab - Load pages within iframe
function loadShopifyPage(url, title = 'Shopify Page') {
    const iframe = document.getElementById('shopify-content-frame');
    const iframeContainer = document.getElementById('shopifyIframeContainer');
    const gallery = document.getElementById('shopifyImageGallery');
    const titleEl = document.getElementById('shopifyIframeTitle');
    
    if (iframe && iframeContainer && gallery) {
        // Hide gallery, show iframe
        gallery.style.display = 'none';
        iframeContainer.style.display = 'block';
        
        // Set title and load URL
        titleEl.textContent = title;
        iframe.src = url;
    }
}

function closeShopifyIframe() {
    const iframeContainer = document.getElementById('shopifyIframeContainer');
    const gallery = document.getElementById('shopifyImageGallery');
    const iframe = document.getElementById('shopify-content-frame');
    
    if (iframeContainer && gallery) {
        // Show gallery, hide iframe
        iframeContainer.style.display = 'none';
        gallery.style.display = 'block';
        
        // Clear iframe src to stop loading
        if (iframe) {
            iframe.src = '';
        }
    }
}

// Expose functions globally
window.loadShopifyPage = loadShopifyPage;
window.closeShopifyIframe = closeShopifyIframe;
