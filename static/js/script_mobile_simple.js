// Simplified Mobile Gallery - No Complex Lazy Loading
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

// Mobile Gallery Initialization - Use Template Data
function initMobileGallery() {
    console.log('Loading mobile gallery...');
    
    // Use images data passed from Flask template (same as desktop)
    if (typeof window.imagesData !== 'undefined' && window.imagesData.length > 0) {
        allImages = window.imagesData;
        filteredImages = allImages;
        initSimpleSwipeGallery(allImages);
        updateMobileImageCount(allImages.length);
    } else {
        console.error('No images data found in template');
        const wrapper = document.getElementById('mobileSwipeWrapper');
        if (wrapper) {
            wrapper.innerHTML = '<div class="error">No images found</div>';
        }
    }
}

// Simple Swipe Gallery - Load All Images Immediately
function initSimpleSwipeGallery(images) {
    filteredImages = images;
    currentSwipeIndex = 0;
    
    const wrapper = document.getElementById('mobileSwipeWrapper');
    if (!wrapper) {
        console.error('Mobile swipe wrapper not found');
        return;
    }
    
    console.log('Creating gallery with', images.length, 'images');
    
    // Create slides with actual images (no lazy loading)
    wrapper.innerHTML = images.map((image, index) => `
        <div class="swipe-slide" data-index="${index}">
            <img src="${image.url}" alt="${image.title}" loading="eager" />
        </div>
    `).join('');
    
    // Add touch event listeners to the gallery container
    const gallery = document.getElementById('mobileSwipeGallery');
    if (gallery) {
        gallery.addEventListener('touchstart', handleTouchStart, { passive: true });
        gallery.addEventListener('touchmove', handleTouchMove, { passive: false });
        gallery.addEventListener('touchend', handleTouchEnd, { passive: true });
    }
    
    // Update order button
    updateOrderButton();
}

// Touch Event Handlers
function handleTouchStart(e) {
    touchStartX = e.touches[0].clientX;
    touchEndX = touchStartX;
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
    const threshold = 30;
    
    if (Math.abs(diff) > threshold) {
        if (diff > 0) {
            // Swipe left - next image (with carousel wrap)
            currentSwipeIndex = (currentSwipeIndex + 1) % filteredImages.length;
            updateSwipePosition();
        } else if (diff < 0) {
            // Swipe right - previous image (with carousel wrap)
            currentSwipeIndex = currentSwipeIndex === 0 ? filteredImages.length - 1 : currentSwipeIndex - 1;
            updateSwipePosition();
        }
        updateOrderButton();
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

// Update order button with correct route
function updateOrderButton() {
    const orderBtn = document.getElementById('mobileOrderBtn');
    if (orderBtn && filteredImages.length > 0) {
        const currentImage = filteredImages[currentSwipeIndex];
        if (currentImage) {
            // Update button to use correct route format
            orderBtn.onclick = () => {
                window.location.href = `/order-print/${currentImage.filename}`;
            };
        }
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
    initSimpleSwipeGallery(filtered);
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
        countElement.textContent = `Swipe through ${count} images`;
    }
}

// Mobile Hero - Load from admin settings
function initMobileHero() {
    loadMobileHeroImage();
}

async function loadMobileHeroImage() {
    try {
        console.log('Loading hero image...');
        const response = await fetch('/api/hero_image');
        const heroData = await response.json();
        
        const heroElement = document.getElementById('mobileHero');
        if (heroData.filename && heroElement) {
            const imageUrl = `/images/${heroData.filename}`;
            heroElement.style.backgroundImage = `url('${imageUrl}')`;
            console.log('Mobile hero image loaded:', heroData.filename);
        } else {
            console.log('No hero image set in admin - no fallback');
            // NO FALLBACK - only show what admin designates
        }
    } catch (error) {
        console.error('Error loading mobile hero image:', error);
        // NO FALLBACK - only show what admin designates
    }
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
    const main = document.querySelector('.mobile-main');
    
    if (!header || !nav || !main) {
        console.log('Sticky nav elements not found');
        return;
    }
    
    let headerHeight = header.offsetHeight;
    let isNavSticky = false;
    
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
            isNavSticky = false;
        }
    }
    
    // Add scroll listener
    window.addEventListener('scroll', handleScroll);
    
    // Handle window resize to recalculate heights
    window.addEventListener('resize', function() {
        headerHeight = header.offsetHeight;
    });
}
