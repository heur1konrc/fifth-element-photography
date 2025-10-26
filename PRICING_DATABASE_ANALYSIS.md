# Pricing Database Analysis

**Export Date:** 2025-10-26  
**Database:** `/data/lumaprints_pricing.db`

## Summary

- **Total Products:** 762 (all active)
- **Categories:** 24
- **Product Variants:** 256 (frame options for Framed Canvas products)
- **Sub Options:** 35
- **Global Markup:** 0% (prices match Lumaprints cost)

## Database Structure

### Products Table
```
- id: INTEGER
- category_id: INTEGER (links to categories table)
- name: TEXT
- size: TEXT (e.g., "10×20")
- cost_price: REAL (Lumaprints wholesale cost)
- price: REAL (retail price shown to customers)
- lumaprints_subcategory_id: INTEGER (for API calls)
- lumaprints_frame_option: INTEGER (nullable, for framed products)
- lumaprints_options: TEXT (JSON string, usually "{}")
- active: INTEGER (1 = active, 0 = inactive)
- created_at: TIMESTAMP
```

### Categories Table
```
- id: INTEGER
- name: TEXT (e.g., "Canvas - 1.25\" Stretched")
- description: TEXT
- created_at: TIMESTAMP
```

### Product Variants Table
```
- id: INTEGER
- product_id: INTEGER (links to products table)
- variant_name: TEXT (e.g., "Maple Wood")
- variant_description: TEXT (e.g., "Maple Wood Floating Frame")
- price_modifier: DECIMAL (added to base price, usually 0)
- is_default: BOOLEAN
- created_at: TIMESTAMP
```

## Categories Breakdown

### Canvas Products (4 categories, 280 products total)
1. **Canvas - 1.25" Stretched** (31 products)
   - Sizes: Various
   - Price range: $24.13 - $XXX
   - Lumaprints subcategory: 101002

2. **Canvas - 1.5" Stretched** (27 products)
   - Price range: TBD

3. **Canvas - 0.75" Stretched** (21 products)
   - Price range: TBD

4. **Canvas - Rolled** (25 products)
   - Price range: TBD

### Framed Canvas Products (3 categories, 256 variants)
5. **Framed Canvas - 0.75"** (products + frame variants)
6. **Framed Canvas - 1.25"** (products + frame variants)
7. **Framed Canvas - 1.5"** (products + frame variants)

### Fine Art Paper Products (7 categories, 189 products)
8-14. Various paper types (Archival Matte, Hot Press, Cold Press, Semi-Gloss, Metallic, Glossy, Somerset Velvet)
   - 27 products each
   - Price ranges vary by paper type

### Foam Mounted Products (7 categories, 189 products)
15-21. Various paper types mounted on foam
   - 27 products each
   - Higher prices than unmounted

### Other Categories (3 categories, 0 products)
22. **Framed Fine Art - 0.875" Frame** (0 products - not populated)
23. **Metal Prints** (0 products - not populated)
24. **Peel & Stick** (0 products - not populated)

## Key Findings

1. **Pricing Structure:**
   - `cost_price` = Lumaprints wholesale cost
   - `price` = Customer retail price
   - Currently `price` == `cost_price` (0% markup)
   - Global markup setting exists but is set to 0

2. **Lumaprints Integration:**
   - Each product has `lumaprints_subcategory_id` for API calls
   - Framed products have `lumaprints_frame_option` for frame selection
   - `lumaprints_options` field stores additional options as JSON

3. **Product Variants:**
   - 256 variants exist (mostly frame options)
   - Variants have `price_modifier` (usually $0)
   - Used for Framed Canvas products to show different frame styles

4. **Missing Data:**
   - Metal Prints, Peel & Stick, and Framed Fine Art categories are empty
   - These need to be populated if you want to offer them

## Next Steps for Pricing API

The pricing endpoint needs to:
1. Accept: `category_id` or `lumaprints_subcategory_id`, `size`, `variant_id` (optional)
2. Query the `products` table for base price
3. Add `price_modifier` if variant is selected
4. Apply global markup percentage (currently 0%)
5. Return: `cost_price`, `retail_price`, `markup_percentage`

## Sample Product Record

```json
{
  "id": 3,
  "category_id": 1,
  "name": "Canvas 1.25\" Stretched Canvas",
  "size": "10×20",
  "cost_price": 24.13,
  "price": 24.13,
  "lumaprints_subcategory_id": 101002,
  "lumaprints_frame_option": null,
  "lumaprints_options": "{}",
  "active": 1,
  "created_at": "2025-10-25 17:56:18"
}
```

## Sample Variant Record

```json
{
  "id": 241,
  "product_id": 404,
  "variant_name": "Maple Wood",
  "variant_description": "Maple Wood Floating Frame",
  "price_modifier": 0,
  "is_default": 1,
  "created_at": "2025-10-19 04:13:57"
}
```

