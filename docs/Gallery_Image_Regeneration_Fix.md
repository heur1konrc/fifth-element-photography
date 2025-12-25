# Gallery Image Regeneration Fix

**Date**: December 25, 2025  
**Issue**: Gallery images not updating after using REPLACE tool (e.g., PineCone.jpg still showing old watermark)  
**Status**: ✅ FIXED

---

## Problem Description

When using the **REPLACE** tool to replace an original image file, the gallery-optimized image (1200px version served to public galleries) was not regenerating properly, or browsers were caching the old version. This caused confusion as the admin would see the new image in the original files but the public gallery would still show the old watermarked version.

### Specific Example
- **PineCone.jpg** was replaced with a new version (removed watermark)
- Original file updated successfully
- Gallery image at `/data/gallery-images/PineCone.jpg` either:
  - Didn't regenerate at all, OR
  - Regenerated but browsers cached the old version

---

## Root Causes Identified

1. **Silent Failures**: Gallery regeneration code had minimal logging, making it impossible to diagnose failures
2. **Browser Caching**: Gallery images were served without proper cache-control headers, causing browsers to cache old versions indefinitely
3. **No Manual Override**: No way to force regenerate a single gallery image if automatic regeneration failed

---

## Solutions Implemented

### 1. Enhanced Logging in `replace_image()` Function

**File**: `app.py` (lines 2413-2442)

Added detailed console logging with `[REPLACE]` prefix to track:
- When gallery regeneration starts
- Gallery file path
- Original image dimensions
- Resized dimensions
- Success/failure status
- Full error tracebacks on failure

**Example Log Output**:
```
[REPLACE] Starting gallery image regeneration for PineCone.jpg
[REPLACE] Gallery path: /data/gallery-images/PineCone.jpg
[REPLACE] Original dimensions: 4000x3000
[REPLACE] Resizing to: 1200x900
[REPLACE] ✓ Successfully regenerated gallery image for PineCone.jpg at /data/gallery-images/PineCone.jpg
```

### 2. Cache-Busting Headers on Gallery Image Endpoint

**File**: `app.py` (lines 1106-1163)

Modified `/gallery-image/<filename>` route to include:
- **Cache-Control**: `public, max-age=300` (5-minute cache)
- **Last-Modified**: File modification timestamp
- **ETag**: `"{filename}-{mtime}"` for conditional requests

**How It Works**:
- Browsers will check if the file has been modified before using cached version
- After 5 minutes, browsers must revalidate
- When gallery image is regenerated, modification time changes, forcing browser to download new version

**Code**:
```python
mtime = os.path.getmtime(gallery_path)
response = make_response(send_file(gallery_path))
response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minute cache
response.headers['Last-Modified'] = str(int(mtime))
response.headers['ETag'] = f'"{filename}-{int(mtime)}"'
return response
```

### 3. Manual "Force Regenerate Gallery Image" Button

**New Files Created**:
- `routes/regenerate_gallery_image.py` - API endpoint
- `static/js/regenerate_gallery.js` - Frontend JavaScript
- Updated `templates/admin_new.html` - Added orange sync button

**API Endpoint**: `POST /api/regenerate-gallery-image/<filename>`

**Features**:
- Deletes existing gallery image (if exists)
- Regenerates from original image
- Returns file size and path for verification
- Detailed logging with `[REGENERATE]` prefix
- Confirmation dialog before execution
- Forces page reload with cache-busting timestamp after success

**Button Location**: Admin Images tab, in the panel-bottom-buttons section

**Button Order** (left to right):
1. **Edit** (pencil) - Edit image metadata
2. **Analyze** (magnifying glass) - View resolution, aspect ratio, etc.
3. **Replace** (exchange arrows) - Replace original image file
4. **Regenerate** (sync icon, orange) - Force regenerate gallery image
5. **Download** (download) - Download original
6. **Delete** (trash) - Delete image

---

## How to Use the Manual Regenerate Button

1. Go to **Admin Dashboard** → **Images** tab
2. Find the image with gallery display issues (e.g., PineCone.jpg)
3. Click the **orange sync icon** button (4th button from left)
4. Confirm the regeneration in the dialog
5. Wait for success message showing file size
6. Page will auto-reload with cache-busting to show new gallery image

**Success Message Example**:
```
✓ Gallery image regenerated successfully!

File: PineCone.jpg
Size: 234.56 KB
```

---

## Testing Instructions

### Test 1: Verify Automatic Regeneration Works
1. Use REPLACE tool on any image
2. Check Railway logs for `[REPLACE]` messages
3. Verify success message appears
4. Hard refresh browser (Ctrl+Shift+R) to see new gallery image

### Test 2: Verify Manual Regeneration Works
1. Click orange sync button on any image
2. Confirm dialog
3. Check for success message with file size
4. Page should auto-reload showing updated gallery image

### Test 3: Verify Cache-Busting Headers
1. Open browser DevTools → Network tab
2. Navigate to a gallery page
3. Find gallery image requests
4. Check Response Headers for:
   - `Cache-Control: public, max-age=300`
   - `Last-Modified: {timestamp}`
   - `ETag: "{filename}-{timestamp}"`

---

## Technical Details

### Gallery Image Generation Logic

**Original Image Location**: `/data/images/{filename}`  
**Gallery Image Location**: `/data/gallery-images/{filename}`

**Processing**:
1. Open original image with PIL
2. Convert RGBA/P to RGB (for JPEG compatibility)
3. Calculate dimensions (max 1200px on longest side, preserve aspect ratio)
4. Resize with LANCZOS resampling (high quality)
5. Save as JPEG with quality=90, optimize=True

**Example Dimensions**:
- Original: 4000x3000 → Gallery: 1200x900
- Original: 3000x4000 → Gallery: 900x1200
- Original: 1000x800 → Gallery: 1000x800 (no upscaling)

### File Registration in app.py

**Lines 55-78**: Import and register the new route
```python
from routes.regenerate_gallery_image import register_regenerate_gallery_image_route
# ... other imports ...
register_regenerate_gallery_image_route(app, require_admin_auth, IMAGES_FOLDER)
```

---

## Rollback Instructions

If these changes cause issues, revert with:

```bash
cd /home/ubuntu/fifth-element-photography
git revert 03e7e68
git push
railway up
```

**Files to manually remove** (if needed):
- `routes/regenerate_gallery_image.py`
- `static/js/regenerate_gallery.js`
- `docs/Gallery_Image_Regeneration_Fix.md`

**Template changes to revert** (if needed):
- Remove orange sync button from `templates/admin_new.html` line 353-355
- Remove `regenerate_gallery.js` script tag from line 892

---

## Related Systems

### DO NOT TOUCH (Working Perfectly)
- ✅ Lumaprints Bulk Mapping tool
- ✅ Shopify Price Sync system
- ✅ Product Creation tool

### Related to This Fix
- Image REPLACE tool (`/api/replace_image` endpoint)
- Gallery image serving (`/gallery-image/<filename>` endpoint)
- Thumbnail generation (separate system, not affected)

---

## Future Improvements

1. **Batch Regeneration**: Add "Regenerate All Gallery Images" button to admin tools
2. **Progress Indicator**: Show spinner during regeneration (currently just confirmation dialog)
3. **Automatic Verification**: After REPLACE, automatically verify gallery image was regenerated
4. **CDN Cache Purging**: If using CDN in future, add cache purge API calls

---

## Commit Information

**Commit Hash**: `03e7e68`  
**Commit Message**: "Add gallery image regeneration fixes: cache-busting headers, detailed logging, and manual regenerate button"

**Files Changed**:
- `app.py` - Enhanced logging, cache headers
- `routes/regenerate_gallery_image.py` - NEW API endpoint
- `static/js/regenerate_gallery.js` - NEW frontend function
- `templates/admin_new.html` - Added button and script tag
- `docs/Gallery_Image_Regeneration_Fix.md` - NEW documentation (this file)

---

## Questions & Support

If gallery images still don't regenerate after these fixes:

1. **Check Railway logs** for `[REPLACE]` or `[REGENERATE]` messages
2. **Try manual regeneration** using the orange sync button
3. **Verify original image exists** at `/data/images/{filename}`
4. **Check disk space** on Railway volume (`df -h /data`)
5. **Test with a small image** (< 1MB) to rule out size issues

**Railway Logs Command**:
```bash
railway logs
```

Look for lines containing `[REPLACE]` or `[REGENERATE]` to see what's happening during gallery image generation.
