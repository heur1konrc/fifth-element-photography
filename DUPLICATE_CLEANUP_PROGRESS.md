# Duplicate Size Cleanup - Progress Report

**Date:** October 25, 2025  
**Issue:** Catalog showing 4 duplicate cards for each size  
**Repository:** https://github.com/heur1konrc/fifth-element-photography  
**Live Site:** https://fifthelement.photos/

---

## 🔍 PROBLEM IDENTIFIED

### Initial Symptoms
- Catalog page shows **77 total sizes** (should be ~25-30)
- "Stretched Canvas 0.75"" product shows **44 size cards** (should be 11)
- Each size appears **4 times** with identical pricing (e.g., four 8×10 cards)
- "Remove Duplicate Orientations" button runs but doesn't fix the issue

### Root Cause Discovery
After investigation, found that the database stores **BOTH orientations** separately:
- **8×10** (vertical) AND **10×8** (horizontal)
- **11×14** (vertical) AND **14×11** (horizontal)
- **12×16** (vertical) AND **16×12** (horizontal)
- etc.

**Database Query Results:**
```sql
SELECT p.name, s.width, s.height, s.orientation, COUNT(*) 
FROM pictorem_sizes s 
JOIN pictorem_products p ON s.product_id = p.id 
WHERE p.id = 1 
GROUP BY s.width, s.height;
```

Shows 22 entries for "Stretched Canvas 0.75"" - both 8×10 AND 10×8 exist as separate records.

### Why This Happens
- The `pictorem_sizes` table has a UNIQUE constraint on `(product_id, width, height)`
- This prevents TRUE duplicates (same width, height, product)
- BUT it allows orientation duplicates (8×10 vs 10×8)
- For canvas prints, orientation doesn't matter - they can be hung either way
- So we only need ONE entry per size dimension

---

## 🛠️ SOLUTION IMPLEMENTED

### Changes Made

#### 1. Added Debug Endpoint (Commit: 9682e13)
**File:** `pictorem_admin.py`  
**Endpoint:** `/api/debug_duplicates` (GET)

Shows exactly what duplicates exist in the database:
```json
{
  "total_sizes": 77,
  "duplicate_groups": 0,
  "total_duplicates_to_delete": 0
}
```

This confirmed NO exact duplicates exist (same product_id, width, height).

#### 2. Fixed Cleanup Function (Commit: 03935f9)
**File:** `pictorem_admin.py`  
**Function:** `api_cleanup_duplicate_orientations()`

**Old Logic (WRONG):**
```sql
-- Looked for exact duplicates only
SELECT product_id, width, height, COUNT(*) 
FROM pictorem_sizes
GROUP BY product_id, width, height
HAVING COUNT(*) > 1
```
This found NOTHING because 8×10 and 10×8 are different width/height values.

**New Logic (CORRECT):**
```sql
-- Finds orientation duplicates (8x10 vs 10x8)
SELECT DISTINCT s1.id as id_to_delete
FROM pictorem_sizes s1
JOIN pictorem_sizes s2 ON 
    s1.product_id = s2.product_id AND
    s1.width = s2.height AND
    s1.height = s2.width AND
    s1.id > s2.id
WHERE s1.width < s1.height
```

This finds entries where:
- Same product
- Width and height are swapped (8×10 vs 10×8)
- Keeps the one with lower ID (typically horizontal orientation)
- Deletes the duplicate orientation

---

## 📊 EXPECTED RESULTS

### Before Cleanup
- **Total Sizes:** 77
- **Stretched Canvas 0.75":** 22 sizes (both orientations)
- **Catalog Display:** 44 cards (showing both orientations as separate options)

### After Cleanup
- **Total Sizes:** ~38-40 (removing ~37 orientation duplicates)
- **Stretched Canvas 0.75":** 11 sizes (one per dimension)
- **Catalog Display:** 11 cards per product

### Size List (Expected After Cleanup)
Each product should show ONE entry for each of these sizes:
- 8×10
- 11×14
- 12×16
- 16×20
- 18×24
- 20×24
- 20×30
- 24×30
- 24×36
- 30×40
- 36×48

---

## ✅ DEPLOYMENT STATUS

### Commits Pushed
1. **9682e13** - Add debug endpoint to view duplicate sizes data
2. **03935f9** - Fix cleanup function to remove orientation duplicates (8x10 vs 10x8)

### Railway Deployment
- **Status:** Deploying (in progress)
- **Branch:** main
- **Auto-deploy:** Enabled

---

## 🎯 NEXT STEPS

1. **Wait for Railway deployment to complete** (~2 minutes)
2. **Test the cleanup function:**
   - Go to https://fifthelement.photos/admin/database
   - Click "Remove Duplicate Orientations" button
   - Should see: "Deleted X sizes, Y remaining"
3. **Verify the catalog:**
   - Go to https://fifthelement.photos/admin/catalog
   - Check "Stretched Canvas 0.75"" product
   - Should show exactly 11 size cards (not 44)
4. **Sync prices** for remaining products if needed

---

## 📝 TECHNICAL NOTES

### Database Schema
```sql
CREATE TABLE pictorem_sizes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    orientation TEXT NOT NULL,
    display_name TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES pictorem_products(id),
    UNIQUE(product_id, width, height)
);
```

### Key Files Modified
- `/home/ubuntu/fifth-element-photography/pictorem_admin.py`

### API Endpoints
- `GET /api/debug_duplicates` - View duplicate data
- `POST /api/cleanup_duplicate_orientations` - Remove orientation duplicates

---

## 🚨 IMPORTANT NOTES

- **This is NOT a Lumaprints issue** - The project has switched to Pictorem
- **Database location:** `/data/pictorem.db` (Railway persistent volume)
- **The cleanup is SAFE** - It only removes orientation duplicates, not actual size data
- **Pricing data** associated with deleted sizes will also be removed
- **After cleanup**, may need to re-sync prices for affected products

---

**Last Updated:** October 25, 2025 - REAL FIX FOUND!

## 🎉 ACTUAL ROOT CAUSE FOUND

The problem was in the **import script** (`import_pictorem_products.py`), not the cleanup function!

The script was importing BOTH orientations:
```python
standard_sizes = [
    (8, 10), (10, 8),  # ← BOTH ORIENTATIONS!
    (11, 14), (14, 11),
    ...
]
```

**Fix Applied:** Modified import script to only import ONE orientation per size.

**Next Step:** Click "Force Re-Initialize" button on database admin page to rebuild database with correct data.

**Commits:**
- 9682e13 - Add debug endpoint
- 03935f9 - Fix cleanup function (didn't work)
- 3dcc891 - **FIX IMPORT SCRIPT** (the real fix!)

