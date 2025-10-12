// Print sizes for analysis
const printSizes = [
    { name: "4 x 6", width: 4, height: 6 },
    { name: "5 x 7", width: 5, height: 7 },
    { name: "8 x 10", width: 8, height: 10 },
    { name: "8.5 x 11 (Letter)", width: 8.5, height: 11 },
    { name: "11 x 14", width: 11, height: 14 },
    { name: "16 x 20", width: 16, height: 20 },
    { name: "20 x 30", width: 20, height: 30 },
    { name: "12 x 12 (Square)", width: 12, height: 12 }
];

// Calculate aspect ratio
function getAspectRatio(width, height) {
    const gcd = (a, b) => b === 0 ? a : gcd(b, a % b);
    const divisor = gcd(width, height);
    const w = width / divisor;
    const h = height / divisor;
    
    // Common ratios
    if (Math.abs(w/h - 3/2) < 0.1) return "3:2";
    if (Math.abs(w/h - 4/3) < 0.1) return "4:3";
    if (Math.abs(w/h - 16/9) < 0.1) return "16:9";
    if (Math.abs(w/h - 4/5) < 0.1) return "4:5";
    if (Math.abs(w/h - 1) < 0.1) return "1:1";
    
    return `${Math.round(w)}:${Math.round(h)}`;
}

// Get quality rating based on DPI
function getQualityRating(dpi) {
    if (dpi >= 300) {
        return { text: "Excellent", class: "excellent" };
    } else if (dpi >= 150) {
        return { text: "Good", class: "good" };
    } else {
        return { text: "Poor", class: "poor" };
    }
}

// Main function called from "Open Image And Analyze" button
function openImageAndAnalyze(filename, title) {
    // Open the full-size image in a new window
    const imageUrl = `https://fifthelement.photos/images/${filename}`;
    window.open(imageUrl, '_blank');
    
    // Analyze the image by loading it from the URL
    analyzeImageFromUrl(imageUrl, filename, title);
}

// Analysis function that loads image from URL to get real dimensions
function analyzeImageFromUrl(imageUrl, filename, title) {
    // Set up the modal with image info
    const modal = document.getElementById('analysisModal');
    const analysisImage = document.getElementById('analysisImage');
    const analysisImageTitle = document.getElementById('analysisImageTitle');
    
    // Set image and title
    analysisImage.src = imageUrl;
    analysisImageTitle.textContent = title || filename;
    
    // Create a new image to load and get real dimensions
    const img = new Image();
    img.onload = function() {
        const actualWidth = this.naturalWidth;
        const actualHeight = this.naturalHeight;
        
        console.log('Real image dimensions:', { filename, actualWidth, actualHeight });
        
        // Calculate basic stats using ACTUAL dimensions
        const aspectRatio = getAspectRatio(actualWidth, actualHeight);
        const totalPixels = actualWidth * actualHeight;
        const megaPixels = (totalPixels / 1000000).toFixed(2);
        
        // Update stats display with ACTUAL dimensions
        document.getElementById('analysisAspectRatio').textContent = aspectRatio;
        document.getElementById('analysisDimensions').textContent = `${actualWidth} x ${actualHeight} px`;
        document.getElementById('analysisMegapixels').textContent = `${megaPixels} MP`;
        
        // Calculate print suitability using ACTUAL dimensions
        const printResults = document.getElementById('printAnalysisResults');
        printResults.innerHTML = '';
        
        const isImagePortrait = actualHeight > actualWidth;
        
        printSizes.forEach(size => {
            let printWidth, printHeight;
            
            if (isImagePortrait) {
                printWidth = Math.min(size.width, size.height);
                printHeight = Math.max(size.width, size.height);
            } else {
                printWidth = Math.max(size.width, size.height);
                printHeight = Math.min(size.width, size.height);
            }
            
            // Use ACTUAL image dimensions for DPI calculation
            const dpiHorizontal = actualWidth / printWidth;
            const dpiVertical = actualHeight / printHeight;
            const effectiveDPI = Math.floor(Math.min(dpiHorizontal, dpiVertical));
            
            const quality = getQualityRating(effectiveDPI);
            const sizeRatio = getAspectRatio(Math.round(printWidth * 10), Math.round(printHeight * 10));
            
            const ratioMatchText = aspectRatio === sizeRatio ? 
                '<span class="match-perfect">Perfect Match</span>' : 
                '<span class="match-crop">Requires Cropping</span>';
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="size-name">${size.name}</td>
                <td class="aspect-match">${ratioMatchText}</td>
                <td class="dpi-value">${effectiveDPI} DPI</td>
                <td class="quality-rating">
                    <span class="quality-badge ${quality.class}">${quality.text}</span>
                </td>
            `;
            
            printResults.appendChild(row);
        });
        
        // Show the modal with a slight delay to ensure it appears on top
        setTimeout(() => {
            modal.style.display = 'block';
            modal.focus(); // Bring modal to front
        }, 500);
    };
    
    // Handle image load error
    img.onerror = function() {
        console.error('Failed to load image:', imageUrl);
        alert('Failed to load image for analysis. Please check if the image exists.');
    };
    
    // Start loading the image
    img.src = imageUrl;
}

// Modal close functionality
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('analysisModal');
    const closeBtn = document.querySelector('.analysis-close');
    
    // Close modal when clicking the X
    if (closeBtn) {
        closeBtn.onclick = function() {
            modal.style.display = 'none';
        };
    }
    
    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && modal.style.display === 'block') {
            modal.style.display = 'none';
        }
    });
});
