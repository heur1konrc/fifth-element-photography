// Image Sort and Filter Functionality
// Fifth Element Photography Admin
// Updated to use URL parameters for persistence across pagination

function applySortAndFilter() {
    const sortBy = document.getElementById('sortBy').value;
    const galleryFilter = document.getElementById('galleryFilter').value;
    const searchTerm = document.getElementById('imageSearch').value.trim();
    
    // Build URL with current filters
    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);
    
    // Update sort parameter
    if (sortBy) {
        params.set('sort', sortBy);
    } else {
        params.delete('sort');
    }
    
    // Update search parameter
    if (searchTerm) {
        params.set('search', searchTerm);
    } else {
        params.delete('search');
    }
    
    // Update gallery parameter
    if (galleryFilter) {
        params.set('gallery', galleryFilter);
    } else {
        params.delete('gallery');
    }
    
    // Reset to page 1 when filters change
    params.set('page', '1');
    
    // Reload page with new parameters
    window.location.href = `${url.pathname}?${params.toString()}`;
}

// Debounce function for search input
let searchTimeout;
function debouncedSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        applySortAndFilter();
    }, 500); // Wait 500ms after user stops typing
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Image sort and filter initialized');
    
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('search') || '';
    const galleryFilter = urlParams.get('gallery') || '';
    const sortBy = urlParams.get('sort') || 'az';
    
    // Set input values from URL
    const searchInput = document.getElementById('imageSearch');
    const gallerySelect = document.getElementById('galleryFilter');
    const sortSelect = document.getElementById('sortBy');
    
    if (searchInput && searchQuery) {
        searchInput.value = searchQuery;
    }
    
    if (gallerySelect && galleryFilter) {
        gallerySelect.value = galleryFilter;
    }
    
    if (sortSelect && sortBy) {
        sortSelect.value = sortBy;
    }
    
    // Update event listeners to use debounced search for input
    if (searchInput) {
        searchInput.removeAttribute('oninput');
        searchInput.addEventListener('input', debouncedSearch);
    }
    
    if (gallerySelect) {
        gallerySelect.removeAttribute('onchange');
        gallerySelect.addEventListener('change', applySortAndFilter);
    }
    
    if (sortSelect) {
        sortSelect.removeAttribute('onchange');
        sortSelect.addEventListener('change', applySortAndFilter);
    }
});
