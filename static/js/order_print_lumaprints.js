/**
 * Lumaprints Order Interface JavaScript
 * Based on official Lumaprints API documentation
 */

class LumaprintsOrderInterface {
    constructor() {
        this.currentCategory = null;
        this.currentProduct = null;
        this.currentSize = null;
        this.cart = [];
        this.currentView = 'products';
        
        // Lumaprints API product data based on official documentation
        this.productData = {
            // Canvas Category (ID: 101)
            101: {
                name: 'Canvas',
                subcategories: [
                    { id: 101001, name: '0.75in Stretched Canvas', minWidth: 8, maxWidth: 30, minHeight: 10, maxHeight: 30, dpi: 200 },
                    { id: 101002, name: '1.25in Stretched Canvas', minWidth: 8, maxWidth: 45, minHeight: 10, maxHeight: 60, dpi: 200 },
                    { id: 101003, name: '1.50in Stretched Canvas', minWidth: 8, maxWidth: 45, minHeight: 10, maxHeight: 60, dpi: 200 },
                    { id: 101005, name: 'Rolled Canvas', minWidth: 8, maxWidth: 45, minHeight: 10, maxHeight: 60, dpi: 200 }
                ]
            },
            // Framed Canvas Category (ID: 102)
            102: {
                name: 'Framed Canvas',
                subcategories: [
                    // Frame depth options - user selects depth first, then colors
                    { 
                        id: 102001, 
                        name: '0.75" Framed Canvas', 
                        minWidth: 8, maxWidth: 30, minHeight: 10, maxHeight: 40, dpi: 200,
                        frameColors: [
                            { name: '1.625inx1.375 Black Frame', optionId: 12 },
                            { name: '1.25x0.875 White Frame', optionId: 13 },
                            { name: '1.25x0.875 Oak Frame', optionId: 14 },
                            { name: '1.25x0.875 Maple Frame', optionId: 15 },
                            { name: '1.25x0.875 Black Frame', optionId: 16 },
                            { name: '0.875x1.125 Natural Wood Frame', optionId: 17 },
                            { name: '0.875x1.125 Maple Frame', optionId: 18 },
                            { name: '0.875x1.125 Gold Frame', optionId: 19 },
                            { name: '0.875x1.125 Espresso Frame', optionId: 20 },
                            { name: '0.875x0.875 Oak Frame', optionId: 21 },
                            { name: '0.875x0.875 White Frame', optionId: 22 },
                            { name: '0.875x0.875 Black Frame', optionId: 23 },
                            { name: '0.74x1.125 White Frame', optionId: 24 },
                            { name: '0.75inx1.125 Black Frame', optionId: 25 },
                            { name: '0.75in Gold Plein Air Frame', optionId: 26 },
                            { name: '0.75in Vintage Collection Copper Frame', optionId: 27 },
                            { name: '0.75 Concerto Black w/Gold Frame', optionId: 28 },
                            { name: '0.75in Barnwood - Driftwood White Frame', optionId: 29 },
                            { name: '0.75 Barnwood - Driftwood Gray Frame', optionId: 30 },
                            { name: '0.75in Gold Floating Frame', optionId: 31 },
                            { name: '0.75in Silver Floating Frame', optionId: 32 },
                            { name: '0.75in White Floating Frame', optionId: 33 },
                            { name: '0.75in Black Floating Frame', optionId: 34 }
                        ]
                    },
                    { 
                        id: 102002, 
                        name: '1.25" Framed Canvas', 
                        minWidth: 8, maxWidth: 48, minHeight: 10, maxHeight: 48, dpi: 200,
                        frameColors: [
                            { name: '1.25in Walnut Floating Frame', optionId: 35 },
                            { name: '1.25in Oak Floating Frame', optionId: 36 },
                            { name: '1.25in Black Floating Frame', optionId: 37 }
                        ]
                    },
                    { 
                        id: 102003, 
                        name: '1.50" Framed Canvas', 
                        minWidth: 8, maxWidth: 48, minHeight: 10, maxHeight: 48, dpi: 200,
                        frameColors: [
                            { name: '1.50in Maple Wood Floating Frame', optionId: 38 },
                            { name: '1.50in Espresso Floating Frame', optionId: 39 },
                            { name: '1.50in Natural Wood Floating Frame', optionId: 40 },
                            { name: '1.50in Oak Floating Frame', optionId: 41 },
                            { name: '1.50in Gold Floating Frame', optionId: 42 },
                            { name: '1.50in Silver Floating Frame', optionId: 43 },
                            { name: '1.50in White Floating Frame', optionId: 44 },
                            { name: '1.50in Black Floating Frame', optionId: 45 }
                        ]
                    }
                ]
            },
            // Fine Art Paper Category (ID: 103)
            103: {
                name: 'Fine Art Paper',
                subcategories: [
                    { id: 103001, name: 'Archival Matte Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 103002, name: 'Hot Press Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 103003, name: 'Cold Press Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 103005, name: 'Semi-Glossy Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 103006, name: 'Metallic Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 103007, name: 'Glossy Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 103008, name: 'Semi-Matte Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 103009, name: 'Somerset Velvet Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 }
                ]
            },
            // Foam-mounted Print Category (ID: 104) - Based on Fine Art Paper products
            104: {
                name: 'Foam-mounted Print',
                subcategories: [
                    { id: 104001, name: 'Foam-mounted Archival Matte Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 104002, name: 'Foam-mounted Hot Press Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 104003, name: 'Foam-mounted Cold Press Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 104005, name: 'Foam-mounted Semi-Glossy Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 104006, name: 'Foam-mounted Metallic Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 104007, name: 'Foam-mounted Glossy Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 104009, name: 'Foam-mounted Somerset Velvet Fine Art Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 104010, name: 'Foam-mounted Canvas', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 },
                    { id: 104011, name: 'Foam-mounted Photo Paper', minWidth: 5, maxWidth: 44, minHeight: 7, maxHeight: 60, dpi: 300 }
                ]
            },
            // Framed Fine Art Paper Category (ID: 105) - Exactly 25 frame options
            105: {
                name: 'Framed Fine Art Paper',
                subcategories: [
                    // 0.875in Frame Options - 8 Colors
                    { id: 105001, name: '0.875in Black Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105002, name: '0.875in White Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105003, name: '0.875in Oak Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105004, name: '0.875in Walnut Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105008, name: '0.875in Espresso Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105009, name: '0.875in Silver Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105010, name: '0.875in Gold Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105011, name: '0.875in Natural Wood Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    
                    // 1.25in Frame Options - 9 Colors  
                    { id: 105005, name: '1.25in Black Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105006, name: '1.25in White Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105007, name: '1.25in Oak Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105014, name: '1.25in Walnut Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105015, name: '1.25in Espresso Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105016, name: '1.25in Silver Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105017, name: '1.25in Gold Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105018, name: '1.25in Natural Wood Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105019, name: '1.25in Maple Wood Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    
                    // 1.75in Frame Options - 8 Colors
                    { id: 105021, name: '1.75in Black Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105022, name: '1.75in White Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105023, name: '1.75in Oak Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105024, name: '1.75in Walnut Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105025, name: '1.75in Espresso Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105026, name: '1.75in Silver Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105027, name: '1.75in Gold Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 },
                    { id: 105028, name: '1.75in Natural Wood Frame', minWidth: 5, maxWidth: 36, minHeight: 7, maxHeight: 48, dpi: 300 }
                ]
            },
            // Metal Category (ID: 106)
            106: {
                name: 'Metal',
                subcategories: [
                    { id: 106001, name: 'Glossy White Metal Print', minWidth: 5, maxWidth: 48, minHeight: 5, maxHeight: 96, dpi: 300 },
                    { id: 106001, name: 'Glossy Silver Metal Print', minWidth: 5, maxWidth: 48, minHeight: 5, maxHeight: 96, dpi: 300 }
                ]
            },
            // Peel and Stick Category (ID: 107)
            107: {
                name: 'Peel and Stick',
                subcategories: [
                    { id: 107001, name: 'Peel and Stick Vinyl', minWidth: 5, maxWidth: 48, minHeight: 5, maxHeight: 96, dpi: 300 },
                    { id: 107002, name: 'Peel and Stick Fabric', minWidth: 5, maxWidth: 48, minHeight: 5, maxHeight: 96, dpi: 300 }
                ]
            }
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.createMobileDropdowns(); // Create mobile dropdowns if on mobile
        this.loadCategory(101); // Start with Canvas category
    }
    
    createMobileDropdowns() {
        // Check if we're on mobile (screen width < 768px)
        if (window.innerWidth <= 768) {
            this.createMobileInterface();
        }
    }
    
    createMobileInterface() {
        const categoriesSection = document.querySelector('.categories-section');
        if (!categoriesSection) return;
        
        // Clear any existing mobile dropdowns
        const existingDropdowns = categoriesSection.querySelectorAll('.mobile-dropdown');
        existingDropdowns.forEach(dropdown => dropdown.remove());
        
        // Create container for all mobile dropdowns
        const mobileContainer = document.createElement('div');
        mobileContainer.className = 'mobile-dropdowns-container';
        
        // Dropdown 1: Product Type
        const productTypeDropdown = document.createElement('select');
        productTypeDropdown.className = 'mobile-category-dropdown mobile-dropdown';
        productTypeDropdown.id = 'mobileProductType';
        productTypeDropdown.innerHTML = `
            <option value="">Select Product Type...</option>
            <option value="101">Canvas</option>
            <option value="102">Framed Canvas</option>
            <option value="103">Fine Art Paper</option>
            <option value="104">Foam-mounted Print</option>
            <option value="105">Framed Fine Art Paper</option>
            <option value="106">Metal</option>
            <option value="107">Peel and Stick</option>
        `;
        
        // Dropdown 2: Variant
        const variantDropdown = document.createElement('select');
        variantDropdown.className = 'mobile-products-dropdown mobile-dropdown';
        variantDropdown.id = 'mobileVariant';
        variantDropdown.innerHTML = '<option value="">Select Variant...</option>';
        variantDropdown.style.display = 'none';
        
        // Dropdown 3: Variant #2 (if required)
        const variant2Dropdown = document.createElement('select');
        variant2Dropdown.className = 'mobile-sizes-dropdown mobile-dropdown';
        variant2Dropdown.id = 'mobileVariant2';
        variant2Dropdown.innerHTML = '<option value="">Select Option...</option>';
        variant2Dropdown.style.display = 'none';
        
        // Add dropdowns to container
        mobileContainer.appendChild(productTypeDropdown);
        mobileContainer.appendChild(variantDropdown);
        mobileContainer.appendChild(variant2Dropdown);
        
        // Add container to categories section
        categoriesSection.appendChild(mobileContainer);
        
        // Add event listeners
        this.setupMobileDropdownListeners();
    }
    
    setupMobileDropdownListeners() {
        const productTypeDropdown = document.getElementById('mobileProductType');
        const variantDropdown = document.getElementById('mobileVariant');
        const variant2Dropdown = document.getElementById('mobileVariant2');
        
        // Product Type selection
        productTypeDropdown.addEventListener('change', (e) => {
            const categoryId = parseInt(e.target.value);
            if (categoryId) {
                this.loadMobileVariants(categoryId);
            } else {
                variantDropdown.style.display = 'none';
                variant2Dropdown.style.display = 'none';
            }
        });
        
        // Variant selection
        variantDropdown.addEventListener('change', (e) => {
            const variantId = parseInt(e.target.value);
            if (variantId) {
                this.handleMobileVariantSelection(variantId);
            } else {
                variant2Dropdown.style.display = 'none';
            }
        });
        
        // Variant #2 selection
        variant2Dropdown.addEventListener('change', (e) => {
            const variant2Id = parseInt(e.target.value);
            if (variant2Id) {
                this.handleMobileVariant2Selection(variant2Id);
            }
        });
    }
    
    loadMobileVariants(categoryId) {
        const variantDropdown = document.getElementById('mobileVariant');
        const variant2Dropdown = document.getElementById('mobileVariant2');
        
        // Get category data
        const categoryData = this.productData[categoryId];
        if (!categoryData) return;
        
        // Clear and populate variant dropdown
        variantDropdown.innerHTML = '<option value="">Select Variant...</option>';
        categoryData.subcategories.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = product.name;
            variantDropdown.appendChild(option);
        });
        
        // Show variant dropdown, hide variant2
        variantDropdown.style.display = 'block';
        variant2Dropdown.style.display = 'none';
    }
    
    handleMobileVariantSelection(variantId) {
        const variant2Dropdown = document.getElementById('mobileVariant2');
        
        // Find the selected variant
        let selectedVariant = null;
        for (const categoryData of Object.values(this.productData)) {
            selectedVariant = categoryData.subcategories.find(p => p.id === variantId);
            if (selectedVariant) break;
        }
        
        if (!selectedVariant) return;
        
        // Check if this variant has frame colors (requires variant #2)
        if (selectedVariant.frameColors && selectedVariant.frameColors.length > 0) {
            // Show variant #2 dropdown with frame colors
            variant2Dropdown.innerHTML = '<option value="">Select Frame Color...</option>';
            selectedVariant.frameColors.forEach(frame => {
                const option = document.createElement('option');
                option.value = frame.optionId;
                option.textContent = frame.name;
                variant2Dropdown.appendChild(option);
            });
            variant2Dropdown.style.display = 'block';
        } else {
            // No variant #2 needed, proceed directly
            variant2Dropdown.style.display = 'none';
            this.proceedToMobileOrdering(selectedVariant);
        }
    }
    
    handleMobileVariant2Selection(variant2Id) {
        // Handle final selection with both variants
        console.log('Selected variant #2:', variant2Id);
        // Proceed to ordering with both variants selected
    }
    
    proceedToMobileOrdering(product, frameOptionId = null) {
        console.log('Proceeding to mobile ordering:', product.name);
        if (frameOptionId) {
            console.log('With frame option:', frameOptionId);
        }
        // This is where we'll integrate with the ordering system
    }
    
    setupEventListeners() {
        // Category selection
        document.querySelectorAll('.category-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const categoryId = parseInt(e.currentTarget.dataset.categoryId);
                this.selectCategory(categoryId);
            });
        });
        
        // Back buttons
        document.getElementById('backToProducts')?.addEventListener('click', () => {
            this.showView('products');
        });
        
        document.getElementById('backToSizes')?.addEventListener('click', () => {
            this.showView('sizes');
        });
        
        // Quantity controls
        document.getElementById('qtyMinus')?.addEventListener('click', () => {
            this.adjustQuantity(-1);
        });
        
        document.getElementById('qtyPlus')?.addEventListener('click', () => {
            this.adjustQuantity(1);
        });
        
        document.getElementById('quantity')?.addEventListener('change', (e) => {
            this.updateItemTotal();
        });
        
        // Action buttons
        document.getElementById('addToCartBtn')?.addEventListener('click', () => {
            this.addToCart();
        });
        
        document.getElementById('continueShoppingBtn')?.addEventListener('click', () => {
            this.continueShopping();
        });
        
        document.getElementById('checkoutBtn')?.addEventListener('click', () => {
            this.proceedToCheckout();
        });
    }
    
    selectCategory(categoryId) {
        // Update UI
        document.querySelectorAll('.category-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-category-id="${categoryId}"]`).classList.add('active');
        
        // Load category products
        this.loadCategory(categoryId);
        this.showView('products');
    }
    
    async loadCategory(categoryId) {
        try {
            // Set current category
            this.currentCategory = categoryId;
            
            // Use local productData instead of API call
            const categoryData = this.productData[categoryId];
            
            if (categoryData) {
                // Get category name
                const categoryName = this.getCategoryName(categoryId);
                
                // Update category title
                document.getElementById('categoryTitle').textContent = categoryName;
                
                // Load products from local data
                this.loadProducts(categoryData.subcategories);
            } else {
                console.error('Category not found in productData:', categoryId);
            }
        } catch (error) {
            console.error('Error loading category:', error);
        }
    }
    
    getCategoryName(categoryId) {
        const categoryNames = {
            101: 'Canvas',
            102: 'Framed Canvas',
            103: 'Fine Art Paper',
            104: 'Foam-mounted Print',
            105: 'Framed Fine Art Paper',
            106: 'Metal',
            107: 'Peel and Stick'
        };
        return categoryNames[categoryId] || 'Unknown Category';
    }
    
    loadProducts(subcategories) {
        const grid = document.getElementById('productsGrid');
        grid.innerHTML = '';
        
        // Desktop: Create product cards
        subcategories.forEach(product => {
            const productCard = this.createProductCard(product);
            grid.appendChild(productCard);
        });
        
        // Mobile dropdowns are handled separately in createMobileInterface()
    }
    
    createProductCard(product) {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.dataset.productId = product.id;
        
        // Generate product key for thumbnail lookup
        const productKey = this.generateProductKey(product.name);
        const thumbnailUrl = `/static/product-thumbnails/${productKey}.jpg`;
        
        card.innerHTML = `
            <div class="product-thumbnail">
                <img src="${thumbnailUrl}" alt="${product.name}" 
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                     style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;">
                <span style="display: none;">Product Preview</span>
            </div>
            <div class="product-name">${product.name}</div>
            <div class="product-description">
                Size range: ${product.minWidth}"×${product.minHeight}" to ${product.maxWidth}"×${product.maxHeight}"<br>
                Required DPI: ${product.dpi}
            </div>
        `;
        
        card.addEventListener('click', () => {
            this.selectProduct(product);
        });
        
        return card;
    }
    
    generateProductKey(productName) {
        // Match the exact format used by the admin system
        // Convert product name to the same format as admin uploads
        const productType = 'canvas';
        const variantName = productName.toLowerCase().replace(/[^a-zA-Z0-9]/g, '_');
        return `${productType}_${variantName}`;
    }
    
    generateFrameProductKey(productName, frameName) {
        // Match the admin interface naming convention exactly
        // Admin format: framed-canvas_0.75in_framed_canvas_frame_name
        const productType = 'framed-canvas';
        const productVariant = productName.toLowerCase().replace(/[^a-zA-Z0-9]/g, '_');
        const frameOption = frameName.toLowerCase().replace(/[^a-zA-Z0-9]/g, '_');
        return `${productType}_${productVariant}_${frameOption}`;
    }
    
    generateOtherProductKey(categoryName, productName) {
        // For other product types (Fine Art Paper, Metal, etc.)
        const categoryKey = categoryName.toLowerCase().replace(/[^a-zA-Z0-9]/g, '-');
        return `${categoryKey}_${productName}`.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
    }
    
    selectProduct(product) {
        this.currentProduct = product;
        
        // Update UI
        document.querySelectorAll('.product-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-product-id="${product.id}"]`).classList.add('selected');
        
        // Update product title
        document.getElementById('productTitle').textContent = product.name;
        
        // Check if this is a Framed Canvas product (category 102) that needs frame options
        if (this.currentCategory === 102) {
            this.loadFrameOptions(product);
        } else {
            // Load sizes directly for products without frame options
            this.loadSizes(product);
            this.showView('sizes');
        }
    }

    async loadFrameOptions(product) {
        try {
            const response = await fetch(`/api/lumaprints/options/${product.subcategoryId}`);
            const data = await response.json();
            
            if (data.success && data.options.length > 0) {
                this.showFrameColorSelection(product, data.options);
            } else {
                // No frame options available, proceed to sizes
                this.loadSizes(product);
                this.showView('sizes');
            }
        } catch (error) {
            console.error('Error loading frame options:', error);
            // Fallback to sizes if API fails
            this.loadSizes(product);
            this.showView('sizes');
        }
    }

    showFrameColorSelection(product, frameOptions) {
        // Update the products grid to show frame color options
        const grid = document.getElementById('productsGrid');
        grid.innerHTML = '';
        
        // Update category title to show we're selecting frame colors
        document.getElementById('categoryTitle').textContent = product.name + ' - Choose Frame Color';
        
        frameOptions.forEach(option => {
            const colorCard = document.createElement('div');
            colorCard.className = 'product-card';
            colorCard.dataset.colorId = option.optionId;
            
            // Generate product key for frame color thumbnail
            const frameProductKey = this.generateFrameProductKey(product.name, option.name);
            const thumbnailUrl = `/static/product-thumbnails/${frameProductKey}.jpg`;
            
            colorCard.innerHTML = `
                <div class="product-thumbnail">
                    <img src="${thumbnailUrl}" alt="${option.name}" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                         style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;">
                    <span style="display: none;">Product Preview</span>
                </div>
                <div class="product-name">${option.name}</div>
                <div class="product-description">
                    Size range: ${product.minWidth}"×${product.minHeight}" to ${product.maxWidth}"×${product.maxHeight}"<br>
                    Required DPI: ${product.dpi}
                </div>
            `;
            
            colorCard.addEventListener('click', () => {
                this.selectFrameColor(product, option);
            });
            
            grid.appendChild(colorCard);
        });
    }

    selectFrameColor(product, option) {
        // Create a new product object with the selected frame option
        this.currentProduct = {
            ...product,
            name: product.name + ' - ' + option.name,
            optionId: option.optionId,
            selectedOption: option
        };
        
        // Update UI
        document.querySelectorAll('.product-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-color-id="${option.optionId}"]`).classList.add('selected');
        
        // Update product title
        document.getElementById('productTitle').textContent = this.currentProduct.name;
        
        // Load sizes
        this.loadSizes(this.currentProduct);
        this.showView('sizes');
    }
    
    async loadSizes(product) {
        const grid = document.getElementById('sizesGrid');
        grid.innerHTML = '<div class="loading">Loading sizes...</div>';
        
        // Generate common sizes within the product's constraints
        const sizes = await this.generateSizes(product.minWidth, product.maxWidth, product.minHeight, product.maxHeight);
        
        grid.innerHTML = '';
        sizes.forEach(size => {
            const sizeCard = this.createSizeCard(size);
            grid.appendChild(sizeCard);
        });
    }
    
    async generateSizes(minW, maxW, minH, maxH) {
        const productName = this.currentProduct?.name || '';
        
        // Handle Canvas products with specific size data
        if (productName.includes('Canvas') && this.currentCategory === 101) {
            try {
                const response = await fetch('/correct_canvas_sizes.json');
                const canvasData = await response.json();
                
                // Find the matching product in canvas data
                let productSizes = [];
                
                if (productName.includes('0.75in Stretched Canvas')) {
                    productSizes = canvasData['0.75in Stretched Canvas']?.available_sizes || [];
                } else if (productName.includes('1.25in Stretched Canvas')) {
                    productSizes = canvasData['1.25in Stretched Canvas']?.available_sizes || [];
                } else if (productName.includes('1.50in Stretched Canvas')) {
                    productSizes = canvasData['1.50in Stretched Canvas']?.available_sizes || [];
                } else if (productName.includes('Rolled Canvas')) {
                    productSizes = canvasData['Rolled Canvas']?.available_sizes || [];
                }
                
                // Convert canvas data to size objects with markup
                const sizes = productSizes.map(item => {
                    return {
                        width: item.width,
                        height: item.height,
                        price: item.wholesale_price * 2.5 // 150% markup
                    };
                }).filter(size => 
                    size.width >= minW && size.width <= maxW && 
                    size.height >= minH && size.height <= maxH
                );
                
                if (sizes.length > 0) return sizes;
                
            } catch (error) {
                console.error('Error loading canvas sizes data:', error);
            }
        }
        
        // Generate comprehensive sizes for Fine Art Paper, Foam-mounted Print, and other products
        // Based on actual Lumaprints catalog with 50+ size options
        const standardSizes = [
            // Small sizes
            { width: 5, height: 7, price: 15.99 },
            { width: 6, height: 8, price: 18.99 },
            { width: 8.5, height: 11, price: 22.99 },
            { width: 8, height: 10, price: 24.99 },
            { width: 8, height: 12, price: 29.99 },
            { width: 8, height: 16, price: 34.99 },
            { width: 9, height: 12, price: 32.99 },
            { width: 9, height: 16, price: 38.99 },
            { width: 10, height: 8, price: 28.99 },
            { width: 10, height: 10, price: 32.99 },
            { width: 10, height: 20, price: 54.99 },
            { width: 10, height: 30, price: 74.99 },
            { width: 10, height: 40, price: 94.99 },
            { width: 11, height: 14, price: 39.99 },
            { width: 11, height: 17, price: 44.99 },
            { width: 12, height: 12, price: 42.99 },
            { width: 12, height: 16, price: 49.99 },
            { width: 12, height: 18, price: 54.99 },
            { width: 12, height: 20, price: 59.99 },
            { width: 12, height: 24, price: 69.99 },
            { width: 12, height: 30, price: 84.99 },
            { width: 12, height: 36, price: 99.99 },
            { width: 14, height: 14, price: 54.99 },
            { width: 14, height: 18, price: 64.99 },
            { width: 15, height: 15, price: 59.99 },
            
            // Medium sizes
            { width: 16, height: 20, price: 79.99 },
            { width: 16, height: 24, price: 89.99 },
            { width: 16, height: 32, price: 119.99 },
            { width: 16, height: 40, price: 149.99 },
            { width: 18, height: 24, price: 99.99 },
            { width: 18, height: 27, price: 109.99 },
            { width: 18, height: 36, price: 139.99 },
            { width: 18, height: 48, price: 179.99 },
            { width: 18, height: 60, price: 219.99 },
            { width: 18, height: 72, price: 259.99 },
            { width: 20, height: 20, price: 109.99 },
            { width: 20, height: 24, price: 119.99 },
            { width: 20, height: 30, price: 139.99 },
            { width: 20, height: 40, price: 179.99 },
            { width: 20, height: 60, price: 249.99 },
            { width: 22, height: 28, price: 149.99 },
            { width: 24, height: 24, price: 139.99 },
            { width: 24, height: 30, price: 159.99 },
            { width: 24, height: 36, price: 189.99 },
            { width: 24, height: 48, price: 239.99 },
            { width: 24, height: 60, price: 299.99 },
            { width: 24, height: 72, price: 359.99 },
            
            // Large sizes
            { width: 30, height: 30, price: 219.99 },
            { width: 30, height: 40, price: 279.99 },
            { width: 30, height: 45, price: 309.99 },
            { width: 30, height: 60, price: 399.99 },
            { width: 32, height: 40, price: 299.99 },
            { width: 32, height: 42, price: 319.99 },
            { width: 32, height: 48, price: 359.99 },
            { width: 36, height: 48, price: 399.99 },
            { width: 40, height: 40, price: 379.99 },
            { width: 40, height: 60, price: 529.99 },
            { width: 44, height: 60, price: 579.99 }
        ];
        
        // Filter sizes based on product constraints
        return standardSizes.filter(size => 
            size.width >= minW && size.width <= maxW && 
            size.height >= minH && size.height <= maxH
        );
    }
    
    createSizeCard(size) {
        const card = document.createElement('div');
        card.className = 'size-card';
        card.dataset.width = size.width;
        card.dataset.height = size.height;
        card.dataset.price = size.price;
        
        card.innerHTML = `
            <div class="size-dimensions">${size.width}" × ${size.height}"</div>
            <div class="size-price">$${size.price.toFixed(2)}</div>
        `;
        
        card.addEventListener('click', () => {
            this.selectSize(size);
        });
        
        return card;
    }
    
    selectSize(size) {
        this.currentSize = size;
        
        // Update UI
        document.querySelectorAll('.size-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-width="${size.width}"][data-height="${size.height}"]`).classList.add('selected');
        
        // Update quantity view
        this.updateQuantityView();
        this.showView('quantity');
    }
    
    updateQuantityView() {
        const preview = document.getElementById('selectedItemPreview');
        preview.innerHTML = `
            <h3>${this.currentProduct.name}</h3>
            <p>Size: ${this.currentSize.width}" × ${this.currentSize.height}"</p>
            <p>Unit Price: $${this.currentSize.price.toFixed(2)}</p>
        `;
        
        document.getElementById('unitPrice').textContent = `$${this.currentSize.price.toFixed(2)}`;
        this.updateItemTotal();
    }
    
    adjustQuantity(delta) {
        const qtyInput = document.getElementById('quantity');
        const currentQty = parseInt(qtyInput.value);
        const newQty = Math.max(1, Math.min(99, currentQty + delta));
        qtyInput.value = newQty;
        this.updateItemTotal();
    }
    
    updateItemTotal() {
        const quantity = parseInt(document.getElementById('quantity').value);
        const total = this.currentSize.price * quantity;
        document.getElementById('itemTotal').textContent = `$${total.toFixed(2)}`;
    }
    
    addToCart() {
        const quantity = parseInt(document.getElementById('quantity').value);
        
        const cartItem = {
            id: Date.now(), // Simple ID generation
            categoryName: this.productData[this.currentCategory].name,
            productName: this.currentProduct.name,
            subcategoryId: this.currentProduct.id,
            width: this.currentSize.width,
            height: this.currentSize.height,
            quantity: quantity,
            unitPrice: this.currentSize.price,
            totalPrice: this.currentSize.price * quantity
        };
        
        this.cart.push(cartItem);
        this.updateCartDisplay();
        
        // Show success message or animation
        alert(`Added ${quantity}x ${this.currentProduct.name} (${this.currentSize.width}"×${this.currentSize.height}") to your order!`);
    }
    
    updateCartDisplay() {
        const cartItems = document.getElementById('cartItems');
        const cartTotal = document.getElementById('cartTotal');
        const checkoutBtn = document.getElementById('checkoutBtn');
        
        if (this.cart.length === 0) {
            cartItems.innerHTML = '<p class="cart-empty">No items added yet</p>';
            cartTotal.style.display = 'none';
            checkoutBtn.style.display = 'none';
            return;
        }
        
        // Show cart items
        cartItems.innerHTML = this.cart.map(item => `
            <div class="cart-item">
                <div class="cart-item-name">${item.productName}</div>
                <div class="cart-item-details">
                    ${item.width}"×${item.height}" × ${item.quantity} = $${item.totalPrice.toFixed(2)}
                </div>
            </div>
        `).join('');
        
        // Calculate and show total
        const subtotal = this.cart.reduce((sum, item) => sum + item.totalPrice, 0);
        document.getElementById('subtotalAmount').textContent = `$${subtotal.toFixed(2)}`;
        
        cartTotal.style.display = 'block';
        checkoutBtn.style.display = 'block';
    }
    
    continueShopping() {
        // Reset quantity to 1
        document.getElementById('quantity').value = 1;
        
        // Go back to products view
        this.showView('products');
    }
    
    proceedToCheckout() {
        // Refresh cart from localStorage to ensure we have the latest data
        const savedCart = localStorage.getItem('lumaprintsCart');
        if (savedCart) {
            this.cart = JSON.parse(savedCart);
        }
        
        // Double-check cart contents
        if (this.cart.length === 0) {
            console.log('Cart is empty, refreshing cart display');
            this.updateCartDisplay();
            // Instead of showing alert, just return - let the checkout page handle empty cart
            return;
        }

        // Save cart to localStorage for the checkout page
        localStorage.setItem('lumaprintsCart', JSON.stringify(this.cart));
        
        // Save current image ID for order processing
        localStorage.setItem('currentImageId', window.location.pathname.split('/').pop());
        
        // Redirect to professional checkout page
        window.location.href = '/checkout';
    }
    
    async collectCustomerInfo() {
        // Simple prompt-based customer info collection
        // In a real implementation, you'd show a proper form
        const firstName = prompt('Enter your first name:');
        if (!firstName) return null;
        
        const lastName = prompt('Enter your last name:');
        if (!lastName) return null;
        
        const email = prompt('Enter your email address:');
        if (!email) return null;
        
        const phone = prompt('Enter your phone number (optional):') || '';
        
        const address1 = prompt('Enter your street address:');
        if (!address1) return null;
        
        const city = prompt('Enter your city:');
        if (!city) return null;
        
        const state = prompt('Enter your state (2-letter code):');
        if (!state) return null;
        
        const postalCode = prompt('Enter your ZIP/postal code:');
        if (!postalCode) return null;
        
        const country = prompt('Enter your country (2-letter code, default: US):') || 'US';
        
        return {
            customer: {
                firstName,
                lastName,
                email,
                phone
            },
            shipping: {
                firstName,
                lastName,
                address1,
                address2: '',
                city,
                state,
                postalCode,
                country
            }
        };
    }
    
    showView(viewName) {
        this.currentView = viewName;
        
        // Hide all views
        document.querySelectorAll('.view-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        // Show selected view
        const viewMap = {
            'products': 'productsView',
            'sizes': 'sizesView',
            'quantity': 'quantityView'
        };
        
        document.getElementById(viewMap[viewName]).classList.add('active');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.orderInterface = new LumaprintsOrderInterface();
});

// Also initialize immediately if DOM is already ready
if (document.readyState === 'loading') {
    // DOM hasn't finished loading yet
    document.addEventListener('DOMContentLoaded', () => {
        window.orderInterface = new LumaprintsOrderInterface();
    });
} else {
    // DOM is already ready
    window.orderInterface = new LumaprintsOrderInterface();
}
