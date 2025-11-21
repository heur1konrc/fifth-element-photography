# V3 System Reference - Single Source of Truth

**Version**: 3.0.0-alpha  
**Last Updated**: December 20, 2024  
**Status**: In Active Development

---

## ⚠️ READ THIS FIRST

This document is the **SINGLE SOURCE OF TRUTH** for all V3 system facts. If you have a question about how V3 works, the answer is in this document. Do not make assumptions - check this document first.

---

## Critical System Facts

### Data Storage Locations

**Image Files:**
- **Location**: `/data/` (root of data directory, NOT in a subdirectory)
- **NOT** in `/data/images/` 
- **NOT** in `/static/images/`
- Images are stored as individual files directly in `/data/`

**Metadata Files (V3-specific):**
- `/data/image_metadata_v3.json` - Image titles and descriptions
- `/data/image_categories_v3.json` - Category assignments per image
- `/data/categories_v3.json` - List of available categories
- `/data/featured_image_v3.json` - Featured image selection
- `/data/hero_image_v3.json` - Hero image selection

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
```

### Flask Routes
```python
# app_v3.py
@app.route('/data/<filename>')
def serve_image(filename):
    return send_from_directory('/data', filename)
```

### Frontend (JavaScript)
```javascript
// admin_v3.js and index_v3.js
const imageUrl = `/data/${image.filename}`;  // NOT /data/images/
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
| Metadata Files | `image_metadata.json` | `image_metadata_v3.json` |
| Categories File | `categories.json` | `categories_v3.json` |
| Image URL Pattern | `/data/<filename>` | `/data/<filename>` (same) |

---

## V3 Starting State

When V3 first deploys:
- ✅ **Images**: All 84+ existing images visible immediately (from `/data/`)
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

### Public Routes
- `/` - Public front-end gallery
- `/login_v3` - Login page
- `/api/v3/images` (GET) - Read-only image list for public front-end
- `/data/<filename>` - Image file serving

---

## API Endpoints

### Images
- `GET /api/v3/images` - Get all images (public)
- `POST /api/v3/images/upload` - Upload new image (requires login)
- `PUT /api/v3/images/<filename>` - Update image metadata (requires login)
- `DELETE /api/v3/images/<filename>` - Delete image (requires login)

### Categories
- `GET /api/v3/categories` - Get all categories (public)
- `POST /api/v3/categories` - Create new category (requires login)
- `DELETE /api/v3/categories/<name>` - Delete category (requires login)

### Static Files
- `GET /data/<filename>` - Serve image file from `/data/`

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
- No automated backup system (manual git backups only)
- Basic test front-end (production design planned)
- No image randomization on front-end (planned)

### Fixed Issues
- ✅ Metadata file conflicts (now using separate `_v3.json` files)
- ✅ Image path confusion (corrected to `/data/` not `/data/images/`)

---

## Testing Workflow

1. **Switch Railway to v3-staging branch**
2. **Wait for deployment** (1-2 minutes)
3. **Access admin**: `https://your-url.railway.app/login_v3`
4. **Login** with credentials from environment variables
5. **Test features** while AI is live and ready to fix issues
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

---

## Version History

- **3.0.0-alpha** (Current) - Initial V3 build with core features
- Future: 3.0.0-beta, 3.0.0 (production), 3.1.0 (Shopify integration)

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

---

## Contact & Support

- **GitHub Issues**: Report bugs and feature requests
- **Live Testing**: AI available during testing sessions for immediate fixes
- **Documentation**: All docs in `/docs/` directory

---

**Last Updated**: December 20, 2024  
**Next Review**: After successful V3 testing completion

