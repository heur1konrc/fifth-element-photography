// Mobile Navigation and Section Switching
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing mobile navigation...');
    initMobileNavigation();
    initSectionSwitching();
    initActionButtons();
    initCategoriesCarousel();
    initMobileContactForm();
});

// Mobile Navigation Toggle
function initMobileNavigation() {
    console.log('Initializing mobile navigation...');
    const menuBtn = document.getElementById('mobileMenuBtn');
    const mobileNav = document.getElementById('mobileNav');
    
    console.log('Menu button:', menuBtn);
    console.log('Mobile nav:', mobileNav);
    
    if (menuBtn && mobileNav) {
        menuBtn.addEventListener('click', function() {
            console.log('Menu button clicked');
            mobileNav.classList.toggle('active');
        });
        console.log('Menu event listener attached');
    } else {
        console.error('Menu elements not found');
    }
}

// Section Switching
function initSectionSwitching() {
    console.log('Initializing section switching...');
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.mobile-section');
    const mobileNav = document.getElementById('mobileNav');
    const menuBtn = document.getElementById('mobileMenuBtn');
    
    console.log('Nav links found:', navLinks.length);
    console.log('Sections found:', sections.length);
    
    navLinks.forEach((link, index) => {
        link.addEventListener('click', function(e) {
            console.log('Nav link clicked:', this.getAttribute('href'));
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link and target section
            this.classList.add('active');
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
                console.log('Activated section:', targetId);
            }
            
            // Close mobile menu
            if (mobileNav) {
                mobileNav.classList.remove('active');
                console.log('Menu closed');
            }
            
            // Scroll to top
            window.scrollTo(0, 0);
        });
        console.log('Event listener attached to nav link', index);
    });
}

// Action Buttons Functionality
function initActionButtons() {
    console.log('Initializing action buttons...');
    const actionButtons = document.querySelectorAll('.action-btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const buttonText = this.textContent.trim();
            console.log('Action button clicked:', buttonText);
            
            switch(buttonText) {
                case 'VIEW HIGH RESOLUTION':
                    // Handle high resolution view
                    alert('High resolution view functionality will be implemented');
                    break;
                case 'DOWNLOAD FULL SIZE':
                    // Handle download
                    alert('Download functionality will be implemented');
                    break;
                case 'SHARE ON SOCIAL MEDIA':
                    // Handle social sharing
                    alert('Social sharing functionality will be implemented');
                    break;
            }
        });
    });
}

// Logo Click Handler
document.addEventListener('DOMContentLoaded', function() {
    const logoSection = document.querySelector('.logo-section');
    
    if (logoSection) {
        logoSection.addEventListener('click', function() {
            console.log('Logo clicked - returning to home');
            
            // Remove active from all sections and nav links
            const sections = document.querySelectorAll('.mobile-section');
            const navLinks = document.querySelectorAll('.nav-link');
            
            sections.forEach(s => s.classList.remove('active'));
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Activate home section and link
            const homeSection = document.getElementById('home');
            const homeLink = document.querySelector('.nav-link[href="#home"]');
            
            if (homeSection) homeSection.classList.add('active');
            if (homeLink) homeLink.classList.add('active');
            
            // Close mobile menu if open
            const mobileNav = document.getElementById('mobileNav');
            
            if (mobileNav) mobileNav.classList.remove('active');
            
            // Scroll to top
            window.scrollTo(0, 0);
        });
    }
});

// Touch and Swipe Enhancements
let touchStartY = 0;
let touchEndY = 0;
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', function(e) {
    touchStartY = e.changedTouches[0].screenY;
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', function(e) {
    touchEndY = e.changedTouches[0].screenY;
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const swipeDistanceY = touchStartY - touchEndY;
    const swipeDistanceX = touchStartX - touchEndX;
    
    // Swipe up to close menu
    if (swipeDistanceY > swipeThreshold) {
        const mobileNav = document.getElementById('mobileNav');
        
        if (mobileNav && mobileNav.classList.contains('active')) {
            mobileNav.classList.remove('active');
            console.log('Menu closed by swipe');
        }
    }
    
    // Handle horizontal swipes for carousel
    const carousel = document.getElementById('categoriesCarousel');
    if (carousel && Math.abs(swipeDistanceX) > swipeThreshold) {
        if (swipeDistanceX > 0) {
            // Swipe left - scroll right
            scrollCarousel('next');
        } else {
            // Swipe right - scroll left
            scrollCarousel('prev');
        }
    }
}

// Enhanced Categories Carousel Functionality
function initCategoriesCarousel() {
    const carousel = document.getElementById('categoriesCarousel');
    const prevBtn = document.getElementById('carouselPrev');
    const nextBtn = document.getElementById('carouselNext');
    const indicators = document.getElementById('carouselIndicators');
    const categoryBtns = document.querySelectorAll('.category-btn');
    
    if (!carousel || categoryBtns.length === 0) return;
    
    let currentIndex = 0;
    const itemsPerView = getItemsPerView();
    const totalItems = categoryBtns.length;
    const maxIndex = Math.max(0, totalItems - itemsPerView);
    
    // Create indicators
    const totalPages = Math.ceil(totalItems / itemsPerView);
    for (let i = 0; i < totalPages; i++) {
        const dot = document.createElement('div');
        dot.className = 'carousel-dot';
        if (i === 0) dot.classList.add('active');
        dot.addEventListener('click', () => goToPage(i));
        indicators.appendChild(dot);
    }
    
    // Navigation button handlers
    if (prevBtn) {
        prevBtn.addEventListener('click', () => scrollCarousel('prev'));
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => scrollCarousel('next'));
    }
    
    // Category button handlers
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all buttons
            categoryBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Filter gallery
            const category = btn.dataset.category;
            filterGallery(category);
            
            // Scroll to gallery section
            const gallerySection = document.querySelector('.gallery-section');
            if (gallerySection) {
                gallerySection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    function getItemsPerView() {
        const screenWidth = window.innerWidth;
        if (screenWidth < 360) return 2;
        if (screenWidth < 480) return 3;
        return 4;
    }
    
    function scrollCarousel(direction) {
        const itemWidth = carousel.children[0].offsetWidth + 15; // width + gap
        
        if (direction === 'next' && currentIndex < maxIndex) {
            currentIndex++;
        } else if (direction === 'prev' && currentIndex > 0) {
            currentIndex--;
        }
        
        const scrollPosition = currentIndex * itemWidth;
        carousel.scrollTo({
            left: scrollPosition,
            behavior: 'smooth'
        });
        
        updateIndicators();
        updateNavButtons();
    }
    
    function goToPage(pageIndex) {
        currentIndex = Math.min(pageIndex * itemsPerView, maxIndex);
        const itemWidth = carousel.children[0].offsetWidth + 15;
        const scrollPosition = currentIndex * itemWidth;
        
        carousel.scrollTo({
            left: scrollPosition,
            behavior: 'smooth'
        });
        
        updateIndicators();
        updateNavButtons();
    }
    
    function updateIndicators() {
        const dots = indicators.querySelectorAll('.carousel-dot');
        const currentPage = Math.floor(currentIndex / itemsPerView);
        
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === currentPage);
        });
    }
    
    function updateNavButtons() {
        if (prevBtn) {
            prevBtn.disabled = currentIndex === 0;
        }
        if (nextBtn) {
            nextBtn.disabled = currentIndex >= maxIndex;
        }
    }
    
    // Initialize button states
    updateNavButtons();
    
    // Handle window resize
    window.addEventListener('resize', () => {
        const newItemsPerView = getItemsPerView();
        if (newItemsPerView !== itemsPerView) {
            // Reinitialize carousel on significant layout changes
            setTimeout(() => {
                initCategoriesCarousel();
            }, 100);
        }
    });
}

// Gallery Filtering
function filterGallery(category) {
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    galleryItems.forEach(item => {
        const itemCategory = item.getAttribute('data-image-category');
        
        if (category === 'all' || itemCategory === category) {
            item.style.display = 'block';
            item.style.opacity = '1';
        } else {
            item.style.display = 'none';
            item.style.opacity = '0';
        }
    });
    
    console.log(`Filtered gallery by category: ${category}`);
}

// Mobile Contact Form Handling
function initMobileContactForm() {
    const mobileContactForm = document.getElementById('mobileContactForm');
    if (mobileContactForm) {
        mobileContactForm.addEventListener('submit', handleMobileContactSubmit);
    }
}

async function handleMobileContactSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('.action-btn');
    const originalText = submitBtn.textContent;
    
    // Show loading state
    submitBtn.textContent = 'Sending...';
    submitBtn.disabled = true;
    
    try {
        // Collect form data
        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            shoot_type: formData.get('shoot_type'),
            budget: formData.get('budget'),
            how_heard: formData.get('how_heard'),
            message: formData.get('message')
        };
        
        // Send to server
        const response = await fetch('/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Show success message
            showMobileMessage('Thank you for your message! We will get back to you soon.', 'success');
            form.reset();
        } else {
            // Show error message
            showMobileMessage(result.error || 'Failed to send message. Please try again.', 'error');
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        showMobileMessage('An error occurred. Please try again later.', 'error');
    } finally {
        // Restore button
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

function showMobileMessage(message, type) {
    // Remove any existing message
    const existingMessage = document.querySelector('.mobile-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `mobile-message ${type}`;
    messageDiv.textContent = message;
    
    // Insert message at top of contact form
    const contactForm = document.querySelector('.contact-form');
    contactForm.insertBefore(messageDiv, contactForm.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

// Image Modal Functionality
let currentImageCategory = '';

function openImageModal(galleryItem) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    const modalCategory = document.getElementById('modalCategory');
    
    // Get image data
    const img = galleryItem.querySelector('.gallery-image');
    const title = galleryItem.getAttribute('data-image-title');
    const category = galleryItem.getAttribute('data-image-category');
    
    // Store current category for filtering
    currentImageCategory = category;
    
    // Update modal content
    modalImage.src = img.src;
    modalImage.alt = img.alt;
    modalTitle.textContent = title || 'Untitled';
    modalCategory.textContent = category || 'Uncategorized';
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restore scrolling
}

function filterByModalCategory() {
    // Close modal
    closeImageModal();
    
    // Filter gallery by the category from the modal
    if (currentImageCategory) {
        // Update category button selection
        const categoryBtns = document.querySelectorAll('.category-btn');
        categoryBtns.forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-category') === currentImageCategory) {
                btn.classList.add('active');
            }
        });
        
        // Filter gallery
        filterGallery(currentImageCategory);
        
        // Navigate to home section if not already there
        const homeSection = document.getElementById('home');
        const sections = document.querySelectorAll('.mobile-section');
        const navLinks = document.querySelectorAll('.nav-link');
        
        if (homeSection) {
            sections.forEach(s => s.classList.remove('active'));
            navLinks.forEach(l => l.classList.remove('active'));
            
            homeSection.classList.add('active');
            const homeLink = document.querySelector('.nav-link[href="#home"]');
            if (homeLink) homeLink.classList.add('active');
            
            // Scroll to gallery section
            const gallerySection = document.querySelector('.gallery-section');
            if (gallerySection) {
                setTimeout(() => {
                    gallerySection.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            }
        }
    }
}

// Utility function for smooth scrolling
function scrollToElement(element) {
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Handle keyboard navigation for accessibility
document.addEventListener('keydown', function(e) {
    const modal = document.getElementById('imageModal');
    
    if (modal && modal.style.display === 'block') {
        if (e.key === 'Escape') {
            closeImageModal();
        }
    }
    
    // Handle arrow keys for carousel navigation
    const carousel = document.getElementById('categoriesCarousel');
    if (carousel && document.activeElement.classList.contains('category-btn')) {
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            scrollCarousel('prev');
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            scrollCarousel('next');
        }
    }
});

// Intersection Observer for carousel auto-scroll indicators
function initCarouselObserver() {
    const carousel = document.getElementById('categoriesCarousel');
    const indicators = document.getElementById('carouselIndicators');
    
    if (!carousel || !indicators) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const index = Array.from(carousel.children).indexOf(entry.target);
                const pageIndex = Math.floor(index / getItemsPerView());
                
                // Update indicators
                const dots = indicators.querySelectorAll('.carousel-dot');
                dots.forEach((dot, i) => {
                    dot.classList.toggle('active', i === pageIndex);
                });
            }
        });
    }, {
        root: carousel,
        threshold: 0.5
    });
    
    // Observe all category slides
    carousel.querySelectorAll('.category-slide').forEach(slide => {
        observer.observe(slide);
    });
}

// Initialize carousel observer when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initCarouselObserver, 100);
});

function getItemsPerView() {
    const screenWidth = window.innerWidth;
    if (screenWidth < 360) return 2;
    if (screenWidth < 480) return 3;
    return 4;
}

// Mobile Order Form Functions
function showMobileOrderForm() {
    console.log('showMobileOrderForm called');
    
    // Prevent body scroll
    document.body.classList.add('modal-open');
    
    // Use requestAnimationFrame for Safari compatibility
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            // Hide the image view
            const imageContainer = document.querySelector('.modal-content > .modal-image-container');
            const modalInfo = document.querySelector('.modal-content > .modal-info');
            const orderForm = document.getElementById('mobileOrderForm');
            
            console.log('Elements found:', { imageContainer, modalInfo, orderForm });
            
            if (imageContainer) imageContainer.style.display = 'none';
            if (modalInfo) modalInfo.style.display = 'none';
            
            // Show the order form
            if (orderForm) {
                orderForm.style.display = 'block';
                console.log('Order form displayed');
            }
        });
    });
    
    // Get image info from the modal
    const imageName = document.getElementById('modalTitle').textContent;
    const imageElement = document.getElementById('modalImage');
    
    // Populate order form with image details
    const orderImageDetails = document.getElementById('mobileOrderImageDetails');
    const orderImagePreview = document.getElementById('mobileOrderImagePreview');
    
    if (orderImageDetails && imageName && imageElement && imageElement.src) {
        const img = new Image();
        img.onload = function() {
            const width = this.naturalWidth;
            const height = this.naturalHeight;
            
            // Calculate DPI for 12x12 print
            const printSize = 12; // inches
            const dpi = Math.round(Math.min(width, height) / printSize);
            
            // Populate image details
            orderImageDetails.innerHTML = `
                <p><strong>Image Name:</strong> ${imageName}</p>
                <p><strong>Image Size:</strong> ${width}x${height} pixels, DPI: ${dpi}</p>
                <p><strong>Product:</strong> Canvas Print 12x12</p>
                <p><strong>Image:</strong> ${imageElement.src}</p>
            `;
            
            // Add image thumbnail
            if (orderImagePreview) {
                orderImagePreview.innerHTML = `
                    <img src="${imageElement.src}" alt="${imageName}">
                `;
            }
        };
        img.src = imageElement.src;
    }
}

function showMobileImageView() {
    console.log('showMobileImageView called');
    
    // Allow body scroll - multiple methods to ensure it works
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.position = '';
    
    // Hide the order form
    const orderForm = document.getElementById('mobileOrderForm');
    if (orderForm) orderForm.style.display = 'none';
    
    // Show the image view
    const imageContainer = document.querySelector('.modal-content > .modal-image-container');
    const modalInfo = document.querySelector('.modal-content > .modal-info');
    
    if (imageContainer) imageContainer.style.display = 'block';
    if (modalInfo) modalInfo.style.display = 'block';
    
    console.log('Image view restored, scroll enabled');
}

// Update closeImageModal to reset mobile form
function closeImageModal() {
    console.log('closeImageModal called');
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.style.display = 'none';
        
        // Always ensure body scroll is restored
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.position = '';
        
        // Reset to image view (this also removes modal-open class)
        showMobileImageView();
        
        // Clear any previous order form data
        const orderImageDetails = document.getElementById('mobileOrderImageDetails');
        if (orderImageDetails) orderImageDetails.innerHTML = '';
        
        const orderImagePreview = document.getElementById('mobileOrderImagePreview');
        if (orderImagePreview) orderImagePreview.innerHTML = '';
        
        console.log('Modal closed and scroll restored');
    }
}

// Legacy function for compatibility
function openOrderForm() {
    showMobileOrderForm();
}
