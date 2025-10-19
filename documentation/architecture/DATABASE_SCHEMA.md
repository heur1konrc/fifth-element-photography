# Database Schema Documentation

**Database:** `lumaprints_pricing.db` (SQLite)  
**Total Products:** 679  
**Total Categories:** 26  
**Total Variants:** 256

---

## 📊 Table Structures

### **1. products**
Primary table containing all Lumaprints product catalog.

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    size TEXT NOT NULL,
    cost_price REAL NOT NULL,
    category_id INTEGER NOT NULL,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

**Sample Data:**
```
id: 1, name: "Canvas 0.75\"", size: "8×10\"", cost_price: 15.39, category_id: 1
id: 2, name: "Canvas 0.75\"", size: "11×14\"", cost_price: 18.76, category_id: 1  
id: 3, name: "Framed Canvas 1.5\"", size: "8×10\"", cost_price: 31.25, category_id: 6
```

### **2. categories**
Product categories for organization and display.

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data:**
```
id: 1, name: "Canvas - 0.75\" Stretched", display_order: 1
id: 2, name: "Canvas - 1.25\" Stretched", display_order: 2
id: 6, name: "Framed Canvas - 1.5\"", display_order: 6
```

### **3. settings**
Global configuration stored as key-value pairs.

```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Settings:**
```
key_name: "global_markup_percentage", value: "123.0"
key_name: "last_updated", value: "2025-10-19"
```

### **4. product_variants**
Frame options for products that support variants.

```sql
CREATE TABLE product_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    variant_name TEXT NOT NULL,
    variant_description TEXT NOT NULL,
    price_modifier REAL DEFAULT 0.0,
    is_default INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**Sample Data (for Framed Canvas 1.5" products):**
```
product_id: 150, variant_name: "Maple Wood", variant_description: "Maple Wood Floating Frame", is_default: 1
product_id: 150, variant_name: "Espresso", variant_description: "Espresso Floating Frame", is_default: 0
product_id: 150, variant_name: "Natural Wood", variant_description: "Natural Wood Floating Frame", is_default: 0
```

---

## 🔗 Relationships

### **products ↔ categories**
- **Type:** Many-to-One
- **Foreign Key:** `products.category_id → categories.id`
- **Purpose:** Organize products into logical groups

### **products ↔ product_variants**
- **Type:** One-to-Many  
- **Foreign Key:** `product_variants.product_id → products.id`
- **Purpose:** Support product options (frame types)

---

## 📈 Data Statistics

### **Product Distribution by Category:**
```
Canvas - 0.75" Stretched: 32 products
Canvas - 1.25" Stretched: 32 products  
Canvas - 1.5" Stretched: 32 products
Framed Canvas - 0.75": 32 products
Framed Canvas - 1.25": 32 products
Framed Canvas - 1.5": 32 products (with 8 variants each = 256 total variants)
Fine Art Paper categories: ~400+ products
Metal Print categories: ~100+ products
```

### **Pricing Range:**
```
Lowest Cost: ~$8.00 (small fine art papers)
Highest Cost: ~$200.00 (large framed canvases)
Average Cost: $48.49
Average Customer Price (123% markup): $108.14
```

---

## 🔍 Key Queries

### **Get All Products with Categories:**
```sql
SELECT p.*, c.name as category_name 
FROM products p 
JOIN categories c ON p.category_id = c.id 
WHERE p.active = 1 AND c.active = 1
ORDER BY c.display_order, p.size;
```

### **Get Products with Variant Count:**
```sql
SELECT p.*, c.name as category_name, COUNT(pv.id) as variant_count
FROM products p
JOIN categories c ON p.category_id = c.id
LEFT JOIN product_variants pv ON p.id = pv.product_id
WHERE p.active = 1 AND c.active = 1
GROUP BY p.id
ORDER BY c.display_order, p.size;
```

### **Get Global Markup:**
```sql
SELECT value FROM settings WHERE key_name = 'global_markup_percentage';
```

### **Get Product Variants:**
```sql
SELECT * FROM product_variants 
WHERE product_id = ? 
ORDER BY is_default DESC, variant_name;
```

---

## 🛠️ Indexes for Performance

```sql
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_active ON products(active);
CREATE INDEX idx_categories_active ON categories(active);
CREATE INDEX idx_categories_display_order ON categories(display_order);
CREATE INDEX idx_product_variants_product ON product_variants(product_id);
CREATE INDEX idx_settings_key ON settings(key_name);
```

---

## 🔄 Data Initialization Scripts

### **1. init_pricing_db.py**
- Creates initial database schema
- Loads first batch of Lumaprints products
- Sets up categories and settings

### **2. complete_pricing_data.py**  
- Loads remaining product categories
- Completes the 679-product catalog
- Updates statistics

### **3. create_variants_system.py**
- Creates product_variants table
- Adds 8 frame variants for each 1.5" Framed Canvas product
- Sets Maple Wood as default

---

## 💾 Backup and Recovery

### **Backup Strategy:**
1. **Git Repository:** Database file included in version control
2. **Railway Deployment:** Automatic backup with each deploy
3. **Manual Backup:** Copy `lumaprints_pricing.db` file

### **Recovery Process:**
1. Restore database file from backup
2. Run initialization scripts if needed
3. Verify data integrity with sample queries

---

## 🔧 Maintenance Operations

### **Adding New Products:**
```sql
INSERT INTO products (name, size, cost_price, category_id) 
VALUES ('Coffee Mug', '11oz', 8.50, 27);
```

### **Updating Global Markup:**
```sql
UPDATE settings 
SET value = '150.0', updated_at = CURRENT_TIMESTAMP 
WHERE key_name = 'global_markup_percentage';
```

### **Adding Product Variants:**
```sql
INSERT INTO product_variants (product_id, variant_name, variant_description, is_default)
VALUES (679, 'Blue Handle', 'Coffee Mug with Blue Handle', 1);
```

---

*End of Database Schema Documentation*
