// Mobile-Optimized JavaScript for Fifth Element Photography

document.addEventListener('DOMContentLoaded', function() {
    console.log('Mobile script loaded');
    
    // Initialize mobile functionality
    initMobileNavigation();
    initMobileGallery();
    initMobileFilters();
    initMobileHero();
    initMobileContactForm();
});

// Mobile Navigation
function initMobileNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const headerContactBtn = document.querySelector('.header-contact-btn');
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
    
    // Handle header contact button
    if (headerContactBtn) {
        headerContactBtn.addEventListener('click', function() {
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

// Mobile Gallery
let allImages = [];
let currentFilter = 'all';

function initMobileGallery() {
    loadMobileImages();
}

async function loadMobileImages() {
    try {
        const response = await fetch('/api/images');
        allImages = await response.json();
        
        console.log('Loaded images:', allImages.length);
        
        // Set random hero image
        setMobileHeroImage();
        
        // Display all images initially
        displayMobileImages(allImages);
        updateMobileImageCount(allImages.length);
        
    } catch (error) {
        console.error('Error loading images:', error);
        document.getElementById('mobileImageGrid').innerHTML = 
            '<div class="loading">Error loading images. Please try again.</div>';
    }
}

function displayMobileImages(images) {
    const grid = document.getElementById('mobileImageGrid');
    
    if (images.length === 0) {
        grid.innerHTML = '<div class="loading">No images found for this category.</div>';
        return;
    }
    
    grid.innerHTML = images.map(image => `
        <div class="mobile-image-item" onclick="openMobileModal('${image.url}', '${image.title}', '${image.category}')">
            <img src="${image.url}" alt="${image.title}" loading="lazy">
            <div class="mobile-image-overlay">
                <div class="mobile-image-title">${image.title}</div>
                <div class="mobile-image-category">${image.category}</div>
            </div>
        </div>
    `).join('');
}

function updateMobileImageCount(count) {
    const countElement = document.getElementById('mobileImageCount');
    if (countElement) {
        countElement.textContent = `${count} images`;
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
    let filteredImages;
    
    if (category === 'all') {
        filteredImages = allImages;
    } else {
        filteredImages = allImages.filter(image => 
            image.category.toLowerCase() === category.toLowerCase()
        );
    }
    
    displayMobileImages(filteredImages);
    updateMobileImageCount(filteredImages.length);
    
    // Scroll to gallery
    const gallery = document.getElementById('mobileImageGrid');
    if (gallery) {
        gallery.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Mobile Hero Image
function initMobileHero() {
    setMobileHeroImage();
}

async function setMobileHeroImage() {
    const hero = document.getElementById('mobileHero');
    if (!hero) return;
    
    try {
        // First, try to get the selected hero image from API (same as desktop)
        const heroResponse = await fetch('/api/hero_image');
        const heroData = await heroResponse.json();
        
        if (heroData.filename) {
            // Use the selected hero image (same as desktop)
            hero.style.backgroundImage = `url('/images/${heroData.filename}')`;
            hero.style.backgroundSize = 'cover';
            hero.style.backgroundPosition = 'center';
            hero.style.backgroundRepeat = 'no-repeat';
        } else {
            // Fallback to random hero image
            setRandomMobileHeroImage();
        }
    } catch (error) {
        console.error('Error loading hero image selection:', error);
        // Fallback to random hero image
        setRandomMobileHeroImage();
    }
}

// Fallback function for random hero image
function setRandomMobileHeroImage() {
    const hero = document.getElementById('mobileHero');
    if (!hero || allImages.length === 0) return;
    
    // Use random image as fallback
    const randomImage = allImages[Math.floor(Math.random() * allImages.length)];
    if (randomImage) {
        hero.style.backgroundImage = `url('${randomImage.url}')`;
        hero.style.backgroundSize = 'cover';
        hero.style.backgroundPosition = 'center';
        hero.style.backgroundRepeat = 'no-repeat';
    }
}

// Mobile Modal
function openMobileModal(imageUrl, title, category) {
    const modal = document.getElementById('mobileImageModal');
    const modalImage = document.getElementById('mobileModalImage');
    const modalTitle = document.getElementById('mobileModalTitle');
    const modalCategory = document.getElementById('mobileModalCategory');
    
    if (modal && modalImage && modalTitle && modalCategory) {
        modalImage.src = imageUrl;
        modalImage.alt = title;
        modalTitle.textContent = title;
        modalCategory.textContent = category.toUpperCase();
        
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeMobileModal() {
    const modal = document.getElementById('mobileImageModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Close modal when clicking outside the image
document.addEventListener('click', function(event) {
    const modal = document.getElementById('mobileImageModal');
    if (event.target === modal) {
        closeMobileModal();
    }
});

// Touch gestures for modal
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', function(event) {
    touchStartX = event.changedTouches[0].screenX;
});

document.addEventListener('touchend', function(event) {
    touchEndX = event.changedTouches[0].screenX;
    handleMobileSwipe();
});

function handleMobileSwipe() {
    const modal = document.getElementById('mobileImageModal');
    if (modal && modal.style.display === 'block') {
        const swipeThreshold = 50;
        const swipeDistance = touchEndX - touchStartX;
        
        if (Math.abs(swipeDistance) > swipeThreshold) {
            // Swipe detected - close modal
            closeMobileModal();
        }
    }
}

// Image Actions (same as desktop but mobile-optimized)
function viewFullscreen(imageUrl, title) {
    openMobileModal(imageUrl, title, '');
}

function downloadImage(imageUrl, filename) {
    try {
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = filename || 'image.jpg';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        console.error('Download failed:', error);
        // Fallback: open in new tab
        window.open(imageUrl, '_blank');
    }
}

function shareOnSocial(title, imageUrl) {
    const currentUrl = window.location.href;
    const shareText = `Check out this amazing photo: ${title}`;
    
    if (navigator.share) {
        // Use native mobile sharing if available
        navigator.share({
            title: title,
            text: shareText,
            url: currentUrl
        }).catch(error => {
            console.log('Error sharing:', error);
            fallbackShare(shareText, currentUrl);
        });
    } else {
        fallbackShare(shareText, currentUrl);
    }
}

function fallbackShare(text, url) {
    // Fallback sharing options
    const shareOptions = [
        {
            name: 'Twitter',
            url: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`
        },
        {
            name: 'Facebook',
            url: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`
        },
        {
            name: 'Copy Link',
            action: () => {
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(url).then(() => {
                        alert('Link copied to clipboard!');
                    });
                } else {
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = url;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    alert('Link copied to clipboard!');
                }
            }
        }
    ];
    
    // Create simple share menu
    const shareMenu = shareOptions.map(option => {
        if (option.action) {
            return `<button onclick="(${option.action.toString()})()" style="display: block; width: 100%; padding: 10px; margin: 5px 0; background: #6799c2; color: #000; border: none; border-radius: 5px; cursor: pointer;">${option.name}</button>`;
        } else {
            return `<a href="${option.url}" target="_blank" style="display: block; width: 100%; padding: 10px; margin: 5px 0; background: #6799c2; color: #000; text-decoration: none; border-radius: 5px; text-align: center;">${option.name}</a>`;
        }
    }).join('');
    
    const shareDialog = document.createElement('div');
    shareDialog.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 2000; display: flex; align-items: center; justify-content: center;">
            <div style="background: #111; padding: 20px; border-radius: 10px; max-width: 300px; width: 90%;">
                <h3 style="color: #fff; margin-bottom: 15px; text-align: center;">Share this image</h3>
                ${shareMenu}
                <button onclick="this.closest('div').parentElement.remove()" style="display: block; width: 100%; padding: 10px; margin: 10px 0 0 0; background: #333; color: #fff; border: none; border-radius: 5px; cursor: pointer;">Cancel</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(shareDialog);
}

// Smooth scrolling for mobile
function smoothScrollTo(element) {
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Handle orientation changes
window.addEventListener('orientationchange', function() {
    setTimeout(() => {
        // Recalculate layout after orientation change
        if (allImages.length > 0) {
            displayMobileImages(
                currentFilter === 'all' ? allImages : 
                allImages.filter(img => img.category.toLowerCase() === currentFilter.toLowerCase())
            );
        }
    }, 100);
});

// Performance optimization: Lazy loading for images
function observeImages() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Initialize lazy loading after images are loaded
setTimeout(observeImages, 1000);

// Mobile Contact Form
function initMobileContactForm() {
    const mobileContactForm = document.querySelector('#contact-section form');
    if (mobileContactForm) {
        mobileContactForm.addEventListener('submit', handleMobileContactSubmit);
    }
}

async function handleMobileContactSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('.mobile-submit-btn');
    const originalText = submitBtn.textContent;
    
    // Get form data
    const formData = {
        name: form.querySelector('input[placeholder="Your Name"]').value,
        email: form.querySelector('input[placeholder="Your Email"]').value,
        phone: form.querySelector('input[placeholder="Your Phone Number"]').value,
        shoot_type: form.querySelector('#mobile-shoot-type').value,
        budget: form.querySelector('#mobile-budget').value,
        how_heard: form.querySelector('#mobile-how-heard').value,
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
