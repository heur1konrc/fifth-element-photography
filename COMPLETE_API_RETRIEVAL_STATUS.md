# Complete Lumaprints API Retrieval & Database Build

**Date:** October 23, 2025  
**Status:** ✅ COMPLETE

---

## Objective

Retrieve ALL product data from Lumaprints Sandbox API and build a complete database to support the dynamic ordering form.

---

## Critical Requirements

1. ✅ Use Lumaprints Sandbox API credentials provided
2. ✅ Get ALL categories, subcategories, and options
3. ✅ Build database schema to store all data
4. ✅ **DID NOT TOUCH** the admin pricing tool or its database

---

## API Credentials

- **API Key:** e909ca3adc5026beb5dc306020ffe3068cf0e5962d31303137373136
- **API Secret:** 23ab680f283aeabd077e2d31303137373136
- **Base URL:** https://us.api-sandbox.lumaprints.com/api/v1

---

## Phase 1: Complete API Data Retrieval ✅

### Step 1: Get All Categories ✅
- Endpoint: `/products/categories`
- Result: **7 categories**

### Step 2: Get All Subcategories for Each Category ✅
- Endpoint: `/products/categories/{categoryId}/subcategories`
- Result: **44 subcategories**

### Step 3: Get All Options for Each Subcategory ✅
- Endpoint: `/products/subcategories/{subcategoryId}/options`
- Result: **168 option groups, 913 total options**

### Step 4: Save Complete Data Structure ✅
- Saved to: `/home/ubuntu/lumaprints_complete_data.json`
- File size: Complete product catalog

---

## Phase 2: Database Schema Design ✅

### Tables Created:
1. **categories** - 7 top-level product categories
2. **subcategories** - 44 product types within categories
3. **option_groups** - 168 groups of options (e.g., "Mat Size", "Paper Type")
4. **options** - 99 unique option choices
5. **products** - For storing size/price combinations (ready for pricing import)
6. **product_options** - Many-to-many relationship between products and options
7. **metadata** - System information and sync timestamps

---

## Phase 3: Database Creation ✅

- **Database file:** `data/lumaprints_orders.db` (separate from pricing tool)
- **Status:** Created and populated

---

## Phase 4: Data Import ✅

**Import Results:**
- ✅ 7 categories imported
- ✅ 44 subcategories imported
- ✅ 168 option groups imported
- ✅ 99 unique options imported

---

## Complete Product Catalog

### 1. Canvas (Category ID: 101)
- **Subcategories:** 4
  - Rolled Canvas (101005)
  - 0.75" Stretched Canvas (101001)
  - 1.25" Stretched Canvas (101002)
  - 1.50" Stretched Canvas (101003)
- **Option Groups:** 1 per subcategory
- **Total Options:** 4 option groups

### 2. Framed Canvas (Category ID: 102)
- **Subcategories:** 3
  - 0.75" Framed Canvas (102001) - 4 option groups
  - 1.25" Framed Canvas (102002) - 4 option groups
  - 1.50" Framed Canvas (102003) - 5 option groups
- **Total Options:** 13 option groups

### 3. Fine Art Paper (Category ID: 103)
- **Subcategories:** 7
  - Archival Matte (103001)
  - Hot Press (103002)
  - Cold Press (103003)
  - Semi-Glossy (103005)
  - Metallic (103006)
  - Glossy (103007)
  - Somerset Velvet (103009)
- **Option Groups:** 1 per subcategory
- **Total Options:** 7 option groups

### 4. Framed Fine Art Paper (Category ID: 105)
- **Subcategories:** 19 frame types
  - 0.875"x0.875" Black, White, Oak
  - 1.25"x0.875" Black, White, Oak
  - 0.875"x1.125" Natural Wood, Gold, Espresso
  - 0.75"x1.125" Black, White
  - 2"x1.0625" Framer's Choice
  - 3"x0.875" Concerto
  - 1.125"x0.75" Slimwoods (2 types)
  - 3"x1" Driftwood (2 types)
  - 2.5625"x1" Plein Air
  - 3.250"x1.375" Vintage Copper
- **Option Groups:** 7 per frame type
  - Mat Size (10 options)
  - Paper Type (9 options)
  - Hanging Hardware (3 options)
  - Backing (2 options)
  - Mat Color (14 options)
  - Glazing (2 options)
  - Print Mounting (2 options)
- **Total Options:** 133 option groups

### 5. Metal (Category ID: 106)
- **Subcategories:** 2
  - Glossy White Metal Print (106001)
  - Glossy Silver Metal Print (106002)
- **Option Groups:** 1 per subcategory
- **Total Options:** 2 option groups

### 6. Peel and Stick (Category ID: 107)
- **Subcategories:** 1
  - Peel and Stick Art Print (107001)
- **Option Groups:** 0 (no customization options)
- **Total Options:** 0 option groups

### 7. Foam-mounted Fine Art Paper (Category ID: 108)
- **Subcategories:** 8
  - Archival Matte (108001)
  - Hot Press (108002)
  - Cold Press (108003)
  - Semi-Glossy (108005)
  - Metallic (108006)
  - Glossy (108007)
  - Somerset Velvet (108009)
  - Canvas (108010)
- **Option Groups:** 1 per subcategory
- **Total Options:** 8 option groups

---

## Database Structure Summary

```
categories (7)
├── subcategories (44)
    ├── option_groups (168)
        └── options (99 unique)
```

---

## Next Steps

1. ✅ Create API endpoints to query this database
2. ⏳ Build dynamic form that reads from this database
3. ⏳ Import size/price data for products table
4. ⏳ Connect form to Lumaprints order submission API

---

## Files Created

1. ✅ `/home/ubuntu/lumaprints_complete_data.json` - Complete API data
2. ✅ `data/lumaprints_orders.db` - Database with all product structure
3. ✅ `COMPLETE_API_RETRIEVAL_STATUS.md` - This status document

---

## Database Verification

```sql
SELECT COUNT(*) FROM categories;     -- 7
SELECT COUNT(*) FROM subcategories;  -- 44
SELECT COUNT(*) FROM option_groups;  -- 168
SELECT COUNT(*) FROM options;        -- 99
```

---

**Completed:** October 23, 2025 01:30 CDT  
**Duration:** ~15 minutes  
**Status:** ✅ SUCCESS - All data retrieved and imported

