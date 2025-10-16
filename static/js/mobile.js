// Mobile JavaScript - Built from scratch for Fifth Element Photography

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile functionality
    initMobileMenu();
    initCategoryFilters();
    initSwipeGallery();
    initContactForm();
    initModals();
});

// Mobile Menu Toggle
function initMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const navLinks = document.querySelectorAll('.nav-link');

    menuToggle.addEventListener('click', function() {
        menuToggle.classList.toggle('active');
        mobileMenu.classList.toggle('active');
    });

    // Handle navigation
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding section
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
            }
            
            // Close mobile menu
            menuToggle.classList.remove('active');
            mobileMenu.classList.remove('active');
        });
    });
}

// Category Filters
function initCategoryFilters() {
    const categoryBtns = document.querySelectorAll('.category-btn');
    const swipeItems = document.querySelectorAll('.swipe-item');
    const imageCount = document.getElementById('imageCount');

    categoryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            categoryBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            const category = this.getAttribute('data-category');
            let visibleCount = 0;
            
            swipeItems.forEach(item => {
                const itemCategory = item.getAttribute('data-category');
                
                if (category === 'all' || itemCategory === category) {
                    item.classList.remove('hidden');
                    visibleCount++;
                } else {
                    item.classList.add('hidden');
                }
            });
            
            // Update image count
            if (imageCount) {
                imageCount.textContent = `${visibleCount} images`;
            }
        });
    });
}

// Swipe Gallery
function initSwipeGallery() {
    const swipeContainer = document.getElementById('swipeContainer');
    
    if (!swipeContainer) return;
    
    // Add touch event listeners for smooth scrolling
    let isDown = false;
    let startX;
    let scrollLeft;
    
    swipeContainer.addEventListener('mousedown', (e) => {
        isDown = true;
        swipeContainer.classList.add('active');
        startX = e.pageX - swipeContainer.offsetLeft;
        scrollLeft = swipeContainer.scrollLeft;
    });
    
    swipeContainer.addEventListener('mouseleave', () => {
        isDown = false;
        swipeContainer.classList.remove('active');
    });
    
    swipeContainer.addEventListener('mouseup', () => {
        isDown = false;
        swipeContainer.classList.remove('active');
    });
    
    swipeContainer.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - swipeContainer.offsetLeft;
        const walk = (x - startX) * 2;
        swipeContainer.scrollLeft = scrollLeft - walk;
    });
    
    // Touch events for mobile
    swipeContainer.addEventListener('touchstart', (e) => {
        startX = e.touches[0].pageX - swipeContainer.offsetLeft;
        scrollLeft = swipeContainer.scrollLeft;
    });
    
    swipeContainer.addEventListener('touchmove', (e) => {
        if (!startX) return;
        const x = e.touches[0].pageX - swipeContainer.offsetLeft;
        const walk = (x - startX) * 2;
        swipeContainer.scrollLeft = scrollLeft - walk;
    });
}

// Contact Form
function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (!contactForm) return;
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const submitBtn = this.querySelector('.submit-btn');
        const originalText = submitBtn.innerHTML;
        
        // Show loading state
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        submitBtn.disabled = true;
        
        // Submit form
        fetch('/contact', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Message sent successfully!', 'success');
                contactForm.reset();
            } else {
                showNotification('Error sending message. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error sending message. Please try again.', 'error');
        })
        .finally(() => {
            // Restore button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    });
}

// Modals
function initModals() {
    // Close modals when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeImageModal();
            closeOrderModal();
        }
    });
}

// Image Modal Functions
function openImageModal(imageUrl, title, category) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    const modalCategory = document.getElementById('modalCategory');
    
    if (modal && modalImage && modalTitle && modalCategory) {
        modalImage.src = imageUrl;
        modalTitle.textContent = title;
        modalCategory.textContent = category.toUpperCase();
        modal.style.display = 'block';
        
        // Prevent body scrolling
        document.body.style.overflow = 'hidden';
    }
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Order Modal Functions
function openOrderModal(imageUrl = null, title = null) {
    const modal = document.getElementById('orderModal');
    const container = document.getElementById('orderFormContainer');
    
    if (!modal || !container) return;
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Load order form from desktop system
    container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading order form...</div>';
    
    // Fetch the order form HTML from the desktop test order form
    fetch('/test_order_form')
        .then(response => response.text())
        .then(html => {
            // Extract just the form content from the full page
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const orderForm = doc.querySelector('.order-form-container');
            
            if (orderForm) {
                container.innerHTML = orderForm.outerHTML;
                
                // If specific image was selected, pre-populate it
                if (imageUrl && title) {
                    const imagePreview = container.querySelector('.selected-image img');
                    const imageTitle = container.querySelector('.selected-image-title');
                    
                    if (imagePreview) imagePreview.src = imageUrl;
                    if (imageTitle) imageTitle.textContent = title;
                }
                
                // Initialize PayPal buttons and form functionality
                initOrderForm();
            } else {
                container.innerHTML = '<p>Error loading order form. Please try again.</p>';
            }
        })
        .catch(error => {
            console.error('Error loading order form:', error);
            container.innerHTML = '<p>Error loading order form. Please try again.</p>';
        });
}

function closeOrderModal() {
    const modal = document.getElementById('orderModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Initialize order form functionality (PayPal integration)
function initOrderForm() {
    // This function will initialize the PayPal buttons and form validation
    // The actual PayPal integration code will be loaded from the desktop system
    
    // Re-run any PayPal initialization scripts
    if (window.paypal && typeof initializePayPalButtons === 'function') {
        initializePayPalButtons();
    }
    
    // Re-initialize any form validation
    if (typeof initializeOrderFormValidation === 'function') {
        initializeOrderFormValidation();
    }
}

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 90px;
        left: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 15px;
        border-radius: 8px;
        z-index: 3000;
        transform: translateY(-100px);
        transition: transform 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateY(0)';
    }, 100);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.transform = 'translateY(-100px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Handle window resize
window.addEventListener('resize', debounce(() => {
    // Recalculate any layout-dependent elements
    const swipeContainer = document.getElementById('swipeContainer');
    if (swipeContainer) {
        // Reset scroll position on orientation change
        swipeContainer.scrollLeft = 0;
    }
}, 250));
