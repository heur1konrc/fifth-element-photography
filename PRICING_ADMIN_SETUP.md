# Print Ordering Pricing Admin - Setup Guide

**Version:** Beta 0.1.0  
**Date:** October 30, 2025  
**Status:** Ready for Railway deployment

---

## Overview

The Print Ordering Pricing Admin system provides a complete interface for managing product pricing, markups, and availability for the Fifth Element Photography print ordering system.

---

## Setup Instructions (Railway Deployment)

### Step 1: Deploy to Railway

The code is already pushed to GitHub. Railway will automatically deploy when you push.

**Git Commit:** `0967d13` - Initial pricing admin  
**Git Commit:** `[NEXT]` - Database setup route added

### Step 2: Initialize Database

After deployment completes:

1. **Log into admin:** https://fifthelement.photos/admin
2. **Visit setup page:** https://fifthelement.photos/admin/setup-pricing
3. **Click "Initialize Database"** button
4. **Wait for confirmation** (should take 5-10 seconds)
5. **Verify:** Should show "172 products loaded"

### Step 3: Access Pricing Management

1. **Return to admin dashboard:** https://fifthelement.photos/admin
2. **Click "Pricing Management (Beta)"** button
3. **You should see:**
   - Main pricing dashboard
   - 172 products at cost prices
   - All markups at 0% (no markup applied)

---

## What Gets Created

### Database Location
- **Railway:** `/data/print_ordering.db` (persistent volume)
- **Local:** `database/print_ordering.db` (for development)

### Database Contents
- **172 pricing entries** imported from Excel catalog
- **4 product categories:** Canvas, Framed Canvas, Fine Art Paper, Foam-mounted
- **All prices at COST** (wholesale from Lumaprints)
- **Lumaprints API IDs** properly mapped
- **Frame options** configured for all depths

### Product Breakdown
- Canvas: 15 sizes (1:1 and 3:2 ratios)
- Framed Canvas: 36 combinations (3 depths × 3 colors × sizes)
- Fine Art Paper: 52 sizes (4 paper types)
- Foam-mounted: 52 sizes (4 paper types)

---

## Admin Interface Features

### 1. Main Dashboard (`/admin/pricing`)
- Overview statistics
- Quick navigation
- System status

### 2. Browse Pricing (`/admin/pricing/browse`)
- View all products by category
- See cost prices
- Filter by aspect ratio
- Search functionality

### 3. Manage Markups (`/admin/pricing/markups`)
- **Global markup:** Apply percentage to all products
- **Category markups:** Different markup per category
- **Individual overrides:** Custom pricing for specific products
- **Coupon codes:** Create promotional discounts

### 4. Manage Products (`/admin/pricing/products`)
- Enable/disable categories
- Enable/disable individual products
- Control customer ordering options

---

## Markup Strategy Examples

### Option A: Global Markup
Set one markup for everything:
- **40% markup** → All products marked up 40%
- Simple and consistent

### Option B: Category-Specific
Different markups per product type:
- **Canvas:** 35% markup
- **Framed Canvas:** 40% markup
- **Metal:** 50% markup
- **Paper:** 30% markup

### Option C: Hybrid
- **Global:** 40% base markup
- **Override:** Specific products with custom pricing
- **Coupons:** Promotional discounts

---

## Troubleshooting

### "Internal Server Error" on /admin/pricing

**Cause:** Database not initialized  
**Solution:** Visit `/admin/setup-pricing` and click "Initialize Database"

### Database shows 0 products

**Cause:** Import failed  
**Solution:** Check Railway logs for errors, re-run setup

### Prices not updating

**Cause:** Database connection issue  
**Solution:** Restart Railway service, verify /data volume

---

## Next Steps After Setup

1. **Review all prices** - Browse pricing to verify import
2. **Set markup strategy** - Decide on global vs category markups
3. **Enable products** - Choose which products to offer
4. **Create coupons** (optional) - Set up promotional codes
5. **Test ordering flow** - Build customer-facing interface

---

## Files Created

### Routes
- `routes/pricing_admin.py` - Main pricing management
- `routes/setup_pricing.py` - Database initialization

### Templates
- `templates/admin_pricing.html` - Main dashboard
- `templates/admin_pricing_browse.html` - Browse products
- `templates/admin_pricing_markups.html` - Manage markups
- `templates/admin_pricing_products.html` - Enable/disable products
- `templates/admin_setup_pricing.html` - Database setup page

### Database
- `database/print_ordering_schema.sql` - Database schema
- `database/print_ordering.db` - Local database (for reference)
- `scripts/import_pricing_data.py` - Import script

### Documentation
- `PRINT_ORDERING_SYSTEM_PLAN.md` - Complete system plan
- `PRINT_ORDERING_QUICK_REFERENCE.md` - Quick reference
- `LUMAPRINTS_API_NOTES.md` - API documentation
- `ORDERDESK_API_NOTES.md` - OrderDesk API docs

---

## Support

If you encounter issues:
1. Check Railway logs
2. Verify /data directory exists
3. Re-run database setup
4. Check this documentation

---

**Ready to proceed with customer-facing ordering interface after pricing is configured!**

