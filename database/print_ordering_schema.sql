-- Fifth Element Photography - Print Ordering Database Schema
-- Version: Beta 0.1.0
-- Date: October 28, 2025

-- ============================================================================
-- PRODUCT CATALOG TABLES
-- ============================================================================

-- Categories (Product Types)
CREATE TABLE IF NOT EXISTS product_categories (
    category_id INTEGER PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subcategories (Specific Products)
CREATE TABLE IF NOT EXISTS product_subcategories (
    subcategory_id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    subcategory_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    max_width INTEGER,  -- Maximum width in inches (structural limit)
    max_height INTEGER, -- Maximum height in inches (structural limit)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id)
);

-- Options (Customization Choices)
CREATE TABLE IF NOT EXISTS product_options (
    option_id INTEGER PRIMARY KEY,
    option_group VARCHAR(100) NOT NULL, -- e.g., "Canvas Border", "Hanging Hardware"
    option_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subcategory-Option Relationships (which options apply to which products)
CREATE TABLE IF NOT EXISTS subcategory_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subcategory_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    is_required BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subcategory_id) REFERENCES product_subcategories(subcategory_id),
    FOREIGN KEY (option_id) REFERENCES product_options(option_id),
    UNIQUE(subcategory_id, option_id)
);

-- ============================================================================
-- ASPECT RATIO & SIZE MANAGEMENT
-- ============================================================================

-- Aspect Ratios
CREATE TABLE IF NOT EXISTS aspect_ratios (
    aspect_ratio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ratio_name VARCHAR(50) NOT NULL UNIQUE, -- e.g., "3:2", "1:1", "4:3"
    ratio_decimal DECIMAL(10,6) NOT NULL,   -- e.g., 1.5 for 3:2, 1.0 for 1:1
    display_name VARCHAR(50) NOT NULL,
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Print Sizes
CREATE TABLE IF NOT EXISTS print_sizes (
    size_id INTEGER PRIMARY KEY AUTOINCREMENT,
    aspect_ratio_id INTEGER NOT NULL,
    width INTEGER NOT NULL,  -- Width in inches
    height INTEGER NOT NULL, -- Height in inches
    size_name VARCHAR(50) NOT NULL, -- e.g., "12×18"
    display_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (aspect_ratio_id) REFERENCES aspect_ratios(aspect_ratio_id),
    UNIQUE(width, height)
);

-- ============================================================================
-- PRICING TABLES
-- ============================================================================

-- Base Pricing (Cost from Lumaprints)
CREATE TABLE IF NOT EXISTS base_pricing (
    pricing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subcategory_id INTEGER NOT NULL,
    size_id INTEGER NOT NULL,
    cost_price DECIMAL(10,2) NOT NULL, -- Wholesale cost from Lumaprints
    is_available BOOLEAN DEFAULT TRUE, -- FALSE for "n/a" sizes
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subcategory_id) REFERENCES product_subcategories(subcategory_id),
    FOREIGN KEY (size_id) REFERENCES print_sizes(size_id),
    UNIQUE(subcategory_id, size_id)
);

-- Option Pricing (Additional costs for options)
CREATE TABLE IF NOT EXISTS option_pricing (
    option_pricing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subcategory_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    size_id INTEGER, -- NULL means applies to all sizes
    cost_price DECIMAL(10,2) NOT NULL DEFAULT 0.00, -- Additional cost for this option
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subcategory_id) REFERENCES product_subcategories(subcategory_id),
    FOREIGN KEY (option_id) REFERENCES product_options(option_id),
    FOREIGN KEY (size_id) REFERENCES print_sizes(size_id),
    UNIQUE(subcategory_id, option_id, size_id)
);

-- Markup Rules (Profit margin management)
CREATE TABLE IF NOT EXISTS markup_rules (
    markup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(20) NOT NULL, -- 'global', 'category', 'subcategory', 'specific'
    category_id INTEGER,
    subcategory_id INTEGER,
    size_id INTEGER,
    markup_type VARCHAR(20) NOT NULL, -- 'percentage', 'fixed'
    markup_value DECIMAL(10,2) NOT NULL,
    priority INTEGER DEFAULT 0, -- Higher priority rules override lower
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id),
    FOREIGN KEY (subcategory_id) REFERENCES product_subcategories(subcategory_id),
    FOREIGN KEY (size_id) REFERENCES print_sizes(size_id)
);

-- Retail Pricing (Calculated: cost + markup)
-- This is a view, not a table, calculated on-the-fly
CREATE VIEW IF NOT EXISTS retail_pricing AS
SELECT 
    bp.pricing_id,
    bp.subcategory_id,
    bp.size_id,
    bp.cost_price,
    COALESCE(
        (SELECT markup_value 
         FROM markup_rules 
         WHERE rule_type = 'specific' 
           AND subcategory_id = bp.subcategory_id 
           AND size_id = bp.size_id 
           AND is_active = TRUE 
         ORDER BY priority DESC LIMIT 1),
        (SELECT markup_value 
         FROM markup_rules 
         WHERE rule_type = 'subcategory' 
           AND subcategory_id = bp.subcategory_id 
           AND is_active = TRUE 
         ORDER BY priority DESC LIMIT 1),
        (SELECT markup_value 
         FROM markup_rules 
         WHERE rule_type = 'category' 
           AND category_id = (SELECT category_id FROM product_subcategories WHERE subcategory_id = bp.subcategory_id)
           AND is_active = TRUE 
         ORDER BY priority DESC LIMIT 1),
        (SELECT markup_value 
         FROM markup_rules 
         WHERE rule_type = 'global' 
           AND is_active = TRUE 
         ORDER BY priority DESC LIMIT 1),
        0
    ) as markup_percentage,
    ROUND(bp.cost_price * (1 + COALESCE(
        (SELECT markup_value / 100.0 FROM markup_rules WHERE rule_type = 'specific' AND subcategory_id = bp.subcategory_id AND size_id = bp.size_id AND is_active = TRUE ORDER BY priority DESC LIMIT 1),
        (SELECT markup_value / 100.0 FROM markup_rules WHERE rule_type = 'subcategory' AND subcategory_id = bp.subcategory_id AND is_active = TRUE ORDER BY priority DESC LIMIT 1),
        (SELECT markup_value / 100.0 FROM markup_rules WHERE rule_type = 'category' AND category_id = (SELECT category_id FROM product_subcategories WHERE subcategory_id = bp.subcategory_id) AND is_active = TRUE ORDER BY priority DESC LIMIT 1),
        (SELECT markup_value / 100.0 FROM markup_rules WHERE rule_type = 'global' AND is_active = TRUE ORDER BY priority DESC LIMIT 1),
        0
    )), 2) as retail_price
FROM base_pricing bp
WHERE bp.is_available = TRUE;

-- ============================================================================
-- COUPON SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS coupons (
    coupon_id INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    discount_type VARCHAR(20) NOT NULL, -- 'percentage', 'fixed'
    discount_value DECIMAL(10,2) NOT NULL,
    scope_type VARCHAR(20) NOT NULL, -- 'all', 'category', 'subcategory', 'specific'
    category_id INTEGER,
    subcategory_id INTEGER,
    size_id INTEGER,
    min_order_value DECIMAL(10,2),
    max_discount DECIMAL(10,2),
    usage_limit INTEGER, -- NULL = unlimited
    usage_count INTEGER DEFAULT 0,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id),
    FOREIGN KEY (subcategory_id) REFERENCES product_subcategories(subcategory_id),
    FOREIGN KEY (size_id) REFERENCES print_sizes(size_id)
);

-- ============================================================================
-- ORDER MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_order_id VARCHAR(100) UNIQUE, -- OrderDesk order ID
    user_id INTEGER,
    order_status VARCHAR(50) DEFAULT 'pending', -- pending, paid, submitted, processing, shipped, completed, cancelled
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    shipping_cost DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    coupon_code VARCHAR(50),
    payment_status VARCHAR(50), -- pending, completed, failed, refunded
    payment_method VARCHAR(50),
    payment_transaction_id VARCHAR(255),
    shipping_first_name VARCHAR(100),
    shipping_last_name VARCHAR(100),
    shipping_address1 VARCHAR(255),
    shipping_address2 VARCHAR(255),
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(50),
    shipping_zip VARCHAR(20),
    shipping_country VARCHAR(2) DEFAULT 'US',
    shipping_phone VARCHAR(50),
    customer_email VARCHAR(255),
    customer_notes TEXT,
    admin_notes TEXT,
    orderdesk_submitted_at TIMESTAMP,
    lumaprints_order_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    subcategory_id INTEGER NOT NULL,
    size_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    cost_price DECIMAL(10,2) NOT NULL,
    retail_price DECIMAL(10,2) NOT NULL,
    selected_options TEXT, -- JSON array of option IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (image_id) REFERENCES images(id),
    FOREIGN KEY (subcategory_id) REFERENCES product_subcategories(subcategory_id),
    FOREIGN KEY (size_id) REFERENCES print_sizes(size_id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_subcategories_category ON product_subcategories(category_id);
CREATE INDEX IF NOT EXISTS idx_subcategory_options_subcategory ON subcategory_options(subcategory_id);
CREATE INDEX IF NOT EXISTS idx_subcategory_options_option ON subcategory_options(option_id);
CREATE INDEX IF NOT EXISTS idx_print_sizes_aspect_ratio ON print_sizes(aspect_ratio_id);
CREATE INDEX IF NOT EXISTS idx_base_pricing_subcategory ON base_pricing(subcategory_id);
CREATE INDEX IF NOT EXISTS idx_base_pricing_size ON base_pricing(size_id);
CREATE INDEX IF NOT EXISTS idx_option_pricing_subcategory ON option_pricing(subcategory_id);
CREATE INDEX IF NOT EXISTS idx_option_pricing_option ON option_pricing(option_id);
CREATE INDEX IF NOT EXISTS idx_markup_rules_active ON markup_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_coupons_code ON coupons(coupon_code);
CREATE INDEX IF NOT EXISTS idx_coupons_active ON coupons(is_active);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);

-- ============================================================================
-- INITIAL DATA POPULATION
-- ============================================================================

-- Insert Product Categories
INSERT OR IGNORE INTO product_categories (category_id, category_name, display_name, description, display_order) VALUES
(101, 'canvas', 'Canvas', 'Gallery-wrapped canvas prints on wood frames', 1),
(102, 'framed_canvas', 'Framed Canvas', 'Canvas prints in decorative floating frames', 2),
(103, 'fine_art_paper', 'Fine Art Paper', 'Museum-quality paper prints', 3),
(104, 'foam_mounted', 'Foam-mounted Print', 'Fine art paper mounted on rigid foam board', 4);

-- Insert Aspect Ratios
INSERT OR IGNORE INTO aspect_ratios (ratio_name, ratio_decimal, display_name, description) VALUES
('1:1', 1.0, 'Square', 'Square format (1:1 aspect ratio)'),
('3:2', 1.5, 'Standard', 'Standard digital/35mm format (3:2 aspect ratio)');

-- Insert Product Options
INSERT OR IGNORE INTO product_options (option_id, option_group, option_name, display_name, description, is_default) VALUES
-- Canvas Border Options
(1, 'Canvas Border', 'image_wrap', 'Image Wrap', 'Image wraps around edges', FALSE),
(2, 'Canvas Border', 'mirror_wrap', 'Mirror Wrap', 'Image mirrors around edges', TRUE),
(3, 'Canvas Border', 'solid_color', 'Solid Color', 'Solid color border', FALSE),

-- Hanging Hardware Options
(4, 'Hanging Hardware', 'sawtooth_hanger', 'Sawtooth Hanger', 'Sawtooth hanger installed', FALSE),
(5, 'Hanging Hardware', 'hanging_wire', 'Hanging Wire', 'Hanging wire installed', TRUE),
(6, 'Hanging Hardware', 'black_backboard_sawtooth', 'Black Backboard with Sawtooth', 'Black backboard with sawtooth', FALSE),
(7, 'Hanging Hardware', 'black_backboard_wire', 'Black Backboard with Wire', 'Black backboard with hanging wire', FALSE),
(8, 'Hanging Hardware', 'wire_loose', 'Wire Provided Loose', 'Hanging wire provided loose', FALSE),
(133, 'Hanging Hardware', 'three_point_security', 'Three-point Security', 'Three-point security hardware', FALSE),

-- Frame Canvas Hanging Hardware
(16, 'Framed Canvas Hanging Hardware', 'hanging_wire_frame', 'Hanging Wire', 'Hanging wire installed on frame', TRUE),
(17, 'Framed Canvas Hanging Hardware', 'black_backboard_wire_frame', 'Black Backboard with Wire', 'Black backboard with wire on frame', FALSE),
(18, 'Framed Canvas Hanging Hardware', 'hardware_loose_frame', 'Hardware Provided Loose', 'Hanging hardware provided loose', FALSE),
(134, 'Framed Canvas Hanging Hardware', 'three_point_security_frame', 'Three-point Security', 'Three-point security hardware on frame', FALSE),

-- 0.75" Frame Styles
(12, '0.75" Frame Style', 'black_floating_075', '0.75" Black Floating Frame', 'Black floating frame', TRUE),
(13, '0.75" Frame Style', 'white_floating_075', '0.75" White Floating Frame', 'White floating frame', FALSE),
(15, '0.75" Frame Style', 'gold_plein_air', 'Gold Plein Air Frame', 'Gold plein air frame', FALSE),

-- 1.25" Frame Styles
(27, '1.25" Frame Style', 'black_floating_125', '1.25" Black Floating Frame', 'Black floating frame', TRUE),
(91, '1.25" Frame Style', 'oak_floating_125', '1.25" Oak Floating Frame', 'Oak floating frame', FALSE),
(120, '1.25" Frame Style', 'walnut_floating_125', '1.25" Walnut Floating Frame', 'Walnut floating frame', FALSE),

-- 1.50" Frame Styles
(23, '1.50" Frame Style', 'black_floating_150', '1.50" Black Floating Frame', 'Black floating frame', TRUE),
(24, '1.50" Frame Style', 'white_floating_150', '1.50" White Floating Frame', 'White floating frame', FALSE),
(26, '1.50" Frame Style', 'oak_floating_150', '1.50" Oak Floating Frame', 'Oak floating frame', FALSE),

-- Fine Art Paper Bleed Options
(36, 'Fine Art Paper Bleed', 'bleed_025', '0.25" Bleed', '0.25" bleed on each side (for framing)', TRUE),
(39, 'Fine Art Paper Bleed', 'no_bleed', 'No Bleed', 'No bleed (image to edge)', FALSE);

-- Insert Product Subcategories
INSERT OR IGNORE INTO product_subcategories (subcategory_id, category_id, subcategory_name, display_name, description, display_order, max_width, max_height) VALUES
-- Canvas Products
(101001, 101, '075_stretched', '0.75" Stretched Canvas', 'Canvas wrapped on 0.75" deep wood frame', 1, 30, 30),
(101002, 101, '125_stretched', '1.25" Stretched Canvas', 'Canvas wrapped on 1.25" deep wood frame', 2, NULL, NULL),
(101003, 101, '150_stretched', '1.50" Stretched Canvas', 'Canvas wrapped on 1.50" deep wood frame', 3, NULL, NULL),
(101005, 101, 'rolled', 'Rolled Canvas', 'Canvas print without frame (rolled)', 4, NULL, NULL),

-- Framed Canvas Products
(102001, 102, '075_framed', '0.75" Framed Canvas', 'Canvas on 0.75" frame in decorative frame', 1, NULL, NULL),
(102002, 102, '125_framed', '1.25" Framed Canvas', 'Canvas on 1.25" frame in decorative frame', 2, NULL, NULL),
(102003, 102, '150_framed', '1.50" Framed Canvas', 'Canvas on 1.50" frame in decorative frame', 3, NULL, NULL),

-- Fine Art Paper Products
(103002, 103, 'hot_press', 'Hot Press Fine Art Paper', 'Smooth finish fine art paper', 1, NULL, NULL),
(103003, 103, 'cold_press', 'Cold Press Fine Art Paper', 'Textured finish fine art paper', 2, NULL, NULL),
(103005, 103, 'semi_glossy', 'Semi-Glossy Fine Art Paper', 'Vibrant semi-glossy finish', 3, NULL, NULL),
(103007, 103, 'glossy', 'Glossy Fine Art Paper', 'High-gloss finish', 4, NULL, NULL),

-- Foam-mounted Products (use category 104, subcategory IDs need to be determined)
(104002, 104, 'foam_hot_press', 'Foam-mounted Hot Press', 'Hot press paper on foam board', 1, NULL, NULL),
(104003, 104, 'foam_cold_press', 'Foam-mounted Cold Press', 'Cold press paper on foam board', 2, NULL, NULL),
(104005, 104, 'foam_semi_glossy', 'Foam-mounted Semi-Glossy', 'Semi-glossy paper on foam board', 3, NULL, NULL),
(104007, 104, 'foam_glossy', 'Foam-mounted Glossy', 'Glossy paper on foam board', 4, NULL, NULL);

-- ============================================================================
-- NOTES
-- ============================================================================

-- This schema provides:
-- 1. Complete product catalog with Lumaprints API IDs
-- 2. Aspect ratio and size management
-- 3. Flexible pricing with cost + markup
-- 4. Coupon system for promotions
-- 5. Order tracking and management
-- 6. Performance indexes for fast queries

-- Next steps:
-- 1. Import pricing data from Excel spreadsheet
-- 2. Set up default markup rules
-- 3. Configure subcategory-option relationships
-- 4. Test pricing calculations

