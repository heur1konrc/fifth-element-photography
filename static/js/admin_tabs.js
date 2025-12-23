// Admin Tabs JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.admin-tab-button');
    const tabContents = document.querySelectorAll('.admin-tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            document.getElementById(`tab-${targetTab}`).classList.add('active');
            
            // Clear URL parameters when switching to Shopify tab
            if (targetTab === 'shopify') {
                // Remove search, gallery, sort, and page parameters from URL
                const url = new URL(window.location);
                url.searchParams.delete('search');
                url.searchParams.delete('gallery');
                url.searchParams.delete('sort');
                url.searchParams.delete('page');
                window.history.replaceState({}, '', url);
            }
            
            // Store active tab in localStorage for persistence
            localStorage.setItem('activeAdminTab', targetTab);
        });
    });
    
    // Restore last active tab from localStorage
    const savedTab = localStorage.getItem('activeAdminTab');
    if (savedTab) {
        const savedButton = document.querySelector(`[data-tab="${savedTab}"]`);
        if (savedButton) {
            savedButton.click();
        }
    }
});
