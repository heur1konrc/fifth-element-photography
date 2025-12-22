// Category and Gallery Selector Modals
// Fifth Element Photography Admin

let currentImageFilename = null;
let currentImageCategories = [];
let currentImageGalleries = [];

// All available categories
const ALL_CATEGORIES = [
    'Architecture', 'Autumn 2025', 'Events', 'Flora', 'Fowl', 'Landscapes',
    'Low Res', 'Mid Res', 'Nature', 'Other', 'Pets', 'Portrait', 'Print Ready',
    'Sports', 'Travel', 'Wildlife'
];

// Category Selector Functions
function openCategorySelector(filename) {
    currentImageFilename = filename;
    
    // Get current categories from the panel
    const panel = document.querySelector(`[data-filename="${filename}"]`);
    const categoriesAttr = panel.dataset.categories || '';
    currentImageCategories = categoriesAttr ? categoriesAttr.split(',').map(c => c.trim()) : [];
    
    // Populate category options
    const optionsContainer = document.getElementById('categoryOptions');
    optionsContainer.innerHTML = '';
    
    ALL_CATEGORIES.forEach(category => {
        const isChecked = currentImageCategories.includes(category);
        const optionDiv = document.createElement('div');
        optionDiv.className = 'selector-option';
        optionDiv.innerHTML = `
            <input type="checkbox" id="cat-${category.replace(/\s+/g, '-')}" value="${category}" ${isChecked ? 'checked' : ''}>
            <label for="cat-${category.replace(/\s+/g, '-')}">${category}</label>
        `;
        optionsContainer.appendChild(optionDiv);
    });
    
    // Show modal
    document.getElementById('categoryModal').classList.add('active');
}

function closeCategorySelector() {
    document.getElementById('categoryModal').classList.remove('active');
    currentImageFilename = null;
    currentImageCategories = [];
}

async function saveCategoryChanges() {
    if (!currentImageFilename) return;
    
    // Get selected categories
    const checkboxes = document.querySelectorAll('#categoryOptions input[type="checkbox"]:checked');
    const selectedCategories = Array.from(checkboxes).map(cb => cb.value);
    
    try {
        const response = await fetch('/admin/update-image-categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: currentImageFilename,
                categories: selectedCategories
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Categories updated successfully', 'success');
            // Reload page to reflect changes
            setTimeout(() => location.reload(), 500);
        } else {
            showNotification('Failed to update categories: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error updating categories:', error);
        showNotification('Error updating categories', 'error');
    }
    
    closeCategorySelector();
}

// Gallery Selector Functions
function openGallerySelector(filename) {
    currentImageFilename = filename;
    
    // Get current galleries from the panel
    const panel = document.querySelector(`[data-filename="${filename}"]`);
    const galleriesAttr = panel.dataset.galleries || '';
    currentImageGalleries = galleriesAttr ? galleriesAttr.split(',').map(g => g.trim()) : [];
    
    // Fetch available galleries from server
    fetchGalleries();
}

async function fetchGalleries() {
    try {
        const response = await fetch('/admin/get-galleries');
        const data = await response.json();
        
        if (data.success) {
            populateGalleryOptions(data.galleries);
            document.getElementById('galleryModal').classList.add('active');
        } else {
            showNotification('Failed to load galleries', 'error');
        }
    } catch (error) {
        console.error('Error fetching galleries:', error);
        showNotification('Error loading galleries', 'error');
    }
}

function populateGalleryOptions(galleries) {
    const optionsContainer = document.getElementById('galleryOptions');
    optionsContainer.innerHTML = '';
    
    if (galleries.length === 0) {
        optionsContainer.innerHTML = '<p style="color: #888;">No galleries available</p>';
        return;
    }
    
    galleries.forEach(gallery => {
        const isChecked = currentImageGalleries.includes(gallery);
        const optionDiv = document.createElement('div');
        optionDiv.className = 'selector-option';
        optionDiv.innerHTML = `
            <input type="checkbox" id="gal-${gallery.replace(/\s+/g, '-')}" value="${gallery}" ${isChecked ? 'checked' : ''}>
            <label for="gal-${gallery.replace(/\s+/g, '-')}">${gallery}</label>
        `;
        optionsContainer.appendChild(optionDiv);
    });
}

function closeGallerySelector() {
    document.getElementById('galleryModal').classList.remove('active');
    currentImageFilename = null;
    currentImageGalleries = [];
}

async function saveGalleryChanges() {
    if (!currentImageFilename) return;
    
    // Get selected galleries
    const checkboxes = document.querySelectorAll('#galleryOptions input[type="checkbox"]:checked');
    const selectedGalleries = Array.from(checkboxes).map(cb => cb.value);
    
    try {
        const response = await fetch('/admin/update-image-galleries', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: currentImageFilename,
                galleries: selectedGalleries
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Galleries updated successfully', 'success');
            // Reload page to reflect changes
            setTimeout(() => location.reload(), 500);
        } else {
            showNotification('Failed to update galleries: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error updating galleries:', error);
        showNotification('Error updating galleries', 'error');
    }
    
    closeGallerySelector();
}

// Close modals when clicking outside
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('selector-modal')) {
        closeCategorySelector();
        closeGallerySelector();
    }
});
