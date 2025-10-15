/**
 * Enhanced Mobile JavaScript for Fifth Element Photography
 * Version: 2.0 Mobile-First
 * Focus: Mobile Ordering Excellence
 */

class MobilePhotoGallery {
    constructor() {
        this.currentImageIndex = 0;
        this.filteredImages = [];
        this.allImages = window.imagesData || [];
        this.categories = window.categoriesData || [];
        this.isMenuOpen = false;
        this.lastScrollY = 0;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupMobileNavigation();
        this.setupImageFiltering();
        this.setupImageModal();
        this.setupScrollBehavior();
        this.loadImages();
        
        // Initialize with all images
        this.filteredImages = [...this.allImages];
        this.updateImageCount();
    }
    
    setupEventListeners() {
        // Mobile menu toggle
        const menuBtn = document.getElementById('mobileMenuBtn');
        const menuOverlay = document.getElementById('mobileMenuOverlay');
        
        if (menuBtn) {
            menuBtn.addEventListener('click', () => this.toggleMobileMenu());
        }
        
        if (menuOverlay) {
            menuOverlay.addEventListener('click', () => this.closeMobileMenu());
        }
        
        // Navigation links
        document.querySelectorAll('.mobile-nav-link, .nav-link').forEach(link => {
            link.addEventListener('click', (e) => this.handleNavigation(e));
        });
        
        // Category filters
        document.querySelectorAll('.mobile-filter-btn, .mobile-category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleCategoryFilter(e));
        });
        
        // Hero CTA
        const heroCTA = document.querySelector('.mobile-hero-cta');
        if (heroCTA) {
            heroCTA.addEventListener('click', (e) => {
                e.preventDefault();
                this.scrollToGallery();
            });
        }
        
        // Touch events for image swiping
        this.setupTouchEvents();
    }
    
    setupMobileNavigation() {
        // Handle section switching
        const navLinks = document.querySelectorAll('[data-section]');
        const sections = document.querySelectorAll('.content-section');
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                if (link.dataset.section) {
                    e.preventDefault();
                    
                    // Update active nav
                    navLinks.forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                    
                    // Show section
                    sections.forEach(section => section.classList.remove('active'));
                    const targetSection = document.getElementById(link.dataset.section + '-section');
                    if (targetSection) {
                        targetSection.classList.add('active');
                    }
                    
                    // Close mobile menu
                    this.closeMobileMenu();
                    
                    // Scroll to top
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
        });
    }
    
    setupImageFiltering() {
        // Category filtering functionality
        const filterBtns = document.querySelectorAll('.mobile-filter-btn, .mobile-category-btn');
        
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                
                const category = btn.dataset.category;
                
                // Update active filter
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Filter images
                this.filterImages(category);
                
                // Close menu if filtering from mobile menu
                if (btn.classList.contains('mobile-category-btn')) {
                    this.closeMobileMenu();
                }
            });
        });
    }
    
    setupImageModal() {
        // Image click handlers
        document.addEventListener('click', (e) => {
            const imageItem = e.target.closest('.mobile-image-item, .image-item');
            if (imageItem) {
                const imageId = imageItem.dataset.imageId;
                if (imageId) {
                    this.openImageModal(imageId);
                }
            }
        });
    }
    
    setupScrollBehavior() {
        // Header hide/show on scroll
        const header = document.getElementById('mobileHeader');
        if (!header) return;
        
        let ticking = false;
        
        const updateHeader = () => {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > this.lastScrollY && currentScrollY > 100) {
                // Scrolling down
                header.classList.add('hidden');
            } else {
                // Scrolling up
                header.classList.remove('hidden');
            }
            
            this.lastScrollY = currentScrollY;
            ticking = false;
        };
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateHeader);
                ticking = true;
            }
        });
    }
    
    setupTouchEvents() {
        // Touch events for image swiping in modal
        let startX = 0;
        let startY = 0;
        let isSwipe = false;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isSwipe = false;
        });
        
        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;
            
            const currentX = e.touches[0].clientX;
            const currentY = e.touches[0].clientY;
            
            const diffX = Math.abs(currentX - startX);
            const diffY = Math.abs(currentY - startY);
            
            if (diffX > diffY && diffX > 50) {
                isSwipe = true;
            }
        });
        
        document.addEventListener('touchend', (e) => {
            if (!isSwipe || !startX) return;
            
            const endX = e.changedTouches[0].clientX;
            const diffX = startX - endX;
            
            // Only handle swipes in modal
            const modal = document.querySelector('.modal.active, .mobile-image-modal.active');
            if (modal) {
                if (diffX > 50) {
                    // Swipe left - next image
                    this.nextImage();
                } else if (diffX < -50) {
                    // Swipe right - previous image
                    this.previousImage();
                }
            }
            
            startX = 0;
            startY = 0;
            isSwipe = false;
        });
    }
    
    toggleMobileMenu() {
        const menu = document.getElementById('mobileMenu');
        const overlay = document.getElementById('mobileMenuOverlay');
        const btn = document.getElementById('mobileMenuBtn');
        
        if (!menu || !overlay || !btn) return;
        
        this.isMenuOpen = !this.isMenuOpen;
        
        if (this.isMenuOpen) {
            menu.classList.add('active');
            overlay.classList.add('active');
            btn.classList.add('active');
            document.body.style.overflow = 'hidden';
        } else {
            menu.classList.remove('active');
            overlay.classList.remove('active');
            btn.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    closeMobileMenu() {
        if (this.isMenuOpen) {
            this.toggleMobileMenu();
        }
    }
    
    handleNavigation(e) {
        const link = e.target.closest('[data-section]');
        if (!link || !link.dataset.section) return;
        
        e.preventDefault();
        
        // Update active states
        document.querySelectorAll('.mobile-nav-link, .nav-link').forEach(l => {
            l.classList.remove('active');
        });
        link.classList.add('active');
        
        // Show corresponding section
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        const targetSection = document.getElementById(link.dataset.section + '-section');
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // Close mobile menu
        this.closeMobileMenu();
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    handleCategoryFilter(e) {
        e.preventDefault();
        
        const btn = e.target.closest('[data-category]');
        if (!btn) return;
        
        const category = btn.dataset.category;
        
        // Update active filter
        document.querySelectorAll('.mobile-filter-btn, .mobile-category-btn').forEach(b => {
            b.classList.remove('active');
        });
        btn.classList.add('active');
        
        // Filter images
        this.filterImages(category);
        
        // Close menu if filtering from mobile menu
        if (btn.classList.contains('mobile-category-btn')) {
            this.closeMobileMenu();
        }
    }
    
    filterImages(category) {
        if (category === 'all') {
            this.filteredImages = [...this.allImages];
        } else {
            this.filteredImages = this.allImages.filter(img => 
                img.category.toLowerCase() === category.toLowerCase()
            );
        }
        
        this.updateImageGrid();
        this.updateImageCount();
    }
    
    updateImageGrid() {
        const grid = document.getElementById('mobileImageGrid') || document.querySelector('.masonry-grid');
        if (!grid) return;
        
        // Show/hide images based on filter
        const imageItems = grid.querySelectorAll('.mobile-image-item, .image-item');
        
        imageItems.forEach(item => {
            const imageCategory = item.dataset.category;
            const shouldShow = this.filteredImages.some(img => 
                img.category.toLowerCase() === imageCategory
            );
            
            if (shouldShow) {
                item.style.display = 'block';
                item.style.animation = 'fadeIn 0.3s ease';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    updateImageCount() {
        const countElement = document.getElementById('mobileImageCount');
        if (countElement) {
            countElement.textContent = `${this.filteredImages.length} images`;
        }
        
        // Update filter counts
        document.querySelectorAll('.mobile-filter-count').forEach(count => {
            const filterBtn = count.closest('[data-category]');
            if (filterBtn) {
                const category = filterBtn.dataset.category;
                if (category === 'all') {
                    count.textContent = this.allImages.length;
                } else {
                    const categoryCount = this.allImages.filter(img => 
                        img.category.toLowerCase() === category.toLowerCase()
                    ).length;
                    count.textContent = categoryCount;
                }
            }
        });
    }
    
    loadImages() {
        // Progressive image loading
        const imageItems = document.querySelectorAll('.mobile-image-item img, .image-item img');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Add loading skeleton
                    img.parentElement.classList.add('mobile-image-skeleton');
                    
                    img.onload = () => {
                        img.parentElement.classList.remove('mobile-image-skeleton');
                        img.style.opacity = '1';
                    };
                    
                    // Stop observing this image
                    imageObserver.unobserve(img);
                }
            });
        });
        
        imageItems.forEach(img => {
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.3s ease';
            imageObserver.observe(img);
        });
    }
    
    scrollToGallery() {
        const gallery = document.getElementById('gallery') || document.querySelector('.mobile-gallery-section');
        if (gallery) {
            gallery.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
    
    openImageModal(imageId) {
        // Find the image data
        const imageData = this.allImages.find(img => img.id == imageId);
        if (!imageData) return;
        
        // For now, redirect to order form with image data
        // This will be enhanced with a proper mobile modal later
        const orderUrl = `/test_order_form?image=${encodeURIComponent(imageData.filename)}&title=${encodeURIComponent(imageData.title)}`;
        window.open(orderUrl, '_blank');
    }
    
    nextImage() {
        if (this.currentImageIndex < this.filteredImages.length - 1) {
            this.currentImageIndex++;
            this.updateModalImage();
        }
    }
    
    previousImage() {
        if (this.currentImageIndex > 0) {
            this.currentImageIndex--;
            this.updateModalImage();
        }
    }
    
    updateModalImage() {
        // This will be implemented when we create the mobile modal
        console.log('Update modal image:', this.currentImageIndex);
    }
    
    updateCartCount(count) {
        // Update cart count in mobile header and menu
        const mobileCartCount = document.getElementById('mobileCartCount');
        const mobileMenuCartCount = document.getElementById('mobileMenuCartCount');
        
        if (mobileCartCount) {
            mobileCartCount.textContent = count;
            mobileCartCount.style.display = count > 0 ? 'flex' : 'none';
        }
        
        if (mobileMenuCartCount) {
            mobileMenuCartCount.textContent = count;
        }
        
        // Update desktop cart count too
        const cartCount = document.getElementById('cartCount');
        if (cartCount) {
            cartCount.textContent = count;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize mobile gallery
    window.mobileGallery = new MobilePhotoGallery();
    
    // Initialize Lucide icons if available
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideInLeft {
            from { transform: translateX(-100%); }
            to { transform: translateX(0); }
        }
        
        @keyframes slideInRight {
            from { transform: translateX(100%); }
            to { transform: translateX(0); }
        }
        
        .mobile-image-item {
            animation: fadeIn 0.3s ease;
        }
        
        .mobile-menu.active {
            animation: slideInLeft 0.3s ease;
        }
    `;
    document.head.appendChild(style);
});

// Export for global access
window.MobilePhotoGallery = MobilePhotoGallery;
