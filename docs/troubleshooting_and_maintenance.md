# Troubleshooting and Maintenance Guide

**Author:** Manus AI
**Date:** January 6, 2026

## 1. Introduction

This guide provides solutions to common problems and outlines maintenance procedures for the new features on the Fifth Element Photography website. It is designed to help you quickly resolve issues and keep the site running smoothly.

---

## 2. Description Cleaning System

### 2.1. Troubleshooting

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| **Internal Server Error on `/admin/clean-descriptions`** | The template file is missing or the path is incorrect. | Verify that `templates/admin/clean_descriptions.html` exists. If the error persists, check the Railway logs for more details. |
| **Login Screen on `/admin/clean-descriptions`** | Authentication is enabled on the route. | The authentication has been removed. If this issue reappears, it means the code was reverted. Re-apply the change to remove the authentication check in `routes/clean_descriptions_admin.py`. |
| **Descriptions still have bad formatting after running the tool** | A new, unhandled formatting issue has been introduced. | The cleaning script in `clean_descriptions.py` needs to be updated. The regular expressions may need to be adjusted to handle the new formatting problem. |

### 2.2. Maintenance

-   **Backup Files**: The cleaning tool automatically creates backups of your descriptions file (e.g., `image_descriptions.json.backup.20260106_143000`). To save space, you can periodically delete old backup files from the `/data` directory on Railway.

---

## 3. Substrate Hover Descriptions

### 3.1. Troubleshooting

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| **Tooltips not appearing on hover** | A JavaScript error is preventing the hover functionality from working. | Open the browser's developer console (usually by pressing F12) and check for any errors in `shopify-integration.js` or `substrate-descriptions.js`. |
| **Incorrect description in tooltip** | The description in the `substrate-descriptions.js` file is incorrect. | Edit the corresponding entry in `static/js/substrate-descriptions.js` to update the description. |

### 3.2. Maintenance

-   **Adding a New Substrate**: To add a new substrate and description, simply add a new entry to the `substrate-descriptions.js` file, following the existing format.

---

## 4. Print Availability Notifications

### 4.1. Troubleshooting

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| **Admin not receiving email notifications** | The admin email address is incorrect, or there is an issue with the email server. | Verify that the admin email address in `routes/print_notifications.py` is correct (`rick@fifthelement.photos`). Check the Railway logs for any email sending errors. |
| **Customers not being created in Shopify** | The Shopify API credentials are invalid, or the app lacks the necessary permissions. | Ensure that the Shopify API credentials are correct and that the app has the `write_customers` permission in Shopify. |

### 4.2. Maintenance

-   **Check Notification Requests**: Periodically check the `print_notifications` table in the `print_ordering.db` database to ensure that all notification requests are being processed correctly.

---

## 5. General Maintenance

-   **Check Railway Logs**: Regularly review the logs in your Railway project for any errors or warnings that may indicate a problem with the application.
-   **Keep GitHub Updated**: Ensure that all changes to the code are committed and pushed to the `main` branch of the GitHub repository to maintain a single source of truth.


---

## 6. Back Button Navigation

### 6.1. Troubleshooting

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| **Back button not appearing on some print types** | The original image URL and product handles are not being stored correctly when the modal opens. | Verify that `window.originalImageUrl`, `window.originalImageTitle`, and `window.originalProductHandles` are being set in the `openShopifyProductModal` function in `static/js/shopify-integration.js`. |
| **Back button appears but doesn't work** | The stored values may be incorrect or the `showCategorySelector` function is not being called properly. | Check the browser console for JavaScript errors. Verify that the click event handler is properly attached to the back button. |

### 6.2. Maintenance

-   **Verify Functionality**: Periodically test the back button on all print types (Canvas, Metal, Fine Art Paper, Foam-mounted Print, Framed Canvas) to ensure it continues to work as expected after any code changes.


## 7. Enhanced "Add Product" Form

### 7.1. Troubleshooting

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| **Product Type dropdown freezes on "Loading..."** | A JavaScript error is preventing the subcategories from being loaded. | This was caused by an incorrect element ID in the JavaScript. The issue has been fixed. If it recurs, check the browser console for errors in `admin_pricing_dashboard_v2.html`. |
| **500 Internal Server Error on form submission** | The backend is receiving invalid data from the form. | This was caused by the backend expecting a string for `is_available` but receiving a boolean. The issue has been fixed. If it recurs, check the Railway logs for the exact error message. |

### 7.2. Maintenance

-   **Verify Functionality**: Periodically test the "Add New Pricing Entry" form to ensure it continues to work as expected after any code changes.
