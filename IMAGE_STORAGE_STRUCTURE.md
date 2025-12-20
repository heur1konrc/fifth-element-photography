# Image Storage Structure

**Last Updated:** December 20, 2025

## Railway Production Environment

### Storage Location
- **Volume Mount:** `/data` (5GB Railway persistent volume)
- **Region:** US West (California, USA)

### Directory Structure

```
/data/
├── *.jpg, *.jpeg, *.png          # ALL images (web + hi-res) stored here
├── *.json                         # Image metadata files
├── galleries.db                   # Gallery database
├── lumaprints_pricing.db          # Pricing database
├── image_categories.json          # Image category assignments
├── image_metadata.json            # Image metadata
└── originals/                     # EMPTY - not currently used
```

### Critical Information

**⚠️ IMPORTANT:** All images (both web-optimized and hi-res) are stored directly in `/data/`, NOT in `/data/originals/`.

The `/data/originals/` directory exists but is **empty**. Do not assume hi-res images are in a separate directory.

### Image Serving Routes

1. **Web Images:** `/images/<filename>` → serves from `/data/<filename>`
2. **Hi-Res Download:** `/admin/download-highres/<filename>` → downloads from `/data/<filename>`
3. **Hi-Res View (for analysis):** `/admin/view-highres/<filename>` → serves from `/data/<filename>`

### Image Analysis Tool

The Analyze Image feature checks images in this order:
1. `/data/<filename>` (primary location)
2. `/data/originals/<filename>` (fallback, currently empty)
3. Returns 404 if not found

### Storage Statistics (as of Dec 20, 2025)
- **Total images:** 86 images in `/data/`
- **Images in originals:** 0 (directory empty)
- **Database files:** 3 (galleries.db, lumaprints_pricing.db, emergency backup)

### Backup Information

When backing up the Railway volume, ensure you backup `/data/` which contains:
- All image files
- All databases
- All metadata JSON files

### Migration Notes

If you need to separate web and hi-res images in the future:
1. Create `/data/originals/` structure
2. Copy hi-res images to `/data/originals/`
3. Update `image_storage_manager.py` to use the new structure
4. Update all routes that serve images
5. Test thoroughly before deploying

### Common Issues

**Issue:** Analyze Image button fails with "Image not found"
**Cause:** Code looking in `/data/originals/` instead of `/data/`
**Solution:** Check `/data/<filename>` first before checking originals

**Issue:** Images not appearing after restore
**Cause:** Images restored to wrong directory
**Solution:** Ensure images are in `/data/` root, not `/data/originals/`
