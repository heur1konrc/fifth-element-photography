// BETA MODAL JAVASCRIPT

// Get modal elements
const modalBeta = document.getElementById('imageModalBeta');
const modalBetaClose = document.querySelector('.modal-beta-close');

// Store current image data
let currentImageDataBeta = null;

// Open beta modal
function openModalBeta(imageData) {
    currentImageDataBeta = imageData;
    
    // Populate title
    document.getElementById('modalBetaTitle').textContent = imageData.title || 'Untitled';
    
    // Populate image
    document.getElementById('modalBetaImage').src = imageData.url || '';
    document.getElementById('modalBetaImage').alt = imageData.title || 'Image';
    
    // Populate EXIF data (now loaded from database in gallery data - instant!)
    document.getElementById('exifModel').textContent = imageData.model || 'Unavailable';
    document.getElementById('exifLens').textContent = imageData.lens || 'Unavailable';
    document.getElementById('exifAperture').textContent = imageData.aperture || 'Unavailable';
    document.getElementById('exifShutter').textContent = imageData.shutter_speed || 'Unavailable';
    document.getElementById('exifISO').textContent = imageData.iso || 'Unavailable';
    document.getElementById('exifFocal').textContent = imageData.focal_length || 'Unavailable';
    
    // Populate description
    const descriptionDiv = document.getElementById('modalBetaDescription');
    if (imageData.description) {
        descriptionDiv.innerHTML = imageData.description;
    } else {
        descriptionDiv.innerHTML = '<p>No description available for this image.</p>';
    }
    
    // Show/hide ORDER PRINTS button based on Shopify mapping
    const orderBtn = document.getElementById('btnOrderPrints');
    
    // Check if this image has Shopify product mappings (supports multiple categories)
    console.log('[ORDER PRINTS DEBUG] imageData.url:', imageData.url);
    const productHandles = typeof getAllProductHandlesFromUrl === 'function' ? getAllProductHandlesFromUrl(imageData.url) : [];
    console.log('[ORDER PRINTS DEBUG] productHandles:', productHandles);
    
    if (productHandles && productHandles.length > 0) {
        orderBtn.style.display = 'block';
    } else {
        orderBtn.style.display = 'none';
    }
    
    // Show modal
    modalBeta.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Close modal
function closeModalBeta() {
    modalBeta.style.display = 'none';
    document.body.style.overflow = 'auto';
    currentImageDataBeta = null;
    
    // Remove any open share menus
    const shareMenus = document.querySelectorAll('[data-share-menu]');
    shareMenus.forEach(menu => menu.remove());
}

// Event listeners
modalBetaClose.onclick = closeModalBeta;

window.onclick = function(event) {
    if (event.target == modalBeta) {
        closeModalBeta();
    }
}

// View High Resolution
document.getElementById('btnViewHighRes').onclick = function() {
    if (currentImageDataBeta && currentImageDataBeta.url) {
        window.open(currentImageDataBeta.url, '_blank');
    }
};

// Download Full Size
document.getElementById('btnDownload').onclick = function() {
    if (currentImageDataBeta && currentImageDataBeta.url) {
        const link = document.createElement('a');
        link.href = currentImageDataBeta.url;
        link.download = currentImageDataBeta.filename || 'image.jpg';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
};

// Share on Social Media
document.getElementById('btnShare').onclick = function() {
    if (!currentImageDataBeta) {
        alert('No image selected');
        return;
    }
    
    // Get the full image URL and create shareable page URL
    const imageUrl = window.location.origin + currentImageDataBeta.url;
    // Extract actual filename from URL (e.g., /images/file.jpg -> file.jpg)
    const actualFilename = currentImageDataBeta.url.split('/').pop();
    const sharePageUrl = window.location.origin + '/photo/' + actualFilename;
    const title = encodeURIComponent(currentImageDataBeta.title || 'Fifth Element Photography');
    const description = encodeURIComponent('Check out this image from Fifth Element Photography');
    
    // Create share menu
    const shareMenu = document.createElement('div');
    shareMenu.setAttribute('data-share-menu', 'true');
    shareMenu.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1a1a1a; padding: 20px; border-radius: 8px; z-index: 10002; box-shadow: 0 4px 20px rgba(0,0,0,0.5);';
    shareMenu.innerHTML = `
        <h3 style="color: #fff; margin-bottom: 15px; font-family: Poppins, sans-serif;">Share on Social Media</h3>
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <a href="https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(sharePageUrl)}" target="_blank" style="background: #4267B2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-family: Poppins, sans-serif;">Share on Facebook</a>
            <a href="https://twitter.com/intent/tweet?url=${encodeURIComponent(sharePageUrl)}&text=${title}" target="_blank" style="background: #1DA1F2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-family: Poppins, sans-serif;">Share on Twitter</a>
            <a href="https://pinterest.com/pin/create/button/?url=${encodeURIComponent(sharePageUrl)}&media=${encodeURIComponent(imageUrl)}&description=${title}" target="_blank" style="background: #E60023; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-family: Poppins, sans-serif;">Share on Pinterest</a>
            <button onclick="this.parentElement.parentElement.remove()" style="background: #666; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-family: Poppins, sans-serif;">Cancel</button>
        </div>
    `;
    document.body.appendChild(shareMenu);
};

// ORDER PRINTS button - use same function as old modal
document.getElementById('btnOrderPrints').onclick = function() {
    // Call the existing openOrderWizard function from script.js
    if (typeof openOrderWizard === 'function') {
        openOrderWizard();
    } else {
        console.error('openOrderWizard function not found');
        alert('Order function not available. Please refresh the page.');
    }
};

// Expose openModalBeta globally
window.openModalBeta = openModalBeta;
