/**
 * DYNAMIC PRICING FORM - SIMPLE & EFFICIENT
 * Connects to database API to populate form and calculate prices
 */

let currentConfig = {
    subcategoryId: null,
    optionId: null,
    size: null,
    quantity: 1,
    price: 0
};

// Load categories on page load
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('productCategory').addEventListener('change', onCategoryChange);
    document.getElementById('subcategory').addEventListener('change', onSubcategoryChange);
    document.getElementById('productSize').addEventListener('change', onSizeChange);
    document.getElementById('quantity').addEventListener('change', updateJSON);
    document.getElementById('copyButton').addEventListener('click', copyToClipboard);
}

async function loadCategories() {
    try {
        const response = await fetch('/api/products/categories');
        const categories = await response.json();
        
        const select = document.getElementById('productCategory');
        select.innerHTML = '<option value="">-- Choose a Category --</option>';
        
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function onCategoryChange(e) {
    const category = e.target.value;
    if (!category) {
        document.getElementById('subcategoryGroup').classList.add('hidden');
        return;
    }
    
    try {
        const response = await fetch(`/api/products/subcategories/${encodeURIComponent(category)}`);
        const products = await response.json();
        
        const select = document.getElementById('subcategory');
        select.innerHTML = '<option value="">-- Choose Product --</option>';
        
        products.forEach(product => {
            const option = document.createElement('option');
            option.value = JSON.stringify({
                subcategoryId: product.subcategory_id, 
                optionId: product.option_id
            });
            option.textContent = product.name;
            select.appendChild(option);
        });
        
        document.getElementById('subcategoryGroup').classList.remove('hidden');
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

async function onSubcategoryChange(e) {
    const value = e.target.value;
    if (!value) return;
    
    const config = JSON.parse(value);
    currentConfig.subcategoryId = config.subcategoryId;
    currentConfig.optionId = config.optionId;
    
    // Load sizes for this subcategory/option
    try {
        const url = `/api/products/sizes?subcategory_id=${config.subcategoryId}&option_id=${config.optionId}`;
        const response = await fetch(url);
        const sizes = await response.json();
        
        const select = document.getElementById('productSize');
        select.innerHTML = '<option value="">-- Select Size --</option>';
        
        sizes.forEach(item => {
            const option = document.createElement('option');
            option.value = item.size;
            option.textContent = `${item.size}" - $${item.price.toFixed(2)}`;
            option.dataset.price = item.price;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading sizes:', error);
    }
}

function onSizeChange(e) {
    const size = e.target.value;
    if (!size) return;
    
    const selectedOption = e.target.options[e.target.selectedIndex];
    const price = parseFloat(selectedOption.dataset.price);
    
    currentConfig.size = size;
    currentConfig.price = price;
    
    updateJSON();
}

function updateJSON() {
    const quantity = parseInt(document.getElementById('quantity').value) || 1;
    currentConfig.quantity = quantity;
    
    if (!currentConfig.subcategoryId || !currentConfig.size) {
        document.getElementById('jsonOutput').textContent = '{\n    // Select product and size first\n}';
        return;
    }
    
    // Parse size (e.g., "8x10" -> width: 8, height: 10)
    const [width, height] = currentConfig.size.split('x').map(Number);
    
    const payload = {
        subcategoryId: currentConfig.subcategoryId,
        quantity: currentConfig.quantity,
        size: {
            width: width,
            height: height
        },
        options: {}
    };
    
    // Add frame option if present
    if (currentConfig.optionId) {
        // Determine option name based on subcategory
        let optionName = 'frame_style';
        if (currentConfig.subcategoryId === 102001) optionName = '0.75in_frame_style';
        else if (currentConfig.subcategoryId === 102002) optionName = '1.25in_frame_style';
        else if (currentConfig.subcategoryId === 102003) optionName = '1.50in_frame_style';
        
        payload.options[optionName] = currentConfig.optionId;
    }
    
    const totalPrice = (currentConfig.price * currentConfig.quantity).toFixed(2);
    
    const output = JSON.stringify(payload, null, 4);
    document.getElementById('jsonOutput').textContent = 
        `// Total Price: $${totalPrice}\n\n` + output;
}

function copyToClipboard() {
    const text = document.getElementById('jsonOutput').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const message = document.getElementById('copyMessage');
        message.style.opacity = '1';
        setTimeout(() => {
            message.style.opacity = '0';
        }, 2000);
    });
}

