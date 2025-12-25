/**
 * Force regenerate gallery image for a specific image file
 * This is useful when the REPLACE tool doesn't properly regenerate the gallery image
 */
function regenerateGalleryImage(filename) {
    if (!confirm(`Force regenerate gallery image for ${filename}?\n\nThis will delete and recreate the gallery-optimized version of this image.`)) {
        return;
    }
    
    console.log(`[REGENERATE] Starting gallery regeneration for: ${filename}`);
    
    fetch(`/api/regenerate-gallery-image/${encodeURIComponent(filename)}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`[REGENERATE] Success:`, data);
            alert(`✓ Gallery image regenerated successfully!\n\nFile: ${filename}\nSize: ${(data.file_size / 1024).toFixed(2)} KB`);
            
            // Force reload the page to show the new gallery image
            // Add timestamp to bust any browser cache
            window.location.href = window.location.href.split('?')[0] + '?t=' + Date.now();
        } else {
            console.error(`[REGENERATE] Error:`, data.error);
            alert(`✗ Failed to regenerate gallery image:\n\n${data.error}`);
        }
    })
    .catch(error => {
        console.error(`[REGENERATE] Network error:`, error);
        alert(`✗ Network error while regenerating gallery image:\n\n${error.message}`);
    });
}
