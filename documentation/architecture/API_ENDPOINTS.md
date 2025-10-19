# API Endpoints Documentation

**Base URL:** `https://fifth-element-photography-production.up.railway.app`  
**Authentication:** Session-based for admin endpoints

---

## 🛒 Customer Order Form APIs

### **GET /api/products**
Load all active products for the customer order form.

**Purpose:** Populate product dropdown with real-time pricing  
**Authentication:** None required  
**Response Format:** JSON

**Response Example:**
```json
{
    "success": true,
    "products": [
        {
            "id": "canvas_075_8x10",
            "database_id": 1,
            "name": "Canvas 0.75\"",
            "size": "8×10\"",
            "cost_price": 15.39,
            "customer_price": 34.32,
            "category_name": "Canvas - 0.75\" Stretched",
            "category_id": 1,
            "product_type": "stretched_canvas",
            "thickness": "0.75\"",
            "has_variants": false,
            "variant_count": 0
        },
        {
            "id": "framed_15_8x10",
            "database_id": 150,
            "name": "Framed Canvas 1.5\"",
            "size": "8×10\"",
            "cost_price": 31.25,
            "customer_price": 69.69,
            "category_name": "Framed Canvas - 1.5\"",
            "category_id": 6,
            "product_type": "framed_canvas",
            "thickness": "1.5\"",
            "has_variants": true,
            "variant_count": 8,
            "variants": [
                {
                    "id": 1,
                    "name": "Maple Wood",
                    "description": "Maple Wood Floating Frame",
                    "price_modifier": 0.0,
                    "is_default": true
                },
                {
                    "id": 2,
                    "name": "Espresso",
                    "description": "Espresso Floating Frame", 
                    "price_modifier": 0.0,
                    "is_default": false
                }
            ]
        }
    ],
    "total_count": 167
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "Error fetching products: [error details]",
    "products": []
}
```

### **GET /api/product-variants/{product_id}**
Get variants for a specific product.

**Purpose:** Load frame options when customer selects framed canvas  
**Authentication:** None required  
**Parameters:** `product_id` (integer)

**Response Example:**
```json
{
    "success": true,
    "variants": [
        {
            "id": 1,
            "name": "Maple Wood",
            "description": "Maple Wood Floating Frame",
            "price_modifier": 0.0,
            "is_default": true
        },
        {
            "id": 2,
            "name": "Espresso", 
            "description": "Espresso Floating Frame",
            "price_modifier": 0.0,
            "is_default": false
        }
    ]
}
```

---

## 🔧 Admin Pricing Management APIs

### **GET /admin/pricing**
Load the pricing admin interface.

**Purpose:** Display admin dashboard with all products and pricing  
**Authentication:** Required (`@require_admin_auth`)  
**Response:** HTML template with embedded data

**Template Data:**
- Global markup percentage and multiplier
- All categories with product counts
- All products with calculated customer prices
- Statistics (total products, categories, average costs)

### **POST /admin/pricing/update-markup**
Update the global markup percentage.

**Purpose:** Change pricing for all products instantly  
**Authentication:** Required  
**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
markup_percentage=150.0
```

**Response:**
```json
{
    "success": true,
    "message": "Global markup updated to 150.0%",
    "new_multiplier": 2.5
}
```

### **POST /admin/pricing/update-product**
Update cost price for individual product.

**Purpose:** Modify specific product costs  
**Authentication:** Required  
**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
product_id=123
new_cost=25.99
```

**Response:**
```json
{
    "success": true,
    "message": "Product cost updated successfully",
    "product_id": 123,
    "new_cost": 25.99,
    "new_customer_price": 57.98
}
```

### **POST /admin/pricing/add-product**
Add new product to catalog.

**Purpose:** Expand product offerings (coffee mugs, ornaments, etc.)  
**Authentication:** Required  
**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
category_id=27
product_name=Coffee Mug
size=11oz
cost_price=8.50
```

**Response:**
```json
{
    "success": true,
    "message": "Product added successfully",
    "product_id": 680,
    "customer_price": 18.96
}
```

### **DELETE /admin/pricing/delete-product/{id}**
Remove product from catalog.

**Purpose:** Remove discontinued products  
**Authentication:** Required  
**Parameters:** `id` (integer)

**Response:**
```json
{
    "success": true,
    "message": "Product deleted successfully",
    "product_id": 123
}
```

---

## 📂 Category Management APIs

### **POST /admin/pricing/add-category**
Create new product category.

**Purpose:** Add categories for new product types  
**Authentication:** Required  
**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
category_name=Coffee Mugs
description=Custom printed coffee mugs
```

**Response:**
```json
{
    "success": true,
    "message": "Category added successfully",
    "category_id": 27,
    "category_name": "Coffee Mugs"
}
```

### **DELETE /admin/pricing/delete-category/{id}**
Remove empty category.

**Purpose:** Clean up unused categories  
**Authentication:** Required  
**Parameters:** `id` (integer)

**Response:**
```json
{
    "success": true,
    "message": "Category deleted successfully",
    "category_id": 27
}
```

---

## 🛠️ System Management APIs

### **GET /setup-database**
Initialize database on live server.

**Purpose:** Create tables and load initial data  
**Authentication:** None (temporary setup endpoint)  
**Usage:** One-time setup for new deployments

**Response:**
```json
{
    "success": true,
    "message": "Database initialized successfully",
    "tables_created": ["products", "categories", "settings", "product_variants"],
    "products_loaded": 679,
    "categories_created": 26,
    "variants_created": 256
}
```

---

## 🔍 Data Flow Examples

### **Customer Order Process:**
1. `GET /enhanced_order_form` → Load order form page
2. `GET /api/products` → Populate product dropdown
3. Customer selects framed canvas → Variants loaded from product data
4. Customer completes order → Form submission

### **Admin Pricing Update:**
1. `GET /admin/pricing` → Load admin interface
2. Admin changes markup → `POST /admin/pricing/update-markup`
3. All customer prices recalculated instantly
4. Next customer order shows new prices

### **Adding New Product:**
1. Admin clicks "Add Product" → Form appears
2. Admin fills details → `POST /admin/pricing/add-product`
3. Product added to database
4. Immediately available in customer order form

---

## 🚨 Error Handling

### **Common Error Responses:**

**Authentication Required:**
```json
{
    "success": false,
    "message": "Authentication required",
    "redirect": "/login"
}
```

**Database Error:**
```json
{
    "success": false,
    "message": "Database error: [specific error]",
    "error_code": "DB_ERROR"
}
```

**Validation Error:**
```json
{
    "success": false,
    "message": "Invalid input: [field] is required",
    "field_errors": {
        "cost_price": "Must be a positive number"
    }
}
```

---

## 🔒 Security Considerations

### **Admin Endpoints:**
- All `/admin/*` routes protected by `@require_admin_auth`
- Session-based authentication
- CSRF protection via Flask built-ins

### **Input Validation:**
- SQL injection prevention (parameterized queries)
- XSS protection in templates
- Data type validation on all inputs

### **Rate Limiting:**
- Consider implementing for production
- Especially for database modification endpoints

---

## 📊 Performance Notes

### **Optimization Strategies:**
- Database indexes on frequently queried fields
- Minimal data transfer in API responses
- Efficient SQL queries with JOINs
- Caching of global settings

### **Response Times:**
- `/api/products`: ~200-500ms (679 products)
- Admin operations: ~100-300ms
- Database queries: <50ms average

---

*End of API Endpoints Documentation*
