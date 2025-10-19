# Lumaprints Pricing Admin Workflow

**Author:** Manus AI
**Date:** October 18, 2025

## 1. Overview

This document provides a comprehensive guide to using the new Lumaprints Pricing Admin system for the Fifth Element Photography website. This powerful tool gives you complete control over your print-on-demand pricing, allowing you to manage costs, set global markups, and ensure your pricing is always accurate and profitable.

The system is built on a robust database containing the complete Lumaprints product catalog (678 products across 25 categories) and automates all customer-facing price calculations based on your desired markup.

## 2. Accessing the Pricing Admin

To access the pricing admin panel, navigate to the following URL:

```
https://fifth-element-photography-production.up.railway.app/admin/pricing
```

You will be required to log in with your admin credentials to access this page.

## 3. Core Features

The pricing admin system provides the following key features:

| Feature | Description |
| :--- | :--- |
| **Global Markup Control** | Set a single markup percentage that applies to all 678+ products. | 
| **Real-Time Calculations** | Customer prices are instantly updated sitewide when you change the markup. |
| **Individual Cost Editing** | Manually override the cost of any product to adjust for sales or price changes. |
| **Product Management** | Add new products or remove existing ones from your catalog. |
| **Comprehensive Dashboard** | View key statistics like total products, categories, and average costs. |

### 3.1. Managing Global Markup

The most powerful feature is the **Global Markup** control. This allows you to set your profit margin across all products with a single input.

> **How it works:** The system calculates customer prices using the formula:
> `Customer Price = Wholesale Cost × (1 + (Markup Percentage / 100))`

To update the global markup:

1.  Enter your desired markup percentage in the **Global Markup** field (e.g., `150` for a 150% markup).
2.  The `Current multiplier` will update in real-time to show you the calculation factor (e.g., `2.50x`).
3.  Click the **Update** button.

All 678+ product prices will be recalculated and updated instantly across the website.

### 3.2. Managing Individual Products

You also have granular control over each product in the catalog.

#### Editing Product Costs

To change the wholesale cost of a single product:

1.  Locate the product in the list.
2.  Click into the **Cost** field for that product.
3.  Enter the new cost.
4.  The **Customer Price** will automatically update based on the current global markup.

This is useful for running sales on specific items or adjusting for one-off price changes from Lumaprints.

#### Adding a New Product

To add a new product to your catalog:

1.  Click the **+ Add Product** button.
2.  Select the appropriate **Category** from the dropdown menu.
3.  Enter the **Product Name**, **Size**, and wholesale **Cost**.
4.  Click the **Add** button.

The new product will be added to the database and will be available for customers to order.

#### Removing a Product

To remove a product from your catalog:

1.  Locate the product in the list.
2.  Click the red **trash icon** in the **Actions** column.
3.  Confirm the deletion when prompted.

The product will be soft-deleted from the database, meaning it will no longer be visible to customers but can be restored if needed.

## 4. Database & Data Source

The pricing system is powered by a dedicated SQLite database (`lumaprints_pricing.db`) that contains the complete, official wholesale pricing data from Lumaprints. This ensures your costs are always accurate.

-   **Data Source:** [https://www.lumaprints.com/pricing/](https://www.lumaprints.com/pricing/)
-   **Last Updated:** October 18, 2025

This system was designed to be easily updatable as Lumaprints changes its pricing in the future.

Should you have any questions, please do not hesitate to ask.

