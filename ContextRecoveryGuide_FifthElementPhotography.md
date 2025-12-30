# Context Recovery Guide: Fifth Element Photography
**Date**: Dec 28, 2025
**Status**: STABLE (Contact Form Added & Email Integration Working)
**Repository**: `heur1konrc/fifth-element-photography` (Public)

---

## 1. Executive Summary
This document allows any AI agent to immediately resume work on the **Fifth Element Photography** project without losing context.

### 🔴 MANDATORY REQUIREMENT FOR ALL AI AGENTS
**When ANY feature or fix is completed, you MUST:**
1. **Update this Context Recovery Guide** with complete implementation details
2. **Create or update version documentation** for the feature/component
3. **Commit and push documentation changes** to the repository
4. **DO NOT ask for permission** - this is a standing requirement

Failure to maintain documentation causes context loss and wastes client money.

### ⚠️ CRITICAL: Live Template Information
**The live production website uses `templates/index_new.html` NOT `templates/index.html`**

- **Main Homepage Template**: `templates/index_new.html`
- **Admin Dashboard Template**: `templates/admin_new.html`
- **Contact Page Template**: `templates/contact.html`
- **Admin Tool Templates**: Located in `templates/admin/` (e.g., `shopify_mapping.html`)
- **DO NOT modify `templates/index.html`** - it is NOT the live template
- **DO NOT modify `templates/admin.html`** - it is NOT the live admin template
- The site uses a horizontal navigation bar (NO SIDEBAR)
- Navigation links: HOME, galleries, ABOUT, CONTACT, BUY ME A COFFEE

**Current State**:
*   **Shopify Mapping Tool**: **FULLY OPTIMIZED**.
    *   **Search Bar**: **ADDED**. You can now filter images by title or filename instantly.
    *   **Performance**: Uses **thumbnails** for fast loading.
    *   **Schema**: Fixed (`image_filename` used consistently).
    *   **Save**: Fixed (`NOT NULL constraint` resolved).
*   **Contact Form**: **FULLY FUNCTIONAL** (Version 1.0.0 - Dec 28, 2025).
*   **Excel Cleanup Tool**: **FULLY FUNCTIONAL** (Version 1.0.0 - Dec 28, 2025).
        - Standalone tool on Admin/Shopify tab
        - Sorts Excel A-Z by Column A and removes "Mapped" rows
        - Processing time: 8.5 seconds for 975-row file
        - API: `/api/excel-cleanup/process` (POST), `/api/excel-cleanup/download` (GET)
    *   **Page**: Accessible at `/contact` route (GET request displays form, POST submits)
    *   **Template**: `templates/contact.html` (standalone page)
    *   **Route Handler**: `/contact` in `app.py` (lines ~3214-3280)
    *   **API Endpoint**: `/api/contact/submit` (POST) - handled by `routes/contact_form.py`
    *   **Email Integration**: Gmail SMTP working with App Password authentication.
    *   **Email Credentials**: Stored in `/home/ubuntu/.email_credentials`
    *   **Fields**: 
        - Name (required text input)
        - Email (required text input)
        - Phone (required text input)
        - Can we text that number? (dropdown: Yes/No)
        - I am interested in: (dropdown with 9 options including "Other")
        - Other: (conditional text field, appears when "Other" selected)
        - Date of Event or deadline (date picker)
        - How did you hear about my services? (checkboxes: Facebook, Instagram, Google, Printed ad, Referral)
    *   **Design**: Dark theme matching site aesthetic
        - Font: Poppins
        - Primary accent: #6799c2 (blue)
        - Secondary accent: #ff6b35 (orange)
        - Background: rgba(255, 255, 255, 0.1) for inputs
        - Text: #fff (white)
    *   **Styling Issues Fixed**:
        - Dropdown options: Dark background (#1a1a1a) with white text
        - Input fields: Forced dark semi-transparent background with !important flags
        - Webkit autofill: Override to maintain dark theme
    *   **Version History**:
        - v1.0.0 (Dec 28, 2025): Initial implementation with all fields and email integration
*   **Order Prints**: Active and functional.
*   **Deployment**: All fixes pushed to `main` branch on GitHub.

---

## 2. Critical Authentication (READ THIS FIRST)

**GitHub Credentials Location**:
The GitHub Personal Access Token (PAT) and authentication details are stored securely in the sandbox at:
```
/home/ubuntu/.github_credentials
```

**How to Use**:
1. Read the credentials file to get the PAT:
   ```bash
   cat /home/ubuntu/.github_credentials
   ```

2. Set the git remote URL using the credentials:
   ```bash
   git remote set-url origin https://[USERNAME]:[PAT]@github.com/heur1konrc/fifth-element-photography.git
   ```
   (Replace `[USERNAME]` and `[PAT]` with values from the credentials file)

*Note: The token is valid for 90 days from Dec 27, 2025.*

---

## 3. Email Configuration (CRITICAL)

**Gmail SMTP Credentials Location**:
The Gmail App Password for the contact form is stored securely in the sandbox at:
```
/home/ubuntu/.email_credentials
```

**Email Settings**:
*   **SMTP Server**: `smtp.gmail.com`
*   **Port**: `587` (TLS/STARTTLS)
*   **Username**: `rick@fifthelement.photos`
*   **App Password**: Stored in `/home/ubuntu/.email_credentials`
*   **Recipient**: `rick@fifthelement.photos`

**Important Notes**:
*   The App Password is NOT the regular Gmail password
*   2-Step Verification must be enabled on the Google account
*   IMAP/SMTP access must be enabled in Google Workspace settings
*   App Password is valid until revoked

---

## 4. Recent Fixes & Features

### Dec 30, 2025: Hero Image Focal Point Control
*   **Feature**: Added ability to control the focal point of hero images on gallery pages.
*   **Implementation**:
    *   **Database**: Added `hero_focal_point` column to `galleries` table in `gallery_db.py` (default: 'center-center')
    *   **Admin UI**: Added focal point selector dropdown to Gallery Admin edit form with 9 preset positions:
        - top-left, top-center, top-right
        - center-left, center-center, center-right
        - bottom-left, bottom-center, bottom-right
    *   **Frontend**: Updated `templates/gallery_page.html` to apply focal point using CSS `object-position` property
    *   **Hero Height Reduction**: Reduced hero image height by 25%:
        - Desktop: 500px → 375px
        - Mobile: 300px → 225px
*   **How It Works**:
    *   Gallery admin selects focal point from dropdown when editing gallery
    *   Focal point value is stored in database (e.g., 'top-left', 'center-center')
    *   Template converts hyphenated value to CSS format (e.g., 'top left', 'center center')
    *   CSS variable `--hero-focal-point` is set on `.hero-image` div
    *   `object-position` property controls which part of the image is centered when cropped
*   **Files Modified**:
    *   `gallery_db.py`: Added column and migration logic
    *   `templates/gallery_admin.html`: Added focal point selector to edit form
    *   `templates/gallery_page.html`: Reduced hero height and added CSS object-position
*   **Result**: Gallery owners can now control which part of their hero image is visible when it's cropped to fit the hero container, ensuring important subjects remain in frame.

### Dec 30, 2025: Watermark Positioning & Replacement
*   **Feature**: Replaced watermark images with new signature-style versions and adjusted positioning for a tighter fit.
*   **Watermark Files**:
    *   **Location**: `watermarks/` directory
    *   **Files**: `WATERMARK_RCorey_WHITE.png` and `WATERMARK_RCorey_BLACK.png` were replaced with new, properly cropped versions that have minimal transparent padding.
*   **Positioning Fix**:
    *   **File**: `watermark_helper.py`
    *   **Change**: The `padding` variable was changed from `int(width * 0.02)` (2% of image width) to a hardcoded `2` pixels.
    *   **Result**: Watermarks are now positioned just 2 pixels from the edge of the image, providing a much tighter and more professional look.
*   **Troubleshooting**: Initial attempts to fix positioning were unsuccessful because the original watermark PNG files had excessive transparent space around the signature. The issue was resolved by replacing the files with properly cropped versions.

### Dec 29, 2025: Navigation & About Page
*   **Feature**: Implemented nested dropdown navigation and created a new About page.
*   **Navigation Dropdown**:
    *   **Location**: `templates/index_new.html`, `templates/contact.html`, `templates/gallery_page.html`
    *   **Implementation**: A "GALLERIES" dropdown now houses all photo gallery links (Geology, Nature, etc.), cleaning up the main nav bar.
    *   **Mobile Support**: Fully responsive with touch support. Tapping "GALLERIES" on mobile toggles the dropdown.
    *   **Hover Fix**: Corrected a CSS issue where the dropdown would disappear when the mouse moved from the nav item to the menu. The gap was bridged by removing `margin-top` and adding `padding-top` with a pseudo-element.
    *   **Link Fix**: Added the missing "Buy Me A Coffee" link to the `gallery_page.html` template.
*   **About Page**:
    *   **Route**: `/about` (defined in `app.py`)
    *   **Template**: `templates/about.html`
    *   **Content**: Displays the bio and image managed from the Admin -> Settings tab.
    *   **Layout**: Features text wrapping around the floated image on desktop, and a stacked layout on mobile.
    *   **Title**: Page title changed from "About the Photographer" to "My Story".
*   **Styling Updates**:
    *   **Contact Form**: Changed the "Get in Touch" heading color to `#7B68EE` to match the site's primary accent color.

### Dec 28, 2025: Excel Cleanup Tool (Standalone)
*   **Feature**: Separate standalone tool to prepare Lumaprints Excel exports before bulk mapping.
*   **Location**: 
    *   Button: Admin/Shopify tab → "Excel Cleanup Tool" button
    *   Modal: `templates/admin_new.html` (Excel Cleanup Tool modal)
    *   Backend: `routes/excel_cleanup.py`
    *   Frontend JS: `static/js/excel_cleanup.js`
    *   API Endpoints: 
        - `/api/excel-cleanup/process` (POST) - Process uploaded file
        - `/api/excel-cleanup/download` (GET) - Download cleaned file
*   **What It Does**:
    1. **Sorts uploaded Excel file A-Z by Column A (Product Name)** - Keeps header row (Row 1) in place
    2. **Removes all rows where Column O (Mapping Status) = "Mapped"** - Keeps only "Unmapped" products
    3. **Provides cleaned file for download** - Ready for Lumaprints Bulk Mapping Tool
*   **Performance**: Optimized to process 975-row file in **8.5 seconds** (17x faster than initial version)
*   **Workflow**:
    1. Export from Lumaprints
    2. Use Excel Cleanup Tool to remove mapped rows and sort
    3. Download cleaned file
    4. Use Lumaprints Bulk Mapping Tool with cleaned file
*   **Result**: Eliminates manual Excel editing step, saves 5-10 minutes per upload
*   **Testing**: Verified with 975-product file (842 Mapped + 133 Unmapped) → Result: 133 Unmapped products, sorted A-Z
*   **Version**: 1.0.0 (Dec 28, 2025)
*   **Note**: This is a SEPARATE tool from Lumaprints Bulk Mapping Tool - preprocessing was removed from the mapping tool to keep it simple

### Dec 28, 2025: Contact Form
*   **Feature**: Professional contact form with Gmail SMTP email delivery.
*   **Location**: 
    *   Frontend: `templates/contact_form_new.html` (included in `templates/index.html`)
    *   Backend: `routes/contact_form.py`
    *   API Endpoint: `/api/contact/submit` (POST)
*   **Fields**:
    *   Name (required)
    *   Email (required)
    *   Phone (required)
    *   Can we text that number? (dropdown: Yes/No)
    *   I am interested in: (dropdown with 9 options including "Other")
    *   Other text field (appears when "Other" is selected)
    *   Date of Event or deadline (date picker)
    *   How did you hear about my services? (checkboxes: Facebook, Instagram, Google, Printed ad, Referral)
*   **Email Template**: Professional HTML email with all form data formatted nicely
*   **Result**: Emails are delivered to rick@fifthelement.photos successfully

### Dec 27, 2025: Shopify Mapping Improvements

### A. Search & Filter (New!)
*   **Feature**: Added a search bar to the top of the Shopify Mapping page.
*   **Implementation**: Client-side JavaScript filtering in `templates/admin/shopify_mapping.html`.
*   **Result**: Users can instantly find specific images without scrolling through hundreds of cards.

### B. Performance Optimization (Thumbnails)
*   **Issue**: The Mapping Page was loading full-resolution images, causing massive lag.
*   **Fix**:
    1.  Added `/admin/thumbnail/<filename>` route to `routes/shopify_admin.py`.
    2.  Updated `templates/admin/shopify_mapping.html` to use this route.
*   **Result**: Page loads significantly faster.

### C. Schema & Save Fixes
*   **Schema**: Fixed mismatch between `image_title` and `image_filename`.
*   **Save**: Fixed `NOT NULL constraint` error by preserving existing Shopify IDs during updates.

---

## 5. System Architecture

### Database (`print_ordering.db`)
*   **Table**: `shopify_products`
*   **Schema**:
    *   `id` (INTEGER PRIMARY KEY)
    *   `image_filename` (TEXT NOT NULL) - **Key Identifier**
    *   `category` (TEXT NOT NULL) - e.g., "Metal", "Canvas"
    *   `shopify_product_id` (TEXT) - The ID from Shopify
    *   `shopify_handle` (TEXT NOT NULL) - The handle used for URLs
    *   `UNIQUE(image_filename, category)`

### File Structure
*   `/data`: Stores high-res images and the database.
*   `/data/thumbnails`: Stores generated thumbnails.
*   `routes/shopify_admin.py`: Backend logic for the admin tool.
*   `templates/admin/shopify_mapping.html`: Frontend interface.

---

## 6. Immediate Next Steps

**Contact Form Verification**:
*   Navigate to the Contact section on the website
*   Fill out and submit the form
*   Verify email is received at rick@fifthelement.photos
*   Check that all form fields are included in the email

**1. Verify Search Functionality**:
*   Open the Shopify Mapping page.
*   Type in the search bar.
*   Confirm that non-matching images disappear instantly.

**2. Verify Thumbnail Loading**:
*   Confirm that images load quickly and are not full-resolution (check network tab if unsure).

---

## 7. Troubleshooting

**Contact Form Email Not Sending**:
*   Verify the App Password in `/home/ubuntu/.email_credentials` is correct
*   Check that `routes/contact_form.py` has the correct SMTP settings
*   Ensure 2-Step Verification is enabled on rick@fifthelement.photos
*   Verify IMAP/SMTP is enabled in Google Workspace settings

**"Repository not found" Error**:
*   Ensure you are using the correct URL: `https://github.com/heur1konrc/fifth-element-photography.git`
*   Ensure you are using the PAT from `/home/ubuntu/.github_credentials`.

**"No such column" Error**:
*   This should be fixed. If it recurs, check if `routes/shopify_admin.py` was reverted. It MUST use `image_filename`.

---

# ADDENDUM: Controlling Shopify Product Selection
**Date**: Dec 27, 2025
**Related File**: `routes/shopify_api_creator.py`

---

## A1. Purpose
This addendum explains how to **Add** or **Remove** specific product variants (e.g., "Rolled Canvas", "4x6 Prints", "Silver Frames") from the "Create Shopify Product" tool.

The tool does not simply "copy" the database; it uses specific **Filters** and **Lists** to decide what to send to Shopify.

## A2. Removing "Rolled Canvas" (or other Sub-Categories)
**Mechanism**: SQL Query Filtering
**Location**: `routes/shopify_api_creator.py` (Lines ~166-190)

The code fetches products using a SQL query. To remove a specific type like "Rolled Canvas", you must add an exclusion condition to the `WHERE` clause.

**Current Code:**
```python
WHERE bp.is_available = TRUE
AND ar.display_name = ?
AND pc.display_name IN ('Canvas', 'Fine Art Paper', 'Foam-mounted Fine Art Paper', 'Metal')
```

**How to Modify (Exclude Rolled Canvas):**
Add `AND ps.display_name NOT LIKE '%Rolled%'` to the query.

```python
WHERE bp.is_available = TRUE
AND ar.display_name = ?
AND pc.display_name IN ('Canvas', 'Fine Art Paper', 'Foam-mounted Fine Art Paper', 'Metal')
AND ps.display_name NOT LIKE '%Rolled%'  # <--- ADD THIS LINE
```

## A3. Adding/Removing Frame Options
**Mechanism**: Hardcoded List
**Location**: `routes/shopify_api_creator.py` (Lines ~195-212)

Framed canvases are NOT fetched purely from the database. They are defined in a manual list called `framed_canvas_config`.

**Current Code:**
```python
framed_canvas_config = [
    ('0.75" Framed Canvas', [
        ('Black', 'black_floating_075'),
        ('White', 'white_floating_075'),
        ('Silver', 'silver_floating_075'), # <--- TO REMOVE SILVER, DELETE THIS LINE
        ('Gold', 'gold_plein_air'),
    ]),
    # ...
]
```

**How to Modify:**
*   **To Remove**: Simply delete the line (e.g., the 'Silver' line).
*   **To Add**: Add a new tuple: `('Color Name', 'database_option_name')`.
    *   *Note*: The `database_option_name` must exist in the `product_options` table in your database.

## A4. Renaming Products (The Mapping)
**Mechanism**: Dictionary Lookup
**Location**: `routes/shopify_api_creator.py` (Function `map_product_type_to_shopify`, Lines ~75-100)

If you want "Glossy White Metal" to appear as "High-Gloss Metal Print" on Shopify, change it here.

**Current Code:**
```python
mapping = {
    'Glossy White Metal': 'Glossy White Metal Print',
    # ...
}
```

**How to Modify:**
Change the value on the right side.
```python
mapping = {
    'Glossy White Metal': 'High-Gloss Metal Print', # <--- CHANGED
    # ...
}
```

---
**End of Context Recovery Guide**
