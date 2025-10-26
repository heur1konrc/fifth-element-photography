# Database Structure Analysis

## Database Path: `/data/lumaprints_pricing.db`

## Tables Found:

### 1. categories (24 rows)
- id (INTEGER)
- name (TEXT)
- description (TEXT)
- created_at (TIMESTAMP)

### 2. products (762 rows) ✅
- id (INTEGER)
- category_id (INTEGER)
- name (TEXT)
- size (TEXT)
- price (REAL)
- cost_price (REAL)
- lumaprints_subcategory_id (INTEGER)
- lumaprints_frame_option (INTEGER)
- lumaprints_options (TEXT)
- active (INTEGER)
- created_at (TIMESTAMP)

### 3. product_variants (256 rows) ✅
- id (INTEGER)
- product_id (INTEGER)
- variant_name (VARCHAR(100))
- variant_description (TEXT)
- price_modifier (DECIMAL(10,2))
- is_default (BOOLEAN)
- created_at (TIMESTAMP)

### 4. settings (1 row)
- key (TEXT)
- value (TEXT)
- updated_at (TIMESTAMP)

### 5. sub_options (35 rows)
- id (INTEGER)
- product_type_id (INTEGER)
- level (INTEGER)
- option_type (VARCHAR(50))
- name (VARCHAR(100))
- value (VARCHAR(100))
- image_path (VARCHAR(255))
- display_order (INTEGER)
- active (BOOLEAN)
- created_at (TIMESTAMP)

### 6. pricing (0 rows) - EMPTY
### 7. import_log (0 rows) - EMPTY
### 8. sub_option_combinations (0 rows) - EMPTY

## Key Findings:

✅ Database EXISTS at `/data/lumaprints_pricing.db`
✅ 762 products with prices
✅ 256 product variants (frame options)
✅ Products linked to Lumaprints via `lumaprints_subcategory_id`

## What We Need:

The pricing API should query:
1. **products** table - for base prices by category/subcategory/size
2. **product_variants** table - for frame/option price modifiers
3. **settings** table - for global markup percentage

