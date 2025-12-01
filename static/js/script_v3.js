// Global variables
let allImages = [];
let categories = [];
let currentCategory = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadImages();
    setupModal();
});

// Load all images from API
async function loadImages() {
    try {
        const response = await fetch('/api/v3/images');
        allImages = await response.json();
        
        // Extract unique categories
        extractCategories();
        
        // Load featured images
        loadFeaturedGallery();
        
        // Load category navigation
        loadCategoryNav();
        
    } catch (error) {
        console.error('Error loading images:', error);
    }
}

// Extract unique categories from all images
function extractCategories() {
    const categorySet = new Set();
    allImages.forEach(image => {
        if (image.categories && Array.isArray(image.categories)) {
            image.categories.forEach(cat => categorySet.add(cat));
        }
    });
    categories = Array.from(categorySet).sort();
}

// Load featured gallery with staggered grid
function loadFeaturedGallery() {
    const featuredGrid = document.getElementById('featuredGrid');
    
    // Show first 7 images for Pixie layout
    let featuredImages = allImages.slice(0, 7);
    
    featuredGrid.innerHTML = '';
    
    featuredImages.forEach(image => {
        const item = document.createElement('div');
        item.className = 'featured-item';
        item.innerHTML = `<img src="/data/thumbnails/${image.filename}" alt="${image.title}">`;
        item.addEventListener('click', () => openModal(image));
        featuredGrid.appendChild(item);
    });
}

// Load category navigation buttons
function loadCategoryNav() {
    const categoryNav = document.getElementById('categoryNav');
    categoryNav.innerHTML = '';
    
    categories.forEach((category, index) => {
        const btn = document.createElement('button');
        btn.className = 'category-btn';
        if (index === 0) btn.classList.add('active');
        btn.textContent = category;
        btn.addEventListener('click', () => selectCategory(category, btn));
        categoryNav.appendChild(btn);
    });
    
    // Load first category by default
    if (categories.length > 0) {
        selectCategory(categories[0]);
    }
}

// Select and display a category
function selectCategory(category, clickedBtn) {
    currentCategory = category;
    
    // Update active button
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (clickedBtn) {
        clickedBtn.classList.add('active');
    }
    
    // Load category slide
    loadCategorySlide(category);
}

// Load category slide with staggered rows
function loadCategorySlide(category) {
    const container = document.getElementById('categorySlideContainer');
    
    // Filter images by category
    const categoryImages = allImages.filter(img => 
        img.categories && img.categories.includes(category)
    );
    
    container.innerHTML = '';
    
    if (categoryImages.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">No images in this category</p>';
        return;
    }
    
    // Create staggered rows (alternating left/right)
    const imagesPerRow = 4;
    const rows = Math.ceil(categoryImages.length / imagesPerRow);
    
    for (let i = 0; i < rows; i++) {
        const row = document.createElement('div');
        row.className = `slide-row ${i % 2 === 0 ? 'left' : 'right'}`;
        
        const startIdx = i * imagesPerRow;
        const endIdx = Math.min(startIdx + imagesPerRow, categoryImages.length);
        const rowImages = categoryImages.slice(startIdx, endIdx);
        
        rowImages.forEach(image => {
            const item = document.createElement('div');
            item.className = 'slide-item';
            item.innerHTML = `<img src="/data/thumbnails/${image.filename}" alt="${image.title}">`;
            item.addEventListener('click', () => openModal(image));
            row.appendChild(item);
        });
        
        container.appendChild(row);
    }
}

// Modal functionality
function setupModal() {
    const modal = document.getElementById('imageModal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.addEventListener('click', closeModal);
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

function openModal(image) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    const modalCategory = document.getElementById('modalCategory');
    const modalDescription = document.getElementById('modalDescription');
    
    modalImage.src = `/data/${image.filename}`;
    modalTitle.textContent = image.title || 'Untitled';
    modalCategory.textContent = image.categories ? image.categories.join(', ') : '';
    modalDescription.textContent = image.description || '';
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}
