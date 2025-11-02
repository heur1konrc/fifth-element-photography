# Shopify Integration - Version 2.1.0
**Date:** November 1, 2025  
**Backup:** `fifth-element-photography_backup_shopify_integration_20251101_235239`

## Overview

This update integrates Shopify e-commerce functionality directly into the fifthelement.photos website, allowing customers to order prints without leaving the main site. The integration uses Shopify Buy Button SDK to embed product selection interfaces within modals on the photography gallery.

## Key Features

### 1. Seamless Ordering Experience
- Users browse the gallery on fifthelement.photos as usual
- Clicking "ORDER PRINTS" opens a modal with the Shopify product interface embedded
- Substrate options (Canvas, Fine Art Paper types) displayed within the modal
- Size selection and dynamic pricing shown in real-time
- "Add to Cart" and "Buy it Now" buttons functional within the modal
- Only redirects to Shopify for final checkout

### 2. Product Mapping
- Each gallery image can be mapped to a specific Shopify product
- Current products in Shopify store:
  - Lily of The Valley (test-print-of-capital-paper-and-canva-combined)
  - Additional products to be added as needed

### 3. Fulfillment Integration
- Shopify store connected to Lumaprints for print fulfillment
- All product variants (substrate + size combinations) mapped to Lumaprints SKUs
- Order processing handled automatically through Shopify → Lumaprints workflow

### 4. Admin Enhancements
- Individual image download buttons added to admin panel
- Blue "Download" button on each image card
- Downloads high-resolution originals when available, falls back to web versions
- Route: `/admin/download-image/<filename>`

## Technical Implementation

### Shopify Configuration
- **Store Domain:** `fifth-element-photography.myshopify.com`
- **Integration Method:** Shopify Buy Button SDK / Storefront API
- **Product Structure:** Individual products per image with multiple variants
- **Variants:** Substrate (4 options) × Size (5 options) = 20+ variants per product

### Code Changes

#### New Routes
```python
@app.route('/admin/download-image/<filename>')
@require_admin_auth
def download_image(filename):
    """Download image - tries high-res first, falls back to web version"""
```

#### Modified Files
- `static/js/script.js` - Updated `openOrderWizard()` function for Shopify integration
- `app.py` - Added download route
- `app_version.py` - Updated to v2.1.0

#### New Files
- Shopify Buy Button embed code (to be added)
- Product mapping configuration (to be implemented)

## Product Variants

### Substrate Options
1. **Stretched Canvas** - Gallery-wrapped canvas prints
2. **Hot Press Fine Art Paper** - Best for photos, smooth finish
3. **Semi-Gloss Fine Art Paper** - Slight sheen, vibrant colors
4. **Glossy Fine Art Paper** - High gloss, maximum color saturation

### Size Options
- 8×8 inches
- 10×10 inches
- 12×12 inches
- 14×14 inches
- 6×6 inches

### Pricing
- Dynamic pricing based on substrate and size selection
- Range: $2.00 - $45.00 depending on configuration
- Prices managed in Shopify admin panel

## Deployment Notes

### Prerequisites
- Shopify store must be live (currently in preview mode)
- Storefront API access token required
- Product IDs or handles needed for each gallery image

### Testing Checklist
- [ ] Modal opens correctly when clicking ORDER PRINTS
- [ ] Substrate options display and are selectable
- [ ] Size options display and are selectable
- [ ] Price updates dynamically based on selections
- [ ] Add to Cart button functions correctly
- [ ] Buy it Now button redirects to Shopify checkout
- [ ] Cart persists across page navigation
- [ ] Checkout process completes successfully
- [ ] Order appears in Shopify admin
- [ ] Order forwards to Lumaprints for fulfillment

### Known Limitations
- Only 3 images currently have Shopify products configured
- Bulk download feature removed due to performance issues
- Individual downloads work but bulk operations need optimization

## Future Enhancements

### Phase 2 (Planned)
- Automatic product creation in Shopify when images are uploaded to admin
- Image-to-product mapping interface in admin panel
- Bulk product management tools
- Custom product descriptions per image

### Phase 3 (Planned)
- Custom checkout flow on fifthelement.photos (full white-label)
- Payment processing directly on site
- Order management dashboard in admin panel

## Rollback Instructions

If issues arise, rollback to v2.0.0:

```bash
cd /home/ubuntu
rm -rf fifth-element-photography
cp -r fifth-element-photography_backup_shopify_integration_20251101_235239 fifth-element-photography
cd fifth-element-photography
git reset --hard 77fabac  # Commit before Shopify integration
git push -f origin main
```

## Support & Maintenance

### Shopify Admin Access
- URL: `https://fifth-element-photography.myshopify.com/admin`
- Product management, order tracking, and fulfillment settings

### Lumaprints Integration
- Managed through Shopify app marketplace
- Product variant mapping maintained in Shopify admin
- Fulfillment status tracked in Shopify orders

## Version History

- **v2.1.0** (2025-11-01) - Shopify integration with embedded product modals
- **v2.0.0** (2025-10-27) - Removed all print ordering, kept gallery only
- **v1.x.x** (2025-10-20 to 2025-10-26) - Full Lumaprints API integration (removed)

---

**Status:** In Development  
**Next Steps:** Implement Shopify Buy Button SDK and test modal integration

