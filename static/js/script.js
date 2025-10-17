let allImages = [];
let currentCategory = 'all';

// DOM elements
const imageGrid = document.getElementById('imageGrid');
const galleryTitle = document.getElementById('galleryTitle');
const imageCount = document.getElementById('imageCount');
const heroImage = document.getElementById('heroImage');
const modal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalTitle = document.getElementById('modalTitle');
const modalCategory = document.getElementById('modalCategory');
const closeModal = document.querySelector('.close');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadImages();
    setupEventListeners();
});

// Load images from API
async function loadImages() {
    try {
        const response = await fetch('/api/images');
        allImages = await response.json();
        
        if (allImages.length > 0) {
            // Set hero image (selected or random)
            setHeroImage();
            
            // Initialize pagination
            initPagination();
            
            // Display all images initially with pagination
            displayImagesWithPagination(allImages);
            updateImageCount(allImages.length);
        } else {
            imageGrid.innerHTML = '<div class="loading">No images found in /data directory</div>';
        }
    } catch (error) {
        console.error('Error loading images:', error);
        imageGrid.innerHTML = '<div class="loading">Error loading images</div>';
    }
}

// Set hero image (selected or random)
async function setHeroImage() {
    try {
        // First, try to get the selected hero image from API
        const response = await fetch('/api/hero-image');
        const heroData = await response.json();
        
        if (heroData.success && heroData.hero_image) {
            // Use the selected hero image
            const heroImageName = heroData.hero_image;
            const heroImagePath = `/images/${heroImageName}.jpg`;
            heroImage.src = heroImagePath;
            heroImage.alt = heroImageName;
            
            // Add click handler to open modal
            heroImage.onclick = () => openModal(heroImageName, getImageCategory(heroImageName));
        } else {
            // Fallback to random image if no hero image is set
            const randomImage = allImages[Math.floor(Math.random() * allImages.length)];
            const heroImagePath = `/images/${randomImage.name}.jpg`;
            heroImage.src = heroImagePath;
            heroImage.alt = randomImage.name;
            
            // Add click handler to open modal
            heroImage.onclick = () => openModal(randomImage.name, randomImage.category);
        }
    } catch (error) {
        console.error('Error setting hero image:', error);
        // Fallback to first image
        if (allImages.length > 0) {
            const firstImage = allImages[0];
            const heroImagePath = `/images/${firstImage.name}.jpg`;
            heroImage.src = heroImagePath;
            heroImage.alt = firstImage.name;
            
            // Add click handler to open modal
            heroImage.onclick = () => openModal(firstImage.name, firstImage.category);
        }
    }
}

// Get image category by name
function getImageCategory(imageName) {
    const image = allImages.find(img => img.name === imageName);
    return image ? image.category : 'Other';
}

// Pagination variables
let currentPage = 1;
let imagesPerPage = 12;
let totalPages = 1;

// Initialize pagination
function initPagination() {
    imagesPerPage = 12; // Default images per page
    currentPage = 1;
}

// Display images with pagination
function displayImagesWithPagination(images) {
    totalPages = Math.ceil(images.length / imagesPerPage);
    const startIndex = (currentPage - 1) * imagesPerPage;
    const endIndex = startIndex + imagesPerPage;
    const imagesToShow = images.slice(startIndex, endIndex);
    
    displayImages(imagesToShow);
    updatePaginationControls(images.length);
}

// Display images in grid
function displayImages(images) {
    if (images.length === 0) {
        imageGrid.innerHTML = '<div class="loading">No images found for this category</div>';
        return;
    }
    
    imageGrid.innerHTML = images.map(image => `
        <div class="image-item" onclick="openModal('${image.name}', '${image.category}')">
            <img src="/images/${image.name}.jpg" alt="${image.name}" loading="lazy">
            <div class="image-overlay">
                <div class="image-title">${image.name}</div>
                <div class="image-category">${image.category}</div>
            </div>
        </div>
    `).join('');
}

// Update pagination controls
function updatePaginationControls(totalImages) {
    const paginationContainer = document.getElementById('paginationControls');
    if (!paginationContainer) return;
    
    let paginationHTML = '';
    
    if (totalPages > 1) {
        paginationHTML = '<div class="pagination">';
        
        // Previous button
        if (currentPage > 1) {
            paginationHTML += `<button onclick="changePage(${currentPage - 1})" class="pagination-btn">Previous</button>`;
        }
        
        // Page numbers (show max 5 pages around current page)
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        if (startPage > 1) {
            paginationHTML += `<button onclick="changePage(1)" class="pagination-btn">1</button>`;
            if (startPage > 2) {
                paginationHTML += '<span class="pagination-ellipsis">...</span>';
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === currentPage ? 'active' : '';
            paginationHTML += `<button onclick="changePage(${i})" class="pagination-btn ${activeClass}">${i}</button>`;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += '<span class="pagination-ellipsis">...</span>';
            }
            paginationHTML += `<button onclick="changePage(${totalPages})" class="pagination-btn">${totalPages}</button>`;
        }
        
        // Next button
        if (currentPage < totalPages) {
            paginationHTML += `<button onclick="changePage(${currentPage + 1})" class="pagination-btn">Next</button>`;
        }
        
        paginationHTML += '</div>';
        
        // Add page info
        const startItem = (currentPage - 1) * imagesPerPage + 1;
        const endItem = Math.min(currentPage * imagesPerPage, totalImages);
        paginationHTML += `<div class="pagination-info">Showing ${startItem}-${endItem} of ${totalImages} images</div>`;
    }
    
    paginationContainer.innerHTML = paginationHTML;
}

// Change page
function changePage(page) {
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        const filteredImages = getFilteredImages();
        displayImagesWithPagination(filteredImages);
    }
}

// Get filtered images based on current category
function getFilteredImages() {
    if (currentCategory === 'all') {
        return allImages;
    }
    return allImages.filter(image => image.category === currentCategory);
}

// Filter images by category
function filterImages(category) {
    currentCategory = category;
    currentPage = 1; // Reset to first page when filtering
    
    const filteredImages = getFilteredImages();
    displayImagesWithPagination(filteredImages);
    updateImageCount(filteredImages.length);
    
    // Update gallery title
    if (category === 'all') {
        galleryTitle.textContent = 'All Images';
    } else {
        galleryTitle.textContent = category;
    }
    
    // Update active category button
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[onclick="filterImages('${category}')"]`).classList.add('active');
}

// Update image count display
function updateImageCount(count) {
    if (imageCount) {
        imageCount.textContent = `${count} image${count !== 1 ? 's' : ''}`;
    }
}

// Open modal
function openModal(imageName, category) {
    const imagePath = `/images/${imageName}.jpg`;
    modalImage.src = imagePath;
    modalTitle.textContent = imageName;
    modalCategory.textContent = category;
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

// Close modal
function closeModalFunc() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restore scrolling
}

// Setup event listeners
function setupEventListeners() {
    // Close modal when clicking the X
    if (closeModal) {
        closeModal.onclick = closeModalFunc;
    }
    
    // Close modal when clicking outside the image
    window.onclick = function(event) {
        if (event.target === modal) {
            closeModalFunc();
        }
    }
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeModalFunc();
        }
    });
}

// Search functionality
function searchImages() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    
    if (searchTerm === '') {
        // If search is empty, show all images for current category
        const filteredImages = getFilteredImages();
        displayImagesWithPagination(filteredImages);
        updateImageCount(filteredImages.length);
        return;
    }
    
    // Filter images based on search term
    const baseImages = getFilteredImages();
    const searchResults = baseImages.filter(image => 
        image.name.toLowerCase().includes(searchTerm) ||
        image.category.toLowerCase().includes(searchTerm)
    );
    
    currentPage = 1; // Reset to first page
    displayImagesWithPagination(searchResults);
    updateImageCount(searchResults.length);
}

// Clear search
function clearSearch() {
    document.getElementById('searchInput').value = '';
    searchImages();
}

// Handle Enter key in search
function handleSearchKeyPress(event) {
    if (event.key === 'Enter') {
        searchImages();
    }
}

// Mobile menu toggle
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    const hamburger = document.querySelector('.hamburger');
    
    mobileMenu.classList.toggle('active');
    hamburger.classList.toggle('active');
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const mobileMenu = document.getElementById('mobileMenu');
    const hamburger = document.querySelector('.hamburger');
    
    if (mobileMenu && mobileMenu.classList.contains('active')) {
        if (!mobileMenu.contains(event.target) && !hamburger.contains(event.target)) {
            mobileMenu.classList.remove('active');
            hamburger.classList.remove('active');
        }
    }
});

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Initialize category buttons
function initializeCategoryButtons() {
    // Get unique categories from all images
    const categories = ['all', ...new Set(allImages.map(img => img.category))];
    
    const categoryContainer = document.getElementById('categoryButtons');
    if (categoryContainer) {
        categoryContainer.innerHTML = categories.map(category => {
            const displayName = category === 'all' ? 'All Images' : category;
            const activeClass = category === 'all' ? 'active' : '';
            return `<button class="category-btn ${activeClass}" onclick="filterImages('${category}')">${displayName}</button>`;
        }).join('');
    }
}

// Call this after images are loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait for images to load, then initialize category buttons
    setTimeout(() => {
        if (allImages.length > 0) {
            initializeCategoryButtons();
        }
    }, 1000);
});

// Lazy loading intersection observer
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.remove('lazy');
            observer.unobserve(img);
        }
    });
});

// Apply lazy loading to images
function applyLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    lazyImages.forEach(img => {
        imageObserver.observe(img);
    });
}

// Order Print Functions

// Original order print function (kept for compatibility)
function orderPrint(imageName) {
    if (imageName) {
        window.open('/test_order_form?image=' + encodeURIComponent(imageName), '_blank');
    } else {
        window.open('/test_order_form', '_blank');
    }
}

// New Order System Function - Bypasses all old Lumaprints code
function openNewOrderForm() {
    const modalTitle = document.getElementById('modalTitle');
    const modalImage = document.getElementById('modalImage');
    
    if (modalTitle && modalTitle.textContent && modalImage) {
        const imageName = encodeURIComponent(modalTitle.textContent.trim());
        
        // Get image dimensions by creating a temporary image
        const tempImg = new Image();
        tempImg.onload = function() {
            const width = this.naturalWidth;
            const height = this.naturalHeight;
            const dpi = Math.round(Math.sqrt((width * height) / (12 * 12))); // Estimate DPI for 12x12 print
            
            const imageSize = encodeURIComponent(`${width}x${height} pixels, DPI: ${dpi}`);
            const orderFormUrl = `/test_order_form?image=${imageName}&imageSize=${imageSize}`;
            window.open(orderFormUrl, '_blank');
        };
        tempImg.onerror = function() {
            // If image fails to load, still open form but without size info
            const orderFormUrl = '/test_order_form?image=' + imageName;
            window.open(orderFormUrl, '_blank');
        };
        tempImg.src = modalImage.src;
    } else {
        window.open('/test_order_form', '_blank');
    }
}
