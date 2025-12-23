# Release Notes - v2.3.3

**Date:** December 23, 2024

## Summary
Automated Shopify product mapping - no more manual handle entry! When you create Shopify products, all 5 category handles are automatically saved to the database. Order Prints button now shows a category selector modal so customers can choose which print type they want.

## What's New

### Automated Product Mapping
- **Auto-save handles**: When creating Shopify products via "Create Shopify Product" button, all 5 category handles are automatically saved to database
- **No manual entry**: Previously required entering 5 handles per image manually - now completely automated
- **Smart handle capture**: Captures actual handle from Shopify API response (handles conflicts and normalization)

### Category Selector Modal
- **Order Prints enhancement**: When user clicks "Order Prints", shows modal with 5 category buttons
- **Categories**: Canvas, Metal, Fine Art Paper, Framed Canvas, Foam-mounted Print
- **User flow**: Click image → Order Prints → Choose category → Shopify checkout

### Technical Improvements
- **Database structure**: `shopify_products` table with composite unique key (filename + category)
- **API endpoint**: `/api/shopify/product-categories/<filename>` returns all handles for an image
- **Frontend integration**: Loads category-based mappings and displays selector modal
- **Handle normalization**: Captures actual handle from Shopify (handles title-to-handle conversion)

## Workflow

### Before v2.3.3
1. Create 5 Shopify products (one per category)
2. Manually copy each handle
3. Manually enter 5 handles in mapping tool
4. Repeat for 100+ images (500+ manual entries!)

### After v2.3.3
1. Create Shopify products (all 5 handles auto-saved)
2. Order Prints button works immediately
3. Users see category selector and choose print type

## Files Modified
- `routes/shopify_api_creator.py`: Updated product creation to save handles with categories
- `routes/shopify_admin.py`: Updated `/api/shopify-mapping/all` to return category-based mappings
- `static/js/shopify-config.js`: Updated to handle category-based mapping format
- `app_version.py`: Version bumped to v2.3.3

## Database Schema
```sql
CREATE TABLE shopify_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_filename TEXT NOT NULL,
    category TEXT NOT NULL,
    shopify_product_id TEXT NOT NULL,
    shopify_handle TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(image_filename, category)
);
```

## Deployment
1. Pull from GitHub: `git pull origin main`
2. Restart Flask app
3. Test: Create Shopify product → Verify handles saved → Test Order Prints button

## Notes
- Existing products created before v2.3.3 will need to be recreated to populate the new database structure
- Category selector automatically appears when multiple product types exist for an image
- Single product type (legacy) opens directly without selector modal
