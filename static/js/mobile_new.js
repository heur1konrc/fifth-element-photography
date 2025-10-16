// Mobile New Layout JavaScript - Fifth Element Photography

document.addEventListener('DOMContentLoaded', function() {
    initMobileNavigation();
    initSectionSwitching();
    initActionButtons();
});

// Mobile Navigation Toggle
function initMobileNavigation() {
    const menuBtn = document.getElementById('mobileMenuBtn');
    const mobileNav = document.getElementById('mobileNav');
    
    if (menuBtn && mobileNav) {
        menuBtn.addEventListener('click', function() {
            mobileNav.classList.toggle('active');
            
            // Update button text
            if (mobileNav.classList.contains('active')) {
                menuBtn.textContent = 'CLOSE';
            } else {
                menuBtn.textContent = 'MENU';
            }
        });
    }
}

// Section Switching
function initSectionSwitching() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.mobile-section');
    const mobileNav = document.getElementById('mobileNav');
    const menuBtn = document.getElementById('mobileMenuBtn');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
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
            }
            
            // Close mobile menu
            if (mobileNav) {
                mobileNav.classList.remove('active');
            }
            if (menuBtn) {
                menuBtn.textContent = 'MENU';
            }
            
            // Scroll to top
            window.scrollTo(0, 0);
        });
    });
}

// Action Buttons Functionality
function initActionButtons() {
    const actionButtons = document.querySelectorAll('.action-btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const buttonText = this.textContent.trim();
            
            switch(buttonText) {
                case 'VIEW HIGH RESOLUTION':
                    handleViewHighRes();
                    break;
                case 'DOWNLOAD FULL SIZE':
                    handleDownloadFullSize();
                    break;
                case 'SHARE ON SOCIAL MEDIA':
                    handleShareSocial();
                    break;
            }
        });
    });
}

// Action Button Handlers (placeholder functions)
function handleViewHighRes() {
    // Placeholder for high resolution view
    console.log('View High Resolution clicked');
    // Will be connected to admin functionality later
}

function handleDownloadFullSize() {
    // Placeholder for download functionality
    console.log('Download Full Size clicked');
    // Will be connected to admin functionality later
}

function handleShareSocial() {
    // Placeholder for social sharing
    console.log('Share on Social Media clicked');
    // Will be connected to admin functionality later
}

// Logo Click Handler (return to home)
document.addEventListener('DOMContentLoaded', function() {
    const logoContainer = document.querySelector('.logo-container');
    
    if (logoContainer) {
        logoContainer.addEventListener('click', function() {
            // Remove active from all sections and links
            document.querySelectorAll('.mobile-section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            
            // Activate home section and link
            const homeSection = document.getElementById('home');
            const homeLink = document.querySelector('a[href="#home"]');
            
            if (homeSection) homeSection.classList.add('active');
            if (homeLink) homeLink.classList.add('active');
            
            // Close mobile menu if open
            const mobileNav = document.getElementById('mobileNav');
            const menuBtn = document.getElementById('mobileMenuBtn');
            
            if (mobileNav) mobileNav.classList.remove('active');
            if (menuBtn) menuBtn.textContent = 'MENU';
            
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
        const menuBtn = document.getElementById('mobileMenuBtn');
        
        if (mobileNav && mobileNav.classList.contains('active')) {
            mobileNav.classList.remove('active');
            if (menuBtn) menuBtn.textContent = 'MENU';
        }
    }
}
