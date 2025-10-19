# Deployment Guide - Complete System Recreation

**Purpose:** Step-by-step instructions to recreate the Fifth Element Photography system from scratch  
**Target:** New deployment or system migration  
**Time Required:** 2-3 hours

---

## 🎯 Prerequisites

### **Required Accounts:**
- GitHub account (for code repository)
- Railway account (for hosting) or similar PaaS provider
- Domain name (optional, for custom URL)

### **Required Tools:**
- Git command line
- Python 3.8+ (for local development)
- Text editor or IDE
- Web browser (for testing)

### **Required Knowledge:**
- Basic Flask/Python understanding
- SQLite database concepts
- Git version control
- Web development fundamentals

---

## 📋 Step 1: Repository Setup

### **1.1 Create New Repository**
```bash
# Create new repository on GitHub
# Clone to local machine
git clone https://github.com/[username]/[repository-name].git
cd [repository-name]
```

### **1.2 Create Directory Structure**
```bash
mkdir -p templates static/js static/css documentation/architecture
```

### **1.3 Create Core Files**
```bash
touch app.py requirements.txt runtime.txt
touch pricing_admin.py dynamic_product_api.py variant_routes.py
touch category_admin.py database_setup_route.py
```

---

## 📁 Step 2: Core Application Setup

### **2.1 Create requirements.txt**
```txt
Flask==2.3.3
gunicorn==21.2.0
```

### **2.2 Create runtime.txt**
```txt
python-3.11.0
```

### **2.3 Create Main Flask App (app.py)**
```python
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def require_admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Comment out for initial setup, uncomment for production
        # if 'admin_logged_in' not in session:
        #     return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enhanced_order_form')
def enhanced_order_form():
    image_url = request.args.get('image', '')
    return render_template('enhanced_order_form.html', image_url=image_url)

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 🗄️ Step 3: Database Setup

### **3.1 Create Database Initialization Script**
Create `init_pricing_db.py` with complete Lumaprints product data:

```python
import sqlite3
import json
from datetime import datetime

def create_database():
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            display_order INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            size TEXT NOT NULL,
            cost_price REAL NOT NULL,
            category_id INTEGER NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_name TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            variant_name TEXT NOT NULL,
            variant_description TEXT NOT NULL,
            price_modifier REAL DEFAULT 0.0,
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Insert initial settings
    cursor.execute('''
        INSERT OR REPLACE INTO settings (key_name, value, description)
        VALUES ('global_markup_percentage', '123.0', 'Global markup percentage applied to all products')
    ''')
    
    cursor.execute('''
        INSERT OR REPLACE INTO settings (key_name, value, description)
        VALUES ('last_updated', ?, 'Last database update timestamp')
    ''', (datetime.now().isoformat(),))
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == '__main__':
    create_database()
```

### **3.2 Load Lumaprints Product Data**
You'll need to create scripts to load the 679 products. Reference the existing data files:
- Copy product data from `lumaprints_current_pricing_2025.txt`
- Create category insertion scripts
- Load all product data with proper categorization

---

## 🎨 Step 4: Frontend Templates

### **4.1 Create Enhanced Order Form Template**
Create `templates/enhanced_order_form.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Order Your Print - Fifth Element Photography</title>
    <style>
        /* Add comprehensive CSS styling here */
        /* Reference existing enhanced_order_form.html for complete styles */
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Order Your Print</h1>
            <p>Professional quality prints delivered to your door</p>
        </header>
        
        <div class="content">
            <!-- Left Panel: Image & Product Selection -->
            <div class="left-panel">
                <div class="section">
                    <h3>Selected Image</h3>
                    <div id="imagePreview">Loading image preview...</div>
                </div>
                
                <div class="section">
                    <h3>Choose Your Product</h3>
                    <div class="form-group">
                        <label for="productSelect">Product & Size:</label>
                        <select id="productSelect" required>
                            <option value="">Select a product...</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="quantityInput">Quantity:</label>
                        <input type="number" id="quantityInput" min="1" max="10" value="1" required>
                    </div>

                    <div id="productDetails">
                        <p>Select a product to see details.</p>
                    </div>
                </div>
            </div>
            
            <!-- Right Panel: Customer Info & Order Summary -->
            <div class="right-panel">
                <!-- Customer form and order summary here -->
            </div>
        </div>
    </div>
    
    <script src="/static/js/dynamic_ordering_system.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const orderingSystem = new DynamicOrderingSystem();
            orderingSystem.init();
        });
    </script>
</body>
</html>
```

### **4.2 Create Admin Pricing Template**
Create `templates/admin_pricing.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fifth Element Pricing Structure</title>
    <style>
        /* Add admin interface styling */
        /* Reference existing admin_pricing.html for complete styles */
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Fifth Element Pricing Structure</h1>
        </header>
        
        <!-- Global Markup Section -->
        <div class="markup-section">
            <!-- Markup controls here -->
        </div>
        
        <!-- Products & Pricing Section -->
        <div class="products-section">
            <!-- Collapsible categories with products -->
        </div>
    </div>
    
    <script>
        // Add admin interface JavaScript
    </script>
</body>
</html>
```

---

## 🔧 Step 5: Backend Implementation

### **5.1 Create Pricing Admin Backend**
Create `pricing_admin.py` with all the pricing management functions:

```python
import sqlite3
import json
from datetime import datetime
from flask import request, jsonify, render_template

def get_db_connection():
    conn = sqlite3.connect('lumaprints_pricing.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_global_markup():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key_name = 'global_markup_percentage'")
    result = cursor.fetchone()
    conn.close()
    return float(result['value']) if result else 123.0

# Add all other pricing admin functions here
```

### **5.2 Create Dynamic Product API**
Create `dynamic_product_api.py` with product loading functions:

```python
import sqlite3
from flask import jsonify

def get_db_connection():
    conn = sqlite3.connect('lumaprints_pricing.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_products_for_order_form():
    # Implementation for loading products with variants
    pass

# Add all product API functions here
```

### **5.3 Create Frontend JavaScript**
Create `static/js/dynamic_ordering_system.js`:

```javascript
class DynamicOrderingSystem {
    constructor() {
        this.allProducts = [];
        this.selectedProduct = null;
        this.selectedVariant = null;
    }
    
    async init() {
        await this.loadProducts();
        this.setupEventListeners();
        this.populateProductDropdown();
    }
    
    async loadProducts() {
        try {
            const response = await fetch('/api/products');
            const data = await response.json();
            if (data.success) {
                this.allProducts = data.products;
            }
        } catch (error) {
            console.error('Error loading products:', error);
        }
    }
    
    // Add all other frontend functions here
}
```

---

## 🚀 Step 6: Deployment Setup

### **6.1 Railway Deployment**
1. Connect GitHub repository to Railway
2. Set environment variables:
   - `SECRET_KEY`: Generate secure key
   - `PYTHON_VERSION`: 3.11.0
3. Configure build settings
4. Deploy from main branch

### **6.2 Database Initialization**
1. Add temporary setup route to app.py
2. Visit `/setup-database` after deployment
3. Verify database creation and data loading
4. Remove or secure setup route

### **6.3 Domain Configuration**
1. Configure custom domain in Railway (optional)
2. Set up SSL certificate
3. Update DNS settings

---

## ✅ Step 7: Testing & Verification

### **7.1 Admin Interface Testing**
1. Visit `/admin/pricing`
2. Verify all 679 products load
3. Test global markup updates
4. Test individual product cost updates
5. Test add/remove product functionality

### **7.2 Customer Order Form Testing**
1. Visit `/enhanced_order_form?image=[test-url]`
2. Verify products load in dropdown
3. Test product selection and details display
4. Test variant dropdown for framed canvas
5. Verify pricing calculations

### **7.3 Integration Testing**
1. Update pricing in admin
2. Verify changes reflect in order form
3. Test adding new products
4. Verify new products appear in order form

---

## 🔒 Step 8: Security & Production Setup

### **8.1 Enable Authentication**
1. Uncomment `@require_admin_auth` decorators
2. Implement admin login system
3. Set secure session configuration
4. Test admin access restrictions

### **8.2 Production Configuration**
1. Set `debug=False` in production
2. Configure proper error handling
3. Set up logging
4. Implement backup procedures

### **8.3 Performance Optimization**
1. Add database indexes
2. Implement caching where appropriate
3. Optimize SQL queries
4. Test load performance

---

## 📊 Step 9: Data Migration (If Needed)

### **9.1 Export Existing Data**
```python
# Script to export current database to JSON
import sqlite3
import json

def export_database():
    conn = sqlite3.connect('lumaprints_pricing.db')
    # Export all tables to JSON files
    # Create migration scripts
```

### **9.2 Import to New System**
```python
# Script to import data from JSON files
def import_database():
    # Load JSON files
    # Insert into new database
    # Verify data integrity
```

---

## 🛠️ Step 10: Maintenance Setup

### **10.1 Backup Procedures**
1. Database file included in Git repository
2. Automatic backup with deployments
3. Manual backup procedures documented

### **10.2 Update Procedures**
1. Product updates via admin interface
2. Code updates via Git deployment
3. Database schema updates via migration scripts

### **10.3 Monitoring Setup**
1. Error logging and monitoring
2. Performance monitoring
3. Uptime monitoring
4. User activity tracking

---

## 🚨 Troubleshooting Common Issues

### **Database Issues:**
- Check database file permissions
- Verify table creation scripts
- Test database connections

### **API Issues:**
- Check Flask route definitions
- Verify JSON response formats
- Test API endpoints individually

### **Frontend Issues:**
- Check JavaScript console for errors
- Verify API response handling
- Test cross-browser compatibility

### **Deployment Issues:**
- Check Railway build logs
- Verify environment variables
- Test database initialization

---

## 📈 Post-Deployment Checklist

- [ ] All 679 products loading correctly
- [ ] Pricing calculations accurate
- [ ] Admin interface fully functional
- [ ] Customer order form working
- [ ] Variant selection operational
- [ ] Authentication enabled
- [ ] Backup procedures in place
- [ ] Performance acceptable
- [ ] Error handling working
- [ ] Documentation complete

---

## 🎯 Success Metrics

**System is successfully deployed when:**
- ✅ 679+ products load in under 1 second
- ✅ Pricing updates reflect instantly across system
- ✅ Admin can add/remove products seamlessly
- ✅ Customers can select products and variants
- ✅ All calculations are accurate
- ✅ System handles expected user load
- ✅ No critical errors in production

---

*End of Deployment Guide*
