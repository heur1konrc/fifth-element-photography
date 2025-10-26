# CRITICAL NOTE: Image Quality Check

## Issue
The Lumaprints image quality check API (`/api/v1/images/checkImageConfig`) is currently DISABLED in the order form because it hangs and blocks the form.

## Location
- **File**: `templates/order_form.html`
- **Lines**: 448-515
- **Function**: `selectSize()` - image validation section

## When Re-enabling Later

⚠️ **CRITICAL**: The image quality check MUST use the **FULL PATH TO THE FULL SIZE HIRES IMAGE**, NOT the thumbnail displayed on the form.

### Common Error (DO NOT REPEAT)
- ❌ Using thumbnail path from form display
- ❌ Using relative paths
- ❌ Using preview/resized images

### Correct Approach
- ✅ Use full path to original high-resolution image
- ✅ Use absolute URL to the full-size file
- ✅ Verify image dimensions match the actual source file

## Current Status
Image quality check is COMMENTED OUT to allow form to function. Pricing integration takes priority.

## API Documentation
https://api-docs.lumaprints.com/api-5384561

---
*Created: 2025-10-26*
*This error was repeated multiple times - DO NOT MAKE AGAIN*

