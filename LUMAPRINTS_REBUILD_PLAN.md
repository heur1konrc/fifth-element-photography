# Lumaprints-Only Database Rebuild Plan
**Created:** October 21, 2025 9:15 PM CDT
**Status:** READY TO EXECUTE

## 🎯 OBJECTIVE

Rebuild the product database from scratch using **ONLY Lumaprints codes and prices**. Eliminate all internal ID mappings and the sub_options system that has caused endless cross-reference nightmares.

## 🔥 CRITICAL CONTEXT

**Current Problem:**
- Products use internal IDs (sub_option_1_id, sub_option_2_id) that don't match Lumaprints codes
- Sub_options table shows options that don't have products
- Product names don't match their assigned IDs
- Constant data mismatches and errors

**The Solution:**
- Use ONLY Lumaprints product codes (subcategory IDs, option IDs)
- Scrape prices directly from Lumaprints pricing grids (NO formulas, NO estimating)
- Dropdowns show what Lumaprints offers
- What customer selects = what gets sent to Lumaprints

**Non-Negotiables:**
1. ✅ All prices come from Lumaprints pricing grids on their website
2. ✅ Pricing Tool must allow editing individual product prices
3. ✅ Pricing Tool must allow global markup adjustments
4. ✅ Database must persist in `/data/` on Railway
5. ✅ No formulas, no calculations, no estimating prices

## 📋 THE PLAN

### **Step 1: Get Products from Lumaprints API**

**What to do:**
- Query Lumaprints API for all product categories
- Extract Lumaprints product codes:
  - Subcategory IDs (e.g., 101001 = 0.75" Canvas, 105001 = 0.875" Black Frame)
  - Option IDs (e.g., 64 = No Mat, 66 = 1.5" Mat, 12 = Black Frame Color)
- Get available sizes for each product type
- Store product structure with Lumaprints codes

**Lumaprints Product Code Reference:**

**Canvas Prints (Product Type 1):**
- 101001: 0.75" Stretched Canvas
- 101002: 1.25" Stretched Canvas
- 101003: 1.5" Stretched Canvas

**Framed Canvas (Product Type 2):**
- 102001: 0.75" Framed Canvas
- 102002: 1.25" Framed Canvas
- 102003: 1.5" Framed Canvas
- Frame Colors (options): 12 = Black, 13 = White, 91 = Oak

**Fine Art Paper (Product Type 3):**
- Paper Types (options): 27 = Archival Matte, 28 = Hot Press, 29 = Cold Press, 30 = Semi-Gloss, 31 = Metallic, 32 = Glossy, 33 = Somerset Velvet, 34 = Canvas

**Framed Fine Art Paper (Product Type 4):**
- 105001: 0.875" Black Frame
- 105002: 0.875" White Frame
- 105003: 0.875" Oak Frame
- 105005: 1.25" Black Frame
- 105006: 1.25" White Frame
- 105007: 1.25" Oak Frame
- Mat Sizes (options): 64 = No Mat, 66 = 1.5" mat, 67 = 2.0" mat, 68 = 2.5" mat, 69 = 3.0" mat
- Paper Types (options): Same as Fine Art Paper above

**Metal Prints (Product Type 5):**
- TBD from API

**Peel & Stick (Product Type 6):**
- TBD from API

**Foam-Mounted Fine Art (Product Type 7):**
- Paper Types (options): Same as Fine Art Paper above

**Rolled Canvas (Product Type 8):**
- TBD from API

### **Step 2: Scrape Prices from Lumaprints Website**

**Pricing Grid URLs:**
- Canvas: https://www.lumaprints.com/canvas-prints
- Framed Canvas: https://www.lumaprints.com/framed-canvas-prints
- Fine Art Paper: https://www.lumaprints.com/fine-art-paper
- Framed Fine Art: https://www.lumaprints.com/framed-fine-art-paper
- Metal: https://www.lumaprints.com/metal-prints
- Peel & Stick: https://www.lumaprints.com/peel-and-stick-prints
- Foam-Mounted: https://www.lumaprints.com/foam-mounted-fine-art-paper

**What to extract:**
- Size (e.g., "8×10", "11×14", "16×20")
- Price for each product type/depth combination
- Example from Canvas grid:
  - 8×10" / 1.25" Stretched = $10.99
  - 8×10" / 1.5" Stretched = $12.09
  - 8×10" / 0.75" Stretched = $9.89

**How to match:**
- Size + Lumaprints subcategory ID = unique product
- Store as cost_price in database
- Example: Canvas 1.25" 8×10" → lumaprints_subcategory_id=101002, size="8×10", cost_price=10.99

### **Step 3: Create New Database Schema**

**New products table structure:**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    product_type_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    size TEXT NOT NULL,
    cost_price REAL NOT NULL,
    
    -- LUMAPRINTS CODES (ONLY SOURCE OF TRUTH)
    lumaprints_subcategory_id INTEGER,  -- Frame depth, canvas depth, etc.
    lumaprints_options TEXT,  -- JSON: {"mat_size": 66, "paper_type": 27, "frame_color": 12}
    
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- NO MORE sub_option_1_id or sub_option_2_id columns!
```

**Keep these tables:**
- `settings` (for global_markup_percentage)
- `categories` (for grouping products in Pricing Admin)
- `product_types` (for top-level product categories)

**Remove these tables:**
- `sub_options` (no longer needed - query products directly)

### **Step 4: Populate Database with Scraped Data**

**Process:**
1. For each product type (Canvas, Framed Canvas, etc.):
   - Get Lumaprints codes from API
   - Get prices from pricing grid
   - Create product entries

2. Example product creation:
```python
# Canvas 1.25" 8×10" = $10.99 from Lumaprints grid
{
    "name": "Canvas 1.25\" 8×10\"",
    "product_type_id": 1,
    "category_id": 2,  # "Canvas - 1.25" Stretched"
    "size": "8×10\"",
    "cost_price": 10.99,
    "lumaprints_subcategory_id": 101002,
    "lumaprints_options": null,  # Canvas has no additional options
    "active": 1
}

# Framed Fine Art 0.875" Black Frame, 1.5" Mat, Archival Matte, 8×10" = $XX.XX
{
    "name": "Framed Fine Art 0.875\" Black Frame 1.5\" Mat Archival Matte 8×10\"",
    "product_type_id": 4,
    "category_id": 15,  # "Framed Fine Art - 0.875" Frame"
    "size": "8×10\"",
    "cost_price": 25.95,  # From Lumaprints grid
    "lumaprints_subcategory_id": 105001,  # 0.875" Black Frame
    "lumaprints_options": "{\"mat_size\": 66, \"paper_type\": 27}",
    "active": 1
}
```

3. Import all combinations that exist in Lumaprints pricing grids

### **Step 5: Update Wizard Frontend**

**Current wizard flow (BROKEN):**
1. Select product type → loads sub_options for level 1
2. Select sub_option 1 (internal ID) → loads sub_options for level 2
3. Select sub_option 2 (internal ID) → loads products
4. API queries by sub_option_1_id and sub_option_2_id

**New wizard flow (LUMAPRINTS-ONLY):**
1. Select product type → query products for distinct lumaprints_subcategory_id
2. Select subcategory (Lumaprints code) → query products for distinct lumaprints_options
3. Select options (Lumaprints codes) → load final product list
4. API queries by lumaprints_subcategory_id and lumaprints_options

**API endpoint changes:**

**OLD:**
```
GET /api/hierarchical/sub-options/4/1
Returns: sub_options table entries (internal IDs)

GET /api/hierarchical/available-sizes?product_type_id=4&sub_option_1_id=22&sub_option_2_id=66
Returns: products filtered by internal IDs
```

**NEW:**
```
GET /api/lumaprints/subcategories/4
Returns: DISTINCT lumaprints_subcategory_id from products table
Example: [105001, 105002, 105003] (0.875" frames only)

GET /api/lumaprints/options/4?subcategory_id=105001
Returns: DISTINCT lumaprints_options from products table
Example: [{"mat_size": 64}, {"mat_size": 66}, {"mat_size": 67}]

GET /api/lumaprints/products?product_type_id=4&subcategory_id=105001&mat_size=66
Returns: products filtered by Lumaprints codes
```

**Frontend JavaScript changes:**
- Update `hierarchical_ordering_system.js` to call new API endpoints
- Store Lumaprints codes instead of internal IDs in currentSelections
- Build dropdown options from actual products, not sub_options table

### **Step 6: Test All Product Types**

**Testing checklist:**
- [ ] Canvas Prints (3 depths: 0.75", 1.25", 1.5")
- [ ] Framed Canvas (3 depths × 3 colors = 9 combinations)
- [ ] Fine Art Paper (7 paper types)
- [ ] Framed Fine Art (3 frame sizes × 5 mat sizes × 7 paper types = 105 combinations)
- [ ] Metal Prints
- [ ] Peel & Stick
- [ ] Foam-Mounted Fine Art (7 paper types)
- [ ] Rolled Canvas

**For each product type:**
1. ✅ Dropdown shows only options with products
2. ✅ Prices match Lumaprints pricing grids exactly
3. ✅ Selecting options loads correct products
4. ✅ No empty product lists
5. ✅ Lumaprints codes are correct for order submission

### **Step 7: Verify Pricing Tool Still Works**

**Must verify:**
- [ ] Pricing Admin shows all products grouped by category
- [ ] Can edit individual product cost_price
- [ ] Can adjust global markup percentage
- [ ] Changes persist in `/data/lumaprints_pricing.db`
- [ ] Order form reflects price changes immediately

## 🔧 TECHNICAL DETAILS

### Files to Modify

**Backend (Python):**
- `app.py` - Add new Lumaprints API endpoints, update existing endpoints
- Create `scrape_lumaprints_pricing.py` - Script to scrape pricing grids
- Create `import_lumaprints_products.py` - Script to populate database

**Frontend (JavaScript):**
- `static/js/hierarchical_ordering_system.js` - Update to use Lumaprints codes

**Database:**
- `init_pricing_db.py` - Update schema to remove sub_option columns
- Create migration script to backup old data and create new schema

### Lumaprints API Integration

**Check if API exists:**
- Look in `lumaprints_api.py` for existing API client
- If API provides pricing, use it instead of scraping
- If API doesn't provide pricing, scrape from website

**API endpoints to use (if available):**
- Get product categories
- Get subcategories (frame depths, canvas depths, etc.)
- Get options (mat sizes, paper types, frame colors)
- Get available sizes

### Scraping Strategy

**If no API or API doesn't have pricing:**
1. Use BeautifulSoup to parse Lumaprints pricing pages
2. Extract HTML tables with size/price data
3. Parse product names to extract Lumaprints codes
4. Store in structured format for import

**Example scraping code:**
```python
import requests
from bs4 import BeautifulSoup

def scrape_canvas_pricing():
    url = "https://www.lumaprints.com/canvas-prints"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find pricing table
    table = soup.find('table', class_='pricing-table')
    
    # Extract rows
    for row in table.find_all('tr')[1:]:  # Skip header
        cols = row.find_all('td')
        size = cols[0].text.strip()
        price_125 = float(cols[1].text.strip().replace('$', ''))
        price_150 = float(cols[2].text.strip().replace('$', ''))
        price_075 = float(cols[3].text.strip().replace('$', ''))
        
        # Create products
        products.append({
            'size': size,
            'subcategory_id': 101002,
            'price': price_125
        })
        # ... repeat for other depths
```

## 📦 BACKUP STATUS

**Current database backed up:**
- File: `lumaprints_pricing_backup_20251021_211335.db`
- Size: 364KB
- Products: 1,420 active products
- Location: Committed to GitHub
- Status: ✅ SAFE

**Backup contains:**
- All current products with pricing
- Global markup: 123%
- Categories and product types
- Settings

**Restore command (if needed):**
```bash
cp lumaprints_pricing_backup_20251021_211335.db /data/lumaprints_pricing.db
```

## 🚀 EXECUTION ORDER

**Phase 1: Preparation (30 min)**
1. Check if Lumaprints API provides pricing
2. If not, test scraping one pricing grid (Canvas)
3. Verify data extraction works correctly

**Phase 2: Data Collection (1 hour)**
1. Scrape all 8 product type pricing grids
2. Extract Lumaprints codes from API or documentation
3. Match sizes to codes
4. Store in JSON files for review

**Phase 3: Database Rebuild (30 min)**
1. Create new schema (remove sub_option columns)
2. Import products with Lumaprints codes and scraped prices
3. Verify all products imported correctly
4. Test Pricing Admin still works

**Phase 4: Frontend Update (1 hour)**
1. Create new API endpoints for Lumaprints codes
2. Update JavaScript to use new endpoints
3. Test dropdowns show correct options
4. Verify products load with correct pricing

**Phase 5: Testing (30 min)**
1. Test all 8 product types
2. Verify prices match Lumaprints grids
3. Test Pricing Tool modifications
4. Test global markup changes

**Total estimated time: 3-4 hours**

## ✅ SUCCESS CRITERIA

**The rebuild is successful when:**
1. ✅ All products use ONLY Lumaprints codes (no internal IDs)
2. ✅ All prices match Lumaprints pricing grids exactly
3. ✅ Dropdowns show only options that have products
4. ✅ No empty product lists or errors
5. ✅ Pricing Tool can edit individual prices
6. ✅ Pricing Tool can adjust global markup
7. ✅ Changes persist in `/data/` database
8. ✅ Order form reflects pricing changes immediately
9. ✅ Customer selections map directly to Lumaprints order codes

## 🔴 CRITICAL NOTES

**DO NOT:**
- ❌ Estimate or calculate prices - ALL prices from Lumaprints grids
- ❌ Use formulas for pricing
- ❌ Keep internal ID system
- ❌ Rely on sub_options table

**DO:**
- ✅ Scrape exact prices from Lumaprints website
- ✅ Use ONLY Lumaprints product codes
- ✅ Query products table directly for dropdowns
- ✅ Test thoroughly before declaring success

## 📞 NEXT STEPS

**When ready to proceed:**
1. User adds more credits to Manus account
2. Resume from Phase 1: Check Lumaprints API for pricing
3. If API doesn't have pricing, start scraping pricing grids
4. Follow execution order above

**Current status:** READY TO EXECUTE - Backup complete, plan documented

---
**Last Updated:** October 21, 2025 9:20 PM CDT
**Document Status:** COMPLETE - Ready for execution

