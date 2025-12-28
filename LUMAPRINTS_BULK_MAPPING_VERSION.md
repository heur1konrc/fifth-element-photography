# Lumaprints Bulk Mapping Tool - Version History

## Version 1.1.0 (Dec 28, 2025) - PRODUCTION READY

### New Feature: Automatic Preprocessing
**Eliminates manual Excel editing step for user**

#### What Was Added
- **Automatic sorting** of uploaded Excel file A-Z by Column A (Product Name)
- **Automatic deletion** of all rows where Column O (Mapping Status) = "Mapped"
- Preprocessing runs **before** existing mapping workflow
- **No changes** to existing mapping functionality

#### Technical Implementation
**Location**: `/api/lumaprints/upload` route in `app.py` (lines ~5125-5131)

**Code Changes**:
```python
# PREPROCESSING STEP 1: Sort A-Z by Column A (Product Name)
print("Sorting worksheet A-Z by Product Name...")
lm.sort_worksheet_by_product_name(ws)

# PREPROCESSING STEP 2: Delete all rows with "Mapped" status
deleted_count = lm.delete_mapped_rows(ws)
print(f"Deleted {deleted_count} mapped rows")
```

**Functions Used** (from `lumaprints_mapper.py`):
- `sort_worksheet_by_product_name(ws)` - Sorts all data rows A-Z by Column A, preserving header row
- `delete_mapped_rows(ws)` - Deletes all rows where Column O = "Mapped", returns count

#### Testing Results
**Test File**: `FifthElementPhotography(74677)2025-12-28-13-08-49.xlsx`
- **Input**: 975 total products (842 Mapped + 133 Unmapped)
- **Output**: 133 Unmapped products, sorted A-Z by Product Name
- **Verification**: Output matches manually edited file exactly

#### User Workflow Impact
**Before (Manual Process)**:
1. Export Excel from Lumaprints
2. Open in Excel/Sheets
3. Sort A-Z by Column A
4. Delete all "Mapped" rows
5. Save edited file
6. Upload to Bulk Mapping Tool

**After (Automated)**:
1. Export Excel from Lumaprints
2. Upload directly to Bulk Mapping Tool ✓

**Time Saved**: ~5-10 minutes per upload

---

## Version 1.0.0 (Original Implementation)

### Core Functionality
- Upload Lumaprints Excel export (.xlsx)
- Display unmapped products grouped by title
- Batch mapping interface with:
  - Product title dropdown
  - Image filename input
  - Aspect ratio selector
- Apply mappings to all product types (Canvas + Art Paper variants)
- Download mapped Excel file for Lumaprints upload

### Technical Details
**Frontend**: `templates/admin_new.html` (modal interface)
**JavaScript**: `static/js/admin_new.js` (lines ~1343-1881)
**Backend Routes**:
- `/api/lumaprints/upload` (POST) - Upload and process file
- `/api/lumaprints/apply-mapping` (POST) - Apply mappings
- `/api/lumaprints/download` (GET) - Download mapped file

**Module**: `lumaprints_mapper.py`
- Product templates for different aspect ratios (1:1, 3:2, 2:3, etc.)
- Mapping data structure for Canvas and Art Paper products
- Excel manipulation functions

### Product Types Supported
**Canvas**:
- Subcategory: 0.75in Stretched Canvas
- Options: Mirror Wrap, Sawtooth Hanger, Semi-Glossy Finish

**Art Paper** (3 types):
- Hot Press Fine Art Paper
- Semi-Glossy Fine Art Paper
- Glossy Fine Art Paper
- Options: 0.25in Bleed

### Aspect Ratios
- 1:1 (Square)
- 3:2 (Landscape)
- 2:3 (Portrait)
- 4:3, 3:4, 16:9, 9:16 (additional ratios)

---

## Future Enhancements (Potential)
- Auto-detect aspect ratio from image library
- Bulk filename suggestions based on title matching
- Progress indicator for large file processing
- Undo/redo for mapping changes
- Export mapping report (CSV/PDF)
