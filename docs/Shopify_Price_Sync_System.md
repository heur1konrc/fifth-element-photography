# Shopify Price Sync System: Technical Documentation

**Author:** Manus AI
**Date:** December 25, 2025
**Version:** 1.0

## 1. Overview

This document provides a complete technical overview of the Shopify Price Sync system for the Fifth Element Photography website. The system is designed to synchronize product prices between the local pricing database (`print_ordering.db`) and the live Shopify store. It is initiated manually by an administrator from the Pricing Management dashboard.

The primary goal is to allow for global price adjustments via a markup multiplier and have those changes reflected across all relevant products in Shopify automatically, without manual data entry.

## 2. System Architecture & Key Components

The system consists of three main parts: a frontend interface, a backend API endpoint, and a server configuration modification.

| Component                 | Location                                                       | Description                                                                                             |
| ------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Frontend Interface**    | `templates/admin_pricing_dashboard_v2.html`                    | Contains the UI button, JavaScript logic, and the progress monitor modal for user interaction.          |
| **Backend API Endpoint**  | `routes/shopify_price_sync_api.py`                             | A Flask Blueprint that contains the core logic for fetching data, matching products, and calling the Shopify API. |
| **Server Configuration**  | `Procfile`                                                     | Defines the Gunicorn server command, modified to increase the worker timeout for this long-running task.   |
| **Pricing Data Source**   | `data/print_ordering.db`                                       | The SQLite database that serves as the single source of truth for product costs and availability.         |

## 3. Workflow

The end-to-end process is as follows:

1.  **Initiation:** The administrator navigates to the "Pricing Management" page.
2.  **User Action:** The admin clicks the **"🔄 Sync to Shopify"** button.
3.  **Confirmation:** A JavaScript `confirm()` dialog appears to prevent accidental execution.
4.  **Frontend Request:** Upon confirmation, the `syncPricesToShopify()` JavaScript function is called. It displays a modal progress monitor and sends a `POST` request to the `/api/shopify/sync-prices` endpoint.
5.  **Backend Processing:** The Flask server receives the request and begins the sync process (see Section 4 for details).
6.  **Frontend Feedback:** The progress monitor UI provides real-time feedback, including a progress bar, status messages, and a timer. **Note:** The progress bar is a simulation, as the backend does not currently stream progress. It jumps from 10% (connected) to 90% (processing) to 100% (complete).
7.  **Completion:** The backend returns a final JSON object containing the results (success/failure, counts, errors).
8.  **Display Results:** The frontend JavaScript parses the JSON and displays the final summary in the progress monitor. The monitor remains visible until the user manually closes it.

## 4. Backend Logic Deep Dive

The core logic resides in the `sync_shopify_prices()` function within `routes/shopify_price_sync_api.py`.

### Key Steps:

1.  **Fetch Global Markup:** Retrieves the current `global_markup` multiplier from the database.
2.  **Load Local Prices:** Queries the `print_ordering.db` database to build a Python dictionary of all available products. This dictionary is keyed by a tuple of `(product_type, size)` for fast lookups. It only includes products where `is_available` is `TRUE`.
3.  **Fetch Shopify Products:** Makes a GraphQL query to the Shopify Admin API to get all products and their variants. The query is paginated to handle a large number of products.
4.  **Iterate and Match:** The script iterates through every product and every variant from Shopify.
    *   **Variant Matching:** For each Shopify variant, it constructs a lookup key based on its option values (e.g., `option1`, `option2`).
    *   **Data Cleaning:** It strips known prefixes like `"Printed Product - "` and `"Size - "` from the Shopify option values to normalize them.
    *   **Name Mapping:** It uses the crucial `map_product_type_to_shopify()` function to resolve naming inconsistencies between the database (`0.75" Stretched Canvas`) and Shopify (`0.75 Stretched Canvas`). This mapping is now identical to the one used by the `shopify_api_creator.py` script, ensuring consistency.
5.  **Calculate and Update:**
    *   If a matching product is found in the local price dictionary, it calculates the new price: `new_price = cost_price * markup_multiplier`.
    *   It compares the calculated price to the current Shopify price. If they differ, it executes a `variantUpdate` GraphQL mutation to update the price on Shopify.
6.  **Return Response:** After iterating through all products, it returns a JSON response summarizing the operation, including `products_updated`, `variants_updated`, `duration_minutes`, and a list of `errors` (variants that could not be matched).

## 5. Key Fixes & Implementation Details

Several critical issues were identified and resolved during the development of this feature.

### 5.1. Gunicorn Worker Timeout

*   **Problem:** The sync process takes several minutes, but the default Gunicorn worker timeout is only 30 seconds. This caused the server to kill the process prematurely, resulting in a `500 Internal Server Error`.
*   **Solution:** The `Procfile` was modified to increase the timeout to 600 seconds (10 minutes).
    *   **File:** `Procfile`
    *   **Change:** `web: gunicorn --timeout 600 app:app`

### 5.2. Product Matching & Mapping

*   **Problem:** The initial sync failed because product type names and option values in Shopify did not exactly match the `display_name` in the local database.
*   **Solution:** A two-part solution was implemented in `routes/shopify_price_sync_api.py`:
    1.  **Prefix Stripping:** The code now explicitly strips common prefixes from Shopify variant options before attempting a match.
    2.  **Canonical Mapping:** The `map_product_type_to_shopify()` function was updated to be a complete, canonical mapping of all database product names to their corresponding Shopify names. This ensures that inconsistencies (e.g., `"` vs. no `"`, `Metal` vs. `Metal Print`) are correctly handled.

### 5.3. User Feedback / Progress Monitoring

*   **Problem:** The long-running process provided no feedback to the user, making it impossible to know if it was working, stuck, or finished.
*   **Solution:** A modal progress monitor was implemented in `templates/admin_pricing_dashboard_v2.html`.
    *   **UI:** Consists of a modal overlay with a spinner, progress bar, status text, and a timer.
    *   **Logic:** The `syncPricesToShopify()` JavaScript function was rewritten to manage the state of this modal, showing it on initiation and populating it with final results upon completion.

## 6. Revert Path

A backup of the `shopify_price_sync_api.py` file was created before the final mapping fix was applied. A full revert plan is documented.

*   **Revert Instructions:** `/home/ubuntu/fifth-element-photography/REVERT_PRICE_SYNC_FIX.md`
*   **Backup File:** `/home/ubuntu/fifth-element-photography/routes/shopify_price_sync_api.py.backup_20251225_020247`

This ensures that the system can be quickly restored to its previous state if any unforeseen issues arise.
