# Session Oct 26, 2025 - Pricing Display Fix

## 🎯 PROJECT INFO

**Website:** https://fifth-element-photography-production.up.railway.app/  
**Public Domain:** https://fifthelement.photos  
**Repository:** https://github.com/heur1konrc/fifth-element-photography.git  
**Local Path:** `/home/ubuntu/fifth-element-photography`  
**Deployment:** Railway (auto-deploys from main branch)  
**GitHub Classic Token:** [Stored securely - ask user if needed]

---

## ✅ WHAT WE ACCOMPLISHED TODAY

### 🎉 SUCCESS: PRICING DISPLAY NOW WORKING!

**Before:** No prices showing on size buttons  
**After:** All sizes display with correct prices from database

**Example Working Output:**
- 10×20" - $62.38
- 10×30" - $75.34
- 11×14" - $45.17
- 12×12" - $50.85

---

## 🔧 FIXES IMPLEMENTED

### 1. Disabled Broken Image Quality Check
**File:** `templates/order_form.html` (lines 448-515)  
**Problem:** Lumaprints `/api/v1/images/checkImageConfig` endpoint was hanging  
**Solution:** Commented out entire image quality check section  
**Critical Note:** When re-enabling, MUST use FULL PATH to FULL SIZE HIRES IMAGE, NOT thumbnails

**Commit:** "Disable image quality check to prevent form hanging"

### 2. Changed Size Source from Generated to Database
**File:** `templates/order_form.html` (displaySizes function)  
**Problem:** Form was generating sizes dynamically based on aspect ratio  
**Solution:** Rewrote to fetch sizes+prices from `/api/pricing/category/{subcategory_id}`  

**Before:**
```javascript
// Generated sizes based on aspect ratio
for (let shortSide = minSize; shortSide <= maxSize; shortSide += 2) {
    const longSide = Math.round(shortSide * aspectRatio);
    sizes.push({ width, height, name: `${shortSide}x${longSide}"` });
}
```

**After:**
```javascript
// Fetch from pricing database
const response = await fetch(`/api/pricing/category/${subcategoryId}`);
const data = await response.json();
data.products.forEach(product => {
    // Display size with price from database
});
```

**Commit:** "Fix: Fetch sizes and prices from pricing database instead of generating dynamically"

### 3. Fixed Database Query Column
**File:** `pricing_api.py` (line 141)  
**Problem:** API was querying by internal `category_id` instead of `lumaprints_subcategory_id`  
**Solution:** Changed WHERE clause to use correct column

**Before:**
```python
WHERE p.category_id = ?
```

**After:**
```python
WHERE p.lumaprints_subcategory_id = ?
```

**Commit:** "Fix: Query by lumaprints_subcategory_id instead of category_id"

---

## 📊 HOW IT WORKS NOW

### Data Flow
1. **User selects product type:** "Framed Canvas" (from Lumaprints API)
2. **User selects subcategory:** "1.50in Framed Canvas" → subcategoryId: `102003` (from Lumaprints API)
3. **Form fetches sizes+prices:** `GET /api/pricing/category/102003` (from YOUR database)
4. **Display sizes with prices:** Shows all available sizes for that subcategory with retail prices

### Subcategory ID Mapping
**Lumaprints API → Your Pricing Database:**
- `102001`: 0.75in Framed Canvas
- `102002`: 1.25in Framed Canvas
- `102003`: 1.50in Framed Canvas

All three exist in your pricing database with sizes and prices.

### Database Structure
**Location:** `/data/lumaprints_pricing.db` (Railway persistent volume)

**Products Table:**
- 762 rows total
- Columns: `id`, `name`, `size`, `price` (retail), `cost_price`, `lumaprints_subcategory_id`
- Size format: Uses `×` symbol (e.g., "8×10", "12×18")

**Current Pricing Data:**
- Canvas (101002)
- Framed Canvas 0.75" (102001) - Black/White/Oak
- Framed Canvas 1.25" (102002) - Black/White/Oak
- Framed Canvas 1.50" (102003) - Black/White/Oak
- Fine Art Paper (103001)

---

## 🔄 NEXT STEPS (When You Return)

### Phase 1: Options Pricing
**Goal:** Add flat fees for frame options

**Options to Price:**
- Frame Style (Maple, Espresso, Natural, Oak, Silver, Gold, White, Black) - NO BASE PRICE
- Hanging Hardware (Wire, Backboard, Security, Loose) - ADD FLAT FEE (e.g., $1.60)
- Canvas Border (Image Wrap, Mirror, Solid Color) - NO BASE PRICE
- Canvas Underlayer (None, Foamcore) - ADD FLAT FEE if selected

**Implementation:**
1. Create options pricing table in database or config
2. Fetch options from Lumaprints API
3. Display options with prices
4. Calculate: Base price + option fees
5. Display subtotal

### Phase 2: Global Markup
**Goal:** Apply markup percentage to final price

**Implementation:**
1. Get markup percentage from admin settings
2. Calculate: (Base price + options) × (1 + markup%)
3. Display final total

### Phase 3: Checkout Integration
**Goal:** Accept payment and create order

**Implementation:**
1. Integrate payment gateway (PayPal/Stripe)
2. Collect customer shipping info
3. Generate order confirmation
4. Send to OrderDesk

### Phase 4: OrderDesk Integration
**Goal:** Format and submit orders to Lumaprints

**Lumaprints Order Format:**
```
Image URL: [full path to /data/images/IMG_5555.JPG]
print_sku: 102003
print_width: 8
print_height: 12
lumaprints_options: 1,16,9,93
```

**Option ID Mapping:**
- Canvas Border: 1 (Image Wrap), etc.
- Hanging Hardware: 16 (Wire), etc.
- Canvas Underlayer: 9 (None), etc.
- Frame Style: 93 (Maple), etc.

---

## 🐛 KNOWN ISSUES

### Fixed Today
- ✅ Image quality check hanging
- ✅ Sizes not showing
- ✅ Prices not showing
- ✅ Wrong subcategory ID query

### Still To Fix
- ⚠️ Aspect ratio display shows "1.50" instead of "3:2"
- ⚠️ Image quality check needs full-size image path when re-enabled

---

## 📝 CRITICAL NOTES FOR NEXT SESSION

1. **DO NOT regenerate sizes** - they come from the pricing database
2. **Subcategory IDs must match** between Lumaprints API and pricing database
3. **Size format in database** uses `×` symbol (Unicode U+00D7), not `x`
4. **Image quality check** is disabled - must use full-size image path when re-enabling
5. **Pricing database** is on Railway persistent volume at `/data/lumaprints_pricing.db`

---

## 🚀 DEPLOYMENT COMMANDS

```bash
cd /home/ubuntu/fifth-element-photography

# Check status
git status

# Stage changes
git add .

# Commit
git commit -m "Your message here"

# Push to GitHub (triggers Railway auto-deploy)
git push https://[TOKEN]@github.com/heur1konrc/fifth-element-photography.git main

# Check Railway deployment
# Wait ~2-3 minutes for build and deploy
```

---

## 📂 KEY FILES MODIFIED

1. **templates/order_form.html**
   - Line 379: `displaySizes()` function
   - Lines 448-515: Image quality check (commented out)

2. **pricing_api.py**
   - Line 116: `get_category_products()` function
   - Line 141: Changed to query by `lumaprints_subcategory_id`

---

## ✅ VERIFICATION CHECKLIST

**Test the working flow:**
1. Go to: https://fifthelement.photos/order?image=IMG_5555.JPG
2. Click "Framed Canvas"
3. Click "1.50in Framed Canvas"
4. Verify sizes display with prices (10×20" $62.38, etc.)
5. All size buttons should show prices immediately

**If prices don't show:**
1. Open browser console (F12)
2. Check Network tab for `/api/pricing/category/102003` call
3. Verify it returns 200 OK
4. Check Response tab - should have `products` array with data
5. If `products: []`, check database has correct subcategory IDs

---

**Session End Time:** ~8:00 AM CST  
**Status:** ✅ PRICING DISPLAY WORKING - Ready for options integration  
**Next Session:** Continue with options pricing and markup calculation

