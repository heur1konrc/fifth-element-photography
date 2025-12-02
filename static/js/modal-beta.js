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
    
    // Populate EXIF data
    document.getElementById('exifModel').textContent = imageData.camera_model || 'Unavailable';
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
    console.log('Image data:', imageData);
    console.log('order_prints_enabled:', imageData.order_prints_enabled);
    console.log('shopify_product_handle:', imageData.shopify_product_handle);
    
    if (imageData.order_prints_enabled && imageData.shopify_product_handle) {
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
    if (navigator.share && currentImageDataBeta) {
        navigator.share({
            title: currentImageDataBeta.title || 'Fifth Element Photography',
            text: 'Check out this image from Fifth Element Photography',
            url: window.location.href
        }).catch(err => console.log('Error sharing:', err));
    } else {
        alert('Sharing not supported on this browser');
    }
};

// ORDER PRINTS button
document.getElementById('btnOrderPrints').onclick = function() {
    if (currentImageDataBeta && currentImageDataBeta.shopify_product_handle) {
        const shopifyUrl = `https://fifth-element-photography.myshopify.com/products/${currentImageDataBeta.shopify_product_handle}`;
        window.open(shopifyUrl, '_blank');
    }
};

// Expose openModalBeta globally
window.openModalBeta = openModalBeta;
