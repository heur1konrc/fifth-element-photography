/**
 * Fifth Element Photography V3 - Test Front-End JavaScript
 * Version: 3.0.0-alpha
 * 
 * Simple JavaScript to fetch and display images from the admin API
 * This validates that the admin dashboard is working correctly
 */

// ===================================
// INITIALIZATION
// ===================================
document.addEventListener('DOMContentLoaded', function() {
    loadImages();
});

/**
 * Load all images from the API
 * Fetches images and displays them in the gallery
 */
async function loadImages() {
    const gallery = document.getElementById('image-gallery');
    
    try {
        // Fetch images from the API
        const response = await fetch('/api/v3/images');
        
        if (!response.ok) {
            throw new Error('Failed to load images');
        }
        
        const images = await response.json();
        
        // Clear loading message
        gallery.innerHTML = '';
        
        // Check if there are any images
        if (images.length === 0) {
            displayEmptyState(gallery);
            return;
        }
        
        // Display each image
        images.forEach(image => {
            const card = createImageCard(image);
            gallery.appendChild(card);
        });
        
    } catch (error) {
        console.error('Error loading images:', error);
        gallery.innerHTML = '<div class="loading">Error loading images. Please try again later.</div>';
    }
}

/**
 * Create an image card element
 * @param {Object} image - Image data object
 * @returns {HTMLElement} - Image card element
 */
function createImageCard(image) {
    const card = document.createElement('div');
    card.className = 'image-card';
    
    // Build image URL - use thumbnail for gallery, full image on click
    const thumbnailUrl = `/data/thumbnails/${image.filename}`;
    const fullImageUrl = `/data/${image.filename}`;
    
    // Build categories HTML
    let categoriesHtml = '';
    if (image.categories && image.categories.length > 0) {
        categoriesHtml = '<div class="image-categories">';
        image.categories.forEach(category => {
            categoriesHtml += `<span class="category-badge">${escapeHtml(category)}</span>`;
        });
        categoriesHtml += '</div>';
    }
    
    // Build card HTML
    card.innerHTML = `
        <img src="${thumbnailUrl}" alt="${escapeHtml(image.title || 'Untitled')}" loading="lazy">
        <div class="image-info">
            <h3 class="image-title">${escapeHtml(image.title || 'Untitled')}</h3>
            ${image.description ? `<p class="image-description">${escapeHtml(image.description)}</p>` : ''}
            ${categoriesHtml}
        </div>
    `;
    
    return card;
}

/**
 * Display empty state when no images exist
 * @param {HTMLElement} gallery - Gallery container element
 */
function displayEmptyState(gallery) {
    gallery.innerHTML = `
        <div class="empty-state">
            <p>No images found.</p>
            <p>Use the admin dashboard to upload images.</p>
        </div>
    `;
}

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} text - Text to escape
 * @returns {string} - Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

