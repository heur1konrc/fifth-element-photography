# API Endpoints Documentation v2.0

## Overview

The Fifth Element Photography system provides a comprehensive RESTful API for managing products, pricing, and customer orders. The API supports both the admin pricing interface and the 3-dropdown customer ordering system.

## Base URL
- **Development:** `http://localhost:5000`
- **Production:** `https://fifth-element-photography-production.up.railway.app`

## Authentication

### Admin Routes
All admin routes require authentication via session cookies. Users must log in through the admin interface before accessing protected endpoints.

**Login Endpoint:**
```
POST /admin/login
Content-Type: application/json

{
  "username": "admin_username",
  "password": "admin_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful"
}
```

## Customer API Endpoints

### Get All Products
Retrieves all active products with pricing and variant information for the 3-dropdown system.

**Endpoint:** `GET /api/products`

**Response:**
```json
{
  "success": true,
  "products": [
    {
      "database_id": 1,
      "category_id": 1,
      "category_name": "Canvas - 0.75\" Stretched",
      "name": "Canvas 0.75\" Stretched 8×10\"",
      "size": "8×10\"",
      "cost_price": 24.13,
      "customer_price": 53.81,
      "product_type": "stretched_canvas",
      "thickness": "0.75",
      "has_variants": false,
      "variants": []
    },
    {
      "database_id": 45,
      "category_id": 15,
      "category_name": "Framed Canvas - 1.5\"",
      "name": "Framed Canvas 1.5\" 8×10\"",
      "size": "8×10\"",
      "cost_price": 35.12,
      "customer_price": 78.05,
      "product_type": "framed_canvas",
      "thickness": "1.5",
      "has_variants": true,
      "variants": [
        {
          "id": 1,
          "variant_name": "frame_type",
          "variant_value": "Maple Wood Floating Frame",
          "price_modifier": 0.00,
          "is_default": true
        },
        {
          "id": 2,
          "variant_name": "frame_type", 
          "variant_value": "Espresso Floating Frame",
          "price_modifier": 0.00,
          "is_default": false
        }
      ]
    }
  ],
  "total_products": 679,
  "categories_count": 26
}
```

### Get Product Categories
Retrieves all active product categories for Dropdown 1.

**Endpoint:** `GET /api/categories`

**Response:**
```json
{
  "success": true,
  "categories": [
    {
      "id": 1,
      "name": "Canvas - 0.75\" Stretched",
      "description": "Traditional stretched canvas prints",
      "product_count": 32,
      "has_variants": false
    },
    {
      "id": 15,
      "name": "Framed Canvas - 1.5\"",
      "description": "Framed canvas with floating frame options",
      "product_count": 32,
      "has_variants": true
    }
  ]
}
```

### Get Product Variants
Retrieves variants for a specific product (used for Dropdown 2).

**Endpoint:** `GET /api/product-variants/{product_id}`

**Parameters:**
- `product_id` (integer): Database ID of the product

**Response:**
```json
{
  "success": true,
  "product_id": 45,
  "variants": [
    {
      "id": 1,
      "variant_name": "frame_type",
      "variant_value": "Maple Wood Floating Frame",
      "price_modifier": 0.00,
      "is_default": true
    },
    {
      "id": 2,
      "variant_name": "frame_type",
      "variant_value": "Espresso Floating Frame", 
      "price_modifier": 0.00,
      "is_default": false
    },
    {
      "id": 3,
      "variant_name": "frame_type",
      "variant_value": "Natural Wood Floating Frame",
      "price_modifier": 0.00,
      "is_default": false
    }
  ]
}
```

## Admin API Endpoints

### Pricing Management

#### Get Admin Pricing Data
Retrieves all products and categories for the admin pricing interface.

**Endpoint:** `GET /admin/pricing/data`  
**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "global_markup": 123.0,
  "multiplier": 2.23,
  "categories": [
    {
      "id": 1,
      "name": "Canvas - 0.75\" Stretched",
      "products": [
        {
          "id": 1,
          "name": "Canvas 0.75\" Stretched 8×10\"",
          "size": "8×10\"",
          "cost_price": 24.13,
          "customer_price": 53.81,
          "has_variants": false
        }
      ]
    }
  ],
  "stats": {
    "total_products": 679,
    "total_categories": 26,
    "avg_cost": 48.49,
    "avg_customer_price": 108.14
  }
}
```

#### Update Global Markup
Updates the global markup percentage applied to all products.

**Endpoint:** `POST /admin/pricing/update-markup`  
**Authentication:** Required

**Request:**
```json
{
  "markup": 150.0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Global markup updated successfully",
  "new_markup": 150.0,
  "new_multiplier": 2.50,
  "products_updated": 679
}
```

#### Update Product Cost
Updates the cost price for an individual product.

**Endpoint:** `POST /admin/pricing/update-product`  
**Authentication:** Required

**Request:**
```json
{
  "product_id": 1,
  "cost_price": 25.00
}
```

**Response:**
```json
{
  "success": true,
  "message": "Product updated successfully",
  "product": {
    "id": 1,
    "name": "Canvas 0.75\" Stretched 8×10\"",
    "old_cost": 24.13,
    "new_cost": 25.00,
    "old_customer_price": 53.81,
    "new_customer_price": 55.75
  }
}
```

#### Add New Product
Adds a new product to the catalog.

**Endpoint:** `POST /admin/pricing/add-product`  
**Authentication:** Required

**Request:**
```json
{
  "category_id": 1,
  "name": "Canvas 0.75\" Stretched 24×36\"",
  "size": "24×36\"",
  "cost_price": 89.50,
  "product_type": "stretched_canvas",
  "thickness": "0.75"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Product added successfully",
  "product": {
    "id": 680,
    "category_id": 1,
    "name": "Canvas 0.75\" Stretched 24×36\"",
    "size": "24×36\"",
    "cost_price": 89.50,
    "customer_price": 199.59,
    "created_at": "2025-10-19T15:30:00Z"
  }
}
```

#### Delete Product
Removes a product from the catalog.

**Endpoint:** `DELETE /admin/pricing/delete-product/{product_id}`  
**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "message": "Product deleted successfully",
  "deleted_product_id": 680
}
```

### Category Management

#### Add New Category
Creates a new product category.

**Endpoint:** `POST /admin/pricing/add-category`  
**Authentication:** Required

**Request:**
```json
{
  "name": "Coffee Mugs",
  "description": "Custom printed coffee mugs"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Category added successfully",
  "category": {
    "id": 27,
    "name": "Coffee Mugs",
    "description": "Custom printed coffee mugs",
    "active": true,
    "created_at": "2025-10-19T15:30:00Z"
  }
}
```

#### Get Categories
Retrieves all categories for admin management.

**Endpoint:** `GET /admin/pricing/categories`  
**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "categories": [
    {
      "id": 1,
      "name": "Canvas - 0.75\" Stretched",
      "description": "Traditional stretched canvas prints",
      "product_count": 32,
      "active": true
    }
  ]
}
```

### Variant Management

#### Add Product Variant
Adds a new variant option to a product.

**Endpoint:** `POST /admin/pricing/add-variant`  
**Authentication:** Required

**Request:**
```json
{
  "product_id": 45,
  "variant_name": "frame_type",
  "variant_value": "Cherry Wood Floating Frame",
  "price_modifier": 0.00,
  "is_default": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Variant added successfully",
  "variant": {
    "id": 257,
    "product_id": 45,
    "variant_name": "frame_type",
    "variant_value": "Cherry Wood Floating Frame",
    "price_modifier": 0.00,
    "is_default": false
  }
}
```

#### Get Product Variants (Admin)
Retrieves all variants for a product in admin interface.

**Endpoint:** `GET /admin/pricing/product-variants/{product_id}`  
**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "product_id": 45,
  "product_name": "Framed Canvas 1.5\" 8×10\"",
  "variants": [
    {
      "id": 1,
      "variant_name": "frame_type",
      "variant_value": "Maple Wood Floating Frame",
      "price_modifier": 0.00,
      "is_default": true
    }
  ]
}
```

## Database Setup Endpoints

### Initialize Database
Sets up the complete database schema and loads initial data.

**Endpoint:** `POST /setup-database`  
**Authentication:** None (development only)

**Response:**
```json
{
  "success": true,
  "message": "Database initialized successfully",
  "stats": {
    "products_created": 679,
    "categories_created": 26,
    "variants_created": 256,
    "settings_initialized": true
  }
}
```

## Error Responses

### Standard Error Format
All API endpoints return errors in a consistent format:

```json
{
  "success": false,
  "error": "Error type",
  "message": "Detailed error description",
  "code": 400
}
```

### Common Error Codes
- **400 Bad Request:** Invalid request parameters
- **401 Unauthorized:** Authentication required
- **403 Forbidden:** Insufficient permissions
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server-side error

### Example Error Responses

**Authentication Required:**
```json
{
  "success": false,
  "error": "Authentication Required",
  "message": "Please log in to access this resource",
  "code": 401
}
```

**Product Not Found:**
```json
{
  "success": false,
  "error": "Product Not Found", 
  "message": "Product with ID 999 does not exist",
  "code": 404
}
```

**Invalid Markup Value:**
```json
{
  "success": false,
  "error": "Invalid Input",
  "message": "Markup must be a positive number",
  "code": 400
}
```

## Rate Limiting

The API implements basic rate limiting to prevent abuse:
- **Admin endpoints:** 100 requests per minute per IP
- **Customer endpoints:** 200 requests per minute per IP
- **Database setup:** 1 request per hour per IP

## API Usage Examples

### JavaScript Fetch Examples

**Get All Products:**
```javascript
fetch('/api/products')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Loaded', data.products.length, 'products');
      // Populate dropdowns
    }
  });
```

**Update Global Markup:**
```javascript
fetch('/admin/pricing/update-markup', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    markup: 150.0
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Markup updated to', data.new_markup, '%');
  }
});
```

### Python Requests Examples

**Get Products:**
```python
import requests

response = requests.get('https://your-domain.com/api/products')
data = response.json()

if data['success']:
    products = data['products']
    print(f"Loaded {len(products)} products")
```

**Add New Product:**
```python
import requests

product_data = {
    'category_id': 1,
    'name': 'Canvas 0.75" Stretched 30×40"',
    'size': '30×40"',
    'cost_price': 125.00,
    'product_type': 'stretched_canvas',
    'thickness': '0.75'
}

response = requests.post(
    'https://your-domain.com/admin/pricing/add-product',
    json=product_data,
    cookies=admin_session_cookies
)

if response.json()['success']:
    print("Product added successfully")
```

## Integration Notes

### 3-Dropdown System Integration
The customer ordering system uses these API endpoints in sequence:
1. **Load Products:** `GET /api/products` - Populates all three dropdowns
2. **Extract Types:** JavaScript processes products to create Dropdown 1 options
3. **Filter Variants:** When type selected, filters products for Dropdown 2 options
4. **Show Sizes:** When variant selected, shows available sizes in Dropdown 3

### Admin Interface Integration
The admin pricing interface uses these endpoints:
1. **Load Dashboard:** `GET /admin/pricing/data` - Shows all products and categories
2. **Update Pricing:** `POST /admin/pricing/update-markup` - Global price changes
3. **Manage Products:** Various endpoints for CRUD operations
4. **Real-time Updates:** Changes immediately reflect in customer interface

### Database Consistency
All endpoints maintain database consistency through:
- **Foreign Key Constraints:** Prevent orphaned records
- **Transaction Management:** Ensure atomic operations
- **Input Validation:** Prevent invalid data entry
- **Error Handling:** Graceful failure recovery

---

**API Version:** 2.0  
**Last Updated:** October 19, 2025  
**Total Endpoints:** 15+ endpoints  
**Authentication:** Session-based for admin, public for customer  
**Rate Limiting:** Implemented  
**Error Handling:** Standardized JSON responses
