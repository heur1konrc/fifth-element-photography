// Global variables
let allImages = [];
let currentCategory = 'all';

// DOM elements
const imageGrid = document.getElementById('imageGrid');
const galleryTitle = document.getElementById('galleryTitle');
const imageCount = document.getElementById('imageCount');
const heroImage = document.getElementById('heroImage');
const modal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalTitle = document.getElementById('modalTitle');
const modalCategory = document.getElementById('modalCategory');
const closeModal = document.querySelector('.close');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadImages();
    setupEventListeners();
});

// Load images from API
async function loadImages() {
    try {
        const response = await fetch('/api/images');
        allImages = await response.json();
        
        if (allImages.length > 0) {
            // Set random hero image
            setRandomHeroImage();
            
            // Display all images initially
            displayImages(allImages);
            updateImageCount(allImages.length);
        } else {
            imageGrid.innerHTML = '<div class="loading">No images found in /data directory</div>';
        }
    } catch (error) {
        console.error('Error loading images:', error);
        imageGrid.innerHTML = '<div class="loading">Error loading images</div>';
    }
}

// Set random hero image
function setRandomHeroImage() {
    if (allImages.length > 0) {
        const randomImage = allImages[Math.floor(Math.random() * allImages.length)];
        heroImage.style.backgroundImage = `url('${randomImage.url}')`;
    }
}

// Display images in masonry grid
function displayImages(images) {
    if (images.length === 0) {
        imageGrid.innerHTML = '<div class="loading">No images found for this category</div>';
        return;
    }

    const imageHTML = images.map(image => `
        <div class="image-item" onclick="openModal('${image.url}', '${image.title}', '${image.category}')">
            <img src="${image.url}" alt="${image.title}" loading="lazy">
            <div class="image-info">
                <div class="image-title">${image.title}</div>
                <div class="image-category">${image.category}</div>
            </div>
        </div>
    `).join('');

    imageGrid.innerHTML = imageHTML;
}

// Filter images by category
function filterImages(category) {
    currentCategory = category;
    
    let filteredImages;
    if (category === 'all') {
        filteredImages = allImages;
        galleryTitle.textContent = 'All Galleries';
    } else {
        filteredImages = allImages.filter(image => image.category === category);
        galleryTitle.textContent = category.charAt(0).toUpperCase() + category.slice(1);
    }
    
    displayImages(filteredImages);
    updateImageCount(filteredImages.length);
}

// Update image count display
function updateImageCount(count) {
    imageCount.textContent = `${count} image${count !== 1 ? 's' : ''}`;
}

// Setup event listeners
function setupEventListeners() {
    // Navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active state
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Filter images
            const category = this.getAttribute('data-category');
            if (category) {
                filterImages(category);
            }
        });
    });

    // Modal close events
    closeModal.addEventListener('click', closeModalHandler);
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModalHandler();
        }
    });

    // Keyboard events
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModalHandler();
        }
    });
}

// Open image modal
function openModal(imageUrl, title, category) {
    modalImage.src = imageUrl;
    modalTitle.textContent = title;
    modalCategory.textContent = category.toUpperCase();
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Close modal
function closeModalHandler() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Smooth scrolling for navigation
function smoothScroll(target) {
    document.querySelector(target).scrollIntoView({
        behavior: 'smooth'
    });
}

