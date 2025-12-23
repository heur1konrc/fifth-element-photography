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

// Sort Shopify images
function sortShopifyImages() {
    const grid = document.getElementById('shopifyImageGrid');
    if (!grid) return;
    
    const sortBy = document.getElementById('shopifySortBy').value;
    const items = Array.from(grid.querySelectorAll('.shopify-image-item'));
    
    items.sort((a, b) => {
        const filenameA = a.dataset.filename.toLowerCase();
        const filenameB = b.dataset.filename.toLowerCase();
        const dateA = a.dataset.date;
        const dateB = b.dataset.date;
        
        const hasShopifyA = a.querySelector('.fa-check') !== null;
        const hasShopifyB = b.querySelector('.fa-check') !== null;
        
        switch(sortBy) {
            case 'a-z':
                return filenameA.localeCompare(filenameB);
            case 'z-a':
                return filenameB.localeCompare(filenameA);
            case 'date-asc':
                return (dateA || '').localeCompare(dateB || '');
            case 'live':
                if (hasShopifyA === hasShopifyB) {
                    return filenameA.localeCompare(filenameB);
                }
                return hasShopifyB ? 1 : -1;
            case 'date-desc':
            default:
                return (dateB || '').localeCompare(dateA || '');
        }
    });
    
    // Clear and re-append sorted items
    grid.innerHTML = '';
    items.forEach(item => grid.appendChild(item));
}

// Sort on page load (newest first by default)
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for the tab to be ready
    setTimeout(() => {
        const grid = document.getElementById('shopifyImageGrid');
        if (grid) {
            sortShopifyImages();
        }
    }, 500);
});

// Expose function globally
window.sortShopifyImages = sortShopifyImages;
