# Print Ordering Pricing Admin - Changelog

## Version Beta 0.1.0 - October 30, 2025

### Added
- ✅ Complete pricing database system
- ✅ Excel catalog import (172 products)
- ✅ Admin interface for pricing management
- ✅ Markup management (global and per-category)
- ✅ Product enable/disable functionality
- ✅ Coupon code system (structure ready)
- ✅ Database setup route for Railway deployment
- ✅ Automatic database path detection (Railway vs local)

### Database
- **Schema:** Complete relational database design
- **Tables:** 
  - `categories` - Product categories
  - `subcategories` - Product variants
  - `base_pricing` - Cost prices and sizes
  - `markup_rules` - Markup configuration
  - `coupons` - Promotional codes
  - `orders` - Order tracking
  - `order_items` - Order line items

### Products Imported
- **Canvas:** 15 sizes (0.75", 1.25", 1.50", Rolled)
- **Framed Canvas:** 36 combinations
  - 0.75": Black, White, Gold Plein Air
  - 1.25": Black, Oak, Walnut
  - 1.50": Black, White, Oak
- **Fine Art Paper:** 52 sizes
  - Hot Press, Cold Press, Semi-Glossy, Glossy
- **Foam-mounted:** 52 sizes
  - Same 4 paper types with foam backing

### Lumaprints API Mapping
- ✅ All subcategory IDs mapped correctly
- ✅ Frame option IDs configured
- ✅ Canvas options: Mirror Wrap, Hanging Wire
- ✅ Paper options: Bleed settings

### Admin Interface
- **Main Dashboard:** Overview and navigation
- **Browse Pricing:** View all products and costs
- **Manage Markups:** Set pricing strategy
- **Manage Products:** Enable/disable offerings
- **Setup Page:** Initialize database on Railway

### Technical Details
- Database path: `/data/print_ordering.db` (Railway)
- Fallback: `database/print_ordering.db` (local)
- Import source: `LumaprintsCatalogandSizingw_aspectratios.xlsx`
- Admin button: Added to `/admin` dashboard (yellow/warning color)

### Documentation
- `PRICING_ADMIN_SETUP.md` - Setup instructions
- `PRINT_ORDERING_SYSTEM_PLAN.md` - Complete system plan
- `LUMAPRINTS_API_NOTES.md` - API reference
- `ORDERDESK_API_NOTES.md` - OrderDesk integration

### Known Limitations
- Coupon functionality not yet implemented (structure ready)
- Customer-facing ordering interface not built
- No API connection testing yet
- Shipping cost integration pending

### Next Steps
1. Test database setup on Railway
2. Configure markup strategy
3. Build customer ordering interface
4. Test Lumaprints API connection
5. Integrate OrderDesk submission
6. Add payment processing

---

## Deployment History

### Commit: 0967d13
- Initial pricing admin system
- Database and admin interface
- Excel import functionality

### Commit: [PENDING]
- Added database setup route
- Fixed database path for Railway
- Added setup documentation

---

## Backup Information

**Backup Created:** October 30, 2025 01:15 AM  
**Filename:** `fifth-element-backup-20251030_011530_pricing_admin_v0.1.0.tar.gz`  
**Size:** 23 MB  
**Location:** `/home/ubuntu/`

---

## Version Strategy

**Main Site:** v2.0.0 (production)  
**Print Ordering:** Beta v0.1.0 (development)

Print ordering system maintains separate beta versioning until fully tested and released.

---

**Status:** Ready for Railway deployment and testing

