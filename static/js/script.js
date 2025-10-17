// Global variables
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
        const heroResponse = await fetch('/api/hero_image');
        const heroData = await heroResponse.json();
        
        if (heroData.filename) {
            // Use the selected hero image
            heroImage.style.backgroundImage = `url('/images/${heroData.filename}')`;
        } else {
            // Fallback to random hero image
            setRandomHeroImage();
        }
    } catch (error) {
        console.error('Error loading hero image selection:', error);
        // Fallback to random hero image
        setRandomHeroImage();
    }
}

// Set random hero image (fallback)
function setRandomHeroImage() {
    if (allImages.length > 0) {
        const randomImage = allImages[Math.floor(Math.random() * allImages.length)];
        heroImage.style.backgroundImage = `url('${randomImage.url}')`;
    }
}

// Pagination variables
let currentPage = 1;
let imagesPerPage = 18;
let totalPages = 1;
let currentImages = [];

// Display images in masonry grid (for current page)
function displayImages(images) {
    if (images.length === 0) {
        imageGrid.innerHTML = '<div class="loading">No images found for this category</div>';
        return;
    }

    // Size classes for varied masonry layout
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
    
    const grid = document.getElementById('imageGrid');
    
    // Add slide-out animation
    grid.classList.add('sliding-out');
    
    setTimeout(() => {
        currentPage = newPage;
        displayCurrentPage();
        updatePaginationControls();
        
        // Add slide-in animation
        grid.classList.remove('sliding-out');
        grid.classList.add('sliding-in');
        
        setTimeout(() => {
            grid.classList.remove('sliding-in');
        }, 50);
    }, 300);
}

// Update pagination controls
function updatePaginationControls() {
    const paginationInfo = document.getElementById('paginationInfo');
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    const pageNumbers = document.getElementById('pageNumbers');
    
    // Update info
    if (paginationInfo) {
        paginationInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    }
    
    // Update buttons
    if (prevBtn) {
        prevBtn.disabled = currentPage === 1;
    }
    
    if (nextBtn) {
        nextBtn.disabled = currentPage === totalPages;
    }
    
    // Update page numbers
    if (pageNumbers) {
        pageNumbers.innerHTML = '';
        
        // Show max 5 page numbers
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);
        
        if (endPage - startPage < 4) {
            startPage = Math.max(1, endPage - 4);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `page-number ${i === currentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.addEventListener('click', () => changePage(i));
            pageNumbers.appendChild(pageBtn);
        }
    }
}

// Initialize pagination
function initPagination() {
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => changePage(currentPage - 1));
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => changePage(currentPage + 1));
    }
}

// Filter images by category
function filterImages(category) {
    const galleryTitle = document.getElementById('galleryTitle');
    let filteredImages;
    
    if (category === 'all') {
        filteredImages = allImages;
        galleryTitle.textContent = 'Portfolio Gallery';
    } else {
        // Filter images by exact category match
        filteredImages = allImages.filter(image => image.category === category);
        galleryTitle.textContent = `${category.charAt(0).toUpperCase() + category.slice(1)} Gallery`;
    }
    
    // Update current category
    currentCategory = category;
    
    // Display filtered images with pagination
    displayImagesWithPagination(filteredImages);
    updateImageCount(filteredImages.length);
}

// Update image count display
function updateImageCount(count) {
    imageCount.textContent = `${count} image${count !== 1 ? 's' : ''}`;
}

// Setup event listeners
function setupEventListeners() {
    // Navigation links for sections
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            // Skip cart link - let it navigate normally
            if (this.classList.contains('cart-link')) {
                return; // Don't prevent default, let the link navigate to /checkout
            }
            
            e.preventDefault();
            
            const section = this.getAttribute('data-section');
            
            // Update active nav link
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding section
            showSection(section);
        });
    });
    
    // Modal close events
    if (closeModal) {
        closeModal.addEventListener('click', closeImageModal);
    }
    
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeImageModal();
        }
    });
}

// Show specific section
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
}

// Open image modal
function openModal(imageUrl, title, category) {
    modalImage.src = imageUrl;
    modalTitle.textContent = title;
    modalCategory.innerHTML = '<span class="brand-main">FIFTH ELEMENT</span><br><span class="brand-sub">PHOTOGRAPHY</span>';
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

// Close modal
function closeImageModal() {
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
}


// Featured Image Action Functions
function viewFullscreen(imageUrl, imageTitle) {
    // Open image in new window/tab - original behavior
    window.open(imageUrl, '_blank');
}

function downloadImage(imageUrl, filename) {
    // Create a temporary link element
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = filename || 'featured-image.jpg';
    
    // Append to body, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function shareOnSocial(imageTitle, imageUrl) {
    const shareUrl = 'https://fifth-element-photography-production.up.railway.app/#featured';
    const shareText = `Check out this amazing photograph: "${imageTitle}" by Fifth Element Photography`;
    
    // Check if Web Share API is supported
    if (navigator.share) {
        navigator.share({
            title: 'Fifth Element Photography - Featured Image',
            text: shareText,
            url: shareUrl
        }).catch(console.error);
    } else {
        // Fallback: Copy link to clipboard and show options
        navigator.clipboard.writeText(shareUrl).then(() => {
            const shareOptions = `
                <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                           background: #1a1a1a; padding: 2rem; border-radius: 8px; z-index: 1000;
                           border: 1px solid #333; color: white; font-family: Poppins, sans-serif;">
                    <h3 style="margin-top: 0;">Share Featured Image</h3>
                    <p>Link copied to clipboard!</p>
                    <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                        <a href="https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}" 
                           target="_blank" style="color: #1da1f2; text-decoration: none;">Twitter</a>
                        <a href="https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}" 
                           target="_blank" style="color: #4267b2; text-decoration: none;">Facebook</a>
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}" 
                           target="_blank" style="color: #0077b5; text-decoration: none;">LinkedIn</a>
                    </div>
                    <button onclick="this.parentElement.remove()" 
                            style="margin-top: 1rem; background: #333; color: white; border: none; 
                                   padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer;">Close</button>
                </div>
                <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                           background: rgba(0,0,0,0.5); z-index: 999;" onclick="this.nextElementSibling.remove(); this.remove();"></div>
            `;
            document.body.insertAdjacentHTML('beforeend', shareOptions);
        }).catch(() => {
            alert('Unable to copy link. Please manually copy: ' + shareUrl);
        });
    }
}



// Mobile Navigation
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.getElementById('sidebar');
    const mobileOverlay = document.getElementById('mobileOverlay');
    const navLinks = document.querySelectorAll('.nav-link');

    // Toggle mobile menu
    function toggleMobileMenu() {
        mobileMenuBtn.classList.toggle('active');
        sidebar.classList.toggle('active');
        mobileOverlay.classList.toggle('active');
        document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
    }

    // Close mobile menu
    function closeMobileMenu() {
        mobileMenuBtn.classList.remove('active');
        sidebar.classList.remove('active');
        mobileOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Event listeners
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    }

    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', closeMobileMenu);
    }

    // Close menu when nav link is clicked
    navLinks.forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });

    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMobileMenu();
        }
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });
});


// Category Filtering
document.addEventListener('DOMContentLoaded', function() {
    const categoryLinks = document.querySelectorAll('.category-link');
    
    // Add click event listeners to category links
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default link behavior
            const category = this.getAttribute('data-category');
            
            // Update active link
            categoryLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Filter images using the correct function
            filterImages(category);
        });
    });
});



// Desktop Contact Form
function initDesktopContactForm() {
    const desktopContactForm = document.querySelector('#contact-section form');
    if (desktopContactForm) {
        desktopContactForm.addEventListener('submit', handleDesktopContactSubmit);
    }
}

async function handleDesktopContactSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('.btn-primary');
    const originalText = submitBtn.textContent;
    
    // Get form data
    const formData = {
        name: form.querySelector('input[placeholder="Your Name"]').value,
        email: form.querySelector('input[placeholder="Your Email"]').value,
        phone: form.querySelector('input[placeholder="Your Phone Number"]').value,
        shoot_type: form.querySelector('#shoot-type').value,
        budget: form.querySelector('#budget').value,
        how_heard: form.querySelector('#how-heard').value,
        message: form.querySelector('textarea').value
    };
    
    // Validate required fields
    if (!formData.name || !formData.email || !formData.message) {
        alert('Please fill in all required fields (Name, Email, and Message).');
        return;
    }
    
    // Show loading state
    submitBtn.textContent = 'Sending...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            form.reset();
        } else {
            alert(result.error || 'Failed to send message. Please try again.');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        alert('An error occurred. Please try again later.');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Initialize contact form when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initDesktopContactForm();
});



// Initialize Lumaprints functionality
let lumaprintsPricing = null;
let lumaprintsOrdering = null;

// Initialize Lumaprints when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Handle Order Print button clicks - redirect to new PayPal form
    document.addEventListener('click', function(e) {
        if (e.target.closest('#orderPrintBtn')) {
            e.preventDefault();
            
            // Redirect to new PayPal-integrated order form
            window.open('/test_order_form', '_blank');
        }
    });
});
// Desktop Order Form Function
function openDesktopOrderForm() {
    const modalTitle = document.getElementById('modalTitle');
    if (modalTitle && modalTitle.textContent) {
        const imageName = encodeURIComponent(modalTitle.textContent.trim());
        const orderFormUrl = '/test_order_form?image=' + imageName;
        window.open(orderFormUrl, '_blank');
    } else {
        window.open('/test_order_form', '_blank');
    }
}

// New Order System Function - Bypasses all old Lumaprints code
function openNewOrderForm() {
    const modalTitle = document.getElementById('modalTitle');
    if (modalTitle && modalTitle.textContent) {
        const imageName = encodeURIComponent(modalTitle.textContent.trim());
        const orderFormUrl = '/test_order_form?image=' + imageName;
        window.open(orderFormUrl, '_blank');
    } else {
        window.open('/test_order_form', '_blank');
    }
}
