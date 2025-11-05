# Shopify Product Mapping Progress

Track the progress of mapping gallery images to Shopify products for the Fifth Element Photography website.

## Current Status

**Last Updated**: November 5, 2024  
**Products Mapped**: 8  
**Total Gallery Images**: TBD  
**Completion**: In Progress

## Mapping Overview

The Shopify mapping system connects gallery images to Shopify products, enabling the "ORDER PRINTS" button functionality. Each mapping links:

- Gallery image filename
- Shopify product ID
- Product handle
- Product title

## How to Map Products

1. **Access Admin Panel**
   - Navigate to `/admin` and log in
   - Click "Shopify Product Mapping" button

2. **Map Images**
   - Browse gallery images
   - For each image, enter:
     - Shopify Product ID
     - Product Handle
     - Product Title
   - Click "Save Mapping"

3. **Verify Mapping**
   - Visit the main gallery
   - Mapped images will show "ORDER PRINTS" button
   - Click button to test Shopify modal

## Shopify Product Configuration

### Product Types Available

1. **Fine Art Paper Prints**
   - Sizes: 8x8, 10x10, 12x12, 14x14, 8x12, 12x18, 16x24, 20x30, 24x36
   - Finishes: Glossy, Matte, Lustre

2. **Canvas Prints (0.75")**
   - Sizes: 8x8, 10x10, 12x12, 14x14, 8x12, 12x18, 16x24, 20x30, 24x36
   - Gallery wrap finish

### Shipping Profiles

Each product is assigned to one of four shipping profiles:

1. **Paper** (93 products)
   - All fine art paper prints
   - Price increase: +$3

2. **Small/Medium Canvas** (22 products)
   - Sizes: 8x10 to 16x24
   - Price increase: +$10

3. **Medium/Large Canvas**
   - Size: 20x30
   - Price increase: +$10

4. **Extra-Large Canvas** (6 products)
   - Size: 24x36
   - Price increase: +$10

### Shipping Options

Customers can choose from three shipping speeds:
- **Economy** (5-8 days)
- **Standard** (3-5 days)
- **Express** (2nd day air)

## Mapping Progress Log

### November 5, 2024
- **Mapped**: 8 products
- **Status**: Initial mapping phase
- **Next Steps**: Continue mapping remaining gallery images

### Future Updates
- Track progress as more products are mapped
- Document any mapping issues or special cases
- Update total gallery image count

## Technical Notes

### Database Table: `shopify_mappings`

```sql
CREATE TABLE shopify_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_filename TEXT NOT NULL UNIQUE,
    shopify_product_id TEXT NOT NULL,
    product_handle TEXT NOT NULL,
    product_title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Admin Interface
- **URL**: `/admin/shopify-mapping`
- **Features**:
  - Image grid display (5-6 images across)
  - Mapping form for each image
  - Save/update functionality
  - "Back to Admin" and "Go to Website" navigation

### Frontend Integration
- **JavaScript**: `shopify-integration.js`
- **Config**: `shopify-config.js` (loads mappings from database)
- **Modal**: Badge-style variant selectors
- **Button**: "ORDER PRINTS" appears only on mapped images

## Goals

- [ ] Map all gallery images to Shopify products
- [ ] Test ordering flow for each product type
- [ ] Verify shipping calculations
- [ ] Ensure mobile compatibility
- [ ] Document any edge cases or issues

## Resources

- **Shopify Admin**: Access your Shopify store admin panel
- **Product IDs**: Found in Shopify product URLs
- **Product Handles**: URL-friendly product identifiers
- **Mapping Tool**: `/admin/shopify-mapping`

---

*This document will be updated as mapping progress continues.*

