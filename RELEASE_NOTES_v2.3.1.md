# Release Notes - v2.3.1

**Release Date:** December 22, 2024  
**Commit:** e504d1c  
**Backup:** fifth-element-backup-20251223-004904.tar.gz

## Summary

This release fixes critical issues with the admin interface where filters from the Images tab were incorrectly carrying over to the Shopify tab, and improves pagination settings for better usability.

## Bug Fixes

### Shopify Tab Independence
- **Fixed:** Shopify tab now displays ALL images independently from Images tab filters
- **Fixed:** Gallery filter parameter no longer persists when switching from Images to Shopify tab
- **Fixed:** URL parameters (search, gallery, sort, page) are automatically cleared when switching to Shopify tab
- **Impact:** Users can now filter images in the Images tab without affecting what they see in the Shopify tab

### Images Tab Pagination
- **Improved:** Reduced images per page from 24 to 6 for easier browsing
- **Improved:** Removed top pagination controls (kept only bottom pagination)
- **Improved:** Search, filter, and sort parameters persist correctly across pagination

## Technical Changes

### Backend (app.py)
```python
# Line 1423-1424: Create separate unfiltered image list for Shopify tab
all_images_unfiltered = scan_images()  # Keep unfiltered copy for Shopify tab
images = list(all_images_unfiltered)  # Create copy for filtering

# Line 1491: Pass unfiltered images to template
all_images_unfiltered=all_images_unfiltered,  # Unfiltered images for Shopify tab
```

### Frontend (admin_new.html)
```html
<!-- Line 477: Shopify tab uses unfiltered images -->
{% for image in all_images_unfiltered %}
```

### JavaScript (admin_tabs.js)
```javascript
// Lines 20-29: Clear URL parameters when switching to Shopify tab
if (targetTab === 'shopify') {
    const url = new URL(window.location);
    url.searchParams.delete('search');
    url.searchParams.delete('gallery');
    url.searchParams.delete('sort');
    url.searchParams.delete('page');
    window.history.replaceState({}, '', url);
}
```

## Files Modified

- `app.py` - Admin route updated to provide unfiltered images
- `templates/admin_new.html` - Shopify tab updated to use unfiltered images
- `static/js/admin_tabs.js` - Tab switching clears URL parameters
- `app_version.py` - Version bumped to 2.3.1

## Testing Performed

1. ✅ Applied gallery filter in Images tab
2. ✅ Switched to Shopify tab - all images displayed
3. ✅ URL parameters cleared automatically
4. ✅ Switched back to Images tab - filter cleared
5. ✅ Pagination shows 6 images per page
6. ✅ Search and sort persist across pagination

## Deployment Instructions

The changes are already committed and pushed to GitHub main branch (commit e504d1c).

To deploy to production:
```bash
cd /root/fifth-element-photography
git pull origin main
systemctl restart fifth-element-photography
```

## Rollback Instructions

If issues occur, rollback to previous version:
```bash
cd /root/fifth-element-photography
git checkout 04e831d  # Previous commit
systemctl restart fifth-element-photography
```

Or restore from backup:
```bash
cd /root
tar -xzf fifth-element-backup-20251223-004904.tar.gz -C fifth-element-photography-restore/
```

## Known Issues

None identified in this release.

## Next Steps

- Monitor production for any issues with tab switching
- Consider adding visual indicator when filters are active in Images tab
- Future: Add separate sort/filter controls for Shopify tab if needed
