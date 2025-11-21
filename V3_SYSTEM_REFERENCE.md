# V3 System Reference - Single Source of Truth

**Version**: 3.0.0-alpha  
**Last Updated**: December 21, 2024  
**Status**: Core Features Complete, Ready for Extended Testing

---

## ⚠️ READ THIS FIRST

This document is the **SINGLE SOURCE OF TRUTH** for all V3 system facts. If you have a question about how V3 works, the answer is in this document. Do not make assumptions - check this document first.

---

## Core Development Principles

### Code Quality Standards
- **Clean Code**: All code must be well-structured, commented, and maintainable
- **Performance First**: All functionality must be efficient and speed-oriented
- **No Assumptions**: Always verify facts against this document before implementing
- **Test Thoroughly**: All features must be tested before marking complete

### Performance Requirements
- **Fast Loading**: Gallery must load quickly (thumbnails implemented)
- **Responsive UI**: All interactions must feel instant
- **Optimized Images**: Automatic thumbnail generation for all images
- **Efficient Queries**: Database/file operations must be optimized

---

## Critical System Facts

### Data Storage Locations

**Image Files:**
- **Location**: `/data/` (root of data directory, NOT in a subdirectory)
- **NOT** in `/data/images/` 
- **NOT** in `/static/images/`
- Images are stored as individual files directly in `/data/`

**Thumbnail Files:**
- **Location**: `/data/thumbnails/`
- **Size**: 400px width (maintains aspect ratio)
- **Auto-generated**: Created on upload and on-demand for existing images
- **Format**: Same as original image (JPEG, PNG, etc.)

**Metadata Files (V3-specific):**
- `/data/image_metadata_v3.json` - Image titles and descriptions
- `/data/image_categories_v3.json` - Category assignments per image
- `/data/categories_v3.json` - List of available categories
- `/data/featured_image_v3.json` - Featured image selection (future)
- `/data/hero_image_v3.json` - Hero image selection (future)

**Old Production Metadata Files (DO NOT USE):**
- `/data/image_metadata.json` - Old system metadata
- `/data/image_categories.json` - Old system categories
- `/data/categories.json` - Old system category list

**Why separate files?**
- V3 and old production system run on the same `/data/` volume
- Separate metadata prevents conflicts when switching branches
- Old production remains functional while testing V3

---

## File Paths in Code

### Backend (Python)
```python
# data_manager_v3.py
self.data_dir = Path("/data")
self.images_dir = self.data_dir  # Images in /data/ directly, not /data/images/
self.thumbnails_dir = self.data_dir / "thumbnails"  # Thumbnails in /data/thumbnails/
```

### Flask Routes
```python
# app_v3.py
@app.route('/data/<filename>')
def serve_image(filename):
    return send_from_directory('/data', filename)

@app.route('/data/thumbnails/<filename>')
def serve_thumbnail(filename):
    # Auto-generates thumbnail if missing
    return send_from_directory('/data/thumbnails', filename)
```

### Frontend (JavaScript)
```javascript
// admin_v3.js and index_v3.js
const imageUrl = `/data/${image.filename}`;  // Full image
const thumbnailUrl = `/data/thumbnails/${image.filename}`;  // Thumbnail for gallery
```

---

## Railway Deployment

### Branch Configuration
- **Production (main branch)**: Runs old `app.py` with old admin
- **Testing (v3-staging branch)**: Runs new `app_v3.py` with V3 admin

### Procfile Configuration
- **main branch**: `web: gunicorn app:app` (old production)
- **v3-staging branch**: `web: gunicorn app_v3:app` (V3 admin)

### Persistent Volume
- `/data/` directory is persistent across deployments
- Shared between both branches
- Switching branches does NOT delete data
- Images remain in `/data/` regardless of which branch is active

---

## V3 vs Old System Comparison

| Aspect | Old Production (main) | V3 Admin (v3-staging) |
|--------|----------------------|----------------------|
| Flask App | `app.py` | `app_v3.py` |
| Admin Route | `/admin_new` | `/admin_v3` |
| Login Route | `/login` | `/login_v3` |
| Image Storage | `/data/` | `/data/` (same) |
| Thumbnails | None | `/data/thumbnails/` (auto-generated) |
| Metadata Files | `image_metadata.json` | `image_metadata_v3.json` |
| Categories File | `categories.json` | `categories_v3.json` |
| Image URL Pattern | `/data/<filename>` | `/data/<filename>` (same) |
| Bulk Operations | Limited | Full bulk assign/delete |
| Backup System | Manual | One-click download |

---

## V3 Starting State

When V3 first deploys:
- ✅ **Images**: All 84+ existing images visible immediately (from `/data/`)
- ✅ **Thumbnails**: Auto-generated on first view (cached for future loads)
- ❌ **Metadata**: NO titles, descriptions (starts with empty `image_metadata_v3.json`)
- ❌ **Categories**: NO categories assigned (starts with empty `categories_v3.json`)
- 📝 **User Action Required**: Add titles, descriptions, and categories through V3 admin

---

## Authentication

### Admin Credentials
- **Username**: Set via `ADMIN_USERNAME` environment variable (default: `admin`)
- **Password**: Set via `ADMIN_PASSWORD` environment variable (default: `password`)
- **Storage**: Environment variables in Railway (NOT in code)

### Routes Requiring Login
- `/admin_v3` - Admin dashboard
- `/api/v3/images` (POST, PUT, DELETE) - Image management
- `/api/v3/categories` (POST, DELETE) - Category management
- `/api/v3/backup/create` - Backup download
- `/api/v3/images/bulk/*` - Bulk operations

### Public Routes
- `/` - Public front-end gallery
- `/login_v3` - Login page
- `/api/v3/images` (GET) - Read-only image list for public front-end
- `/data/<filename>` - Image file serving
- `/data/thumbnails/<filename>` - Thumbnail serving

---

## API Endpoints

### Images
- `GET /api/v3/images` - Get all images with optional filtering (public)
  - Query params: `category`, `sort`
- `POST /api/v3/images/upload` - Upload new image (requires login)
- `PUT /api/v3/images/<filename>` - Update image metadata (requires login)
- `DELETE /api/v3/images/<filename>` - Delete image (requires login)

### Categories
- `GET /api/v3/categories` - Get all categories with image counts (public)
- `POST /api/v3/categories` - Create new category (requires login)
- `DELETE /api/v3/categories/<name>` - Delete category (requires login)

### Bulk Operations
- `POST /api/v3/images/bulk/assign-categories` - Assign categories to multiple images (requires login)
- `POST /api/v3/images/bulk/delete` - Delete multiple images (requires login)

### Backup
- `GET /api/v3/backup/create` - Download full backup as ZIP (requires login)
  - Includes: all images, thumbnails, and V3 metadata files
  - Filename format: `fifth_element_backup_v3_YYYYMMDD_HHMMSS.zip`

### Static Files
- `GET /data/<filename>` - Serve full-size image from `/data/`
- `GET /data/thumbnails/<filename>` - Serve thumbnail (auto-generates if missing)

### Debug Endpoints (Development Only)
- `GET /api/v3/debug/list-images` - List all files in `/data/images/`
- `GET /api/v3/debug/list-data` - List entire `/data/` directory structure
- `GET /api/v3/debug/categories-data` - View raw category data
- `POST /api/v3/debug/cleanup-categories` - Remove corrupted category entries

---

## Implemented Features

### ✅ Core Image Management
- **Upload Images**: Drag & drop or file browser upload
- **Edit Images**: Update title, description, and categories
- **Delete Images**: Single or bulk delete with confirmation
- **View Images**: Fast gallery with thumbnail loading
- **Automatic Thumbnails**: Generated on upload and on-demand

### ✅ Category Management
- **Create Categories**: Add new categories via modal
- **Delete Categories**: Remove categories (removes from all images)
- **Assign Categories**: Single or bulk assignment
- **Filter by Category**: View images in specific categories
- **Category Counts**: Real-time image counts per category

### ✅ Bulk Operations
- **Select Multiple Images**: Checkboxes on all image cards
- **Bulk Category Assignment**: Assign multiple categories to multiple images
- **Bulk Delete**: Delete multiple images at once
- **Select All/Deselect All**: Quick selection controls

### ✅ Sorting & Filtering
- **Sort Options**: Newest first, oldest first, A-Z, Z-A
- **Category Filter**: Filter by any category or view all
- **Real-time Updates**: Gallery updates immediately after changes

### ✅ Backup System
- **One-Click Backup**: Download all data as ZIP file
- **Includes**: All images, thumbnails, and V3 metadata
- **Timestamped**: Automatic filename with date/time
- **Fast Download**: Compressed ZIP format

### ✅ Performance Optimizations
- **Thumbnail Generation**: 400px thumbnails for fast loading
- **On-Demand Generation**: Thumbnails created as needed
- **Persistent Cache**: Thumbnails saved for future use
- **Fast Gallery Loading**: 10-20x faster than full images

### ✅ User Interface
- **Clean Design**: Modern, professional admin dashboard
- **Responsive Layout**: Works on desktop and tablet
- **Real-time Feedback**: Success/error notifications
- **Intuitive Controls**: Clear buttons and modals

---

## File Extensions Supported

**Image Uploads:**
- `.jpg`, `.jpeg` - JPEG images
- `.png` - PNG images
- `.gif` - GIF images
- `.webp` - WebP images

**Max File Size:** 16MB per image

---

## Known Issues & Limitations

### Current Limitations
- No Shopify Product Mapping tool (planned for future)
- No Lumaprints integration (planned for future)
- Basic test front-end (production design planned)
- No image randomization on front-end (planned)
- No image reordering/drag-drop (planned)

### Fixed Issues
- ✅ Metadata file conflicts (now using separate `_v3.json` files)
- ✅ Image path confusion (corrected to `/data/` not `/data/images/`)
- ✅ Slow gallery loading (thumbnails implemented)
- ✅ Bulk assignment bugs (fixed corrupted data handling)
- ✅ UI refresh issues (auto-reload after bulk operations)

---

## Testing Workflow

1. **Switch Railway to v3-staging branch**
2. **Wait for deployment** (1-2 minutes)
3. **Access admin**: `https://your-url.railway.app/login_v3`
4. **Login** with credentials from environment variables
5. **Test features** systematically:
   - Upload images
   - Create categories
   - Assign categories (single and bulk)
   - Filter and sort
   - Delete images
   - Create backup
6. **Report issues** immediately for real-time fixes
7. **Repeat** until all features work correctly

---

## Rollback Procedure

If V3 has critical issues:

1. Go to Railway dashboard
2. Change deployment branch from `v3-staging` to `main`
3. Wait for redeployment (1-2 minutes)
4. Old production system is restored
5. **NO DATA IS LOST** - `/data/` remains intact
6. V3 metadata files remain in `/data/` but are ignored by old system

---

## Version History

- **3.0.0-alpha** (Current) - Core features complete
  - Image upload/edit/delete
  - Category management
  - Bulk operations
  - Thumbnail generation
  - Backup system
  - Performance optimizations
- Future: 3.0.0-beta (extended testing), 3.0.0 (production), 3.1.0 (Shopify integration)

---

## Quick Reference Commands

### Git
```bash
# Switch to v3-staging
git checkout v3-staging

# Check current branch
git branch

# View recent commits
git log --oneline -10
```

### Railway
```bash
# Set environment variables
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_password
SECRET_KEY=your_secret_key
DATA_DIR=/data
```

### Backup
```bash
# Download backup via browser
https://your-url.railway.app/api/v3/backup/create

# Extract backup
unzip fifth_element_backup_v3_YYYYMMDD_HHMMSS.zip
```

---

## Contact & Support

- **GitHub Issues**: Report bugs and feature requests
- **Live Testing**: AI available during testing sessions for immediate fixes
- **Documentation**: All docs in `/docs/` directory and root `V3_SYSTEM_REFERENCE.md`

---

**Last Updated**: December 21, 2024  
**Next Review**: After extended testing and before production deployment


