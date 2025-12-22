"""
Fifth Element Photography - Main Application
==============================================
Version: v2.3.0
Date: 2024-12-22
Description: Photography gallery with Shopify e-commerce integration

CHANGELOG:
----------
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

__version__ = "2.3.0"
__date__ = "2024-12-22"

