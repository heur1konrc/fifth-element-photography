-- Pictorem Product Database Schema
-- Clean slate replacement for Lumaprints
-- Designed for Pictorem API integration

-- Drop existing tables if they exist
DROP TABLE IF EXISTS pictorem_pricing_cache;
DROP TABLE IF EXISTS pictorem_product_options;
DROP TABLE IF EXISTS pictorem_sizes;
DROP TABLE IF EXISTS pictorem_products;
DROP TABLE IF EXISTS pictorem_categories;
DROP TABLE IF EXISTS pictorem_settings;

-- Categories (Canvas, Framed Fine Art, Metal, Acrylic, Paper)
CREATE TABLE pictorem_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    material TEXT NOT NULL,  -- canvas, paper, metal, acrylic
    description TEXT,
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products (Base product definitions)
CREATE TABLE pictorem_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    material TEXT NOT NULL,  -- canvas, paper, metal, acrylic
    type TEXT NOT NULL,      -- stretched, roll, art, hd, da8, etc.
    description TEXT,
    preorder_template TEXT NOT NULL,  -- Template for building preorder codes
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES pictorem_categories(id)
);

-- Sizes (Available sizes for each product)
CREATE TABLE pictorem_sizes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    orientation TEXT NOT NULL,  -- horizontal, vertical, square
    display_name TEXT NOT NULL,  -- "24x36", "30x40", etc.
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES pictorem_products(id),
    UNIQUE(product_id, width, height)
);

-- Product Options (Frames, mats, glazing, etc.)
CREATE TABLE pictorem_product_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    option_type TEXT NOT NULL,  -- frame, mat, glazing, hanging, finish, depth
    option_code TEXT NOT NULL,  -- 301-21, mb01, plexiglass, wire, c15, etc.
    option_name TEXT NOT NULL,  -- "Espresso Floating Frame", "White Mat", etc.
    description TEXT,
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES pictorem_products(id)
);

-- Pricing Cache (Cache Pictorem API pricing responses)
CREATE TABLE pictorem_pricing_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preorder_code TEXT NOT NULL UNIQUE,
    base_price REAL NOT NULL,
    price_breakdown TEXT,  -- JSON string with itemized pricing
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- Settings (Global configuration)
CREATE TABLE pictorem_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT INTO pictorem_settings (key_name, value, description) VALUES
    ('api_token', '0f32e36462bccc0eda7df265a8cabe68', 'Pictorem API authentication token'),
    ('api_base_url', 'https://www.pictorem.com/artflow', 'Pictorem API base URL'),
    ('global_markup_percentage', '50', 'Global markup percentage applied to base prices'),
    ('pricing_cache_ttl', '300', 'Pricing cache time-to-live in seconds (5 minutes)'),
    ('default_country', 'USA', 'Default country for pricing calculations'),
    ('production_lead_time', '5', 'Default production lead time in business days');

-- Create indexes for performance
CREATE INDEX idx_categories_active ON pictorem_categories(active);
CREATE INDEX idx_products_category ON pictorem_products(category_id);
CREATE INDEX idx_products_active ON pictorem_products(active);
CREATE INDEX idx_sizes_product ON pictorem_sizes(product_id);
CREATE INDEX idx_sizes_active ON pictorem_sizes(active);
CREATE INDEX idx_options_product ON pictorem_product_options(product_id);
CREATE INDEX idx_options_type ON pictorem_product_options(option_type);
CREATE INDEX idx_pricing_cache_expires ON pictorem_pricing_cache(expires_at);
