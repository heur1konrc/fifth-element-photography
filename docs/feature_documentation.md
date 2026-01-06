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
