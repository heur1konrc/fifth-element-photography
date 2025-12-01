// State
const state = {
    images: [],
    categories: [],
    currentCategory: 'all',
    currentPage: 1,
    imagesPerPage: 12
};

// Init
document.addEventListener('DOMContentLoaded', () => {
    loadHeroImage();
    loadCategories();
    loadImages();
});

// Load Hero Image
async function loadHeroImage() {
    try {
        const response = await fetch('/api/v3/hero-image');
        const data = await response.json();
        
        if (data.success && data.hero_image) {
            const heroSection = document.getElementById('heroSection');
            heroSection.style.backgroundImage = `url('/data/${data.hero_image.filename}')`;
        }
    } catch (error) {
        console.error('Error loading hero image:', error);
    }
}

// Load Categories
async function loadCategories() {
    try {
        const response = await fetch('/api/v3/categories');
        const data = await response.json();
        
        if (data.success) {
            state.categories = data.categories.sort();
            renderFilters();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Load Images
async function loadImages() {
    try {
        const response = await fetch('/api/v3/images');
        const data = await response.json();
        
        if (Array.isArray(data)) {
            state.images = data;
            renderGallery();
        }
    } catch (error) {
        console.error('Error loading images:', error);
        document.getElementById('gallery').innerHTML = '<div class="loading">Error loading images</div>';
    }
}

// Render Filters
function renderFilters() {
    const filtersContainer = document.getElementById('categoryFilters');
    filtersContainer.innerHTML = '<button class="filter-btn active" data-category="all">All</button>';
    
    state.categories.forEach(category => {
        const btn = document.createElement('button');
        btn.className = 'filter-btn';
        btn.dataset.category = category;
        btn.textContent = category;
        btn.addEventListener('click', () => filterByCategory(category));
        filtersContainer.appendChild(btn);
    });
    
    // Add event listener to "All" button
    filtersContainer.querySelector('[data-category="all"]').addEventListener('click', () => filterByCategory('all'));
}

// Filter by Category
function filterByCategory(category) {
    state.currentCategory = category;
    state.currentPage = 1;
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === category);
    });
    
    renderGallery();
}

// Get Filtered Images
function getFilteredImages() {
    if (state.currentCategory === 'all') {
        return state.images;
    }
    return state.images.filter(img => 
        img.categories && img.categories.includes(state.currentCategory)
    );
}

// Render Gallery
function renderGallery() {
    const gallery = document.getElementById('gallery');
    const filteredImages = getFilteredImages();
    
    if (filteredImages.length === 0) {
        gallery.innerHTML = '<div class="loading">No images found</div>';
        return;
    }
    
    // Pagination
    const totalPages = Math.ceil(filteredImages.length / state.imagesPerPage);
    const startIndex = (state.currentPage - 1) * state.imagesPerPage;
    const endIndex = startIndex + state.imagesPerPage;
    const pageImages = filteredImages.slice(startIndex, endIndex);
    
    // Render images
    gallery.innerHTML = pageImages.map(image => `
        <div class="gallery-item">
            <img src="/data/thumbnails/${image.filename}" alt="${image.title}" loading="lazy">
            <div class="gallery-overlay">
                <div class="gallery-title">${image.title}</div>
                <div class="gallery-category">${image.categories && image.categories.length > 0 ? image.categories[0] : 'Uncategorized'}</div>
            </div>
        </div>
    `).join('');
    
    // Render pagination
    renderPagination(totalPages);
}

// Render Pagination
function renderPagination(totalPages) {
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `<button ${state.currentPage === 1 ? 'disabled' : ''} onclick="changePage(${state.currentPage - 1})">← Prev</button>`;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || Math.abs(i - state.currentPage) <= 1) {
            html += `<button class="${i === state.currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
        } else if (Math.abs(i - state.currentPage) === 2) {
            html += `<span style="padding: 0 10px; color: #666;">...</span>`;
        }
    }
    
    // Next button
    html += `<button ${state.currentPage === totalPages ? 'disabled' : ''} onclick="changePage(${state.currentPage + 1})">Next →</button>`;
    
    pagination.innerHTML = html;
}

// Change Page
function changePage(page) {
    state.currentPage = page;
    renderGallery();
    window.scrollTo({ top: document.querySelector('.portfolio').offsetTop - 100, behavior: 'smooth' });
}
