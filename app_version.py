"""
Fifth Element Photography - Main Application
==============================================
Version: v2.3.4
Date: 2024-12-23
Description: Photography gallery with Shopify e-commerce integration

CHANGELOG:
----------
v2.3.4 (2024-12-23):
  - AUTOMATED: New Shopify products now auto-publish to Storefront API sales channel
  - FIXED: Products immediately available for Order Prints without manual channel toggle
  - TECHNICAL: Product creation now calls Shopify Publications API to enable Storefront access
  - TECHNICAL: Eliminates need to manually toggle "FIFTHE ELEMENT STROREFRONT API" for each product

v2.3.3 (2024-12-23):
  - AUTOMATED: Shopify product handles now auto-save to database when creating products
  - AUTOMATED: All 5 category handles (Canvas, Metal, Paper, Framed Canvas, Foam-mounted) saved automatically
  - ADDED: Category selector modal for Order Prints button (choose print type before checkout)
  - ADDED: API endpoint /api/shopify/product-categories/<filename> to retrieve all handles
  - IMPROVED: No manual mapping required - create products → handles saved → Order Prints works
  - TECHNICAL: shopify_products table stores filename + category + handle (composite unique key)
  - TECHNICAL: Frontend loads category-based mappings and shows selector modal
  - TECHNICAL: Captures actual handle from Shopify API response (handles conflicts/normalization)

v2.3.2 (2024-12-22):
  - FIXED: Gallery-optimized images now auto-generate on upload for Shopify product creation
  - FIXED: No longer need to manually run "Generate Gallery Images" before creating Shopify products
  - IMPROVED: Upload workflow - upload image → immediately create Shopify products
  - TECHNICAL: Both upload_image() and upload_images_new() now create 1200px gallery versions
  - TECHNICAL: Gallery images saved to /data/gallery-images/ at 90% JPEG quality
  - Commit: b5859f0

v2.3.1 (2024-12-22):
  - FIXED: Shopify tab now shows ALL images independently from Images tab filters
  - FIXED: Gallery filter from Images tab no longer carries over to Shopify tab
  - FIXED: URL parameters automatically cleared when switching to Shopify tab
  - IMPROVED: Images tab pagination reduced to 6 images per page (from 24)
  - IMPROVED: Removed top pagination controls (kept only bottom pagination)
  - IMPROVED: Search, filter, and sort persist correctly across pagination
  - TECHNICAL: Backend provides separate all_images_unfiltered for Shopify tab
  - TECHNICAL: JavaScript clears URL params (search, gallery, sort, page) on tab switch
  - Backup: fifth-element-backup-20251223-004904.tar.gz

v2.3.0 (2024-12-22):
  - ADDED: Tabbed admin interface (Images, Shopify, Tools, Settings)
  - ADDED: Horizontal image panels with category/gallery badges
  - ADDED: Category and gallery selector modals with checkboxes
  - ADDED: Iframe integration for Manage Categories and Gallery Admin
  - ADDED: HTML template for category management page
  - ADDED: Gallery data field to all images
  - ADDED: Date added field for sorting by upload date
  - IMPROVED: 60% less scrolling with horizontal panel layout
  - IMPROVED: Faster Shopify tab loading (seconds vs 90+ seconds)
  - IMPROVED: Inline editing for filenames and titles
  - FIXED: Category modal conflict preventing selector from displaying
  - FIXED: Gallery data integration with new database function
  - Backup: fifth-element-photography_backup_admin_redesign_20241222

v2.1.0 (2025-11-01):
  - ADDED: Shopify Buy Button integration for seamless ordering
  - ADDED: Modal-based product selection on fifthelement.photos
  - ADDED: Individual image download functionality in admin
  - IMPROVED: Users can order prints without leaving the main site
  - IMPROVED: Product options (substrate, size) embedded in site modal
  - Backup: fifth-element-photography_backup_shopify_integration_20251101_235239

v2.0.0 (2025-10-27):
  - REMOVED: All print ordering functionality
  - REMOVED: Pricing database and API routes
  - REMOVED: Order form templates
  - KEPT: Gallery front-end
  - KEPT: Admin authentication and tools
  - Backup: backup_20251027_221047_pre_cleanup.tar.gz

v1.x.x (2025-10-20 to 2025-10-26):
  - Full print ordering system with Lumaprints integration
  - Dynamic pricing calculator
  - Hierarchical product selection
  - (Removed in v2.0.0)

DEPENDENCIES:
-------------
- Flask
- Pillow (PIL)
- Werkzeug
- See requirements.txt for full list

ROUTES:
-------
- / : Gallery home page
- /admin : Admin dashboard
- /admin/images : Image management
- /admin/galleries : Gallery management  
- /admin/settings : Site settings
- /admin/download-image/<filename> : Download individual images (NEW in v2.1.0)

SHOPIFY INTEGRATION (v2.1.0):
-----------------------------
- Store: fifth-element-photography.myshopify.com
- Products mapped to gallery images
- Fulfillment via Lumaprints
- Checkout handled by Shopify
"""

__version__ = "2.3.4"
__date__ = "2024-12-23"
