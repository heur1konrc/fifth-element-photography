DROP TABLE IF EXISTS pictorem_pricing_cache;
DROP TABLE IF EXISTS pictorem_product_options;
DROP TABLE IF EXISTS pictorem_sizes;
DROP TABLE IF EXISTS pictorem_products;
DROP TABLE IF EXISTS pictorem_categories;
DROP TABLE IF EXISTS pictorem_settings;

CREATE TABLE pictorem_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    material TEXT NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pictorem_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    material TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    preorder_template TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES pictorem_categories(id)
);

CREATE TABLE pictorem_sizes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    orientation TEXT NOT NULL,
    display_name TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES pictorem_products(id),
    UNIQUE(product_id, width, height)
);

CREATE TABLE pictorem_product_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    option_type TEXT NOT NULL,
    option_code TEXT NOT NULL,
    option_name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES pictorem_products(id)
);

CREATE TABLE pictorem_pricing_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preorder_code TEXT NOT NULL UNIQUE,
    base_price REAL NOT NULL,
    price_breakdown TEXT,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE pictorem_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO pictorem_settings (key_name, value, description) VALUES
    ('api_token', '0f32e36462bccc0eda7df265a8cabe68', 'Pictorem API token'),
    ('api_base_url', 'https://www.pictorem.com/artflow', 'Pictorem API base URL'),
    ('global_markup_percentage', '50', 'Global markup percentage'),
    ('pricing_cache_ttl', '300', 'Cache TTL in seconds'),
    ('default_country', 'USA', 'Default country for pricing'),
    ('production_lead_time', '5', 'Production lead time in days');

CREATE INDEX idx_categories_active ON pictorem_categories(active);
CREATE INDEX idx_products_category ON pictorem_products(category_id);
CREATE INDEX idx_products_active ON pictorem_products(active);
CREATE INDEX idx_sizes_product ON pictorem_sizes(product_id);
CREATE INDEX idx_options_product ON pictorem_product_options(product_id);
CREATE INDEX idx_pricing_cache_expires ON pictorem_pricing_cache(expires_at);
