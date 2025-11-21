# Fifth Element Photography - Admin V3 Project Structure

**Version:** 3.0.0-alpha  
**Created:** November 20, 2024  
**Status:** In Development

---

## Project Overview

This document defines the file structure and organization for Admin V3, a complete rewrite of the Fifth Element Photography admin dashboard built from scratch with clean, maintainable, and well-documented code.

---

## Core Principles

1. **Documentation First** - Every file, function, and feature is documented
2. **Semantic Versioning** - All versions follow semver (MAJOR.MINOR.PATCH)
3. **Systematic Backups** - Git tags at every milestone
4. **Clean Code** - No legacy code, built from scratch
5. **Separation of Concerns** - Backend, frontend, and data clearly separated

---

## File Structure

```
fifth-element-photography/
│
├── app.py                          # Original Flask app (production)
├── app_v3.py                       # NEW: V3 Flask app with clean routes
│
├── templates/
│   ├── index.html                  # Original front-end (production)
│   ├── admin_new.html              # Original admin (production)
│   ├── index_v3.html               # NEW: Simple test front-end for V3
│   └── admin_v3.html               # NEW: Clean admin dashboard V3
│
├── static/
│   ├── css/
│   │   ├── style.css               # Original front-end styles (production)
│   │   ├── admin_new.css           # Original admin styles (production)
│   │   ├── style_v3.css            # NEW: Test front-end styles V3
│   │   └── admin_v3.css            # NEW: Admin dashboard styles V3
│   │
│   ├── js/
│   │   ├── script.js               # Original front-end JS (production)
│   │   ├── admin_new.js            # Original admin JS (production)
│   │   ├── script_v3.js            # NEW: Test front-end JS V3
│   │   └── admin_v3.js             # NEW: Admin dashboard JS V3
│   │
│   └── images/                     # Shared image assets
│
├── data/                           # Persistent data (shared between versions)
│   ├── images/                     # Uploaded images
│   ├── image_metadata.json         # Image titles and descriptions
│   ├── image_categories.json       # Image category assignments
│   ├── categories.json             # Available categories
│   ├── featured_image.json         # Featured image selection
│   └── hero_image.json             # Hero image selection
│
├── docs/                           # NEW: V3 Documentation
│   ├── README_V3.md                # V3 project overview
│   ├── ARCHITECTURE_V3.md          # V3 system architecture
│   ├── API_V3.md                   # V3 API documentation
│   └── CHANGELOG_V3.md             # V3 version history
│
└── V3_PROJECT_STRUCTURE.md         # THIS FILE
```

---

## V3 Admin Requirements

### Core Functions
1. **Upload Images** - Multi-image upload with drag-and-drop
2. **Delete Images** - Single and bulk deletion
3. **Name Images** - Edit image titles
4. **Describe Images** - Edit image descriptions
5. **Multi-Categorize** - Assign multiple categories per image
6. **Filter Images** - Filter gallery by category
7. **Sort Images** - Sort by date, name, etc.
8. **Manage Categories** - Create and delete categories

### Future Enhancements (Post-V3.0.0)
- Shopify Product Mapping integration
- Randomize image display on front-end
- Advanced backup system

---

## Version Strategy

### Version Numbers
- **3.0.0-alpha** - Initial development
- **3.0.0-beta** - Feature complete, testing phase
- **3.0.0** - Production release
- **3.1.0** - First feature addition
- **3.0.1** - Bug fix release

### Git Tags
Every version bump gets a Git tag:
```bash
git tag -a v3.0.0-alpha -m "Admin V3 Alpha Release"
git push origin v3.0.0-alpha
```

---

## Development Workflow

1. **Build** - Write code in `v3-staging` branch
2. **Commit** - Push to GitHub with clear commit messages
3. **Tag** - Create Git tag at milestones
4. **Test** - User switches Railway to `v3-staging` for live testing
5. **Fix** - Address issues based on user feedback
6. **Repeat** - Until feature is approved
7. **Release** - Merge `v3-staging` → `main` when complete

---

## Data Compatibility

V3 uses the **same data files** as the original system:
- `/data/images/` - No image migration needed
- `/data/*.json` - Compatible metadata format
- Seamless transition when V3 goes live

---

**Next Steps:** Create comprehensive documentation (README, ARCHITECTURE, CHANGELOG)

