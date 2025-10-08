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
    
    // Pure swipe - no navigation to initialize
    
    // Add touch event listeners to the gallery container
    const gallery = document.getElementById('mobileSwipeGallery');
    if (gallery) {
        gallery.addEventListener('touchstart', handleTouchStart, { passive: true });
        gallery.addEventListener('touchmove', handleTouchMove, { passive: false });
        gallery.addEventListener('touchend', handleTouchEnd, { passive: true });
    }
    
    // Pure swipe - no buttons needed
    
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
    
    // Image info is now always visible below gallery
}

// Touch Event Handlers
function handleTouchStart(e) {
    touchStartX = e.touches[0].clientX;
    touchEndX = touchStartX;
    isDragging = true;
    
    console.log('Touch start:', touchStartX);
}

function handleTouchMove(e) {
    if (!isDragging) return;
    
    touchEndX = e.touches[0].clientX;
    const diff = touchStartX - touchEndX;
    
    // Prevent default scrolling when swiping horizontally
    if (Math.abs(diff) > 10) {
        e.preventDefault();
    }
    
    console.log('Touch move:', touchEndX, 'diff:', diff);
}

function handleTouchEnd(e) {
    if (!isDragging) return;
    isDragging = false;
    
    const diff = touchStartX - touchEndX;
    const threshold = 30; // Reduced threshold for easier swiping
    
    console.log('Touch end - diff:', diff, 'threshold:', threshold);
    
    if (Math.abs(diff) > threshold) {
        if (diff > 0 && currentSwipeIndex < filteredImages.length - 1) {
            // Swipe left - next image
            console.log('Swiping to next image');
            currentSwipeIndex++;
            updateSwipePosition();
            
        } else if (diff < 0 && currentSwipeIndex > 0) {
            // Swipe right - previous image
            console.log('Swiping to previous image');
            currentSwipeIndex--;
            updateSwipePosition();
            
        }
    } else {
        console.log('Swipe distance too small:', Math.abs(diff));
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
            console.log('Nav made sticky');
        } 
        // When scrolled back to top, remove nav sticky
        else if (scrollTop < headerHeight && isNavSticky) {
            nav.classList.remove('sticky');
            main.classList.remove('nav-sticky');
            isNavSticky = false;
            console.log('Nav sticky removed');
        }
    }
    
    // Add scroll listener
    window.addEventListener('scroll', handleScroll);
    console.log('Sticky navigation initialized');
    
    // Handle window resize to recalculate heights
    window.addEventListener('resize', function() {
        headerHeight = header.offsetHeight;
    });
}
