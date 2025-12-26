# Fifth Element Photography: Complete Product Management Manual

**Version**: 1.0  
**Last Updated**: December 25, 2025  
**Purpose**: Complete workflow documentation for adding and managing products from creation to Shopify sync

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [The Complete Workflow](#3-the-complete-workflow)
4. [Tool 1: Create Shopify Products](#4-tool-1-create-shopify-products)
5. [Tool 2: Lumaprints Bulk Mapping](#5-tool-2-lumaprints-bulk-mapping)
6. [Tool 3: Shopify Price Sync](#6-tool-3-shopify-price-sync)
7. [Troubleshooting](#7-troubleshooting)
8. [Data Sources & Technical Details](#8-data-sources--technical-details)
9. [Emergency Contacts & Rollback](#9-emergency-contacts--rollback)

---

## 1. Overview

This manual documents the complete process for managing products in the Fifth Element Photography e-commerce system. The workflow involves three main tools that work together to create products, map images, and sync pricing between your local database, Lumaprints, and Shopify.

### The Three Core Tools

| Tool | Purpose | Location |
|------|---------|----------|
| **Create Shopify Products** | Generate Shopify product CSV from your images and pricing database | Admin Dashboard → Shopify Tab |
| **Lumaprints Bulk Mapping** | Map gallery images to Lumaprints products in bulk | Admin Dashboard → Shopify Tab (or Tools Tab) |
| **Shopify Price Sync** | Synchronize prices from local database to live Shopify store | Admin Dashboard → Shopify Tab |

### Why Three Tools?

Each tool serves a specific purpose in the product lifecycle:

1. **Create Shopify Products**: Creates the initial product listings in Shopify with all variants (sizes, frame colors, etc.)
2. **Lumaprints Bulk Mapping**: Links your gallery images to Lumaprints products for print fulfillment
3. **Shopify Price Sync**: Updates prices across all Shopify products when you adjust markup or costs

---

## 2. Prerequisites

Before you begin, ensure you have:

### Required Access
- ✅ Admin access to Fifth Element Photography admin dashboard
- ✅ Shopify store admin access
- ✅ Lumaprints account with product export permissions

### Required Data
- ✅ Gallery images uploaded to the system
- ✅ Images assigned to portfolios and categories
- ✅ Pricing database (`print_ordering.db`) configured with:
  - Product types and sizes
  - Cost prices for each product
  - Global markup percentage
  - Frame options for framed products

### Required Knowledge
- Basic understanding of product variants (size, frame color, etc.)
- Familiarity with CSV file imports
- Understanding of aspect ratios (3:2, 2:3, 1:1)

---

## 3. The Complete Workflow

Here's the big picture of how products flow through the system:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCT MANAGEMENT WORKFLOW                   │
└─────────────────────────────────────────────────────────────────┘

STEP 1: CREATE PRODUCTS IN SHOPIFY
┌──────────────────────────────────────────────────────────────┐
│ 1. Upload images to gallery                                  │
│ 2. Assign images to portfolios/categories                    │
│ 3. Use "Create Shopify Products" tool                        │
│ 4. Download generated CSV file                               │
│ 5. Import CSV into Shopify                                   │
└──────────────────────────────────────────────────────────────┘
                              ↓
STEP 2: MAP IMAGES TO LUMAPRINTS
┌──────────────────────────────────────────────────────────────┐
│ 1. Export unmapped products from Lumaprints (.xlsx)          │
│ 2. Use "Lumaprints Bulk Mapping" tool                        │
│ 3. Upload Lumaprints .xlsx file                              │
│ 4. Map images to product titles                              │
│ 5. Download mapped .xlsx file                                │
│ 6. Import mapped file back to Lumaprints                     │
└──────────────────────────────────────────────────────────────┘
                              ↓
STEP 3: SYNC PRICES (WHEN NEEDED)
┌──────────────────────────────────────────────────────────────┐
│ 1. Update costs or markup in pricing database                │
│ 2. Use "Shopify Price Sync" tool                             │
│ 3. Wait for sync to complete (~5-10 minutes)                 │
│ 4. Verify prices updated in Shopify                          │
└──────────────────────────────────────────────────────────────┘
```

### When to Use Each Tool

**Create Shopify Products**:
- Adding new images to your store
- Creating product listings for a new portfolio
- Regenerating products after pricing database changes

**Lumaprints Bulk Mapping**:
- After creating new Shopify products
- When Lumaprints shows unmapped products
- After adding new product types to Lumaprints

**Shopify Price Sync**:
- After changing global markup percentage
- After updating cost prices in database
- When Shopify prices don't match local database

---

## 4. Tool 1: Create Shopify Products

### Purpose
This tool generates a Shopify-compatible CSV file containing all product variants for your selected images. It reads from your pricing database to determine available sizes, frame options, and prices.

### Location
**Admin Dashboard → Shopify Tab → "Create Shopify Products" button**

---

### Step-by-Step Instructions

#### Step 1: Prepare Your Images

Before creating products, ensure your images are properly configured:

1. **Upload images** to the gallery (Admin → Images tab)
2. **Assign portfolios** to each image (e.g., "Nature", "Landscapes")
3. **Assign categories** to each image (e.g., "Print Ready", "Featured")
4. **Set image titles and descriptions** (used in Shopify product listings)

**Important**: Only images with assigned portfolios will appear in the product creation tool.

#### Step 2: Access the Tool

1. Navigate to **Admin Dashboard**
2. Click the **Shopify** tab in the main navigation
3. In the left sidebar, find **"Shopify Actions"** section
4. Click the **"Create Shopify Products"** button

#### Step 3: Select Images

The tool will display all images from your gallery organized by portfolio.

1. **Review the image list** - Each image shows:
   - Thumbnail preview
   - Filename
   - Title
   - Assigned portfolios
   - Assigned categories

2. **Select images** for product creation:
   - Click individual checkboxes to select specific images
   - Or use **"Select All"** to include all images

3. **Review selection count** - The tool shows how many images are selected

**Tip**: You can create products for a specific portfolio by selecting only images from that portfolio.

#### Step 4: Generate CSV

1. Click the **"Generate Shopify CSV"** button
2. Wait for processing (usually 5-30 seconds depending on number of images)
3. A success message will appear with:
   - Number of products created
   - Number of variants created
   - Download link

#### Step 5: Download CSV

1. Click the **"Download CSV"** button
2. Save the file (default name: `shopify_products_YYYYMMDD_HHMMSS.csv`)
3. **Do not edit the CSV file** - it's formatted specifically for Shopify import

#### Step 6: Import to Shopify

1. Log in to your **Shopify Admin**
2. Navigate to **Products** → **Import**
3. Click **"Add file"** and select your downloaded CSV
4. Choose **"Overwrite existing products that have the same handle"** (if updating)
5. Click **"Upload and continue"**
6. Review the import preview
7. Click **"Import products"**
8. Wait for Shopify to process (can take several minutes for large imports)

**Success**: You'll see a confirmation showing how many products were imported.

---

### What Gets Created?

For each selected image, the tool creates:

#### Product Structure
- **Product Title**: Based on image title (e.g., "Mountain Sunset")
- **Product Type**: "Photography Print"
- **Vendor**: "Fifth Element Photography"
- **Tags**: Generated from portfolios and categories
- **Description**: From image description field

#### Product Variants

The tool creates variants for every combination of:

**For Canvas Products**:
- **Size options**: All sizes defined in pricing database (e.g., 8x10, 11x14, 16x20)
- **Single variant per size** (no frame options for canvas)

**For Framed Canvas Products**:
- **Size options**: All sizes defined in pricing database
- **Frame color options**: All frame colors defined for that product type
  - Example: 1.25" Framed Canvas might have Black, Walnut, Oak
- **Multiple variants per size** (one for each frame color)

**For Metal Prints**:
- **Size options**: All sizes defined in pricing database
- **Single variant per size**

**For Art Paper Products**:
- **Size options**: All sizes defined in pricing database
- **Paper type**: Hot Press, Cold Press, or Smooth Fine Art Paper
- **Multiple variants per size** (one for each paper type)

#### Pricing

Each variant's price is calculated as:
```
Final Price = Cost Price × Global Markup Multiplier
```

**Example**:
- Cost: $45.00
- Markup: 2.5× (250%)
- Final Price: $112.50

---

### Understanding the CSV Structure

The generated CSV follows Shopify's product import format:

| Column | Purpose | Example |
|--------|---------|---------|
| Handle | Unique product identifier | `mountain-sunset` |
| Title | Product name | `Mountain Sunset` |
| Body (HTML) | Product description | `<p>Beautiful mountain at sunset...</p>` |
| Vendor | Store name | `Fifth Element Photography` |
| Product Category | Shopify taxonomy | `Arts & Entertainment > Hobbies & Creative Arts > Arts & Crafts` |
| Type | Product type | `Photography Print` |
| Tags | Search/filter tags | `Nature, Landscapes, Print Ready` |
| Published | Visibility | `TRUE` |
| Option1 Name | First variant option | `Printed Product` |
| Option1 Value | Variant option value | `0.75" Stretched Canvas` |
| Option2 Name | Second variant option | `Size` |
| Option2 Value | Size value | `16x20` |
| Option3 Name | Third variant option | `Frame Color` (if applicable) |
| Option3 Value | Frame color value | `Black` (if applicable) |
| Variant Price | Calculated price | `112.50` |
| Variant Inventory Qty | Stock quantity | `0` (print-on-demand) |
| Variant Inventory Policy | Stock handling | `continue` (allow backorders) |
| Image Src | Product image URL | `https://your-site.com/gallery-image/mountain-sunset.jpg` |
| Image Position | Image order | `1` |
| Variant Image | Variant-specific image | (same as Image Src) |

---

### Important Notes

#### Frame Options Are Database-Driven

**Frame colors come ONLY from the pricing database**, not from any hardcoded list or Lumaprints catalog.

To add or remove frame options:
1. Access the pricing database (`print_ordering.db`)
2. Update the `product_options` table
3. Link options to the correct product subcategory
4. Regenerate the CSV

**Example**: If you want to add "White" frame to 1.25" Framed Canvas:
1. Add "White" to `product_options` table
2. Link it to "1.25\" Framed Canvas" subcategory
3. Add pricing for White frame variants
4. Regenerate CSV - White will now appear as an option

#### Product Availability

Only products marked as `is_available = TRUE` in the pricing database will be included in the CSV.

To hide a product type:
1. Update `is_available = FALSE` in database
2. Regenerate CSV
3. That product type won't appear for any images

#### Image Requirements

Images must meet these requirements to be included:
- ✅ Uploaded to gallery
- ✅ Has at least one portfolio assigned
- ✅ Has a title (used as product name)
- ✅ File is accessible at `/data/{filename}`

---

### Common Issues & Solutions

**Issue**: No products generated
- **Check**: Are images assigned to portfolios?
- **Check**: Is pricing database accessible?
- **Check**: Are any products marked as available in database?

**Issue**: Missing frame colors
- **Check**: Are frame options defined in `product_options` table?
- **Check**: Are options linked to correct subcategory?
- **Check**: Is pricing data present for those frame options?

**Issue**: Wrong prices in CSV
- **Check**: Global markup percentage in database
- **Check**: Cost prices for each product variant
- **Formula**: Final Price = Cost × Markup

**Issue**: Shopify import fails
- **Check**: CSV file not manually edited
- **Check**: Image URLs are accessible
- **Check**: Product handles are unique

---

## 5. Tool 2: Lumaprints Bulk Mapping

### Purpose
This tool automates the process of linking your gallery images to Lumaprints products for print fulfillment. Instead of manually mapping each product variation (Canvas 8x10, Canvas 11x14, Art Paper 8x10, etc.), you map once per image title, and the tool applies it to all variations automatically.

### Location
**Admin Dashboard → Shopify Tab → "Lumaprints Bulk Mapping" button** (also available in Tools Tab)

---

### Why This Tool Exists

**The Problem**: When you export unmapped products from Lumaprints, you might see 50+ rows for a single image:
- Mountain Sunset - 0.75" Stretched Canvas - 8x10
- Mountain Sunset - 0.75" Stretched Canvas - 11x14
- Mountain Sunset - 0.75" Stretched Canvas - 16x20
- Mountain Sunset - Hot Press Fine Art Paper - 8x10
- Mountain Sunset - Hot Press Fine Art Paper - 11x14
- ...and so on

Manually mapping each one is tedious and error-prone.

**The Solution**: Map "Mountain Sunset" to `mountain-sunset.jpg` once, and the tool automatically applies it to all 50+ variations.

---

### Step-by-Step Instructions

#### Step 1: Export Unmapped Products from Lumaprints

1. Log in to your **Lumaprints dashboard**
2. Navigate to **Products** or **Catalog** section
3. Look for **"Export"** or **"Download"** option
4. Select **"Unmapped Products Only"** (if available)
5. Choose **Excel (.xlsx)** format
6. Download the file (usually named something like `products_export.xlsx`)

**What's in this file**: Every product variation that doesn't have an image assigned in Lumaprints.

#### Step 2: Open the Bulk Mapping Tool

1. Navigate to **Admin Dashboard**
2. Click the **Shopify** tab (or **Tools** tab)
3. In the left sidebar, find **"Shopify Actions"** section
4. Click **"Lumaprints Bulk Mapping"** button

A modal window will open with three steps.

#### Step 3: Upload Your Lumaprints File

You'll see **Step 1: Upload Lumaprints Excel File**

1. Click **"Choose File"** button
2. Select the `.xlsx` file you downloaded from Lumaprints
3. Click **"Upload & Process"** button

**What happens**:
- The tool reads the Excel file
- Identifies all unmapped products
- Extracts unique product titles
- Shows you how many unmapped products were found

**Example output**: "Found 127 unmapped products across 3 unique titles"

The tool automatically advances to Step 2.

#### Step 4: Map Images to Product Titles

You'll now see **Step 2: Map Images to Products**

This is where you create the mappings between your gallery images and Lumaprints product titles.

**For each mapping, fill in three fields**:

1. **Product Title** (dropdown)
   - Select from the list of titles extracted from your Excel file
   - Example: "Mountain Sunset"

2. **Image Filename** (text input)
   - Enter the EXACT filename from your gallery
   - Example: `mountain-sunset.jpg`
   - **Must match exactly** - case-sensitive, include extension

3. **Aspect Ratio** (dropdown)
   - Choose the correct ratio for this image
   - Options: `3:2` (landscape), `2:3` (portrait), `1:1` (square)
   - **Important**: This ensures mapping applies to correct product variations

**To add more mappings**:
- Click **"+ Add Another Mapping"** button
- A new row appears
- Fill in the three fields
- Repeat for each unique product title

**Example mapping form**:
```
Product Title: Mountain Sunset
Image Filename: mountain-sunset.jpg
Aspect Ratio: 3:2

Product Title: Forest Path
Image Filename: forest-path.jpg
Aspect Ratio: 2:3

Product Title: Desert Bloom
Image Filename: desert-bloom.jpg
Aspect Ratio: 1:1
```

#### Step 5: Apply Mappings

1. Review your mappings for accuracy
2. Click **"✓ Apply All Mappings"** button

**What happens**:
- The tool processes each mapping
- Finds all product variations matching that title
- Applies the image filename to each variation
- Updates the in-memory Excel file
- Automatically advances to Step 3

**Example**: If "Mountain Sunset" has 42 variations (different sizes, product types), all 42 get mapped to `mountain-sunset.jpg` in one operation.

#### Step 6: Download Mapped File

You'll now see **Step 3: Download Mapped File**

1. Review the success message showing how many products were mapped
2. Click **"Download Excel File"** button
3. Save the file (default name: `lumaprints_mapped.xlsx`)

**What's in this file**: The same Excel structure as your upload, but now with image filenames filled in for all mapped products.

#### Step 7: Upload to Lumaprints

1. Return to your **Lumaprints dashboard**
2. Navigate to **Products** → **Import** (or similar)
3. Click **"Upload File"** or **"Import"**
4. Select your `lumaprints_mapped.xlsx` file
5. Confirm the import
6. Wait for Lumaprints to process (can take several minutes)

**Success**: Lumaprints will show a confirmation that products were updated with image mappings.

---

### Understanding the Mapping Logic

#### How the Tool Matches Products

When you map "Mountain Sunset" to `mountain-sunset.jpg`, the tool:

1. **Searches the Excel file** for all rows where the product title contains "Mountain Sunset"
2. **Filters by aspect ratio** (only maps to products matching your selected ratio)
3. **Updates the image column** in each matching row with `mountain-sunset.jpg`
4. **Preserves all other data** (SKU, price, size, product type, etc.)

#### Why Aspect Ratio Matters

Lumaprints products are organized by aspect ratio:
- **3:2 products**: 8x12, 12x18, 16x24, 20x30, etc.
- **2:3 products**: 12x8, 18x12, 24x16, 30x20, etc.
- **1:1 products**: 8x8, 12x12, 16x16, 20x20, etc.

If you map a 3:2 image to 2:3 products, the print will be cropped or distorted.

**Best practice**: Always verify your image's aspect ratio before mapping.

#### What Gets Mapped

The tool maps to **all product types** for that title:
- ✅ Stretched Canvas (all thicknesses)
- ✅ Framed Canvas (all frame options)
- ✅ Metal Prints
- ✅ Hot Press Fine Art Paper
- ✅ Cold Press Fine Art Paper
- ✅ Smooth Fine Art Paper
- ✅ All available sizes for each type

**You don't need to map each type separately** - one mapping covers everything.

---

### Common Issues & Solutions

**Issue**: Product title not in dropdown
- **Cause**: Title doesn't exist in uploaded Excel file
- **Solution**: Check Excel file for exact title spelling
- **Solution**: Re-export from Lumaprints to get latest data

**Issue**: Mapping not applied to some products
- **Cause**: Aspect ratio mismatch
- **Solution**: Verify image aspect ratio matches selected option
- **Solution**: Check if those products have different title variation

**Issue**: Lumaprints import fails
- **Cause**: Excel file structure was modified
- **Solution**: Don't edit the Excel file manually - use only the tool
- **Solution**: Re-export from Lumaprints and try again

**Issue**: Image filename not found in Lumaprints
- **Cause**: Filename doesn't match exactly
- **Solution**: Check for typos, case sensitivity, file extension
- **Solution**: Verify image exists in gallery at that exact filename

**Issue**: Some products still unmapped after import
- **Cause**: Those products weren't in the Excel file you processed
- **Solution**: Export unmapped products again from Lumaprints
- **Solution**: Run the tool again for remaining products

---

### Tips & Best Practices

**Tip 1: Verify Filenames**
Before mapping, check your gallery to confirm exact filenames. The tool is case-sensitive.

**Tip 2: Map in Batches**
If you have many products, map them in batches (e.g., by portfolio or date added). This makes troubleshooting easier.

**Tip 3: Keep Original Excel File**
Save a copy of the original Lumaprints export before uploading. If something goes wrong, you can start over.

**Tip 4: Check Aspect Ratios**
Use an image viewer or the Image Print Analysis tool (magnifying glass button in admin) to verify aspect ratios before mapping.

**Tip 5: Document Your Mappings**
Keep a simple text file listing which images map to which product titles. Helpful for future reference.

---

## 6. Tool 3: Shopify Price Sync

### Purpose
This tool synchronizes product prices from your local pricing database to your live Shopify store. Use it when you update cost prices or adjust your global markup percentage.

### Location
**Admin Dashboard → Shopify Tab → "Sync Prices to Shopify" button**

---

### When to Use This Tool

**Use the Price Sync tool when**:
- ✅ You change the global markup percentage
- ✅ You update cost prices in the pricing database
- ✅ Shopify prices don't match your local database
- ✅ You add new product variants to existing products
- ✅ Lumaprints changes their pricing and you update your costs

**Don't use this tool for**:
- ❌ Creating new products (use Create Shopify Products tool)
- ❌ Changing product descriptions or images
- ❌ Updating inventory quantities

---

### How It Works

The Price Sync tool:

1. **Reads your local pricing database** (`print_ordering.db`)
2. **Fetches all products from Shopify** via GraphQL API
3. **Matches each Shopify variant** to local database records
4. **Calculates correct prices** using: `Price = Cost × Markup`
5. **Updates Shopify** only for variants where price differs
6. **Reports results** showing what was updated

**Important**: This is a **one-way sync** from database → Shopify. It does not update your local database from Shopify.

---

### Step-by-Step Instructions

#### Step 1: Update Your Pricing Database (If Needed)

Before syncing, ensure your local pricing database is correct:

1. Navigate to **Admin Dashboard → Pricing Tab**
2. Review the **Global Markup** percentage
   - Current value is displayed at the top
   - Example: "Global Markup: 2.5× (250%)"

3. **To change markup**:
   - Click **"Edit Markup"** button
   - Enter new multiplier (e.g., `2.8` for 280%)
   - Click **"Save"**
   - Database is updated immediately

4. **To update cost prices**:
   - Access the pricing database directly (requires database tool)
   - Update `cost_price` values in relevant tables
   - Save changes

**Note**: Cost price updates typically require database access. Contact your developer if you need to change individual product costs.

#### Step 2: Initiate the Sync

1. On the **Shopify Tab**, in the left sidebar under **"Shopify Actions"**, locate the **"Sync Prices to Shopify"** button
2. Click the button
3. A confirmation dialog appears:
   ```
   Are you sure you want to sync prices to Shopify?
   This will update all product prices based on your current database.
   ```
4. Click **"OK"** to proceed (or "Cancel" to abort)

#### Step 3: Monitor Progress

A **Progress Monitor** modal appears showing:

- **Spinner animation** (indicates processing)
- **Progress bar** (visual feedback)
- **Status messages**:
  - "Connecting to Shopify..." (initial connection)
  - "Syncing prices..." (processing products)
  - "Sync complete!" (finished)
- **Timer** showing elapsed time
- **Real-time updates** (if available)

**Typical duration**: 5-10 minutes depending on number of products

**Do not close the browser tab** while sync is running.

#### Step 4: Review Results

When complete, the Progress Monitor shows:

- **✓ Success message** or **✗ Error message**
- **Products updated**: Number of Shopify products modified
- **Variants updated**: Number of individual variants modified
- **Duration**: Total time taken (e.g., "8.5 minutes")
- **Errors** (if any): List of variants that couldn't be matched

**Example success result**:
```
✓ Sync Complete!

Products Updated: 47
Variants Updated: 312
Duration: 8.5 minutes

No errors encountered.
```

**Example with errors**:
```
✓ Sync Complete (with warnings)

Products Updated: 45
Variants Updated: 298
Duration: 9.2 minutes

Errors (14 variants):
- "Mountain Sunset - 24x36 Metal Print" - No matching product in database
- "Forest Path - 30x40 Canvas" - No matching product in database
...
```

#### Step 5: Verify in Shopify

After sync completes:

1. Log in to **Shopify Admin**
2. Navigate to **Products**
3. Open a few products that should have been updated
4. Check variant prices match your expected calculations
5. Verify prices are correct for different sizes/options

**Formula to verify**:
```
Expected Price = Database Cost Price × Global Markup
```

**Example**:
- Cost: $45.00
- Markup: 2.5×
- Expected Shopify Price: $112.50

---

### Understanding the Matching Logic

#### How Variants Are Matched

The sync tool matches Shopify variants to database records using:

1. **Product Type** (e.g., "0.75\" Stretched Canvas")
2. **Size** (e.g., "16x20")
3. **Frame Color** (if applicable, e.g., "Black")

**Matching process**:
1. Tool extracts option values from Shopify variant
2. Strips common prefixes ("Printed Product - ", "Size - ")
3. Normalizes product type names (e.g., "0.75 Stretched Canvas" → "0.75\" Stretched Canvas")
4. Looks up in database using `(product_type, size, frame_color)` tuple
5. If match found, calculates and updates price

#### Product Name Normalization

The tool handles common naming inconsistencies:

| Shopify Name | Database Name | Normalized To |
|--------------|---------------|---------------|
| `0.75 Stretched Canvas` | `0.75" Stretched Canvas` | `0.75" Stretched Canvas` |
| `Metal` | `Metal Print` | `Metal Print` |
| `1.25 Framed Canvas` | `1.25" Framed Canvas` | `1.25" Framed Canvas` |
| `Hot Press Art Paper` | `Hot Press Fine Art Paper` | `Hot Press Fine Art Paper` |

**This normalization is critical** for matching to work correctly.

#### What Doesn't Get Updated

The sync tool **only updates prices**. It does not change:
- ❌ Product titles
- ❌ Product descriptions
- ❌ Product images
- ❌ Variant SKUs
- ❌ Inventory quantities
- ❌ Product availability (published/draft status)

---

### Technical Details

#### API & Performance

**Technology**:
- Uses Shopify **GraphQL Admin API**
- Paginated queries (handles large product catalogs)
- Batch updates for efficiency

**Rate Limits**:
- Shopify API has rate limits (typically 2 requests/second)
- Tool respects these limits automatically
- Large catalogs may take longer due to rate limiting

**Timeout**:
- Server timeout set to **10 minutes** (600 seconds)
- Sufficient for most stores (up to 1000+ products)
- If your store is larger, sync may need to be split into batches

#### Data Sources

**Local Database** (`/data/print_ordering.db`):
- Table: `product_pricing` (or similar)
- Columns: `product_type`, `size`, `frame_color`, `cost_price`, `is_available`
- Global markup stored in: `settings` table

**Shopify Store**:
- Accessed via GraphQL API
- Requires: Admin API access token
- Permissions: `read_products`, `write_products`

---

### Common Issues & Solutions

**Issue**: Sync times out after 10 minutes
- **Cause**: Too many products for single sync
- **Solution**: Contact developer to implement batch syncing
- **Workaround**: Sync specific product types separately (requires code modification)

**Issue**: Many variants show "No matching product in database"
- **Cause**: Product type names don't match between Shopify and database
- **Check**: Verify product type names in database match Shopify exactly
- **Solution**: Update `map_product_type_to_shopify()` function in code

**Issue**: Prices not updating for some variants
- **Cause**: Variant marked as unavailable in database
- **Check**: Verify `is_available = TRUE` for those products
- **Solution**: Update database to mark products as available

**Issue**: Wrong prices after sync
- **Cause**: Incorrect cost prices or markup in database
- **Check**: Verify cost prices in database
- **Check**: Verify global markup percentage
- **Recalculate**: Price = Cost × Markup

**Issue**: Sync button does nothing
- **Cause**: JavaScript error or API connection issue
- **Check**: Browser console for errors (F12 → Console tab)
- **Check**: Shopify API credentials are valid
- **Solution**: Refresh page and try again

**Issue**: "500 Internal Server Error"
- **Cause**: Server timeout or API error
- **Check**: Railway logs for error details
- **Solution**: Try again (may be temporary API issue)
- **Solution**: Contact developer if persists

---

### Tips & Best Practices

**Tip 1: Test with Small Changes**
Before syncing after major price changes, test with a small markup adjustment to verify everything works.

**Tip 2: Sync During Low Traffic**
Run price syncs during off-peak hours to minimize impact on customers browsing your store.

**Tip 3: Verify Before Syncing**
Always double-check your markup percentage and a few cost prices before clicking "Sync to Shopify".

**Tip 4: Keep a Price Log**
Document when you run syncs and what changes you made. Helpful for tracking pricing history.

**Tip 5: Monitor for Errors**
If you see errors in the sync results, investigate immediately. Unmatched variants won't have correct prices.

**Tip 6: Backup Before Major Changes**
Before making major pricing changes, consider exporting your Shopify products as a backup.

---

## 7. Troubleshooting

### General Troubleshooting Steps

When something goes wrong with any tool:

1. **Check browser console** (F12 → Console tab) for JavaScript errors
2. **Check Railway logs** for server-side errors
3. **Verify data sources** (database, files) are accessible
4. **Try refreshing** the page and attempting again
5. **Check API credentials** (Shopify, Lumaprints) are valid
6. **Review recent changes** to database or configuration

---

### Tool-Specific Issues

#### Create Shopify Products Issues

**Problem**: CSV generation fails
- Check: Pricing database accessible?
- Check: Images have portfolios assigned?
- Check: Database has available products?
- Solution: Review Railway logs for specific error

**Problem**: Shopify import fails
- Check: CSV file not manually edited?
- Check: Image URLs accessible from internet?
- Check: Product handles are unique?
- Solution: Try importing a single product first to isolate issue

**Problem**: Missing product variants
- Check: Are those sizes/options in pricing database?
- Check: Are they marked as available?
- Check: Are frame options linked to correct subcategory?
- Solution: Update database and regenerate CSV

---

#### Lumaprints Bulk Mapping Issues

**Problem**: Upload fails
- Check: File is .xlsx format (not .xls or .csv)?
- Check: File not corrupted?
- Check: File size under 10MB?
- Solution: Re-export from Lumaprints and try again

**Problem**: No product titles in dropdown
- Check: Excel file has unmapped products?
- Check: File structure matches expected format?
- Solution: Verify you exported "unmapped products" from Lumaprints

**Problem**: Mappings not applied
- Check: Image filename matches exactly (case-sensitive)?
- Check: Aspect ratio selected correctly?
- Check: Product title matches exactly?
- Solution: Review mapping form for typos

**Problem**: Lumaprints import fails
- Check: Downloaded file not manually edited?
- Check: File structure preserved?
- Solution: Start over - re-export, re-map, re-download

---

#### Shopify Price Sync Issues

**Problem**: Sync times out
- Cause: Too many products
- Solution: Contact developer for batch sync implementation
- Workaround: Reduce product count or sync specific types only

**Problem**: Prices not updating
- Check: Products exist in both Shopify and database?
- Check: Product type names match?
- Check: Variants marked as available in database?
- Solution: Review error list in sync results

**Problem**: Wrong prices after sync
- Check: Global markup percentage correct?
- Check: Cost prices in database correct?
- Formula: Verify Price = Cost × Markup
- Solution: Update database and re-sync

---

### Error Messages & Meanings

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "No matching product in database" | Shopify variant doesn't exist in pricing database | Add product to database or update product type name mapping |
| "Image not found" | Image file doesn't exist at specified path | Verify image uploaded and filename correct |
| "Database connection failed" | Can't access print_ordering.db | Check database file exists and permissions correct |
| "Shopify API error" | API request failed | Check API credentials and rate limits |
| "Invalid aspect ratio" | Aspect ratio doesn't match product | Verify image aspect ratio and select correct option |
| "File upload failed" | Excel file couldn't be processed | Check file format (.xlsx) and structure |
| "Timeout" | Operation took too long | Reduce batch size or contact developer |

---

## 8. Data Sources & Technical Details

### Pricing Database (`print_ordering.db`)

**Location**: `/data/print_ordering.db`  
**Type**: SQLite database  
**Purpose**: Master source of truth for all product pricing and availability

#### Key Tables

**`product_pricing`** (or similar):
- `product_type`: Product name (e.g., "0.75\" Stretched Canvas")
- `size`: Dimensions (e.g., "16x20")
- `frame_color`: Frame option (if applicable)
- `cost_price`: Base cost from supplier
- `is_available`: Whether product is offered (TRUE/FALSE)

**`product_options`**:
- `option_name`: Option name (e.g., "Black", "Walnut")
- `subcategory_id`: Links option to product type

**`settings`**:
- `global_markup`: Markup multiplier (e.g., 2.5 for 250%)

#### Price Calculation

```
Final Price = Cost Price × Global Markup
```

**Example**:
```
Cost Price: $45.00
Global Markup: 2.5
Final Price: $45.00 × 2.5 = $112.50
```

---

### Lumaprints Catalog

**File**: `lumaprints_catalog.json`  
**Type**: Static JSON reference  
**Purpose**: Reference for Lumaprints product IDs and names

**Important**: This file is **NOT** used for product creation. It's only a reference. The pricing database controls what products are created.

---

### Shopify Store

**Access**: Via Shopify Admin API  
**Authentication**: API access token (stored in environment variables)  
**Permissions Required**:
- `read_products`
- `write_products`
- `read_product_listings`
- `write_product_listings`

**API Endpoints Used**:
- GraphQL Admin API (for price sync)
- REST Admin API (for product creation)
- Bulk Import API (for CSV imports)

---

### File Locations

| File | Location | Purpose |
|------|----------|---------|
| Pricing Database | `/data/print_ordering.db` | Product pricing and availability |
| Lumaprints Catalog | `/lumaprints_catalog.json` | Reference data |
| Gallery Images | `/data/{filename}` | Original image files |
| Gallery Optimized | `/data/gallery-images/{filename}` | 1200px versions for web |
| Thumbnails | `/data/thumbnails/{filename}` | Admin thumbnails |
| Generated CSVs | `/tmp/shopify_products_*.csv` | Temporary CSV files |

---

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `SHOPIFY_STORE_URL` | Your Shopify store domain |
| `SHOPIFY_ACCESS_TOKEN` | API access token |
| `LUMAPRINTS_API_KEY` | Lumaprints API key (if used) |
| `DATABASE_PATH` | Path to print_ordering.db |

---

## 9. Emergency Contacts & Rollback

### If Something Goes Wrong

**Immediate Actions**:
1. **Don't panic** - Most issues are reversible
2. **Document the error** - Screenshot error messages
3. **Check logs** - Railway deployment logs show detailed errors
4. **Stop further actions** - Don't make more changes until issue is understood

---

### Rollback Procedures

#### Rollback Shopify Products

If you imported incorrect products to Shopify:

1. **Delete products in Shopify**:
   - Go to Shopify Admin → Products
   - Select products to delete (use bulk select)
   - Click "Delete products"

2. **Fix the issue** in your database or configuration

3. **Regenerate CSV** with correct data

4. **Re-import** to Shopify

**Note**: Shopify product deletion is permanent. Consider exporting products first as backup.

---

#### Rollback Lumaprints Mappings

If you uploaded incorrect mappings to Lumaprints:

1. **Export current products** from Lumaprints (to see what's mapped)

2. **Clear mappings** in Lumaprints (if available) or manually edit Excel file

3. **Re-run bulk mapping tool** with correct data

4. **Re-import** to Lumaprints

**Note**: Lumaprints may cache mappings. Contact their support if issues persist.

---

#### Rollback Price Sync

If prices synced incorrectly:

1. **Update database** with correct cost prices or markup

2. **Run Price Sync again** - it will overwrite incorrect prices

3. **Verify in Shopify** that prices are now correct

**Note**: Price sync is idempotent - running it multiple times is safe.

---

### Code Rollback

If a system update breaks functionality:

**Rollback via Git**:
```bash
cd /home/ubuntu/fifth-element-photography
git log --oneline  # Find commit to revert to
git revert <commit-hash>
git push
railway up
```

**Restore from Backup**:
- Contact your developer
- Provide backup timestamp
- Developer can restore from Railway backups

---

### Emergency Contacts

**Developer**: [Your Developer Contact]  
**Shopify Support**: https://help.shopify.com  
**Lumaprints Support**: [Lumaprints Support Email/Phone]  
**Railway Support**: https://railway.app/help

---

### Backup Recommendations

**Daily Backups**:
- ✅ Pricing database (`print_ordering.db`)
- ✅ Gallery images (if not backed up elsewhere)
- ✅ Lumaprints export files (keep copies)

**Before Major Changes**:
- ✅ Export Shopify products as CSV
- ✅ Backup pricing database
- ✅ Document current markup percentage
- ✅ Screenshot current admin settings

**Backup Locations**:
- Local computer (download files)
- Cloud storage (Google Drive, Dropbox, etc.)
- Railway volume backups (automatic)

---

## Appendix A: Quick Reference

### Tool Locations

| Tool | Navigation Path |
|------|----------------|
| Create Shopify Products | Admin Dashboard → Shopify Tab → "Create Shopify Products" |
| Lumaprints Bulk Mapping | Admin Dashboard → Shopify Tab → "Lumaprints Bulk Mapping" |
| Shopify Price Sync | Admin Dashboard → Shopify Tab → "Sync Prices to Shopify" |

---

### Common Formulas

**Price Calculation**:
```
Final Price = Cost Price × Global Markup
```

**Markup Percentage**:
```
Markup % = (Global Markup - 1) × 100
Example: 2.5 = 150% markup
```

**Profit Margin**:
```
Profit = Final Price - Cost Price
Margin % = (Profit / Final Price) × 100
```

---

### File Formats

| Tool | Input Format | Output Format |
|------|--------------|---------------|
| Create Shopify Products | N/A (uses database) | CSV |
| Lumaprints Bulk Mapping | .xlsx | .xlsx |
| Shopify Price Sync | N/A (uses API) | N/A (updates live) |

---

### Typical Processing Times

| Operation | Duration | Notes |
|-----------|----------|-------|
| Generate Shopify CSV | 5-30 seconds | Depends on image count |
| Shopify CSV Import | 2-10 minutes | Depends on product count |
| Lumaprints File Upload | 5-15 seconds | Depends on file size |
| Lumaprints Mapping | Instant | In-memory processing |
| Lumaprints Import | 2-5 minutes | Depends on product count |
| Shopify Price Sync | 5-10 minutes | Depends on product count |

---

## Appendix B: Glossary

**Aspect Ratio**: The proportional relationship between width and height of an image (e.g., 3:2, 2:3, 1:1)

**CSV**: Comma-Separated Values file format used for data import/export

**Global Markup**: A multiplier applied to all product costs to determine final prices

**GraphQL**: A query language used by Shopify's Admin API

**Handle**: A unique identifier for Shopify products (URL-friendly version of product title)

**Lumaprints**: Print-on-demand fulfillment service

**Product Variant**: A specific version of a product (e.g., size, color, frame option)

**SKU**: Stock Keeping Unit - a unique identifier for product variants

**Subcategory**: A grouping of related products in the pricing database

**Unmapped Product**: A Lumaprints product that doesn't have an image assigned

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 25, 2025 | Initial comprehensive manual | Manus AI |

---

## Questions or Issues?

If you encounter problems not covered in this manual:

1. **Check the troubleshooting section** (Section 7)
2. **Review Railway logs** for detailed error messages
3. **Consult existing documentation** in `/docs/` folder
4. **Contact your developer** with specific error details

**When reporting issues, include**:
- What you were trying to do
- What you expected to happen
- What actually happened
- Error messages (screenshots helpful)
- Browser console errors (F12 → Console)
- Railway log excerpts

---

**End of Manual**

This document is your complete guide to product management in the Fifth Element Photography system. Keep it accessible and refer to it whenever you need to add products, map images, or sync prices.

If you're hit by that proverbial bus, this manual should enable someone else to pick up where you left off. 🚌
