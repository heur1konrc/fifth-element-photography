// Image Sort and Filter Functionality
// Fifth Element Photography Admin

function applySortAndFilter() {
    const sortBy = document.getElementById('sortBy').value;
    const galleryFilter = document.getElementById('galleryFilter').value;
    const searchTerm = document.getElementById('imageSearch').value.toLowerCase();
    
    console.log('Sort by:', sortBy);
    
    // Get selected category filters
    const categoryCheckboxes = document.querySelectorAll('.category-filter-checkbox:checked');
    const selectedCategories = Array.from(categoryCheckboxes).map(cb => cb.value.toLowerCase());
    
    // Get all image panels
    const imageGrid = document.querySelector('.image-grid');
    if (!imageGrid) {
        console.error('Image grid not found');
        return;
    }
    
    const imagePanels = Array.from(imageGrid.querySelectorAll('.image-panel-new'));
    console.log('Found panels:', imagePanels.length);
    
    // Filter images
    imagePanels.forEach(panel => {
        let show = true;
        
        // Search filter
        if (searchTerm) {
            const title = (panel.dataset.title || '').toLowerCase();
            const filename = (panel.dataset.filename || '').toLowerCase();
            if (!title.includes(searchTerm) && !filename.includes(searchTerm)) {
                show = false;
            }
        }
        
        // Category filter
        if (selectedCategories.length > 0) {
            const panelCategories = (panel.dataset.categories || '').toLowerCase().split(',').map(c => c.trim());
            const hasMatchingCategory = selectedCategories.some(cat => panelCategories.includes(cat));
            if (!hasMatchingCategory) {
                show = false;
            }
        }
        
        // Gallery filter
        if (galleryFilter) {
            const panelGalleries = (panel.dataset.galleries || '').toLowerCase().split(',').map(g => g.trim());
            if (!panelGalleries.includes(galleryFilter.toLowerCase())) {
                show = false;
            }
        }
        
        panel.style.display = show ? '' : 'none';
    });
    
    // Get visible panels for sorting
    const visiblePanels = imagePanels.filter(panel => panel.style.display !== 'none');
    console.log('Visible panels:', visiblePanels.length);
    
    // Sort visible panels
    visiblePanels.sort((a, b) => {
        switch(sortBy) {
            case 'az':
                return (a.dataset.title || a.dataset.filename || '').localeCompare(b.dataset.title || b.dataset.filename || '');
            case 'za':
                return (b.dataset.title || b.dataset.filename || '').localeCompare(a.dataset.title || a.dataset.filename || '');
            case 'date-new':
                return (b.dataset.dateAdded || '').localeCompare(a.dataset.dateAdded || '');
            case 'date-old':
                return (a.dataset.dateAdded || '').localeCompare(b.dataset.dateAdded || '');
            case 'category':
                return (a.dataset.categories || '').localeCompare(b.dataset.categories || '');
            case 'gallery':
                return (a.dataset.galleries || '').localeCompare(b.dataset.galleries || '');
            default:
                return 0;
        }
    });
    
    // Clear grid and re-append all panels in correct order
    // First, append all hidden panels
    imagePanels.forEach(panel => {
        if (panel.style.display === 'none') {
            imageGrid.appendChild(panel);
        }
    });
    
    // Then append visible sorted panels
    visiblePanels.forEach(panel => imageGrid.appendChild(panel));
    
    // Update count
    updateVisibleCount(visiblePanels.length, imagePanels.length);
}

function updateVisibleCount(visible, total) {
    const titleElement = document.querySelector('.section-title');
    if (titleElement) {
        const baseText = titleElement.textContent.split('(')[0].trim();
        if (visible < total) {
            titleElement.textContent = `${baseText} (${visible} of ${total} images shown)`;
        } else {
            titleElement.textContent = `${baseText} (${total} images)`;
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Image sort and filter initialized');
});
