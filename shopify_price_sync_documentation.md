'''
# Shopify Price Synchronization Feature

**Author:** Manus AI
**Date:** Dec 19, 2025

## 1. Feature Overview

This document outlines the functionality of the "Sync Prices to Shopify" feature. This feature is designed to update the prices of all existing products and their variants in your Shopify store to match the current pricing rules defined in the print ordering system's database. This is essential for ensuring that your Shopify store reflects any changes you make to your pricing markup, base costs, or print option prices without needing to manually update each product.

## 2. How to Use

The feature is accessible via a new button in the admin panel.

1.  **Navigate to the Admin Panel**: Log in to your print ordering system and go to the main admin dashboard.
2.  **Locate the Button**: Find the **"Sync Prices to Shopify"** button. It is located next to the "Create Shopify Products (API)" button.
3.  **Initiate the Sync**: Click the "Sync Prices to Shopify" button.
4.  **Confirm the Action**: A confirmation dialog will appear, warning you that the process can take **30-60 minutes** to complete due to Shopify's API rate limits. Click "OK" to proceed.
5.  **Monitor Progress**: An alert will appear at the top of the page indicating that the sync is in progress. **It is crucial to keep this browser tab open** for the duration of the process.
6.  **Review the Results**: Once the sync is complete, an alert will display a summary of the operation, including:
    *   Number of products updated
    *   Number of variants updated
    *   Total duration of the sync
    *   A list of any errors that occurred during the process.

## 3. Important Considerations

*   **Duration**: The price synchronization process is lengthy. With Shopify's API rate limit of 2 requests per second, updating a large catalog of products and variants can take a significant amount of time. Please be patient and allow the process to complete.
*   **Keep Tab Open**: The synchronization process is managed by your browser. Closing the tab will interrupt the process, and you will need to start it again.
*   **Global Update**: This feature updates **all** Shopify products that are linked to your print ordering system. It is not possible to sync prices for a subset of products at this time.

## 4. Troubleshooting

*   **Sync Fails to Start**: If you click the button and nothing happens, check your browser's developer console for any JavaScript errors. Ensure you are connected to the internet.
*   **Sync Fails Mid-Process**: If the process is interrupted, you can safely run it again. The system is designed to re-sync all prices, so it will correct any partially completed updates from a previous run.
*   **Errors in the Final Report**: If the completion summary includes errors, they will typically be related to specific products or variants that Shopify could not update. The error messages from Shopify will be displayed to help diagnose the issue. Common causes include a product being deleted from Shopify but still existing in the local database.

## 5. Testing Recommendations

Before running the price sync on your entire product catalog, we strongly recommend testing the feature on a small scale.

1.  **Create a Test Product**: In your Shopify admin, create a new product manually or use the "Create Shopify Products (API)" feature for a single new image.
2.  **Note the Current Price**: Record the price of one or more variants of your test product.
3.  **Change the Pricing in Your Admin Panel**: Go to the pricing rules section of your print ordering system and make a noticeable change to the pricing for the product type and size corresponding to your test product.
4.  **Run the Sync**: Initiate the "Sync Prices to Shopify" feature.
5.  **Verify the Price Change**: Once the sync is complete, check your test product in Shopify. The price should now be updated to reflect the new pricing rule.

By following these testing steps, you can verify that the feature is working as expected before committing to a full catalog update.
'''
