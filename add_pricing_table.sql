-- Add product pricing table for managing all prices
CREATE TABLE IF NOT EXISTS pictorem_product_pricing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    size_id INTEGER NOT NULL,
    option_id INTEGER,
    preorder_code TEXT NOT NULL,
    base_price REAL NOT NULL,
    markup_percentage REAL NOT NULL,
    customer_price REAL NOT NULL,
    price_override REAL,
    active INTEGER DEFAULT 1,
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES pictorem_products(id),
    FOREIGN KEY (size_id) REFERENCES pictorem_sizes(id),
    FOREIGN KEY (option_id) REFERENCES pictorem_product_options(id),
    UNIQUE(product_id, size_id, option_id)
);

CREATE INDEX IF NOT EXISTS idx_pricing_product ON pictorem_product_pricing(product_id);
CREATE INDEX IF NOT EXISTS idx_pricing_size ON pictorem_product_pricing(size_id);
CREATE INDEX IF NOT EXISTS idx_pricing_active ON pictorem_product_pricing(active);

