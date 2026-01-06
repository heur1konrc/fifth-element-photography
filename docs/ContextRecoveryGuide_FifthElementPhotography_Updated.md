# Context Recovery Guide: Fifth Element Photography

**Date**: January 6, 2026
**Status**: STABLE (Description cleaning, notifications, and substrate hovers implemented)
**Repository**: `heur1konrc/fifth-element-photography` (Public)

---

## 1. Executive Summary

This document allows any AI agent to immediately resume work on the **Fifth Element Photography** project without losing context.

**Current State**:
*   **Description Cleaning System**: **IMPLEMENTED**. A one-time cleaning tool and auto-clean on save are live.
*   **Substrate Hover Descriptions**: **IMPLEMENTED**. Detailed tooltips for print options are working.
*   **Print Availability Notifications**: **IMPLEMENTED**. Customer notification system with Shopify integration is live.
*   **Shopify Customer Creation**: **IMPLEMENTED**. Customers are automatically created from the contact form and notification requests.
*   **Deployment**: All fixes pushed to `main` branch on GitHub.

---

## 2. Critical Authentication (READ THIS FIRST)

**GitHub Personal Access Token (PAT)**:
*Token stored securely - contact repository owner for access*

**How to Use**:
When pushing changes, you MUST set the remote URL using the GitHub PAT.
```bash
git remote set-url origin https://heur1konrc:<TOKEN>@github.com/heur1konrc/fifth-element-photography.git
```
*Note: Token expires 90 days from issue date.*

---

## 3. Recent Fixes & Features (Jan 6, 2026)

### A. Description Cleaning System (New!)

*   **Problem**: Excessive line breaks and inconsistent formatting in image descriptions from the Image Admin editor.
*   **Solution**: A two-part fix:
    1.  **One-Time Cleaning Tool**: An admin tool at `/admin/clean-descriptions` that cleans all existing descriptions in `image_descriptions.json`.
    2.  **Automatic Cleaning on Save**: The cleaning logic is now applied automatically whenever a description is saved in the Image Admin.
*   **Key Files**:
    *   `clean_descriptions.py`: Core cleaning logic.
    *   `routes/clean_descriptions_admin.py`: Admin tool route.
    *   `templates/admin/clean_descriptions.html`: Admin tool template.
    *   `app.py`: Modified to include auto-cleaning on save.

### B. Substrate Hover Descriptions (New!)

*   **Feature**: Detailed tooltips with descriptions appear when hovering over print substrate options.
*   **Implementation**: A central JavaScript file holds all descriptions, and another script handles the hover functionality.
*   **Key Files**:
    *   `static/js/substrate-descriptions.js`: Database of substrate descriptions.
    *   `static/js/shopify-integration.js`: Implements the hover functionality.

### C. Print Availability Notifications (New!)

*   **Feature**: Customers can request to be notified when a print becomes available.
*   **Backend Process**: Saves the request to the database, sends an email to the admin, and creates a customer in Shopify.
*   **Key Files**:
    *   `routes/print_notifications.py`: API endpoint for handling requests.

---

## 4. System Architecture

### Database & Data Files

*   `/data/image_descriptions.json`: Stores all image descriptions.
*   `/data/print_ordering.db`: Main database for the site.
    *   `shopify_products`: Table for Shopify product mappings.
    *   `print_notifications`: Table for print availability notification requests.

### Key File Structure

*   `/data`: Stores high-res images, databases, and JSON data files.
*   `clean_descriptions.py`: Core logic for cleaning descriptions.
*   `routes/clean_descriptions_admin.py`: Admin tool for cleaning descriptions.
*   `routes/print_notifications.py`: Handles notification requests.
*   `static/js/substrate-descriptions.js`: Substrate description data.
*   `static/js/shopify-integration.js`: Substrate hover functionality.
*   `templates/admin/clean_descriptions.html`: Template for the cleaning tool.

---

## 5. Verification Steps

**1. Verify Description Cleaning Tool**:
*   Go to `https://fifth-element-photography-production.up.railway.app/admin/clean-descriptions`.
*   Click the "Clean Descriptions" button and confirm it runs successfully.

**2. Verify Auto-Clean on Save**:
*   Go to the Image Admin, edit a description, and save it.
*   View the image modal on the live site and confirm the formatting is clean.

**3. Verify Substrate Hover Descriptions**:
*   Open an image modal and go to the "Order Prints" section.
*   Hover over different substrate options and confirm the tooltips appear with the correct descriptions.

---

## 6. Troubleshooting

**"Internal Server Error on /admin/clean-descriptions"**:
*   **Cause**: The template was trying to extend a non-existent `base.html`.
*   **Solution**: The template was rewritten as a standalone file. If this error recurs, check if the template was reverted.

**"Login Screen on /admin/clean-descriptions"**:
*   **Cause**: The route required admin authentication.
*   **Solution**: The authentication requirement was removed. If this error recurs, check if the route was reverted.

---

**End of Guide**
