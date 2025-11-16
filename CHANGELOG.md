# CHANGELOG

All notable changes to Fifth Element Photography website will be documented in this file.

## [2.0.3] - 2024-11-15

### Fixed
- **Admin Category Display** - Image cards now show ALL assigned categories as badges (not just first one)
- **Admin Button Sizing** - Edit and Delete buttons resized to fit properly without truncation
- **Category Checkbox Layout** - Removed scroll box from edit modal, improved 2-column grid alignment

### Changed
- **Backend Data Field** - Renamed `categories` to `all_categories` in `scan_images()` to match template expectations
- **Button Styling** - Reduced padding (6px/10px) and font size (12px) for compact fit
- **Checkbox Container** - Cleaner layout with better spacing and no overflow scrolling

---

## [2.0.2] - 2024-11-05

### Fixed
- **Featured Image EXIF Data** - Replaced hardcoded EXIF data with dynamic extraction from actual image files
- **EXIF Data Formatting** - Fixed EXIF data structure to properly display camera model, lens, aperture, shutter speed, ISO, and focal length
- **Featured Image Story** - Replaced hardcoded story text with dynamic loading from admin-edited content
- **Story Data Loading** - Fixed story loading to use `featured_stories.json` instead of overwriting with description field

### Changed
- **EXIF Data Extraction** - Modified `extract_exif_data()` to return formatted dict matching template expectations
- **Story Management** - Separated story and description fields for independent editing

### Progress
- **Shopify Product Mapping** - 8 products currently mapped to gallery images (ongoing)
- **Shipping Configuration** - Implemented 4-tier shipping profile system in Shopify
  - Paper prints profile (93 products)
  - Small/Medium canvas profile (22 products)
  - Medium/Large canvas profile
  - Extra-large canvas profile (6 products)
- **Shipping Pricing Strategy** - Hybrid model with partial subsidy in product prices (+$3 paper, +$10 canvas) plus customer-selectable shipping speeds

### Documentation
- Added comprehensive `SHIPPING_SOLUTION_DOCUMENTATION.md` with full shipping strategy details
- Documented Lumaprints shipping cost analysis and integration research

---

## [2.0.1] - 2024-11-03

### Added
- **Admin Gallery Pagination** - Gallery now displays 24 images per page with navigation controls (First, Previous, Next, Last)
- **Shopify Mapping Navigation** - Added "Back to Admin" and "Go to Website" buttons on Shopify mapping page
- **Dynamic Category System** - Website navigation categories now generated dynamically from database
- **AJAX Category Management** - Category add/delete operations now use AJAX for seamless updates

### Fixed
- **Category Management Server Errors** - Fixed 500 Internal Server Error when adding or deleting categories
- **Category Button Updates** - Admin page category buttons now refresh automatically after changes
- **Mobile Shopify Modal Styling** - "Select a size" text now properly styled in blue (#4a90e2) and visible on mobile
- **Mobile Shopify Button Styling** - Mobile variant selection buttons now match desktop with square design and blue highlights
- **Mobile Detection** - Improved mobile device detection to properly distinguish desktop from mobile browsers

### Changed
- **Shopify Mapping UI** - Reduced image sizes from 350px to 220px width (fits 5-6 across instead of 3)
- **Shopify Mapping Images** - Reduced image height from 200px to 140px for more compact display
- **Category Management Response** - Routes now return JSON instead of redirecting, preventing page reloads
- **Website Category Links** - Changed from hardcoded to dynamically generated from database

### Technical Improvements
- Implemented AJAX-based category management functions in `admin_new.js`
- Added `refreshCategoryModal()` and `refreshCategoryButtons()` functions for dynamic updates
- Updated `manage_categories()` route to return proper JSON responses
- Modified mobile detection logic to exclude desktop operating systems explicitly
- Enhanced Shopify modal CSS for better mobile responsiveness

---

## [2.0.0] - 2024-10-30

### Added
- **Shopify Integration** - Complete integration with Shopify Storefront API for print ordering
- **Shopify Product Mapping Admin** - Admin interface at `/admin/shopify-mapping` for managing product mappings
- **Database-Driven Product Mapping** - SQLite database (`shopify_mappings` table) for storing image-to-product mappings
- **ORDER PRINTS Button** - Dynamic button appears on gallery images mapped to Shopify products
- **Shopify Modal** - Badge-style variant selectors with real-time availability checking
- **Mobile Shopify Support** - Full Shopify integration on mobile devices with responsive modal

### Removed
- **Lumaprints Integration** - Removed legacy Lumaprints pricing and ordering system
- **Old Print Orders System** - Removed previous print order management interface
- **Legacy Database Routes** - Cleaned up old database management endpoints

### Changed
- **Order System Architecture** - Migrated from Lumaprints to Shopify for all print ordering
- **Admin Interface** - Streamlined admin panel removing legacy pricing management
- **Mobile Template** - Updated mobile template with Shopify scripts and integration

### Technical Details
- Created `shopify_admin.py` blueprint for Shopify-related routes
- Implemented Shopify Storefront API integration in `shopify-integration.js`
- Added database migration page at `/db-migration` for table creation
- Updated image serving routes to work with Railway's `/data/` directory
- Implemented `shopify-config.js` for loading mappings from database

---

## [1.4] - 2024-10-17

### Fixed
- **Desktop Order System** - Resolved conflicts between old and new ordering systems
- **Image Name Passing** - Fixed proper image identification in order forms
- **Unified Order System** - Both desktop and mobile now use identical order form

### Added
- **New Order Button** - Distinctive orange "🛒 NEW ORDER SYSTEM" button on desktop
- **openNewOrderForm() Function** - Proper image name capture and URL parameter passing

---

## [1.3] - 2024-10-15

### Added
- **Data Synchronization** - Perfect parity between desktop and mobile content
- **Alphabetical Category Sorting** - Consistent ordering across all platforms

### Fixed
- **Mobile Data Loading** - Fixed mobile route to use identical data loading as desktop

---

## [1.2] - 2024-10-12

### Added
- **Mobile Categories Carousel** - Touch-friendly horizontal scrollable category navigation
- **Redesigned Mobile Image Modal** - Full-width layout optimized for mobile viewing
- **Automatic Mobile Detection** - Seamless redirection to mobile-optimized interface

### Changed
- **Mobile Category Navigation** - Replaced dropdown with carousel interface
- **Mobile Modal Layout** - Restructured for better mobile viewing experience

---

## [1.1] - 2024-10-01

### Added
- **Core Portfolio Functionality** - Professional gallery with category filtering
- **Admin Management System** - Multi-user authentication and image management
- **Featured Image System** - Weekly featured image with story integration
- **Hero Image Management** - Dynamic hero image with overlay tagline
- **About Page Management** - Bio and profile information editing
- **Password Recovery** - Secure password reset functionality

### Technical Stack
- Python Flask backend
- JSON-based file storage
- Railway deployment
- Mobile-responsive design

---

## Version Numbering

- **Major.Minor.Patch** format (e.g., 2.0.1)
- **Major**: Significant architecture changes or feature overhauls
- **Minor**: New features, integrations, or substantial improvements
- **Patch**: Bug fixes, UI refinements, and minor enhancements

