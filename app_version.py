"""
Fifth Element Photography - Main Application
==============================================
Version: v2.0.0
Date: 2025-10-27
Description: Photography gallery with admin tools (print ordering removed)

CHANGELOG:
----------
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
- (All /order and /pricing routes removed in v2.0.0)

FILES REMOVED IN v2.0.0:
------------------------
See REMOVAL_LOG_20251027.md for complete list
"""

__version__ = "2.0.0"
__date__ = "2025-10-27"

