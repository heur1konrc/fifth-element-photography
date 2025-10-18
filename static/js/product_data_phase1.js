// Phase 1 Product Data - Stretched Canvas & Framed Canvas
// Based on Lumaprints pricing + 150% markup

const PHASE1_PRODUCTS = {
    // STRETCHED CANVAS PRODUCTS
    "stretched_canvas_075": {
        name: "0.75\" Stretched Canvas",
        subcategoryId: 101001,
        lumaprints_options: "1,4", // Image Wrap + Sawtooth Hanger
        type: "stretched_canvas",
        thickness: "0.75\"",
        sizes: {
            "8x12": {
                width: 8,
                height: 12,
                lumaprints_cost: 15.39,
                customer_price: 38.48, // 15.39 * 2.5
                title: "8×12 0.75\" Stretched Canvas"
            },
            "12x18": {
                width: 12,
                height: 18,
                lumaprints_cost: 21.18,
                customer_price: 52.95, // 21.18 * 2.5
                title: "12×18 0.75\" Stretched Canvas"
            },
            "16x24": {
                width: 16,
                height: 24,
                lumaprints_cost: 27.30,
                customer_price: 68.25, // 27.30 * 2.5
                title: "16×24 0.75\" Stretched Canvas"
            },
            "20x30": {
                width: 20,
                height: 30,
                lumaprints_cost: 42.54,
                customer_price: 106.35, // 42.54 * 2.5
                title: "20×30 0.75\" Stretched Canvas"
            }
        }
    },
    
    "stretched_canvas_125": {
        name: "1.25\" Stretched Canvas",
        subcategoryId: 101002,
        lumaprints_options: "1,4", // Image Wrap + Sawtooth Hanger
        type: "stretched_canvas",
        thickness: "1.25\"",
        sizes: {
            "8x12": {
                width: 8,
                height: 12,
                lumaprints_cost: 16.23,
                customer_price: 40.58, // 16.23 * 2.5
                title: "8×12 1.25\" Stretched Canvas"
            },
            "12x18": {
                width: 12,
                height: 18,
                lumaprints_cost: 22.50,
                customer_price: 56.25, // 22.50 * 2.5
                title: "12×18 1.25\" Stretched Canvas"
            },
            "16x24": {
                width: 16,
                height: 24,
                lumaprints_cost: 29.07,
                customer_price: 72.68, // 29.07 * 2.5
                title: "16×24 1.25\" Stretched Canvas"
            },
            "20x30": {
                width: 20,
                height: 30,
                lumaprints_cost: 45.20,
                customer_price: 113.00, // 45.20 * 2.5
                title: "20×30 1.25\" Stretched Canvas"
            }
        }
    },
    
    "stretched_canvas_150": {
        name: "1.50\" Stretched Canvas",
        subcategoryId: 101003,
        lumaprints_options: "1,4,9", // Image Wrap + Sawtooth Hanger + No Underlayer
        type: "stretched_canvas",
        thickness: "1.50\"",
        sizes: {
            "8x12": {
                width: 8,
                height: 12,
                lumaprints_cost: 18.76,
                customer_price: 46.90, // 18.76 * 2.5
                title: "8×12 1.50\" Stretched Canvas"
            },
            "12x18": {
                width: 12,
                height: 18,
                lumaprints_cost: 26.49,
                customer_price: 66.23, // 26.49 * 2.5
                title: "12×18 1.50\" Stretched Canvas"
            },
            "16x24": {
                width: 16,
                height: 24,
                lumaprints_cost: 34.39,
                customer_price: 85.98, // 34.39 * 2.5
                title: "16×24 1.50\" Stretched Canvas"
            },
            "20x30": {
                width: 20,
                height: 30,
                lumaprints_cost: 53.17,
                customer_price: 132.93, // 53.17 * 2.5
                title: "20×30 1.50\" Stretched Canvas"
            }
        }
    },
    
    // FRAMED CANVAS PRODUCTS
    "framed_canvas_075": {
        name: "0.75\" Framed Canvas",
        subcategoryId: 102001,
        lumaprints_options: "1,16,12", // Image Wrap + Hanging Wire + Black Frame
        type: "framed_canvas",
        thickness: "0.75\"",
        frame_style: "Black Floating Frame",
        sizes: {
            "8x12": {
                width: 8,
                height: 12,
                lumaprints_cost: 25.95, // Estimated based on framed pricing
                customer_price: 64.88, // 25.95 * 2.5
                title: "8×12 0.75\" Framed Canvas (Black Frame)"
            },
            "12x18": {
                width: 12,
                height: 18,
                lumaprints_cost: 35.50, // Estimated based on framed pricing
                customer_price: 88.75, // 35.50 * 2.5
                title: "12×18 0.75\" Framed Canvas (Black Frame)"
            },
            "16x24": {
                width: 16,
                height: 24,
                lumaprints_cost: 45.20, // Estimated based on framed pricing
                customer_price: 113.00, // 45.20 * 2.5
                title: "16×24 0.75\" Framed Canvas (Black Frame)"
            },
            "20x30": {
                width: 20,
                height: 30,
                lumaprints_cost: 65.80, // Estimated based on framed pricing
                customer_price: 164.50, // 65.80 * 2.5
                title: "20×30 0.75\" Framed Canvas (Black Frame)"
            }
        }
    },
    
    "framed_canvas_125": {
        name: "1.25\" Framed Canvas",
        subcategoryId: 102002,
        lumaprints_options: "1,28,27", // Image Wrap + Hanging Wire + Black Frame
        type: "framed_canvas",
        thickness: "1.25\"",
        frame_style: "Black Floating Frame",
        sizes: {
            "8x12": {
                width: 8,
                height: 12,
                lumaprints_cost: 28.50, // Estimated based on framed pricing
                customer_price: 71.25, // 28.50 * 2.5
                title: "8×12 1.25\" Framed Canvas (Black Frame)"
            },
            "12x18": {
                width: 12,
                height: 18,
                lumaprints_cost: 38.75, // Estimated based on framed pricing
                customer_price: 96.88, // 38.75 * 2.5
                title: "12×18 1.25\" Framed Canvas (Black Frame)"
            },
            "16x24": {
                width: 16,
                height: 24,
                lumaprints_cost: 49.20, // Estimated based on framed pricing
                customer_price: 123.00, // 49.20 * 2.5
                title: "16×24 1.25\" Framed Canvas (Black Frame)"
            },
            "20x30": {
                width: 20,
                height: 30,
                lumaprints_cost: 72.50, // Estimated based on framed pricing
                customer_price: 181.25, // 72.50 * 2.5
                title: "20×30 1.25\" Framed Canvas (Black Frame)"
            }
        }
    },
    
    "framed_canvas_150": {
        name: "1.50\" Framed Canvas",
        subcategoryId: 102003,
        lumaprints_options: "1,16,23,9", // Image Wrap + Hanging Wire + Black Frame + No Underlayer
        type: "framed_canvas",
        thickness: "1.50\"",
        frame_style: "Black Floating Frame",
        sizes: {
            "8x12": {
                width: 8,
                height: 12,
                lumaprints_cost: 31.25, // Estimated based on framed pricing
                customer_price: 78.13, // 31.25 * 2.5
                title: "8×12 1.50\" Framed Canvas (Black Frame)"
            },
            "12x18": {
                width: 12,
                height: 18,
                lumaprints_cost: 42.80, // Estimated based on framed pricing
                customer_price: 107.00, // 42.80 * 2.5
                title: "12×18 1.50\" Framed Canvas (Black Frame)"
            },
            "16x24": {
                width: 16,
                height: 24,
                lumaprints_cost: 54.50, // Estimated based on framed pricing
                customer_price: 136.25, // 54.50 * 2.5
                title: "16×24 1.50\" Framed Canvas (Black Frame)"
            },
            "20x30": {
                width: 20,
                height: 30,
                lumaprints_cost: 79.90, // Estimated based on framed pricing
                customer_price: 199.75, // 79.90 * 2.5
                title: "20×30 1.50\" Framed Canvas (Black Frame)"
            }
        }
    }
};

// Helper function to get all products as a flat array for dropdowns
function getAllProducts() {
    const products = [];
    
    Object.keys(PHASE1_PRODUCTS).forEach(productKey => {
        const product = PHASE1_PRODUCTS[productKey];
        
        Object.keys(product.sizes).forEach(sizeKey => {
            const size = product.sizes[sizeKey];
            
            products.push({
                id: `${productKey}_${sizeKey}`,
                productKey: productKey,
                sizeKey: sizeKey,
                subcategoryId: product.subcategoryId,
                lumaprints_options: product.lumaprints_options,
                width: size.width,
                height: size.height,
                lumaprints_cost: size.lumaprints_cost,
                customer_price: size.customer_price,
                title: size.title,
                type: product.type,
                thickness: product.thickness,
                frame_style: product.frame_style || null
            });
        });
    });
    
    return products;
}

// Helper function to get product by ID
function getProductById(productId) {
    const products = getAllProducts();
    return products.find(p => p.id === productId);
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PHASE1_PRODUCTS, getAllProducts, getProductById };
}
