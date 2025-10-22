# Pricing Tool Integration Plan

## Current Status (Phase 1: Get Form Working)

### What's Deployed NOW
- **Route:** `/print-order` (new, uncached)
- **API:** `/api/print-order/products` 
- **Pricing:** Calculated on-the-fly: `retail_price = cost_price × 1.50` (50% markup)
- **Database:** Railway database at `/data/lumaprints_pricing.db` (1420 products)
- **Schema Issue:** Database missing `retail_price` column, only has `cost_price`

### Testing
Once deployed, test at:
```
https://fifth-element-photography-production.up.railway.app/print-order?image=https://fifthelement.photos/images/12x12_Sparrow.jpg
```

Expected result: Form displays all 1420 products with calculated prices

---

## Future Phase 2: Integrate Pricing Tool

### Pricing Tool Location
**URL:** https://fifthelement.photos/admin/pricing

### Pricing Tool Features
1. **Global Markup Control**
   - Input field for markup percentage
   - "UPDATE" button to apply globally
   - Formula: `retail_price = cost_price × (1 + markup/100)`
   - Example: 50% markup = cost × 1.50

2. **Product Management**
   - View all 1420 products organized by category
   - Edit individual product costs
   - Add/remove products
   - Add/remove categories

3. **Statistics Dashboard**
   - Total products count
   - Categories count
   - Average cost
   - Average customer price

### Integration Options

#### Option A: Shared Database (RECOMMENDED)
- Point Railway app to the same database as pricing tool
- Both apps read/write to same database
- Pricing tool updates are immediately available to order form
- Requires finding where pricing tool database is hosted

#### Option B: API Integration
- Pricing tool exposes API endpoint
- Railway app fetches prices via API
- More complex but keeps systems separate

#### Option C: Database Sync
- Add `retail_price` column to Railway database
- Create sync script to copy prices from pricing tool
- Run sync periodically or on-demand

### Implementation Steps (Option A)

1. **Find Pricing Tool Database**
   - Determine where https://fifthelement.photos stores its data
   - Get connection details

2. **Update Railway Database Schema**
   ```sql
   ALTER TABLE products ADD COLUMN retail_price REAL;
   ```

3. **Migrate Data**
   - Copy retail prices from pricing tool database
   - Or recalculate using current markup setting

4. **Update Order API**
   - Change from calculated prices to reading `retail_price` column
   - Still support fallback calculation if `retail_price` is NULL

5. **Test Workflow**
   - Change markup in pricing tool
   - Click UPDATE
   - Verify order form shows updated prices

### User Workflow (After Integration)

1. User goes to https://fifthelement.photos/admin/pricing
2. User adjusts markup percentage (e.g., from 50% to 75%)
3. User clicks "UPDATE" button
4. System recalculates all 1420 retail prices
5. Order form at Railway immediately shows new prices
6. User can also edit individual product costs
7. Changes propagate to order form

---

## Technical Notes

### Current Database Schema (Railway)
```
products table:
- id
- category_id
- name
- size
- cost_price ✅ (exists)
- retail_price ❌ (missing - need to add)
- description
- active
- created_at
- product_type_id
- sub_option_1_id
- sub_option_2_id
- combination_id
- lumaprints_subcategory_id
- lumaprints_options
- lumaprints_frame_option
```

### Settings Table
```
settings table:
- id
- key_name
- value

Key: 'global_markup_percentage'
Value: '50.0' (or whatever user sets)
```

### Pricing Tool Database Schema (Unknown)
Need to investigate:
- Where is it hosted?
- What's the connection string?
- Does it have the same schema?
- How does the UPDATE button work?

---

## Action Items

### Immediate (Phase 1)
- [x] Deploy working order form with calculated prices
- [ ] Test form displays all products
- [ ] Verify prices are calculated correctly (cost × 1.5)

### Future (Phase 2)
- [ ] Investigate pricing tool database location
- [ ] Add `retail_price` column to Railway database
- [ ] Implement pricing tool integration
- [ ] Test UPDATE button workflow
- [ ] Document for user how to manage prices

---

## Questions to Answer

1. Where is the pricing tool database hosted?
2. Is it the same database as Railway or separate?
3. Can we point Railway to that database?
4. How does the pricing tool UPDATE button work currently?
5. Does the pricing tool already have the 1420 products?

