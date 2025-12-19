-- Migration: Add shopify_products table to track which images have been added to Shopify
-- Created: 2025-12-19

CREATE TABLE IF NOT EXISTS shopify_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_filename TEXT NOT NULL UNIQUE,
    shopify_product_id TEXT NOT NULL,
    shopify_handle TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shopify_products_filename ON shopify_products(image_filename);
CREATE INDEX IF NOT EXISTS idx_shopify_products_shopify_id ON shopify_products(shopify_product_id);
