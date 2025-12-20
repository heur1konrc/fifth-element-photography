# Frame Color Configuration

## Current Frame Colors by Canvas Depth

### 0.75" Framed Canvas
- Black (`black_floating_075`)
- White (`white_floating_075`)
- Silver (`silver_floating_075`)
- Gold (`gold_plein_air`)

### 1.25" Framed Canvas
- Black (`black_floating_125`)
- White (`white_floating_125`)
- Oak (`oak_floating_125`)

### 1.50" Framed Canvas
- Black (`black_floating_150`)
- White (`white_floating_150`)
- Oak (`oak_floating_150`)

## Shopify Product Type Naming

Frame colors are flattened into the product type name to work around Shopify's 3-option limit:

**Format:** `"{depth} Framed Canvas {color}"`

**Examples:**
- `0.75" Framed Canvas Black`
- `0.75" Framed Canvas White`
- `0.75" Framed Canvas Silver`
- `0.75" Framed Canvas Gold`
- `1.25" Framed Canvas Black`
- `1.25" Framed Canvas White`
- `1.25" Framed Canvas Oak`
- `1.50" Framed Canvas Black`
- `1.50" Framed Canvas White`
- `1.50" Framed Canvas Oak`

## Size Availability

Framed canvas products start at **8×12"** (no 4×6" or smaller sizes).

Available sizes: 8×12, 12×12, 12×18, 16×24, 20×20, 24×36, 30×30, 32×48, 38×38, 40×40, 40×60, 48×48

## Pricing

All frame colors have the same price for a given canvas size/depth. Frame color does not affect pricing.

Pricing is stored in:
- `base_pricing` table: Base cost for canvas size/depth
- `option_pricing` table: Additional cost for frame option (currently $0.00 for all colors)

## Database Tables

### product_options
Contains frame color options with:
- `option_group`: e.g., "0.75\" Frame Style"
- `option_name`: e.g., "black_floating_075"
- `display_name`: e.g., "0.75\" Black Floating Frame"

### subcategory_options
Links frame options to canvas subcategories

### option_pricing
Stores additional cost for frame options (subcategory_id, option_id, cost_price)
