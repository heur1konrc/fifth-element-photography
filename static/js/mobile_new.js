// Mobile Navigation and Section Switching
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing mobile navigation...');
    initMobileNavigation();
    initSectionSwitching();
    initActionButtons();
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

document.addEventListener('touchstart', function(e) {
    touchStartY = e.changedTouches[0].screenY;
});

document.addEventListener('touchend', function(e) {
    touchEndY = e.changedTouches[0].screenY;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const swipeDistance = touchStartY - touchEndY;
    
    // Swipe up to close menu
    if (swipeDistance > swipeThreshold) {
        const mobileNav = document.getElementById('mobileNav');
        
        if (mobileNav && mobileNav.classList.contains('active')) {
            mobileNav.classList.remove('active');
            console.log('Menu closed by swipe');
        }
    }
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

// Initialize contact form when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initMobileContactForm();
});

// Categories Dropdown Functionality
function initCategoriesDropdown() {
    const categoriesBtn = document.getElementById('mobileCategoriesBtn');
    const categoriesDropdown = document.getElementById('mobileCategoriesDropdown');
    const categoryLinks = document.querySelectorAll('.category-link');
    
    if (categoriesBtn && categoriesDropdown) {
        categoriesBtn.addEventListener('click', function() {
            categoriesDropdown.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!categoriesBtn.contains(e.target) && !categoriesDropdown.contains(e.target)) {
                categoriesDropdown.classList.remove('active');
            }
        });
    }
    
    // Category filtering
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const category = this.getAttribute('data-category');
            
            // Update active state
            categoryLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Filter gallery
            filterGalleryByCategory(category);
            
            // Close dropdown
            if (categoriesDropdown) {
                categoriesDropdown.classList.remove('active');
            }
        });
    });
}

// Gallery Filtering
function filterGalleryByCategory(category) {
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    galleryItems.forEach(item => {
        const itemCategory = item.getAttribute('data-image-category');
        
        if (category === 'all' || itemCategory === category) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
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
        // Update category dropdown selection
        const categoryLinks = document.querySelectorAll('.category-link');
        categoryLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-category') === currentImageCategory) {
                link.classList.add('active');
            }
        });
        
        // Filter gallery
        filterGalleryByCategory(currentImageCategory);
        
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
            
            // Scroll to top
            window.scrollTo(0, 0);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initCategoriesDropdown();
});

// Categories Carousel Functionality
function initCategoriesCarousel() {
    const carousel = document.getElementById('categoriesCarousel');
    const indicators = document.getElementById('carouselIndicators');
    const slides = carousel.querySelectorAll('.category-slide');
    
    if (!carousel || slides.length === 0) return;
    
    // Create indicators
    const totalSlides = Math.ceil(slides.length / 3); // Show 3 categories per "page"
    for (let i = 0; i < totalSlides; i++) {
        const dot = document.createElement('div');
        dot.className = 'carousel-dot';
        if (i === 0) dot.classList.add('active');
        dot.addEventListener('click', () => scrollToSlide(i));
        indicators.appendChild(dot);
    }
    
    function scrollToSlide(index) {
        const slideWidth = slides[0].offsetWidth + 15; // width + gap
        const scrollPosition = index * slideWidth * 3;
        carousel.scrollTo({
            left: scrollPosition,
            behavior: 'smooth'
        });
        
        // Update indicators
        indicators.querySelectorAll('.carousel-dot').forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
    }
    
    // Handle category selection
    slides.forEach(slide => {
        const link = slide.querySelector('.category-link');
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all links
            slides.forEach(s => s.querySelector('.category-link').classList.remove('active'));
            
            // Add active class to clicked link
            link.classList.add('active');
            
            // Filter gallery
            const category = link.dataset.category;
            filterGallery(category);
            
            // Return to home section
            showSection('home');
        });
    });
}

// Initialize carousel when DOM is loaded
document.addEventListener('DOMContentLoaded', initCategoriesCarousel);
