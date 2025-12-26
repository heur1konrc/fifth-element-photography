# Fifth Element Photography - Complete Context Recovery Guide

**Purpose**: This document provides everything needed to restore full project context in a new session, after a crash, or when starting fresh without any prior knowledge.

**Last Updated**: December 25, 2025

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Critical URLs and Access](#critical-urls-and-access)
3. [File System Structure](#file-system-structure)
4. [Database Architecture](#database-architecture)
5. [Railway Deployment](#railway-deployment)
6. [GitHub Repository](#github-repository)
7. [Environment Variables](#environment-variables)
8. [Admin Credentials](#admin-credentials)
9. [Step-by-Step Context Recovery](#step-by-step-context-recovery)
10. [Common Operations](#common-operations)
11. [Troubleshooting](#troubleshooting)

---

## 1. Project Overview

**Project Name**: Fifth Element Photography  
**Type**: Flask-based photography portfolio and e-commerce platform  
**Owner**: Heur1konrc  
**Primary Function**: Photography gallery, Shopify product management, print ordering integration

### Key Features
- **Gallery System**: Public-facing photography portfolio with categories and galleries
- **Admin Dashboard**: Complete image management, product creation, and pricing tools
- **Shopify Integration**: Product creation, price syncing, and order management
- **Lumaprints Integration**: Print fulfillment provider bulk mapping
- **Image Processing**: Automatic thumbnail and gallery image generation

---

## 2. Critical URLs and Access

### Production URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Public Website** | `https://fifth-element-photography-production.up.railway.app` | Main gallery and storefront |
| **Admin Dashboard** | `https://fifth-element-photography-production.up.railway.app/admin` | Full admin interface |
| **Shopify Store** | `https://fifth-element-photography.myshopify.com` | Live Shopify store |

### Admin Dashboard Tabs

The admin dashboard has **4 main tabs**:

1. **Images Tab** - Image management, upload, categories, galleries
2. **Shopify Tab** - All Shopify tools (product creation, Lumaprints mapping, price sync)
3. **Tools Tab** - Backup system, Lumaprints bulk mapping (duplicate)
4. **Settings Tab** - Site configuration

### Key Admin Tools (All in Shopify Tab)

| Tool | Location | Function |
|------|----------|----------|
| Create Shopify Products | Shopify Tab → "Create Shopify Products" button | Creates products directly in Shopify via API |
| Lumaprints Bulk Mapping | Shopify Tab → "Lumaprints Bulk Mapping" button | Maps images to Lumaprints products in bulk |
| Sync Prices to Shopify | Shopify Tab → "Sync Prices to Shopify" button | Updates all Shopify product prices from database |

---

## 3. File System Structure

### Local Development (Sandbox)

```
/home/ubuntu/fifth-element-photography/
├── app.py                          # Main Flask application
├── Procfile                        # Railway deployment config
├── requirements.txt                # Python dependencies
├── admin_config.json               # Admin credentials (hashed password)
├── pricing_config.json             # Pricing configuration
│
├── data/                           # LOCAL databases (not used in production)
│   ├── lumaprints_pricing.db      # Main pricing database (local copy)
│   ├── gallery_images.db          # Gallery metadata (empty)
│   ├── products.db                # Product data
│   ├── photography.db             # Photography metadata
│   └── print_ordering.db          # Print ordering data
│
├── routes/                         # Flask blueprints (API endpoints)
│   ├── shopify_api_creator.py     # Shopify product creation API
│   ├── shopify_price_sync_api.py  # Price syncing API
│   ├── shopify_admin.py           # Shopify admin interface
│   ├── shopify_csv_generator.py   # CSV generation
│   ├── pricing_admin.py           # Pricing management
│   ├── gallery_admin.py           # Gallery management
│   ├── highres_image_viewer.py    # High-res image viewing
│   └── regenerate_gallery_image.py # Gallery image regeneration
│
├── static/                         # Static assets
│   ├── css/                       # Stylesheets
│   ├── js/                        # JavaScript files
│   │   ├── admin_new.js          # Main admin dashboard JS
│   │   └── regenerate_gallery.js # Gallery regeneration JS
│   ├── images/                    # Site images
│   ├── thumbnails/                # Generated thumbnails (local)
│   └── product-thumbnails/        # Product preview images
│
├── templates/                      # HTML templates
│   ├── admin_new.html             # Main admin dashboard
│   ├── index.html                 # Public homepage
│   ├── gallery.html               # Gallery pages
│   └── admin/                     # Admin sub-templates
│
├── docs/                           # Documentation
│   ├── CONTEXT_RECOVERY_GUIDE.md  # This file
│   ├── Product_Management_Manual.md
│   ├── Gallery_Image_Regeneration_Fix.md
│   ├── Shopify_Price_Sync_System.md
│   └── Watermark_Proposal.md
│
├── scripts/                        # Utility scripts
├── backups/                        # Database backups
└── thumbnail_helper.py             # Thumbnail generation utility
```

### Production (Railway) File System

**CRITICAL**: In production, all persistent data is stored in `/data` (Railway volume mount)

```
/data/                              # Railway persistent volume (vol_hlyizta26f0rtzdp)
├── lumaprints_pricing.db          # MAIN DATABASE (all products, pricing, mappings)
├── print_ordering.db              # Print ordering database
│
├── [image files].jpg              # Original uploaded images
├── [image files].png              # Original uploaded images
│
├── thumbnails/                    # Generated 400px thumbnails
│   └── [filename].jpg
│
├── gallery-images/                # Generated 1200px gallery images
│   └── [filename].jpg
│
├── originals/                     # High-resolution originals (optional)
│   └── [filename].jpg
│
├── about/                         # About page images
│   └── [filename].jpg
│
├── categories.json                # Image category assignments
├── featured.json                  # Featured image data
├── featured_image.json            # Current featured image
├── hero_image.json                # Homepage hero image
├── carousel_images.json           # Homepage carousel
├── image_categories.json          # Category mappings
├── image_descriptions.json        # Image descriptions
├── image_titles.json              # Image titles
├── image_dimensions_cache.json    # Cached image dimensions
├── background_images.json         # Background image list
├── featured_stories.json          # Featured stories
├── about_data.json                # About page content
└── lumaprints_orders.json         # Lumaprints order data
```

### Key Path Constants in Code

```python
IMAGES_FOLDER = '/data'  # All images stored here in production
CATEGORIES_FILE = '/data/categories.json'
FEATURED_FILE = '/data/featured.json'
ABOUT_FILE = '/data/about.json'
ORDERS_FILE = '/data/lumaprints_orders.json'
```

---

## 4. Database Architecture

### Primary Database: `/data/lumaprints_pricing.db`

This is the **MAIN DATABASE** containing all product, pricing, and mapping data.

#### Tables

**products**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    product_type_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    size TEXT NOT NULL,
    cost_price REAL NOT NULL,
    retail_price REAL NOT NULL,
    lumaprints_subcategory_id INTEGER,
    lumaprints_options TEXT,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**product_types**
```sql
CREATE TABLE product_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    display_order INTEGER DEFAULT 0
);
```

**categories**
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    product_type_id INTEGER NOT NULL,
    display_order INTEGER DEFAULT 0
);
```

**shopify_mappings**
```sql
CREATE TABLE shopify_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_filename TEXT UNIQUE NOT NULL,
    shopify_product_handle TEXT,
    order_prints_enabled INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**settings**
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

### Secondary Databases

| Database | Location | Purpose | Status |
|----------|----------|---------|--------|
| `gallery_images.db` | `/data/` | Gallery metadata | Empty (not used) |
| `print_ordering.db` | `/data/` | Print ordering | Active |
| `images.db` | Project root | Image metadata | Empty (not used) |

### Database Access Pattern

```python
# Standard connection pattern used throughout app
db_path = '/data/lumaprints_pricing.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # Access columns by name
cursor = conn.cursor()
```

---

## 5. Railway Deployment

### Railway Project Details

| Property | Value |
|----------|-------|
| **Project Name** | fifth-element-photography |
| **Environment** | production |
| **Service Name** | fifth-element-photography-production |
| **Domain** | `fifth-element-photography-production.up.railway.app` |
| **Volume Name** | `vol_hlyizta26f0rtzdp` |
| **Volume Mount** | `/data` |

### Deployment Configuration

**Procfile**:
```
web: gunicorn app:app --timeout 600
```

**Python Version**: 3.11+ (managed by Railway)

**Dependencies** (`requirements.txt`):
```
Flask==2.3.3
Pillow>=11.1.0
gunicorn==21.2.0
requests==2.31.0
pillow-heif==1.1.1
openpyxl==3.1.2
```

### Railway Volume Mount

**CRITICAL**: The `/data` directory is a **persistent volume** that survives deployments.

- **Volume ID**: `vol_hlyizta26f0rtzdp`
- **Mount Path**: `/data`
- **Contents**: All images, databases, JSON configuration files
- **Persistence**: Data persists across deployments and restarts

**What gets reset on deployment**:
- Application code (from GitHub)
- Python packages (reinstalled from requirements.txt)
- Temporary files

**What persists**:
- Everything in `/data/`
- All uploaded images
- All databases
- All configuration JSON files

### Deployment Trigger

Railway automatically deploys when commits are pushed to the `main` branch on GitHub.

**Manual deployment**:
```bash
# In sandbox (requires Railway CLI authentication)
railway up
```

### Railway CLI Access

The Railway CLI is installed in the sandbox but requires authentication:

```bash
# Check login status
railway whoami

# Login (requires browser)
railway login

# View logs
railway logs

# Check deployment status
railway status
```

---

## 6. GitHub Repository

### Repository Details

| Property | Value |
|----------|-------|
| **Owner** | heur1konrc |
| **Repository** | fifth-element-photography |
| **URL** | `https://github.com/heur1konrc/fifth-element-photography` |
| **Branch** | main |
| **Access Token** | (stored in git remote config) |

### Git Configuration

The repository is already configured in the sandbox:

```bash
cd /home/ubuntu/fifth-element-photography
git remote -v
# origin  https://[token]@github.com/heur1konrc/fifth-element-photography.git
```

### Standard Git Workflow

```bash
cd /home/ubuntu/fifth-element-photography

# Check status
git status

# Add changes
git add [files]

# Commit
git commit -m "Description of changes"

# Push to GitHub (triggers Railway deployment)
git push

# Pull latest
git pull
```

---

## 7. Environment Variables

### Required Environment Variables (Railway)

These are configured in the Railway dashboard and **NOT** stored in code:

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `SECRET_KEY` | Flask session encryption | Auto-generated hex string |
| `SHOPIFY_STORE` | Shopify store domain | `fifth-element-photography.myshopify.com` |
| `SHOPIFY_API_KEY` | Shopify API key | (admin provides) |
| `SHOPIFY_API_SECRET` | Shopify API access token | (admin provides) |

### Accessing Environment Variables in Code

```python
import os

SHOPIFY_STORE = os.environ.get('SHOPIFY_STORE', 'fifth-element-photography.myshopify.com')
SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY', '')
SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET', '')
```

### Where to Set Environment Variables

1. Go to Railway dashboard
2. Select the `fifth-element-photography` project
3. Click on the `fifth-element-photography-production` service
4. Go to **Variables** tab
5. Add/edit variables

---

## 8. Admin Credentials

### Admin Login

**Location**: `https://fifth-element-photography-production.up.railway.app/admin`

**Credentials** (stored in `admin_config.json`):
```json
{
  "username": "Heur1konrc",
  "password_hash": "3afeed04eeca02f36260571b19deb0898adfabcf3d0283aacdc9cafb81e0b0e1"
}
```

**Password**: (User knows the plaintext password; hash is SHA-256)

### Password Verification

The admin login uses SHA-256 hashing:

```python
import hashlib

def verify_password(username, password):
    with open('admin_config.json', 'r') as f:
        config = json.load(f)
    
    if username != config['username']:
        return False
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == config['password_hash']
```

---

## 9. Step-by-Step Context Recovery

### Scenario: New Session, Lost Context

Follow these steps to restore full project context:

#### Step 1: Clone Repository (if needed)

```bash
cd /home/ubuntu
# Token is already configured in sandbox git remote
git clone https://github.com/heur1konrc/fifth-element-photography.git
cd fifth-element-photography
```

#### Step 2: Verify Project Structure

```bash
# Check main files exist
ls -la app.py Procfile requirements.txt

# Check directories
ls -d routes/ static/ templates/ docs/ data/

# Verify databases
ls -lh data/*.db
```

#### Step 3: Understand Current State

```bash
# Check git status
git status

# View recent commits
git log --oneline -10

# Check for uncommitted changes
git diff
```

#### Step 4: Review Documentation

```bash
# List all documentation
ls -lh docs/

# Read this file
cat docs/CONTEXT_RECOVERY_GUIDE.md

# Check other relevant docs
cat docs/Product_Management_Manual.md
cat docs/Gallery_Image_Regeneration_Fix.md
```

#### Step 5: Verify Railway Deployment

```bash
# Check Railway CLI status (may require login)
railway whoami

# View recent logs
railway logs --limit 50

# Check deployment status
railway status
```

#### Step 6: Test Admin Access

Open browser and navigate to:
```
https://fifth-element-photography-production.up.railway.app/admin
```

Login with credentials from `admin_config.json`.

#### Step 7: Verify Database Schema

```bash
cd /home/ubuntu/fifth-element-photography

# Check main database schema
sqlite3 data/lumaprints_pricing.db ".schema"

# Count products
sqlite3 data/lumaprints_pricing.db "SELECT COUNT(*) FROM products;"

# Check product types
sqlite3 data/lumaprints_pricing.db "SELECT * FROM product_types;"
```

#### Step 8: Review Key Code Files

```bash
# Main application
head -100 app.py

# Shopify API creator
head -50 routes/shopify_api_creator.py

# Price sync
head -50 routes/shopify_price_sync_api.py
```

#### Step 9: Check for Recent Issues

```bash
# Search for TODO or FIXME comments
grep -r "TODO\|FIXME" --include="*.py" --include="*.js"

# Check for error logs in docs
ls -lh docs/*Fix*.md docs/*Error*.md
```

#### Step 10: Confirm Understanding

You should now be able to answer:

- ✅ Where are images stored in production? (`/data/`)
- ✅ What is the main database? (`/data/lumaprints_pricing.db`)
- ✅ Where are the Shopify tools? (Admin → Shopify Tab)
- ✅ How do I deploy changes? (Git push to main branch)
- ✅ Where is the Railway volume mounted? (`/data`)
- ✅ What are the admin credentials? (Check `admin_config.json`)

---

## 10. Common Operations

### Deploy Code Changes

```bash
cd /home/ubuntu/fifth-element-photography

# Make changes to files
# ...

# Stage changes
git add [files]

# Commit
git commit -m "Description of changes"

# Push (triggers Railway deployment)
git push

# Monitor deployment
railway logs --follow
```

### Update Documentation

```bash
cd /home/ubuntu/fifth-element-photography/docs

# Edit documentation
nano [filename].md

# Commit and push
git add docs/
git commit -m "Update documentation: [description]"
git push
```

### Query Database

```bash
cd /home/ubuntu/fifth-element-photography

# Open database
sqlite3 data/lumaprints_pricing.db

# Example queries
SELECT COUNT(*) FROM products;
SELECT * FROM product_types;
SELECT * FROM shopify_mappings LIMIT 10;

# Exit
.quit
```

### Check Image Storage

```bash
# In production, images are in /data (not accessible from sandbox)
# In sandbox, check local data directory
ls -lh /home/ubuntu/fifth-element-photography/data/*.jpg 2>/dev/null || echo "No images in local data/"

# Check static thumbnails (not used in production)
ls -lh /home/ubuntu/fifth-element-photography/static/thumbnails/ | head -10
```

### Backup Database

```bash
cd /home/ubuntu/fifth-element-photography

# Create backup
cp data/lumaprints_pricing.db backups/lumaprints_pricing_$(date +%Y%m%d_%H%M%S).db

# List backups
ls -lh backups/
```

### View Railway Logs

```bash
# Real-time logs
railway logs --follow

# Last 100 lines
railway logs --limit 100

# Search logs
railway logs | grep "ERROR"
```

---

## 11. Troubleshooting

### Issue: "Can't find /data directory"

**Cause**: You're in the sandbox, not production. `/data` only exists on Railway.

**Solution**: Use local `data/` directory for testing, or check Railway logs for production issues.

### Issue: "Database locked"

**Cause**: Multiple connections to SQLite database.

**Solution**:
```python
# Always close connections
conn = sqlite3.connect(db_path)
try:
    # ... operations ...
finally:
    conn.close()
```

### Issue: "Railway deployment failed"

**Cause**: Syntax error, missing dependency, or configuration issue.

**Solution**:
1. Check Railway logs: `railway logs`
2. Look for Python tracebacks
3. Verify `requirements.txt` has all dependencies
4. Check `Procfile` is correct

### Issue: "Images not showing"

**Cause**: Images not in `/data` directory on Railway.

**Solution**:
1. Check admin dashboard → Images tab
2. Verify images were uploaded through admin interface
3. Check Railway volume is mounted correctly
4. Verify `/data` directory exists in production

### Issue: "Shopify API errors"

**Cause**: Missing or incorrect environment variables.

**Solution**:
1. Check Railway dashboard → Variables tab
2. Verify `SHOPIFY_STORE`, `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET` are set
3. Test API connection in admin dashboard

### Issue: "Admin login fails"

**Cause**: Incorrect password or `admin_config.json` missing.

**Solution**:
1. Verify `admin_config.json` exists in project root
2. Check username matches exactly (case-sensitive)
3. Verify password hash is correct

### Issue: "Thumbnails not generating"

**Cause**: PIL/Pillow not installed or `/data/thumbnails` directory missing.

**Solution**:
1. Check `requirements.txt` includes `Pillow>=11.1.0`
2. Verify `thumbnail_helper.py` uses PIL (not ImageMagick)
3. Check `/data/thumbnails` directory exists in production

### Issue: "Git push rejected"

**Cause**: Local branch behind remote, or authentication issue.

**Solution**:
```bash
# Pull latest changes
git pull --rebase

# If conflicts, resolve them
git status
# ... fix conflicts ...
git add [files]
git rebase --continue

# Push again
git push
```

---

## Quick Reference Card

### Essential Commands

```bash
# Navigate to project
cd /home/ubuntu/fifth-element-photography

# Check status
git status
railway status

# View logs
railway logs --limit 50

# Deploy
git add [files] && git commit -m "message" && git push

# Database query
sqlite3 data/lumaprints_pricing.db "SELECT COUNT(*) FROM products;"

# View documentation
ls docs/
cat docs/CONTEXT_RECOVERY_GUIDE.md
```

### Essential URLs

- **Admin**: `https://fifth-element-photography-production.up.railway.app/admin`
- **Public**: `https://fifth-element-photography-production.up.railway.app`
- **Shopify**: `https://fifth-element-photography.myshopify.com`
- **GitHub**: `https://github.com/heur1konrc/fifth-element-photography`

### Essential Paths

- **Project Root**: `/home/ubuntu/fifth-element-photography`
- **Main App**: `app.py`
- **Routes**: `routes/`
- **Templates**: `templates/admin_new.html`
- **Main Database**: `data/lumaprints_pricing.db` (local) or `/data/lumaprints_pricing.db` (production)
- **Images**: `/data/` (production only)
- **Docs**: `docs/`

---

## Document History

| Date | Change | Author |
|------|--------|--------|
| 2025-12-25 | Initial creation | Manus AI |

---

**END OF CONTEXT RECOVERY GUIDE**
