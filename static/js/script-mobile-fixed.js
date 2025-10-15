// Get DOM elements
const imageGrid = document.getElementById('imageGrid');
const categoryFilters = document.querySelectorAll('.category-filter');
const modal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalTitle = document.getElementById('modalTitle');
const modalCategory = document.getElementById('modalCategory');
const closeModal = document.querySelector('.close');
const prevBtn = document.querySelector('.prev');
const nextBtn = document.querySelector('.next');

// Global variables
let allImages = [];
let filteredImages = [];
let currentImageIndex = 0;
let currentCategory = 'all';
let currentPage = 1;
let imagesPerPage = 18;
let totalPages = 1;
let currentImages = [];

// Display images with mobile detection
function displayImages(images) {
    if (images.length === 0) {
        imageGrid.innerHTML = '<div class="loading">No images found for this category</div>';
        return;
    }

    // Check if mobile device
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Simple mobile layout - no size classes, uniform grid
        const imageHTML = images.map(image => {
            return `
                <div class="image-item mobile-item" onclick="openModal('${image.url}', '${image.title}', '${image.category}')">
                    <img src="${image.url}" alt="${image.title}" loading="lazy">
                    <div class="image-overlay">
                        <div class="image-title">${image.title}</div>
                        <div class="image-category">${image.category.toUpperCase()}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        imageGrid.innerHTML = imageHTML;
        imageGrid.classList.add('mobile-grid');
    } else {
        // Desktop masonry layout
        const sizeClasses = ['size-small', 'size-medium', 'size-large', 'size-wide'];
        const sizeWeights = [0.3, 0.4, 0.2, 0.1]; // Probability weights for each size
        
        function getRandomSize() {
            const random = Math.random();
            let cumulative = 0;
            for (let i = 0; i < sizeWeights.length; i++) {
                cumulative += sizeWeights[i];
                if (random < cumulative) {
                    return sizeClasses[i];
                }
            }
            return sizeClasses[0]; // fallback
        }

        const imageHTML = images.map(image => {
            const sizeClass = getRandomSize();
            return `
                <div class="image-item ${sizeClass}" onclick="openModal('${image.url}', '${image.title}', '${image.category}')">
                    <img src="${image.url}" alt="${image.title}" loading="lazy">
                    <div class="image-overlay">
                        <div class="image-title">${image.title}</div>
                        <div class="image-category">${image.category.toUpperCase()}</div>
                    </div>
                </div>
            `;
        }).join('');

        imageGrid.innerHTML = imageHTML;
        imageGrid.classList.remove('mobile-grid');
    }
}

// Display images with pagination
function displayImagesWithPagination(images) {
    currentImages = images;
    totalPages = Math.ceil(images.length / imagesPerPage);
    currentPage = 1;
    
    if (totalPages <= 1) {
        document.getElementById('paginationContainer').style.display = 'none';
    } else {
        document.getElementById('paginationContainer').style.display = 'block';
    }
    
    displayCurrentPage();
    updatePaginationControls();
}

// Display current page of images
function displayCurrentPage() {
    const startIndex = (currentPage - 1) * imagesPerPage;
    const endIndex = startIndex + imagesPerPage;
    const pageImages = currentImages.slice(startIndex, endIndex);
    
    displayImages(pageImages);
}

// Change page with slide animation
function changePage(newPage) {
    if (newPage < 1 || newPage > totalPages || newPage === currentPage) {
        return;
    }
    
    currentPage = newPage;
    
    // Add slide-out animation
    imageGrid.style.opacity = '0';
    imageGrid.style.transform = 'translateX(-20px)';
    
    setTimeout(() => {
        displayCurrentPage();
        updatePaginationControls();
        
        // Add slide-in animation
        imageGrid.style.opacity = '1';
        imageGrid.style.transform = 'translateX(0)';
    }, 200);
}

// Update pagination controls
function updatePaginationControls() {
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');
    const pageInfo = document.getElementById('pageInfo');
    
    if (prevButton) prevButton.disabled = currentPage === 1;
    if (nextButton) nextButton.disabled = currentPage === totalPages;
    if (pageInfo) pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
}

// Filter images by category
function filterImages(category) {
    currentCategory = category;
    
    // Update active filter
    categoryFilters.forEach(filter => {
        filter.classList.remove('active');
        if (filter.dataset.category === category) {
            filter.classList.add('active');
        }
    });
    
    // Filter images
    if (category === 'all') {
        filteredImages = [...allImages];
    } else {
        filteredImages = allImages.filter(image => 
            image.category.toLowerCase() === category.toLowerCase()
        );
    }
    
    // Update image count
    updateImageCount(filteredImages.length);
    
    // Display filtered images with pagination
    displayImagesWithPagination(filteredImages);
}

// Update image count display
function updateImageCount(count) {
    const imageCountElement = document.querySelector('.image-count');
    if (imageCountElement) {
        imageCountElement.textContent = `${count} images`;
    }
}

// Open modal
function openModal(imageUrl, title, category) {
    modal.style.display = 'block';
    modalImage.src = imageUrl;
    modalTitle.textContent = title;
    modalCategory.textContent = category.toUpperCase();
    
    // Find current image index in filtered images
    currentImageIndex = filteredImages.findIndex(img => img.url === imageUrl);
    
    // Update navigation buttons
    updateModalNavigation();
    
    // Prevent body scrolling
    document.body.style.overflow = 'hidden';
}

// Close modal
function closeImageModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Navigate to previous image
function previousImage() {
    if (currentImageIndex > 0) {
        currentImageIndex--;
        const image = filteredImages[currentImageIndex];
        modalImage.src = image.url;
        modalTitle.textContent = image.title;
        modalCategory.textContent = image.category.toUpperCase();
        updateModalNavigation();
    }
}

// Navigate to next image
function nextImage() {
    if (currentImageIndex < filteredImages.length - 1) {
        currentImageIndex++;
        const image = filteredImages[currentImageIndex];
        modalImage.src = image.url;
        modalTitle.textContent = image.title;
        modalCategory.textContent = image.category.toUpperCase();
        updateModalNavigation();
    }
}

// Update modal navigation buttons
function updateModalNavigation() {
    prevBtn.style.display = currentImageIndex > 0 ? 'block' : 'none';
    nextBtn.style.display = currentImageIndex < filteredImages.length - 1 ? 'block' : 'none';
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    if (modal.style.display === 'block') {
        if (e.key === 'Escape') {
            closeImageModal();
        } else if (e.key === 'ArrowLeft') {
            previousImage();
        } else if (e.key === 'ArrowRight') {
            nextImage();
        }
    }
});

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Category filter listeners
    categoryFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            const category = this.dataset.category;
            filterImages(category);
        });
    });
    
    // Modal listeners
    if (closeModal) {
        closeModal.addEventListener('click', closeImageModal);
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', previousImage);
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', nextImage);
    }
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeImageModal();
        }
    });
    
    // Pagination listeners
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => changePage(currentPage - 1));
    }
    
    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => changePage(currentPage + 1));
    }
    
    // Load images
    loadImages();
    
    // Handle window resize for mobile detection
    window.addEventListener('resize', function() {
        // Redisplay current images when window is resized
        if (currentImages.length > 0) {
            displayCurrentPage();
        }
    });
});

// Load images from server
async function loadImages() {
    try {
        const response = await fetch('/api/images');
        const data = await response.json();
        
        allImages = data.images || [];
        filteredImages = [...allImages];
        
        // Update image count
        updateImageCount(allImages.length);
        
        // Display all images initially with pagination
        displayImagesWithPagination(allImages);
        
    } catch (error) {
        console.error('Error loading images:', error);
        imageGrid.innerHTML = '<div class="loading">Error loading images</div>';
    }
}

// Cart functionality
function updateCartCount() {
    const cartItems = JSON.parse(localStorage.getItem('cartItems') || '[]');
    const cartCount = cartItems.reduce((total, item) => total + item.quantity, 0);
    
    // Update all cart count elements
    const cartCountElements = document.querySelectorAll('.cart-count, #cartCount');
    cartCountElements.forEach(element => {
        element.textContent = cartCount;
        element.style.display = cartCount > 0 ? 'inline' : 'none';
    });
}

// Update cart count on page load and when localStorage changes
document.addEventListener('DOMContentLoaded', updateCartCount);
window.addEventListener('storage', updateCartCount);

// Update cart count periodically in case of same-page updates
setInterval(updateCartCount, 1000);

// Handle order print click
function handleOrderClick() {
    // Redirect to new PayPal-integrated order form
    window.open('/test_order_form', '_blank');
}
