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
