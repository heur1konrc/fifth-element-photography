# Hierarchical Order Form Wizard - Status Report
**Last Updated:** October 21, 2025 6:32 PM CDT

## 🎯 CRITICAL BREAKTHROUGH: Database Persistence Fixed

### ✅ MAJOR ISSUES RESOLVED TODAY

**Database Persistence Problem SOLVED:**
- **Root Cause:** Database was stored in ephemeral directory, wiped on every Railway deployment
- **Solution:** Moved database to `/data/lumaprints_pricing.db` (Railway persistent volume)
- **Result:** Database now persists across deployments - pricing data will never be lost again
- **Products Restored:** 1,452 products with all pricing data intact
- **Backup Created:** Database backup committed to git repo at `static/lumaprints_pricing_restore.db`

**Pricing Tool ↔ Order Form Connection:**
- ✅ Both systems now use the same database at `/data/lumaprints_pricing.db`
- ✅ Price changes in Pricing Admin immediately reflect in order form
- ✅ Global markup (123%) applies correctly to all products
- ✅ Tested: Canvas 1.25" 10×10" shows correct price of $24.13

## 📊 Current System Status

### Database Statistics
- **Total Active Products:** 1,452
- **Categories:** 25
- **Average Cost:** $56.89
- **Average Customer Price:** $126.85 (with 123% markup)
- **Global Markup:** 123.0%

### Working Product Types (5/8 confirmed)
1. ✅ **Rolled Canvas Prints** - 793 products, pricing correct
2. ✅ **Canvas Prints** - 77 products (1.25", 1.5", 0.75"), pricing correct
3. ✅ **Fine Art Paper Prints** - 189 products (7 paper types), pricing correct
4. ✅ **Metal Prints** - 28 products, pricing correct
5. ✅ **Peel and Stick** - 26 products, pricing correct

### Partially Working (2/8)
6. ⚠️ **Framed Canvas Prints** - 96 products (2 options: frame size, color)
   - Dropdowns work but need full testing
   
7. ⚠️ **Framed Fine Art Paper** - 54 products (2 options: frame size, mat size)
   - **ISSUE:** Frame size dropdown showing ALL options instead of just 2 (0.875" and 1.25")
   - **ISSUE:** Some mat size combinations return empty product lists
   - **CAUSE:** Dual ID system (internal wizard IDs vs Lumaprints codes)

### Not Yet Tested (1/8)
8. ❓ **Foam-Mounted Fine Art Paper** - 189 products (1 option: paper type)

## 🔧 CRITICAL ISSUE: Dual ID System

### The Problem
The wizard uses TWO separate ID systems that don't align:

**System 1: Internal Wizard IDs**
- Stored in: `sub_option_1_id`, `sub_option_2_id`
- Used by: Wizard dropdowns and API queries
- Example IDs: 22, 23, 33, 66-69

**System 2: Lumaprints API Codes**
- Stored in: `lumaprints_subcategory_id`, `lumaprints_options` (JSON)
- Used by: Order fulfillment to Lumaprints
- Example IDs: 105001-105007, 64, 66-69

**Why This Breaks:**
- Products have Lumaprints codes but wizard queries by internal IDs
- Mapping between systems is incomplete/incorrect
- Dropdowns show options that don't have matching products
- Some valid combinations return empty results

### The Solution: USE ONLY LUMAPRINTS CODES

**Refactor Plan:**
1. Remove all `sub_option_1_id` / `sub_option_2_id` logic from wizard
2. Update wizard dropdowns to use `lumaprints_subcategory_id` directly
3. Update API queries to filter by `lumaprints_subcategory_id` instead of `sub_option_1_id`
4. Store mat/paper options in `lumaprints_options` JSON field
5. Eliminate internal ID mapping entirely

**Benefits:**
- One source of truth (Lumaprints codes)
- Dropdowns automatically show only valid options
- No more mapping errors
- Simpler, more maintainable code

## 🎨 Lumaprints Product Code Reference

### Framed Fine Art Paper (Product Type 4)
**Frame Sizes (Lumaprints Subcategory IDs):**
- 105001: 0.875" Black Frame
- 105002: 0.875" White Frame
- 105003: 0.875" Oak Frame
- 105005: 1.25" Black Frame
- 105006: 1.25" White Frame
- 105007: 1.25" Oak Frame

**Mat Sizes (Lumaprints Option IDs in JSON):**
- 64: No Mat
- 66: 1.5" mat on each side
- 67: 2.0" mat on each side
- 68: 2.5" mat on each side
- 69: 3.0" mat on each side

**Paper Types (Lumaprints Option IDs in JSON):**
- 27: Archival Matte
- 28: Hot Press
- 29: Cold Press
- 30: Semi-Gloss
- 31: Metallic
- 32: Glossy
- 33: Somerset Velvet
- 34: Canvas

### Canvas Prints (Product Type 1)
**Mounting Sizes (Lumaprints Subcategory IDs):**
- 101001: 0.75" Canvas
- 101002: 1.25" Canvas
- 101003: 1.5" Canvas

### Framed Canvas (Product Type 2)
**Frame Sizes (Lumaprints Subcategory IDs):**
- 102001: 0.75" Framed Canvas
- 102002: 1.25" Framed Canvas
- 102003: 1.5" Framed Canvas

**Frame Colors (Lumaprints Option IDs in JSON):**
- 12: Black
- 13: White
- 91: Oak

## 📦 Database Structure

### Current Schema (Persistent at /data/)
```sql
products (
  id INTEGER PRIMARY KEY,
  name TEXT,
  product_type_id INTEGER,  -- 1-8 for product categories
  category_id INTEGER,
  size TEXT,
  cost_price REAL,
  
  -- INTERNAL IDs (TO BE REMOVED)
  sub_option_1_id INTEGER,  -- ← Remove this
  sub_option_2_id INTEGER,  -- ← Remove this
  
  -- LUMAPRINTS CODES (USE THESE)
  lumaprints_subcategory_id INTEGER,  -- ← Use this for dropdowns
  lumaprints_options TEXT,  -- ← JSON with mat/paper/color options
  
  active INTEGER  -- 1 = active, 0 = inactive
)

settings (
  id INTEGER PRIMARY KEY,
  key_name TEXT UNIQUE,
  value TEXT
)
-- Current: global_markup_percentage = 123.0

product_types (
  id INTEGER PRIMARY KEY,
  name TEXT,
  sub_option_1_name TEXT,
  sub_option_2_name TEXT
)

sub_options (
  id INTEGER PRIMARY KEY,
  product_type_id INTEGER,
  level INTEGER,  -- 1 or 2
  option_type TEXT,
  name TEXT,
  value TEXT
)
-- NOTE: This table may become obsolete after refactor
```

### Product Counts by Category
- Canvas - 1.25" Stretched: 31 products
- Canvas - 1.5" Stretched: 25 products
- Canvas - 0.75" Stretched: 21 products
- Canvas - Rolled: 793 products
- Framed Canvas (all): 96 products
- Fine Art Paper (all types): 189 products
- Framed Fine Art (all): 54 products
- Foam Mounted (all types): 189 products
- Metal Prints: 28 products
- Peel & Stick: 26 products

## 🚀 Deployment Information

**Platform:** Railway (auto-deploys from GitHub main branch)
**Production URL:** https://fifth-element-photography-production.up.railway.app/
**Custom Domain:** https://fifthelement.photos/
**Pricing Admin:** https://fifthelement.photos/admin/pricing
**Order Form:** https://fifth-element-photography-production.up.railway.app/hierarchical_order_form

**GitHub Repository:** https://github.com/heur1konrc/fifth-element-photography.git

**Persistent Volume:** `/data/` (mounted by Railway)
**Database Location:** `/data/lumaprints_pricing.db` (352KB, 1,452 products)
**Database Backup:** `static/lumaprints_pricing_restore.db` (committed to git)
**Restore Endpoint:** `/restore-database-from-backup`

## 📝 Recent Changes (Oct 21, 2025)

### Critical Commits Made Today

1. **"Fix database persistence - use /data volume"** (commit 34fda72)
   - Changed all database connections to `/data/lumaprints_pricing.db`
   - Updated app.py, pricing_admin.py, pricing_data_manager.py, dynamic_pricing_calculator.py

2. **"Add automatic database initialization on startup"** (commit 5941573)
   - Added `ensure_database_exists()` function
   - Creates `/data/` directory automatically
   - Initializes empty database if missing

3. **"URGENT: Copy old database to /data/"** (commit a433de9)
   - Added logic to migrate existing database to persistent volume
   - Attempted to preserve data (but old file was already gone)

4. **"Add database restore endpoint with backup"** (commit 298f9b0)
   - Created `/restore-database-from-backup` endpoint
   - Committed 352KB database backup to git
   - Successfully restored all 1,452 products with pricing ✅

## ⚠️ Known Issues

### 1. Framed Fine Art Frame Size Dropdown
- **Problem:** Shows ALL frame sizes instead of just 2 (0.875" and 1.25")
- **Cause:** `sub_options` table has unused entries (IDs 22-29)
- **Solution:** Refactor to use Lumaprints codes, eliminate sub_options table

### 2. Mat Size Combinations Return Empty
- **Problem:** 1.25" frame + mat sizes (1.5", 2.0", 2.5", 3.0") return no products
- **Cause:** Products exist but `sub_option_2_id` mapping is incorrect
- **Solution:** Query by `lumaprints_options` JSON field instead

### 3. Dual ID System Complexity
- **Problem:** Two ID systems create mapping confusion
- **Impact:** Dropdowns show invalid options, queries return empty results
- **Solution:** Eliminate internal IDs entirely, use only Lumaprints codes

## 🎯 Next Steps (Priority Order)

### IMMEDIATE: Refactor to Lumaprints Codes
1. [ ] Update `/api/hierarchical/available-sizes` to query by `lumaprints_subcategory_id`
2. [ ] Modify `hierarchical_ordering_system.js` to use Lumaprints codes in dropdowns
3. [ ] Remove `sub_option_1_id` / `sub_option_2_id` logic from wizard
4. [ ] Parse `lumaprints_options` JSON for mat/paper/color filtering
5. [ ] Test all 8 product types with new system
6. [ ] Remove or deprecate `sub_options` table

### AFTER REFACTOR: Complete Testing
7. [ ] Test Framed Fine Art with all frame + mat combinations
8. [ ] Test Framed Canvas with all frame + color combinations
9. [ ] Test Foam-Mounted with all paper types
10. [ ] Verify pricing displays correctly for all products
11. [ ] Confirm markup changes apply immediately

### FUTURE: Additional Features
12. [ ] Connect to OrderDesk API for order submission
13. [ ] Integrate payment processing (Stripe)
14. [ ] Add image dimension detection for size filtering
15. [ ] Implement shopping cart persistence

## 💡 Lessons Learned

1. **Always use persistent storage** - Ephemeral directories lose data on deployment
2. **Commit database backups to git** - Saved us from losing 1,452 products today
3. **Avoid dual ID systems** - One source of truth prevents mapping errors
4. **Document everything immediately** - Context loss between sessions is expensive
5. **Test persistence early** - Don't assume cloud platforms persist files

## 📞 Support & Resources

**Manus Support:** https://help.manus.im (for billing/credits questions)
**Railway Docs:** https://docs.railway.app/
**Lumaprints API:** Contact Lumaprints for API documentation

---
**Current Status:** Database persistence FIXED ✅ | Pricing connected ✅ | Refactor NEEDED ⚠️
**Next Action:** Refactor wizard to use Lumaprints codes directly

