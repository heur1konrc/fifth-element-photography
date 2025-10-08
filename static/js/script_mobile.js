// Mobile Gallery Variables
let allImages = [];
let currentFilter = 'all';
let currentSwipeIndex = 0;
let filteredImages = [];
let touchStartX = 0;
let touchEndX = 0;
let isDragging = false;

// Initialize mobile functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Mobile script loaded');
    initMobileNavigation();
    initMobileGallery();
    initMobileFilters();
    initMobileHero();
    initMobileContactForm();
    initStickyNavigation();
});

// Mobile Navigation
function initMobileNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const contactLink = document.querySelector('.contact-link');
    const sections = document.querySelectorAll('.content-section');
    
    navBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetSection = this.getAttribute('data-section');
            
            // Update active nav button
            navBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Show target section
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === targetSection + '-section') {
                    section.classList.add('active');
                }
            });
            
            // Scroll to top
            window.scrollTo(0, 0);
        });
    });
    
    // Handle contact link
    if (contactLink) {
        contactLink.addEventListener('click', function(e) {
            e.preventDefault();
            const targetSection = this.getAttribute('data-section');
            
            // Remove active from nav buttons
            navBtns.forEach(b => b.classList.remove('active'));
            
            // Show contact section
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === targetSection + '-section') {
                    section.classList.add('active');
                }
            });
            
            // Scroll to top
            window.scrollTo(0, 0);
        });
    }
}

// Mobile Gallery Initialization
function initMobileGallery() {
    // Load and display images
    fetch('/api/images')
        .then(response => response.json())
        .then(data => {
            // API returns images array directly, not wrapped in data.images
            allImages = Array.isArray(data) ? data : data.images || [];
            filteredImages = allImages;
            initMobileSwipeGallery(allImages);
            updateMobileImageCount(allImages.length);
        })
        .catch(error => {
            console.error('Error loading images:', error);
            document.getElementById('mobileSwipeWrapper').innerHTML = '<div class="error">Failed to load images</div>';
        });
}

// Mobile Swipe Gallery
function initMobileSwipeGallery(images) {
    filteredImages = images;
    currentSwipeIndex = 0;
    
    const wrapper = document.getElementById('mobileSwipeWrapper');
    const prevBtn = document.getElementById('mobilePrevBtn');
    const nextBtn = document.getElementById('mobileNextBtn');
    const indicator = document.getElementById('mobileSwipeIndicator');
    const imageInfo = document.getElementById('mobileImageInfo');
    
    if (!wrapper) return;
    
    // Create swipe slides
    wrapper.innerHTML = images.map((image, index) => `
        <div class="swipe-slide" data-index="${index}">
            <img src="${image.url}" alt="${image.title}" loading="lazy">
        </div>
    `).join('');
    
    // Initialize navigation
    updateSwipeNavigation();
    updateImageInfo();
    
    // Add touch event listeners
    wrapper.addEventListener('touchstart', handleTouchStart, { passive: true });
    wrapper.addEventListener('touchmove', handleTouchMove, { passive: false });
    wrapper.addEventListener('touchend', handleTouchEnd, { passive: true });
    
    // Add button event listeners
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentSwipeIndex > 0) {
                currentSwipeIndex--;
                updateSwipePosition();
                updateSwipeNavigation();
                updateImageInfo();
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentSwipeIndex < filteredImages.length - 1) {
                currentSwipeIndex++;
                updateSwipePosition();
                updateSwipeNavigation();
                updateImageInfo();
            }
        });
    }
    
    // Add order button functionality
    const orderBtn = document.getElementById('mobileOrderBtn');
    if (orderBtn) {
        orderBtn.addEventListener('click', () => {
            const currentImage = filteredImages[currentSwipeIndex];
            if (currentImage) {
                // Redirect to order print page
                window.location.href = `/order_print?image=${encodeURIComponent(currentImage.filename)}`;
            }
        });
    }
    
    // Show image info after a delay
    setTimeout(() => {
        if (imageInfo) {
            imageInfo.classList.add('show');
        }
    }, 500);
}

// Touch Event Handlers
function handleTouchStart(e) {
    touchStartX = e.touches[0].clientX;
    isDragging = true;
}

function handleTouchMove(e) {
    if (!isDragging) return;
    
    touchEndX = e.touches[0].clientX;
    const diff = touchStartX - touchEndX;
    
    // Prevent default scrolling when swiping horizontally
    if (Math.abs(diff) > 10) {
        e.preventDefault();
    }
}

function handleTouchEnd(e) {
    if (!isDragging) return;
    isDragging = false;
    
    const diff = touchStartX - touchEndX;
    const threshold = 50; // Minimum swipe distance
    
    if (Math.abs(diff) > threshold) {
        if (diff > 0 && currentSwipeIndex < filteredImages.length - 1) {
            // Swipe left - next image
            currentSwipeIndex++;
            updateSwipePosition();
            updateSwipeNavigation();
            updateImageInfo();
        } else if (diff < 0 && currentSwipeIndex > 0) {
            // Swipe right - previous image
            currentSwipeIndex--;
            updateSwipePosition();
            updateSwipeNavigation();
            updateImageInfo();
        }
    }
}

// Update swipe position
function updateSwipePosition() {
    const wrapper = document.getElementById('mobileSwipeWrapper');
    if (wrapper) {
        const translateX = -currentSwipeIndex * 100;
        wrapper.style.transform = `translateX(${translateX}%)`;
    }
}

// Update navigation controls
function updateSwipeNavigation() {
    const prevBtn = document.getElementById('mobilePrevBtn');
    const nextBtn = document.getElementById('mobileNextBtn');
    const indicator = document.getElementById('mobileSwipeIndicator');
    
    if (prevBtn) {
        prevBtn.disabled = currentSwipeIndex === 0;
    }
    
    if (nextBtn) {
        nextBtn.disabled = currentSwipeIndex === filteredImages.length - 1;
    }
    
    if (indicator) {
        indicator.textContent = `${currentSwipeIndex + 1} / ${filteredImages.length}`;
    }
}

// Update image info
function updateImageInfo() {
    const currentImage = filteredImages[currentSwipeIndex];
    if (!currentImage) return;
    
    const title = document.getElementById('mobileImageTitle');
    const category = document.getElementById('mobileImageCategory');
    
    if (title) {
        title.textContent = currentImage.title;
    }
    
    if (category) {
        category.textContent = currentImage.category.toUpperCase();
    }
}

// Mobile Filters
function initMobileFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            
            // Update active filter button
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Filter images
            filterMobileImages(category);
            currentFilter = category;
        });
    });
}

function filterMobileImages(category) {
    let filtered;
    
    if (category === 'all') {
        filtered = allImages;
    } else {
        filtered = allImages.filter(image => 
            image.category.toLowerCase() === category.toLowerCase()
        );
    }
    
    // Reinitialize swipe gallery with filtered images
    initMobileSwipeGallery(filtered);
    updateMobileImageCount(filtered.length);
    
    // Scroll to gallery
    const gallery = document.getElementById('mobileSwipeGallery');
    if (gallery) {
        gallery.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function updateMobileImageCount(count) {
    const countElement = document.getElementById('mobileImageCount');
    if (countElement) {
        countElement.textContent = `${count} images`;
    }
}

// Mobile Hero Image
function initMobileHero() {
    // Hero image functionality if needed
}

// Mobile Contact Form
function initMobileContactForm() {
    const form = document.getElementById('mobileContactForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        // Show loading state
        submitBtn.textContent = 'Sending...';
        submitBtn.disabled = true;
        
        try {
            const formData = {
                name: form.name.value,
                email: form.email.value,
                message: form.message.value
            };
            
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
    });
}

// Handle orientation change
window.addEventListener('orientationchange', function() {
    setTimeout(() => {
        // Recalculate layout after orientation change
        if (filteredImages.length > 0) {
            updateSwipePosition();
        }
    }, 100);
});

// Sticky Navigation
function initStickyNavigation() {
    const header = document.querySelector('.mobile-header');
    const nav = document.querySelector('.mobile-nav');
    const filters = document.querySelector('.mobile-filters');
    const main = document.querySelector('.mobile-main');
    
    if (!header || !nav || !filters || !main) return;
    
    let headerHeight = header.offsetHeight;
    let navHeight = nav.offsetHeight;
    let filtersHeight = filters.offsetHeight;
    let isNavSticky = false;
    let isFiltersSticky = false;
    
    function handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // When scrolled past the header height, make nav sticky
        if (scrollTop >= headerHeight && !isNavSticky) {
            nav.classList.add('sticky');
            main.classList.add('nav-sticky');
            isNavSticky = true;
        } 
        // When scrolled back to top, remove nav sticky
        else if (scrollTop < headerHeight && isNavSticky) {
            nav.classList.remove('sticky');
            main.classList.remove('nav-sticky');
            main.classList.remove('filters-sticky');
            filters.classList.remove('sticky');
            isNavSticky = false;
            isFiltersSticky = false;
        }
        
        // When scrolled past nav + filters, make filters sticky too
        const navFiltersHeight = headerHeight + navHeight + filtersHeight;
        if (scrollTop >= navFiltersHeight && isNavSticky && !isFiltersSticky) {
            filters.classList.add('sticky');
            main.classList.remove('nav-sticky');
            main.classList.add('filters-sticky');
            isFiltersSticky = true;
        }
        // When scrolled back above filters threshold, remove filters sticky
        else if (scrollTop < navFiltersHeight && isFiltersSticky) {
            filters.classList.remove('sticky');
            main.classList.remove('filters-sticky');
            main.classList.add('nav-sticky');
            isFiltersSticky = false;
        }
    }
    
    // Throttle scroll events for better performance
    let ticking = false;
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(handleScroll);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick);
    
    // Handle window resize to recalculate heights
    window.addEventListener('resize', function() {
        headerHeight = header.offsetHeight;
        navHeight = nav.offsetHeight;
        filtersHeight = filters.offsetHeight;
    });
}
