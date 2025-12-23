/**
 * Apply mapping to all unmapped products
 * Simply writes the filename to Column P and "Update" to Column S for ALL unmapped rows
 */
async function applyLumaprintsMapping() {
    // Collect all mapping rows
    const container = document.getElementById('lumaprints-mapping-rows');
    const rows = container.querySelectorAll('.mapping-row');
    
    // Validate and collect mappings
    const userMappings = [];
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const filenameInput = row.querySelector('.mapping-filename-input');
        
        const filename = filenameInput.value.trim();
        
        if (!filename) {
            showAlert(`Mapping #${i + 1}: Please enter an image filename`, 'warning');
            return;
        }
        
        userMappings.push({
            filename: filename
        });
    }
    
    if (userMappings.length === 0) {
        showAlert('Please add at least one mapping', 'warning');
        return;
    }
    
    // Build mappings for ALL unmapped products
    const mappings = [];
    
    for (const userMapping of userMappings) {
        for (const product of LumaprintsState.unmappedProducts) {
            mappings.push({
                row: product.row,
                data: {
                    product_handling: 'Update',
                    image_filename: userMapping.filename
                }
            });
        }
    }
    
    // Send mappings to backend
    try {
        const response = await fetch('/api/lumaprints/apply-mapping', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mappings: mappings })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(`✓ Successfully mapped ${data.mapped_count} products!`, 'success');
            
            // Move to step 3
            document.getElementById('lumaprints-step-2').style.display = 'none';
            document.getElementById('lumaprints-step-3').style.display = 'block';
            document.getElementById('lumaprints-mapped-count').textContent = data.mapped_count;
        } else {
            showAlert('Error applying mapping: ' + data.error, 'error');
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
    }
}
