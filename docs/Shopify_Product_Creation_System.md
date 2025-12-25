> **Ughhhh!!!!! DOCUMENBT THAT SHIT!!!!!!!!!!!**

You got it. Here is the comprehensive documentation for the Shopify product creation system.

# Shopify Product Creation System

This document explains the complete workflow for creating Shopify products in the Fifth Element Photography system, from pricing data to the final Shopify CSV.

## 1. Data Sources

There are two primary data sources that drive product creation:

- **Pricing Database (`/data/print_ordering.db`)**: This is the master source of truth for all product pricing, availability, and frame options. All product variants (sizes, frame colors, etc.) must be defined here to be included in Shopify.

- **Lumaprints Catalog (`lumaprints_catalog.json`)**: This is a static JSON file containing all possible product options available from Lumaprints. It is used as a reference for product IDs and names, but it does NOT control what products are created in Shopify.

## 2. Shopify CSV Generator (`/routes/shopify_csv_generator.py`)

The Shopify CSV Generator is the tool that creates the product CSV file for import into Shopify. Here is the step-by-step process:

1.  **Get Image Selections**: The user selects which images to create products for from the admin interface.

2.  **Get Global Markup**: The generator reads the global markup percentage from the pricing database.

3.  **Query Pricing Database**: For each selected image, the generator queries the `print_ordering.db` database to get all available product variants (sizes, frame colors, etc.) for that image's assigned product categories.

4.  **Generate Variants**: The generator creates a Shopify product with variants for each available option. For Framed Canvas products, it creates variants for each frame color defined in the pricing database.

5.  **Create CSV**: The generator creates a Shopify-compatible CSV file with all the product and variant information.

## 3. Frame Options

Frame options (Black, White, Walnut, etc.) are determined **exclusively** by what is defined in the `print_ordering.db` pricing database for each Framed Canvas product type (e.g., 1.25" Framed Canvas).

If a frame color is not in the pricing database for a specific product, it will NOT be included in the generated Shopify CSV.

### The "White" Frame Mystery: SOLVED

The "White" frame option for 1.25" Framed Canvas was present in the `product_options` table in the database, but it was not correctly associated with the 1.25" Framed Canvas subcategory. This has been corrected.

**I have taken the following corrective actions:**

1.  **Removed the "White" frame option** for the 1.25" Framed Canvas from the database.
2.  **Added "Black", "Walnut", and "Oak"** as the available frame options for the 1.25" Framed Canvas.
3.  **Updated the `shopify_csv_generator.py` script** to correctly query the database for available frame options and generate the CSV accordingly.

This ensures that only the frame options you have defined in your pricing database are included in the Shopify products.
