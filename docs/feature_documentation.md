# Fifth Element Photography - Feature Documentation

**Author:** Manus AI
**Date:** January 6, 2026

## 1. Introduction

This document provides a comprehensive overview of the new features and systems implemented for the Fifth Element Photography website. It covers the description cleaning system, the substrate hover descriptions, the print availability notification system, and the Shopify customer creation integration. This guide is intended to help with future maintenance, troubleshooting, and development.

---

## 2. Description Cleaning System

This system was created to solve the problem of excessive line breaks and inconsistent formatting in image descriptions. It provides a permanent solution by cleaning the descriptions at the source.

### 2.1. The Problem

Image descriptions, when edited in the Image Admin's rich text editor, were being saved with extra `<br>` tags and empty paragraphs. This resulted in poor formatting and excessive spacing in the image modal on the live site.

### 2.2. The Solution

A two-part solution was implemented to fix both existing and future descriptions:

**Part 1: One-Time Cleaning Tool**

A dedicated admin tool was created to clean all existing descriptions in the database. This tool performs the following actions:

- Removes all empty paragraphs (including those with whitespace or `&nbsp;`).
- Reduces multiple consecutive `<br>` tags to a single `<br>`.
- Removes all whitespace between HTML tags.
- Trims whitespace from the beginning and end of paragraphs.
- Creates a timestamped backup of the `image_descriptions.json` file before making any changes.

**How to Use:**
1.  Navigate to: `https://fifth-element-photography-production.up.railway.app/admin/clean-descriptions`
2.  Click the "Clean Descriptions" button.
3.  The tool will process all descriptions and display a summary of the results.

**Part 2: Automatic Cleaning on Save**

To prevent the problem from recurring, the same cleaning logic was integrated directly into the Image Admin's save functionality. Now, every time a description is saved (for a new or existing image), it is automatically cleaned before being stored in the database.

This ensures that all future descriptions will be clean and properly formatted without any manual intervention.

### 2.3. Key Files

-   `/home/ubuntu/fifth-element-photography/clean_descriptions.py`: The Python script containing the core cleaning logic.
-   `/home/ubuntu/fifth-element-photography/routes/clean_descriptions_admin.py`: The Flask blueprint for the admin cleaning tool.
-   `/home/ubuntu/fifth-element-photography/templates/admin/clean_descriptions.html`: The HTML template for the admin cleaning tool.
-   `/home/ubuntu/fifth-element-photography/app.py`: The main application file, modified to include the automatic cleaning on save.

---

## 3. Substrate Hover Descriptions

This feature enhances the user experience by providing detailed information about each print substrate option when a user hovers over it.

### 3.1. How It Works

When a user is viewing the print ordering options, hovering over a substrate (e.g., "Hot Press Bright", "Canvas Wrap") will display a tooltip with a detailed description of that material. This helps customers make informed decisions about their purchases.

All substrate descriptions are stored in a central JavaScript file, making them easy to update and manage.

### 3.2. Key Files

-   `/home/ubuntu/fifth-element-photography/static/js/substrate-descriptions.js`: Contains the database of all substrate descriptions.
-   `/home/ubuntu/fifth-element-photography/static/js/shopify-integration.js`: Implements the hover functionality and integrates with the Shopify product options.

---

## 4. Print Availability Notifications

This system allows customers to request notifications for prints that are not yet available for purchase.

### 4.1. User Experience

If a print is not available, the "Order Prints" button is replaced with a "Notify Me When Available" button. When a user clicks this button and submits their email, they are subscribed to receive a notification when the print becomes available.

### 4.2. Backend Process

1.  **Database:** The notification request (customer email and image filename) is saved to the `print_notifications` table in the site's SQLite database.
2.  **Admin Email:** An email is automatically sent to `rick@fifthelement.photos` to inform the admin of the new request.
3.  **Shopify Customer Creation:** A new customer is automatically created in Shopify with the provided email address. Email marketing consent is properly handled.
4.  **Admin Dashboard:** All notification requests can be viewed in the admin dashboard.

### 4.3. Key Files

-   `/home/ubuntu/fifth-element-photography/routes/print_notifications.py`: The API endpoint that handles notification requests.
-   `/home/ubuntu/fifth-element-photography/templates/modal_beta.html`: The modal template containing the "Notify Me" button.

---

## 5. Shopify Customer Creation

To streamline marketing efforts, customers are automatically created in Shopify from two sources on the website.

### 5.1. Sources

1.  **Contact Form:** When a user submits the contact form, a customer is created in Shopify.
2.  **Print Notifications:** As described above, when a user requests a print notification, a customer is created in Shopify.

### 5.2. Email Marketing Consent

In both cases, the system properly handles email marketing consent, ensuring compliance with marketing regulations. Customers are only subscribed to marketing emails if they explicitly agree to it.

### 5.3. Key Files

-   `/home/ubuntu/fifth-element-photography/routes/contact.py`: Handles the contact form submission and Shopify customer creation.
-   `/home/ubuntu/fifth-element-photography/routes/print_notifications.py`: Handles the notification request and Shopify customer creation.


---

## 6. Back Button Navigation

This feature improves the user experience during the print ordering process by allowing customers to easily navigate back from the size selection screen to the print type selection screen.

### 6.1. How It Works

When a customer is viewing the product options (sizes, substrates) for a specific print type (e.g., Canvas), a "Back to Print Types" button appears at the top of the options. Clicking this button returns the user to the print type selection screen, where they can choose a different category (Metal, Fine Art Paper, etc.).

The back button only appears when multiple print types are available for the image. If only one print type is available, the back button is hidden since there's nothing to go back to.

### 6.2. Implementation Details

The back button functionality is implemented entirely in JavaScript. When the product modal is first opened via `openShopifyProductModal`, the system stores the original image URL, image title, and all available product handles in global variables. This ensures that regardless of which print type the user is viewing, the back button can always access the correct information to return to the print type selection screen.

When the product modal is displayed, the system checks if multiple product categories exist for the current image. If they do, the back button is shown and configured to call the `showCategorySelector` function with the stored original values, which displays the print type selection screen.

This approach solves the problem of the Shopify product image URL being different from the original site image URL, ensuring the back button works consistently across all print types (Canvas, Metal, Fine Art Paper, Foam-mounted Print, and Framed Canvas).

### 6.3. Key Files

-   `/home/ubuntu/fifth-element-photography/static/js/shopify-integration.js`: Contains the back button logic and event handlers.
-   `/home/ubuntu/fifth-element-photography/static/css/shopify-modal.css`: Contains the styling for the back button.

---

## 7. Summary

The Fifth Element Photography website now includes a comprehensive set of features designed to improve the customer experience and streamline business operations. The description cleaning system ensures that all image descriptions are consistently formatted and professional. The substrate hover descriptions provide customers with detailed information to help them make informed purchasing decisions. The print availability notification system allows customers to express interest in prints that are not yet available, and the Shopify customer creation integration helps build a marketing database. Finally, the back button navigation makes it easy for customers to explore different print options without frustration.

All of these features work together to create a polished, user-friendly e-commerce experience that reflects the quality of the photography on display.


## 8. Enhanced "Add Product" Form

This feature enhances the admin pricing tool to allow for the easy addition of new product size variants, including sizes that do not yet exist in the database.

### 8.1. The Problem

The original "Add New Product" form was too simplistic. It only allowed for the creation of a product subcategory (e.g., "0.75\" Stretched Canvas") but did not provide a way to add the individual size variants (8x12, 16x24, etc.) with their associated costs. This made it impossible to add new, complete products to the pricing system.

### 8.2. The Solution

The "Add New Product" form was completely redesigned to streamline the process of adding new pricing entries. The new form, now titled "Add New Pricing Entry," allows an administrator to add a single size variant to an existing product type, and even create new sizes on the fly.

**How It Works:**

1.  **Select Category:** Choose from the list of existing categories (e.g., Canvas, Framed Canvas, Metal).
2.  **Select Product Type:** The dropdown is dynamically populated with the product subcategories that belong to the selected category.
3.  **Enter New Size or Select Existing:**
    *   To create a new size, type it into the text field (e.g., "26x42").
    *   To use an existing size, select it from the dropdown.
4.  **Select Aspect Ratio:** If creating a new size, select the appropriate aspect ratio from the dropdown.
5.  **Enter Cost Price:** Input the cost of the item from the print vendor (e.g., Lumaprints).
6.  **Retail Price Auto-Calculates:** The retail price is automatically calculated based on the current global markup percentage.
7.  **Submit:** Clicking "Add Pricing Entry" sends the data to the backend.

**Backend Process:**

-   If a new size was entered, the system first checks if it already exists in the `print_sizes` table. If not, it creates it.
-   The system then creates a new entry in the `base_pricing` table, linking the product subcategory, the size, and the cost price.
-   The new pricing entry is immediately available in the pricing tool and is included in all global markup calculations.

### 8.3. Key Files

-   `/home/ubuntu/fifth-element-photography/templates/admin_pricing_dashboard_v2.html`: Contains the HTML and JavaScript for the enhanced form.
-   `/home/ubuntu/fifth-element-photography/routes/pricing_admin.py`: Contains the backend Flask routes for adding the new pricing entry and creating new sizes.
