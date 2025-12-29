/**
 * Excel Cleanup Tool
 * Standalone tool to sort and remove mapped rows from Lumaprints Excel exports
 */

function openExcelCleanupModal() {
    document.getElementById('excel-cleanup-modal').style.display = 'block';
    // Reset form
    document.getElementById('excel-cleanup-file-input').value = '';
    document.getElementById('excel-cleanup-status').innerHTML = '';
    document.getElementById('excel-cleanup-download-section').style.display = 'none';
}

function closeExcelCleanupModal() {
    document.getElementById('excel-cleanup-modal').style.display = 'none';
}

// Process Excel file
document.addEventListener('DOMContentLoaded', function() {
    const processBtn = document.getElementById('btn-excel-cleanup-process');
    if (processBtn) {
        processBtn.addEventListener('click', async function() {
            const fileInput = document.getElementById('excel-cleanup-file-input');
            const statusDiv = document.getElementById('excel-cleanup-status');
            const downloadSection = document.getElementById('excel-cleanup-download-section');
            
            if (!fileInput.files.length) {
                statusDiv.innerHTML = '<p style="color: red;">Please select a file first.</p>';
                return;
            }
            
            const file = fileInput.files[0];
            if (!file.name.endsWith('.xlsx')) {
                statusDiv.innerHTML = '<p style="color: red;">Please select an .xlsx file.</p>';
                return;
            }
            
            statusDiv.innerHTML = '<p style="color: blue;">Processing file...</p>';
            downloadSection.style.display = 'none';
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/api/excel-cleanup/process', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    statusDiv.innerHTML = `
                        <div style="color: green; padding: 15px; background: #e8f5e9; border-radius: 4px;">
                            <p><strong>✓ File processed successfully!</strong></p>
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                <li>Total rows before: ${data.total_rows_before}</li>
                                <li>Mapped rows deleted: ${data.deleted_count}</li>
                                <li>Unmapped rows remaining: ${data.total_rows_after}</li>
                            </ul>
                            <p style="margin-top: 10px;">Click "Download Cleaned File" below to get your processed file.</p>
                        </div>
                    `;
                    downloadSection.style.display = 'block';
                } else {
                    statusDiv.innerHTML = `<p style="color: red;">✗ Error: ${data.error}</p>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<p style="color: red;">✗ Error: ${error.message}</p>`;
            }
        });
    }
    
    // Download cleaned file
    const downloadBtn = document.getElementById('btn-excel-cleanup-download');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            window.location.href = '/api/excel-cleanup/download';
        });
    }
});

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('excel-cleanup-modal');
    if (event.target === modal) {
        closeExcelCleanupModal();
    }
});
