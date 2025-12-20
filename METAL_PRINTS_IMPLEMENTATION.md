# Metal Prints Implementation - December 20, 2025

## Overview
Successfully added Metal Prints as a new product category with full Shopify integration.

## Product Details

### Categories Added
- Glossy White Metal
- Glossy Silver Metal

### Sizes and Pricing (11 sizes per color = 22 total)

**Standard (3:2):** 8×12" ($33.95), 12×18" ($59.77), 16×24" ($95.21), 24×36" ($188.32), 32×48" ($316.76), 40×60" ($480.27)

**Square (1:1):** 12×12" ($43.94), 20×20" ($98.15), 24×24" ($132.45), 30×30" ($194.93), 36×36" ($270.62)

## Database Changes

### Added
- Metal category (category_id: 105, category_name: 'metal')
- Glossy White Metal subcategory (104008)
- Glossy Silver Metal subcategory (104009)
- 36×36" size to print_sizes table
- 22 pricing entries in base_pricing

### Modified
- Renamed "Foam-mounted Print" to "Foam-mounted Fine Art Paper"

## Code Changes

### New Migration Endpoints
- /api/admin/add-metal-prints
- /api/admin/add-metal-36x36-pricing
- /api/admin/fix-metal-36x36
- /api/admin/fix-metal-category-name
- /api/admin/rename-foam-mounted
- /api/admin/debug-metal

### Shopify Integration (shopify_api_creator.py)
1. Added 'Metal' to category filter
2. Added Metal to sort order
3. Added Metal product types to mapping
4. Added Metal to categories dictionary
5. Added Metal to categorization logic

## Issues Resolved
1. Aspect ratio names (Standard/Square vs 3:2/1:1)
2. Missing 36×36" size in database
3. Category name case mismatch (Metal vs metal)
4. Missing display_name in category
5. Products filtered out in multiple places

## Testing
✅ Metal appears in pricing admin
✅ All 22 pricing entries correct
✅ Shopify product creator includes Metal
✅ Metal products created in Shopify

## Deployment
- Platform: Railway
- Database: /data/print_ordering.db
- Date: December 20, 2025
- Status: ✅ Live and functional
