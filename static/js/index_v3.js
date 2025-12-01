/**
 * Fifth Element Photography V3 - Frontend JavaScript
 * Handles navigation, gallery, pagination, and modal interactions
 */

// ===================================
// STATE MANAGEMENT
// ===================================
const AppState = {
    currentSection: 'home',
    images: [],
    categories: [],
    currentCategory: 'all',
    currentPage: 1,
    imagesPerPage: 12,
    featuredImage: null,
    heroImage: null
};

// ===================================
// INITIALIZATION
// ===================================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initMobileMenu();
    loadHeroImage();
    loadCategories();
    loadImages();
    loadFeaturedImage();
});

// ===================================
// NAVIGATION
// ===================================
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            navigateToSection(section);
        });
    });
    
    // Handle hash navigation
    if (window.location.hash) {
        const section = window.location.hash.substring(1);
        navigateToSection(section);
    }
}

function navigateToSection(sectionName) {
    // Update state
    AppState.currentSection = sectionName;
    
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.section === sectionName) {
            link.classList.add('active');
        }
    });
    
    // Update URL hash
    window.location.hash = sectionName;
    
    // Close mobile menu if open
    closeMobileMenu();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===================================
// MOBILE MENU
// ===================================
function initMobileMenu() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
}

function closeMobileMenu() {
    const navMenu = document.getElementById('navMenu');
    if (navMenu) {
        navMenu.classList.remove('active');
    }
}

// ===================================
// HERO IMAGE
// ===================================
async function loadHeroImage() {
    try {
        const response = await fetch('/api/v3/hero-image');
        const data = await response.json();
        
        if (data.success && data.hero_image) {
            AppState.heroImage = data.hero_image;
            displayHeroImage();
        }
    } catch (error) {
        console.error('Error loading hero image:', error);
        // Use fallback image
        document.getElementById('heroImage').style.backgroundImage = 
            'url("/static/images/logo-square.png")';
    }
}

function displayHeroImage() {
    const heroImage = document.getElementById('heroImage');
    if (AppState.heroImage && AppState.heroImage.url) {
        heroImage.style.backgroundImage = `url("${AppState.heroImage.url}")`;
    }
}

// ===================================
// CATEGORIES
// ===================================
async function loadCategories() {
    try {
        const response = await fetch('/api/v3/categories');
        const data = await response.json();
        
        if (data.success) {
            AppState.categories = data.categories.sort();
            displayCategoryFilters();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

function displayCategoryFilters() {
    const filtersContainer = document.getElementById('categoryFilters');
    
    // Clear existing filters except "All"
    filtersContainer.innerHTML = '<button class="filter-btn active" data-category="all">All</button>';
    
    // Add category filters
    AppState.categories.forEach(category => {
        const btn = document.createElement('button');
        btn.className = 'filter-btn';
        btn.dataset.category = category;
        btn.textContent = category;
        btn.addEventListener('click', () => filterByCategory(category));
        filtersContainer.appendChild(btn);
    });
    
    // Add event listener to "All" button
    const allBtn = filtersContainer.querySelector('[data-category="all"]');
    allBtn.addEventListener('click', () => filterByCategory('all'));
}

function filterByCategory(category) {
    AppState.currentCategory = category;
    AppState.currentPage = 1;
    
    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.category === category) {
            btn.classList.add('active');
        }
    });
    
    displayGallery();
}

// ===================================
// GALLERY
// ===================================
async function loadImages() {
    try {
        const response = await fetch('/api/v3/images');
        const data = await response.json();
        
        if (Array.isArray(data)) {
            AppState.images = data;
            displayGallery();
        } else if (data.success) {
            AppState.images = data.images;
            displayGallery();
        }
    } catch (error) {
        console.error('Error loading images:', error);
        document.getElementById('galleryGrid').innerHTML = 
            '<div class="loading">Error loading images. Please try again later.</div>';
    }
}

function getFilteredImages() {
    if (AppState.currentCategory === 'all') {
        return AppState.images;
    }
    return AppState.images.filter(img => 
        img.categories && img.categories.includes(AppState.currentCategory)
    );
}

function displayGallery() {
    const galleryGrid = document.getElementById('galleryGrid');
    const filteredImages = getFilteredImages();
    
    if (filteredImages.length === 0) {
        galleryGrid.innerHTML = '<div class="loading">No images found in this category.</div>';
        return;
    }
    
    // Calculate pagination
    const totalPages = Math.ceil(filteredImages.length / AppState.imagesPerPage);
    const startIndex = (AppState.currentPage - 1) * AppState.imagesPerPage;
    const endIndex = startIndex + AppState.imagesPerPage;
    const pageImages = filteredImages.slice(startIndex, endIndex);
    
    // Clear gallery
    galleryGrid.innerHTML = '';
    
    // Add images
    pageImages.forEach(image => {
        const item = createGalleryItem(image);
        galleryGrid.appendChild(item);
    });
    
    // Update pagination
    displayPagination(totalPages);
}

function createGalleryItem(image) {
    const item = document.createElement('div');
    item.className = 'gallery-item';
    item.addEventListener('click', () => openImageModal(image));
    
    const img = document.createElement('img');
    img.src = image.thumbnail_url || image.url || `/data/thumbnails/${image.filename}`;
    img.alt = image.title || 'Untitled';
    img.loading = 'lazy';
    
    const overlay = document.createElement('div');
    overlay.className = 'gallery-item-overlay';
    
    const title = document.createElement('div');
    title.className = 'gallery-item-title';
    title.textContent = image.title || 'Untitled';
    
    const category = document.createElement('div');
    category.className = 'gallery-item-category';
    category.textContent = image.categories ? image.categories.join(', ') : '';
    
    overlay.appendChild(title);
    overlay.appendChild(category);
    
    item.appendChild(img);
    item.appendChild(overlay);
    
    return item;
}

// ===================================
// PAGINATION
// ===================================
function displayPagination(totalPages) {
    const paginationContainer = document.getElementById('pagination');
    paginationContainer.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.className = 'pagination-btn';
    prevBtn.textContent = '← Prev';
    prevBtn.disabled = AppState.currentPage === 1;
    prevBtn.addEventListener('click', () => changePage(AppState.currentPage - 1));
    paginationContainer.appendChild(prevBtn);
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        // Show first, last, current, and adjacent pages
        if (i === 1 || i === totalPages || Math.abs(i - AppState.currentPage) <= 1) {
            const pageBtn = document.createElement('button');
            pageBtn.className = 'pagination-btn';
            if (i === AppState.currentPage) {
                pageBtn.classList.add('active');
            }
            pageBtn.textContent = i;
            pageBtn.addEventListener('click', () => changePage(i));
            paginationContainer.appendChild(pageBtn);
        } else if (Math.abs(i - AppState.currentPage) === 2) {
            // Add ellipsis
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.style.padding = '0.5rem';
            ellipsis.style.color = 'var(--color-muted)';
            paginationContainer.appendChild(ellipsis);
        }
    }
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.className = 'pagination-btn';
    nextBtn.textContent = 'Next →';
    nextBtn.disabled = AppState.currentPage === totalPages;
    nextBtn.addEventListener('click', () => changePage(AppState.currentPage + 1));
    paginationContainer.appendChild(nextBtn);
}

function changePage(page) {
    AppState.currentPage = page;
    displayGallery();
    
    // Scroll to top of gallery
    document.getElementById('portfolio-section').scrollIntoView({ behavior: 'smooth' });
}

// ===================================
// IMAGE MODAL
// ===================================
function openImageModal(image) {
    const modal = document.getElementById('imageModal');
    const modalBody = document.getElementById('modalBody');
    
    // Build modal content
    modalBody.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">
            <div>
                <img src="${image.url || `/data/${image.filename}`}" alt="${escapeHtml(image.title || 'Untitled')}" 
                     style="width: 100%; height: auto; border: 1px solid var(--color-border);">
            </div>
            <div style="padding: 1rem 0;">
                <h2 style="font-size: 2rem; font-weight: 400; margin-bottom: 1rem; color: var(--color-text);">
                    ${escapeHtml(image.title || 'Untitled')}
                </h2>
                ${image.description ? `
                    <p style="font-size: 1.1rem; line-height: 1.8; color: var(--color-muted-light); margin-bottom: 2rem;">
                        ${escapeHtml(image.description)}
                    </p>
                ` : ''}
                ${image.categories && image.categories.length > 0 ? `
                    <div style="margin-bottom: 2rem;">
                        <strong style="color: var(--color-primary);">Categories:</strong> 
                        ${image.categories.map(c => escapeHtml(c)).join(', ')}
                    </div>
                ` : ''}
                ${image.shopify_product_id ? `
                    <button onclick="orderPrints('${image.shopify_product_id}')" 
                            style="background: var(--color-primary); border: none; color: var(--color-bg); 
                                   padding: 1rem 2rem; font-family: var(--font-primary); font-size: 1rem; 
                                   font-weight: 500; text-transform: uppercase; letter-spacing: 1px; 
                                   cursor: pointer; width: 100%; margin-bottom: 2rem;">
                        🛒 Order Prints
                    </button>
                ` : ''}
                ${image.exif ? displayExifData(image.exif) : ''}
            </div>
        </div>
    `;
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function displayExifData(exif) {
    return `
        <div style="background: rgba(255,255,255,0.05); border: 1px solid var(--color-border); padding: 1.5rem;">
            <h3 style="font-size: 1.2rem; font-weight: 400; margin-bottom: 1rem; color: var(--color-primary);">
                Camera Settings
            </h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                ${exif.camera ? `
                    <div>
                        <div style="font-size: 0.85rem; color: var(--color-muted); text-transform: uppercase; letter-spacing: 1px;">Camera</div>
                        <div style="font-size: 1rem; color: var(--color-text);">${escapeHtml(exif.camera)}</div>
                    </div>
                ` : ''}
                ${exif.lens ? `
                    <div>
                        <div style="font-size: 0.85rem; color: var(--color-muted); text-transform: uppercase; letter-spacing: 1px;">Lens</div>
                        <div style="font-size: 1rem; color: var(--color-text);">${escapeHtml(exif.lens)}</div>
                    </div>
                ` : ''}
                ${exif.focal_length ? `
                    <div>
                        <div style="font-size: 0.85rem; color: var(--color-muted); text-transform: uppercase; letter-spacing: 1px;">Focal Length</div>
                        <div style="font-size: 1rem; color: var(--color-text);">${escapeHtml(exif.focal_length)}</div>
                    </div>
                ` : ''}
                ${exif.aperture ? `
                    <div>
                        <div style="font-size: 0.85rem; color: var(--color-muted); text-transform: uppercase; letter-spacing: 1px;">Aperture</div>
                        <div style="font-size: 1rem; color: var(--color-text);">${escapeHtml(exif.aperture)}</div>
                    </div>
                ` : ''}
                ${exif.shutter_speed ? `
                    <div>
                        <div style="font-size: 0.85rem; color: var(--color-muted); text-transform: uppercase; letter-spacing: 1px;">Shutter Speed</div>
                        <div style="font-size: 1rem; color: var(--color-text);">${escapeHtml(exif.shutter_speed)}</div>
                    </div>
                ` : ''}
                ${exif.iso ? `
                    <div>
                        <div style="font-size: 0.85rem; color: var(--color-muted); text-transform: uppercase; letter-spacing: 1px;">ISO</div>
                        <div style="font-size: 1rem; color: var(--color-text);">${escapeHtml(exif.iso)}</div>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

// Modal close handlers
document.getElementById('modalClose').addEventListener('click', closeImageModal);
document.getElementById('modalOverlay').addEventListener('click', closeImageModal);

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeImageModal();
    }
});

// ===================================
// ORDER PRINTS (Shopify Integration)
// ===================================
function orderPrints(shopifyProductId) {
    // TODO: Implement Shopify product page redirect
    // For now, open in new tab
    window.open(`https://your-shopify-store.myshopify.com/products/${shopifyProductId}`, '_blank');
}

// ===================================
// FEATURED IMAGE
// ===================================
async function loadFeaturedImage() {
    try {
        const response = await fetch('/api/v3/featured-image');
        const data = await response.json();
        
        if (data.success && data.featured_image) {
            AppState.featuredImage = data.featured_image;
            displayFeaturedImage();
        }
    } catch (error) {
        console.error('Error loading featured image:', error);
        document.getElementById('featuredContent').innerHTML = 
            '<div class="loading">No featured image available.</div>';
    }
}

function displayFeaturedImage() {
    const container = document.getElementById('featuredContent');
    const image = AppState.featuredImage;
    
    container.innerHTML = `
        <div class="featured-content">
            <div class="featured-image-container">
                <img src="${image.url || `/data/${image.filename}`}" alt="${escapeHtml(image.title || 'Featured Image')}">
            </div>
            <div class="featured-details">
                <h2 class="featured-title">${escapeHtml(image.title || 'Untitled')}</h2>
                ${image.story ? `
                    <div class="featured-story">${escapeHtml(image.story)}</div>
                ` : ''}
                ${image.exif ? `
                    <div class="featured-exif">
                        <h3>Camera Settings</h3>
                        <div class="exif-grid">
                            ${image.exif.camera ? `
                                <div class="exif-item">
                                    <div class="exif-label">Camera</div>
                                    <div class="exif-value">${escapeHtml(image.exif.camera)}</div>
                                </div>
                            ` : ''}
                            ${image.exif.lens ? `
                                <div class="exif-item">
                                    <div class="exif-label">Lens</div>
                                    <div class="exif-value">${escapeHtml(image.exif.lens)}</div>
                                </div>
                            ` : ''}
                            ${image.exif.focal_length ? `
                                <div class="exif-item">
                                    <div class="exif-label">Focal Length</div>
                                    <div class="exif-value">${escapeHtml(image.exif.focal_length)}</div>
                                </div>
                            ` : ''}
                            ${image.exif.aperture ? `
                                <div class="exif-item">
                                    <div class="exif-label">Aperture</div>
                                    <div class="exif-value">${escapeHtml(image.exif.aperture)}</div>
                                </div>
                            ` : ''}
                            ${image.exif.shutter_speed ? `
                                <div class="exif-item">
                                    <div class="exif-label">Shutter Speed</div>
                                    <div class="exif-value">${escapeHtml(image.exif.shutter_speed)}</div>
                                </div>
                            ` : ''}
                            ${image.exif.iso ? `
                                <div class="exif-item">
                                    <div class="exif-label">ISO</div>
                                    <div class="exif-value">${escapeHtml(image.exif.iso)}</div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// ===================================
// UTILITY FUNCTIONS
// ===================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
