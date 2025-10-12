// Image Analysis Modal Functionality

// Define common print sizes in inches (Width x Height)
const printSizes = [
    { name: "4 x 6", width: 6, height: 4, ratio: "3:2" },
    { name: "5 x 7", width: 7, height: 5, ratio: "7:5" },
    { name: "8 x 10", width: 10, height: 8, ratio: "5:4" },
    { name: "8.5 x 11 (Letter)", width: 11, height: 8.5, ratio: "22:17" },
    { name: "11 x 14", width: 14, height: 11, ratio: "14:11" },
    { name: "16 x 20", width: 20, height: 16, ratio: "5:4" },
    { name: "20 x 30", width: 30, height: 20, ratio: "3:2" },
    { name: "12 x 12 (Square)", width: 12, height: 12, ratio: "1:1" },
];

// Utility function to find the Greatest Common Divisor (GCD)
function calculateGCD(a, b) {
    return (b === 0) ? a : calculateGCD(b, a % b);
}

// Utility function to get the simplified aspect ratio string
function getAspectRatio(width, height) {
    if (width === 0 || height === 0) return "0:0";
    const divisor = calculateGCD(width, height);
    return `${width / divisor}:${height / divisor}`;
}

// Utility function to determine print quality rating based on DPI
function getQualityRating(dpi) {
    if (dpi >= 300) {
        return { text: "Excellent", class: "excellent" };
    } else if (dpi >= 150) {
        return { text: "Good", class: "good" };
    } else {
        return { text: "Poor", class: "poor" };
    }
}

// Main analysis function called from the admin buttons
function analyzeImage(filename, title, width, height) {
    // Set up the modal with image info
    const modal = document.getElementById('analysisModal');
    const analysisImage = document.getElementById('analysisImage');
    const analysisImageTitle = document.getElementById('analysisImageTitle');
    
    // Set image and title
    analysisImage.src = `/images/${filename}`;
    analysisImageTitle.textContent = title || filename;
    
    // Use the actual image dimensions passed from the template (not the displayed image size)
    const actualWidth = parseInt(width);
    const actualHeight = parseInt(height);
    
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
    
    // Show the modal
    modal.style.display = 'block';
}

// Close analysis modal
function closeAnalysisModal() {
    const modal = document.getElementById('analysisModal');
    modal.style.display = 'none';
}

// Close modal when clicking outside of it
window.addEventListener('click', function(event) {
    const modal = document.getElementById('analysisModal');
    if (event.target === modal) {
        closeAnalysisModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeAnalysisModal();
    }
});
