# Fifth Element Photography - Lumaprints Integration Project Notes

## 🎯 PROJECT OVERVIEW
**Website:** https://fifth-element-photography-production.up.railway.app/  
**Repository:** https://github.com/heur1konrc/fifth-element-photography.git  
**Local Path:** `/home/ubuntu/fifth-element-photography`  
**Deployment:** Railway (auto-deploys from main branch)  

## 📋 COMPLETED WORK (Oct 2025)

### ✅ **3-Level Hierarchy Implementation for Framed Canvas**
- **Level 1:** Product Type (Framed Canvas)
- **Level 2:** Canvas Depth (0.75in, 1.25in, 1.50in)  
- **Level 3:** Frame Options (23, 3, 8 options respectively)

**Files Modified:**
- `lumaprints_catalog.json` - Updated with 3-level structure
- `app.py` - Added `/api/lumaprints/options/<subcategory_id>` endpoint
- `static/js/order_print_lumaprints.js` - Updated customer interface
- `templates/admin_products_new.html` - Added 3rd dropdown for admin
- `static/js/admin_products_new.js` - Added loadFrameOptions function

### ✅ **Product Catalog Corrections**
**All product categories now show correct counts:**

| Category | Correct Count | Status |
|----------|---------------|---------|
| Canvas (0.75in) | 17 sizes | ✅ Fixed size ranges |
| Canvas (1.25in) | 31 sizes | ✅ Fixed size ranges |
| Canvas (1.50in) | 27 sizes | ✅ Fixed size ranges |
| Rolled Canvas | 25 sizes | ✅ Fixed size ranges |
| Framed Canvas (0.75in) | 23 frame options | ✅ Complete |
| Framed Canvas (1.25in) | 3 frame options | ✅ Complete |
| Framed Canvas (1.50in) | 8 frame options | ✅ Complete |
| Fine Art Paper | 7 options | ✅ Fixed (removed Semi-Matte) |
| Foam-mounted Print | 9 options | ✅ Added missing 7 options |
| Framed Fine Art Paper | 25 frame options | ✅ Added all options |
| Metal | 2 options | ✅ Added Silver option |
| Peel and Stick | N/A | ✅ Already correct |

### ✅ **Size Range Corrections**
**Updated all size ranges to match actual Lumaprints specifications:**

**Canvas Products:**
- 0.75in Stretched Canvas: 8"×10" to 30"×30"
- 1.25in Stretched Canvas: 8"×10" to 45"×60"
- 1.50in Stretched Canvas: 8"×10" to 45"×60"
- Rolled Canvas: 8"×10" to 45"×60"

**Framed Canvas Products:**
- 0.75in Framed Canvas: 8"×10" to 30"×40"
- 1.25in Framed Canvas: 8"×10" to 48"×48"
- 1.50in Framed Canvas: 8"×10" to 48"×48"

## 🗂️ KEY FILES & STRUCTURE

### **Core Configuration Files:**
- `lumaprints_catalog.json` - Main product catalog (categories, subcategories, options)
- `extracted_pricing_data.json` - Pricing data from Lumaprints
- `app.py` - Flask backend with API endpoints
- `lumaprints_routes.py` - Lumaprints-specific API routes

### **Customer Interface:**
- `templates/order_print_lumaprints.html` - Order form template
- `static/js/order_print_lumaprints.js` - Customer ordering interface

### **Admin Interface:**
- `templates/admin_products_new.html` - Admin product management
- `static/js/admin_products_new.js` - Admin interface logic
- `templates/admin_thumbnails.html` - Thumbnail management

### **API Endpoints:**
- `/api/lumaprints/categories` - Get product categories
- `/api/lumaprints/subcategories/<category_id>` - Get subcategories
- `/api/lumaprints/options/<subcategory_id>` - Get frame/variant options
- `/api/product-thumbnails-new` - Thumbnail management

## ⚠️ KNOWN ISSUES

### **Thumbnail Persistence Problem**
- **Issue:** Thumbnails get deleted on every Railway deployment (ephemeral storage)
- **Impact:** Product thumbnails disappear after each code update
- **Solutions to Consider:**
  1. **AWS S3 Integration** (recommended) - Store thumbnails in persistent cloud storage
  2. **Railway Volume Storage** - Use Railway's persistent volume feature
  3. **Database Storage** - Store as base64 encoded data (not ideal for performance)
  4. **Git Integration** - Commit thumbnails to repository (increases repo size)

## 🔧 DEVELOPMENT WORKFLOW

### **Local Development:**
```bash
cd /home/ubuntu/fifth-element-photography
git status
git add .
git commit -m "Description of changes"
git push
```

### **Deployment:**
- Railway auto-deploys from `main` branch
- Deployment typically takes 2-3 minutes
- Check deployment status at Railway dashboard

### **Testing Order Form:**
1. Visit: https://fifth-element-photography-production.up.railway.app/
2. Click on any image → ORDER PRINT
3. Test all product categories and options
4. Verify size ranges and frame options display correctly

## 📊 DATA SOURCES

### **Product Specifications:**
- All product data manually extracted from Lumaprints documentation
- Size ranges verified against official Lumaprints catalog
- Frame options transcribed from provided spreadsheet data

### **Important:** 
Lumaprints API does NOT provide product catalogs - all product lists, sizes, and options must be maintained manually in `lumaprints_catalog.json`

## 🚀 NEXT STEPS (Future Development)

1. **Implement S3 thumbnail storage** to solve persistence issue
2. **Add order processing integration** with Lumaprints API
3. **Implement payment processing** for customer orders
4. **Add order tracking and management** features
5. **Optimize thumbnail loading** and caching

## 💡 DEVELOPMENT NOTES

- **Always test in multiple browsers** - caching issues are common
- **Size ranges come from catalog JSON** - not from JavaScript hardcoded values
- **Frame options are in "options" section** of catalog, not subcategories
- **3-level hierarchy works:** Category → Subcategory → Options
- **Railway deployments are ephemeral** - no persistent file storage

---
**Last Updated:** October 2025  
**Status:** Core functionality complete, ready for production testing
