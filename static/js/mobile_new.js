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
